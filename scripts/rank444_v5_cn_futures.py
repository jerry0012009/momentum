#!/usr/bin/env python3
"""
Rank 444 — v5: 补充中国期货标的回测
====================================
在v4基础上加入12个中国期货主力合约
"""

import json, time, warnings
from datetime import datetime, timedelta
from pathlib import Path
from itertools import product

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

OUT = Path("/root/clawd/jerry/momentum/reports/artifacts/rank444_rsi_bb")


# ═══════════════════════════════════════════════════════════════
# 指标 & 回测 (同v4)
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


def backtest_with_regime(df, rp=7, rl=30, bp=20, bm=2.0, stop_pct=None):
    close = df["close"].values
    rsi = calc_rsi(df["close"], rp).values
    bb_mid, _, bb_low = calc_bb(df["close"], bp, bm)
    bb_mid = bb_mid.values; bb_low = bb_low.values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values

    mask = ~(np.isnan(rsi) | np.isnan(bb_mid) | np.isnan(bb_low))
    close = close[mask]; rsi = rsi[mask]; bb_mid = bb_mid[mask]; bb_low = bb_low[mask]
    ma200 = ma200[mask]
    dates = df["date"].values[mask]

    n = len(close)
    if n < 10: return None

    trades = []
    pos = None
    for i in range(1, n):
        if pos is None:
            if rsi[i] < rl and close[i] < bb_low[i]:
                regime = "bull" if close[i] > ma200[i] else "bear"
                pos = {"ep":close[i],"ei":i,"ed":str(dates[i])[:10],"regime":regime}
        else:
            pnl = (close[i]/pos["ep"]-1)*100
            exit_sl = stop_pct is not None and pnl <= -stop_pct
            exit_mid = close[i] > bb_mid[i]
            if exit_sl or exit_mid:
                net = pnl - 0.2
                trades.append({"ed":pos["ed"],"xd":str(dates[i])[:10],
                               "ep":round(pos["ep"],4),"xp":round(close[i],4),
                               "pnl":round(pnl,4),"net":round(net,4),
                               "bars":i-pos["ei"],"regime":pos["regime"]})
                pos = None

    if not trades:
        return {"n":0,"wr":0,"ret":0,"ann":0,"mdd":0,"sh":0,"pf":0,"ab":0,"ap":0,
                "by_regime":{},"ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}

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

    by_regime = {}
    for rg in ["bull","bear"]:
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
        }

    return {"n":nt,"wr":round(wr,2),"ret":round(ret,2),"ann":round(ann,2),
            "mdd":round(mdd,2),"sh":round(sh,3),"pf":round(gp/gl,3),
            "ab":round(ab,1),"ap":round(t["net"].mean(),4),"by_regime":by_regime,
            "ds":str(df["date"].iloc[0].date()),"de":str(df["date"].iloc[-1].date()),"nb":len(df)}


def param_grid_with_regime(df):
    rsi_ps = [5, 7, 10, 14]
    rsi_ls = [25, 30, 35]
    bb_ps  = [15, 20, 25]
    bb_ms  = [1.5, 2.0, 2.5]

    close = df["close"].values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values
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
        }
    }


def regime_time_pct(df):
    close = df["close"].values
    ma200 = df["close"].rolling(200, min_periods=50).mean().values
    valid = ~np.isnan(ma200)
    c = close[valid]; m = ma200[valid]
    bull = (c > m).sum()
    return {"bull_pct": round(bull/len(c)*100,1) if len(c)>0 else 0,
            "bear_pct": round((1-bull/len(c))*100,1) if len(c)>0 else 0}


# ═══════════════════════════════════════════════════════════════
# 数据获取: 中国期货 (akshare)
# ═══════════════════════════════════════════════════════════════

