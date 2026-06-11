# Rank 423 P2 exit：core scope + live spec 已闭合，直接 promote_P3

- 时间：2026-04-19 03:00 UTC
- 对象：`Rank 423 / liquidation shock × OI unwind -> 30m exhaustion fade`
- 执行动作：`P2 admission / exit decision`；只补 `cross-asset scope + final live spec(event-close vs 1-bar delay)` 这一个出口决策所需最小 blocker
- 结论：`promote_P3`

## 复用证据
- `research/optimization_loop/2026-04-19_0040_rank423_liqshock_oiunwind_freshintake_keep_p1_symbol_cost_bucket.md`
- `research/optimization_loop/2026-04-19_0154_rank423_survivor_followup_promote_p2_entry_realism.md`
- `reports/artifacts/rank423_entry_realism_followup/rank423_entry_realism_summary.json`
- `reports/artifacts/rank423_entry_realism_followup/rank423_entry_realism_events.csv`

## 本轮只回答两个出口问题
### 1) cross-asset scope 是否已经足够收口？
是。当前证据已经把可 live 的 scope 收敛得很清楚：
- `BTC`：`delay1 net8 ≈ +11.11bps`
- `SOL`：`delay1 net8 ≈ +22.42bps`
- `XRP`：`delay1 net8 ≈ +37.12bps`
- `ETH`：`close-entry net8 ≈ +8.08bps`，但 `delay1 net8 ≈ -6.53bps`
- `ADA`：`close-entry net8 ≈ +23.31bps`，但 `delay1 net8 ≈ -2.87bps`，且样本仅 `3`

因此这条线不该再表述成 5 币等权通杀；诚实可执行的 queue-facing scope 应直接收窄为：

> **core live scope = `BTC/SOL/XRP`**
>
> `ETH/ADA` 仅保留为 `close-entry watch`，不进入默认 live spec。

这不是 fatal flaw，因为 core 三币都在统一 delay 口径下保住清楚 after-cost pocket；失真只出现在 watch legs，而不是策略主体。

### 2) 最终 live spec 该选 `event-close` 还是 `1-bar delay`？
应选 **`1-bar delay`**。

原因不是它看起来更漂亮，而是它同时满足：
- 组合层在更诚实执行下仍成立：`delay1 net8 ≈ +15.78bps/event`，`net12 ≈ +11.78bps/event`
- 对 core scope 没有造成破坏，反而更清楚地区分出可 live 的 `BTC/SOL/XRP` 与不应默认纳入 live 的 `ETH/ADA`
- 相比 `event-close`，`delay1` 更接近 bar-close 后真实能执行的 runner 口径，不需要把默认 live 依赖在“事件 bar 收盘瞬间立刻反手”的更紧实现假设上

micro-confirm 不是必须 blocker：它把样本压到 `17` 个后虽然仍正，但不会改变系统最重要认知——`delay1` 本身已经足够支撑 live spec。

## 系统认知变化
`Rank 423` 的 P2 admission 已经诚实收口：`BTC/SOL/XRP` core 在统一 after-cost 下通过，`ETH/ADA` 只需剔除为 watch，不构成 decisive blocker；最终 live spec 也已收敛为 `1-bar delay`。因此本轮不应继续停留在 `P2`，而应直接升级到 `P3 / Paper launch queue`，等待下一步 runner + scheduler + first verified run 的接线动作。

## runtime verdict
- `Rank 423`：`promote_P3`
- queue-facing live spec：`BTC/SOL/XRP equal-weight core + 1-bar delay + 30m exhaustion fade`
- `ETH/ADA`：`close-entry watch only`，不进入默认 live runner scope
