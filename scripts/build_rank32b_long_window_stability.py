#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "build_rank32_ema_slope_clean_replication.py"
ART_DIR = ROOT / "reports" / "artifacts" / "scout_rank32b_slope_floor_continuation_15m"
SITE_DIR = ROOT / "reports" / "site" / "factors" / "scout_rank32b_slope_floor_continuation_15m"
CACHE_DIR = ART_DIR / "long_window_cache"
PRIMARY_VARIANT = "ema_cross_plus_slope_floor"
PRIMARY_COST = 6.0
DEFAULT_DAYS = 1825
DEFAULT_SYMBOLS = ["LTCUSDT", "NEARUSDT", "UNIUSDT"]
DEFAULT_TAG = "candidate_5y_stability"


def load_base_module():
    spec = importlib.util.spec_from_file_location("rank32_base", BASE_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


mod = load_base_module()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def pct(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v) * 100:.{digits}f}%"


def num(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return "-"
    return f"{float(v):.{digits}f}"


def render_table(df: pd.DataFrame, percent_cols: set[str] | None = None, digits_cols: dict[str, int] | None = None) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    percent_cols = percent_cols or set()
    digits_cols = digits_cols or {}
    headers = "".join(f"<th>{escape(str(c))}</th>" for c in df.columns)
    rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            value = row[col]
            if col in percent_cols:
                text = pct(value)
            elif isinstance(value, (float, np.floating, int, np.integer)) and not isinstance(value, bool):
                text = num(value, digits_cols.get(col, 2))
            else:
                text = str(value)
            cells.append(f"<td>{escape(text)}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table>"


def build_asset_map(symbols_csv: str) -> dict[str, str]:
    selected: dict[str, str] = {}
    for raw in symbols_csv.split(','):
        symbol = raw.strip().upper()
        if not symbol:
            continue
        if not symbol.endswith('USDT'):
            raise ValueError(f"unsupported symbol {symbol}: expected *USDT symbol")
        selected[symbol.replace('USDT', '-USD')] = symbol
    if not selected:
        raise ValueError('no symbols provided')
    return selected


def fetch_binance_bars(symbol: str, days: int, interval: str = '15m') -> pd.DataFrame:
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - days * 24 * 60 * 60 * 1000
    rows: list[list] = []
    current = start_ms
    while current < end_ms:
        params = urllib.parse.urlencode(
            {
                'symbol': symbol,
                'interval': interval,
                'startTime': current,
                'endTime': end_ms,
                'limit': 1000,
            }
        )
        url = f"https://api.binance.com/api/v3/klines?{params}"
        data = None
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(url, timeout=20) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                break
            except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
                last_error = exc
                time.sleep(1 + attempt)
        if data is None:
            raise RuntimeError(f"failed to fetch {symbol} after retries: {last_error}")
        if not data:
            break
        rows.extend(data)
        current = int(data[-1][6]) + 1
        if len(data) < 1000:
            break
    df = pd.DataFrame(
        rows,
        columns=[
            'open_time','open','high','low','close','volume','close_time','quote_asset_volume',
            'number_of_trades','taker_buy_base_asset_volume','taker_buy_quote_asset_volume','ignore',
        ],
    )
    out = pd.DataFrame(
        {
            'timestamp': pd.to_datetime(df['open_time'], unit='ms', utc=True),
            'open': pd.to_numeric(df['open'], errors='coerce'),
            'high': pd.to_numeric(df['high'], errors='coerce'),
            'low': pd.to_numeric(df['low'], errors='coerce'),
            'close': pd.to_numeric(df['close'], errors='coerce'),
            'volume': pd.to_numeric(df['volume'], errors='coerce'),
        }
    )
    return out.dropna().sort_values('timestamp').reset_index(drop=True)


def load_or_fetch_bars(symbol: str, days: int) -> pd.DataFrame:
    ensure_dir(CACHE_DIR)
    cache_path = CACHE_DIR / f"{symbol}__{days}d__15m.csv"
    if cache_path.exists():
        df = pd.read_csv(cache_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
        return df.sort_values('timestamp').reset_index(drop=True)
    bars = fetch_binance_bars(symbol, days=days)
    bars.to_csv(cache_path, index=False)
    return bars


def build_frame(asset: str, bars: pd.DataFrame) -> pd.DataFrame:
    frame = bars.copy().sort_values('timestamp').reset_index(drop=True)
    frame['asset'] = asset
    market = frame[['timestamp', 'close']].copy().rename(columns={'close': 'close_1h_src'}).set_index('timestamp')
    market_1h = market.resample('1h').last().dropna().reset_index()
    market_1h['ema_fast_1h'] = market_1h['close_1h_src'].ewm(span=mod.EMA_FAST_1H, adjust=False).mean()
    market_1h['ema_slow_1h'] = market_1h['close_1h_src'].ewm(span=mod.EMA_SLOW_1H, adjust=False).mean()
    market_1h['fast_slope'] = market_1h['ema_fast_1h'].pct_change()
    market_1h['slow_slope'] = market_1h['ema_slow_1h'].pct_change()
    frame = pd.merge_asof(frame, market_1h.sort_values('timestamp'), on='timestamp', direction='backward')
    frame['spread_mid'] = (frame['ema_fast_1h'] + frame['ema_slow_1h']) / 2.0
    frame['long_structure'] = (frame['ema_fast_1h'] > frame['ema_slow_1h']).fillna(False).astype(int)
    frame['short_structure'] = (frame['ema_fast_1h'] < frame['ema_slow_1h']).fillna(False).astype(int)
    frame['slope_floor_long'] = ((frame['fast_slope'] > mod.SLOPE_FLOOR) & (frame['slow_slope'] > 0)).fillna(False).astype(int)
    frame['slope_floor_short'] = ((frame['fast_slope'] < -mod.SLOPE_FLOOR) & (frame['slow_slope'] < 0)).fillna(False).astype(int)
    frame['slope_strength'] = frame['fast_slope'].abs().fillna(0.0) + frame['slow_slope'].abs().fillna(0.0)
    prev_close = frame['close'].shift(1)
    prev_fast = frame['ema_fast_1h'].shift(1)
    frame['cross_only_long'] = ((frame['long_structure'] == 1) & (prev_close <= prev_fast) & (frame['close'] > frame['ema_fast_1h'])).fillna(False).astype(int)
    frame['cross_only_short'] = ((frame['short_structure'] == 1) & (prev_close >= prev_fast) & (frame['close'] < frame['ema_fast_1h'])).fillna(False).astype(int)
    frame['slope_floor_long_signal'] = ((frame['cross_only_long'] == 1) & (frame['slope_floor_long'] == 1)).astype(int)
    frame['slope_floor_short_signal'] = ((frame['cross_only_short'] == 1) & (frame['slope_floor_short'] == 1)).astype(int)
    return frame


def build_yearly_summary(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame(columns=['asset', 'window', 'total_return', 'trades', 'win_rate'])
    work = trades.copy()
    work['event_ts'] = pd.to_datetime(work['event_ts'], utc=True)
    rows = []
    for asset, grp in work.groupby('asset', sort=True):
        start = grp['event_ts'].min()
        end = grp['event_ts'].max()
        total_days = max((end - start).days, 1)
        if total_days >= 365 * 4:
            edges = [end - pd.Timedelta(days=365 * i) for i in range(5, -1, -1)]
            for idx in range(len(edges) - 1):
                lower = edges[idx]
                upper = edges[idx + 1]
                window = grp[(grp['event_ts'] >= lower) & (grp['event_ts'] < upper)]
                if window.empty:
                    continue
                rows.append(
                    {
                        'asset': asset,
                        'window': f'year_{idx+1}',
                        'total_return': float((1.0 + window['net_ret']).prod() - 1.0),
                        'trades': int(len(window)),
                        'win_rate': float((window['net_ret'] > 0).mean()),
                    }
                )
        else:
            cut_recent = end - pd.Timedelta(days=min(240, total_days // 3))
            cut_mid = end - pd.Timedelta(days=min(480, 2 * total_days // 3))
            windows = [
                ('older', grp[grp['event_ts'] < cut_mid]),
                ('middle', grp[(grp['event_ts'] >= cut_mid) & (grp['event_ts'] < cut_recent)]),
                ('recent', grp[grp['event_ts'] >= cut_recent]),
            ]
            for name, window in windows:
                if window.empty:
                    continue
                rows.append(
                    {
                        'asset': asset,
                        'window': name,
                        'total_return': float((1.0 + window['net_ret']).prod() - 1.0),
                        'trades': int(len(window)),
                        'win_rate': float((window['net_ret'] > 0).mean()),
                    }
                )
    return pd.DataFrame(rows)


def build_verdict(asset_summary: pd.DataFrame, yearly_summary: pd.DataFrame, candidate_assets: list[str]) -> tuple[str, str]:
    cand = asset_summary[asset_summary['asset'].isin(candidate_assets)].copy()
    if cand.empty:
        return 'insufficient', '候选币没有形成有效样本。'
    cand_positive = int((cand['total_return'] > 0).sum())
    total_cand = int(len(cand))
    yearly = yearly_summary[yearly_summary['asset'].isin(candidate_assets)].copy()
    if yearly.empty:
        return 'insufficient', '缺少候选币的时间窗口分解结果。'
    stable_assets = []
    for asset, grp in yearly.groupby('asset', sort=True):
        pos_ratio = float((grp['total_return'] > 0).mean())
        if pos_ratio >= 0.6:
            stable_assets.append(asset)
    if cand_positive >= max(2, int(np.ceil(total_cand * 0.6))) and len(stable_assets) >= max(2, int(np.ceil(total_cand * 0.5))):
        return 'candidates mostly stable', f"{cand_positive}/{total_cand} 个候选币总体为正，且至少 {len(stable_assets)} 个候选币在分段窗口里大部分时期为正。"
    if cand_positive >= max(2, int(np.ceil(total_cand * 0.5))):
        return 'mixed but promising', f"{cand_positive}/{total_cand} 个候选币总体为正，但分段稳定性还不够一致，适合先 paper 再决定是否扩池。"
    return 'not yet stable enough', '候选币里不到多数能在更长历史里站住，不建议直接扩池。'


def build_html(generated_at: str, days: int, candidate_assets: list[str], asset_summary: pd.DataFrame, yearly_summary: pd.DataFrame, listing_summary: pd.DataFrame, verdict: str, reason: str) -> str:
    asset_view = asset_summary.copy().sort_values('total_return', ascending=False).reset_index(drop=True)
    candidate_yearly = yearly_summary[yearly_summary['asset'].isin(candidate_assets)].copy()
    candidate_label = ', '.join(a.replace('-USD', '') for a in candidate_assets)
    return f"""<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>Rank 32b · Long-window stability</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1180px; margin: 40px auto; padding: 0 18px; line-height: 1.7; color: #111827; background: #f8fafc; }}
    .card {{ border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }}
    .pill {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; color:#3730a3; font-size:12px; margin-right:6px; }}
    .muted {{ color:#6b7280; }}
    code {{ background:#f3f4f6; padding:1px 5px; border-radius:6px; }}
    table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; }}
    th,td {{ border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }}
  </style>
</head>
<body>
  <p><a href='./report.html'>← 返回 Rank 32b 主报告</a></p>
  <h1>Rank 32b · Long-window stability</h1>
  <p class='muted'>生成时间：{escape(generated_at)} ｜ 目标：验证候选币在更长历史里是否大部分时间稳定有效。</p>

  <div class='card'>
    <h2>这轮回答什么</h2>
    <ul>
      <li>保留原始骨架不变：<code>EMA cross + aligned slope floor</code>。</li>
      <li>候选币：<code>{escape(candidate_label)}</code>。</li>
      <li>时间口径：最长回看 {days} 天；若 Binance 上线历史不足，则如实按可用样本分段。</li>
      <li>成本口径：这里只看与当前主研究一致的 <code>6bps/side</code>，先回答“长窗口下站不站得住”。</li>
    </ul>
  </div>

  <div class='card'>
    <h2>hard read</h2>
    <p><span class='pill'>{escape(verdict)}</span></p>
    <p class='muted'>{escape(reason)}</p>
  </div>

  <div class='card'>
    <h2>可用历史说明</h2>
    {render_table(listing_summary, digits_cols={'bars':0})}
  </div>

  <div class='card'>
    <h2>总体摘要（6bps）</h2>
    {render_table(asset_view[['asset','sample_start','sample_end','bars','trades','total_return','win_rate','no_trade_ratio']], percent_cols={'total_return','win_rate','no_trade_ratio'}, digits_cols={'bars':0,'trades':0})}
  </div>

  <div class='card'>
    <h2>候选币分段稳定性</h2>
    {render_table(candidate_yearly[['asset','window','total_return','trades','win_rate']], percent_cols={'total_return','win_rate'}, digits_cols={'trades':0})}
  </div>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description='Build long-window stability page for Rank 32b candidates.')
    parser.add_argument('--symbols', type=str, default=','.join(DEFAULT_SYMBOLS), help='Comma-separated USDT symbols')
    parser.add_argument('--days', type=int, default=DEFAULT_DAYS)
    parser.add_argument('--tag', type=str, default=DEFAULT_TAG)
    args = parser.parse_args()

    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(CACHE_DIR)

    asset_map = build_asset_map(args.symbols)
    candidate_assets = list(asset_map.keys())
    tag = str(args.tag).strip() or DEFAULT_TAG

    asset_rows = []
    trades_all = []
    listing_rows = []
    for asset, symbol in asset_map.items():
        bars = load_or_fetch_bars(symbol, days=int(args.days))
        frame = build_frame(asset, bars)
        trades, no_trade_ratio, eligible_bars = mod.build_trades(frame, asset, PRIMARY_VARIANT, PRIMARY_COST)
        if not trades.empty:
            trades_all.append(trades)
        asset_rows.append(
            {
                **mod.summarize_asset(
                    trades,
                    asset=asset,
                    variant=PRIMARY_VARIANT,
                    cost_bps=PRIMARY_COST,
                    no_trade_ratio=no_trade_ratio,
                    eligible_bars=eligible_bars,
                ),
                'sample_start': bars['timestamp'].min().strftime('%Y-%m-%d'),
                'sample_end': bars['timestamp'].max().strftime('%Y-%m-%d'),
                'bars': int(len(bars)),
            }
        )
        listing_rows.append(
            {
                'asset': asset,
                'symbol': symbol,
                'sample_start': bars['timestamp'].min().strftime('%Y-%m-%d'),
                'sample_end': bars['timestamp'].max().strftime('%Y-%m-%d'),
                'bars': int(len(bars)),
            }
        )

    asset_summary = pd.DataFrame(asset_rows)
    trades_df = pd.concat(trades_all, ignore_index=True) if trades_all else pd.DataFrame()
    yearly_summary = build_yearly_summary(trades_df)
    listing_summary = pd.DataFrame(listing_rows)
    verdict, reason = build_verdict(asset_summary, yearly_summary, candidate_assets)
    generated_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

    asset_path = ART_DIR / f'{tag}_asset_summary.csv'
    yearly_path = ART_DIR / f'{tag}_yearly_summary.csv'
    listing_path = ART_DIR / f'{tag}_listing_summary.csv'
    html_path = SITE_DIR / f'{tag}.html'

    asset_summary.to_csv(asset_path, index=False)
    yearly_summary.to_csv(yearly_path, index=False)
    listing_summary.to_csv(listing_path, index=False)
    html_path.write_text(build_html(generated_at, int(args.days), candidate_assets, asset_summary, yearly_summary, listing_summary, verdict, reason), encoding='utf-8')

    print(
        json.dumps(
            {
                'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                'html': str(html_path),
                'asset_summary_csv': str(asset_path),
                'yearly_summary_csv': str(yearly_path),
                'listing_summary_csv': str(listing_path),
                'verdict': verdict,
                'candidate_assets': candidate_assets,
                'days': int(args.days),
            },
            ensure_ascii=False,
        )
    )


if __name__ == '__main__':
    main()
