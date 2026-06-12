#!/usr/bin/env python3
"""
Rank 444 — v6: 多空双向策略 + 与单多头对比
==========================================
核心对比：
  A) 单做多 (RSI<超卖 + 价格<BB下轨 → 买涨, 中轨平)
  B) 单做空 (RSI>超买 + 价格>BB上轨 → 卖空, 中轨平)
  C) 多空双向 (A+B同时运行)
"""
import json, time, warnings
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

OUT = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb")

# ═══ 指标 ═══
def calc_rsi(s, p=7):
    d = s.diff()
    g, l = d.clip(lower=0), -d.clip(upper=0)
    ag = g.ewm(com=p-1, min_periods=p).mean()
    al = l.ewm(com=p-1, min_periods=p).mean()
    return 100 - 100/(1 + ag/al)

def calc_bb(s, p=20, m=2.0):
    b = s.rolling(p).mean()
    d = m * s.rolling(p).std()
    return b, b+d, b-d  # mid, upper, lower


def backtest_long_short(df, rp=7, rl=30, rh=70, bp=20, bm=2.0, stop_pct=None, mode="both"):
    """
    mode: "long" / "short" / "both"
    long:  RSI<rl & close<bb_lower → buy, close>bb_mid → exit
    short: RSI>rh & close>bb_upper → short, close<bb_mid → exit
    """
    close = df["close"].values
    rsi = calc_rsi(df["close"], rp).values
    bb_mid, bb_up, bb_low = calc_bb(df["close"], bp, bm)
    bb_mid = bb_mid.values; bb_up = bb_up.values; bb_low = bb_low.values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values

    mask = ~(np.isnan(rsi) | np.isnan(bb_mid) | np.isnan(bb_up) | np.isnan(bb_low))
    close = close[mask]; rsi = rsi[mask]
    bb_mid = bb_mid[mask]; bb_up = bb_up[mask]; bb_low = bb_low[mask]
    ma200 = ma200[mask]
    dates = df["date"].values[mask]

    n = len(close)
    if n < 10: return None

    trades = []
    pos = None  # {"side":"long"/"short", "ep":..., "ei":..., "regime":...}

    for i in range(1, n):
        if pos is None:
            # 入场
            if mode in ("long","both") and rsi[i] < rl and close[i] < bb_low[i]:
                regime = "bull" if close[i] > ma200[i] else "bear"
                pos = {"side":"long","ep":close[i],"ei":i,"ed":str(dates[i])[:10],"regime":regime}
            elif mode in ("short","both") and rsi[i] > rh and close[i] > bb_up[i]:
                regime = "bull" if close[i] > ma200[i] else "bear"
                pos = {"side":"short","ep":close[i],"ei":i,"ed":str(dates[i])[:10],"regime":regime}
        else:
            # 出场
            if pos["side"] == "long":
                pnl = (close[i]/pos["ep"]-1)*100
                exit_sl = stop_pct is not None and pnl <= -stop_pct
                exit_mid = close[i] > bb_mid[i]
            else:  # short
                pnl = (pos["ep"]/close[i]-1)*100  # 做空：价格跌=赚钱
                exit_sl = stop_pct is not None and pnl <= -stop_pct
                exit_mid = close[i] < bb_mid[i]

            if exit_sl or exit_mid:
                net = pnl - 0.2  # 单边手续费
                trades.append({
                    "side":pos["side"],"ed":pos["ed"],
                    "xd":str(dates[i])[:10],
                    "ep":round(pos["ep"],4),"xp":round(close[i],4),
                    "pnl":round(pnl,4),"net":round(net,4),
                    "bars":i-pos["ei"],"regime":pos["regime"],
                    "exit":"止损" if exit_sl else "中轨"
                })
                pos = None

    if not trades:
        return {"n":0,"wr":0,"ret":0,"ann":0,"mdd":0,"sh":0,"pf":0,"ap":0,"ab":0,
                "long_n":0,"short_n":0,"long_ret":0,"short_ret":0,
                "by_regime":{},"trades":[],
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

    # 多/空拆分
    long_t = t[t["side"]=="long"]; short_t = t[t["side"]=="short"]
    long_ret = ((1+long_t["net"]/100).cumprod().iloc[-1]-1)*100 if len(long_t)>0 else 0
    short_ret = ((1+short_t["net"]/100).cumprod().iloc[-1]-1)*100 if len(short_t)>0 else 0

    # Regime拆分
    by_regime = {}
    for rg in ["bull","bear"]:
        sub = t[t["regime"]==rg]
        if len(sub)==0: continue
        sw = sub[sub["net"]>0]; sl = sub[sub["net"]<=0]
        rg_cum = (1+sub["net"]/100).cumprod()
        # 多空子拆分
        for side in ["long","short"]:
            ss = sub[sub["side"]==side]
            if len(ss)==0: continue
            s_cum = (1+ss["net"]/100).cumprod()
            by_regime[f"{rg}_{side}"] = {
                "n":len(ss),"wr":round(len(ss[ss["net"]>0])/len(ss)*100,1),
                "ret":round((s_cum.iloc[-1]-1)*100,2),
                "ap":round(ss["net"].mean(),4)
            }
        by_regime[rg] = {
            "n":len(sub),"wr":round(len(sw)/len(sub)*100,1),
            "ret":round((rg_cum.iloc[-1]-1)*100,2),
            "ap":round(sub["net"].mean(),4)
        }

    return {
        "n":nt,"wr":round(wr,2),"ret":round(ret,2),"ann":round(ann,2),
        "mdd":round(mdd,2),"sh":round(sh,3),"pf":round(gp/gl,3),
        "ap":round(t["net"].mean(),4),"ab":round(ab,1),
        "long_n":len(long_t),"short_n":len(short_t),
        "long_ret":round(long_ret,2),"short_ret":round(short_ret,2),
        "long_wr":round(len(long_t[long_t["net"]>0])/max(len(long_t),1)*100,1),
        "short_wr":round(len(short_t[short_t["net"]>0])/max(len(short_t),1)*100,1),
        "by_regime":by_regime,"trades":trades,
        "ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)
    }


def param_grid_long_short(df, mode="both"):
    """750参数网格对比"""
    rsi_ps = [5,7,10,14]; rsi_ls = [25,30,35]; bb_ps = [15,20,25]; bb_ms = [1.5,2.0,2.5]
    close = df["close"].values
    rsi_c = {rp: calc_rsi(df["close"],rp).values for rp in rsi_ps}
    bb_c = {}
    for bp in bb_ps:
        for bm in bb_ms:
            mid,up,low = calc_bb(df["close"],bp,bm)
            bb_c[(bp,bm)] = (mid.values, up.values, low.values)

    base_mask = np.ones(len(close),dtype=bool)
    for rp in rsi_ps: base_mask &= ~np.isnan(rsi_c[rp])
    for key in bb_c: base_mask &= ~np.isnan(bb_c[key][0])
    c = close[base_mask]

    results = []
    for rp,rl,bp,bm in product(rsi_ps, rsi_ls, bb_ps, bb_ms):
        r = rsi_c[rp][base_mask]
        mid, up, low = bb_c[(bp,bm)]; mid=mid[base_mask]; up=up[base_mask]; low=low[base_mask]

        trades_net = []
        pos = None
        for i in range(1, len(c)):
            if pos is None:
                if mode in ("long","both") and r[i] < rl and c[i] < low[i]:
                    pos = ("L", c[i])
                elif mode in ("short","both") and r[i] > (100-rl) and c[i] > up[i]:
                    pos = ("S", c[i])
            else:
                if pos[0] == "L":
                    pnl = (c[i]/pos[1]-1)*100
                    exit_cond = c[i] > mid[i]
                else:
                    pnl = (pos[1]/c[i]-1)*100
                    exit_cond = c[i] < mid[i]
                if exit_cond:
                    trades_net.append(pnl - 0.2)
                    pos = None

        if not trades_net: continue
        arr = np.array(trades_net)
        cum = np.cumprod(1+arr/100)
        ret = (cum[-1]-1)*100
        wins = arr[arr>0]
        gp = wins.sum() if len(wins)>0 else 0
        gl = abs(arr[arr<=0].sum()) if len(arr[arr<=0])>0 else 0.001
        pk = np.maximum.accumulate(cum)
        mdd = ((cum-pk)/pk*100).min()
        sh = arr.mean()/arr.std()*np.sqrt(min(252/8,len(arr))) if arr.std()>0 else 0
        results.append({"n":len(arr),"ret":round(ret,2),"sh":round(sh,3),
                        "pf":round(gp/gl,2),"mdd":round(mdd,2),"wr":round(len(wins)/len(arr)*100,1)})

    if not results: return None
    rdf = pd.DataFrame(results)
    return {
        "total":len(rdf),"pct_profitable":round((rdf["ret"]>0).mean()*100,1),
        "ret_mean":round(rdf["ret"].mean(),2),"ret_median":round(rdf["ret"].median(),2),
        "ret_std":round(rdf["ret"].std(),2),
        "ret_q25":round(rdf["ret"].quantile(0.25),2),"ret_q75":round(rdf["ret"].quantile(0.75),2),
        "sharpe_mean":round(rdf["sh"].mean(),3),
        "best":rdf.nlargest(3,"ret").to_dict(orient="records"),
        "worst":rdf.nsmallest(3,"ret").to_dict(orient="records"),
    }


def regime_time_pct(df):
    close = df["close"].values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values
    valid = ~np.isnan(ma200)
    c = close[valid]; m = ma200[valid]
    bull = (c > m).sum()
    return {"bull_pct": round(bull/len(c)*100,1) if len(c)>0 else 0,
            "bear_pct": round((1-bull/len(c))*100,1) if len(c)>0 else 0}


# ═══ 数据获取 ═══
def fetch_us(sym, start, end, iv="1d"):
    import yfinance as yf
    try:
        df = yf.Ticker(sym).history(start=start, end=end, interval=iv, auto_adjust=True)
        if df.empty: return None
        df = df.reset_index().rename(columns={"Date":"date","Datetime":"date","Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"})
        if "date" not in df.columns: df["date"] = df.index
        df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
        return df[["date","open","high","low","close","volume"]].dropna().sort_values("date").reset_index(drop=True)
    except: return None

def fetch_cn(sym):
    import akshare as ak
    try:
        df = ak.futures_zh_daily_sina(symbol=sym)
        if df is None or df.empty: return None
        df["date"] = pd.to_datetime(df["date"])
        return df[["date","open","high","low","close","volume"]].dropna().sort_values("date").reset_index(drop=True)
    except: return None


# ═══ MAIN ═══
def run():
    now = datetime.now()
    long_start = now - timedelta(days=365*15+60)

    # 美股标的
    us_assets = [
        ("SPY","标普500"),("QQQ","纳斯达克100"),("AAPL","苹果"),("MSFT","微软"),
        ("GLD","黄金ETF"),("GC=F","COMEX黄金"),("CL=F","WTI原油"),("SI=F","COMEX白银"),("HG=F","COMEX铜"),
    ]
    # 中国期货标的（选代表性的）
    cn_assets = [
        ("M0","豆粕"),("AU0","黄金"),("SC0","原油"),
        ("I0","铁矿石"),("RB0","螺纹钢"),("CU0","铜"),
        ("AL0","铝"),("JM0","焦煤"),("P0","棕榈油"),("SR0","白糖"),
    ]

    all_results = {}

    print("="*70)
    print("Rank 444 — v6: 多空双向策略对比")
    print("="*70)

    # ── 美股 ──
    for sym, name in us_assets:
        print(f"\n  ▸ {name} ({sym})...")
        df = fetch_us(sym, long_start, now)
        if df is None or len(df)<100:
            print("    ⚠ 无数据"); continue
        print(f"    {len(df)} bars, {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")

        long_r = backtest_long_short(df, mode="long")
        short_r = backtest_long_short(df, mode="short")
        both_r = backtest_long_short(df, mode="both")

        rt = regime_time_pct(df)
        pg_long = param_grid_long_short(df, mode="long")
        pg_short = param_grid_long_short(df, mode="short")
        pg_both = param_grid_long_short(df, mode="both")

        print(f"    纯多: n={long_r['n']}, ret={long_r['ret']}%, sh={long_r['sh']}")
        print(f"    纯空: n={short_r['n']}, ret={short_r['ret']}%, sh={short_r['sh']}")
        print(f"    多空: n={both_r['n']}, ret={both_r['ret']}%, sh={both_r['sh']}")
        if pg_long: print(f"    网格 多:{pg_long['pct_profitable']}%盈 均{pg_long['ret_mean']}%")
        if pg_short: print(f"    网格 空:{pg_short['pct_profitable']}%盈 均{pg_short['ret_mean']}%")
        if pg_both: print(f"    网格 双:{pg_both['pct_profitable']}%盈 均{pg_both['ret_mean']}%")

        all_results[sym] = {"name":name,"type":"us","rt":rt,
            "long":long_r,"short":short_r,"both":both_r,
            "pg_long":pg_long,"pg_short":pg_short,"pg_both":pg_both}
        time.sleep(0.3)

    # ── 中国期货 ──
    for sym, name in cn_assets:
        print(f"\n  ▸ {name} ({sym}) [CN]...")
        df = fetch_cn(sym)
        if df is None or len(df)<100:
            print("    ⚠ 无数据"); continue
        print(f"    {len(df)} bars, {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")

        long_r = backtest_long_short(df, mode="long")
        short_r = backtest_long_short(df, mode="short")
        both_r = backtest_long_short(df, mode="both")

        rt = regime_time_pct(df)
        pg_long = param_grid_long_short(df, mode="long")
        pg_short = param_grid_long_short(df, mode="short")
        pg_both = param_grid_long_short(df, mode="both")

        print(f"    纯多: n={long_r['n']}, ret={long_r['ret']}%, sh={long_r['sh']}")
        print(f"    纯空: n={short_r['n']}, ret={short_r['ret']}%, sh={short_r['sh']}")
        print(f"    多空: n={both_r['n']}, ret={both_r['ret']}%, sh={both_r['sh']}")
        if pg_long: print(f"    网格 多:{pg_long['pct_profitable']}%盈 均{pg_long['ret_mean']}%")
        if pg_short: print(f"    网格 空:{pg_short['pct_profitable']}%盈 均{pg_short['ret_mean']}%")
        if pg_both: print(f"    网格 双:{pg_both['pct_profitable']}%盈 均{pg_both['ret_mean']}%")

        all_results[sym] = {"name":name,"type":"cn","rt":rt,
            "long":long_r,"short":short_r,"both":both_r,
            "pg_long":pg_long,"pg_short":pg_short,"pg_both":pg_both}
        time.sleep(0.3)

    out_file = OUT / "full_results_v6.json"
    with open(out_file, "w") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 保存 {out_file} ({out_file.stat().st_size/1024:.0f}KB)")

    # 汇总
    print(f"\n{'='*70}")
    print("汇总对比：纯多 vs 纯空 vs 多空双向")
    print(f"{'='*70}")
    for sym, fd in all_results.items():
        l,r,b = fd["long"],fd["short"],fd["both"]
        tag = "US" if fd["type"]=="us" else "CN"
        print(f"  [{tag}] {fd['name']:12s}  "
              f"多={l['ret']:+7.2f}%(sh={l['sh']:.2f})  "
              f"空={r['ret']:+7.2f}%(sh={r['sh']:.2f})  "
              f"双={b['ret']:+7.2f}%(sh={b['sh']:.2f})  "
              f"网格: 多{l['n']}笔/空{r['n']}笔")


if __name__ == "__main__":
    run()
