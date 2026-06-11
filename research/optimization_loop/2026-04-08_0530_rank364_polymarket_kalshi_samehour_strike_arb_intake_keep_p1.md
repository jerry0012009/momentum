# Rank 364 — Polymarket × Kalshi same-hour strike mismatch fresh intake keep_P1

- Time: 2026-04-08 05:30 UTC
- Target: `research/quant_digests/2026-04-08_0322_polymarket-kalshi-samehour-strike-arb-alpha.md`
- Slot before action: `Fresh intake`
- Action: 对 `same-hour strike mismatch × binary lock-in arb` 做 fresh first verdict
- Verdict: `keep_P1 -> Surviving candidate`

## Why this changes system belief
这条对象已经不只是 prediction-market dashboard / repo showcase，而是把一个可独立复现的 raw alpha 主语压到了可执行层：

1. **主语清楚**：同一小时到期、同一底层事件、不同 strike 表达下，存在 `combo_cost < locked payout` 的 binary mispricing；
2. **执行壳存在**：repo 已把两种方向 (`Poly Down + Kalshi Yes` / `Poly Up + Kalshi No`) 与 `profit = 1 - total_cost` 写成实时扫描逻辑；
3. **约束边界清楚**：fee/slippage、orphan-leg、expiry mapping、halt/深度不足 都已明确是决定性 realism 风险，而不是完全缺席；
4. **适合当前队列**：它是高确定性、小容量、事件驱动的 relative-value sleeve，和泛 prediction-market commentary 有明显区分。

## Why it is not P2 yet
还不够直接升 `P2`，因为当前证据仍停在 thesis + scanner 壳层：

- 还没有 clean-room 方式统一验证 `same expiry / same settlement definition / strike mapping` 的历史可用样本；
- 还没有 post-fee / post-slippage 的真实 locked-edge 分布；
- 最关键的 orphan-leg / queue-loss 仍未被量化成 admission 级证据。

所以本轮最诚实结论不是 `background/P0`，也不是直接 `P2`，而是：

> `Rank 364` 已形成独立的 `same-hour strike mismatch -> binary lock-in arb` raw alpha skeleton，值得保留到 `P1` 做唯一一次 survivor follow-up，但当前还缺 clean-room mapping 与 post-cost/orphan-leg realism，因此先不升 `P2`。

## Runtime effect
- 为该 fresh intake 分配正式 `Rank 364`
- `Fresh intake` 完成 first verdict
- `Surviving candidate slot` 切换到 `Rank 364`
- survivor follow-up budget 设为 `1`
