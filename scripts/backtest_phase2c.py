#!/usr/bin/env python3
"""
Phase 2c Carry Harvest Backtest Engine
=======================================
基于 v1.6a 框架，新增 stall 结构实时识别和 funding_extreme 计算。

核心逻辑：
1. 在事件日当天（h=0 到 h=8）识别"可能进入 stall 结构 + neg_extreme funding"的币种
2. 测试5个候选信号（A-E）
3. 参数扫描 + 结果缓存

输出：
- 参数扫描结果 CSV
- 最优信号推荐
- 因子分析
"""
import pandas as pd
import numpy as np
import os, time, json
from itertools import product
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "reports" / "artifacts" / "binance_hourly_event_study_v1_6" / "hourly_event_panel.pkl"
V1_5_EVENTS = ROOT / "jerry" / "wlfi" / "FR_Monitor" / "reports" / "artifacts" / "binance_daily_event_study_v1_5" / "enriched_gainer_events_v1_5.csv"
OUT_DIR = ROOT / "reports" / "artifacts" / "binance_event_study_phase2c"
os.makedirs(OUT_DIR, exist_ok=True)

COST_PER_TRADE = 0.0013  # 0.13% round trip (baseline)

# ── Load data ──────────────────────────────────────────────────────────────
print("=" * 70)
print("PHASE 2C CARRY HARVEST BACKTEST")
print("=" * 70)

print("\n[1/4] Loading hourly event panel...")
t0 = time.time()
panel = pd.read_pickle(PANEL)
panel = panel.sort_values(['symbol', 'event_date', 'ts']).reset_index(drop=True)
panel['ret_1h'] = panel.groupby(['symbol', 'event_date'])['close'].pct_change()
print(f"  {len(panel):,} rows, {time.time()-t0:.1f}s")

print("\n[2/4] Loading v1.5 event classification...")
v15 = pd.read_csv(V1_5_EVENTS)
v15['event_date'] = v15['event_date'].astype(str)
print(f"  {len(v15):,} events")

# Merge v1.5 structure classification into panel
panel['event_date'] = panel['event_date'].astype(str)
panel = panel.merge(
    v15[['event_date', 'symbol', 'structure', 'carry_raw', 'funding_bucket']],
    on=['event_date', 'symbol'],
    how='left',
    suffixes=('', '_v15')
)
print(f"  Merged structure classification: {panel['structure'].notna().sum():,} rows with structure")

# ── Pre-process: extract arrays per event ──────────────────────────────────
print("\n[3/4] Building event arrays...")
t0 = time.time()

event_metas = []   # symbol, event_date, year, structure
event_arrays = []  # dict of numpy arrays

for (sym, ed), ev_data in panel.groupby(['symbol', 'event_date']):
    ev = ev_data.sort_values('ts').reset_index(drop=True)
    n = len(ev)
    if n < 30:
        continue

    rets = ev['ret_1h'].values.astype(np.float64)
    vols = ev['quote_volume'].values.astype(np.float64)
    funding = ev['funding_rate'].values.astype(np.float64)
    tbr = ev['taker_buy_ratio'].values.astype(np.float64)
    closes = ev['close'].values.astype(np.float64)
    highs = ev['high'].values.astype(np.float64)
    lows = ev['low'].values.astype(np.float64)
    hfe = ev['hours_from_event'].values.astype(np.float64)

    # Trailing vol means
    s = pd.Series(vols)
    tv12 = s.rolling(12, min_periods=6).mean().values
    tv20 = s.rolling(20, min_periods=10).mean().values

    # Cumulative returns (3h, 6h rolling)
    rs = pd.Series(rets)
    cr3 = ((1 + rs).rolling(3).apply(np.prod, raw=True) - 1).values
    cr6 = ((1 + rs).rolling(6).apply(np.prod, raw=True) - 1).values

    # Price volatility (4h rolling std of returns)
    vol_4h = rs.rolling(4, min_periods=2).std().values

    # Funding percentile (rolling 24h)
    fs = pd.Series(funding)
    funding_pctl = fs.rolling(24, min_periods=12).apply(
        lambda x: (x.iloc[-1] <= x).mean(), raw=False
    ).values

    # Structure from v1.5
    structure = ev['structure'].iloc[0] if 'structure' in ev.columns else 'unknown'

    event_metas.append({
        'symbol': sym,
        'event_date': ed,
        'year': int(str(ed)[:4]),
        'structure': structure,
    })
    event_arrays.append({
        'hfe': hfe,
        'closes': closes,
        'highs': highs,
        'lows': lows,
        'vols': vols,
        'rets': rets,
        'funding': funding,
        'tbr': tbr,
        'tv12': tv12,
        'tv20': tv20,
        'cr3': cr3,
        'cr6': cr6,
        'vol_4h': vol_4h,
        'funding_pctl': funding_pctl,
    })

