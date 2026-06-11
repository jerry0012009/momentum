# 2026-03-16 03:17 UTC · Desk Board Review

## Desk verdict

当前 desk 结论比上一轮更明确一格：**`Paper Seat = EMA` 不变，`Live Seat = breakout` 继续保留，但当前正式 desk call 应写成 `keep but narrower-scope`，`Scout Seat` 继续找更短周期的 crypto challenger，且目前仍没有新的 shortlist candidate。**

这轮最值得动的不是重排三席，而是把 `Live Seat verdict` 从“默认继续占位”提升成**显式 verdict**，避免 bot3 把 breakout 误读成还可以无限续切的大主线。

## 这轮先检查了什么

1. repo 状态
   - 当前 worktree 仍有大量历史脏改 / 未跟踪文件；本轮只碰 `docs/TODO.md` 顶部作战板与 review 记录。
2. 最近 optimization logs
   - `2026-03-16_0314_tiny-live-plumbing-board.md`：bot3 已按新 Run 3 fallback 真正切去做了一张 `tiny-live plumbing board`。
   - `2026-03-16_0302_no-progress.md`：确认当前 EMA 仍在 waiting-window，breakout 仍在 rerun cooldown。
3. 最近 strategy review
   - `2026-03-16_0310_strategy-review.md` 已把双阻塞窗口下的 `Run 3 fallback` 写硬。
4. 当前 cron 列表 / run history
   - `bot3-momentum-auto-opt-13m` 当前列表上是 `error`，但 recent run history 显示：最近一轮红在 **exact-text edit mismatch**，并非方向跑偏；而且同轮 summary 与 log 都表明它实际切到了 `tiny-live plumbing`。
   - `bot7-quant-digest-4h` 当前正常。

## Paper Seat verdict

- **谁坐 Paper Seat：** `EMA baseline family`
- **结论：** 继续坐，不改席位。
- **原因：**
  - 仍是 `closest to paper`；
  - 已有 `candidate spec / operating spec / monitoring board / runbook / ledger / refresh history`；
  - 最近真实 completed-bar history 已落下，当前真正缺的是 **连续 market-close refresh / week-1 review 的 forward honesty**，不是更多说明页。
- **当前 blocker：** `refresh continuity / week-1 review continuity / demotion discipline`

## Live Seat verdict

- **谁坐 Live Seat：** `support_breakout_v0`
- **正式 verdict：** **`keep but narrower-scope`**
- **为什么不是 plain keep：**
  - 最近多轮都没有继续减少最关键 blocker；
  - 当前更诚实的位置已经不是“再多做几轮同样本切片就能升级”，而是：`up-flat biased conditional alpha / one_more_gate`。
- **为什么还不是 bench / replace：**
  - 目前仍没有更强的替代 challenger；
  - breakout 仍是最接近 `crypto tiny-live review` 的现有席位。
- **为什么还不能 live-approved：**
  - `pure down coverage = 0`
  - `pre-down bridge coverage = 0`
  - 所以它最缺的还是 **`paper/live mismatch honesty`**，不能诚实假设 default policy 已能穿过 crypto stress pocket。

## Scout Seat verdict

- **当前在找什么：**
  - `crypto 5m/15m`
  - 更贴近 `breakout / confirmation`
  - 尽量满足 `全文可得 + 有代码/可 clean-room`
  - 目标是尽快拿到 first verdict，而不是做泛泛文献综述。
- **有没有新的 shortlist：** **暂时没有。**
- **当前判断：** Scout Seat 继续保留低频辅助位置，但现在还没产出可替换 Live Seat 的 shortlist candidate。

## Next 3 bot3 runs

> 注意：从当前时钟看，未来约 40 分钟内 `EMA` 大概率仍未到 A 股真实 close；所以接下来 3 个 bot3 runs 不应再假装优先做 Paper continuation，而应按 blocked fallback 走。

1. **Run 1 — Live Seat hard verdict / cooldown-aware check**
   - 先看 breakout cooldown 是否已走完；
   - 若仍在 cooldown，**不要 rerun**，直接补一张更 deployment-facing 的 `narrower-scope / keep-one_more_gate` blocker sync；
   - 若 cooldown 恰好结束且 cache 仍领先，再只做 **1 次** heavy rerun 检查。

2. **Run 2 — Scout Seat shortlist card**
   - 产出一张 `crypto 5m/15m breakout/confirmation` 候选卡；
   - 默认要求：`全文可得 + 有代码/可 clean-room + 能更快拿到 first verdict`。

3. **Run 3 — tiny-live plumbing 续接一小步**
   - 在已生成的 `small_live_plumbing_v1` 基础上，再补最小可执行切片之一：
     - `live ledger fields`
     - `routing dry-run checklist`
     - `paper/live mismatch guardrail`
   - 只有当 breakout 在前两轮里真的出现新 blocker reduction，才允许挪回 Live Seat 继续深挖。

## 本轮改动

### 已改：`docs/TODO.md` 顶部 `Live Seat verdict`

新增当前 desk call：
- **`keep but narrower-scope`**
- 明确写死：
  - 当前按 `up-flat biased conditional alpha / one_more_gate` 读；
  - 默认继续保留席位；
  - 若后续仍没有新的 `pure-test / down-tail` blocker reduction，则优先转向 `bench / replace`，而不是继续近义续命。

### 这轮不改

- 不改 `Paper Seat / Scout Seat` 席位
- 不改 cron 频率
- 不改 bot7 方向

原因：当前问题不是调度频率不对，而是 **Live Seat 需要更清楚的显式 verdict**。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改频率；当前红灯主要是并发 edit collision，不是主线跑偏
- `bot7 4h`：不改，继续做 Scout Seat 辅助

## 本轮一句话结论（给 Jerry）

**这轮 desk board 我只补了最必要的一刀：EMA 继续坐 Paper Seat 不变，breakout 继续坐 Live Seat，但正式改写为 `keep but narrower-scope`；Scout Seat 继续找 5m/15m 的 crypto breakout/confirmation challenger，但目前还没有新 shortlist。**
