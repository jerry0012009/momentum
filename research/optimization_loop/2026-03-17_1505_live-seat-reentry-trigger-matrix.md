# 2026-03-17 15:05 UTC · Live Seat re-entry trigger matrix

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / reconciliation`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Run 2 / Scout Fast Lane` 已在上一轮如实压成 `repo_fastlane_temporarily_exhausted`
  - `Rank 2` 的相邻 tiny-live 文档链已被 `next status-changing gate` 明确止损，再继续补同类 packet / starter rows 不再减少真实 blocker

## 为什么这次选这个
这轮不再围着单一候选磨近义 closeout copy，而是把 **“什么条件才允许重新占据 Live Seat”** 压成统一的 desk-level trigger matrix。

更直白地说：
- 当前 `Live Seat` 明确默认空席；
- `Rank 2` 真正会改状态的只剩一次真实 whitelist-bound replay；
- `Rank 17 / Rank 29` 的 open paper positions / continuity 运行状态，不等于 tiny-live review trigger。

把这条边界公开写成 artifact，比继续补一张 `Rank 2` 相邻模板更符合本轮 `Run 3` 的边际价值。

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_live_seat_reentry_trigger_matrix_v1.csv`，把 `Live Seat / Rank 2 / Rank 17 / Rank 29` 的唯一 status-changing 事件、最小证据包、以及下一步只允许到哪一层，统一写成 trigger matrix。
- **紧邻子点**：把同一条结论同步到 `alpha_closure_board` reader-facing 页面，避免后续把 `P3` 身份、open paper positions 或 narrow-paper continuity 误读成 auto-reentry。

## 做了什么改动
### 1) 修改 builder
文件：`scripts/build_alpha_closure_board_report.py`

新增导出：
- `reports/artifacts/alpha_closure_board/small_live_live_seat_reentry_trigger_matrix_v1.csv`

矩阵里固定写清：
1. `Live Seat / default`
   - 只有 `bot2` 明确点名新的 promoted candidate，才允许从空席改成 review 中；
2. `Rank 2 / combo_all`
   - 只有同一条 whitelist-bound `test/no-fill` replay 留下真实 `intent + ack + cancel(close)` refs，才算 status change；
   - 即便成功，下一步也仍只是 `eligible_for_shadow_parity_review_only`；
3. `Rank 17 / pullback recovery（ETH+SOL only）`
   - 只有 `manual runner` 真新增 `closed trade append / weekly-review row`，且 `bot2` 明确把它从 `P3` 升到 `P4 review`，才配进入 tiny-live review candidate；
4. `Rank 29 / trendline breakout navigator`
   - 只有 `manual runner` 真新增 `closed trade append / weekly-review row`，并且 `middle-bucket red-watch` 不再恶化，再由 `bot2` 明确升到 `P4 review`，才配进入 tiny-live review candidate。

### 2) reader-facing 页面同步
重建：
- `reports/site/factors/alpha_closure_board/report.html`

新增区块：
- `Live Seat re-entry trigger matrix（v1）`

页面上公开写死的 hard verdict：
- 当前 `Live Seat` 没有任何 auto-reentry 通道；
- 没有 `bot2` 明确 promotion，就默认继续空席；
- `Rank 2` 没有真实 replay refs，就不该再把相邻 packet / wording 当进展；
- `Rank 17 / Rank 29` 的 open positions / continuity 不是 tiny-live review trigger。

## 验证 / 证据
已运行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_live_seat_reentry_trigger_matrix_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

结果：
- builder 成功退出（code 0）；
- 新 CSV 已生成，逐行写出 `status_change_event / minimum_evidence_bundle / next_allowed_stage / why_not_now`；
- 页面已出现 `Live Seat re-entry trigger matrix（v1）` 区块。

## 当前 hard verdict
**当前 `Live Seat` 仍应保持 `empty_by_default`，并且没有任何 auto-reentry 通道。**

更准确地说：
- `Rank 2` 没有真实 whitelist-bound replay refs，就仍停在 `paper_candidate_only / blocked`；
- `Rank 17 / Rank 29` 当前只是 `P3 continuity / monitoring`，不是 `P4 tiny-live review candidate`；
- 因此后续如果继续认领 tiny-live 侧，默认必须围绕“真实 status-changing 事件”推进，而不是继续补近义文档。

## 风险 / 边界
- 这轮没有新开 Scout intake，也没有推进新的 clean replication；它解决的是 **Live Seat re-entry 边界** 的部署歧义；
- 这不是任何真实 venue execution，也不是 live 放行；
- 这轮刻意没有去改 `docs/TODO.md` 顶板：当前 repo 里 `TODO.md` 已有共享脏改，且本轮 hard verdict 已通过网页可见 artifact 充分外显，避免为了一条 override 文案再扩大共享写入面。

## 下一步建议
1. 若出现新的 `paper / repo based 5m / 15m crypto` 合格 fresh intake，优先把主资源切回 `Scout Seat`；
2. 若没有新 intake，而 operator 真拿到 `Rank 2` 的 whitelist-bound replay receipt refs，再回到 `Rank 2`；
3. `Rank 17 / Rank 29` 只有在 `manual runner` 真新增 `closed trade append / weekly-review row` 且 `bot2` 明确升格时，才值得重新占用 Live Seat 讨论槽位。

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提。
