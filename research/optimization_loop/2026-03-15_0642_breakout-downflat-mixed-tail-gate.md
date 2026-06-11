# Momentum Auto Optimization Loop — 2026-03-15 06:42 UTC

## 本轮主点（deployment-facing）
- 主点：`support_breakout_v0` 的 `down regime tail` / `admission hard gate`。
- 紧邻子点：在不改动默认 `raw + avoid_fluctuating + ETH+SOL pair-conditioned halfsize` 主候选前提下，补一刀**最小 mixed-tail protective gate**（`down + flat` 小时再 `0.5x`），检验它是否能成为 `one_more_gate` 的下一刀。

## 为什么选这个点
- EMA 线已连续补齐 `candidate/operating/scorecard/monitoring`，本轮默认不继续做近义 board。
- breakout 线当前 blocker 已收敛到 `pure-test / down-tail honesty`，更接近 admission 决策。
- 本轮目标是交付一个可落到报告页的、可量化的 gate 候选，而不是继续 wording。

## 执行内容
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增通用 active-context 明细构建：
   - `build_hourly_active_context_detail(...)`（覆盖所有 active hours，不限二仓 pair）。
2. 基于现有默认候选路径（`avoid_fluctuating_eth_sol_pair_halfsize`）新增最小 overlay：
   - 仅对 `regime_mix = down + flat` 的 active hours 再做 `0.5x`。
3. 新增并落盘 artifact：
   - `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_hourly_path_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_hourly_summary_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_affected_hours_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_holdout_split_20bps.csv`
   - `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_20bps.csv`
4. 在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增 deployment-facing 段落：
   - “如果保留当前 pair candidate，再叠一刀最小 down+flat mixed-tail protection，会不会更像下一道 gate？”
   - 明确：该刀是 `promising gate candidate`，**仍不足以解除** `one_more_gate`。
5. 更新 `docs/TODO.md` breakout 已完成条目下的最新补充（06:30 UTC），并重建 plans 页面：
   - `python3 scripts/build_plans_site.py`

## 结果（核心数字）
- 在默认 `pair-conditioned` 候选上叠加 `down+flat mixed-tail` overlay 后：
  - overall hourly path（20bps）累计：`19.90% -> 20.88%`
  - max drawdown：`-9.04% -> -8.53%`
- strict pure-test mixed tail（单段，约 25 小时）
  - 累计：`-0.50% -> -0.25%`
  - delta：约 `+0.26pp`
  - drawdown 改善：约 `+0.87pp`
- 诚实结论：
  - 这刀说明下一步 gate 可以先做 very-small protective honesty，不必立刻扩新泛化变体；
  - 但证据仍集中在单段 mixed tail，未直接填平 pure `down` coverage gap，verdict 继续维持 `one_more_gate`。

## 最小验证
- `python3 scripts/build_support_breakout_v0_reports.py`（成功）
- `python3 scripts/build_plans_site.py`（成功）
- `grep` 检查报告页新增段落与数值（成功）

## 变更文件（本轮相关）
- `scripts/build_support_breakout_v0_reports.py`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `docs/TODO.md`
- `reports/site/plans/index.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/report.html`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_*.csv`

## Git / hygiene 记录
- 当前 worktree 存在大量与本轮无关的历史脏改与未跟踪文件；本轮未尝试混提无关改动。
- 本轮**未提交**：原因是仓库非本轮相关脏改过多，缺少安全的最小 selective-commit 边界。