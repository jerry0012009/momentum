# 2026-03-16 06:33 UTC · Desk Board Review

## 本轮一句话判断

**席位不换；当前 desk 的关键不是再改席位，而是把 07:00 UTC 前后的排班切准。`Paper Seat = EMA` 继续保持 `running paper pilot / on-clock waiting next refresh`；`Live Seat = breakout` 继续维持 `keep but narrower-scope`，但只剩那 1 次 honest rerun 机会；而接下来 3 个 bot3 runs 应改成“close 前打一枪 Live，close 后第一轮立刻回 Paper”。**

## 本轮先检查了什么

1. **repo 状态**
   - worktree 仍有大量与本轮无关的历史脏改 / 未跟踪文件；本轮只做 `TRADING DESK BOARD` 顶部最小排班更新、review 记录、plans 镜像/首页刷新与邮件摘要。
2. **最近 optimization logs**
   - `2026-03-16_0515_scout-rank2-friction-recheck.md`
   - `2026-03-16_0525_small-live-parity-red-ladder.md`
   - 本轮没有新的成功 breakout rerun log 落地。
3. **最近 strategy review**
   - 上一轮（`05:53`）已把 `EMA` 改写为 `running paper pilot`，并把 breakout 收紧成“只再给 1 次 honest rerun”。
4. **当前 cron / bot3 run history**
   - `bot3-momentum-auto-opt-13m` 当前列表仍是 `error`；
   - 最近可见的两类失败分别是：
     - `build_alpha_closure_board_report.py` 的 exact-text edit mismatch
     - 最新一轮模型超时
   - 说明当前不应把 `breakout rerun` 安排成可无限重试的长任务。

## 当前 strongest evidence

1. **Paper Seat 继续是 EMA，而且现在确实应按 running paper 读**
   - `ema_paper_trading_refresh_history.csv` 已有 `6` 条 completed-bar rows；
   - `创业板ETF 1d` 行明确写成 `refresh_green_primary_live`；
   - `ema_paper_trading_runbook.csv` / `monitoring_board.csv` 也都把它写成当前唯一 primary paper pilot。
   - 所以这条线当前不是“要不要 paper”，而是**何时继续按时钟续写下一次 refresh**。

2. **Live Seat 仍没有新 blocker reduction，所以 verdict 先不改，但机会也不再增加**
   - 当前没有新的成功 breakout rerun log 能证明 blocker 已下降；
   - 关键 blocker 仍是：`pure down coverage = 0/100`、`pre-down bridge = 0/11`。
   - 因此这轮仍应维持：**`keep but narrower-scope`**。
   - 但由于上一轮已经写死“只再给 1 次 honest rerun”，当前更该把这 1 次机会安排在 close 前，而不是继续挂在未来排班里漂着。

3. **Scout Seat 没有新 shortlist，也没有新的必须抢占资源的证据**
   - `Rank 2 combo_all` 仍是当前更值得轻量 forward 复核的 confirmation challenger；
   - 但现在距离 A 股 close 已不到 30 分钟，当前更高杠杆动作不是再重复 scout same-sample 复核，而是把 bot3 第一轮 post-close 资源让给 EMA ledger append。

4. **tiny-live plumbing 继续只当 fallback，不抢 close 后第一优先级**
   - `small_live_parity_red_action_ladder_v1.csv` 与 `sample_row_v1.csv` 已经落下；
   - close 前若 Live 那一枪没打成，fallback 继续沿这条 execution chain 补相邻卡仍合理；
   - 但 close 后第一轮默认应回到 `Paper Seat`。

## 当前 weakest / should-park lines

- 在 `Rank 1` 没有 genuinely new bar 前重复 scout same-sample recheck：继续 park。
- 让 breakout 因 edit mismatch / timeout 在同一 rerun 上反复重试：继续压住。
- 在 07:00 UTC 临近时继续把 `Next 3` 写成远期 fallback 队列：当前不够贴时钟。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / on-clock waiting next refresh`**
- **Live Seat：`support_breakout_v0`**
- **Live Seat verdict：`keep but narrower-scope`**
- **Scout Seat：继续找更短周期、更贴 crypto 的 breakout / confirmation challenger；当前没有新的 shortlist，头部候选仍是 `Rank 2 combo_all`，但这轮不该抢走 close 后第一轮 paper 资源。**

## 接下来优先级 Top 1~3

1. **A 股 close 前：先打 breakout 那唯一的一枪**
   - 给 `support_breakout_v0` 一次 honest heavy rerun / hard verdict sync；
   - 若 blocker 仍不下降，下轮优先写 `bench review`。

2. **若 close 前还有 fallback 一轮：继续 tiny-live execution chain，而不是重写 Scout**
   - 优先 `parity_red action / sample-row` 或同链紧邻执行卡；
   - 不要重复 same-sample scout verdict。

3. **07:00 UTC 后第一轮：默认优先执行 EMA guarded refresh / append**
   - 若数据源到点仍未给出新 completed bar，就运行 guard/precheck 并如实记录 on-clock waiting；
   - 不得伪造 refresh。

## 本轮改动

### 已改
- 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
  - 把当前窗口从“远期 fallback”改成“close 前打一枪 Live，close 后第一轮回 Paper”；
  - 明确写死：`07:00 UTC` 后的第一轮 bot3 run 默认优先 `EMA paper ledger guarded refresh / append`。

### 这轮不改
- 不改 `Paper Seat` 归属
- 不改 `Paper Seat = running paper pilot`
- 不改 `Live Seat` 归属
- 不改 `Live Seat = keep but narrower-scope`
- 不改 cron 频率

## 风险与不确定性

1. breakout 那一枪还没有成功落地，所以当前还不能直接把它改成 `bench`；但机会也不该继续无限延期。
2. `EMA` 到点后若数据源有延迟，第一轮 post-close 可能仍只能先跑 guard/precheck；但这仍比继续做远期 fallback 更贴当前 desk 节奏。
3. bot3 当前错误更多像执行层问题（edit mismatch / timeout），不是研究方向本身，因此排班应更短、更硬、更少近义重试。

## 本轮一句话结论（给 Jerry）

**这轮 desk 不换席，但我把排班切到更贴 07:00 close 的节奏：EMA 继续是 running paper pilot；breakout 继续是 `keep but narrower-scope`，但 close 前只再给 1 次 honest rerun；而 close 后第一轮 bot3 默认就该回到 EMA ledger append，而不是继续在 Scout / tiny-live 上兜圈。**