N_EVENTS = len(event_metas)
print(f"  {N_EVENTS} events, {time.time()-t0:.1f}s")

# ── Signal detection functions ──────────────────────────────────────────────
print("\n[4/4] Defining signal detection functions...")

def detect_signal_A(funding_pctl_thresh=0.10, vol_contraction_thresh=0.80, max_drop=0.02):
    """
    Signal A: funding_extreme + volume_contraction
    条件：
    1. funding_rate < p10（极端负funding）
    2. 当前小时成交额 < 过去12小时均值的 80%（成交额萎缩）
    3. 价格跌幅 < 2%（没有暴跌）
    """
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']

        for i in range(12, len(hfe) - 1):
            h = hfe[i]
            if h < 0 or h > 8:  # 事件日当天
                continue

            # 条件1: 极端负funding
            if np.isnan(ev['funding_pctl'][i]) or ev['funding_pctl'][i] > funding_pctl_thresh:
                continue

            # 条件2: 成交额萎缩
            if np.isnan(ev['tv12'][i]) or ev['tv12'][i] <= 0:
                continue
            vol_ratio = ev['vols'][i] / ev['tv12'][i]
            if vol_ratio > vol_contraction_thresh:
                continue

            # 条件3: 没有暴跌
            if h >= 1:
                drop = (ev['closes'][i] / ev['closes'][i-1]) - 1
                if drop < -max_drop:
                    continue

            results.append((ei, {
                'bar': i,
                'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'funding_at_signal': ev['funding'][i],
                'funding_pctl': ev['funding_pctl'][i],
                'vol_ratio': vol_ratio,
                'ret_at_signal': ev['rets'][i],
                'tbr_at_signal': ev['tbr'][i],
            }))
    return results


def detect_signal_B(funding_pctl_thresh=0.10, price_vol_thresh=0.05):
    """
    Signal B: funding_extreme + price_stall
    条件：
    1. funding_rate < p10（极端负funding）
    2. 过去4小时价格波动 < 5%（横盘整理）
    3. 当前价格 > 事件日开盘价（仍在高位）
    """
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']

        # 找到事件日开盘价（h=0 的 open，用 h=0 的 close 近似）
        event_open_idx = None
        for i in range(len(hfe)):
            if hfe[i] >= 0:
                event_open_idx = i
                break
        if event_open_idx is None:
            continue
        event_open = ev['closes'][event_open_idx]

        for i in range(event_open_idx + 4, len(hfe) - 1):
            h = hfe[i]
            if h < 0 or h > 8:
                continue

            # 条件1: 极端负funding
            if np.isnan(ev['funding_pctl'][i]) or ev['funding_pctl'][i] > funding_pctl_thresh:
                continue

            # 条件2: 横盘整理（过去4小时波动 < 5%）
            if np.isnan(ev['vol_4h'][i]) or ev['vol_4h'][i] > price_vol_thresh:
                continue

            # 条件3: 仍在高位
            if ev['closes'][i] < event_open:
                continue

            results.append((ei, {
                'bar': i,
                'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'funding_at_signal': ev['funding'][i],
                'funding_pctl': ev['funding_pctl'][i],
                'vol_4h': ev['vol_4h'][i],
                'ret_at_signal': ev['rets'][i],
                'tbr_at_signal': ev['tbr'][i],
            }))
    return results


