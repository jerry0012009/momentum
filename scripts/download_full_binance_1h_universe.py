#!/usr/bin/env python3
"""
Download missing 1h kline monthly files for a broad Binance USDT perpetual universe.
Universe = union(current exchangeInfo USDT perps, funding archive symbols, existing kline cache symbols).
Period = 2022-01 .. 2026-05.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CACHE_DIR = Path('/root/clawd/jerry/momentum/data/binance_vision_1h_v1_6/klines')
FUNDING_DIR = Path('/root/clawd/jerry/momentum/data/binance_vision_rank154/data/futures/um/monthly/fundingRate')
OUT_DIR = Path('/root/clawd/jerry/momentum/reports/artifacts/binance_event_study_v1_6a_oos')
OUT_DIR.mkdir(parents=True, exist_ok=True)
S3_BASE = 'https://data.binance.vision'
MAX_WORKERS = 32


def current_exchange_symbols() -> set[str]:
    url = 'https://fapi.binance.com/fapi/v1/exchangeInfo'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'v1.6a-full-universe/1.0'})
        data = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return {
            s['symbol'] for s in data['symbols']
            if s.get('quoteAsset') == 'USDT' and s.get('contractType') == 'PERPETUAL'
        }
    except Exception as e:
        print(f'WARN: exchangeInfo failed: {e}')
        return set()


def months() -> list[str]:
    out = []
    for y in range(2022, 2027):
        for m in range(1, 13):
            if y == 2026 and m > 5:
                break
            out.append(f'{y}-{m:02d}')
    return out


def download_one(task):
    sym, month = task
    path = CACHE_DIR / sym / f'{sym}-1h-{month}.zip'
    if path.exists() and path.stat().st_size > 0:
        return {'symbol': sym, 'month': month, 'status': 'cached', 'bytes': path.stat().st_size}
    path.parent.mkdir(parents=True, exist_ok=True)
    url = f'{S3_BASE}/data/futures/um/monthly/klines/{sym}/1h/{sym}-1h-{month}.zip'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'v1.6a-full-universe/1.0'})
        data = urllib.request.urlopen(req, timeout=35).read()
        if not data or data.startswith(b'<Error>'):
            return {'symbol': sym, 'month': month, 'status': 'missing', 'bytes': 0}
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_bytes(data)
        tmp.replace(path)
        return {'symbol': sym, 'month': month, 'status': 'ok', 'bytes': len(data)}
    except Exception as e:
        return {'symbol': sym, 'month': month, 'status': 'fail', 'bytes': 0, 'error': str(e)[:120]}


def main():
    existing = set(p.name for p in CACHE_DIR.iterdir() if p.is_dir()) if CACHE_DIR.exists() else set()
    funding = set(p.name for p in FUNDING_DIR.iterdir() if p.is_dir()) if FUNDING_DIR.exists() else set()
    current = current_exchange_symbols()
    symbols = sorted(s for s in (existing | funding | current) if s.endswith('USDT'))
    ms = months()

    tasks = []
    for sym in symbols:
        for m in ms:
            path = CACHE_DIR / sym / f'{sym}-1h-{m}.zip'
            if not (path.exists() and path.stat().st_size > 0):
                tasks.append((sym, m))

    manifest = {
        'n_existing_cache_symbols': len(existing),
        'n_funding_symbols': len(funding),
        'n_current_exchange_symbols': len(current),
        'n_union_symbols': len(symbols),
        'months': ms,
        'n_missing_files_to_try': len(tasks),
        'max_workers': MAX_WORKERS,
    }
    (OUT_DIR / 'download_full_universe_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print('Universe:')
    for k, v in manifest.items():
        if k != 'months':
            print(f'  {k}: {v}')
    print(f'  period: {ms[0]}..{ms[-1]}')

    counts = {'ok': 0, 'cached': 0, 'missing': 0, 'fail': 0}
    rows = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = [ex.submit(download_one, t) for t in tasks]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            rows.append(r)
            counts[r['status']] = counts.get(r['status'], 0) + 1
            if i % 500 == 0 or i == len(futs):
                elapsed = time.time() - t0
                rate = i / elapsed if elapsed > 0 else 0
                eta = (len(futs) - i) / rate if rate > 0 else 0
                print(f'  {i}/{len(futs)} tried | ok={counts["ok"]} missing={counts["missing"]} fail={counts["fail"]} | ETA {eta:.0f}s')

    # Save log via pandas if available, otherwise JSONL
    try:
        import pandas as pd
        pd.DataFrame(rows).to_csv(OUT_DIR / 'download_full_universe_log.csv', index=False)
    except Exception:
        with open(OUT_DIR / 'download_full_universe_log.jsonl', 'w', encoding='utf-8') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')

    print('Download complete:', counts)
    print(f'Elapsed: {time.time() - t0:.1f}s')


if __name__ == '__main__':
    main()
