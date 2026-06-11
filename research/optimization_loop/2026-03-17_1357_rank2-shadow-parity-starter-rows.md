# 2026-03-17 13:57 UTC · Rank 2 shadow-parity starter rows

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / reconciliation / parity / dry-run`
- 触发原因：
  - `Paper Seat / EMA` 已再次实跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，当前仍是 `waiting_not_due`，没有新的 `due-now / overdue` lane
  - 当前 `Next 3 bot3 runs` 已明确：若 `EMA` 等待窗口继续卡住，就不得空转；若本地 `Scout Seat` 没有更高边际价值的新 intake，则允许先落到 `Run 3`
  - 上两轮已先把 `Live Seat = empty_by_default` 与 `Rank 2 shadow-parity launch packet` 压成 deployable artifact；这轮最贴近执行的一格，不是再补抽象 closeout 文案，而是把 **Rank 2 一旦 replay 过关后第一条 green shadow-parity row 应该怎么落** 写成 starter rows

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件，因此本轮继续只做 selective 写入，不混提
- 当前席位状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = empty_by_default`
  - `Scout Seat = 当前本地 fast-intake 没有比 Run 3 更高边际价值的便宜动作`
- 本轮复核的已存在 artifact：
  - `reports/artifacts/alpha_closure_board/small_live_default_seat_queue_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_green_shadow_parity_sample_row_v1.csv`
  - `reports/site/factors/alpha_closure_board/report.html`

## active Scout / plumbing 边际价值比较
- `Rank 17 / Rank 29`：仍属 `P3 narrow paper` continuity / monitoring，本轮没有新的 append/review need
- `Rank 2`：仍是当前 tiny-live plumbing 里唯一更接近执行的一条线，但上一轮 launch packet 只解决了“第一张 parity ticket 怎么开”，还没把“第一条 green parity row 至少该长什么样”压成具体 starter rows
- 结论：这轮最值钱的动作是继续沿 `Rank 2` 只补 **一个紧邻 launch packet 的最小 deployable artifact**，而不是继续扩 generic handoff / closeout 近义页

## 本轮主点 + 紧邻子点
- **主点**：新增 `small_live_rank2_shadow_parity_starter_rows_v1.csv`，把 `ETH -> SOL -> BTC` 三条腿在 replay green closeout 之后第一条 `shadow_parity green row` 的 starter row 预写出来
- **紧邻子点**：把同一条边界最小写回 `alpha_closure_board` 页面与 `docs/TODO.md` 顶部 `Next 3 bot3 runs` authoritative override，明确后续只应回填真实 `rounded_qty / cost_estimate_bps`，而不是临时拼字段或误写成 tiny-live ready

## 本轮做了什么
### 1) 扩 `alpha_closure_board` builder，新增 Rank 2 shadow-parity starter rows
修改：`scripts/build_alpha_closure_board_report.py`

新增导出：
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_starter_rows_v1.csv`

表内固定写清：
- `launch_priority = ETH -> SOL -> BTC`
- `shadow_review_ticket_stub`
- `paper_ref_id_stub`
- `live_shadow_ref_id_stub`
- `stage_status = shadow_parity`
- `mismatch_status = green_when_first_row_lands`
- `operator_action = continue_shadow_review`
- `minimum_writeback = paper_ref_id + live_shadow_ref_id + rounded_qty + cost_estimate_bps + mismatch_status=green`
- `pending_fields_before_closeout = rounded_qty / cost_estimate_bps`
- 硬边界：只要 `rounded_qty / cost / whitelist / clock` 任一未过关，就不能拿 starter row 冒充 green closeout，必须回到 `parity_red / freeze_review`

### 2) reader-facing 页面同步新增 `Rank 2 shadow-parity starter rows（v1）`
重建：
- `reports/site/factors/alpha_closure_board/report.html`

页面新增：
- `Rank 2 shadow-parity starter rows（v1）` 区块
- summary 明确写出：
  - launch packet 解决“第一张 parity ticket 怎么开”
  - starter rows 解决“开完以后第一条 green parity row 至少该长什么样”
  - 这仍不是 tiny-live 放行；只是把第一条可审计 green row 的字段顺序提前压死

### 3) 指挥板最小写回
更新：`docs/TODO.md` 顶部 `Next 3 bot3 runs` authoritative override

补回的关键信息：
- `small_live_rank2_shadow_parity_starter_rows_v1` 已落地
- 后续若 Rank 2 的 whitelist-bound replay 真过关，默认应先按 starter row 回填真实 `rounded_qty / cost_estimate_bps`
- 不允许 future run 到那一步时再临时拼 `ticket / paper_ref / live_shadow_ref / writeback`，更不允许偷写成 tiny-live ready

## 核心 hard verdict
**`Rank 2` 当前仍不是 tiny-live ready；但一旦那唯一允许的 whitelist-bound replay 过关，第一条 shadow-parity green row 现在已经有可直接照抄的 starter rows。**

更直白地说：
- 上一轮只把“第一张 parity ticket 怎么开”写清楚了
- 这轮把“第一条 parity green row 至少该怎么落”也压成了 artifact
- 现在真正缺的仍不是更多 closeout 文案，而是那次真实 replay 本身，以及之后真实回填 `rounded_qty / cost_estimate_bps`
- 若这些真实字段还没落地，就不能用 starter row 假装自己已经 green / 更不能假装已 tiny-live ready

## 交付物
### deployable / plumbing artifacts
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_starter_rows_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

### 相关同步
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`

## 最小验证
已运行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_starter_rows_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md` 顶部 `Next 3 bot3 runs`

结果：
- builder 成功退出（code 0）
- 新 CSV 已生成，且三条腿都明确写出 `ticket / paper_ref / live_shadow_ref / minimum_writeback`
- 页面已出现 `Rank 2 shadow-parity starter rows（v1）` 区块
- 指挥板已写回这条新的 Run 3 plumbing 落点

## 风险 / 边界
- 这轮没有新开 fresh intake，也没有推进新的 clean replication；它继续解决的是 **Rank 2 从 replay green closeout 到第一条 shadow-parity green row 之间的执行歧义**
- 这不是任何真实 venue execution，也不是 replay 已成功；它只是把 replay 成功后的第一条 green row 提前预写成 starter rows
- 若后续还没有更高边际价值的 Scout 动作，这条线也不应无限补近义文档；真正会改变状态的，仍然是那次真实 whitelist-bound replay 和真实 writeback

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
