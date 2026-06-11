# 2026-03-17 09:25 UTC · Rank 29 no-overlap honesty check（P1 -> P2）

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 先执行了 `Run 1` 守门：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：全 desk 仍是 `waiting_not_due`，没有 `due-now / overdue` lane，因此按 board 规则转到 `Scout Seat`。

## active Scout 边际价值比较（本轮前）
- `Rank 17 / Rank 2`：当前没有新的真实 `append/review need`。
- `Rank 26 / 27 / 28`：已在 `park / evidence pool`，不该重开。
- `Rank 29`：处于 `P1 weak candidate`，且 board 明确只剩 **1 次 genuinely verdict-changing cheap honesty check** 预算。
- 结论：本轮主资源应给 `Rank 29`，不并行打开新候选。

## 本轮主点
- 执行 `Rank 29` 的那 1 次最小诚实检查：**`no_overlap_guard`**。
- 检查目的：验证上一轮收益是否依赖“同资产并发持仓（overlap）”导致乐观放大。

## 执行动作
1. 新增脚本：`scripts/build_rank29_no_overlap_honesty_check.py`
2. 固定口径：
   - 样本：`BTC/ETH/SOL 120d 15m`（复用现有 `rank29` signals）
   - 信号：`breakout_align_ge2`
   - 执行：`next-bar open`，持有 `8` bars
   - 对照：`overlap_allowed` vs `no_overlap_guard`
   - 成本：`6/10/15/20 bps per side`
3. 产物：
   - `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/no_overlap_overall_summary.csv`
   - `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/no_overlap_asset_summary.csv`
   - `reports/site/factors/scout_rank29_trendline_breakout_navigator_15m/no_overlap_honesty_check.html`

## 关键结果（hard evidence）
- `no_overlap_guard` 后仍存活：
  - `6bps`：`mean_total_return≈+57.79%`，`positive_asset_ratio=3/3`
  - `10bps`：`≈+40.99%`，`3/3`
  - `15bps`：`≈+22.49%`，`3/3`
  - `20bps`：`≈+6.41%`，`2/3`
- 交易数从 overlap 模式的 `[171,150,159]` 下修到 no-overlap 的 `[150,132,140]`，但没有出现“去 overlap 即坍塌”的红旗。

## 本轮 hard verdict
- **`promote to paper candidate pool（P2）`**
- 理由：
  - P1 仅有的一次便宜诚实检查已执行且未爆雷；
  - 在更诚实的 no-overlap 约束下，轻 friction（6/10/15bps）仍保持跨资产正向。

## 对 board 的更新
- 已把 `Rank 29` 从 `P1 weak candidate` 更新为 **`paper candidate pool（P2）`**。
- 下一轮若继续认领，默认必须按 `P2` 预算做 **1 个会改变 verdict 的最小检查**，并直接给出：
  - `升到 P3 narrow paper pilot` 或
  - `压回 park`

## 审计备注
- 工作区存在大量无关脏文件；本轮未 commit，未混提。
- 仅新增最小必要脚本/产物/网页与日志，符合 desk 回合制最小推进原则。
