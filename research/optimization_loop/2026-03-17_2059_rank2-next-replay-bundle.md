# 2026-03-17 20:59 UTC · Rank 2 next replay bundle

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / Rank 2 next replay bundle`
- 触发原因：
  - 已先读 `docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper Seat / EMA` 当前已由 guarded refresh 脚本再次确认是 `waiting_not_due`
  - `Scout Seat` 顶板已明确进入本地 fast-lane `exhaustion state`
  - `Rank 2 / Rank 17 / Rank 29` 的 `P3 continuity` 日预算不该继续消耗在近义接线
  - 因此本轮继续诚实落到 `Run 3 / tiny-live plumbing`

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 最近 runs：
  - `19:53 UTC`：`tiny-live state resync`
  - `20:17 UTC`：`ema due window resync`
  - `20:36 UTC`：`rank2 replay order honesty sync`
  - `20:46 UTC`：`rank2 receipt audit rounding sync`
- 当前 seat 读法：
  - `Paper Seat`：`EMA = running paper / waiting_not_due`
  - `Live Seat`：默认空席
  - `Scout Seat`：当前没有新的合格 `paper / repo based 5m / 15m crypto` intake，且顶板已写回 exhaustion

## active 路径边际价值比较
### Run 1 / EMA
- 实际执行了：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：脚本明确返回“当前没有 due-now / overdue lane”，最靠前的是 `Crypto 1d+1wk`，约 `3.1h` 后才到点
- 继续认领只会落回 waiting-window 空转

### Run 2 / Scout Seat
- `docs/TODO.md` 顶板 authoritative override 已明确写回：当前本地 `paper / repo based 5m / 15m crypto` fast lane 已暂时 exhaustion
- 本轮没有 bot2 点名新的 promoted candidate，也没有新的合格 source

### Run 3 / tiny-live plumbing
- 当前最值钱的一步，不是继续扩 Rank 2 的 packet / starter / wording 链，而是把**当前唯一允许的 status-changing 动作**压成单行 operator bundle
- 前几轮已经分别写出了：
  - `replay order`
  - `receipt audit`
  - `replay closeout`
  - `shadow parity launch packet`
- 但 reader-facing / operator-facing 仍需要在多张表之间自己拼出“所以现在到底先做哪一腿、样例金额怎么读、必须抓哪三段 refs、成功后下一张 ticket 开什么”
- 因此本轮主点应是：**生成 `small_live_rank2_next_replay_bundle_v1.csv`，把 Rank 2 当前唯一最该做的一腿压成一张单行 deployable artifact**

## 本轮主点 + 紧邻子点
- **主点**：在 `scripts/build_alpha_closure_board_report.py` 中新增 `Rank 2 next replay bundle` 生成逻辑
- **紧邻子点**：重建 `alpha_closure_board`，让网页 `report.html` 同步出现该单行执行包

## 本轮做了什么
### 1) 扩展 builder，新增单行 replay bundle artifact
文件：`scripts/build_alpha_closure_board_report.py`

本轮新增：
- 常量：`SMALL_LIVE_RANK2_NEXT_REPLAY_BUNDLE_PATH`
- 函数：
  - `get_rank2_next_replay_bundle_rows()`
  - `write_rank2_next_replay_bundle_csv()`

生成逻辑只复用现有 authoritative 产物，不新发明规则：
- `small_live_rank2_receipt_chain_audit_v1.csv`
- `small_live_rank2_replay_runsheet_v1.csv`
- `small_live_rank2_replay_closeout_matrix_v1.csv`
- `small_live_rank2_shadow_parity_launch_packet_v1.csv`

输出把当前第一优先腿压成一行，直接回答：
- 先做哪条腿
- 为什么先做它
- `25bps` 口径下建议样例金额
- `50U` 当前预算读法
- 当前唯一允许动作
- 必须抓到的 `intent / ack / cancel(close)` refs
- 成功时 closeout / 下一张 parity ticket
- 当前硬阻断

### 2) 重建 reader-facing 页面
执行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

同步刷新：
- `reports/artifacts/alpha_closure_board/small_live_rank2_next_replay_bundle_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

## 当前 hard verdict
**当前如果只允许做 1 次真正会改状态的 Rank 2 replay，最诚实的第一腿就是 `SOL-USD / SOLUSDT`。**

单行 bundle 当前写死的关键读法：
- `bundle_order = P1`
- `research_symbol = SOL-USD`
- `sample_notional_usdt = 40`
- `sample_50u_budget_read = pass_25bps`
- `replay_action = one whitelist-bound test/no-fill replay only; cancel_after_ack; capital stays 0`
- `must_capture_refs = intent->ack->cancel/close receipt chain on test/no-fill for at least one whitelisted symbol`
- `if_pass = dry_run_pass -> eligible_for_shadow_parity_review only`
- `parity_ticket_stub_if_pass = SL-PARITY-paper-rank2-solusdt-next-001-<yyyymmddhhmm>`
- `hard_stop = missing any ref / scope drift / capital > 0 / missing cancel-close`

更直白地说：
- Run 3 现在不缺“再多一张 Rank 2 近义说明页”
- 缺的是**一张可以直接告诉 operator：现在只许先做 SOL 这一腿，而且成功也只推进到 shadow parity，不推进到 tiny-live** 的 authoritative 单行执行包

## reader-facing / deployable 落点
- 新 artifact：`reports/artifacts/alpha_closure_board/small_live_rank2_next_replay_bundle_v1.csv`
- 页面同步：`reports/site/factors/alpha_closure_board/report.html`

## 验证 / 证据
已验证：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py` 成功
- builder 成功退出并重建 `alpha_closure_board/report.html`
- 新 artifact 已生成，且当前首行明确写回：`P1 = SOL-USD / sample_notional_usdt=40 / sample_50u_budget_read=pass_25bps`
- 当前 closeout 仍只允许到 `eligible_for_shadow_parity_review`，没有任何字段把它偷写成 tiny-live ready

## 风险 / 边界
- 本轮没有触发真实 venue replay
- 本轮没有新增 Scout candidate
- 本轮没有重开 `Live Seat`
- 本轮没有把 `Rank 2` 从 `paper_candidate_only / blocked` 偷渡成 `shadow_parity passed`
- 这轮只是把**当前唯一允许动作**压成更不容易误操作的单行 artifact

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
