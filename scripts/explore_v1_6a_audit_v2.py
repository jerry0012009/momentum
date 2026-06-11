#!/usr/bin/env python3
"""
V1.6A Audit v2:
Q1: Verify event overlay matches full-universe event detection.
Q2: V4 signal alone + trailing stop on ALL 89K signals.
"""
import zipfile, glob, os, json, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
KLINES = ROOT / 'data' / 'binance_vision_1h_v1_6' / 'klines'
V4_TRADES = ROOT / 'reports' / 'artifacts' / 'binance_event_study_v1_6a_oos' / 'all_trades_full_universe.csv'
EVENT_FILE = ROOT / 'reports' / 'artifacts' / 'binance_event_study_v1_6a_realtime_event_overlay' / 'events_rank20_ret30_vol5m.csv'
OUTDIR = ROOT / 'reports' / 'artifacts' / 'binance_event_study_v1_6a_audit'
OUTDIR.mkdir(parents=True, exist_ok=True)

RANK_MAX = 20; RET24_MIN = 0.30; VOL24_MIN = 5_000_000; COOLDOWN_H = 24; MIN_XSEC = 100; MAX_HOLD = 48

def load_sym(sym):
    d = KLINES / sym
    fs = sorted(glob.glob(str(d / f'{sym}-1h-*.zip')))
    if not fs: return None
    fr = []
    for f in fs:
        try:
            with zipfile.ZipFile(f) as zf:
                ns = [n for n in zf.namelist() if n.endswith('.csv')]
                if not ns: continue
                raw = pd.read_csv(zf.open(ns[0]))
                o = pd.DataFrame({
                    'ts': pd.to_datetime(pd.to_numeric(raw['open_time'], errors='coerce'), unit='ms', utc=True),
                    'sym': sym,
                    'open': pd.to_numeric(raw.get('open', raw['close']), errors='coerce').astype(float),
                    'high': pd.to_numeric(raw.get('high', raw['close']), errors='coerce').astype(float),
                    'low': pd.to_numeric(raw.get('low', raw['close']), errors='coerce').astype(float),
                    'close': pd.to_numeric(raw['close'], errors='coerce').astype(float),
                    'qv': pd.to_numeric(raw.get('quote_volume', 0), errors='coerce').astype(float),
                }).dropna(subset=['ts','close'])
                fr.append(o)
        except: continue
    if not fr: return None
    df = pd.concat(fr, ignore_index=True).sort_values('ts').drop_duplicates('ts')
    if len(df) < 200: return None
    df['ret24'] = df['close'].pct_change(24)
    df['vol24'] = df['qv'].rolling(24, min_periods=12).sum()
    df = df.dropna(subset=['ret24'])
    df['ts_ns'] = df['ts'].dt.as_unit('ns').astype(np.int64)
    return df

def pf(r):
    g = r[r>0].sum(); l = abs(r[r<=0].sum())
    return g/max(l,1e-9)

# ═══ Q1 ═══════════════════════════════════════════════════
print("="*70); print("Q1: FULL-UNIVERSE EVENT DETECTION"); print("="*70)
ev = pd.read_csv(EVENT_FILE, parse_dates=['event_ts'])
ev['event_ts'] = pd.to_datetime(ev['event_ts'], utc=True)
print(f"\nExisting overlay: {len(ev)} events, {ev['symbol'].nunique()} symbols")

print("\nLoading all symbols...")
t0 = time.time()
sd = {}
for s in sorted(d.name for d in KLINES.iterdir() if d.is_dir()):
    df = load_sym(s)
    if df is not None: sd[s] = df
print(f"  {len(sd)} symbols in {time.time()-t0:.0f}s")

print("Building cross-sections...")
parts = []
for s, df in sd.items():
    parts.append(df[['ts','sym','ret24','vol24']].dropna().rename(columns={'sym':'symbol'}))
cs = pd.concat(parts, ignore_index=True).sort_values('ts')
print(f"  {len(cs):,} rows")

det = []; tg = 0
for tv, g in cs.groupby('ts'):
    if len(g) < MIN_XSEC: continue
    tg += 1
    g = g.copy()
    g['rank'] = g['ret24'].rank(ascending=False, method='first').astype(int)
    f = g[(g['rank']<=RANK_MAX)&(g['ret24']>=RET24_MIN)&(g['vol24']>=VOL24_MIN)]
    for _, r in f.iterrows():
        det.append({'symbol':r['symbol'],'event_ts':tv,'ret24':r['ret24'],'vol24':r['vol24'],'rank':int(r['rank'])})

