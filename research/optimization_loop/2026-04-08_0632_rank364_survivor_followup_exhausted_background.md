# Rank 364 survivor follow-up — keep_P1 exhausted -> background

- Time: 2026-04-08 06:32 UTC
- Target: `Rank 364 / Polymarket × Kalshi same-hour strike mismatch binary lock-in arb`
- Slot before action: `Surviving candidate`
- Action: 用 repo 的 clean-room expiry/settlement mapping、post-fee / post-slippage locked-edge 口径与 orphan-leg realism 证据，回答它是否足够从 `P1` 升到 `P2`
- Verdict: `keep_P1 exhausted -> background`

## Why this changes system belief
这条对象的 raw alpha 主语本身没问题：`same-hour strike mismatch -> binary lock-in arb` 的 payout 结构是清楚的，repo 也确实把 `Poly Down + Kalshi Yes` / `Poly Up + Kalshi No` 写成了扫描器。

但这次 survivor follow-up 要回答的不是“数学上像不像套利”，而是它是否已经有 admission 级的 **同事件映射 + post-cost + execution realism**。当前证据不够，因此不能升 `P2`。

## Decisive findings
1. **expiry / settlement mapping 仍然停在口头假设，不是 clean-room 证明。**
   - `thesis.md` 与 `README.md` 都只写“same hourly market / corresponding Kalshi markets”，但没有逐条证明两边的 `expiry timestamp`、`reference window`、`settlement source`、`boundary inclusion` 完全一致。
   - `get_current_markets.py` 甚至直接把 Polymarket 目标时间设为“当前整点”，Kalshi 目标时间设为“下一小时”，这说明 repo 本身就在用一个近似对位规则，而不是严谨的同事件 canonical mapping。
   - `fetch_current_kalshi.py` 只按 `event_ticker` 拉一整个事件，再从 `subtitle` 里正则提取 strike；并没有校验 resolution rule、结算时间戳或边界条件。

2. **post-cost locked edge 没有被 admission 级量化。**
   - `arbitrage_bot.py` 的判定门槛仍是裸的 `total_cost < 1.00`；并没有把 Polymarket / Kalshi 双边 fee、滑点、最小成交深度约束统一并入真实入场阈值。
   - `thesis.md` 只在 caveats 里口头提到 fees/liquidity/execution risk，没有把它们写成实际过滤条件或可复核的净收益分布。

3. **orphan-leg / queue-loss realism 仍是致命未解块，而不是可忽略尾部。**
   - 当前实现是逐腿读取 best ask 后直接相加，未给出同步成交、深度消耗、撤单失败、单腿先成交后的库存处理规则。
   - 这类跨 venue event arb 的真正风险就在这里；如果没有最小 fill protocol 或历史 orphan ratio，`1 - total_cost` 只是屏幕毛边，不是可 admission 的净边。

## Honest conclusion
这条线仍值得保留在素材库里，因为它把 prediction-market 里的 binary payout mismatch 压成了一个很清楚的 raw alpha skeleton；但在当前证据口径下，它还没有通过唯一一次 survivor follow-up 所要求的 decisive realism 检查。

因此本轮最诚实的收口不是 `promote_P2`，而是：

> `Rank 364` 的核心 locked edge 目前仍主要停留在 payout algebra + 名义上的 same-hour matching；repo 没有把 expiry/settlement canonical mapping、统一 post-cost 阈值与 orphan-leg execution protocol 压成 admission 级证据，因此 survivor follow-up 用尽，结论为 `keep_P1 exhausted -> background`。

## Runtime effect
- `Surviving candidate slot` 释放为 `none`
- `Rank 364` 移入 `Background pool`
- 当前轮 `cycle_plan` 第 1 项收口完成，结果为 `done`
