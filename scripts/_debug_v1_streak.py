#!/usr/bin/env python3
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('v1', '/root/clawd/jerry/momentum/scripts/build_binance_daily_event_study_v1.py')
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
panel=mod.DEFAULT_PANEL
print('panel exists', panel.exists())
import pandas as pd
p=mod.compute_derived(pd.read_pickle(panel))
count=0
state={}
prev=set()
for date,g in p[(p['is_eligible'].fillna(False)) & (p['listing_days']>=30) & p['quote_volume'].notna() & p['close'].notna()].groupby('date', sort=True, observed=True):
    u=g.sort_values('quote_volume', ascending=False).head(150)
    if len(u)<40: continue
    tagmap=mod.tag_events_for_day(u,15)
    tagmap_syms={'top_gainer_1d': set(), 'top_loser_1d': set()}
    for idx,meta in tagmap.items(): tagmap_syms[meta['event_type']].add(u.loc[idx,'symbol'])
    local=set(u['symbol'])
    update=prev | local
    new_state={}
    for sym in update:
        for ev in ['top_gainer_1d','top_loser_1d']:
            key=(sym,ev)
            if sym in local and key in tagmap_syms.get(ev,set()):
                new_state[key]=state.get(key,0)+1
            else:
                new_state[key]=0
    state=new_state
    prev=local
    counts=[]
    for idx,meta in tagmap.items():
        key=(u.loc[idx,'symbol'], meta['event_type'])
        counts.append((key,state[key]))
    print(date, 'tagmap', len(tagmap), 'sample_keys', counts[:5])