def fetch_cn_futures(sym):
    """从akshare获取中国期货主力合约日线"""
    import akshare as ak
    try:
        df = ak.futures_zh_daily_sina(symbol=sym)
        if df is None or df.empty: return None
        df = df.rename(columns={"date":"date","open":"open","high":"high",
                                "low":"low","close":"close","volume":"volume"})
        df["date"] = pd.to_datetime(df["date"])
        df = df[["date","open","high","low","close","volume"]].dropna().sort_values("date").reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  ✗ {sym}: {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def run():
    now = datetime.now()

    cn_assets = [
        ("I0","铁矿石","黑色系"),("RB0","螺纹钢","黑色系"),
        ("J0","焦炭","黑色系"),("JM0","焦煤","黑色系"),
        ("CU0","铜","有色金属"),("AL0","铝","有色金属"),("ZN0","锌","有色金属"),
        ("AU0","黄金","贵金属"),("AG0","白银","贵金属"),
        ("SC0","原油","能源化工"),
        ("P0","棕榈油","农产品"),("M0","豆粕","农产品"),
        ("SR0","白糖","农产品"),("LC0","碳酸锂","新能源"),
    ]

    print("="*70)
    print("Rank 444 — v5: 中国期货标的补充回测")
    print("="*70)

    all_cn = {}

    for sym, name, cat in cn_assets:
        print(f"\n  ▸ {name} ({sym}) [{cat}]...")
        df = fetch_cn_futures(sym)
        if df is None or len(df)<100:
            print(f"    ⚠ 数据不足")
            continue
        print(f"    {len(df)} bars, {df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}")

        # 主回测
        r = backtest_with_regime(df)
        if r is None:
            print("    ⚠ 无交易")
            continue
        rg = r.get("by_regime",{})
        rt = regime_time_pct(df)
        print(f"    n={r['n']}, ret={r['ret']}%, sh={r['sh']}, mdd={r['mdd']}%")
        print(f"    bull={rg.get('bull',{}).get('ret','?')}%({rg.get('bull',{}).get('n','?')}笔), "
              f"bear={rg.get('bear',{}).get('ret','?')}%({rg.get('bear',{}).get('n','?')}笔)")
        print(f"    time: bull{rt['bull_pct']}%, bear{rt['bear_pct']}%")

        # 参数网格
        pg = param_grid_with_regime(df)
        if pg:
            rs = pg.get("regime_summary",{})
            print(f"    参数网格: {pg['total']}种, {pg['pct_profitable']}%盈利, "
                  f"bull均={rs.get('bull_ret_mean','?')}%, bear均={rs.get('bear_ret_mean','?')}%")

        # 止损测试
        sl_results = []
        for stop in [None, 3, 5, 8, 10]:
            sr = backtest_with_regime(df, stop_pct=stop)
            if sr:
                sl_results.append({"stop":stop if stop else "无","n":sr["n"],"ret":sr["ret"],"mdd":sr["mdd"]})

        all_cn[sym] = {
            "name":name,"cat":cat,
            "data_range":f"{df['date'].iloc[0].date()}~{df['date'].iloc[-1].date()}",
            "bars":len(df),"years":round((df['date'].iloc[-1]-df['date'].iloc[0]).days/365.25,1),
            "main":r,"param_grid":pg,"regime_time":rt,"stop_loss":sl_results,
        }
        time.sleep(0.3)

    # ── 保存 ──
    out_file = OUT / "cn_futures_v5.json"
    with open(out_file, "w") as f:
        json.dump(all_cn, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 保存 {out_file} ({out_file.stat().st_size/1024:.0f}KB)")

    # 汇总
    print(f"\n{'='*70}")
    print("汇总")
    print(f"{'='*70}")
    for sym, fd in all_cn.items():
        m = fd["main"]
        rg = m.get("by_regime",{})
        print(f"  {fd['name']:6s} ({fd['years']:4.1f}年): ret={m['ret']:+7.2f}%, "
              f"sh={m['sh']:.3f}, bull={rg.get('bull',{}).get('ret','?'):>7}%, "
              f"bear={rg.get('bear',{}).get('ret','?'):>7}%, "
              f"网格盈利{fd['param_grid']['pct_profitable'] if fd['param_grid'] else '?'}%")

if __name__ == "__main__":
    run()
