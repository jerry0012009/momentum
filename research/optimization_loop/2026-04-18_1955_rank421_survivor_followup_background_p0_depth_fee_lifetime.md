# Rank 421 survivor follow-up -> background/P0

- 时间：2026-04-18 19:55 UTC
- 对象：`Rank 421 / 同所同步报价 cross-rate inconsistency`
- 本轮动作：survivor 唯一 follow-up（围绕唯一 blocker：`low-fee / depth-aware execution realism`）
- 结论：`background/P0`

## 本轮要回答的唯一问题
上一轮 fresh intake 已经把问题收敛得很窄：公开 Binance Spot BBO 下三腿闭环 gross edge 稳定存在，但是否能在更诚实的 `真实低费率 + 前3~5档深度 + 最小机会寿命` 口径下，仍留下可交易 after-cost pocket；若不能，就不能升 `P2`。

## 这轮补的最小 honesty 检查
我没有再扩成第二个研究点，只做了当前唯一 blocker 的最小执行现实检查：

1. 先复核上一轮 artifact：
   - `fee=0 bps/leg`：`90/90` 正 gross，median `+1.50bps`，best `+4.68bps`
   - `fee=4 bps/leg`：`0/90` 为正
2. 再用 Binance Spot 当前 live `bookTicker + depth(limit=5)` 对最优三角路径做前 5 档聚合，测试更乐观的低费率情景：
   - 费率口径新增：`0.75bps/leg`、`1bps/leg`、`2bps/leg`
   - 起始名义：`100 / 1000 / 5000 USDT`
   - 同时看 best BBO cycle 在约 `6s`、`250ms` 轮询下是否只是瞬时幻觉

## 关键结果
### 1) best cycle 的 gross 不是幻觉，但不足以穿过低费率门槛
本轮 live probe 的 best cycle 为：`USDT>BTC>BNB>USDT`

- BBO gross：约 `+1.75bps`
- 前 5 档、`100~1000 USDT`：gross 仍约 `+1.75bps`
- 前 5 档、`5000 USDT`：gross 已被深度吃到约 `+1.31bps`

但一旦扣最乐观的三腿 `0.75bps/leg`：
- `100 USDT`：`net ≈ -0.50bps`
- `1000 USDT`：`net ≈ -0.50bps`
- `5000 USDT`：`net ≈ -0.94bps`

更不用说：
- `1bps/leg`：best case 约 `-1.25bps`
- `2bps/leg`：best case 约 `-4.25bps`

同轮其他高 gross cycle 也一样：
- `USDT>BTC>FDUSD>USDT`：`gross +1.59bps`，`0.75bps/leg` 后 `-0.66bps`
- `USDT>BTC>ETH>USDT`：`gross +1.30bps`，`0.75bps/leg` 后 `-0.95bps`
- DOGE / USDC / FDUSD 相关闭环在前 5 档下衰减更快，`1000~5000 USDT` 已出现 gross 近零或转负

### 2) 机会寿命存在，但只能证明“gross pocket 持续”，不能把它救成可交易 net pocket
对当下 best cycle 做了约 `24` 个样本、每 `250ms` 一次的 BBO persistence probe：
- `24/24` 样本 gross 为正
- gross 区间约 `+1.67 ~ +1.84bps`
- median 约 `+1.75bps`

这说明它**不是纯 stale quote 单点幻觉**；但也恰恰说明 blocker 已被诚实回答：
- 连续存在的只是一个 `~1.7bps` 级别的 gross inconsistency
- 它没有大到能覆盖即便很乐观的三腿 `0.75bps/leg` 成本，更别说残腿、排队、撤改单失败与 child execution buffer

## 为什么这轮必须直接收口 background/P0
按照当前 cycle item 的 success criterion，这一步必须直接回答 `promote_P2` 或 `background/P0`。

现在答案已经很清楚：
- 它**没有**在最乐观的低费率 + depth-aware 口径下保住 after-cost pocket；
- survivior 唯一 follow-up 已经用掉；
- 唯一 blocker 已被回答为负，不再适合继续占用前排资源。

因此，最诚实的系统结论是：

> `Rank 421` 的公开同所三腿 cross-rate inconsistency 仍稳定表现为一个可观测的 gross relative-value dislocation，但在前 5 档深度与极乐观 `0.75bps/leg` 三腿费率下 best cycle 仍持续费后为负；它没有保住足以进入 `P2 / paper-prep` 的可交易 after-cost pocket，本轮应直接收口 `background/P0`，保留为 quote-fragmentation / quote-health 指标线索，而不是继续当前 front object。

## 对 runtime 的直接影响
- `Fresh intake slot`：清空当前 front object
- `Surviving candidate slot`：清空，follow-up 预算归零
- `Rank 421`：转入 `Background pool`
- `cycle_plan item1`：标记 `done`

## 本轮产出
- 内部日志：本文
- 新 reader-facing 结论：有（对象层级收口到 `background/P0`）
