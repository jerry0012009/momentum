#!/usr/bin/env python3
"""
Rank 444 — RSI + BB 均值回复策略 完整回测引擎 v2
==================================================
包含：多频率回测 / 参数稳定性 / 时间稳定性 / 未来函数审计
"""

import json
import sys
import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

OUTPUT_DIR = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 指标计算
# ═══════════════════════════════════════════════════════════════

def calc_rsi(series, period=7):
    """经典 RSI 计算（Wilder 平滑）"""
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_bollinger(series, period=20, mult=2.0):
    """布林带：中轨=SMA, 上轨=中轨+mult*std, 下轨=中轨-mult*std"""
    basis = series.rolling(period).mean()
    dev = mult * series.rolling(period).std()
    return basis, basis + dev, basis - dev


# ═══════════════════════════════════════════════════════════════
# 回测核心（无未来函数审计标记）
# ═══════════════════════════════════════════════════════════════

def backtest(df, rsi_period=7, rsi_limit=30, bb_period=20, bb_mult=2.0,
             exit_mode="middle_band", commission=0.001):
    """
    回测引擎。所有信号只用 <= 当前 bar 的数据（无未来函数）。

    exit_mode:
      'middle_band' — close 上穿 BB 中轨时平仓
      'close_gt_open' — 收阳线平仓（源码版）
    """
    df = df.copy()
    df["rsi"] = calc_rsi(df["close"], rsi_period)
    df["bb_mid"], df["bb_upper"], df["bb_lower"] = calc_bollinger(
        df["close"], bb_period, bb_mult)
    df = df.dropna().reset_index(drop=True)

    if len(df) < 10:
        return None

    trades = []
    position = None

    for i in range(1, len(df)):
        row = df.iloc[i]

        if position is None:
            # 开仓：RSI < 阈值 且 收盘价 < 下轨
            if row["rsi"] < rsi_limit and row["close"] < row["bb_lower"]:
                position = {
                    "entry_date": str(row["date"]),
                    "entry_price": row["close"],
                    "entry_idx": i,
                }
        else:
            # 平仓
            should_exit = False
            if exit_mode == "middle_band" and row["close"] > row["bb_mid"]:
                should_exit = True
            elif exit_mode == "close_gt_open" and row["close"] > row["open"]:
                should_exit = True

            if should_exit:
                pnl_pct = (row["close"] / position["entry_price"] - 1) * 100
                net_pnl_pct = pnl_pct - commission * 2 * 100  # 双边手续费
                trades.append({
                    "entry_date": position["entry_date"],
                    "exit_date": str(row["date"]),
                    "entry_price": round(position["entry_price"], 6),
                    "exit_price": round(row["close"], 6),
                    "pnl_pct": round(pnl_pct, 4),
                    "net_pnl_pct": round(net_pnl_pct, 4),
                    "hold_bars": i - position["entry_idx"],
                })
                position = None

    return calc_metrics(trades, df)


def calc_metrics(trades, df):
    if not trades:
        return {
            "trades": [], "n_trades": 0, "win_rate": 0,
            "total_return_pct": 0, "annual_return_pct": 0,
            "max_dd_pct": 0, "sharpe": 0, "profit_factor": 0,
            "avg_hold_bars": 0, "avg_pnl_pct": 0, "median_pnl_pct": 0,
        }

    tdf = pd.DataFrame(trades)
    winners = tdf[tdf["net_pnl_pct"] > 0]
    losers = tdf[tdf["net_pnl_pct"] <= 0]

    n = len(tdf)
    wr = len(winners) / n * 100

    # 累计净值
    cum = (1 + tdf["net_pnl_pct"] / 100).cumprod()
    total_ret = (cum.iloc[-1] - 1) * 100

    # 年化
    first = pd.to_datetime(df["date"].iloc[0])
    last = pd.to_datetime(df["date"].iloc[-1])
    years = max((last - first).days / 365.25, 0.01)
    ann_ret = ((1 + total_ret / 100) ** (1 / years) - 1) * 100

    # 最大回撤
    eq = cum.cummax()
    dd = (cum - eq) / eq * 100
    max_dd = dd.min()

    # Sharpe
    if tdf["net_pnl_pct"].std() > 0:
        avg_hold = max(tdf["hold_bars"].mean(), 1)
        sharpe = tdf["net_pnl_pct"].mean() / tdf["net_pnl_pct"].std() * np.sqrt(min(252 / avg_hold, n))
    else:
        sharpe = 0

    # 盈亏比
    gp = winners["net_pnl_pct"].sum() if len(winners) > 0 else 0
    gl = abs(losers["net_pnl_pct"].sum()) if len(losers) > 0 else 0.001
    pf = gp / gl

    return {
        "trades": trades,
        "n_trades": n,
        "win_rate": round(wr, 2),
        "total_return_pct": round(total_ret, 2),
        "annual_return_pct": round(ann_ret, 2),
        "max_dd_pct": round(max_dd, 2),
        "sharpe": round(sharpe, 3),
        "profit_factor": round(pf, 3),
        "avg_hold_bars": round(tdf["hold_bars"].mean(), 1),
        "avg_pnl_pct": round(tdf["net_pnl_pct"].mean(), 4),
        "median_pnl_pct": round(tdf["net_pnl_pct"].median(), 4),
        "data_start": str(first.date()),
        "data_end": str(last.date()),
        "data_bars": len(df),
    }


