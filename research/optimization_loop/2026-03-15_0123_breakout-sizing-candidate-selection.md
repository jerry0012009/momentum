# breakout sizing 候选同框架定序（pair vs context）

## 本轮认领

- 主点：`support_breakout_v0 / breakout-short follow-up`
- 具体任务：把 `pair-conditioned` 与更窄 `context-conditioned` 两版 sizing 放进同一更严格口径对照，明确 breakout 线默认保留哪个 sizing 候选。

## 为什么做这刀

上一轮已经有两版动作，但默认候选还没正式定序：
1. `pair-conditioned halfsize` 改善更大；
2. 更窄 `context-conditioned halfsize` 影响面更小；
3. 需要同框架下直接比较 overall 与 pure-test，避免两条候选并排悬着。

同时遵守本轮硬约束：不再重复提交“同一刀 pair-halfsize”的近义切片，而是走允许的新轴（更严格 portfolio honesty 下的候选定序）。

## 本轮改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 同时计算两版候选：
     - `avoid_fluctuating_eth_sol_pair_halfsize`
     - `avoid_fluctuating_eth_sol_test_validate_up_halfsize`
   - 新增 `summarize_sizing_candidate_compare(...)`，把两版候选放进同一张定序表；
   - 新增/补齐 artifact：
     - `avoid_fluctuating_eth_sol_pair_halfsize_holdout_split_20bps.csv`
     - `avoid_fluctuating_sizing_candidate_compare_20bps.csv`
   - 在 `support_breakout_v0_h24` 页新增“默认候选保留谁”的决策段与对照表。
2. 更新 `scripts/build_alpha_closure_board_report.py`
   - breakout 卡片证据与 next-step 改为“默认先保留 pair-conditioned，context-conditioned 为次级分支待更严格复核”。
3. 更新 `docs/TODO.md`
   - 将 `Current relay baton` 第 3 项标记为完成，并补入同框架定序结论。
4. 重建页面
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `reports/site/plans/momentum_todo.html`

## 关键结果（同一更严格口径）

来自 `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_sizing_candidate_compare_20bps.csv` 与对应 holdout split artifact：

- `pair-conditioned`（默认候选）
  - overall delta vs gate：约 `+4.44pp`
  - max drawdown：约 `-9.04%`
  - pure-test：`5` 小时，条件累计改善约 `+0.76pp`
- `context-conditioned`（更窄分支）
  - overall delta vs gate：约 `+2.40pp`
  - max drawdown：约 `-9.97%`（基本无进一步改善）
  - pure-test：`3` 小时，条件累计改善约 `+0.08pp`

结论：当前默认应保留 `pair-conditioned` 作为 breakout sizing 主候选；`context-conditioned` 保留为更窄、证据仍薄的次级分支。

## 验证

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

命中：
- `support_breakout_v0_h24/report.html` 已出现“默认该留 pair-conditioned 还是 context-conditioned”段；
- `alpha_closure_board/report.html` breakout 卡片已同步“pair 默认、context 次级”；
- `docs/TODO.md` 与 `plans/momentum_todo.html` 第 3 项已完成并同步定序结果。

## Commit

本轮未提交。

原因：当前仓库存在大量在途改动与跨路径脏文件，且本轮涉及文件在本轮前已处于 dirty 状态；此时 selective commit 无法保证只打包本轮改动。