# 2026-04-17 13:51 UTC bot2 strategy review

## Inputs checked
- Policy: `docs/BOT2_BOT3_POLICY.md`
- State: `docs/BOT2_BOT3_STATE.md`
- Repo status: `git status --short`（仍主要是历史遗留未跟踪临时文件；本轮不把这些噪音当成调度依据）
- Recent optimization loop:
  - `2026-04-17_1332_rank419_xsmomentum_btcvoloverlay_first_verdict_keep_p1.md`
  - `2026-04-17_1346_item3_rank60_conditional_freshintake_blocked_survivor_lock.md`
- Recent strategy review: `2026-04-17_1248_strategy-review.md`
- Recent park-reframe candidates:
  - `research/park_reframe/2026-04-06_1034_rank60-park-reframe.md`
  - `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
  - `research/park_reframe/2026-04-03_0656_rank57-park-reframe.md`

## 四个问题（本轮结论）
1. `Paper launch queue` 是否非空？
   - 结论：**否**。
   - `current_target = none`；`connected_runner_live` 虽非空，但这些对象都已完成 runner + scheduler + first verified run，不属于待接线 queue。

2. 本轮 `fresh intake` 是什么？
   - 结论：**`Rank 419 / cross-sectional relative-strength continuation × BTC realized vol / dispersion overlay`**。
   - 解释：runtime 前排里最新被 bot3 真正首判并保留下来的对象就是 `Rank 419`；它当前同时占用 `Fresh intake slot` 与 `Surviving candidate slot`。此时 bot2 不应再把“更新鲜但已收口为 P0 的旧 intake”误当成本轮 fresh intake。

3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
   - 结论：**值得，而且这唯一一次 follow-up 已被 `Rank 419` 锁定。**
   - 理由：`2026-04-17_1332_rank419_xsmomentum_btcvoloverlay_first_verdict_keep_p1.md` 已把 blocker 收敛得很干净：base alpha 不是 overlay，而是 `liquid-major crypto cross-sectional relative-strength continuation`；当前唯一 decisive blocker 是 `short-leg cost`。这正符合 policy 里“上一条 fresh intake 若首判 `keep_P1`，其唯一 survivor follow-up 享有前排锁定权”的条件。

4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
   - 结论：**不存在。**
   - `Active P2 = none`；最近一次 P2 出口仍是 `Rank 417` 的 one-time `P2->P1 re-scope`，但它已经退出 active 槽位，不构成本轮待判对象。

## Rank 合规检查
- `Paper launch queue / Surviving candidate / Active P2` 当前不存在“已到 `keep_P1 / P2 / P3` 却没有正式 Rank”的违规。
- 本轮无需补发新 Rank。

## 排班判断
- 当前没有待接线 `P3`，也没有 `Active P2`。
- 但存在明确的 survivor 锁定位对象 `Rank 419`，所以默认排班必须先收口它的唯一 follow-up，不能让新的 intake 抢到前面。
- `Rank 419` 已不是开放式研究问题；本轮应直接做出口式 survivor follow-up：
  - 若 `short BTC/ETH` 收缩版在统一 desk 成本下仍保留费后边际，就应升入 `P2 admission`；
  - 若费后不成立，就应诚实收口 `background/P0`；
  - 不得再给它写第三种模糊拖延型 `keep_P1`。
- 只有在 `Rank 419` 诚实收口后，剩余预算才应回到 fresh intake。按 policy 的来源优先级与现有 `derived_hypothesis_drafted` 存量，当前最合适的补位顺序是：
  1. `Rank 60`（retest-window impulse re-break confirmation）
  2. `Rank 27`（breakout-bar taker-imbalance confirmation on neckline break）
  3. `Rank 57`（pre-break compression admission）

## State rewrite（本轮执行）
- 未改写前排槽位身份：
  - `Fresh intake slot` 仍为 `Rank 419 / first_verdict_keep_P1`
  - `Surviving candidate slot` 仍锁定 `Rank 419`
  - `Active P2 slot` 仍为 `none`
- 仅按 policy 重写 `cycle_plan` 为当前合法顺序：
  1. `Rank 419` survivor 唯一 follow-up（先回答 `P2` 还是 `P0`）
  2. `Rank 60` conditional fresh intake
  3. `Rank 27` conditional fresh intake
  4. `Rank 57` conditional fresh intake

## P2->P3 兜底裁判检查
- 本轮无 `Active P2`，因此不存在“desk review 已清楚表明足够值得 paper trade，但 bot3 尚未升级”的兜底升 `P3` 场景。
- 本轮无需把任何对象强制写入 `P3 / Paper launch queue` 或 handoff 路径。

## Tail steps
- homepage 刷新：已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，进程于 `2026-04-17 14:00 UTC` 被 `SIGKILL` 终止；按 policy 作为**非阻断尾部失败**处理，不回滚本轮 review / state rewrite。
- 邮件通知：继续单独执行中文邮件摘要发送。
