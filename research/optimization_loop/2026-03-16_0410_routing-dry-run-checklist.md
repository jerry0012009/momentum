# 2026-03-16 04:10 UTC｜routing dry-run checklist：把 Run 3 的 tiny-live 第一刀压成可审计 operator checklist

## 先看当前 desk 状态
- **Repo / worktree**：当前仓库存在大量与本轮无关的已修改/未跟踪文件（docs、reports、artifacts、scripts，以及 workspace 上层目录内容）。本轮只做 selective 改动：
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 由脚本重建出的 `reports/artifacts/alpha_closure_board/*` 与 `reports/site/factors/alpha_closure_board/report.html`
  - `reports/site/plans/momentum_todo.html`
- **最近 runs**：
  - `03:14`：`tiny-live plumbing board v1`
  - `03:23`：`Scout Seat shortlist card`
  - `03:36`：`small_live_ledger_template_v1`
  - `03:55`：`τ-band 15m crypto first verdict`
- **Paper Seat / Run 1**：`ema_paper_trading_due_guardrail_snapshot.csv` 仍显示 A 股 `waiting_not_due`，下一次 close 约在 `2026-03-16 07:00 UTC`，当前不能伪造 refresh。
- **Live Seat / Run 2**：`avoid_fluctuating_revisit_guard_20bps.csv` 仍是 `cache_advanced_but_recent_recheck_cooldown_hold`，最近 heavy recheck 距今约 `3.6h`，仍处于 `6h` cooldown 内，不应重复 rerun。
- 因此本轮按 `TRADING DESK BOARD` 自动切到 **Run 3**，且只认领一个主点：`small_live_plumbing_v1` 后续的 **routing dry-run checklist**。

## 本轮主点（Run 3）
把“先做一次 routing dry-run 再说”从抽象提醒压成真正可审计的 checklist：
- 新增 artifact：`reports/artifacts/alpha_closure_board/small_live_routing_dry_run_checklist_v1.csv`
- 同步页面：`reports/site/factors/alpha_closure_board/report.html`
- 同步计划镜像：`docs/TODO.md` + `reports/site/plans/momentum_todo.html`

## 这轮具体做了什么
1. 在 `scripts/build_alpha_closure_board_report.py` 中新增 `small_live_routing_dry_run_checklist_v1.csv` 的生成逻辑。
2. 把 checklist 收成 6 个 operator 步骤：
   - 白名单候选冻结
   - `venue symbol / precision` 映射快照
   - `intent -> ack -> cancel/close` 回执链
   - 时钟 / bar 对齐审计
   - 数量舍入 / 资金占用预检
   - 同账本留痕 + 红旗动作
3. 在 `alpha_closure_board` 新增 reader-facing 区块 `Routing dry-run checklist（v1）`，明确这不是 tiny-live 放行，而是 future small-live 最前面那一刀的执行清单。
4. 在 `docs/TODO.md` 的“项目级 / paper -> 小资金实盘”条目下追加 `2026-03-16 04:10 UTC` 最新补充，避免结果只留日志。

## 为什么这轮算有效推进
- 它没有假装 `EMA` 已到 paper refresh 时点，也没有把 breakout 的 cooldown 硬说成 fresh rerun 机会。
- 它也没有再重复写一张抽象 `live rules` 说明页，而是把 **Run 3 当前最贴 execution 的子点** 压成 artifact。
- 相比上一轮的 `small_live_plumbing_v1` 与 `small_live_ledger_template_v1`，这次多出来的是：
  - 不只是“要记哪些字段”；
  - 而是 **routing dry-run 真开始时，先按什么顺序审计 candidate / symbol / receipt / clock / qty / cap**。
- 这样 future run 如果真进入 routing dry-run，就不需要再靠口头记忆拼步骤，也更不容易在 `symbol mapping / precision / receipt chain` 这些基础环节 silently 出错。

## 最小验证
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`
4. `sed -n '1,12p' reports/artifacts/alpha_closure_board/small_live_routing_dry_run_checklist_v1.csv`
5. `grep -n "Routing dry-run checklist（v1）\|small_live_routing_dry_run_checklist_v1.csv" reports/site/factors/alpha_closure_board/report.html`
6. `grep -n "2026-03-16 04:10 UTC\|small_live_routing_dry_run_checklist_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html`

## 本轮 hard verdict
- **Run 1 / Paper Seat**：真实 market-close 仍未到，继续 blocked。
- **Run 2 / Live Seat**：rerun cooldown 仍未走完，继续 blocked。
- **Run 3 / tiny-live plumbing**：这轮可以推进，而且应优先做 execution checklist，而不是再扩抽象说明页。
- 因此当前最诚实结论是：
  - `EMA` 继续等真实 close；
  - breakout 继续等 cooldown 后、且 cache 仍领先时再做下一次 rerun；
  - Run 3 现已从 `plumbing board + live ledger template` 继续推进到 `routing dry-run checklist v1`。

## 交付物
- `reports/artifacts/alpha_closure_board/small_live_routing_dry_run_checklist_v1.csv`
- `reports/site/factors/alpha_closure_board/report.html`
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

## 下一步最自然的紧邻子点
- 若 Run 1 / Run 2 仍 blocked，`Run 3` 下一刀优先补：
  - `paper-live shadow parity checklist`，把 `paper_ref / live_shadow_ref / cost_estimate / parity_red` 也压成同等级 operator artifact；
  - 但不要重复回头再写近义 tiny-live 规则页。

## Git / 提交
- **未提交 git。** 原因：当前工作区仍有大量与本轮无关的脏文件与未跟踪文件，不适合混提；本轮保持 selective 改动，只刷新必须的 artifact / 页面 / 计划镜像。
