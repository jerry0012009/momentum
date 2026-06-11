# Rank 408 fresh intake verdict（BB expansion breakout × pullback continuation）
- 时间：2026-04-15 01:28 UTC
- 执行对象：`research/quant_digests/2026-04-14_2353_bbexpansion-pullback-continuation-shell.md`
- cycle_plan 小点：#2（fresh intake first-verdict）

## 本轮执行
基于 digest 已给出的 portability probe（Binance USDⓈ-M, 2026-01-01~2026-04-14, BTC/ETH/SOL/BNB）进行首判，并补 1 个最小 honesty/execution 子检查：核验信号到成交映射是否严格 next-bar。

### honesty / execution 最小子检查
- 读取 `reports/artifacts/quant_digests/bbexpansion_pullback_probe_trades_2026-04-14.csv`
- 检查 `entry_time - setup_time`
- 结果：
  - trades = 148
  - `min_entry_lag_min = 5.0`
  - `share_entry_lag_ge_5m = 1.0`
  - `non_positive_lag_count = 0`
- 结论：本 probe 的成交映射为统一 next-bar open 执行，无同 bar 成交/负延迟痕迹；未发现 lookahead 型执行作弊迹象。

## fresh intake verdict
- 资产层费后表现分化明显：BNB/BTC 口袋可行，ETH 明显不过线，SOL 边际。
- 合并口径在 4 bps 成本后仅剩轻微正值，不足以直接晋升 P2。
- 但 alpha skeleton（15m breakout setup + 5m pullback reversal entry）可复现，且 execution realism 子检查通过。

**最终结论：`Rank 408` -> `keep_P1`（不升 P2）。**

## 唯一 survivor follow-up blocker（已锁定）
只做一次：将资产域收敛到 `BTC+BNB`，在统一 4/6 bps 成本下验证 `positive week ratio` 与 `avg net bps` 是否同时稳态为正；若不成立则直接收口到 `background/P0`。
