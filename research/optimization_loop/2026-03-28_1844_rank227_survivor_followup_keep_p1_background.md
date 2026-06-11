# Rank 227 / stablecoin signed-flow shock path alpha — survivor follow-up 收口：keep_P1 后转 background

- 时间：2026-03-28 18:44 UTC
- 对象：`Rank 227 / stablecoin signed-flow shock path alpha`
- 本轮角色：当前唯一合法 `Surviving candidate` 的唯一一次 follow-up
- 结论：`keep_P1 后转 background`
- 产物：`reports/artifacts/rank227_event_followup_20260328_1844/summary.csv`

## 一句话结论
把这条线从 `1m kline proxy` 升级到 public `aggTrades` 的 event-time signed-flow shock 后，结论仍然没跨过 admission 门槛：BTC 只剩下很薄的 continuation gross，ETH 只剩下很薄的 decay-fade gross，**两边都过不了 `4~6 bps` round-trip 成本线，也没有形成稳定跨资产 pocket**，因此 `Rank 227` 不升 `P2`，按 survivor 预算正式收口为 `keep_P1 后转 background`。

## 这轮实际做了什么
按 `cycle_plan` 的第 1 个 pending 小点，直接用 Binance USDⓈ-M Futures 的公开 `aggTrades` 做最小 event-study，而不是继续停留在 bar proxy 叙事：

- 标的：`BTCUSDT`、`ETHUSDT`
- 样本：最近 `7` 个完整自然日（`2026-03-21` 到 `2026-03-27`）的 daily `aggTrades`
- 事件桶：`5s`
- shock 定义：`signed_notional` 相对过去 `1h`（`720` 个 `5s` 桶）的 rolling z-score，要求 `|shock_z| >= 3`
- 方向确认：shock 当桶收益与 flow 方向一致（避免把反向冲击也算成 continuation 候选）
- 非重叠：事件间隔至少 `15m`
- continuation markout：按 shock 方向看 `1m/3m/5m/15m`
- decay-fade 定义：若后续 `60s` 的平均绝对 flow 明显衰减（≤ 初始 shock 的 `35%`）或均值 flow 翻向，则从 `+1m` 开始反向看 `5m/15m`

脚本输出目录：
- `reports/artifacts/rank227_event_followup_20260328_1844/summary.csv`
- `reports/artifacts/rank227_event_followup_20260328_1844/btcusdt_events.csv`
- `reports/artifacts/rank227_event_followup_20260328_1844/ethusdt_events.csv`

## 关键结果
`summary.csv` 主结果如下：

### BTCUSDT
- raw shock events：`1935`
- 15m 非重叠事件：`425`
- decay-qualified events：`415`
- continuation `1m`：`+0.129 bps`
- continuation `3m`：`+0.404 bps`
- continuation `5m`：`+0.672 bps`
- continuation `15m`：`+1.531 bps`
- decay-fade `5m`：`-0.422 bps`
- decay-fade `15m`：`-1.281 bps`

读法：BTC 的 event-time 版确实比上一轮 `1m` kline proxy 更像“有一点 continuation”，但 strongest leg 也只到 `15m +1.53 bps` gross，离现实 `4~6 bps` 成本线仍差一大截；fade 这条腿则直接不成立。

### ETHUSDT
- raw shock events：`1785`
- 15m 非重叠事件：`404`
- decay-qualified events：`396`
- continuation `1m`：`+0.316 bps`
- continuation `3m`：`-0.744 bps`
- continuation `5m`：`-0.330 bps`
- continuation `15m`：`-1.083 bps`
- decay-fade `5m`：`+0.598 bps`
- decay-fade `15m`：`+1.612 bps`

读法：ETH 反而更像“shock 之后 eventually decay-fade 有一点形状”，但 strongest leg 也只到 `15m +1.61 bps` gross；continuation 在 `3m/5m/15m` 还转负，说明这不是一个跨资产一致的 continuation alpha。

## 这轮真正改变系统认知的地方
这次 follow-up 给出的新增，不是“stablecoin flow shock 在 aggTrades 上完全没东西”，而是更具体的：

> **event-time 版 signed-flow shock 的可见 edge 仍然只停留在 `1~2 bps` gross 量级，BTC 更像薄 continuation、ETH 更像薄 decay-fade；两条腿分裂、跨资产不共振，因此它不够资格进入 `P2 admission`。**

换句话说，上一轮可以把失败归因于 `1m kline proxy` 太粗；但这轮已经把粒度提升到 `aggTrades` 事件流，仍然没有把 gross edge 推到能穿过现实成本的位置。到这里，继续让它占用前排资源就不诚实了。

## 为什么不升 P2
`P2` admission 至少要看到某种“比较像真的”东西，而这轮没有：

1. **effectiveness / expected return 不够**：最好的 pocket 也只有 `~1.5-1.6 bps` gross，离 `4~6 bps` 净边太远。
2. **cross-asset stability 不够**：BTC 偏 continuation，ETH 偏 decay-fade；同一条腿并没有跨资产稳定复现。
3. **honesty 上已经做过最便宜的 event-level 提纯**：本轮不是继续重复同一维度的 bar proxy，而是已经升级到 public `aggTrades` event study；若这一步还过不了，默认不该自动续命。

## 为什么不是 drop_to_background with fatal flaw
它不是“逻辑自相矛盾”或“一眼假信号”，所以不需要写成 `fatal flaw`：

- 论文机制本身仍然自洽；
- public `aggTrades` 的 event study 也确实看到一点很薄的 path 形状；
- 只是这个形状太弱，**不足以在 major coins 上撑起值得 admission 的现实 raw alpha**。

所以最诚实的写法不是 `P0`，而是：
- 保留它作为历史 `P1` 证据；
- 但 survivor 预算已经用完，**现在就退出前排，进入 background**。

## 本轮正式 verdict
- `Rank 227 / stablecoin signed-flow shock path alpha`：**`keep_P1 后转 background`**
- 不升 `P2`
- 不保留 survivor 前排资格

## 对 runtime 的直接影响
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 应归零
- `Background pool` 更新为本对象的最新 parked 记录
- `cycle_plan` 第 1 项应写为 `done`

## 会改变系统认知的话
`Rank 227 / stablecoin signed-flow shock path alpha` 的唯一 survivor follow-up 已完成：public `aggTrades` event-time 版本下，BTC 只剩薄 continuation、ETH 只剩薄 decay-fade，最强 pocket 仍只有 `~1.5-1.6 bps` gross、过不了 `4~6 bps` 成本线，也没有稳定跨资产共振，因此本轮正式收口为 `keep_P1 后转 background`，不升 `P2`。
