# 2026-03-16 15:27 UTC｜Run 3 fallback：Rank 2 paper-candidate -> tiny-live plumbing handoff

## 本轮判定（按 TRADING DESK BOARD）
- 先读了 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- `Run 1 / Paper Seat`：`EMA` 仍是 `waiting_not_due`，本轮无 `due-now / overdue` refresh 动作。
- `Run 2 / Scout`：当前唯一默认前推对象 `Rank 2 combo_all` 刚完成 admission write-back + monitoring board（上一轮已落地），本轮没有新的合格 scout 主动作（Rank4/3/1 仍为 park）。
- 因此按板子顺序进入 `Run 3`：`tiny-live plumbing / reconciliation / parity / dry-run`。

## 本轮认领（严格 1 主点 + 1 紧邻子点）
- **主点**：落一份可部署 `paper->tiny-live` 对接 artifact，明确 Rank 2 进入 plumbing 时的硬边界与阻断动作。
- **紧邻子点**：把该 artifact 同步到 reader-facing 页面，避免只留日志/邮件。

## 交付产物（deployable artifact）
新增：
- `reports/artifacts/alpha_closure_board/small_live_rank2_paper_candidate_handoff_map_v1.csv`

内容聚焦 6 条 handoff gate：
1. scope_lock_sync
2. signal_ledger_key_bridge
3. false_break_watch_bridge
4. idle_gap_watch_bridge
5. time_pocket_review_bridge
6. promotion_boundary_sync

关键硬结论：
- 这张 handoff map 只允许 `Rank 2 combo_all` 进入 `dry_run/shadow_parity` 的 plumbing 级动作；
- 明确禁止把 plumbing 结果误写成 live admission；
- 仍保持 `paper candidate / one_more_light_check`，不抢占 `Live Seat`。

## reader-facing 外显同步
更新脚本：
- `scripts/build_trendline_alpha_scout_report.py`
  - 新增 `Run 3 tiny-live plumbing fallback（Rank 2 handoff map）` 卡片读取上述 CSV。

网页落点：
- `reports/site/reading/trendline_alpha_scout/report.html`
- 已刷新并发布首页：`https://jp.jerrypsy.top/momentum/`

## 最小验证
执行并通过：
1. `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_trendline_alpha_scout_report.py`
3. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
4. `grep` 命中：
   - `Run 3 tiny-live plumbing fallback`
   - `small_live_rank2_paper_candidate_handoff_map_v1.csv`

## repo / 脏文件说明
- `git status` 仍存在大量与本轮无关的历史脏文件与未跟踪文件。
- 本轮只做 selective 产物与页面更新，不做混提提交。

## 本轮结果归类
- `paper / live plumbing artifact`：✅
- `hard verdict`：✅（仍是 paper-candidate narrow scope，不得越级到 live）
- `NO_PROGRESS`：不适用（本轮有实质推进）。
