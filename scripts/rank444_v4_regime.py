#!/usr/bin/env python3
"""
Rank 444 — v4: 牛熊regime分析 + 多频率对比
==========================================
1) 日线 15年+ (覆盖多个牛熊周期)
2) Regime检测: 200日均线 + 滚动6个月收益
3) 多频率: 1d / 12h / 4h / 1h / 15m (取yfinance最大可用)
4) 分regime统计收益
"""

import json, time, warnings
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

OUT = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb")
OUT.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 指标 & 回测
# ═══════════════════════════════════════════════════════════════

def calc_rsi(s, p=7):
    d = s.diff()
    g, l = d.clip(lower=0), -d.clip(upper=0)
    ag = g.ewm(com=p-1, min_periods=p).mean()
    al = l.ewm(com=p-1, min_periods=p).mean()
    return 100 - 100/(1 + ag/al)

def calc_bb(s, p=20, m=2.0):
    b = s.rolling(p).mean()
    d = m * s.rolling(p).std()
    return b, b+d, b-d


def backtest_with_regime(df, rp=7, rl=30, bp=20, bm=2.0, exit_mode="mid", stop_pct=None):
    """回测 + 按regime分组统计"""
    close = df["close"].values
    rsi = calc_rsi(df["close"], rp).values
    bb_mid, _, bb_low = calc_bb(df["close"], bp, bm)
    bb_mid = bb_mid.values; bb_low = bb_low.values

    # Regime: 200日均线上方=bull, 下方=bear
    ma200 = df["close"].rolling(200, min_periods=50).mean().values
    # 更短的regime: 50日均线
    ma50 = df["close"].rolling(50, min_periods=20).mean().values

    mask = ~(np.isnan(rsi) | np.isnan(bb_mid) | np.isnan(bb_low))
    close = close[mask]; rsi = rsi[mask]; bb_mid = bb_mid[mask]; bb_low = bb_low[mask]
    ma200 = ma200[mask]; ma50 = ma50[mask]
    dates = df["date"].values[mask] if "date" in df.columns else np.arange(len(close))

    n = len(close)
    if n < 10: return None

    trades = []
    pos = None
    for i in range(1, n):
        if pos is None:
            if rsi[i] < rl and close[i] < bb_low[i]:
                # 判定入场时的regime
                if not np.isnan(ma200[i]):
                    regime = "bull" if close[i] > ma200[i] else "bear"
                else:
                    regime = "unknown"
                pos = {"ep":close[i],"ei":i,"ed":str(dates[i])[:10],"regime":regime}
        else:
            pnl = (close[i]/pos["ep"]-1)*100
            exit_sl = stop_pct is not None and pnl <= -stop_pct
            exit_mid = exit_mode=="mid" and close[i]>bb_mid[i]
            if exit_sl or exit_mid:
                net = pnl - 0.2
                trades.append({"ed":pos["ed"],"xd":str(dates[i])[:10],
                               "ep":round(pos["ep"],4),"xp":round(close[i],4),
                               "pnl":round(pnl,4),"net":round(net,4),
                               "bars":i-pos["ei"],"regime":pos["regime"],
                               "exit":"止损" if exit_sl else "中轨"})
                pos = None

    if not trades:
        return {"n":0,"wr":0,"ret":0,"ann":0,"mdd":0,"sh":0,"pf":0,"ab":0,"ap":0,
                "trades":[],"by_regime":{},
                "ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}

    t = pd.DataFrame(trades)
    w = t[t["net"]>0]; l = t[t["net"]<=0]
    nt = len(t); wr = len(w)/nt*100
    cum = (1+t["net"]/100).cumprod()
    ret = (cum.iloc[-1]-1)*100
    yrs = max((pd.to_datetime(df["date"].iloc[-1])-pd.to_datetime(df["date"].iloc[0])).days/365.25, 0.01)
    ann = ((1+ret/100)**(1/yrs)-1)*100
    eq = cum.cummax(); dd = (cum-eq)/eq*100; mdd = dd.min()
    ab = max(t["bars"].mean(),1)
    sh = t["net"].mean()/t["net"].std()*np.sqrt(min(252/ab,nt)) if t["net"].std()>0 else 0
    gp = w["net"].sum() if len(w)>0 else 0
    gl = abs(l["net"].sum()) if len(l)>0 else 0.001

    # 按regime分组
    by_regime = {}
    for rg in ["bull","bear","unknown"]:
        sub = t[t["regime"]==rg]
        if len(sub)==0: continue
        sw = sub[sub["net"]>0]; sl = sub[sub["net"]<=0]
        rg_wr = len(sw)/len(sub)*100
        rg_cum = (1+sub["net"]/100).cumprod()
        rg_ret = (rg_cum.iloc[-1]-1)*100
        rg_gp = sw["net"].sum() if len(sw)>0 else 0
        rg_gl = abs(sl["net"].sum()) if len(sl)>0 else 0.001
        by_regime[rg] = {
            "n":len(sub),"wr":round(rg_wr,1),"ret":round(rg_ret,2),
            "pf":round(rg_gp/rg_gl,2),"ap":round(sub["net"].mean(),4),
            "mdd":round(((rg_cum.cummax()-rg_cum)/rg_cum.cummax()*100).min(),2) if len(sub)>1 else 0,
            "avg_bars":round(sub["bars"].mean(),1),
        }

    return {"n":nt,"wr":round(wr,2),"ret":round(ret,2),"ann":round(ann,2),
            "mdd":round(mdd,2),"sh":round(sh,3),"pf":round(gp/gl,3),
            "ab":round(ab,1),"ap":round(t["net"].mean(),4),
            "trades":trades,"by_regime":by_regime,
            "ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}


# ═══════════════════════════════════════════════════════════════
# Regime 时间占比统计
# ═══════════════════════════════════════════════════════════════

def regime_time_pct(df):
    """统计整个数据区间内bull/bear各占多少时间"""
    close = df["close"].values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values
    valid = ~np.isnan(ma200)
    c = close[valid]; m = ma200[valid]
    bull = (c > m).sum()
    bear = (c <= m).sum()
    total = len(c)
    return {
        "total_bars": total,
        "bull_pct": round(bull/total*100,1) if total>0 else 0,
        "bear_pct": round(bear/total*100,1) if total>0 else 0,
    }


# ═══════════════════════════════════════════════════════════════
# 数据获取
# ═══════════════════════════════════════════════════════════════

def fetch(sym, start, end, iv="1d"):
    import yfinance as yf
    try:
        t = yf.Ticker(sym)
        # yfinance限制
        if iv == "15m":
            start = max(start, datetime.now()-timedelta(days=59))
        elif iv == "1h":
            start = max(start, datetime.now()-timedelta(days=729))
        df = t.history(start=start, end=end, interval=iv, auto_adjust=True)
        if df.empty: return None
        df = df.reset_index()
        df = df.rename(columns={"Date":"date","Datetime":"date","Open":"open","High":"high",
                                "Low":"low","Close":"close","Volume":"volume"})
        if "date" not in df.columns: df["date"] = df.index
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        return df[["date","open","high","low","close","volume"]].dropna().sort_values("date").reset_index(drop=True)
    except Exception as e:
        print(f"  ✗ {sym}({iv}): {e}")
        return None


def resample_ohlcv(df, rule):
    """将分钟级OHLCV重采样到更大周期"""
    df = df.copy()
    df = df.set_index("date")
    o = df["open"].resample(rule).first()
    h = df["high"].resample(rule).max()
    l = df["low"].resample(rule).min()
    c = df["close"].resample(rule).last()
    v = df["volume"].resample(rule).sum()
    out = pd.DataFrame({"open":o,"high":h,"low":l,"close":c,"volume":v}).dropna()
    out = out.reset_index()
    return out


# ═══════════════════════════════════════════════════════════════
# 参数网格（快速版）
# ═══════════════════════════════════════════════════════════════

def param_grid_with_regime(df):
    """108种参数组合 + regime分析"""
    rsi_ps = [5, 7, 10, 14]
    rsi_ls = [25, 30, 35]
    bb_ps  = [15, 20, 25]
    bb_ms  = [1.5, 2.0, 2.5]

    close = df["close"].values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values

    # 预计算
    rsi_c = {rp: calc_rsi(df["close"],rp).values for rp in rsi_ps}
    bb_c = {}
    for bp in bb_ps:
        for bm in bb_ms:
            mid,_,low = calc_bb(df["close"],bp,bm)
            bb_c[(bp,bm)] = (mid.values, low.values)

    base_mask = np.ones(len(close),dtype=bool)
    for rp in rsi_ps: base_mask &= ~np.isnan(rsi_c[rp])
    for key in bb_c: base_mask &= ~np.isnan(bb_c[key][0]) & ~np.isnan(bb_c[key][1])
    base_mask &= ~np.isnan(ma200)

    c = close[base_mask]; m200 = ma200[base_mask]

    results = []
    for rp,rl,bp,bm in product(rsi_ps, rsi_ls, bb_ps, bb_ms):
        r = rsi_c[rp][base_mask]
        mid, low = bb_c[(bp,bm)]; mid = mid[base_mask]; low = low[base_mask]

        trades_net, trades_regime = [], []
        pos = None
        for i in range(1, len(c)):
            if pos is None:
                if r[i] < rl and c[i] < low[i]:
                    regime = "bull" if c[i] > m200[i] else "bear"
                    pos = (c[i], regime)
            else:
                pnl = (c[i]/pos[0]-1)*100
                if c[i] > mid[i]:
                    trades_net.append(pnl - 0.2)
                    trades_regime.append(pos[1])
                    pos = None

        if not trades_net: continue
        arr = np.array(trades_net)
        wins = arr[arr>0]; losses = arr[arr<=0]
        wr = len(wins)/len(arr)*100
        cum = np.cumprod(1+arr/100)
        ret = (cum[-1]-1)*100
        gp = wins.sum() if len(wins)>0 else 0
        gl = abs(losses.sum()) if len(losses)>0 else 0.001
        sh = arr.mean()/arr.std()*np.sqrt(min(252/8,len(arr))) if arr.std()>0 else 0
        pk = np.maximum.accumulate(cum)
        mdd = ((cum-pk)/pk*100).min()

        # Regime breakdown
        bull_idx = [j for j,tr in enumerate(trades_regime) if tr=="bull"]
        bear_idx = [j for j,tr in enumerate(trades_regime) if tr=="bear"]
        bull_arr = arr[bull_idx] if bull_idx else np.array([])
        bear_arr = arr[bear_idx] if bear_idx else np.array([])

        rg = {}
        if len(bull_arr)>0:
            b_w = bull_arr[bull_arr>0]
            rg["bull"] = {"n":len(bull_arr),"wr":round(len(b_w)/len(bull_arr)*100,1),
                          "ap":round(bull_arr.mean(),4),
                          "ret":round((np.cumprod(1+bull_arr/100)[-1]-1)*100,2)}
        if len(bear_arr)>0:
            b_w = bear_arr[bear_arr>0]
            rg["bear"] = {"n":len(bear_arr),"wr":round(len(b_w)/len(bear_arr)*100,1),
                          "ap":round(bear_arr.mean(),4),
                          "ret":round((np.cumprod(1+bear_arr/100)[-1]-1)*100,2)}

        results.append({"rp":rp,"rl":rl,"bp":bp,"bm":bm,
                        "n":len(arr),"wr":round(wr,1),"ret":round(ret,2),
                        "sh":round(sh,3),"pf":round(gp/gl,2),"mdd":round(mdd,2),
                        "by_regime":rg})

    if not results: return None
    rdf = pd.DataFrame([{k:v for k,v in r.items() if k!="by_regime"} for r in results])

    # 汇总regime
    bull_rets = [r["by_regime"].get("bull",{}).get("ret",0) for r in results if "bull" in r.get("by_regime",{})]
    bear_rets = [r["by_regime"].get("bear",{}).get("ret",0) for r in results if "bear" in r.get("by_regime",{})]

    return {
        "total":len(rdf),
        "pct_profitable":round((rdf["ret"]>0).mean()*100,1),
        "ret_mean":round(rdf["ret"].mean(),2),
        "ret_std":round(rdf["ret"].std(),2),
        "ret_median":round(rdf["ret"].median(),2),
        "ret_q25":round(rdf["ret"].quantile(0.25),2),
        "ret_q75":round(rdf["ret"].quantile(0.75),2),
        "sharpe_mean":round(rdf["sh"].mean(),3),
        "best5":rdf.nlargest(5,"ret").to_dict(orient="records"),
        "worst5":rdf.nsmallest(5,"ret").to_dict(orient="records"),
        "regime_summary": {
            "bull_ret_mean":round(np.mean(bull_rets),2) if bull_rets else None,
            "bull_ret_std":round(np.std(bull_rets),2) if bull_rets else None,
            "bear_ret_mean":round(np.mean(bear_rets),2) if bear_rets else None,
            "bear_ret_std":round(np.std(bear_rets),2) if bear_rets else None,
            "bull_count":len(bull_rets),
            "bear_count":len(bear_rets),
        }
    }


# ═══════════════════════════════════════════════════════════════
# 时间段子集回测
# ═══════════════════════════════════════════════════════════════

def period_backtest(df, label, rp=7, rl=30, bp=20, bm=2.0):
    """对特定时间段做回测"""
    r = backtest_with_regime(df, rp=rp, rl=rl, bp=bp, bm=bm)
    if r is None: return None
    r["period_label"] = label
    return r


# ═══════════════════════════════════════════════════════════════
# 多频率完整对比
# ═══════════════════════════════════════════════════════════════

def multifreq_analysis(sym, name, daily_start, now):
    """
    1d: 最长可用 (15年+)
    12h: 从1h重采样 (~2年)
    4h: 从1h重采样 (~2年)
    1h: ~2年
    15m: ~60天 (太短，仅供参考)
    """
    results = {}

    # 1d: 拉长
    print(f"    1d (长周期)...")
    df_1d = fetch(sym, daily_start, now, "1d")
    if df_1d is not None and len(df_1d)>=100:
        r = backtest_with_regime(df_1d)
        if r:
            r["bars"] = len(df_1d)
            rp = regime_time_pct(df_1d)
            r["regime_time"] = rp
            r["pg"] = param_grid_with_regime(df_1d)
            results["1d"] = r
            print(f"      {r['nb']} bars, {r['ds']}~{r['de']}")
            print(f"      n={r['n']}, ret={r['ret']}%, bull%={rp['bull_pct']}%, bear%={rp['bear_pct']}%")
            rg = r.get("by_regime",{})
            if "bull" in rg: print(f"      [bull] n={rg['bull']['n']}, ret={rg['bull']['ret']}%")
            if "bear" in rg: print(f"      [bear] n={rg['bear']['n']}, ret={rg['bear']['ret']}%")
            pg = r.get("pg",{})
            if pg:
                rs = pg.get("regime_summary",{})
                print(f"      参数网格: {pg['total']}种, {pg['pct_profitable']}%盈利")
                print(f"      regime均值: bull={rs.get('bull_ret_mean','?')}%, bear={rs.get('bear_ret_mean','?')}%")

    # 1h: ~2年
    print(f"    1h (~2年)...")
    df_1h = fetch(sym, now-timedelta(days=729), now, "1h")
    if df_1h is not None and len(df_1h)>=100:
        r = backtest_with_regime(df_1h)
        if r:
            r["bars"] = len(df_1h)
            rp = regime_time_pct(df_1h)
            r["regime_time"] = rp
            results["1h"] = r
            print(f"      {len(df_1h)} bars, n={r['n']}, ret={r['ret']}%")
            rg = r.get("by_regime",{})
            if "bull" in rg: print(f"      [bull] n={rg['bull']['n']}, ret={rg['bull']['ret']}%")
            if "bear" in rg: print(f"      [bear] n={rg['bear']['n']}, ret={rg['bear']['ret']}%")

        # 从1h重采样4h和12h
        for rule, label in [("4h","4h"),("12h","12h")]:
            print(f"    {label} (从1h重采样)...")
            df_rs = resample_ohlcv(df_1h, rule)
            if len(df_rs) >= 50:
                r = backtest_with_regime(df_rs)
                if r:
                    r["bars"] = len(df_rs)
                    rp = regime_time_pct(df_rs)
                    r["regime_time"] = rp
                    results[label] = r
                    print(f"      {len(df_rs)} bars, n={r['n']}, ret={r['ret']}%")
                    rg = r.get("by_regime",{})
                    if "bull" in rg: print(f"      [bull] n={rg['bull']['n']}, ret={rg['bull']['ret']}%")
                    if "bear" in rg: print(f"      [bear] n={rg['bear']['n']}, ret={rg['bear']['ret']}%")

    # 15m: ~60天
    print(f"    15m (~60天)...")
    df_15m = fetch(sym, now-timedelta(days=59), now, "15m")
    if df_15m is not None and len(df_15m)>=100:
        r = backtest_with_regime(df_15m)
        if r:
            r["bars"] = len(df_15m)
            r["regime_time"] = regime_time_pct(df_15m)
            results["15m"] = r
            print(f"      {len(df_15m)} bars, n={r['n']}, ret={r['ret']}%")

    return results


# ═══════════════════════════════════════════════════════════════
# 已知熊市区间回测
# ═══════════════════════════════════════════════════════════════

BEAR_PERIODS = [
    # (label, start, end, description)
    ("2008金融危机","2007-10-01","2009-03-31","标普500跌57%"),
    ("2011欧债危机","2011-05-01","2011-10-31","标普跌19%"),
    ("2015中国股灾+联储加息","2015-08-01","2016-02-29","标普跌13%"),
    ("2018Q4回调","2018-10-01","2018-12-31","标普跌20%"),
    ("2020新冠崩盘","2020-02-19","2020-03-23","标普跌34%"),
    ("2022加息熊市","2022-01-03","2022-10-12","标普跌27%"),
]


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def run():
    now = datetime.now()
    # 15年日线
    long_start = now - timedelta(days=365*15+60)

    # 核心标的（选有长历史的）
    assets = [
        ("SPY","标普500 ETF","美股"),
        ("QQQ","纳斯达克100 ETF","美股"),
        ("AAPL","苹果","美股"),
        ("MSFT","微软","美股"),
        ("GLD","黄金ETF","贵金属"),
        ("GC=F","COMEX黄金期货","贵金属"),
        ("CL=F","WTI原油期货","国际期货"),
        ("SI=F","COMEX白银期货","贵金属"),
        ("HG=F","COMEX铜期货","国际期货"),
    ]

    print("="*70)
    print("Rank 444 — v4: 牛熊regime分析 + 多频率对比")
    print("="*70)

    all_results = {}

    for sym, name, cat in assets:
        print(f"\n{'='*50}")
        print(f"▸ {name} ({sym})")
        print(f"{'='*50}")

        mf = multifreq_analysis(sym, name, long_start, now)
        all_results[sym] = {"name":name,"cat":cat,"freq_data":mf}
        time.sleep(0.5)

    # ── 已知熊市区间回测 ──
    print(f"\n{'='*70}")
    print("▸ 已知熊市区间回测 (SPY)")
    print(f"{'='*70}")

    bear_results = []
    # 先拿最长的SPY日线
    df_spy_long = fetch("SPY", long_start, now, "1d")
    if df_spy_long is not None:
        for label, bs, be, desc in BEAR_PERIODS:
            mask = (df_spy_long["date"]>=bs) & (df_spy_long["date"]<=be)
            sub = df_spy_long[mask].reset_index(drop=True)
            if len(sub)<10:
                print(f"  {label}: 数据不足({len(sub)}bars)")
                continue
            r = backtest_with_regime(sub)
            if r is None:
                print(f"  {label}: 无交易")
                continue
            # 同期buy-and-hold收益
            bh = (sub["close"].iloc[-1]/sub["close"].iloc[0]-1)*100
            bear_results.append({
                "label":label,"desc":desc,"start":bs,"end":be,
                "n":r["n"],"wr":r["wr"],"ret":r["ret"],"mdd":r["mdd"],
                "sh":r["sh"],"buyhold":round(bh,2),"alpha":round(r["ret"]-bh,2),
                "by_regime":r.get("by_regime",{}),"nb":len(sub)
            })
            print(f"  {label}: n={r['n']}, 策略={r['ret']}%, buy&hold={bh:.1f}%, alpha={r['ret']-bh:.1f}%")

    # ── 保存 ──
    output = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "version": "v4_regime",
        "description": "牛熊regime分析 + 多频率对比(1d/12h/4h/1h/15m) + 熊市区间回测",
        "freq_analysis": all_results,
        "bear_periods": bear_results,
    }
    out_file = OUT / "full_results_v4.json"
    with open(out_file, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 保存 {out_file} ({out_file.stat().st_size/1024:.0f}KB)")

    # 汇总
    print(f"\n{'='*70}")
    print("汇总")
    print(f"{'='*70}")
    for sym, fd in all_results.items():
        d1 = fd["freq_data"].get("1d",{})
        if not d1: continue
        rg = d1.get("by_regime",{})
        rt = d1.get("regime_time",{})
        pg = d1.get("pg",{})
        rs = pg.get("regime_summary",{}) if pg else {}
        print(f"  {fd['name']:15s}  总={d1['ret']:+.1f}%  "
              f"bull={rg.get('bull',{}).get('ret','?')}%({rg.get('bull',{}).get('n','?')}笔)  "
              f"bear={rg.get('bear',{}).get('ret','?')}%({rg.get('bear',{}).get('n','?')}笔)  "
              f"time: bull{rt.get('bull_pct','?')}%/bear{rt.get('bear_pct','?')}%  "
              f"网格: bull均{rs.get('bull_ret_mean','?')}%/bear均{rs.get('bear_ret_mean','?')}%")

if __name__ == "__main__":
    run()
