# 2026-03-17 16:25 UTC · small-live now-action queue

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / now-action queue`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Scout Seat` 当前本地 `paper / repo based 5m / 15m crypto` fast lane 继续处于 `temporarily exhausted`
  - 上几轮 tiny-live 侧已经补了 `watchboard / trigger snapshot / dynamic snapshot`，但还缺一张**直接告诉后续轮次“现在谁该等、谁该由谁接、下一步唯一允许动作是什么”**的动态操作队列

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前 seat 读法：
  - `Paper Seat / EMA`：`waiting_not_due`
  - `Scout Seat`：当前没有新的合格本地 fast-lane 候选可诚实认领
  - `Live Seat`：默认仍空席；没有 bot2 promotion 不能自动重开

## active 路径边际价值比较
### Run 1 / EMA
- 当前没有 `due-now / overdue` refresh；继续做 paper continuity 会落回 waiting-window 空转

### Run 2 / Scout Seat
- 顶板已明确本地 fast-intake shortlist 基本耗尽；继续磨已 park 候选或 external-data probe 的边际价值低于把 tiny-live 当前唯一允许动作写成明确队列

### Run 3 / tiny-live plumbing
- `watchboard` 解决的是“去哪里看”
- `trigger snapshot` 解决的是“有没有新事件”
- 但后续轮次仍可能卡在：**知道没 trigger / 有 continuity 事件，却不知道“现在唯一允许动作是什么”**
- 因此这轮主点应是：**把 tiny-live 当前 now-action 压成动态队列，而不是继续补同义 snapshot / wording**

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_now_action_queue_v1.csv`
- **紧邻子点**：把同一结论挂到 `alpha_closure_board` 页面，形成 reader-facing 外显落点

## 本轮做了什么
### 1) 修改 builder
文件：`scripts/build_alpha_closure_board_report.py`

新增导出：
- `reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv`

实现口径：
- 复用现有 `small_live_status_trigger_snapshot` + `small_live_status_change_watchboard` 结论
- 不再只写“有没有触发”，而是统一压成：
  - `seat_or_candidate`
  - `trigger_state_now`
  - `action_owner_now`
  - `next_allowed_action_now`
  - `still_waiting_for`
  - `hard_stop`
  - `why_this_is_the_honest_next_step`

当前动态队列的硬读法：
1. `Live Seat / default`
   - 现在唯一允许动作：继续空席，只等 `bot2` 明确 promotion note
2. `Rank 2 / combo_all`
   - 现在唯一允许动作：只做 **1 次** whitelist-bound `test/no-fill` replay，并回填 `intent + ack + cancel(close)` 真实 refs
   - 没有这三段真实 refs，仍不得跳去 `shadow parity`
3. `Rank 17 / pullback recovery（ETH+SOL only）`
   - 当前只配 `monitoring / continuity`
   - 没有新的 append/review 行 + bot2 promotion，就不得推进到 `P4 / tiny-live review`
4. `Rank 29 / trendline breakout navigator`
   - 当前同样只配 `monitoring / continuity`
   - 没有新的 append/review 行 + bot2 promotion，就不得推进到 `P4 / tiny-live review`

### 2) reader-facing 页面同步
重建：
- `reports/site/factors/alpha_closure_board/report.html`

新增区块：
- `Tiny-live now-action queue（v1）`

页面公开口径：
- 当前 tiny-live 侧最多只配三类动作：
  - 保持 `Live Seat` 空席
  - 催成 `Rank 2` 的唯一一次真实 receipt-chain replay
  - 把 `Rank 17 / Rank 29` 的事件严格限制在 `P3 review / continuity`
- 除此之外继续补 tiny-live 同义文档，当前都不算真实进展

## 为什么这轮比继续补同义 snapshot 更值钱
- 它不再只回答“有没有变化”，而是直接给出：
  - **现在谁负责**
  - **现在唯一允许动作是什么**
  - **还缺什么证据**
  - **什么是硬阻断**
- 这让后续轮次可以直接按一张表行动，而不是再读多张 tiny-live 文档后自行拼接结论

## 验证 / 证据
已运行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

结果：
- builder 成功退出（code 0）
- 新 CSV 已生成，逐条写出 `owner / next_allowed_action_now / still_waiting_for / hard_stop`
- 页面已出现 `Tiny-live now-action queue（v1）` 区块

## 当前 hard verdict
**当前 tiny-live 侧默认不该继续围绕“是不是快够了”打转；更诚实的动作是按 now-action queue 执行：Live Seat 继续空席、Rank 2 只等那唯一一次真实 replay、Rank 17 / 29 只按 P3 continuity 处理。**

## 风险 / 边界
- 本轮没有引入新的 Scout candidate，也没有推进真实 venue execution
- 本轮没有改变任何 seat verdict
- 本轮没有去改 `docs/TODO.md` 顶板，避免在共享脏文件上扩大写入面

## 交付物
### deployable / reader-facing artifact
- `reports/artifacts/alpha_closure_board/small_live_now_action_queue_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

### 同步文件
- `scripts/build_alpha_closure_board_report.py`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
