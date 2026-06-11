# Rank 197 survivor follow-up — park to background

- Time: 2026-03-27 13:41 UTC
- Target: `Rank 197 / top-vs-bottom lagged-return XS ranking`
- Prior state: sole `Surviving candidate slot` occupant with `followup_budget_remaining = 1`
- This round action: execute the one allowed clean-room follow-up only, then force a single survivor verdict
- Outcome: `park_to_background`

## What was checked
I deliberately did **not** reopen the old paper-era RF framing. This follow-up only asked the compressed survivor question from runtime:

> 在 liquid perp universe 上，用过去多窗口 lagged returns 做横截面排序；每个 rebalance 做多最强 top3、做空最弱 bottom3，持有约 120 分钟，看成本后 top-minus-bottom spread 是否仍保留足够可信的正向雏形。

Two minimal clean-room probes were run on public Binance USDT perpetual data:

1. **Probe A** — broad top-volume `15m` universe, average of lagged-return windows `1/2/4/8/16/32` bars, rebalance every `8` bars (`120m`), equal-weight `top3 vs bottom3`, with `8 bps` round-trip drag.
   - Artifact: `reports/artifacts/rank197_survivor_followup_summary.json`
   - Result snapshot:
     - `portfolio_mean_bp_per_rebalance = +5.36 bps`
     - `daily_mean_bp = +8.13 bps/day`
     - `portfolio_t = 0.45`
     - `daily_t = 0.68`
   - Immediate problem: this universe admitted non-target contaminants such as `XAUUSDT`, `XAGUSDT`, `PAXGUSDT` and several obviously unstable oddballs.

2. **Probe B** — cleaner mature-crypto attempt (`15m`, same ranking/holding logic, same `8 bps` drag, age floor + commodity proxy exclusions).
   - Artifact: `reports/artifacts/rank197_survivor_followup_summary_v2.json`
   - Result snapshot:
     - `portfolio_mean_bp_per_rebalance = +14.25 bps`
     - `daily_mean_bp = +30.30 bps/day`
     - `portfolio_t = 1.09`
     - `daily_t = 1.47`
   - But the supposedly cleaner universe still concentrated in symbols like `SIRENUSDT`, `PIPPINUSDT`, `PORT3USDT`, `CUSDT`, `ALPACAUSDT`, `BNXUSDT`, not the kind of stable liquid perp core that would justify treating this as an honest desk-ready baseline.

## Why this does **not** earn `promote_P2`
The follow-up succeeded in one narrow sense: the underlying mother-object is not obviously nonsense. A plain lagged-return top-minus-bottom spread can print positive in some recent Binance-perp slices.

But that is **not** the bar for survivor promotion.

To promote `Rank 197` into `P2`, this one allowed follow-up needed to show that the alpha survives in a **recognizably liquid, honest, desk-relevant perp universe**. Instead, the positive read kept relying on a polluted or unstable symbol mix, while the cleaner attempts still had weak significance and poor universe credibility.

So the system-learning sentence is:

> `Rank 197 / top-vs-bottom lagged-return XS ranking` 的 plain lagged-return XS spread 在宽松 Binance perp 样本里能印出一点正向均值，但这一步正值主要依赖污染或不稳定币池，尚不足以证明它在诚实的 liquid-perp baseline 上成立，因此本轮用完 survivor 的唯一 follow-up 后，直接 `park_to_background`，不升 `P2`。

## Runtime consequences
- `Surviving candidate slot` should be cleared.
- `Active P2 slot` remains `none`.
- `cycle_plan` item 4 should be marked `done` with the park verdict above.
- `Background pool.latest_parked` should update to this object.

## Artifacts
- `reports/artifacts/rank197_survivor_followup_summary.json`
- `reports/artifacts/rank197_survivor_followup_summary_v2.json`
