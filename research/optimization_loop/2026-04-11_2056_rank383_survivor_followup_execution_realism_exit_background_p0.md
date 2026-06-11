# Rank 383 survivor follow-up（execution realism decisive check）

- 时间：2026-04-11 20:56 UTC
- 执行槽位：Surviving candidate slot
- 对象：`Rank 383 / past-hour MAX overvaluation XS fade alpha`
- 关联 intake：`research/quant_digests/2026-04-11_1258_pasthour-max-overvaluation-xs-fade-alpha.md`

## 本轮动作
按 cycle_plan 仅执行 survivor 唯一 follow-up：围绕唯一 blocker（成本后净边际）做最小、便宜、可改变层级的 execution realism 检查。

数据来源：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/intraday_lottery_max_probe_series_2026-04-11.csv`

口径：固定论文同族最优落点 `15m_1bar / k=4`，读取全样本逐笔 `gross_pnl_bp` 与 `turnover`，对比三档净边际：
1. 已有低成本档 `0.25bp`
2. 更保守 `1.00bp`
3. 最小延迟保守代理：在 `1.00bp` 基础上额外扣 `0.25bp * turnover`（等价 `1.25bp`）

## 关键结果
- observations: `5755`
- `avg_gross_bp`: `+0.8113`
- `avg_turnover`: `1.1759`
- `avg_net_bp @0.25bp`: `+0.5173`
- `avg_net_bp @1.00bp`: `-0.3647`
- `avg_net_bp @1.25bp(delay proxy)`: `-0.6587`

## 出口决策（按计划二选一）
**`background/P0`**。

原因：该 alpha 仅在低成本执行档存活；一旦进入保守现实口径（`1bp` 及以上，含最小延迟代理）即稳定转负。当前唯一 decisive blocker 仍是**成本后净边际不可保留**，且本轮已用完 survivor 唯一 follow-up，不满足 `promote_P2` 条件。

## 改变系统认知的一句话
`Rank 383` 在保守执行现实下净边际不可迁移（`1bp` 与 `1.25bp` 均为负），因此 survivor 收口为 `background/P0`，不升 `P2`。
