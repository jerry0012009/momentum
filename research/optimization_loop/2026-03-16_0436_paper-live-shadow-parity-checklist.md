# 2026-03-16 04:36 UTC｜paper-live shadow parity checklist：把 Run 3 的同步审计链压成可复用 operator artifact

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前席位与 run 顺序：

- **Repo / worktree**：当前仓库仍有大量与本轮无关的既有脏文件与未跟踪文件；本轮继续只做 selective 改动，避免混提。
- **Run 1 / Paper Seat**：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示 `waiting_not_due`，A 股下一次 close 仍是 `2026-03-16 07:00 UTC`，当前不能伪造 paper refresh。
- **Run 2 / Live Seat**：`reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv` 显示最近 heavy recheck 在 `2026-03-15 23:25 UTC`，当前仍处在 `6h cooldown hold` 内，不应再做同类 heavy rerun。
- **最近 runs**：
  - `04:10`：`small_live_routing_dry_run_checklist_v1`
  - `04:23`：`Scout Rank 2 clean-room spec`
- 因此本轮按 desk board 自动落到 **Run 3**，且只认领一个主点：在 `small_live_plumbing_v1 + routing dry-run checklist v1` 基础上，补出 `paper-live shadow parity checklist`。

## 本轮主点 + 紧邻子点
### 主点
把 `paper vs live-shadow` 的同步审计，从 plumbing board 里的一个抽象子句，压成可直接复用的 checklist artifact：

- 新 artifact：`reports/artifacts/alpha_closure_board/paper_live_shadow_parity_checklist_v1.csv`
- 同步页面：`reports/site/factors/alpha_closure_board/report.html`

本轮冻结的 6 个 parity 步骤：
1. `paper signal 配对冻结`
2. `payload parity 快照`
3. `shadow price + 成本快照`
4. `数量舍入 / 资金占用 parity`
5. `paper vs live-shadow 时钟 / 路径对齐`
6. `同账本留双引用 + 红旗动作`

它们对应的硬红旗也一起写死：
- `paper_ref` 缺失或一对多映射 → 直接停在 parity review；
- `symbol / side / precision / whitelist` 任一不一致 → 直接记 `parity_red`；
- `clock drift > 60s` 或单笔成本偏差 `> 25bps` → 不允许继续往 tiny-live 解释成“小偏差”；
- parity 结果若只留在终端/日志、没有回写同一张 ledger → 视为流程不可审计。

### 紧邻子点（reader-facing 落点）
同步更新了：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `reports/site/factors/alpha_closure_board/report.html`

其中顶部 `Next 3 bot3 runs` 也顺手刷新成 `04:36 UTC` 新窗口：
- 继续明确 `EMA` 仍是 waiting-window；
- 继续明确 breakout 仍在 cooldown；
- 不让下一轮再重复认领已经做完的 `shadow parity checklist` 这一刀。

## 为什么这轮算有效推进
这轮没有假装主策略已经 ready for live，也没有重复再写一页近义的 live rules 文案。

相比前几轮：
- `small_live_plumbing_v1` 解决的是项目级栏位；
- `small_live_ledger_template_v1` 解决的是同一张账本要记什么；
- `small_live_routing_dry_run_checklist_v1` 解决的是进 venue 前第一刀怎么审；
- **这轮新增的是**：当 `paper signal` 真要映射成 `live-shadow payload` 时，究竟先对齐哪些字段、哪些红旗必须当场阻断。

也就是说，当前 tiny-live 路线已经不只是“知道上 live 前要谨慎”，而是把 `paper_ref -> live_shadow_ref` 这条最关键的同步审计链，也压成了明确 artifact。

## 验证 / 证据
执行：
1. `python3 -m py_compile scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_alpha_closure_board_report.py`
3. `python3 scripts/build_plans_site.py`
4. `sed -n '1,10p' reports/artifacts/alpha_closure_board/paper_live_shadow_parity_checklist_v1.csv`
5. `grep -n "Paper-live shadow parity checklist（v1）\|paper_live_shadow_parity_checklist_v1.csv" reports/site/factors/alpha_closure_board/report.html`
6. `grep -n "2026-03-16 04:36 UTC\|paper_live_shadow_parity_checklist_v1.csv" docs/TODO.md reports/site/plans/momentum_todo.html`

已确认：
- 新 checklist artifact 生成成功；
- `alpha_closure_board` 已出现新的 reader-facing 卡片；
- `TODO` 顶部排班与项目级 live 规则补充都已同步到站点镜像。

## 本轮 hard verdict
- **Run 1 / Paper Seat**：仍是 `waiting_not_due`，不能伪造 refresh。
- **Run 2 / Live Seat**：仍在 cooldown，不应重跑 heavy rerun。
- **Run 3 / tiny-live plumbing**：当前最有效的一刀，是把 `paper-live shadow parity` 压成可审计 checklist，而不是继续写抽象 live 规则页。

一句话结论：
**这轮把 tiny-live 路线里最容易“口头说对齐、实际没法审”的 `paper vs live-shadow` 同步链，正式压成了 operator checklist。**

## 风险 / 边界
- 这仍不是 live approval，也不是 routing 已接通。
- 当前只补的是 checklist，不是实跑样例；因此还不能宣称 `paper/live mismatch` 已被真实验证。
- `parity_red` 阈值目前是 v1 执行口径；后续若要改更严格/更宽松，应单独立项，不应在这份 checklist 上静默漂移。

## 下一步建议
- 若下一轮 Run 1 / Run 2 仍 blocked，`small_live` 侧不要回头再写抽象规则页；若还要继续，只应补 `parity_red action / sample-row` 这类紧邻执行卡。
- 更高优先级仍是：
  1. breakout cooldown 结束后，按 guard 只给一次 honest rerun 机会；
  2. 若 Rank 1 τ-band 新 bar 仍不足，则把 Rank 2 `volume + support-flip + higher-low` 从 spec 推到 first verdict。

## Commit hash
- 未提交。

## 如果未提交，原因
- 当前工作区存在大量与本轮无关的既有脏文件与未跟踪文件，不适合安全 selective commit；本轮只刷新必须的脚本 / artifact / 页面 / 计划镜像。