# ═══════════════════════════════════════════════════════════════
# 数据获取
# ═══════════════════════════════════════════════════════════════

def fetch_yf(symbol, name, start, end, interval="1d"):
    """yfinance 数据获取，支持 1d/1h/15m 等"""
    import yfinance as yf
    try:
        ticker = yf.Ticker(symbol)
        # yfinance 限制: 1m 最多7天, 15m/30m 最多60天, 1h 最多730天
        if interval in ("15m", "30m"):
            actual_start = max(start, datetime.now() - timedelta(days=59))
        elif interval == "1h":
            actual_start = max(start, datetime.now() - timedelta(days=729))
        else:
            actual_start = start

        df = ticker.history(start=actual_start, end=end, interval=interval, auto_adjust=True)
        if df.empty:
            return None
        df = df.reset_index()
        # 统一列名
        rename = {"Date": "date", "Datetime": "date", "Open": "open", "High": "high",
                  "Low": "low", "Close": "close", "Volume": "volume"}
        df = df.rename(columns=rename)
        if "date" not in df.columns:
            # yfinance sometimes uses index
            df["date"] = df.index
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df = df[["date", "open", "high", "low", "close", "volume"]].dropna()
        df = df.sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  ✗ {name} ({symbol}, {interval}): {e}")
        return None


