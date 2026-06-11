# 2026-03-17 13:40 UTC · Rank 2 shadow-parity launch packet

## 本轮归属
- Desk lane：`Run 3 / tiny-live plumbing / reconciliation / parity / dry-run`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`
  - `Run 2 / Scout Fast Lane` 仍没有更高边际价值的本地 `paper / repo based 5m / 15m crypto` 新动作：`Rank 35` 已 park，`Rank 30 / 31 / 32 / 33 / 34` 也都已完成当前允许动作并 park，`Rank 5 / Rank 6` 仍偏外部数据依赖
  - `Live Seat` 上一轮已明确写成 `empty_by_default`，`Rank 17 / 29` 也都不自动回 tiny-live review
  - 因此这轮最诚实的剩余 Run 3 动作，是把 **`Rank 2` 一旦拿到那唯一允许的 whitelist-bound replay 后，下一步仍只允许怎么进入 `shadow_parity`** 压成 deployable artifact，而不是继续补近义 closeout 文案

## 开始前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件，因此本轮只做 selective 写入，不混提
- 当前席位状态：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = 当前本地 fast-intake 无更高边际价值的便宜 fresh candidate`
- 本轮复核的现有 plumbing 证据：
  - `reports/artifacts/alpha_closure_board/small_live_rank2_status_snapshot_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_operator_packet_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_rank2_receipt_chain_completion_gate_v1.csv`
  - `reports/artifacts/alpha_closure_board/small_live_review_ticket_template_v1.csv`

## active Scout / plumbing 边际价值比较
- `Rank 17 / Rank 29`：仍是 `P3 narrow paper` continuity / monitoring，不构成当前 tiny-live review need
- `Rank 2`：仍是唯一更贴近执行的关闭链，但真实 blocker 已收敛到 **一次 whitelist-bound replay 成功后，下一张 `shadow_parity` 卡该如何开**
- 结论：这轮最值钱的动作不是再新增一张 generic checklist，而是把 `Rank 2` 从 `dry_run_pass -> eligible_for_shadow_parity_review` 这半步压成可直接照抄的启动包

## 本轮主点 + 紧邻子点
- **主点**：给 `alpha_closure_board` 新增 `small_live_rank2_shadow_parity_launch_packet_v1`，把 `Rank 2` 一旦完成唯一允许的 whitelist-bound replay 后，下一步如何打开第一张 `shadow_parity` review ticket、绑定 `paper_ref / live_shadow_ref`、以及第一条 green parity row 至少要写回哪些字段，写成 deployable packet
- **紧邻子点**：把同一条边界最小写回 `docs/TODO.md` 顶部 `Next 3 bot3 runs` authoritative override，明确即使 replay 成功，也仍只允许进入 `shadow_parity`，并沿 `ETH -> SOL -> BTC` 作为默认启动顺序

## 本轮做了什么
### 1) 扩 `alpha_closure_board` builder，新增 Rank 2 shadow-parity launch packet
修改：`scripts/build_alpha_closure_board_report.py`

新增导出：
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv`

表内固定写清：
- `dry_run_pass_trigger = eligible_for_shadow_parity_review only; still not tiny-live`
- `shadow_review_ticket_stub = SL-PARITY-paper-rank2-<symbol>-next-001-<yyyymmddhhmm>`
- 第一条 `shadow parity` 行最小 writeback：`paper_ref_id + live_shadow_ref_id + rounded_qty + cost_estimate_bps + mismatch_status=green`
- 只要缺 `paper_ref / qty rounding / cost snapshot / whitelist / clock` 任一，仍继续 `blocked`

同时把默认启动顺序固定成：
- `P1 = ETH`
- `P2 = SOL`
- `P3 = BTC`

### 2) reader-facing 页面同步新增 `Rank 2 shadow-parity launch packet`
重建：
- `reports/site/factors/alpha_closure_board/report.html`

页面新增：
- `Rank 2 shadow-parity launch packet（v1）` 区块
- 明确写出：前一张 closeout matrix 只负责 `dry-run replay` 如何关单；这张新 packet 专门负责 **green closeout 后，第一张 shadow parity ticket 该怎么开**
- summary 继续钉死：即使 replay 成功，下一步也仍然只是 `shadow_parity`，不是 tiny-live ready

### 3) 指挥板最小写回
更新：`docs/TODO.md` 顶部 `Next 3 bot3 runs` authoritative override

补回的关键信息：
- `alpha_closure_board` 已新增 `small_live_rank2_shadow_parity_launch_packet_v1`
- `Rank 2` 即便完成唯一允许的 whitelist-bound replay，下一步也仍只允许进入 `shadow_parity`
- 默认启动顺序仍是 `ETH -> SOL -> BTC`

## 核心 hard verdict
**`Rank 2` 当前仍不是 tiny-live ready；即使那唯一允许的 whitelist-bound replay 成功，下一步也只是 `shadow_parity`，而不是 live 放行。**

更直白地说：
- `dry_run_pass` 不是 live 资格，只是第一次拿到 `eligible_for_shadow_parity_review`
- 真正进入 `shadow_parity` 时，必须把 `paper_ref / live_shadow_ref / rounded_qty / cost_estimate_bps / mismatch_status` 一次写回
- 只要 `paper_ref`、`qty rounding`、`cost snapshot`、`whitelist`、`clock alignment` 任一缺失，就继续 blocked，不允许偷写成 tiny-live ready

## 交付物
### deployable / plumbing artifacts
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`

### 相关同步
- `docs/TODO.md`
- `scripts/build_alpha_closure_board_report.py`

## 最小验证
已运行：
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`

已抽查：
- `reports/artifacts/alpha_closure_board/small_live_rank2_shadow_parity_launch_packet_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md` 顶部 `Next 3 bot3 runs`

结果：
- builder 成功退出（code 0）
- 新 CSV 已生成，且三条腿都明确写成 `dry_run_pass -> eligible_for_shadow_parity_review only`
- 页面已出现 `Rank 2 shadow-parity launch packet（v1）` 区块
- 指挥板已写回这条新的 Run 3 plumbing 落点

## 风险 / 边界
- 这轮没有新开 fresh intake，也没有推进新的 clean replication；它继续解决的是 **当前 tiny-live / shadow parity 交界处的部署歧义**
- 这不是任何真实 venue execution，也不是 replay 已完成；它只是把 replay 成功后的下一步启动包写清
- 若后续还没有更高边际价值的 fresh intake，这条线也不应无限补近义文档；真正会改变状态的，仍然是那次真实 whitelist-bound replay

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
