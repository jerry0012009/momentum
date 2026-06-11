# bot3 optimization loop log — 2026-04-15 17:06 UTC

## 执行小点
- cycle_plan item 1
- target: `research/quant_digests/2026-04-15_1621_vwapstretch-rsi-15madveto-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` 成本口径 + 最小 honesty 检查）

## 结果摘要（会改变系统认知）
`VWAP stretch × RSI exhaustion with 15m AD veto` 在本轮统一口径下未通过 first verdict：按 `t+2` 入场并持有 3 bar（15m）计算后，`Asia/EU/US` 在 `4/6/8bps` 下费后均为负，因此本轮收口 `background/P0`，不进入 survivor、且不分配 Rank。

## 关键证据
复核脚本来源：
- `reports/artifacts/quant_digests/2026-04-15_vwap_rsi_portability_probe.py`

按 UTC 时段聚合（Asia=00-07, EU=08-15, US=16-23），以信号时刻 `t`，执行采用 `t+2` close 入场、`t+5` close 出场（方向对称），净收益均值（bps）：

| 成本口径 | Asia | EU | US | 全体均值 | 样本数 |
|---|---:|---:|---:|---:|---:|
| net4bps | -3.003 | -11.150 | -2.409 | -5.784 | 106 |
| net6bps | -5.003 | -13.150 | -4.409 | -7.784 | 106 |
| net8bps | -7.003 | -15.150 | -6.409 | -9.784 | 106 |

判定：未满足“Asia/EU/US 分时段同向为正”。

## 最小 honesty / execution realism 子检查
- `15m` 过滤对齐使用 `merge_asof(..., direction="backward")`，检查结果 `filter_time > open_time` 计数为 `0`，未见 15m 过滤前视。
- 指标均为 rolling / ewm 常规时序计算（`VWAP(288)`、`RSI(14)`、`ADX(14)`、`volume_sma(20)`），未使用未来窗口重算或 centered 平滑。

结论：未发现可单独推翻本轮 verdict 的泄漏/重绘型 blocker；负费后结果本身已足够给出 `background/P0`。

## 本轮执行结论
- verdict: `background/P0`
- rank_assignment: `none`（未达到 `keep_P1`）
- survivor: `not eligible`
- status: `done`
