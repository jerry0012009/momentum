#!/usr/bin/env python3
"""
Rank 444 — RSI + Bollinger Bands 均值回复策略 回测引擎
=======================================================
策略逻辑：
  - 买入：RSI < rsilimit AND close < BB 下轨
  - 卖出（代码版）：close > open  （阳线即卖）
  - 卖出（中轨版）：close 上穿 BB 中轨

测试标的：A股 / 美股 / 黄金 / 期货（碳酸锂等）
"""

import json
import sys
import time
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ─── 策略参数 ───────────────────────────────────────────────────
RSI_PERIOD = 7
RSI_LIMIT = 30
BB_PERIOD = 20
BB_MULT = 2.0
INITIAL_CAPITAL = 100000
POSITION_PCT = 1.0  # 每次投入全部资金（单标的回测）
COMMISSION_RATE = 0.001  # 单边手续费 0.1%


# ─── 指标计算 ───────────────────────────────────────────────────
def calc_rsi(series, period=7):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_bollinger(series, period=20, mult=2.0):
    basis = series.rolling(period).mean()
    dev = mult * series.rolling(period).std()
    upper = basis + dev
    lower = basis - dev
    return basis, upper, lower


# ─── 回测引擎 ───────────────────────────────────────────────────
def backtest(df, rsi_period=RSI_PERIOD, rsi_limit=RSI_LIMIT,
             bb_period=BB_PERIOD, bb_mult=BB_MULT,
             exit_mode="middle_band",
             initial_capital=INITIAL_CAPITAL, commission=COMMISSION_RATE):
    """
    exit_mode:
      'middle_band' — 价格上穿 BB 中轨平仓
      'close_gt_open' — 阳线平仓（与源码一致）
    """
    df = df.copy()
    df["rsi"] = calc_rsi(df["close"], rsi_period)
    df["bb_mid"], df["bb_upper"], df["bb_lower"] = calc_bollinger(
        df["close"], bb_period, bb_mult
    )
    df = df.dropna().reset_index(drop=True)

    if len(df) < 2:
        return _empty_result()

    trades = []
    position = None  # {"entry_date", "entry_price", "shares"}

    for i in range(1, len(df)):
        row = df.iloc[i]
        prev = df.iloc[i - 1]

        # 开仓
        if position is None:
            if row["rsi"] < rsi_limit and row["close"] < row["bb_lower"]:
                shares = int(initial_capital * (1 - commission) / row["close"])
                if shares > 0:
                    position = {
                        "entry_date": row["date"],
                        "entry_price": row["close"],
                        "shares": shares,
                        "entry_idx": i,
                    }
        else:
            # 平仓
            should_exit = False
            if exit_mode == "middle_band":
                if row["close"] > row["bb_mid"]:
                    should_exit = True
            elif exit_mode == "close_gt_open":
                if row["close"] > row["open"]:
                    should_exit = True

            if should_exit:
                exit_price = row["close"]
                entry_cost = position["shares"] * position["entry_price"] * commission
                exit_cost = position["shares"] * exit_price * commission
                gross_pnl = position["shares"] * (exit_price - position["entry_price"])
                net_pnl = gross_pnl - entry_cost - exit_cost
                pnl_pct = (exit_price / position["entry_price"] - 1) * 100
                hold_days = i - position["entry_idx"]
                trades.append({
                    "entry_date": str(position["entry_date"]),
                    "exit_date": str(row["date"]),
                    "entry_price": round(position["entry_price"], 4),
                    "exit_price": round(exit_price, 4),
                    "shares": position["shares"],
                    "gross_pnl": round(gross_pnl, 2),
                    "net_pnl": round(net_pnl, 2),
                    "pnl_pct": round(pnl_pct, 4),
                    "hold_days": hold_days,
                    "commission": round(entry_cost + exit_cost, 2),
                })
                position = None

    return _calc_metrics(trades, initial_capital, df)


def _empty_result():
    return {
        "trades": [], "total_trades": 0, "win_rate": 0,
        "total_return_pct": 0, "annual_return_pct": 0,
        "max_drawdown_pct": 0, "sharpe": 0, "profit_factor": 0,
        "avg_hold_days": 0, "avg_pnl_pct": 0,
        "median_pnl_pct": 0, "total_net_pnl": 0,
    }


