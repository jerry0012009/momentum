# 2026-03-16 10:17 UTC｜small-live review writeback matrix：把 review ticket 的 closeout 写回链固定成可审计矩阵

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat（EMA）**：`ema_paper_trading_due_guardrail_snapshot.csv` 仍是 `waiting_not_due`，当前无 `due-now / overdue`。
- **Run 2 / Scout Seat**：先核对共享 Binance `15m` cache，`BTCUSDT / ETHUSDT / SOLUSDT` 最新 completed bar 均仍在 `2026-03-16 09:45 UTC`，没有 genuinely new local bar，不能诚实做 continuity。
- 于是按规则回退到 **Run 3 / tiny-live plumbing**。

本轮只认领：
- **主点**：新增 `small_live review writeback matrix v1`（deployable artifact）
- **紧邻子点**：把该卡同步到 `alpha_closure_board` 页面与 `TODO/plans` reader-facing 落点

## 本轮产物
### 1) 新增 artifact
- `reports/artifacts/alpha_closure_board/small_live_review_writeback_matrix_v1.csv`

矩阵覆盖 5 类 closeout：
1. `dry_run_pass -> eligible_for_shadow_parity_review`
2. `shadow parity green -> continue_shadow_review`
3. `shadow parity red -> freeze_review_with_reopen_gate`
4. `freeze review 完成 -> reopen_ready`
5. `resume green -> resume_shadow_review`

每一类都写死：
- 最小 writeback 字段集合（ticket_id、row ref、reason、时点等）
- 必须留在同一条 review registry / ledger 的状态切换
- 下一步队列去向
- 何种缺失下不能“口头过关”

### 2) 同步代码与页面
- 修改：`scripts/build_alpha_closure_board_report.py`
  - 新增生成函数：`get_small_live_review_writeback_matrix_rows()`
  - 新增导出函数：`write_small_live_review_writeback_matrix_csv()`
  - 在 `main()` 中纳入该 artifact 写出
  - 在 `report.html` 模板中新增卡片：`Small-live review writeback matrix（v1）`
- 同步：`docs/TODO.md` 顶部 `TRADING DESK BOARD`（10:17 UTC 补充）
- 同步站点：
  - `reports/site/factors/alpha_closure_board/report.html`
  - `reports/site/plans/momentum_todo.html`
  - 首页发布：`https://jp.jerrypsy.top/momentum/`

## 最小验证
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py` ✅
2. `python3 scripts/build_alpha_closure_board_report.py` ✅
3. `python3 scripts/build_plans_site.py` ✅
4. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` ✅
5. `head -n 6 reports/artifacts/alpha_closure_board/small_live_review_writeback_matrix_v1.csv` ✅
6. `grep -n "10:17 UTC|small_live_review_writeback_matrix_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html` ✅
7. `grep -n "Small-live review writeback matrix|small_live_review_writeback_matrix_v1.csv" reports/site/factors/alpha_closure_board/report.html` ✅

## 本轮 hard verdict
一句话：

**当前 EMA 在 waiting_not_due + Scout 无新 completed 15m bar，Run 2 不可做；本轮合规回退到 Run 3，并把 tiny-live 的 review closeout 从“模板描述”推进到“可审计 writeback 矩阵”。**

## 风险与边界
- 本轮不是 live 放行，也不是新 alpha；仅补执行链可审计性。
- 未重跑 breakout heavy analysis（继续遵守 `bench / recheck-only`）。
- 未做与本轮无关的大范围重下载。

## 下一步建议
- 若下轮 Scout 仍无 genuinely new local bar，继续沿 `closeout / registry / writeback` 紧邻缺口补齐。
- 一旦出现新 completed 15m bar，优先回到 `Run 2` 做 honest continuity。

## Commit
- HEAD：`573439c`
- 本轮未提交（worktree 存在大量无关脏文件，避免混提）。
