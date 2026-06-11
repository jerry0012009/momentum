#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ART_DIR = ROOT / 'reports' / 'artifacts' / 'scout_rank144_intraday_vol_commonality_15m'
SITE_DIR = ROOT / 'reports' / 'site' / 'factors' / 'scout_rank144_intraday_vol_commonality_15m'
READING_PATH = ROOT / 'reports' / 'site' / 'reading' / 'repo_scout' / 'rank144_intraday_vol_commonality_clean_replication.html'

SYMBOLS = {
    'BTC-USD': 'BTCUSDT',
    'ETH-USD': 'ETHUSDT',
    'SOL-USD': 'SOLUSDT',
}
INTERVAL = '15m'
LIMIT = 1500
RV_Z_THRESHOLD = 1.0
COMMONALITY_HIGH_MIN = 2
HOLD_BARS = 8
COST_BPS_PER_SIDE = 12.0
API = 'https://fapi.binance.com/fapi/v1/klines'

CSS = """
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; max-width:1180px; margin:32px auto; padding:0 18px 48px; line-height:1.68; color:#111827; background:#f8fafc; }
h1,h2,h3 { color:#111827; }
.card { border:1px solid #e5e7eb; border-radius:14px; background:white; padding:18px 20px; margin:16px 0; }
.muted { color:#6b7280; }
.good { color:#065f46; font-weight:600; }
.warn { color:#92400e; font-weight:600; }
.bad { color:#991b1b; font-weight:600; }
code { background:#f3f4f6; padding:1px 5px; border-radius:6px; }
table { width:100%; border-collapse:collapse; margin-top:12px; font-size:14px; background:white; }
th, td { border-bottom:1px solid #e5e7eb; padding:8px 10px; text-align:left; vertical-align:top; }
a { color:#2563eb; text-decoration:none; }
"""


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fetch_klines(symbol: str, limit: int = LIMIT) -> pd.DataFrame:
    qs = urlencode({'symbol': symbol, 'interval': INTERVAL, 'limit': limit})
    req = Request(f'{API}?{qs}', headers={'User-Agent': 'Mozilla/5.0'})
    with urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read().decode('utf-8'))
    df = pd.DataFrame(rows, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_volume', 'trade_count', 'taker_buy_base', 'taker_buy_quote', 'ignore',
    ])
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    df['timestamp'] = pd.to_datetime(df['open_time'], unit='ms', utc=True)
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamp').reset_index(drop=True)


def prepare_frames() -> dict[str, pd.DataFrame]:
    frames = {}
    for asset, symbol in SYMBOLS.items():
        df = fetch_klines(symbol)
        ret = np.log(df['close']).diff()
        rv1h = np.sqrt((ret.pow(2)).rolling(4, min_periods=4).sum())
        rv_mean = rv1h.rolling(96, min_periods=96).mean()
        rv_std = rv1h.rolling(96, min_periods=96).std(ddof=0)
        rv_z = (rv1h - rv_mean) / rv_std.replace(0, np.nan)
        out = df.copy()
        out['asset'] = asset
        out['rv1h'] = rv1h
        out['rv_z'] = rv_z
        frames[asset] = out
        time.sleep(0.2)
    return frames


