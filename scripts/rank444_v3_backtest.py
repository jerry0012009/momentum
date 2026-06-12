#!/usr/bin/env python3
"""
Rank 444 — RSI+BB 扩展回测 v3 (向量化加速版)
=============================================
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
# 向量化指标
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


# ═══════════════════════════════════════════════════════════════
# 快速回测（numpy版，不含逐笔交易明细）
# ═══════════════════════════════════════════════════════════════

def fast_backtest(close_arr, rsi_arr, bb_mid, bb_low, exit_mode="mid", stop_pct=None):
    """
    纯numpy快速回测，返回汇总指标。不记录逐笔交易。
    exit_mode: 'mid'=中轨出场, 'co'=阳线出场(需要open_arr)
    stop_pct: 止损百分比 (如5.0=5%止损), None=不止损
    """
    n = len(close_arr)
    trades_net = []
    pos_entry = None

    for i in range(1, n):
        if pos_entry is None:
            if rsi_arr[i] < 30 and close_arr[i] < bb_low[i]:
                pos_entry = close_arr[i]
        else:
            pnl_pct = (close_arr[i] / pos_entry - 1) * 100
            should_exit = False
            if stop_pct is not None and pnl_pct <= -stop_pct:
                should_exit = True
            elif exit_mode == "mid" and close_arr[i] > bb_mid[i]:
                should_exit = True
            if should_exit:
                trades_net.append(pnl_pct - 0.2)  # 双边手续费0.2%
                pos_entry = None

    if not trades_net:
        return {"n":0,"wr":0,"ret":0,"sh":0,"pf":0,"mdd":0,"ap":0}
    arr = np.array(trades_net)
    wins = arr[arr > 0]
    losses = arr[arr <= 0]
    wr = len(wins)/len(arr)*100
    cum = np.cumprod(1 + arr/100)
    ret = (cum[-1]-1)*100
    peak = np.maximum.accumulate(cum)
    dd = (cum-peak)/peak*100
    mdd = dd.min()
    sh = arr.mean()/arr.std()*np.sqrt(min(252/max(arr.mean()*0+8,1), len(arr))) if arr.std()>0 else 0
    gp = wins.sum() if len(wins)>0 else 0
    gl = abs(losses.sum()) if len(losses)>0 else 0.001
    return {"n":len(arr),"wr":round(wr,1),"ret":round(ret,2),
            "sh":round(sh,3),"pf":round(gp/gl,2),"mdd":round(mdd,2),
            "ap":round(arr.mean(),4)}


def full_backtest(df, rp=7, rl=30, bp=20, bm=2.0, exit_mode="mid", stop_pct=None):
    """完整回测（含交易明细）用于主回测"""
    close = df["close"].values
    rsi = calc_rsi(df["close"], rp).values
    bb_mid, _, bb_low = calc_bb(df["close"], bp, bm)
    bb_mid = bb_mid.values; bb_low = bb_low.values

    # 去NaN
    mask = ~(np.isnan(rsi) | np.isnan(bb_mid) | np.isnan(bb_low))
    close = close[mask]; rsi = rsi[mask]; bb_mid = bb_mid[mask]; bb_low = bb_low[mask]
    dates = df["date"].values[mask] if "date" in df.columns else np.arange(len(close))

    n = len(close)
    if n < 10: return None

    trades = []
    pos = None
    for i in range(1, n):
        if pos is None:
            if rsi[i] < rl and close[i] < bb_low[i]:
                pos = {"ep":close[i],"ei":i,"ed":str(dates[i])[:10]}
        else:
            pnl = (close[i]/pos["ep"]-1)*100
            exit_sl = stop_pct is not None and pnl <= -stop_pct
            exit_mid = exit_mode=="mid" and close[i]>bb_mid[i]
            exit_co = exit_mode=="co" and close[i]>df.iloc[mask.nonzero()[0][i]]["open"] if exit_mode=="co" else False
            if exit_sl or exit_mid or exit_co:
                net = pnl - 0.2
                trades.append({"ed":pos["ed"],"xd":str(dates[i])[:10],
                               "ep":round(pos["ep"],4),"xp":round(close[i],4),
                               "pnl":round(pnl,4),"net":round(net,4),
                               "bars":i-pos["ei"]})
                pos = None

    if not trades:
        return {"n":0,"wr":0,"ret":0,"ann":0,"mdd":0,"sh":0,"pf":0,"ab":0,"ap":0,"mp":0,
                "trades":[],"ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}

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

    return {"n":nt,"wr":round(wr,2),"ret":round(ret,2),"ann":round(ann,2),
            "mdd":round(mdd,2),"sh":round(sh,3),"pf":round(gp/gl,3),
            "ab":round(ab,1),"ap":round(t["net"].mean(),4),"mp":round(t["net"].median(),4),
            "trades":trades,
            "ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}


# ═══════════════════════════════════════════════════════════════
# 快速参数网格（用numpy快回测）
# ═══════════════════════════════════════════════════════════════

def param_grid_fast(df, exit_mode="mid"):
    """快速网格搜索，预计算指标避免重复计算"""
    close = df["close"].values
    rsi_periods = [3, 5, 7, 10, 14, 21]
    rsi_limits = [20, 25, 30, 35, 40]
    bb_periods = [10, 15, 20, 25, 30]
    bb_mults = [1.0, 1.5, 2.0, 2.5, 3.0]

    # 预计算所有RSI和BB
    rsi_cache = {}
    for rp in rsi_periods:
        rsi_cache[rp] = calc_rsi(df["close"], rp).values

    bb_cache = {}
    for bp in bb_periods:
        for bm in bb_mults:
            mid, _, low = calc_bb(df["close"], bp, bm)
            bb_cache[(bp,bm)] = (mid.values, low.values)

    # 去NaN mask（取所有指标的交集）
    base_mask = np.ones(len(close), dtype=bool)
    for rp in rsi_periods:
        base_mask &= ~np.isnan(rsi_cache[rp])
    for key in bb_cache:
        base_mask &= ~np.isnan(bb_cache[key][0]) & ~np.isnan(bb_cache[key][1])

    c = close[base_mask]

    results = []
    for rp, rl, bp, bm in product(rsi_periods, rsi_limits, bb_periods, bb_mults):
        r = rsi_cache[rp][base_mask]
        mid, low = bb_cache[(bp,bm)]
        mid = mid[base_mask]; low = low[base_mask]

        # 快速回测
        trades_net = []
        pos = None
        for i in range(1, len(c)):
            if pos is None:
                if r[i] < rl and c[i] < low[i]:
                    pos = c[i]
            else:
                pnl = (c[i]/pos-1)*100
                if exit_mode=="mid" and c[i]>mid[i]:
                    trades_net.append(pnl - 0.2)
                    pos = None
        if trades_net:
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
            results.append({"rp":rp,"rl":rl,"bp":bp,"bm":bm,
                            "n":len(arr),"wr":round(wr,1),"ret":round(ret,2),
                            "sh":round(sh,3),"pf":round(gp/gl,2),"mdd":round(mdd,2)})

    if not results:
        return None
    rdf = pd.DataFrame(results)

    # 分组统计
    def group_by(col, vals):
        out = {}
        for v in vals:
            sub = rdf[rdf[col]==v]
            if len(sub)==0: continue
            out[str(v)] = {
                "count":len(sub),
                "pct_profit":round((sub["ret"]>0).mean()*100,1),
                "ret_mean":round(sub["ret"].mean(),2),
                "ret_std":round(sub["ret"].std(),2),
                "sharpe_mean":round(sub["sh"].mean(),3),
            }
        return out

    return {
        "total": len(rdf),
        "profitable": int((rdf["ret"]>0).sum()),
        "pct_profitable": round((rdf["ret"]>0).mean()*100,1),
        "ret_mean": round(rdf["ret"].mean(),2),
        "ret_std": round(rdf["ret"].std(),2),
        "ret_median": round(rdf["ret"].median(),2),
        "ret_min": round(rdf["ret"].min(),2),
        "ret_max": round(rdf["ret"].max(),2),
        "ret_q25": round(rdf["ret"].quantile(0.25),2),
        "ret_q75": round(rdf["ret"].quantile(0.75),2),
        "sharpe_mean": round(rdf["sh"].mean(),3),
        "sharpe_std": round(rdf["sh"].std(),3),
        "best10": rdf.nlargest(10,"ret").to_dict(orient="records"),
        "worst10": rdf.nsmallest(10,"ret").to_dict(orient="records"),
        "by_rsi_period": group_by("rp", rsi_periods),
        "by_rsi_limit": group_by("rl", rsi_limits),
        "by_bb_period": group_by("bp", bb_periods),
        "by_bb_mult": group_by("bm", bb_mults),
    }


# ═══════════════════════════════════════════════════════════════
# 止损测试
# ═══════════════════════════════════════════════════════════════

def stop_loss_sweep(df):
    stops = [None, 3, 5, 8, 10, 15]
    out = []
    for sl in stops:
        r = full_backtest(df, stop_pct=sl)
        if r is None: continue
        out.append({
            "stop": sl if sl else "无",
            "n":r["n"],"wr":r["wr"],"ret":r["ret"],"ann":r["ann"],
            "mdd":r["mdd"],"sh":r["sh"],"pf":r["pf"],
        })
    return out


# ═══════════════════════════════════════════════════════════════
# 时间稳定性
# ═══════════════════════════════════════════════════════════════

def time_stability(df, exit_mode="mid"):
    df = df.copy()
    df["date_dt"] = pd.to_datetime(df["date"])
    df["year"] = df["date_dt"].dt.year
    df["quarter"] = df["date_dt"].dt.to_period("Q")

    yearly = []
    for y in sorted(df["year"].unique()):
        ydf = df[df["year"]==y].reset_index(drop=True)
        if len(ydf)<30: continue
        r = full_backtest(ydf, exit_mode=exit_mode)
        if r is None: continue
        yearly.append({"period":str(int(y)),"n":r["n"],"wr":r["wr"],"ret":r["ret"],
                        "sh":r["sh"],"mdd":r["mdd"],"nb":len(ydf)})

    quarterly = []
    for q in sorted(df["quarter"].unique()):
        qdf = df[df["quarter"]==q].reset_index(drop=True)
        if len(qdf)<15: continue
        r = full_backtest(qdf, exit_mode=exit_mode)
        if r is None: continue
        quarterly.append({"period":str(q),"n":r["n"],"wr":r["wr"],"ret":r["ret"],
                          "sh":r["sh"],"mdd":r["mdd"],"nb":len(qdf)})

    rolling = []
    dates = df["date_dt"].sort_values()
    if len(dates) >= 120:
        wd, sd = 365, 182
        cur = dates.iloc[0]; end = dates.iloc[-1]
        while cur + timedelta(days=wd) <= end:
            wdf = df[(df["date_dt"]>=cur)&(df["date_dt"]<cur+timedelta(days=wd))].reset_index(drop=True)
            if len(wdf)>=60:
                r = full_backtest(wdf, exit_mode=exit_mode)
                if r:
                    rolling.append({"start":str(cur.date()),"end":str((cur+timedelta(days=wd)).date()),
                                    "n":r["n"],"wr":r["wr"],"ret":r["ret"],"sh":r["sh"],"mdd":r["mdd"]})
            cur += timedelta(days=sd)

    def summarize(lst):
        if not lst: return {}
        d = pd.DataFrame(lst)
        return {"count":len(lst),"positive":int((d["ret"]>0).sum()),
                "consistency":round((d["ret"]>0).mean()*100,1),
                "ret_mean":round(d["ret"].mean(),2),"ret_std":round(d["ret"].std(),2),
                "ret_min":round(d["ret"].min(),2),"ret_max":round(d["ret"].max(),2)}

    return {"yearly":yearly,"quarterly":quarterly,"rolling":rolling,
            "ysum":summarize(yearly),"qsum":summarize(quarterly),"rsum":summarize(rolling)}


# ═══════════════════════════════════════════════════════════════
# 数据获取
# ═══════════════════════════════════════════════════════════════

def fetch(sym, start, end, iv="1d"):
    import yfinance as yf
    try:
        t = yf.Ticker(sym)
        if iv == "1h":
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


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def run():
    now = datetime.now()
    start = now - timedelta(days=365*3+60)

    assets = [
        ("SPY","标普500 ETF","美股"),("QQQ","纳斯达克100 ETF","美股"),
        ("AAPL","苹果","美股"),("TSLA","特斯拉","美股"),("MSFT","微软","美股"),
        ("GC=F","COMEX黄金期货","贵金属"),("GLD","黄金ETF","贵金属"),
        ("SI=F","COMEX白银期货","贵金属"),
        ("CL=F","WTI原油期货","国际期货"),("HG=F","COMEX铜期货","国际期货"),
    ]

    print("="*70)
    print("Rank 444 — RSI+BB 扩展回测 v3 (750参数组合)")
    print("="*70)

    data_cache = {}
    all_main, all_param, all_time, all_sl = [], [], [], []

    # ── 主回测 ──
    print("\n▶ Part 1: 日线主回测")
    for sym, name, cat in assets:
        print(f"\n  ▸ {name} ({sym})...")
        df = fetch(sym, start, now)
        if df is None or len(df)<60:
            print("    ⚠ 数据不足"); continue
        data_cache[sym] = df
        print(f"    {len(df)} bars")

        for em, el in [("mid","中轨出场"),("co","阳线出场")]:
            r = full_backtest(df, exit_mode=em)
            if r is None: continue
            r.update({"sym":sym,"name":name,"cat":cat,"exit":el})
            all_main.append(r)
            print(f"    [{el}] n={r['n']}, wr={r['wr']}%, ret={r['ret']}%, sh={r['sh']}")

        t0 = time.time()
        pg = param_grid_fast(df)
        dt = time.time()-t0
        if pg:
            all_param.append({"sym":sym,"name":name,"cat":cat,"grid":pg})
            print(f"    参数网格: {pg['total']}种, {pg['pct_profitable']}%盈利, "
                  f"收益[{pg['ret_q25']},{pg['ret_median']},{pg['ret_q75']}], 耗时{dt:.1f}s")

        ts = time_stability(df)
        ts.update({"sym":sym,"name":name,"cat":cat})
        all_time.append(ts)
        ys=ts.get("ysum",{}); qs=ts.get("qsum",{}); rs=ts.get("rsum",{})
        print(f"    时间: 年{ys.get('positive',0)}/{ys.get('count',0)}({ys.get('consistency',0)}%), "
              f"季{qs.get('positive',0)}/{qs.get('count',0)}({qs.get('consistency',0)}%), "
              f"滚动{rs.get('positive',0)}/{rs.get('count',0)}({rs.get('consistency',0)}%)")

        sl = stop_loss_sweep(df)
        if sl:
            all_sl.append({"sym":sym,"name":name,"results":sl})
            for s in sl:
                if s["stop"]!="无":
                    print(f"    SL={s['stop']}%: n={s['n']}, ret={s['ret']}%, mdd={s['mdd']}%")
        time.sleep(0.2)

    # ── 频率对比 ──
    print("\n▶ Part 2: 频率对比")
    freq_data = {}
    for sym, name in [("SPY","标普500"),("AAPL","苹果"),("GC=F","黄金期货")]:
        print(f"\n  ▸ {name}...")
        fd = {}
        for iv in ["1d","1h"]:
            df = fetch(sym, start, now, iv)
            if df is None or len(df)<30: continue
            r = full_backtest(df, exit_mode="mid")
            if r is None: continue
            fd[iv] = {"n":r["n"],"wr":r["wr"],"ret":r["ret"],"sh":r["sh"],"mdd":r["mdd"],"bars":len(df)}
            print(f"    {iv}: n={r['n']}, ret={r['ret']}%, sh={r['sh']}")
            if iv=="1d":
                pg = param_grid_fast(df)
                fd[iv]["param_grid"] = pg
                if pg:
                    print(f"      参数网格: {pg['total']}种, {pg['pct_profitable']}%盈利")
            time.sleep(0.2)
        freq_data[sym] = {"name":name,"data":fd}

    # ── 保存 ──
    output = {
        "generated_at": now.strftime("%Y-%m-%d %H:%M"),
        "version": "v3_expanded",
        "param_grid_size": "750 (6 RSI periods × 5 RSI limits × 5 BB periods × 5 BB mults)",
        "main": [{k:v for k,v in r.items()} for r in all_main],
        "param_grid": all_param,
        "time_stability": all_time,
        "stop_loss": all_sl,
        "freq": freq_data,
    }
    out_file = OUT / "full_results_v3.json"
    with open(out_file, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 保存 {out_file} ({out_file.stat().st_size/1024:.0f}KB)")
    print(f"  主回测: {len(all_main)} 组")
    print(f"  参数网格: {len(all_param)} 标的 × 750种")
    print(f"  时间稳定性: {len(all_time)} 标的")
    print(f"  止损测试: {len(all_sl)} 标的 × 6档")
    print(f"  频率对比: {len(freq_data)} 标的")

if __name__ == "__main__":
    run()
