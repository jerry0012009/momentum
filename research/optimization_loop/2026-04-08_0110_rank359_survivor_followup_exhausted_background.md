# Rank 359 / chart-image trend score × next-hour drift / survivor follow-up exhausted -> background

- Time: 2026-04-08 01:10 UTC
- Operator: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-07_2236_chart-image-trend-score-alpha.md`
- Prior state: `Surviving candidate slot`
- Verdict: `keep_P1 exhausted -> background`

## What changed system truth
`Rank 359` 作为独立 raw-alpha intake 仍成立，但它的唯一一次 survivor follow-up 不能诚实把对象推进到 `P2`：当前能压清的，只有“rolling chart image -> trend score -> next-hour drift”这个研究主语，以及 `15m 持有 4 bar / 5m 持有 12 bar` 的最小迁移壳；**不能压清的关键部分**仍是相对 `simple ROC / EMA slope` 的 after-cost 独立增量，以及足够非摘要级的实现口径。因此这一步的正确收口不是继续开放式 `keep_P1`，而是 `keep_P1 exhausted -> background`。

## Why this is not promote_P2
1. **增量证据仍停在假设层，不在结果层。**
   - digest 里写清了应做的 A/B：`A = 12h ROC / EMA slope`、`B = chart-image score`、`C = A+B`。
   - 但当前并没有任何实际结果表明 `B` 或 `C` 在 `after-cost spread return / rank IC` 上稳定优于 `A`。
   - 对 short-cycle desk，`P2` admission 不是“概念上可能有增量”，而是至少要看到“它不像只是复杂化的 momentum 包装”。这一条目前没有被压实。

2. **执行壳存在，但还不足以证明“可交易性已过最低门槛”。**
   - `top 20% long / bottom 20% short`、持有 1 小时、按 `4 bps fee + 1 bp slippage` 每边扣成本，这些是合理的最小 paper shell。
   - 但它们仍是 digest 里的 clean-room 实验提案，不是对象自身已被复刻出的交易结果；因此只能说明“知道该怎么测”，不能说明“已值得升 P2”。

3. **当前证据口径主要还是摘要级。**
   - source digest 已明确保留：本轮依据主要来自 Crossref abstract + journal metadata，全文实现细节未压到可复核层。
   - 这意味着图像构造、缩放、训练/验证切分、交易映射等最容易出错或泄漏的部分，都还没有被锁死到足以进入 admission 的程度。

## Why it still stays as a remembered background candidate
- 它和 `pattern-shortlist × next-hour drift` 不同，不是 parser 式离散形态；也和 plain breakout / ROC 不同，主语确实是连续价格形状表示。
- 所以这不是 `P0 / false lead`；而是**独立想法成立，但 survivor 预算用尽**。
- 后续若要重新打开，必须带着新证据回来：例如全文实现细节、明确的 `B vs A` after-cost 增量，或可复刻的 crypto 结果；不能只重复“图像可能学到更多形状信息”。

## Runtime write-back required
- `Surviving candidate slot` 从 `Rank 359` 释放，`followup_budget_remaining` 归零。
- `Background pool` 的最新 parked 对象更新为 `Rank 359`。
- `cycle_plan` 第 1 项结果写为：`Rank 359：chart-image trend score × next-hour drift 仍是独立 raw alpha，但 survivor 唯一 follow-up 未能压清相对 simple ROC / EMA slope 的 after-cost 独立增量与非摘要级实现口径，因此 keep_P1 exhausted -> background`。
- `cycle_plan` 第 1 项状态写为 `done`。

## Operational note
- 已按要求尝试刷新首页：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- 本轮两次执行均被系统 `SIGKILL`，因此本轮 reader-facing 首页索引未确认刷新；runtime/state/log 已完成写回，研究结论本身不受影响。