def _calc_metrics(trades, initial_capital, df):
    if not trades:
        return _empty_result()

    tdf = pd.DataFrame(trades)
    winners = tdf[tdf["net_pnl"] > 0]
    losers = tdf[tdf["net_pnl"] <= 0]
    total_trades = len(tdf)
    win_rate = len(winners) / total_trades * 100

    total_net_pnl = tdf["net_pnl"].sum()
    total_return_pct = total_net_pnl / initial_capital * 100

    # 年化收益
    if len(df) > 1:
        first_date = pd.to_datetime(df["date"].iloc[0])
        last_date = pd.to_datetime(df["date"].iloc[-1])
        years = max((last_date - first_date).days / 365.25, 0.01)
        if total_return_pct > -100:
            annual_return_pct = ((1 + total_return_pct / 100) ** (1 / years) - 1) * 100
        else:
            annual_return_pct = -100
    else:
        annual_return_pct = 0

    # 最大回撤（基于逐笔累计 PnL）
    cum_pnl = tdf["net_pnl"].cumsum()
    equity = initial_capital + cum_pnl
    running_max = equity.cummax()
    drawdown = (equity - running_max) / running_max * 100
    max_drawdown_pct = drawdown.min()

    # Sharpe（简化：按笔算）
    if tdf["pnl_pct"].std() > 0:
        sharpe = tdf["pnl_pct"].mean() / tdf["pnl_pct"].std() * np.sqrt(252 / max(tdf["hold_days"].mean(), 1))
    else:
        sharpe = 0

    # Profit Factor
    gross_profit = winners["net_pnl"].sum() if len(winners) > 0 else 0
    gross_loss = abs(losers["net_pnl"].sum()) if len(losers) > 0 else 0.01
    profit_factor = gross_profit / gross_loss

    return {
        "trades": trades,
        "total_trades": total_trades,
        "win_rate": round(win_rate, 2),
        "total_return_pct": round(total_return_pct, 2),
        "annual_return_pct": round(annual_return_pct, 2),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "sharpe": round(sharpe, 3),
        "profit_factor": round(profit_factor, 3),
        "avg_hold_days": round(tdf["hold_days"].mean(), 1),
        "avg_pnl_pct": round(tdf["pnl_pct"].mean(), 4),
        "median_pnl_pct": round(tdf["pnl_pct"].median(), 4),
        "total_net_pnl": round(total_net_pnl, 2),
    }


# ─── 数据获取 ───────────────────────────────────────────────────
def fetch_akshare_stock(symbol, name, start, end):
    """获取A股日线数据"""
    import akshare as ak
    try:
        df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                start_date=start.strftime("%Y%m%d"),
                                end_date=end.strftime("%Y%m%d"),
                                adjust="qfq")
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume"
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date").reset_index(drop=True)
        print(f"  ✓ {name} ({symbol}): {len(df)} bars")
        return df
    except Exception as e:
        print(f"  ✗ {name} ({symbol}): {e}")
        return None