def detect_signal_C(funding_pctl_thresh=0.10, decel_ratio=0.50):
    """
    Signal C: funding_extreme + momentum_deceleration
    条件：
    1. funding_rate < p10（极端负funding）
    2. 过去3小时累计收益 < 事件日当小时收益的 50%（动量衰减）
    3. 成交额没有显著萎缩（仍在交易）
    """
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']

        for i in range(6, len(hfe) - 1):
            h = hfe[i]
            if h < 0 or h > 8:
                continue

            # 条件1: 极端负funding
            if np.isnan(ev['funding_pctl'][i]) or ev['funding_pctl'][i] > funding_pctl_thresh:
                continue

            # 条件2: 动量衰减
            if np.isnan(ev['cr3'][i]) or np.isnan(ev['rets'][i]):
                continue
            if ev['rets'][i] == 0:
                continue
            if ev['cr3'][i] > decel_ratio * ev['rets'][i]:
                continue

            # 条件3: 成交额没有显著萎缩
            if np.isnan(ev['tv12'][i]) or ev['tv12'][i] <= 0:
                continue
            vol_ratio = ev['vols'][i] / ev['tv12'][i]
            if vol_ratio < 0.3:  # 成交额萎缩超过70%
                continue

            results.append((ei, {
                'bar': i,
                'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'funding_at_signal': ev['funding'][i],
                'funding_pctl': ev['funding_pctl'][i],
                'cr3': ev['cr3'][i],
                'ret_at_signal': ev['rets'][i],
                'vol_ratio': vol_ratio,
                'tbr_at_signal': ev['tbr'][i],
            }))
    return results


def detect_signal_D(funding_pctl_thresh=0.10, tbr_thresh=0.55):
    """
    Signal D: funding_extreme + taker_sell_exhaustion
    条件：
    1. funding_rate < p10（极端负funding）
    2. taker_buy_ratio > 0.55（卖压耗竭，买盘开始主导）
    3. 价格企稳或小幅反弹
    """
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']

        for i in range(4, len(hfe) - 1):
            h = hfe[i]
            if h < 0 or h > 8:
                continue

            # 条件1: 极端负funding
            if np.isnan(ev['funding_pctl'][i]) or ev['funding_pctl'][i] > funding_pctl_thresh:
                continue

            # 条件2: 卖压耗竭
            if np.isnan(ev['tbr'][i]) or ev['tbr'][i] < tbr_thresh:
                continue

            # 条件3: 价格企稳或小幅反弹
            if h >= 1:
                ret = ev['rets'][i]
                if ret < -0.02:  # 跌幅超过2%
                    continue

            results.append((ei, {
                'bar': i,
                'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'funding_at_signal': ev['funding'][i],
                'funding_pctl': ev['funding_pctl'][i],
                'tbr_at_signal': ev['tbr'][i],
                'ret_at_signal': ev['rets'][i],
            }))
    return results


