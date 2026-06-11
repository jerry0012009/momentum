# Strategy Review — 2026-04-03 00:55 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态（`git status --short`）
- 最近 optimization 证据：
  - `research/optimization_loop/2026-04-03_0048_rank301_slot_guard_block_bb_zscore_mr.md`
  - `research/optimization_loop/2026-04-03_0017_rank300_liquidity_split_lagged_return_keep_p1.md`
  - `research/optimization_loop/2026-04-03_0003_rank299_survivor_exit_background.md`
  - `research/optimization_loop/2026-04-02_2329_rank299_ema_rsi_regime_keep_p1.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-03_0014_strategy-review.md`
- 最近新 intake 候选：
  - `research/quant_digests/2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
  - `research/quant_digests/2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
  - `research/quant_digests/2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`

## 只回答 4 个问题

1) `Paper launch queue` 是否非空？
- 否。
- `Paper launch queue.current_target = none`。
- 当前只有 `Rank 200 / 201 / 213 / 229` 处于 `connected_runner_live`；没有等待 bot2 兜底推进的 queue 头对象。

2) 本轮 `fresh intake` 是什么？
- 当前运行态里，fresh intake 头仍是 `research/quant_digests/2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`。
- 但它现在是 **合法对象、非法时点**：对象本身已被识别为独立 `overshoot-snapback` raw-alpha 候选，可是 `Rank 300` 仍占用唯一 survivor slot，所以 fresh intake 暂时只能维持 `blocked`。
- 一旦 `Rank 300` 在本轮前部收口，这条 `2356` 就应恢复为下一条正式 fresh intake 头。

3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- 值得。
- 上一条 fresh intake 是 `Rank 300 / 24h lagged-return × liquidity-split sign flip alpha`，其 first verdict 已明确说明它不是旧 `loser-bounce` 的换词包装，而是一个真正的 `liquidity-conditioned direction fork` 家族：在当前 liquid perp desk 上更像 high-liquidity `winner-follow` sleeve。
- 它还没有直接到 `P2`，但也明显不是该直接扔回 `background/P0` 的弱题；所以按 policy，它值得那唯一一次 survivor follow-up。
- 这次 follow-up 必须只围绕仅剩的两个 blocker：`liquidity cutoff` 与 `formation/holding pocket`；如果还收不出口，就应诚实退回 `background/P0`。

4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- 当前不存在明确 `Active P2`（`current_target = none`）。
- 最近一次 P2 出口仍是 `Rank 285` 的 `one-time P2->P1 re-scope`；此后没有新对象进入 `Active P2`。
- 因而当前不存在需要 bot2 兜底裁成 `P3 / P1 / P0` 的在役 P2 对象。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot = Rank 300`
- `Active P2 slot = none`
- 当前前排对象均有正式 rank；本轮无需补发新整数 `Rank`。

## P2 -> P3 兜底裁判检查
- 当前没有 `Active P2`，因此不触发 bot2 直接改写到 `P3 / Paper launch queue` 或 handoff 路径。
- 最近证据里也没有出现“对象已足够 paper trade，但 bot3 还没升”的漏升案例。

## 本轮排班结论
按 policy 默认顺序，当前轮必须重排为：
`P3 handoff > P2 admission/promote/park > P1 survivor follow-up > fresh intake > P0`

当前实际运行态：
- `P3` 无待接线对象；
- `Active P2 = none`；
- `Surviving candidate = Rank 300`；
- `Fresh intake slot` 当前被 `2356` 合法占位但因 survivor lock 暂时 `blocked`。

因此本轮 `cycle_plan` 必须先把已有前排对象收口，再接 fresh intake：
1. `Rank 300` survivor follow-up（唯一一次 decisive follow-up）
2. `2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
3. `2026-04-03_0042_btc-volclock-first30-impulse-alpha.md`
4. `2026-04-02_2257_rf-threshold-hfpt-pairs-alpha.md`

这么排的原因是：
- 不能让新的 fresh intake 越过现存 survivor；
- `2356` 已被证明是合法候选，所以 survivor 一旦收口，它就应回到 fresh intake 头；
- `0042` 是最新且主语清楚的新 directional raw-alpha，优先级高于更旧的 `2043`；
- `2257` 继续保留为 conditional fresh intake。

## 本轮写回内容
- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改动：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排

## 本轮改变系统认知的一句话
当前轮的真正前排不是新的发现，而是 `Rank 300` 的唯一 survivor 收口；在它诚实结束前，`2356` 只能维持 `blocked`，所以 bot2 已把 `cycle_plan` 改回 policy 要求的顺序：先做 `Rank 300`，再做 `BB/z-score MR`，然后才轮到新的 `BTC first30 impulse` 与 `RF threshold pairs` intake。