def fetch_akshare_futures(symbol, name, start, end):
    """获取期货日线数据"""
    import akshare as ak
    try:
        df = ak.futures_zh_daily_sina(symbol=symbol)
        df = df.rename(columns={
            "date": "date", "open": "open", "high": "high",
            "low": "low", "close": "close", "volume": "volume"
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df[(df["date"] >= start) & (df["date"] <= end)]
        df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date").reset_index(drop=True)
        print(f"  ✓ {name} ({symbol}): {len(df)} bars")
        return df
    except Exception as e:
        print(f"  ✗ {name} ({symbol}): {e}")
        return None


def fetch_yfinance(symbol, name, start, end):
    """获取 yfinance 数据"""
    import yfinance as yf
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start, end=end, auto_adjust=True)
        df = df.reset_index()
        df = df.rename(columns={"Date": "date", "Open": "open", "High": "high",
                                "Low": "low", "Close": "close", "Volume": "volume"})
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        df = df[["date", "open", "high", "low", "close", "volume"]].sort_values("date").reset_index(drop=True)
        print(f"  ✓ {name} ({symbol}): {len(df)} bars")
        return df
    except Exception as e:
        print(f"  ✗ {name} ({symbol}): {e}")
        return None


# ─── 标的定义 ───────────────────────────────────────────────────
def get_symbols():
    """返回 (fetch_func, symbol, display_name, category) 列表"""
    now = datetime.now()
    start_3y = now - timedelta(days=365 * 3 + 30)
    start_2y = now - timedelta(days=365 * 2 + 30)

    symbols = [
        # A股 — 大盘蓝筹 + 热门赛道
        (fetch_akshare_stock, "600519", "贵州茅台", "A股", start_3y, now),
        (fetch_akshare_stock, "601318", "中国平安", "A股", start_3y, now),
        (fetch_akshare_stock, "300750", "宁德时代", "A股", start_3y, now),
        (fetch_akshare_stock, "600036", "招商银行", "A股", start_3y, now),
        (fetch_akshare_stock, "000858", "五粮液", "A股", start_3y, now),

        # 美股 — 科技巨头 + 指数 ETF
        (fetch_yfinance, "AAPL", "苹果 AAPL", "美股", start_3y, now),
        (fetch_yfinance, "TSLA", "特斯拉 TSLA", "美股", start_3y, now),
        (fetch_yfinance, "SPY", "标普500 ETF", "美股", start_3y, now),
        (fetch_yfinance, "QQQ", "纳斯达克100 ETF", "美股", start_3y, now),

        # 黄金 / 贵金属
        (fetch_yfinance, "GC=F", "COMEX黄金期货", "黄金", start_3y, now),
        (fetch_yfinance, "GLD", "黄金ETF GLD", "黄金", start_3y, now),

        # 期货 — 国际
        (fetch_yfinance, "CL=F", "WTI原油期货", "期货", start_3y, now),
        (fetch_yfinance, "HG=F", "COMEX铜期货", "期货", start_3y, now),
    ]

    return symbols


# ─── 主流程 ───────────────────────────────────────────────────
def run_all():
    print("=" * 60)
    print("Rank 444 — RSI + BB 均值回复策略回测")
    print("=" * 60)

    symbols = get_symbols()
    all_results = []

    for fetch_func, sym, name, category, start, end in symbols:
        print(f"\n▸ 获取数据: {name} ({sym})...")
        df = fetch_func(sym, name, start, end)
        if df is None or len(df) < 60:
            print(f"  ⚠ 数据不足，跳过")
            continue

        # 两种 exit mode
        for exit_mode, exit_label in [
            ("middle_band", "中轨平仓"),
            ("close_gt_open", "阳线平仓(源码)")
        ]:
            result = backtest(df, exit_mode=exit_mode)
            result["symbol"] = sym
            result["name"] = name
            result["category"] = category
            result["exit_mode"] = exit_label
            result["data_bars"] = len(df)
            result["data_start"] = str(df["date"].iloc[0].date())
            result["data_end"] = str(df["date"].iloc[-1].date())
            all_results.append(result)
            print(f"  [{exit_label}] trades={result['total_trades']}, "
                  f"win={result['win_rate']}%, "
                  f"return={result['total_return_pct']}%, "
                  f"sharpe={result['sharpe']}")

        time.sleep(0.3)  # rate limit

    # 尝试碳酸锂期货
    print(f"\n▸ 尝试碳酸锂期货...")
    try:
        import akshare as ak
        # 碳酸锂主力合约
        for sym in ["LC0", "lc2401", "lc2406", "lc2407", "LC2401"]:
            try:
                df = fetch_akshare_futures(sym, f"碳酸锂 {sym}", datetime(2023, 1, 1), datetime.now())
                if df is not None and len(df) > 60:
                    for exit_mode, exit_label in [("middle_band", "中轨平仓"), ("close_gt_open", "阳线平仓(源码)")]:
                        result = backtest(df, exit_mode=exit_mode)
                        result["symbol"] = sym
                        result["name"] = f"碳酸锂 {sym}"
                        result["category"] = "期货"
                        result["exit_mode"] = exit_label
                        result["data_bars"] = len(df)
                        result["data_start"] = str(df["date"].iloc[0].date())
                        result["data_end"] = str(df["date"].iloc[-1].date())
                        all_results.append(result)
                    break
            except:
                continue
    except:
        print("  ⚠ 碳酸锂数据获取失败")

    # 尝试更多国内期货
    print(f"\n▸ 尝试国内期货（沪铜/沪金/螺纹钢）...")
    try:
        import akshare as ak
        futures_symbols = [
            ("CU0", "沪铜主力"),
            ("AU0", "沪金主力"),
            ("RB0", "螺纹钢主力"),
            ("I0", "铁矿石主力"),
        ]
        for sym, fname in futures_symbols:
            try:
                df = fetch_akshare_futures(sym, fname, datetime(2022, 1, 1), datetime.now())
                if df is not None and len(df) > 60:
                    for exit_mode, exit_label in [("middle_band", "中轨平仓"), ("close_gt_open", "阳线平仓(源码)")]:
                        result = backtest(df, exit_mode=exit_mode)
                        result["symbol"] = sym
                        result["name"] = fname
                        result["category"] = "期货"
                        result["exit_mode"] = exit_label
                        result["data_bars"] = len(df)
                        result["data_start"] = str(df["date"].iloc[0].date())
                        result["data_end"] = str(df["date"].iloc[-1].date())
                        all_results.append(result)
            except Exception as e:
                print(f"  ⚠ {fname}: {e}")
    except:
        pass

    # 保存结果
    output_dir = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb")
    output_dir.mkdir(parents=True, exist_ok=True)

    results_file = output_dir / "backtest_results.json"
    with open(results_file, "w") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n✓ 结果保存到 {results_file}")

    return all_results


if __name__ == "__main__":
    results = run_all()
    print(f"\n{'=' * 60}")
    print(f"共完成 {len(results)} 组回测")