def detect_signal_E(funding_pctl_thresh=0.10, vol_contraction_thresh=0.80,
                    price_vol_thresh=0.05, stall_score_thresh=0.70):
    """
    Signal E: 组合信号（funding + stall_score）
    stall_score = 0.4 * funding_extreme + 0.3 * volume_contraction + 0.3 * price_stall
    条件：
    1. stall_score > 阈值（如 0.7）
    2. 价格没有暴跌
    """
    results = []
    for ei in range(N_EVENTS):
        ev = event_arrays[ei]
        hfe = ev['hfe']

        for i in range(12, len(hfe) - 1):
            h = hfe[i]
            if h < 0 or h > 8:
                continue

            # 计算 stall_score
            # 1. funding_extreme score (0-1, 越负越高)
            if np.isnan(ev['funding_pctl'][i]):
                continue
            funding_score = 1.0 - ev['funding_pctl'][i]  # pctl=0 -> score=1, pctl=1 -> score=0

            # 2. volume_contraction score (0-1, 越萎缩越高)
            if np.isnan(ev['tv12'][i]) or ev['tv12'][i] <= 0:
                continue
            vol_ratio = ev['vols'][i] / ev['tv12'][i]
            vol_score = max(0, 1.0 - vol_ratio)  # vol_ratio=0 -> score=1, vol_ratio=1 -> score=0

            # 3. price_stall score (0-1, 越平稳越高)
            if np.isnan(ev['vol_4h'][i]):
                continue
            price_score = max(0, 1.0 - ev['vol_4h'][i] / price_vol_thresh)

            # 组合评分
            stall_score = 0.4 * funding_score + 0.3 * vol_score + 0.3 * price_score

            if stall_score < stall_score_thresh:
                continue

            # 条件2: 没有暴跌
            if h >= 1:
                drop = (ev['closes'][i] / ev['closes'][i-1]) - 1
                if drop < -0.03:  # 跌幅超过3%
                    continue

            results.append((ei, {
                'bar': i,
                'trigger_hour': h,
                'entry_price': ev['closes'][i],
                'funding_at_signal': ev['funding'][i],
                'funding_pctl': ev['funding_pctl'][i],
                'vol_ratio': vol_ratio,
                'vol_4h': ev['vol_4h'][i],
                'stall_score': stall_score,
                'funding_score': funding_score,
                'vol_score': vol_score,
                'price_score': price_score,
                'ret_at_signal': ev['rets'][i],
                'tbr_at_signal': ev['tbr'][i],
            }))
    return results


# ── Trade simulation (same as v1.6a) ──────────────────────────────────────
def simulate_trade(ev, sig, exit_rule):
    """Simulate one trade. Returns dict."""
    bi = sig['bar']
    ep = sig['entry_price']
    etype = exit_rule['type']
    max_h = exit_rule.get('hold_hours', 8)
    sl = exit_rule.get('sl_pct')
    tp = exit_rule.get('tp_pct')

    cum_ret = 0.0
    cum_fund = 0.0
    exit_reason = 'max_hold'
    exit_bar = bi

    for ho in range(1, max_h + 1):
        bar = bi + ho
        if bar >= len(ev['closes']):
            exit_bar = bar - 1
            exit_reason = 'data_end'
            break

        h_ret = ev['rets'][bar]
        h_fund = ev['funding'][bar]

        # SL check (hourly low)
        if sl is not None:
            if (ev['lows'][bar] / ep) - 1 <= -sl:
                cum_ret += -sl
                cum_fund += h_fund * 0.5
                exit_bar = bar
                exit_reason = 'stop_loss'
                break

        # TP check (hourly high)
        if tp is not None:
            if (ev['highs'][bar] / ep) - 1 >= tp:
                cum_ret += tp
                cum_fund += h_fund * 0.5
                exit_bar = bar
                exit_reason = 'take_profit'
                break

        # Funding flip check
        if etype == 'funding_flip' and h_fund > 0:
            cum_ret = (1 + cum_ret) * (1 + h_ret) - 1
            cum_fund += h_fund
            exit_bar = bar
            exit_reason = 'funding_flip'
            break

        cum_ret = (1 + cum_ret) * (1 + h_ret) - 1
        cum_fund += h_fund
        exit_bar = bar

    total = cum_ret - cum_fund
    return {
        'hold_hours': exit_bar - bi,
        'price_return': cum_ret,
        'funding_sum': cum_fund,
        'total_return': total,
        'net_return': total - COST_PER_TRADE,
        'exit_reason': exit_reason,
    }


# ── Parameter grid ─────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("RUNNING PARAMETER SCAN")
print("=" * 70)

# Signal A parameters
SIGNAL_A_PARAMS = list(product(
    [0.05, 0.10, 0.15, 0.20],  # funding_pctl_thresh
    [0.60, 0.70, 0.80, 0.90],  # vol_contraction_thresh
    [0.01, 0.02, 0.03],         # max_drop
))

# Signal B parameters
SIGNAL_B_PARAMS = list(product(
    [0.05, 0.10, 0.15, 0.20],  # funding_pctl_thresh
    [0.03, 0.05, 0.08, 0.10],  # price_vol_thresh
))

# Signal C parameters
SIGNAL_C_PARAMS = list(product(
    [0.05, 0.10, 0.15, 0.20],  # funding_pctl_thresh
    [0.30, 0.50, 0.70],         # decel_ratio
))

