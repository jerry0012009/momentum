# bot3 optimization loop — same-venue basis zscore shell fresh intake first verdict（background/P0）

- 时间：2026-04-14 01:36 UTC
- 执行对象：`research/quant_digests/2026-04-13_1808_samevenue-basis-zscore-shell.md`
- 对应 cycle_plan 小点：#4（fresh intake first-verdict）

## 本轮执行
按 state 的首个 pending 小点，对 `same-venue basis zscore shell` 做统一成本/延迟口径 first verdict，并补 1 条最小 honesty 检查（标准化窗口与触发/平仓是否引入 lookahead/repaint/future anchor）。

## 证据摘录（沿用已落库 artifact）
来源：
- `reports/artifacts/quant_digests/delta_basis_binance_probe_summary_2026-04-13.csv`
- `reports/artifacts/quant_digests/delta_basis_binance_probe_costladder_2026-04-13.csv`
- `reports/artifacts/quant_digests/2026-04-13_delta_basis_binance_probe.py`

关键数值（gross+funding，bps/笔）：
- BTC 1h: `+0.5057`
- ETH 1h: `+0.7845`
- BTC 15m: `+0.4028`
- ETH 15m: `+0.3546`

8bps round-trip 后净值（avg net bps/笔）：
- BTC 1h: `-7.4943`
- ETH 1h: `-7.2155`
- BTC 15m: `-7.5972`
- ETH 15m: `-7.6454`

结论：在统一成本与最小执行延迟口径下，same-venue broad 版本费后稳定性不成立，未达到 `keep_P1` 的最小可执行门槛。

## honesty / execution realism 最小检查
静态核验 `2026-04-13_delta_basis_binance_probe.py`：
- entry 使用 `entry_idx = i + 1`（下一根执行）
- exit 使用 `exit_idx = i + 1`（下一根执行）
- zscore 由 `rolling(lookback_bars)` 计算，未见 future-window anchor

本轮未发现会推翻结论的单一 honesty blocker；结论仍是成本后全灭而非因前视误报。

## 本轮 verdict（改变系统认知的一句话）
`same-venue basis zscore shell` 在 Binance majors 的 1h/15m 统一成本与最小执行延迟口径下，8bps 后四个 bucket 全部显著为负，且最小 honesty 检查未见 lookahead/repaint/future-anchor，故 fresh intake 直接收口为 `background/P0`（不进入 P1）。

## runtime 回写动作
- 将 `cycle_plan` 第 4 小点写为 `done`
- 更新 `Fresh intake slot` 最新结论与记录
- 更新 `Background pool` 最新 parked 对象与记录