dd = pd.DataFrame(det)
if len(dd) > 0:
    dd['event_ts'] = pd.to_datetime(dd['event_ts'], utc=True)
    ded = []
    for sym, g in dd.groupby('symbol'):
        g = g.sort_values('event_ts'); last = pd.Timestamp('1970-01-01',tz='UTC')
        for _, r in g.iterrows():
            if (r['event_ts']-last).total_seconds()/3600 >= COOLDOWN_H:
                ded.append(r); last = r['event_ts']
    dd = pd.DataFrame(ded)

print(f"\nFull-universe: {len(dd)} events, {dd['symbol'].nunique() if len(dd)>0 else 0} symbols")
print(f"  Scanned timestamps: {tg:,}")

if len(dd) > 0:
    ds = set(zip(dd['symbol'],dd['event_ts'])); es = set(zip(ev['symbol'],ev['event_ts']))
    ov = ds & es; od = ds - es; oe = es - ds
    print(f"\n  Overlap: {len(ov)} ({len(ov)/max(len(es),1)*100:.1f}%)")
    print(f"  Only in full scan: {len(od)}")
    print(f"  Only in overlay: {len(oe)}")
    if oe: print(f"    Overlay-only examples: {list(oe)[:5]}")
    if od: print(f"    Full-only examples: {list(od)[:5]}")

# ═══ Q2 ═══════════════════════════════════════════════════
print("\n"+"="*70); print("Q2: V4 FULL-UNIVERSE + TRAILING STOP"); print("="*70)

v4 = pd.read_csv(V4_TRADES, parse_dates=['ts'])
v4['signal_ts'] = pd.to_datetime(v4['ts'], utc=True)
v4 = v4[~v4['symbol'].isin(['BTCUSDT','ETHUSDT'])].copy()
v4['signal_ts_ns'] = v4['signal_ts'].dt.as_unit('ns').astype(np.int64)
print(f"\nV4 signals: {len(v4):,}")

r4 = v4['net_4h'].values
print(f"  4h fixed: mean={np.mean(r4)*100:.2f}%, med={np.median(r4)*100:.2f}%, "
      f"wr={np.sum(r4>0)/len(r4)*100:.1f}%, pf={pf(r4):.2f}")

v4s = set(v4['symbol'].unique())
print(f"\nLoading candles for {len(v4s)} symbols...")
t0 = time.time()
ca = {}
for s in v4s:
    df = load_sym(s)
    if df is not None:
        ca[s] = {'ts':df['ts_ns'].values,'o':df['open'].values,'h':df['high'].values,
                 'l':df['low'].values,'c':df['close'].values}
print(f"  {len(ca)} loaded in {time.time()-t0:.0f}s")

ss = v4['symbol'].values; sn = v4['signal_ts_ns'].values; sy = v4['signal_ts'].dt.year.values
tps = [0.005,0.01,0.015,0.02,0.025,0.03,0.04,0.05]

print(f"\n{'Trail':>8} {'N':>8} {'Mean%':>8} {'Med%':>8} {'WR%':>7} {'PF':>7}")
print("-"*50)

tr = {}
for tp in tps:
    rets = np.full(len(ss), np.nan)
    for i in range(len(ss)):
        a = ca.get(ss[i])
        if a is None: continue
        idx = np.searchsorted(a['ts'], sn[i], side='right') - 1
        if idx < 0 or idx >= len(a['c'])-1: continue
        ep = a['c'][idx]
        if ep <= 0: continue
        ts_ = ep*(1.0-tp); pk = ep; er = np.nan
        for j in range(idx+1, min(idx+1+MAX_HOLD, len(a['c']))):
            bh=a['h'][j]; bl=a['l'][j]; bo=a['o'][j]
            if bh>pk: pk=bh; ts_=pk*(1.0-tp)
            if bl<=ts_:
                xp=max(ts_,bo); xp=min(xp,bh); xp=max(xp,bl)
                er=(xp/ep)-1.0; break
        if np.isnan(er):
            li=min(idx+MAX_HOLD,len(a['c'])-1); er=(a['c'][li]/ep)-1.0
        rets[i] = er
    v = rets[~np.isnan(rets)]; tr[tp] = v
    w = np.sum(v>0)
    print(f"  {tp*100:5.1f}% {len(v):>8,} {np.mean(v)*100:>7.2f}% {np.median(v)*100:>7.2f}% "
          f"{w/len(v)*100:>6.1f}% {pf(v):>6.2f}")

