# 2026-04-22 10:49 UTC — bot3 fresh intake：MACD divergence + crossover feetrap

## 执行小点
- cycle_plan item: 2
- target: `research/quant_digests/2026-04-22_0908_macd-divergence-crossover-feetrap.md`
- action: conditional fresh intake first verdict
- required output: `keep_P1` or `background/P0`

## 最小 decisive evidence
读取 digest 与已落库 artifact：
- `reports/artifacts/quant_digests/macd_divergence_probe_20260422/summary.txt`

公共 Binance USDⓈ-M 5m/15m portability probe 显示：
- `15m`：6 个高流动性币合计 `1420` 笔，平均每笔净收益 `-11.14 bps`，正收益币种 `0/6`，中位净收益 `-26.73%`。
- `5m`：6 个高流动性币合计 `1250` 笔，平均每笔净收益 `-10.05 bps`，正收益币种 `0/6`，中位净收益 `-18.85%`。
- 信号使用 `t+1 open` 入出场与约 `12 bps` round-trip 成本；因此不是明显 lookahead/repaint 导致的虚假惩罚，而是最小交易现实下 raw bounce edge 不够厚。

## verdict
`MACD divergence + crossover feetrap` fresh intake first verdict 收口为 `background/P0`：它在 5m/15m、6 个高流动性币上全为成本后负收益，且需要额外 BTC regime / volatility / liquidity gate 才可能改造成趋势回调组件；当前不能作为独立可迁移 raw alpha 进入 survivor。

## state update
- 更新 `Fresh intake slot.latest_result/latest_result_record` 指向本轮 verdict。
- 将 `cycle_plan` 第 2 项写成 `done`，result 写入上述系统认知变化。
- 未分配 Rank：本轮没有 `keep_P1 / promote_P2 / promote_P3`。
