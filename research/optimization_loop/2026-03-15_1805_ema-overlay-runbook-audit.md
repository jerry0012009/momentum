# 2026-03-15 18:05 UTC｜EMA/PSAR A股daily overlay runbook 审计（deployment 口径）

## 为什么这次选这个
- 本轮继续优先 `EMA / PSAR raw alpha focus`，且对齐当前 steering：少做近义 board，多做更接近 paper/shadow 运行规则的可执行结论。
- `EMA` 线已经有 candidate/operating/monitoring/runbook 基础；当前更关键的是把“PSAR 快退出到底该不该焊进默认 runbook”做成可审计 verdict。

## 做了什么改动
1. 在 `scripts/build_ema_psar_raw_alpha_report.py` 新增 A股 daily overlay 审计切片：
   - 新增 `build_ema_ashare_daily_psar_overlay_audit()`，复用既有 strict holdout 框架，对比 `EMA-only` vs `EMA + PSAR exit overlay`。
   - 产出 3 个新工件：
     - `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_holdout_window_metrics.csv`
     - `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_pocket_summary.csv`
     - `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_psar_overlay_overall_summary.csv`
2. 把 overlay 审计结果接入 runbook 生成链：
   - `build_ema_paper_trading_runbook(...)` 增加 `daily_overlay_pocket_df` 输入；
   - 在 `创业板ETF 1d` / `沪深300ETF 1d` 的 runbook `current_runbook_read` 中写入 overlay verdict（强调是否仅限 shadow protective 观察位）。
3. 在 EMA 报告页新增 `Q35e`（deployment-facing）：
   - 直接回答“PSAR 快退出是否应焊进当前 A股 daily 默认 runbook”；
   - 给出 primary/shadow/overall 三层读法与结论。
4. 更新 `docs/TODO.md`：
   - 将 `做一版 EMA + PSAR 最小组合研究` 标记为 `[x]`；
   - 追加本轮 runbook overlay audit 的最新结果说明（用真实数值，不再写估计值）。

## 验证 / 证据
- 语法与构建：
  - `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py` 通过。
  - `python3 scripts/build_ema_psar_raw_alpha_report.py` 成功生成报告与工件。
  - `python3 scripts/build_plans_site.py` 成功更新 plans 页面。
- 关键结果（`ema_ashare_daily_psar_overlay_*`）：
  - `创业板ETF 1d`（primary）：`8` 个 holdout 中 `75%` 改善，median net20 delta `+1.996pp`，median trade delta `+13`。
  - `沪深300ETF 1d`（shadow）：`8` 个 holdout 中仅 `25%` 改善，median net20 delta `-1.507pp`，median trade delta `+15`。
  - overall：改善占比 `50%`，median net20 delta `-0.381pp`，verdict = `mixed_shadow_only_not_default`。
- 网站可见性：
  - `reports/site/factors/ema_psar_raw_alpha/report.html` 已新增 `Q35e`。
  - `reports/site/plans/momentum_todo.html` 已包含 TODO 状态更新。

## 风险 / 边界
- 本轮结论是 **A股 daily runbook 接线层** 的诚实审计，不是“PSAR 全市场无效”结论。
- 结果显示 primary pocket 有改善信号，但跨 A股 daily 合并后仍是 mixed；因此当前只能给到“shadow protective 候选/观察位”，不能改写默认 admission 规则。
- 构图阶段仍有中文字体缺失 warning（不影响 CSV/HTML 结果）。

## 下一步建议
- EMA 线下一刀优先：
  1) 继续真实 market-close refresh / week-1 review（而非再扩近义 runbook wording）；
  2) 对 `创业板ETF 1d` 的 overlay 候选做更窄的执行约束（例如仅 shadow protocol，不触发默认持有逻辑）；
  3) `沪深300ETF 1d` 继续按 shadow gate 走，不允许 overlay 充当 promotion patch。

## Commit hash
- 本轮未提交。
- 原因：当前 repo 存在大量与本轮无关的既有脏变更（跨 docs/reports/scripts/memory 与未跟踪目录），不适合安全做 selective commit，避免混入无关改动。
