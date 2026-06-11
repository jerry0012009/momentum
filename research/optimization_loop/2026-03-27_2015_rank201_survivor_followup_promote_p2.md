# Rank 201 / UTC clock seasonality low-switch schedule — survivor 唯一 follow-up promote P2

- 时间：2026-03-27 20:15 UTC
- 对象：`Rank 201 / UTC clock seasonality low-switch schedule`
- 本轮角色：bot3 对 survivor 做唯一一次 decisive follow-up，只回答这条 `UTC fixed-hour low-switch schedule` 在 `15m` 真执行口径下是否仍存活，以及它相对 `Rank 200` 是否具备独立 admission 价值

## 结论
**单一正式 verdict：`promote_P2`。**

更准确地说，进入 `Active P2` 的对象是：

> **8 币 perp 等权的固定 UTC 低切换 schedule：`20:00~21:59 UTC long`，`22:00~23:59 UTC short`，执行在 `15m` bar 上，当前先按静态 pocket 做 desk 候选。**

## 这次补的唯一关键证据
我直接用现成的 Binance perp `15m` 缓存，对 digest 里保留下来的当前 pocket（`20~21 long / 22~23 short`）做了 executable transfer check，而不是继续停留在 `1h` 小时级映射叙事。

- 数据：`reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/*__365d__15m__perp.csv`
- 标的：`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK`
- 检查窗：`2026-01-01` ~ `2026-03-26 UTC`
- 执行口径：
  - `20:00` 切入 long sleeve
  - `22:00` long -> short 翻仓
  - `00:00` 平 short
  - 仅在仓位变化时扣成本；按单边 `4 bps` 扣

### 15m executable transfer check 结果
组合层（8 币等权）：
- gross cumret：`+35.85%`
- net cumret：`+18.96%`
- gross Sharpe：`4.91`
- net Sharpe：`2.84`
- 平均每个交易日约 `3` 次仓位变化（long open、flip、flat）

分币种净后都没有翻负：
- BTC：`+3.86%`，net Sharpe `0.86`
- ETH：`+16.17%`，net Sharpe `2.35`
- SOL：`+32.55%`，net Sharpe `3.79`
- BNB：`+6.50%`，net Sharpe `1.34`
- XRP：`+5.80%`，net Sharpe `0.93`
- DOGE：`+32.81%`，net Sharpe `3.79`
- ADA：`+31.01%`，net Sharpe `3.65`
- LINK：`+26.30%`，net Sharpe `3.30`

这一步已经回答了 survivor 阶段最关键的问题：**它不是只能在 `1h` 叙事层面成立；落到 `15m` 真执行后，当前 pocket 仍然存活。**

## 相对 Rank 200 的独立性怎么判
它与 `Rank 200` 当然同属 clock / schedule 家族，但**不是同一个策略的换壳 pocket**，理由有三点：

1. **对象层不同。**
   - `Rank 200` 是 `BTC-only`、`weekday × hour` 稀疏弱桶、`monthly refresh`、`4h short`。
   - `Rank 201` 是 `8-asset cross-asset`、固定 `UTC hour-of-day`、当前静态 pocket、`daily long+short sleeves`。

2. **触发结构不同。**
   - `Rank 200` 依赖每月滚动重算 bottom-5 weekday-hour weak buckets，本质是稀疏事件时钟；
   - `Rank 201` 则是每天固定时段运行的低切换 schedule，本质更接近日内 circadian sleeve，而不是“某几个 weekday-hour 事件后再做后续 4h short”。

3. **资产暴露不同。**
   - `Rank 200` 的 admission 结论已经明确是 BTC-only，不主张扩成跨资产；
   - `Rank 201` 当前恰恰是跨资产组合在 `15m` 上一起存活，且并非靠 BTC 一条腿扛住。

所以更诚实的系统认知是：
> `Rank 201` 不是 `Rank 200` 的重复命名，但它仍属于同一大类 `clock/schedule raw alpha family` 的另一条母线；值得获得独立 `P2 admission`，但不该被误读成完全无关的新题材。

## 为什么这轮是 promote_P2，而不是直接 P3 / background
### 不是直接进 P3
还不到。虽然 `15m` executable transfer check 已经过关，但 admission 还没补完：
- 时间稳定性仍需拆月/拆 regime；
- 参数稳定性还要回答 `21 only / 21 long + 22 short / 19~21 long + 22~23 short` 等邻近 pocket 是否同向；
- honesty / execution realism 还应再补更明确的 venue/cost/调仓边界定义。

所以这轮最合规的层级是 **先升 `P2 admission`**，而不是直接 paper queue。

### 不是退回 background
因为 survivor 该回答的两件事，这轮都给了肯定答案：
1. `15m` 真执行版仍存活；
2. 相对 `Rank 200` 具备独立 admission 价值。

既然如此，就不该把它用完 survivor 预算后直接丢回 background。

## 本轮改变系统认知的一句话
`Rank 201 / UTC clock seasonality low-switch schedule` 的 survivor 唯一 follow-up 已经完成：`20~21 UTC long / 22~23 UTC short` 在 `8` 币 perp `15m` 真执行口径下成本后仍为正，且它相对 `Rank 200` 属于同一时钟家族中的另一条独立母线，因此本轮应从 `Surviving candidate` 升入 `Active P2`。
