# 2026-03-16 03:36 UTC｜tiny-live live ledger template：把 Run 3 的 live-ledger 子点压成可审计 schema

## 为什么这次选这个
- 先按要求检查了 repo 状态、`docs/TODO.md` 顶部 `TRADING DESK BOARD`、最近几轮 optimization logs、当前脏文件与当前席位状态。
- **Run 1 / Paper Seat（EMA）**：`ema_paper_trading_due_guardrail_snapshot.csv` 仍显示 A 股日频 lane 处于 `waiting_not_due`，当前不能伪造新的 market-close refresh。
- **Run 2 / Live Seat（breakout）**：`avoid_fluctuating_revisit_guard_20bps.csv` 仍是 `cache_advanced_but_recent_recheck_cooldown_hold`；最近一次 heavy recheck 距今太近，当前继续同类 rerun 只会撞 cooldown。
- 因此这轮按板子自动切到 **Run 3**，并且只认领 `small_live_plumbing_v1` 里的一个主点：**live ledger**。目标不是再写一张泛泛 live 规则页，而是把 future `dry-run / shadow parity / tiny-live / rollback` 都要复用的最小账本字段写死。

## 本轮主点
- 主点：`tiny-live plumbing` 的 **live-ledger template v1**
- 紧邻子点：把它同步挂到 `alpha_closure_board` 与 `TODO/plans` 镜像，避免只留在脚本或口头规则里。

## 做了什么改动
1. 修改 `scripts/build_alpha_closure_board_report.py`
   - 新增 artifact：
     - `reports/artifacts/alpha_closure_board/small_live_ledger_template_v1.csv`
   - 新增网页区块：
     - `Tiny-live live-ledger template（v1）`

2. 这轮把 tiny-live 的最小账本 schema 固定成 12 个 operator 字段组，核心包括：
   - `candidate_id / deployment_scope`
   - `stage_status`
   - `paper_ref_id / signal_bar_utc`
   - `research_symbol / venue_symbol / side`
   - `route_intent_ts_utc / route_ack_ts_utc / ack_latency_ms`
   - `intended_notional_usd / cap_pct_total / cap_pct_sleeve / remaining_cap_pct`
   - `intended_qty / rounded_qty / min_notional_check`
   - `shadow_price / fill_price / fill_qty`
   - `cost_estimate_bps / slippage_bps`
   - `mismatch_status / mismatch_reason`
   - `operator_action / live_order_id`
   - `trigger_reason / reopen_earliest_ts / operator_note`

3. 更新 `docs/TODO.md`
   - 在项目级 `paper trading -> 小资金实盘` promotion gate 条目下新增 `2026-03-16 03:36 UTC` 最新补充，明确这轮交付的是 `live ledger` 子点，而不是把任何候选偷偷升级成可直接 live。

4. 重建网页可见面
   - `python3 scripts/build_alpha_closure_board_report.py`
   - `python3 scripts/build_plans_site.py`

## 硬判断 / 这轮真正新增的 desk call
- **Run 3 现在不只是一张 tiny-live plumbing board。**
- 当前又多了一张可直接复用的 **live-ledger template**，它把 `crypto live mismatch` 从抽象风险继续压成了同一张账本上的可审计字段与阻断条件。
- 这不代表任何候选已经 live-approved；它只代表：
  - 未来如果先做 `routing dry-run`，必须落 `route_ack / ack_latency / venue_symbol`；
  - 如果先做 `paper-live shadow parity`，必须落 `paper_ref_id / intended vs rounded qty / mismatch_status`；
  - 如果未来真的进入 `tiny-live`，必须能回填 `fill_price / slippage_bps / remaining_cap / live_order_id`；
  - 若触发 kill switch，不能只口头说 rollback，必须落 `trigger_reason / reopen_earliest_ts / operator_note`。

## 验证 / 证据
- `python3 -m py_compile scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`
- `grep -n "small_live_ledger_template_v1.csv\|Tiny-live live-ledger template\|2026-03-16 03:36 UTC" reports/site/factors/alpha_closure_board/report.html reports/site/plans/momentum_todo.html docs/TODO.md`
- 额外核对：
  - `reports/artifacts/alpha_closure_board/small_live_ledger_template_v1.csv` 已生成；
  - `reports/site/factors/alpha_closure_board/report.html` 已出现新 template 区块；
  - `reports/site/plans/momentum_todo.html` 已同步新的 `TODO` 补充。

## 风险 / 边界
- 这轮新增的是 **账本 schema / operator artifact**，不是新的 alpha 证据，也不是任何 live 放行。
- 它不会替代 breakout 的 `one_more_gate`，也不会替代 EMA 仍在等待真实 completed bar 的事实。
- 它的价值是：当 future run 真进入 `dry-run / shadow / tiny-live` 检查时，不再临时拼字段，也不再把 `crypto live mismatch` 停留在口头提醒层。

## git / hygiene
- 当前 worktree 仍有大量与本轮无关的既有脏改 / 未跟踪文件。
- 本轮只安全补了：
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - `reports/artifacts/alpha_closure_board/small_live_ledger_template_v1.csv`
  - `reports/site/factors/alpha_closure_board/report.html`
  - `reports/site/plans/momentum_todo.html`
- **未提交 git。** 原因：当前工作区远不干净，不适合把本轮与历史脏改混提。

## Commit hash
- HEAD：`4edc095`
- 本轮未提交。

## 下一刀默认
1. 若 `EMA` 进入真实 `due-now / overdue`，优先立即切回 Paper Seat，沿同一张 ledger 继续真实 refresh / review。
2. 若 breakout cooldown 结束且 cache 仍领先，再回 Live Seat 做一次 cooldown-aware rerun 检查；否则别重复撞同类重跑。
3. 若 Run 3 继续触发，默认可从这次新模板继续往前压一小步：优先 `routing dry-run` 或 `paper-live shadow parity` 的最小检查清单，而不是再回到抽象 live 规则页。