# Signal D parameters
SIGNAL_D_PARAMS = list(product(
    [0.05, 0.10, 0.15, 0.20],  # funding_pctl_thresh
    [0.50, 0.55, 0.60],         # tbr_thresh
))

# Signal E parameters
SIGNAL_E_PARAMS = list(product(
    [0.05, 0.10, 0.15, 0.20],  # funding_pctl_thresh
    [0.60, 0.70, 0.80],         # vol_contraction_thresh
    [0.03, 0.05, 0.08],         # price_vol_thresh
    [0.50, 0.60, 0.70, 0.80],   # stall_score_thresh
))

EXIT_RULES = [
    {'type': 'fixed_hold', 'hold_hours': 4, 'label': 'hold_4h'},
    {'type': 'fixed_hold', 'hold_hours': 8, 'label': 'hold_8h'},
    {'type': 'fixed_hold', 'hold_hours': 12, 'label': 'hold_12h'},
    {'type': 'fixed_hold', 'hold_hours': 24, 'label': 'hold_24h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.03, 'label': 'sl_3pct_8h'},
    {'type': 'stop_loss', 'hold_hours': 8, 'sl_pct': 0.05, 'label': 'sl_5pct_8h'},
    {'type': 'take_profit', 'hold_hours': 8, 'tp_pct': 0.05, 'label': 'tp_5pct_8h'},
    {'type': 'take_profit', 'hold_hours': 8, 'tp_pct': 0.10, 'label': 'tp_10pct_8h'},
    {'type': 'funding_flip', 'hold_hours': 24, 'label': 'funding_flip'},
]

# ── Main scan loop ─────────────────────────────────────────────────────────
all_results = []

def run_scan(signal_name, signal_func, param_grid, param_names):
    """Run parameter scan for a signal."""
    print(f"\n{'─' * 60}")
    print(f"Scanning {signal_name}: {len(param_grid)} param combos × {len(EXIT_RULES)} exit rules")
    print(f"{'─' * 60}")

    results = []
    t_start = time.time()

    for pi, params in enumerate(param_grid):
        # Detect signals once per param combo
        signals = signal_func(*params)
        n_sigs = len(signals)

        if n_sigs == 0:
            continue

        # Simulate each exit rule
        for er in EXIT_RULES:
            trades = []
            for ei, sig in signals:
                tr = simulate_trade(event_arrays[ei], sig, er)
                tr.update(sig)
                tr['year'] = event_metas[ei]['year']
                tr['structure'] = event_metas[ei]['structure']
                trades.append(tr)

            td = pd.DataFrame(trades)
            net = td['net_return']

            if len(net) < 50:
                continue

            # Calculate metrics
            win_rate = (net > 0).mean()
            sharpe = net.mean() / net.std() * np.sqrt(365 * 24) if net.std() > 0 else 0

            # Year breakdown
            year_stats = {}
            for yr in sorted(td['year'].unique()):
                yr_mask = td['year'] == yr
                yr_net = net[yr_mask]
                if len(yr_net) >= 10:
                    year_stats[yr] = {
                        'n': int(yr_mask.sum()),
                        'mean': float(yr_net.mean()),
                        'win_rate': float((yr_net > 0).mean()),
                    }

            # Structure breakdown
            struct_stats = {}
            for struct in td['structure'].unique():
                if pd.isna(struct):
                    continue
                struct_mask = td['structure'] == struct
                struct_net = net[struct_mask]
                if len(struct_net) >= 10:
                    struct_stats[struct] = {
                        'n': int(struct_mask.sum()),
                        'mean': float(struct_net.mean()),
                        'win_rate': float((struct_net > 0).mean()),
                    }

            results.append({
                'signal': signal_name,
                'params': dict(zip(param_names, params)),
                'exit_rule': er['label'],
                'n_trades': len(net),
                'net_mean': float(net.mean()),
                'net_median': float(net.median()),
                'win_rate': float(win_rate),
                'sharpe': float(sharpe),
                'funding_mean': float(td['funding_at_signal'].mean()),
                'trigger_hour_mean': float(td['trigger_hour'].mean()),
                'year_stats': year_stats,
                'struct_stats': struct_stats,
            })

        if (pi + 1) % 10 == 0:
            elapsed = time.time() - t_start
            eta = elapsed / (pi + 1) * (len(param_grid) - pi - 1)
            print(f"  [{pi+1}/{len(param_grid)}] {elapsed:.0f}s elapsed, {eta:.0f}s remaining")

    print(f"  Total: {len(results)} variants, {time.time()-t_start:.1f}s")
    return results


# Run all signals
print("\n" + "=" * 70)
print("STARTING PARAMETER SCAN")
print("=" * 70)

t_total = time.time()

# Signal A
all_results.extend(run_scan(
    'A_funding_vol_contraction',
    detect_signal_A,
    SIGNAL_A_PARAMS,
    ['funding_pctl_thresh', 'vol_contraction_thresh', 'max_drop']
))

# Signal B
all_results.extend(run_scan(
    'B_funding_price_stall',
    detect_signal_B,
    SIGNAL_B_PARAMS,
    ['funding_pctl_thresh', 'price_vol_thresh']
))

# Signal C
all_results.extend(run_scan(
    'C_funding_momentum_decel',
    detect_signal_C,
    SIGNAL_C_PARAMS,
    ['funding_pctl_thresh', 'decel_ratio']
))

# Signal D
all_results.extend(run_scan(
    'D_funding_taker_exhaustion',
    detect_signal_D,
    SIGNAL_D_PARAMS,
    ['funding_pctl_thresh', 'tbr_thresh']
))

# Signal E
all_results.extend(run_scan(
    'E_combo_stall_score',
    detect_signal_E,
    SIGNAL_E_PARAMS,
    ['funding_pctl_thresh', 'vol_contraction_thresh', 'price_vol_thresh', 'stall_score_thresh']
))

print(f"\n{'=' * 70}")
print(f"SCAN COMPLETE: {len(all_results)} total variants, {time.time()-t_total:.1f}s")
print(f"{'=' * 70}")

# ── Save results ───────────────────────────────────────────────────────────
print("\nSaving results...")

# Save full results as JSON
results_path = OUT_DIR / "param_scan_results.json"
with open(results_path, 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"  Saved: {results_path}")

# Create summary DataFrame
summary_rows = []
for r in all_results:
    row = {
        'signal': r['signal'],
        'exit_rule': r['exit_rule'],
        'n_trades': r['n_trades'],
        'net_mean': r['net_mean'],
        'win_rate': r['win_rate'],
        'sharpe': r['sharpe'],
        'funding_mean': r['funding_mean'],
    }
    row.update(r['params'])
    summary_rows.append(row)

summary_df = pd.DataFrame(summary_rows)
summary_path = OUT_DIR / "param_scan_summary.csv"
summary_df.to_csv(summary_path, index=False)
print(f"  Saved: {summary_path}")

# Find top variants
print("\n" + "=" * 70)
print("TOP VARIANTS BY NET MEAN")
print("=" * 70)

top_variants = summary_df.sort_values('net_mean', ascending=False).head(20)
for i, row in top_variants.iterrows():
    print(f"\n#{i+1}: {row['signal']} + {row['exit_rule']}")
    print(f"  Net mean: {row['net_mean']*100:.2f}%")
    print(f"  Win rate: {row['win_rate']*100:.1f}%")
    print(f"  Sharpe: {row['sharpe']:.2f}")
    print(f"  Trades: {row['n_trades']}")
    print(f"  Funding mean: {row['funding_mean']*100:.3f}%")
    print(f"  Params: {dict(row.drop(['signal', 'exit_rule', 'n_trades', 'net_mean', 'win_rate', 'sharpe', 'funding_mean']))}")

print(f"\n{'=' * 70}")
print("NEXT STEPS")
print(f"{'=' * 70}")
print("1. Run build_phase2c_report.py to generate HTML report")
print("2. Review top variants for overfitting")
print("3. Test on out-of-sample data")
print("4. Consider paper lane promotion")
