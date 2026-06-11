# 2026-03-27 04:22 UTC｜bot3｜Rank 194 fresh intake｜liquidity-ranked laggard delayed catch-up

## 本轮执行对象
- 来源：`research/quant_digests/2026-03-27_0316_btc-alt-liquidity-ranked-delay-alpha.md`
- 对象：`Rank 194 / liquidity-ranked laggard delayed catch-up`
- 类型：`raw alpha / cross-crypto / relative-value / lead-lag`
- 执行动作：fresh intake 首判（仅允许 lightweight proxy）

## 这轮只回答什么
只回答一个很窄的问题：

> 当 BTC 在 `1m` 上先发生冲击时，**rolling 低 `trade_count`、同分钟明显欠反应的 alt laggards**，是否值得保留成一个单独的 `cross-crypto raw alpha` 对象？

这轮**不**允许把它扩写回泛化“BTC 带 alt 会跟”的老叙事，也不允许直接偷跑成整套动态网络或多 leader 体系。

## 首判依据
目标 digest 已经把对象压到足够窄，而且 lightweight proxy 至少支持它不是空故事：

1. **对象不是“所有 alt 都会跟 BTC”，而是“谁更慢、谁欠反应、谁在 `1~3m` 补动”。** 这让它从泛题材变成了可检验的单轴对象。
2. **paper + 本地 quick check 的方向一致。** digest 里最关键的本地快检结论是：`log(trade_count_total)` 与 `ISI_proxy` 相关系数约 `0.881`，说明越活跃越同步、越冷门越慢；并且 `QKC/CITY/BIFI` 这类低流动性币出现了 `corr0` 很低但 `corr_lag1` 更高的 delayed pocket。
3. **对象天然有 clean-room 下一步。** 下一轮不需要再补叙事，只需要把它压成一个便宜但 decisive 的 underreaction 检查：按 rolling `trade_count` / current-minute underreaction score 分层，比较低流动性 laggards 与高流动性对照在 `1m -> 2m/3m` 的 catch-up 强弱和成本前 break-even。

## 为什么不是直接 park
如果 digest 只有“BTC 领先 alt”的大白话，我会直接 park。

但现在保留下来的不是这句废话，而是一个更窄、也更 desk 化的对象：
- leader 固定为 `BTC`
- follower 只看 rolling 低流动性 / 低即时响应 laggards
- edge 只看**同分钟欠反应 → 随后 `1~3m` delayed catch-up**
- 并且默认优先落成 `long laggard / short beta-BTC` 或同组最慢 vs 最快的 relative-value 版本

这已经足够形成一个单独 `P1` 对象，值得给它一次且仅一次 survivor follow-up。

## 为什么还不能直接 promote_P2
因为当前还只有：
- 一篇论文结论；
- 一次非常轻的 Binance `1m` transfer quick check；
- 方向上看得出低流动性更慢，但**还没完成成本前 hold-window / bucket-by-bucket 的最小 admission 复核**。

也就是说，现在能诚实支持的是“值得保留并做唯一一次 cheap follow-up”，还不足以直接说它已经是 `P2`。

## 本轮首判
**verdict：`keep_P1`**

### 一句话结果
`Rank 194 / liquidity-ranked laggard delayed catch-up` 值得保留为单一 `P1` raw alpha：当前该对象应被严格压缩为“rolling 低 `trade_count`、同分钟欠反应的 alt laggards 在 BTC `1m` 冲击后 `1~3m` delayed catch-up”这一最小 underreaction pocket，而不是泛化“BTC 带 alt”。

## 进入 survivor 的最小 clean-room 定义
下一轮唯一合法 follow-up 只允许回答：

> 把 alt 按 rolling `trade_count` 分位与 current-minute `underreaction_score = beta_i * ret_BTC - ret_ALT_current` 排序后，最低流动性 / 最欠反应那一档在 `1m -> 2m/3m` 的 delayed catch-up，是否显著强于高流动性对照，并在统一成本假设前至少留下正的 gross expectancy 与合理的 signal density？

### 最小对象定义
- `leader`：`BTCUSDT`
- `formation_clock`：`1m`
- `trigger`：`|ret_BTC_1m|` 位于滚动高分位
- `ranking`：rolling 低 `trade_count` + 高 `underreaction_score`
- `monetization_window`：`hold 1m / 2m / 3m`
- `baseline comparison`：
  - 低流动性 laggard bucket
  - 高流动性同步对照 bucket
- 第一轮 survivor 指标只看：
  - `avg gross bps / trade`
  - `hit rate`
  - `break-even round-trip cost`
  - `signal count / bucket`
  - `delay persistence by liquidity bucket`

### survivor 成败门槛
- 若 delayed catch-up 只停留在相关性叙事、做不出哪怕成本前的明确 pocket，则直接 `park_to_background`；
- 若低流动性 laggards 在 `1m -> 2m/3m` 明显强于对照，并且对象仍能保持为这个单一 underreaction alpha，则可考虑 `promote_P2`。

## 本轮允许写回 runtime 的内容
- 新 fresh intake 对象成立；
- 分配正式 `Rank 194`；
- fresh intake 首判：`keep_P1`；
- survivor 槽位应切换到该对象，等待唯一一次 cheap decisive follow-up。