def fetch_akshare_futures(symbol, name, start, end):
    """国内期货数据"""
    import akshare as ak
    try:
        df = ak.futures_zh_daily_sina(symbol=symbol)
        df = df.rename(columns={"date": "date", "open": "open", "high": "high",
                                "low": "low", "close": "close", "volume": "volume"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  ✗ {name} ({symbol}): {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# 参数稳定性测试
# ═══════════════════════════════════════════════════════════════

def parameter_stability(df, symbol, name, exit_mode="middle_band"):
    """网格搜索不同参数组合，测试策略对参数的敏感度"""
    rsi_periods = [5, 7, 10, 14]
    rsi_limits = [25, 30, 35]
    bb_periods = [15, 20, 25]
    bb_mults = [1.5, 2.0, 2.5]

    results = []
    for rp, rl, bp, bm in product(rsi_periods, rsi_limits, bb_periods, bb_mults):
        r = backtest(df, rsi_period=rp, rsi_limit=rl, bb_period=bp,
                     bb_mult=bm, exit_mode=exit_mode)
        if r is None:
            continue
        results.append({
            "rsi_period": rp, "rsi_limit": rl, "bb_period": bp, "bb_mult": bm,
            "n_trades": r["n_trades"], "win_rate": r["win_rate"],
            "total_return_pct": r["total_return_pct"],
            "sharpe": r["sharpe"], "profit_factor": r["profit_factor"],
        })

    if not results:
        return None

    rdf = pd.DataFrame(results)
    return {
        "symbol": symbol, "name": name,
        "total_combos": len(rdf),
        "profitable_combos": int((rdf["total_return_pct"] > 0).sum()),
        "pct_profitable": round((rdf["total_return_pct"] > 0).mean() * 100, 1),
        "return_mean": round(rdf["total_return_pct"].mean(), 2),
        "return_std": round(rdf["total_return_pct"].std(), 2),
        "return_min": round(rdf["total_return_pct"].min(), 2),
        "return_max": round(rdf["total_return_pct"].max(), 2),
        "sharpe_mean": round(rdf["sharpe"].mean(), 3),
        "sharpe_std": round(rdf["sharpe"].std(), 3),
        "best_params": rdf.loc[rdf["total_return_pct"].idxmax()].to_dict(),
        "worst_params": rdf.loc[rdf["total_return_pct"].idxmin()].to_dict(),
        "all_results": rdf.to_dict(orient="records"),
    }


# ═══════════════════════════════════════════════════════════════
# 时间稳定性测试（逐年拆分）
# ═══════════════════════════════════════════════════════════════

def time_stability(df, symbol, name, exit_mode="middle_band"):
    """逐年回测，检查策略在不同年份的表现一致性"""
    df = df.copy()
    df["year"] = pd.to_datetime(df["date"]).dt.year
    years = sorted(df["year"].unique())

    yearly = []
    for y in years:
        ydf = df[df["year"] == y].reset_index(drop=True)
        if len(ydf) < 30:
            continue
        r = backtest(ydf, exit_mode=exit_mode)
        if r is None:
            continue
        yearly.append({
            "year": int(y), "n_trades": r["n_trades"],
            "win_rate": r["win_rate"], "total_return_pct": r["total_return_pct"],
            "sharpe": r["sharpe"], "max_dd_pct": r["max_dd_pct"],
            "data_bars": len(ydf),
        })

    if not yearly:
        return None

    ydf = pd.DataFrame(yearly)
    return {
        "symbol": symbol, "name": name,
        "years": yearly,
        "n_years": len(yearly),
        "positive_years": int((ydf["total_return_pct"] > 0).sum()),
        "consistency": round((ydf["total_return_pct"] > 0).mean() * 100, 1),
        "year_return_mean": round(ydf["total_return_pct"].mean(), 2),
        "year_return_std": round(ydf["total_return_pct"].std(), 2),
    }


# ═══════════════════════════════════════════════════════════════
# 主流程
# ═══════════════════════════════════════════════════════════════

def run_full():
    print("=" * 70)
    print("Rank 444 — RSI + BB 均值回复策略 完整回测 v2")
    print("=" * 70)

    now = datetime.now()
    start_3y = now - timedelta(days=365 * 3 + 60)

    # ── 标的定义 ──
    assets = [
        # (fetch_func, args, display_name, category)
        ("yf", "AAPL", "苹果 AAPL", "美股", "1d"),
        ("yf", "TSLA", "特斯拉 TSLA", "美股", "1d"),
        ("yf", "SPY", "标普500 ETF (SPY)", "美股", "1d"),
        ("yf", "QQQ", "纳斯达克100 ETF (QQQ)", "美股", "1d"),
        ("yf", "MSFT", "微软 MSFT", "美股", "1d"),
        ("yf", "GC=F", "COMEX黄金期货", "黄金", "1d"),
        ("yf", "GLD", "黄金ETF (GLD)", "黄金", "1d"),
        ("yf", "CL=F", "WTI原油期货", "期货-国际", "1d"),
        ("yf", "HG=F", "COMEX铜期货", "期货-国际", "1d"),
        ("yf", "SI=F", "COMEX白银期货", "期货-国际", "1d"),
    ]

    # 多频率标的（用流动性好的标的测频率差异）
    freq_assets = [
        ("yf", "SPY", "标普500 ETF", "美股"),
        ("yf", "AAPL", "苹果", "美股"),
        ("yf", "GC=F", "黄金期货", "黄金"),
    ]
    intervals = ["1d", "1h"]

    all_main = []
    all_freq = []
    all_param = []
    all_time = []

    # ── Part 1: 主回测（日线） ──
    print("\n" + "─" * 50)
    print("Part 1: 日线主回测")
    print("─" * 50)

    for method, sym, name, cat, interval in assets:
        print(f"\n▸ {name} ({sym})...")
        if method == "yf":
            df = fetch_yf(sym, name, start_3y, now, interval)
        elif method == "ak_futures":
            df = fetch_akshare_futures(sym, name, start_3y, now)
        else:
            continue

        if df is None or len(df) < 60:
            print(f"  ⚠ 数据不足，跳过")
            continue

        print(f"  数据：{len(df)} bars, {df['date'].iloc[0].date()} ~ {df['date'].iloc[-1].date()}")

        for exit_mode, exit_label in [("middle_band", "中轨出场"), ("close_gt_open", "阳线出场(源码)")]:
            r = backtest(df, exit_mode=exit_mode)
            if r is None:
                continue
            r["symbol"] = sym
            r["name"] = name
            r["category"] = cat
            r["exit_mode"] = exit_label
            r["interval"] = "日线"
            all_main.append(r)
            print(f"  [{exit_label}] 笔数={r['n_trades']}, 胜率={r['win_rate']}%, "
                  f"收益={r['total_return_pct']}%, Sharpe={r['sharpe']}")

        # 参数稳定性
        print(f"  参数稳定性测试...")
        ps = parameter_stability(df, sym, name)
        if ps:
            all_param.append(ps)
            print(f"    {ps['total_combos']}种参数组合, {ps['pct_profitable']}%盈利, "
                  f"收益均值={ps['return_mean']}%±{ps['return_std']}%")

        # 时间稳定性
        ts = time_stability(df, sym, name)
        if ts:
            all_time.append(ts)
            print(f"    逐年: {ts['n_years']}年, {ts['consistency']}%年份盈利, "
                  f"年均={ts['year_return_mean']}%")

        time.sleep(0.3)

    # 国内期货
    print(f"\n▸ 国内期货...")
    futures_list = [("LC0", "碳酸锂"), ("CU0", "沪铜"), ("AU0", "沪金"),
                    ("RB0", "螺纹钢"), ("I0", "铁矿石")]
    for sym, fname in futures_list:
        try:
            df = fetch_akshare_futures(sym, fname, datetime(2022, 1, 1), now)
            if df is None or len(df) < 60:
                continue
            print(f"  {fname}: {len(df)} bars")
            for exit_mode, exit_label in [("middle_band", "中轨出场"), ("close_gt_open", "阳线出场(源码)")]:
                r = backtest(df, exit_mode=exit_mode)
                if r is None:
                    continue
                r["symbol"] = sym
                r["name"] = fname
                r["category"] = "期货-国内"
                r["exit_mode"] = exit_label
                r["interval"] = "日线"
                all_main.append(r)
                print(f"    [{exit_label}] 笔数={r['n_trades']}, 胜率={r['win_rate']}%, 收益={r['total_return_pct']}%")
            ps = parameter_stability(df, sym, fname)
            if ps:
                all_param.append(ps)
            ts = time_stability(df, sym, fname)
            if ts:
                all_time.append(ts)
        except Exception as e:
            print(f"  ✗ {fname}: {e}")

    # ── Part 2: 多频率对比 ──
    print("\n" + "─" * 50)
    print("Part 2: 多频率回测对比")
    print("─" * 50)

    for method, sym, name, cat in freq_assets:
        for interval in intervals:
            print(f"\n▸ {name} ({sym}) @ {interval}...")
            df = fetch_yf(sym, name, start_3y, now, interval)
            if df is None or len(df) < 30:
                print(f"  ⚠ 数据不足")
                continue

            print(f"  数据：{len(df)} bars")
            r = backtest(df, exit_mode="middle_band")
            if r is None:
                continue
            r["symbol"] = sym
            r["name"] = name
            r["category"] = cat
            r["exit_mode"] = "中轨出场"
            r["interval"] = interval
            all_freq.append(r)
            print(f"  笔数={r['n_trades']}, 胜率={r['win_rate']}%, 收益={r['total_return_pct']}%, Sharpe={r['sharpe']}")

            # 参数稳定性（仅日线和1h）
            if interval in ("1d", "1h"):
                ps = parameter_stability(df, f"{sym}_{interval}", f"{name} ({interval})")
                if ps:
                    all_param.append(ps)

            time.sleep(0.3)

    # ── 保存全部结果 ──
    output = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "main_results": [{k: v for k, v in r.items() if k != "trades"} for r in all_main],
        "main_trades": {f"{r['symbol']}_{r['exit_mode']}": r["trades"] for r in all_main},
        "freq_results": [{k: v for k, v in r.items() if k != "trades"} for r in all_freq],
        "freq_trades": {f"{r['symbol']}_{r['interval']}": r["trades"] for r in all_freq},
        "param_stability": all_param,
        "time_stability": all_time,
    }

    out_file = OUTPUT_DIR / "full_results_v2.json"
    with open(out_file, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 全部结果保存到 {out_file}")
    print(f"  主回测: {len(all_main)} 组")
    print(f"  频率对比: {len(all_freq)} 组")
    print(f"  参数稳定性: {len(all_param)} 标的")
    print(f"  时间稳定性: {len(all_time)} 标的")

    return output


if __name__ == "__main__":
    run_full()
