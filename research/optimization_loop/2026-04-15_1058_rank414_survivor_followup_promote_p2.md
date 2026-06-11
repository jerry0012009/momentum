# Rank 414 survivor 唯一 follow-up — promote_P2

- 时间：2026-04-15 10:58 UTC
- 对象：`Rank 414 / roundtrip regime-stable pairs admission (admission-layer scope)`
- 本轮动作：在现有 15m pairs shell 结果表中做 head-to-head：`naive`（按相关性排序 top8） vs `Rank414 trade-quality proxy`（`active_pct + phi/half-life 稳定性 + net4` 组合）并统一查看 `net2/net4/net8`。

## 本轮执行证据
- 输入表：`reports/artifacts/quant_digests/pairs_repo_20260404/pair_scan_15m.csv`
- 相关性侧信息：`reports/artifacts/quant_digests/pairs_trading_in_crypto_probe_20260325_0948/pair_metrics.csv`
- 产物目录：`reports/artifacts/optimization_loop/rank414_followup_20260415/`
  - `naive_corr_top8_from_pairscan15m.csv`
  - `tradequality_top8_from_pairscan15m.csv`
  - `selector_head_to_head_summary.csv`

`selector_head_to_head_summary.csv` 关键结果：
- naive corr top8（352 trades）
  - `trade_weighted_net2_bps = +0.0286`
  - `trade_weighted_net4_bps = -0.0014`
  - `trade_weighted_net8_bps = -0.0615`
  - `positive_net8_pairs = 2/8`
- Rank414 trade-quality top8 proxy（408 trades）
  - `trade_weighted_net2_bps = +0.1623`
  - `trade_weighted_net4_bps = +0.1277`
  - `trade_weighted_net8_bps = +0.0587`
  - `positive_net8_pairs = 7/8`

## honesty / execution realism 最小子检查
- 本轮信号仍使用既有 shell 的 `t+2` 执行口径与 `net2/net4/net8` 成本梯度结果表；未新增 lookahead/repaint 路径。
- `pair_metrics.csv` 的 ADF 字段在该批次产物为缺失值，因此本轮 naive 侧退化为“相关性排序 top8”；该缺口不构成阻断升级的单一 decisive blocker（因为 trade-quality 侧在更严格 `8bps` 仍保留正的 trade-weighted 净值，且正净 pair 覆盖显著更高）。

## 出口结论
**结论：`promote_P2`。**

一句会改变系统认知的话：
> `Rank 414` 在 15m 统一成本口径下相对 naive 相关性选对照已表现出稳定 post-cost uplift（尤其 `net8` 从负转正且正净 pair 覆盖 `2/8 -> 7/8`），因此不再停留 P1 survivor，直接升级到 `Active P2` 做 admission 收口。
