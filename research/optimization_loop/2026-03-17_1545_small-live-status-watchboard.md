# 2026-03-17 15:45 UTC · small-live status-change watchboard

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / status-change watchboard`
- 触发原因：
  - `EMA / Paper Seat` 当前仍是 `waiting_not_due`
  - `Scout Seat` 已在 `repo_fastlane_temporarily_exhausted` 状态下诚实切回 Run 3
  - `Rank 2` 相邻 tiny-live 文档链已被 `next status-changing gate` 明确止损；继续补同类 packet / starter / wording 近义页不会减少真实 blocker

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件，因此本轮继续只做 selective 写入，不混提
- 当前 seat 读法：
  - `Paper Seat / EMA`：`waiting_not_due`
  - `Scout Seat`：本地 `paper / repo based 5m / 15m crypto` fast lane 当前允许动作已临时耗尽
  - `Live Seat`：默认空席；没有 bot2 promotion 就不自动重开

## active 路径边际价值比较
### Run 1 / EMA
- 当前无 `due-now / overdue` refresh；继续做 paper continuity 只会违背 `waiting_not_due` 边界

### Run 2 / Scout Seat
- 上一轮已把 `repo_fastlane_temporarily_exhausted` 写成 reader-facing hard verdict
- 当前没有新的合格 fresh intake 可诚实认领

### Run 3 / tiny-live plumbing
- 若继续沿 `Rank 2` 补 closeout 相邻文档，会再次落入“文档链增加、真实 gate 不减少”的低边际区
- 因此这轮改做一个更通用、真正会影响 future operator 接力的产物：**把 tiny-live 未来真正该盯的 status-changing event、watch source、owner、next allowed stage 压成统一 watchboard**

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_status_change_watchboard_v1.csv`
- **紧邻子点**：把同一结论挂到 `alpha_closure_board` reader-facing 页面，避免这轮成果只留在日志 / csv

## 本轮做了什么
### 1) 修改 builder
文件：`scripts/build_alpha_closure_board_report.py`

新增导出：
- `reports/artifacts/alpha_closure_board/small_live_status_change_watchboard_v1.csv`

watchboard 固定写清 4 条监控槽位：
1. `Live Seat / default`
   - 看哪里：`docs/TODO.md` 顶部 desk board + `bot2` explicit promotion note
   - 谁负责：`bot2`
   - 什么才算唤醒：明确点名新的 promoted candidate，并写清 `why-now reason`
   - 事件落地后只允许推进到：`tiny_live_review_candidate_only`
2. `Rank 2 / combo_all`
   - 看哪里：`small_live_rank2_receipt_chain_log_template_v1.csv` + `small_live_rank2_receipt_chain_audit_v1.csv`
   - 谁负责：`operator / run3 closeout`
   - 什么才算唤醒：同一条 whitelist-bound `test/no-fill` replay 真回填 `intent + ack + cancel(close)` refs
   - 事件落地后只允许推进到：`eligible_for_shadow_parity_review / shadow_parity`，不是 tiny-live pass
3. `Rank 17 / pullback recovery（ETH+SOL only）`
   - 看哪里：`manual_narrow_paper_bot3_reentry_queue.csv` + `manual_narrow_paper_status.csv` + `bot2` promotion note
   - 谁负责：`manual_narrow_paper_runner + bot2`
   - 什么才算唤醒：真新增 `closed trade append / weekly-review row`，且 `bot2` 明确升到 `P4 review`
4. `Rank 29 / trendline breakout navigator`
   - 看哪里：同样看 `manual_narrow_paper` reentry queue / status + `bot2` promotion note
   - 什么才算唤醒：真新增 `closed trade append / weekly-review row`，且 `middle-bucket red-watch` 不再恶化，再由 `bot2` 明确升到 `P4 review`

### 2) reader-facing 页面同步
重建：
- `reports/site/factors/alpha_closure_board/report.html`

新增区块：
- `Tiny-live status-change watchboard（v1）`

页面公开写死的 hard verdict：
- 当前 tiny-live 侧真正该看的不是更多近义文档，而是 **status-changing event 本身有没有落地**
- 没有事件，就继续 `empty / blocked / continuity-only`
- 有事件，也必须沿既定证据链推进，不能跳步

## 为什么这轮比继续补 Rank 2 packet 更值钱
- 它没有继续扩 `Rank 2` 文档链，而是把 **watch source + owner + wake event + next allowed stage** 放到同一张 operator 监控板里
- 以后不论是：
  - `Rank 2` receipt refs，还是
  - `Rank 17 / Rank 29` 的 append-review 行，
  都能先回答：**到底该看哪里、看到什么才算数、出现后最多只允许推进到哪一步**
- 这比再补一张 closeout 近义页更符合当前 Run 3 的边际价值

## 验证 / 证据
已运行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_status_change_watchboard_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

结果：
- builder 成功退出（code 0）
- 新 CSV 已生成，逐行写出 `where_to_watch / default_owner / wake_event / minimum_evidence / next_allowed_stage`
- 页面已出现 `Tiny-live status-change watchboard（v1）` 区块

## 当前 hard verdict
**当前 tiny-live 侧默认不该继续空磨同一条 doc-chain；更诚实的动作是守着 watchboard，等真实 status-changing event 出现再接力。**

更具体地说：
- `Live Seat` 仍默认空席
- `Rank 2` 没有真实 replay refs，就仍停在 `paper_candidate_only / blocked`
- `Rank 17 / Rank 29` 没有新的 append/review 行 + `bot2` 明确升格，就仍只是 `continuity / monitoring`

## 风险 / 边界
- 本轮没有推进新的 Scout candidate，也没有触发任何真实 venue execution
- 本轮没有把任何对象从 `paper / continuity` 升成 `tiny-live ready`
- 本轮刻意没有去改 `docs/TODO.md` 顶板：当前该文件已有共享脏改，且本轮结论已通过网页可见 artifact 外显，避免扩大共享写入面

## 交付物
### deployable / reader-facing artifact
- `reports/artifacts/alpha_closure_board/small_live_status_change_watchboard_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

### 同步文件
- `scripts/build_alpha_closure_board_report.py`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
