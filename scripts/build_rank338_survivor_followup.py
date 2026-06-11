#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'rank338_survivor_followup'
ART_DIR.mkdir(parents=True, exist_ok=True)

SYMBOLS = ['BTCUSDT', 'ETHUSDT']
LOOKBACK_DAYS = 730
CAPITAL = 10_000.0
NOTIONAL_WEIGHT = 0.20
ENTRY_FEE_PCT = 0.0014
EXIT_FEE_PCT = 0.0014
WINDOW_NOTIONAL = CAPITAL * NOTIONAL_WEIGHT
INTERVAL = '5m'
PRE_BARS = 12
POST_BARS = 96
FUNDING_EVENT_HOURS = 8
EXTREME_APR = 15.0
BASELINE_ENTRY_APR = 5.0
BASELINE_EXIT_APR = 3.0
BOUNDARY_MINUTES = 30
REQUEST_PAUSE = 0.15

SPOT_BASE = 'https://api.binance.com'
PERP_BASE = 'https://fapi.binance.com'


def get_json(base: str, path: str, params: dict) -> list | dict:
    qs = urlencode(params)
    url = f'{base}{path}?{qs}'
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=30) as resp:
        raw = resp.read().decode('utf-8')
    time.sleep(REQUEST_PAUSE)
    return json.loads(raw)


def fetch_funding(symbol: str, start_ms: int, end_ms: int) -> list[dict]:
    out = []
    cur = start_ms
    while True:
        batch = get_json(PERP_BASE, '/fapi/v1/fundingRate', {
            'symbol': symbol,
            'startTime': cur,
            'endTime': end_ms,
            'limit': 1000,
        })
        if not batch:
            break
        out.extend(batch)
        last = int(batch[-1]['fundingTime'])
        if last >= end_ms or len(batch) < 1000:
            break
        cur = last + 1
    return out


def fetch_klines(base: str, path: str, symbol: str, start_ms: int, end_ms: int, interval: str = '5m') -> list[list]:
    out = []
    cur = start_ms
    while True:
        batch = get_json(base, path, {
            'symbol': symbol,
            'interval': interval,
            'startTime': cur,
            'endTime': end_ms,
            'limit': 1000,
        })
        if not batch:
            break
        out.extend(batch)
        last = int(batch[-1][0])
        if last >= end_ms or len(batch) < 1000:
            break
        cur = last + 1
    return out


def annualized_apr(funding_rate: float) -> float:
    return funding_rate * 3.0 * 365.0 * 100.0


def kline_map(rows: Iterable[list]) -> dict[int, float]:
    return {int(r[0]): float(r[4]) for r in rows}


def bar_ms(interval: str = '5m') -> int:
    unit = interval[-1]
    n = int(interval[:-1])
    if unit == 'm':
        return n * 60 * 1000
    raise ValueError(interval)


@dataclass
class EventRow:
    symbol: str
    funding_time: int
    funding_iso: str
    funding_rate: float
    apr: float
    entry_spot: float
    entry_perp: float
    exit_spot: float
    exit_perp: float
    basis_now_bps: float
    basis_15m_bps: float
    basis_30m_bps: float
    basis_60m_bps: float
    basis_slope_15m_bps: float
    basis_slope_30m_bps: float
    basis_slope_60m_bps: float
    net_event_return: float
    funding_component: float
    basis_component: float
    fees_component: float
    veto_pass: int


