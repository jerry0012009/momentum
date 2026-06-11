from __future__ import annotations
import argparse, csv, json, math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

COST_PER_SIDE_BPS = 6.0
ROUNDTRIP_COST = COST_PER_SIDE_BPS * 2 / 10000.0
ARMS = ['baseline', 'veto_opp_dir', 'confirm_same_dir_only']


def parse_args():
    p = argparse.ArgumentParser(description='Minimal PBO/DSR proxy demo from rank139-style trade log.')
    p.add_argument('--trade-log', required=True)
    p.add_argument('--event-col', default='event_0.8')
    p.add_argument('--out-dir', required=True)
    p.add_argument('--label', default='Rank 139 @ thr=0.8')
    return p.parse_args()


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def stdev(xs):
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def sharpe_proxy(xs):
    s = stdev(xs)
    return mean(xs) / s if s > 0 else 0.0


def deflated_sharpe_proxy(sharpe: float, trials: int, n: int) -> float:
    if n <= 1:
        return sharpe
    penalty = math.sqrt(max(0.0, 2.0 * math.log(max(1, trials)))) / math.sqrt(n)
    return sharpe - penalty


def arm_returns(row, event_col):
    gross = float(row['gross_ret'])
    net = gross - ROUNDTRIP_COST
    event = row[event_col].strip()
    out = {'baseline': net}
    if event != 'opp_dir_first':
        out['veto_opp_dir'] = net
    if event == 'same_dir_first':
        out['confirm_same_dir_only'] = net
    return out


def rank_desc(values_by_arm):
    ordered = sorted(values_by_arm.items(), key=lambda kv: kv[1], reverse=True)
    return {arm: i + 1 for i, (arm, _) in enumerate(ordered)}


def main():
    args = parse_args()
    rows = list(csv.DictReader(open(args.trade_log, newline='')))
    rows.sort(key=lambda r: r['signal_ts'])
    split = max(1, len(rows) // 2)
    halves = {'is_first_half': rows[:split], 'oos_second_half': rows[split:]}

    half_stats = {}
    for half_name, subset in halves.items():
        by_arm = defaultdict(list)
        for row in subset:
            for arm, ret in arm_returns(row, args.event_col).items():
                by_arm[arm].append(ret)
        metrics = {}
        for arm in ARMS:
            xs = by_arm.get(arm, [])
            metrics[arm] = {
                'trades': len(xs),
                'mean_net': mean(xs),
                'sharpe_proxy': sharpe_proxy(xs),
            }
        half_stats[half_name] = metrics

    all_by_arm = defaultdict(list)
    for row in rows:
        for arm, ret in arm_returns(row, args.event_col).items():
            all_by_arm[arm].append(ret)

    is_rank = rank_desc({a: half_stats['is_first_half'][a]['sharpe_proxy'] for a in ARMS})
    oos_rank = rank_desc({a: half_stats['oos_second_half'][a]['sharpe_proxy'] for a in ARMS})

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / 'rank139_pbo_honesty_proxy_scorecard.csv'
    json_path = out_dir / 'rank139_pbo_honesty_proxy_meta.json'

    best_is = min(is_rank, key=is_rank.get)
    best_oos_rank = oos_rank[best_is]
    flag = 'high' if best_oos_rank >= 3 else ('medium' if best_oos_rank == 2 else 'low')

    with csv_path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'label', 'arm', 'trades', 'mean_net_6bps', 'sharpe_proxy_6bps',
            'deflated_sharpe_proxy_6bps', 'is_rank_by_sharpe_proxy', 'oos_rank_by_sharpe_proxy',
            'selection_flip_flag', 'note'
        ])
        writer.writeheader()
        for arm in ARMS:
            xs = all_by_arm.get(arm, [])
            shp = sharpe_proxy(xs)
            writer.writerow({
                'label': args.label,
                'arm': arm,
                'trades': len(xs),
                'mean_net_6bps': mean(xs),
                'sharpe_proxy_6bps': shp,
                'deflated_sharpe_proxy_6bps': deflated_sharpe_proxy(shp, trials=len(ARMS), n=len(xs)),
                'is_rank_by_sharpe_proxy': is_rank[arm],
                'oos_rank_by_sharpe_proxy': oos_rank[arm],
                'selection_flip_flag': flag if arm == best_is else '',
                'note': 'proxy only; not canonical CSCV/PBO/DSR'
            })

    meta = {
        'generated_at_utc': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
        'label': args.label,
        'source_trade_log': args.trade_log,
        'event_col': args.event_col,
        'roundtrip_cost_assumption_bps': COST_PER_SIDE_BPS * 2,
        'best_is_arm_by_sharpe_proxy': best_is,
        'best_is_arm_oos_rank_by_sharpe_proxy': best_oos_rank,
        'selection_flip_flag': flag,
        'warning': 'This is a minimal offline proxy, not canonical CSCV/PBO or Deflated Sharpe Ratio.'
    }
    json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    print(csv_path)
    print(json_path)


if __name__ == '__main__':
    main()
