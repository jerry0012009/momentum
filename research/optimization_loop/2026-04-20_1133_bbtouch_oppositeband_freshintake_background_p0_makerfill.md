# bot3 auto — fresh intake first verdict：BB touch opposite-band maker shell

- 时间：2026-04-20 11:33 UTC
- 执行小点：cycle_plan item 1
- 对象：`research/quant_digests/2026-04-19_2132_bbtouch-oppositeband-maker-shell.md`
- 主题：`EMA200 顺势外轨触碰回归 × opposite-band maker exit`

## 结论

`EMA200 顺势外轨触碰回归 × opposite-band maker exit` 的 first verdict 已诚实收口：原 digest 中 `15m/5m` 表面正 pocket 主要依赖“触 band 当根即可成交”的理想入场；加入最小 `1-bar maker fill / cancel` realism 后，最强 `5m hold24` 从约 `+6.1bps` 转为 `-0.7bps`，`15m hold12` 从约 `+4.1bps` 转为 `-11.3bps`，且 `15m` TIME exit 仍约 `64%~68%`、5m 窄带 q25 为负，因此本轮不保留 survivor，直接收口 `background/P0`。

## 最小 honesty 检查

复用原 digest artifact，并新增一条最小 blocker 检查：

- 原始 digest 产物：
  - `reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_5m_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_bb_ema_oppositeband_15m_summary.csv`
- 本轮新增 honesty 产物：
  - `reports/artifacts/quant_digests/2026-04-20_bb_oppositeband_honesty_check.json`

### 关键数值

| 口径 | baseline net | 1-bar maker fill/cancel 后 | fill rate | TIME exit |
|---|---:|---:|---:|---:|
| `5m hold24` | `+6.10bps` | `-0.71bps` | `66.9%` | `35.3%` |
| `15m hold12` | `+4.08bps` | `-11.31bps` | `67.1%` | `67.6%` |

补充检查：

- `5m` 窄带 q25 子集：`mean_net≈-2.46bps`，说明窄 band 下回归空间不足以覆盖成本/挂单现实。
- `15m` baseline 虽仍有约 `+4bps`，但 TIME exit 约 `64%`，不是稳定 hit opposite band 的兑现结构；在 maker 1-bar 成交后直接转负。
- 小时切片正负分散明显，存在 trend-day / session-pocket 依赖风险，不足以构成独立可承接的 P1 front object。

## runtime verdict

- verdict：`background/P0`
- 不分配 Rank：本轮没有 `keep_P1` 或更高 verdict。
- Fresh intake slot 应清空，等待 bot2 下轮重排。
- cycle_plan item 1 写为 done。

## 对系统认知的改变

这条线可以保留为“maker-first BB/EMA 壳的设计参考”，但不能作为当前 front-slot survivor：它的可见正收益在最小 maker fill realism 下不成立，且兑现过多依赖 TIME exit / 持仓漂移，而不是可复用的 opposite-band 回补 edge。