def combine_commonality(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    merged = None
    for asset, df in frames.items():
        slim = df[['timestamp', 'rv_z']].rename(columns={'rv_z': f'rv_z_{asset}'})
        merged = slim if merged is None else merged.merge(slim, on='timestamp', how='inner')
    rv_cols = [c for c in merged.columns if c.startswith('rv_z_')]
    merged['commonality_count'] = merged[rv_cols].gt(RV_Z_THRESHOLD).sum(axis=1)
    return merged[['timestamp', 'commonality_count'] + rv_cols]


def simulate(frames: dict[str, pd.DataFrame], commonality: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    cost_rate = COST_BPS_PER_SIDE / 10000.0
    for asset, df in frames.items():
        joined = df.merge(commonality[['timestamp', 'commonality_count']], on='timestamp', how='inner')
        for side in ['long', 'short']:
            for i in range(96, len(joined) - HOLD_BARS - 1):
                row = joined.iloc[i]
                entry_idx = i + 1
                exit_idx = i + HOLD_BARS
                entry = float(joined.iloc[entry_idx]['open'])
                exit_px = float(joined.iloc[exit_idx]['close'])
                if not math.isfinite(entry) or not math.isfinite(exit_px) or entry <= 0:
                    continue
                gross = (exit_px / entry - 1.0) if side == 'long' else (entry / exit_px - 1.0)
                net = (1.0 + gross) * (1.0 - cost_rate) * (1.0 - cost_rate) - 1.0
                rows.append({
                    'asset': asset,
                    'side': side,
                    'signal_ts': row['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'entry_ts': joined.iloc[entry_idx]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'exit_ts': joined.iloc[exit_idx]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'commonality_count': int(row['commonality_count']),
                    'bucket': 'c2_3' if int(row['commonality_count']) >= COMMONALITY_HIGH_MIN else 'c0_1',
                    'net_ret': net,
                    'net_bp': net * 10000.0,
                    'win': int(net > 0),
                })
    return pd.DataFrame(rows)


def summarize(trades: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    split = (trades.groupby(['asset', 'side', 'bucket'], as_index=False)
             .agg(n=('net_bp', 'size'), mean_net_bp=('net_bp', 'mean'), win_rate=('win', 'mean')))
    pooled = (trades.groupby(['side', 'bucket'], as_index=False)
              .agg(n=('net_bp', 'size'), mean_net_bp=('net_bp', 'mean'), win_rate=('win', 'mean')))
    return split, pooled


def verdict(split: pd.DataFrame, pooled: pd.DataFrame) -> dict:
    def get(df: pd.DataFrame, **conds) -> pd.Series:
        mask = pd.Series(True, index=df.index)
        for k, v in conds.items():
            mask &= df[k].eq(v)
        return df[mask].iloc[0]

    short_low = get(pooled, side='short', bucket='c0_1')
    short_high = get(pooled, side='short', bucket='c2_3')
    long_low = get(pooled, side='long', bucket='c0_1')
    long_high = get(pooled, side='long', bucket='c2_3')
    short_improve = float(short_high['mean_net_bp'] - short_low['mean_net_bp'])
    long_delta = float(long_high['mean_net_bp'] - long_low['mean_net_bp'])

    split_pivot = split.pivot_table(index=['asset', 'side'], columns='bucket', values='mean_net_bp')
    short_split = split_pivot.xs('short', level='side').copy()
    short_split['delta_bp'] = short_split['c2_3'] - short_split['c0_1']
    improved_assets = int((short_split['delta_bp'] > 0).sum())

    score = {
        'usefulness': 2 if short_improve > 5 else 1,
        'time_stability': 1,
        'cross_asset_stability': 2 if improved_assets >= 2 else 1,
        'cost_trade_stability': 1,
        'deployability': 2,
    }
    hard_fails = []
    if float(short_high['mean_net_bp']) <= 0:
        hard_fails.append('not_post_cost_positive_even_in_best_bucket')
    if improved_assets < 3:
        hard_fails.append('cross_asset_asymmetry_persists_in_clean_rep')
    hard_fails.append('router_attachment_still_not_done')

    if short_improve > 8 and improved_assets >= 2 and float(short_high['mean_net_bp']) > -3.0:
        action = 'keep_P1'
        board_label = 'P1 / keep_P1 / budget used / breakout-short follow-up only'
    else:
        action = 'park'
        board_label = 'P0 / park / evidence only'

    return {
        'scorecard': score,
        'recommended_action': action,
        'board_label': board_label,
        'hard_fail_flags': hard_fails,
        'short_improvement_bp': short_improve,
        'long_delta_bp': long_delta,
        'short_high_mean_net_bp': float(short_high['mean_net_bp']),
        'improved_short_assets': improved_assets,
    }


def fmt(v: float | int | None, digits: int = 2) -> str:
    if v is None or pd.isna(v):
        return '-'
    return f'{float(v):.{digits}f}'


def render_table(df: pd.DataFrame) -> str:
    if df.empty:
        return '<p class="muted">暂无数据。</p>'
    headers = ''.join(f'<th>{escape(str(c))}</th>' for c in df.columns)
    body_rows = []
    for _, row in df.iterrows():
        cells = []
        for col in df.columns:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                cells.append(f'<td>{escape(fmt(val, 2))}</td>')
            else:
                cells.append(f'<td>{escape(str(val))}</td>')
        body_rows.append(f'<tr>{"".join(cells)}</tr>')
    return f'<table><thead><tr>{headers}</tr></thead><tbody>{"".join(body_rows)}</tbody></table>'


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(f"<!doctype html><html><head><meta charset='utf-8'><title>{escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>", encoding='utf-8')


def main() -> None:
    ensure_dir(ART_DIR)
    ensure_dir(SITE_DIR)
    ensure_dir(READING_PATH.parent)

    frames = prepare_frames()
    commonality = combine_commonality(frames)
    trades = simulate(frames, commonality)
    split, pooled = summarize(trades)
    decision = verdict(split, pooled)

    commonality.to_csv(ART_DIR / 'commonality_frame.csv', index=False)
    trades.to_csv(ART_DIR / 'trade_log.csv', index=False)
    split.to_csv(ART_DIR / 'asset_split_summary.csv', index=False)
    pooled.to_csv(ART_DIR / 'pooled_summary.csv', index=False)
    (pd.DataFrame([{
        'rv_z_threshold': RV_Z_THRESHOLD,
        'commonality_high_min': COMMONALITY_HIGH_MIN,
        'hold_bars': HOLD_BARS,
        'cost_bps_per_side': COST_BPS_PER_SIDE,
        'universe': 'BTCUSDT,ETHUSDT,SOLUSDT',
        'data_points_per_symbol': LIMIT,
    }])).to_csv(ART_DIR / 'threshold_config.csv', index=False)

    scorecard = {
        'rank': 144,
        'name': 'intraday volatility commonality asymmetric follow-up gate',
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
        'method': 'Binance USDⓈ-M 15m klines, 1h realized-vol zscore > 1, commonality_count>=2, next-bar open entry, hold 8 bars, 12bps/side cost',
        **decision,
        'why_now': '用一次冻结阈值 + BTC/ETH/SOL 分资产 clean replication，回答 Rank 144 还能不能继续留在 active Scout。',
        'main_weakness': '依然只是公共行情代理，尚未真正接到 production breakout-short router，也没有更长窗口的时间稳定性。',
    }
    (ART_DIR / 'promotion_scorecard.json').write_text(json.dumps(scorecard, ensure_ascii=False, indent=2), encoding='utf-8')
    pd.DataFrame([{
        'usefulness': decision['scorecard']['usefulness'],
        'time_stability': decision['scorecard']['time_stability'],
        'cross_asset_stability': decision['scorecard']['cross_asset_stability'],
        'cost_trade_stability': decision['scorecard']['cost_trade_stability'],
        'deployability': decision['scorecard']['deployability'],
        'hard_fail_flags': ';'.join(decision['hard_fail_flags']),
        'recommended_action': decision['recommended_action'],
        'why_now': '冻结阈值后做最小 clean replication，确认它该留样还是退出 active Scout。',
        'main_weakness': '还没接 router，也没做更长窗口稳健性。',
    }]).to_csv(ART_DIR / 'promotion_scorecard.csv', index=False)

    body = f"""
    <p><a href=\"../../plans/momentum_todo.html\">← 返回 TODO / desk board</a></p>
    <h1>Rank 144 · intraday volatility commonality · minimal clean replication</h1>
    <div class=\"card\">
      <p><b>Desk verdict：</b><span class=\"{'warn' if decision['recommended_action'] == 'keep_P1' else 'bad'}\">{escape(scorecard['board_label'])}</span></p>
      <p class=\"muted\">这次不再复读 digest，而是把阈值冻结成 <code>rv_z &gt; 1.0</code>、把 universe 固定成 <code>BTC/ETH/SOL</code>，看 short 侧改善是不是还站得住。</p>
      <p><b>关键读法：</b>short 高共振桶相对低共振桶改善 <code>{fmt(decision['short_improvement_bp'])} bp</code>；但 best bucket 仍未转正，且只做到 <code>{decision['improved_short_assets']}/3</code> 个币改善，所以不升 P2。</p>
    </div>
    <div class=\"card\">
      <h2>pooled summary</h2>
      {render_table(pooled)}
    </div>
    <div class=\"card\">
      <h2>asset split summary</h2>
      {render_table(split)}
    </div>
    <div class=\"card\">
      <h2>scorecard</h2>
      <ul>
        <li>usefulness = {decision['scorecard']['usefulness']}/3</li>
        <li>time_stability = {decision['scorecard']['time_stability']}/3</li>
        <li>cross_asset_stability = {decision['scorecard']['cross_asset_stability']}/3</li>
        <li>cost_trade_stability = {decision['scorecard']['cost_trade_stability']}/3</li>
        <li>deployability = {decision['scorecard']['deployability']}/3</li>
        <li>hard-fail flags = {escape(', '.join(decision['hard_fail_flags']))}</li>
        <li>recommended_action = {escape(decision['recommended_action'])}</li>
        <li>why_now = 冻结阈值后做一次真正会改变 verdict 的最小 clean replication。</li>
        <li>main_weakness = 还没接 router，也没做更长窗口时间稳定性。</li>
      </ul>
    </div>
    <div class=\"card\">
      <h2>artifact</h2>
      <ul>
        <li><code>reports/artifacts/scout_rank144_intraday_vol_commonality_15m/asset_split_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank144_intraday_vol_commonality_15m/pooled_summary.csv</code></li>
        <li><code>reports/artifacts/scout_rank144_intraday_vol_commonality_15m/threshold_config.csv</code></li>
        <li><code>reports/artifacts/scout_rank144_intraday_vol_commonality_15m/promotion_scorecard.json</code></li>
      </ul>
    </div>
    """
    write_html(SITE_DIR / 'report.html', 'Rank 144 commonality clean replication', body)
    write_html(READING_PATH, 'Rank 144 intraday vol commonality clean replication', body)
    print(json.dumps(scorecard, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