# Trail 2% yearly
print(f"\nTrail 2% yearly:")
tp2 = tr.get(0.02, np.array([]))
yr = {}
for i in range(len(ss)):
    a = ca.get(ss[i])
    if a is None: continue
    idx = np.searchsorted(a['ts'], sn[i], side='right') - 1
    if idx < 0 or idx >= len(a['c'])-1: continue
    ep = a['c'][idx]
    if ep <= 0: continue
    ts_=ep*0.98; pk=ep; er=np.nan
    for j in range(idx+1,min(idx+1+MAX_HOLD,len(a['c']))):
        bh=a['h'][j]; bl=a['l'][j]; bo=a['o'][j]
        if bh>pk: pk=bh; ts_=pk*0.98
        if bl<=ts_:
            xp=max(ts_,bo); xp=min(xp,bh); xp=max(xp,bl); er=(xp/ep)-1.0; break
    if np.isnan(er):
        li=min(idx+MAX_HOLD,len(a['c'])-1); er=(a['c'][li]/ep)-1.0
    yr.setdefault(int(sy[i]),[]).append(er)

print(f"{'Year':>6} {'N':>8} {'Mean%':>8} {'Med%':>8} {'WR%':>7} {'PF':>7}")
print("-"*50)
for y in sorted(yr):
    r = np.array(yr[y]); w = np.sum(r>0)
    print(f"  {y:>4} {len(r):>8,} {np.mean(r)*100:>7.2f}% {np.median(r)*100:>7.2f}% "
          f"{w/len(r)*100:>6.1f}% {pf(r):>6.2f}")

# ═══ COMPARISON ═══════════════════════════════════════════
print("\n"+"="*70)
print("SIDE-BY-SIDE COMPARISON")
print("="*70)
r2 = tr.get(0.02, np.array([]))
if len(r2)>0:
    print(f"\n  V4-only trail 2%:  n={len(r2):,}, mean={np.mean(r2)*100:.2f}%, "
          f"med={np.median(r2)*100:.2f}%, wr={np.sum(r2>0)/len(r2)*100:.1f}%, pf={pf(r2):.2f}")
print(f"  V4-only 4h fixed:  n={len(r4):,}, mean={np.mean(r4)*100:.2f}%, "
      f"med={np.median(r4)*100:.2f}%, wr={np.sum(r4>0)/len(r4)*100:.1f}%, pf={pf(r4):.2f}")

# ═══ SAVE ═════════════════════════════════════════════════
print("\nSaving...")
q1 = {'existing':{'events':len(ev),'symbols':int(ev['symbol'].nunique())},
      'full_scan':{'events':int(len(dd)),'symbols':int(dd['symbol'].nunique()) if len(dd)>0 else 0,'timestamps':tg}}
if len(dd)>0:
    q1['overlap']={'n':len(ov),'pct':f"{len(ov)/max(len(es),1)*100:.1f}%",
                   'only_overlay':len(oe),'only_full':len(od)}
json.dump(q1, open(OUTDIR/'q1_universe_audit.json','w'), indent=2, default=str)

q2 = {'v4_4h_fixed':{'n':int(len(r4)),'mean':float(np.mean(r4)),'med':float(np.median(r4)),
                      'wr':float(np.sum(r4>0)/len(r4)),'pf':float(pf(r4))}}
for tp,v in tr.items():
    q2[f'trail_{tp*100:.1f}pct']={'n':int(len(v)),'mean':float(np.mean(v)),'med':float(np.median(v)),
                                    'wr':float(np.sum(v>0)/len(v)),'pf':float(pf(v))}
q2['trail_2pct_yearly']={}
for y in sorted(yr):
    r=np.array(yr[y]); q2['trail_2pct_yearly'][str(y)]={'n':int(len(r)),'mean':float(np.mean(r)),
        'med':float(np.median(r)),'wr':float(np.sum(r>0)/len(r)),'pf':float(pf(r))}
json.dump(q2, open(OUTDIR/'q2_v4_trailing_stop.json','w'), indent=2, default=str)

if len(dd)>0: dd.to_csv(OUTDIR/'full_universe_events_detected.csv', index=False)

print(f"\n{'='*70}"); print("DONE"); print(f"{'='*70}")