def build_events(symbol: str) -> list[EventRow]:
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=LOOKBACK_DAYS)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    funding = fetch_funding(symbol, start_ms, end_ms)
    extreme = [r for r in funding if annualized_apr(float(r['fundingRate'])) >= EXTREME_APR]
    if not extreme:
        return []
    bar = bar_ms(INTERVAL)
    first = int(extreme[0]['fundingTime']) - PRE_BARS * bar
    last = int(extreme[-1]['fundingTime']) + POST_BARS * bar
    spot = kline_map(fetch_klines(SPOT_BASE, '/api/v3/klines', symbol, first, last, INTERVAL))
    perp = kline_map(fetch_klines(PERP_BASE, '/fapi/v1/klines', symbol, first, last, INTERVAL))
    out = []
    for r in extreme:
        t = int(r['fundingTime'])
        entry_t = t - (BOUNDARY_MINUTES * 60 * 1000)
        exit_t = t + (FUNDING_EVENT_HOURS * 60 * 60 * 1000)
        need = [entry_t, exit_t, t, t - 3 * bar, t - 6 * bar, t - 12 * bar]
        if any(ts not in spot or ts not in perp for ts in need):
            continue
        entry_spot = spot[entry_t]
        entry_perp = perp[entry_t]
        exit_spot = spot[exit_t]
        exit_perp = perp[exit_t]
        basis_now = perp[t] / spot[t] - 1.0
        basis_15 = perp[t - 3 * bar] / spot[t - 3 * bar] - 1.0
        basis_30 = perp[t - 6 * bar] / spot[t - 6 * bar] - 1.0
        basis_60 = perp[t - 12 * bar] / spot[t - 12 * bar] - 1.0
        basis_slope_15 = basis_now - basis_15
        basis_slope_30 = basis_now - basis_30
        basis_slope_60 = basis_now - basis_60
        basis_component = (exit_spot / entry_spot - 1.0) - (exit_perp / entry_perp - 1.0)
        fr = float(r['fundingRate'])
        funding_component = fr
        fees_component = ENTRY_FEE_PCT + EXIT_FEE_PCT
        net = funding_component + basis_component - fees_component
        veto_pass = int(basis_slope_15 <= 0.0)
        out.append(EventRow(
            symbol=symbol,
            funding_time=t,
            funding_iso=datetime.fromtimestamp(t / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            funding_rate=fr,
            apr=annualized_apr(fr),
            entry_spot=entry_spot,
            entry_perp=entry_perp,
            exit_spot=exit_spot,
            exit_perp=exit_perp,
            basis_now_bps=basis_now * 10000.0,
            basis_15m_bps=basis_15 * 10000.0,
            basis_30m_bps=basis_30 * 10000.0,
            basis_60m_bps=basis_60 * 10000.0,
            basis_slope_15m_bps=basis_slope_15 * 10000.0,
            basis_slope_30m_bps=basis_slope_30 * 10000.0,
            basis_slope_60m_bps=basis_slope_60 * 10000.0,
            net_event_return=net,
            funding_component=funding_component,
            basis_component=basis_component,
            fees_component=fees_component,
            veto_pass=veto_pass,
        ))
    return out


def summarize_variant(events: list[EventRow], variant: str, symbols_scope: set[str]) -> dict:
    scoped = [e for e in events if e.symbol in symbols_scope]
    if variant == 'extreme_only':
        sample = scoped
    elif variant == 'boundary_timed_extreme_only':
        sample = scoped
    elif variant == 'boundary_timed_extreme_only_plus_veto':
        sample = [e for e in scoped if e.veto_pass == 1]
    else:
        raise ValueError(variant)
    if not sample:
        return {
            'variant': variant,
            'symbols': ','.join(sorted(symbols_scope)),
            'events': 0,
            'positive_events': 0,
            'positive_ratio': math.nan,
            'mean_apr': math.nan,
            'mean_funding_bps': math.nan,
            'mean_basis_bps': math.nan,
            'mean_fee_bps': math.nan,
            'mean_net_bps': math.nan,
            'median_net_bps': math.nan,
            'total_pnl_usd': 0.0,
        }
    mean_net = sum(e.net_event_return for e in sample) / len(sample)
    med_sorted = sorted(e.net_event_return for e in sample)
    median = med_sorted[len(med_sorted) // 2]
    return {
        'variant': variant,
        'symbols': ','.join(sorted(symbols_scope)),
        'events': len(sample),
        'positive_events': sum(1 for e in sample if e.net_event_return > 0),
        'positive_ratio': sum(1 for e in sample if e.net_event_return > 0) / len(sample),
        'mean_apr': sum(e.apr for e in sample) / len(sample),
        'mean_funding_bps': sum(e.funding_component for e in sample) / len(sample) * 10000.0,
        'mean_basis_bps': sum(e.basis_component for e in sample) / len(sample) * 10000.0,
        'mean_fee_bps': sum(e.fees_component for e in sample) / len(sample) * 10000.0,
        'mean_net_bps': mean_net * 10000.0,
        'median_net_bps': median * 10000.0,
        'total_pnl_usd': sum(e.net_event_return * WINDOW_NOTIONAL for e in sample),
    }


def summarize_continuous(symbol: str) -> dict:
    end_dt = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=LOOKBACK_DAYS)
    funding = fetch_funding(symbol, int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000))
    in_pos = False
    entries = 0
    net = 0.0
    funding_component = 0.0
    for row in funding:
        apr = annualized_apr(float(row['fundingRate']))
        fr = float(row['fundingRate'])
        if (not in_pos) and fr >= 0 and apr >= BASELINE_ENTRY_APR:
            in_pos = True
            entries += 1
            net -= ENTRY_FEE_PCT
        if in_pos:
            net += fr
            funding_component += fr
        if in_pos and (fr < 0 or apr < BASELINE_EXIT_APR):
            in_pos = False
            net -= EXIT_FEE_PCT
    if in_pos:
        net -= EXIT_FEE_PCT
    return {
        'variant': 'continuous_threshold_carry',
        'symbols': symbol,
        'events': len(funding),
        'positive_events': '',
        'positive_ratio': '',
        'mean_apr': sum(annualized_apr(float(r['fundingRate'])) for r in funding) / len(funding),
        'mean_funding_bps': funding_component / max(entries, 1) * 10000.0,
        'mean_basis_bps': '',
        'mean_fee_bps': ((ENTRY_FEE_PCT + EXIT_FEE_PCT) * entries / max(entries, 1)) * 10000.0,
        'mean_net_bps': net / max(entries, 1) * 10000.0,
        'median_net_bps': '',
        'total_pnl_usd': net * WINDOW_NOTIONAL,
        'entries': entries,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    all_events: list[EventRow] = []
    for symbol in SYMBOLS:
        all_events.extend(build_events(symbol))
    write_csv(ART_DIR / 'extreme_event_rows.csv', [e.__dict__ for e in all_events])

    summary_rows = []
    for symbol in SYMBOLS:
        summary_rows.append(summarize_continuous(symbol))
        ev = [e for e in all_events if e.symbol == symbol]
        for variant in ['extreme_only', 'boundary_timed_extreme_only', 'boundary_timed_extreme_only_plus_veto']:
            summary_rows.append(summarize_variant(ev, variant, {symbol}))
    for variant in ['extreme_only', 'boundary_timed_extreme_only', 'boundary_timed_extreme_only_plus_veto']:
        summary_rows.append(summarize_variant(all_events, variant, set(SYMBOLS)))
    write_csv(ART_DIR / 'summary.csv', summary_rows)

    combined_veto = [e for e in all_events if e.veto_pass == 1]
    combined_non = [e for e in all_events if e.veto_pass == 0]
    decision = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'sample': 'BTCUSDT + ETHUSDT, 730d public Binance funding + spot/perp 5m boundary event study',
        'events_total': len(all_events),
        'events_veto_pass': len(combined_veto),
        'events_veto_fail': len(combined_non),
        'mean_net_bps_veto_pass': (sum(e.net_event_return for e in combined_veto) / len(combined_veto) * 10000.0) if combined_veto else None,
        'mean_net_bps_veto_fail': (sum(e.net_event_return for e in combined_non) / len(combined_non) * 10000.0) if combined_non else None,
        'verdict': 'background_P0',
        'one_line': 'Rank 338 的唯一 survivor follow-up 显示，极端 funding 尾部本身并不足以在 BTC/ETH 上留下稳定净收益；boundary-time 事件持有的 after-cost 期望仍为负，basis-expansion veto 只是在删坏事件而没有把样本整体抬到可 admission 的 P2 壳，因此应直接收口回 background/P0。',
    }
    if combined_veto and (sum(e.net_event_return for e in combined_veto) / len(combined_veto) > 0) and len(combined_veto) >= 8:
        decision['verdict'] = 'promote_P2'
        decision['one_line'] = 'Rank 338 的 survivor follow-up 显示，BTC/ETH 极端 funding 事件在 boundary-time + basis-expansion veto 下已留下正向 after-cost 净收益，足以升 P2。'
    (ART_DIR / 'decision.json').write_text(json.dumps(decision, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
