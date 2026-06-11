# Rank 423 survivor follow-up：entry-realism / delay 轴通过，promote_P2

- 时间：2026-04-19 01:54 UTC
- 对象：`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`
- 执行动作：survivor 唯一 follow-up；只补 `BTC/ETH/SOL/XRP/ADA` pocket 的 entry-realism / delay 轴，比较 `event close 反手`、`1-bar delay` 与最小 micro-confirm 后的 after-cost 保真度
- 结论：`promote_P2`

## 输入证据
复用 fresh intake 已落库事件样本：

- `reports/artifacts/quant_digests/2026-04-18_liq_oi_unwind_events.csv`
- 本轮 scope：`BTC/ETH/SOL/XRP/ADA`
- 样本：`25` 个 liquidation-like OI-unwind 事件
- 本轮新 artifact：
  - `reports/artifacts/rank423_entry_realism_followup/rank423_entry_realism_events.csv`
  - `reports/artifacts/rank423_entry_realism_followup/rank423_entry_realism_summary.json`

## 本轮最小 honesty 检查
只检查一个 blocker：更诚实入场是否会吃掉 `30m exhaustion fade` 的净边。

定义：
- `close-entry`：事件 bar 收盘立刻反手，持有 30m；
- `1-bar delay`：下一根 5m 收盘再反手，持有 30m；
- `micro-confirm`：下一根未继续沿事件方向扩张，或下一根 close 落在拒绝方向的半区，才用 delayed entry。

统一成本口径：继续使用 `8bps` / `12bps` round-trip stress。

## 结果
### 组合层
`BTC/ETH/SOL/XRP/ADA` 组合：

| entry 口径 | n | gross mean | net8 mean | net12 mean | net8 win |
|---|---:|---:|---:|---:|---:|
| close-entry 30m | 25 | `+22.74bps` | `+14.74bps` | `+10.74bps` | `80.0%` |
| 1-bar delay 30m | 25 | `+23.78bps` | `+15.78bps` | `+11.78bps` | `68.0%` |
| micro-confirm + delay | 17 | `+20.87bps` | `+12.87bps` | `+8.87bps` | `70.6%` |

结论很直接：这条线没有被更诚实入场毁掉。`1-bar delay` 不但没有吃掉均值，组合层反而略高于 close-entry；micro-confirm 过滤后样本少到 `17` 个，但 `net8` 仍有约 `+12.87bps/event`。

### symbol 层
本轮也暴露了 scope 应继续收窄的地方：

- `BTC`：delay / micro 后仍稳定，`delay net8≈+11.11bps`；
- `SOL`：delay 后明显改善，`delay net8≈+22.42bps`，micro 后仍 `+14.75bps`；
- `XRP`：delay 后最强，`delay net8≈+37.12bps`，micro 后 `+60.54bps`，但样本少；
- `ETH`：close-entry 有正 net，但 delay 后转负，说明它更像需要当根 close 反手、不能等待的快衰减 bucket；
- `ADA`：close-entry 很强，但 delay 后转负，样本仅 3 个，暂不应作为 P2 core。

因此 P2 admission 的诚实 scope 不应写成 5 币等权通杀，而应写成：

> **core scope：`BTC/SOL/XRP`；watch / optional：`ETH/ADA close-entry only`。**

这不是 fatal flaw，因为 survivor follow-up 的成功标准是回答 `30m exhaustion fade` 在更诚实入场后是否仍有独立 after-cost pocket；当前组合层与 core symbol 层都已通过。更精细的 `ETH/ADA` 是否剔除，留给 P2 admission 的 cross-asset / parameter stability 继续验证即可。

## 系统认知变化
`Rank 423` 的唯一 survivor follow-up 已用完且通过：`BTC/SOL/XRP` core 的 `1-bar delay / micro-confirm` 版本仍保留清楚 after-cost pocket，整体 5 币组合在 `delay + 8/12bps` 下也未失真，因此本轮从 `P1 / surviving candidate` 升级为 `Active P2`，下一步只应做 P2 admission，而不是继续补第二次 survivor 检查。

## runtime verdict
- `Rank 423`：`promote_P2`
- Survivor follow-up budget：`0`
- New Active P2：`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade (core BTC/SOL/XRP; ETH/ADA close-entry watch)`
