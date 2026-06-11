# Rankless fresh intake first verdict — anchor-open displacement × minute-vol breakout continuation

- Time: 2026-04-09 22:49 UTC
- Target: `research/quant_digests/2026-04-09_2235_anchor-open-vwap-sigma-continuation-alpha.md`
- Action type: `fresh intake first verdict`
- Verdict: `background / P0`

## What I checked
只做了这个 intake 的最小 honesty / portability 收口：
1. 重读 digest 里的主张与保留意见；
2. 直接核 repo 源码 `prepare_indicators.py` 与 `backtest_strategy.py`；
3. 对照 Concretum writeup 的业绩描述，看 repo 真实可复刻的规则骨架到底是什么。

## Source-grounded findings
### 1) 这条线最核心的“alpha 定义”其实强绑定 equity cash-session 微结构
源码里 `sigma_open` 不是泛化的“分钟波动阈值”，而是：
- 先按日内真实 cash open（9:30）定义 `min_from_open` / `minute_of_day`；
- 再对每个 `minute_of_day` 取过去约 `14` 天该同一分钟的 `move_open` 滚动均值；
- 最后把这个移位后的值当作 `sigma_open` 用来画 `UB/LB`。

也就是说，它不是一个在任意 24/7 市场天然成立的 raw alpha，而是一个**建立在“固定真实开盘 + 同一分钟历史噪音分布稳定”前提上的 session 标准化 breakout 壳**。

### 2) `sigma_open` 口径本身更像经验阈值，不是独立 continuation pocket 的强证明
`prepare_indicators.py` 里：
- `move_open = abs(close / open_price - 1)`
- `sigma_open` 实际来自 `minute_groups['move_open'].transform(lambda x: x.rolling(window=14, min_periods=13).mean()).shift(1)`

这更像“过去同一分钟离开 open 的平均绝对幅度”，不是通常意义上的条件波动率估计。它当然能当 threshold 用，但**它说明的是何时算异常位移，不足以单独证明 crypto 里也存在一个独立、稳健、可兑现的 session continuation alpha**。

### 3) 交易逻辑本体依然是 session breakout + VWAP 同向过滤
`backtest_strategy.py` 的核心入场就是：
- `close > UB` 且 `close > vwap` 做多；
- `close < LB` 且 `close < vwap` 做空；
- 每 `30` 分钟才允许调仓一次；
- 信号反转或收盘强平；
- 仓位按日频 `spy_dvol` 做 `vol_target`，并设 `max_leverage = 4`。

因此 repo 最扎实的部分其实是一个**完整 session breakout shell**：entry/exit/sizing/risk 都写出来了；但 raw alpha 若抽掉美股 cash open、同分钟噪音模板、SPY 特有时段流动性结构后，还剩多少，不在当前证据里。

### 4) 成本与执行 realism 也没有给 crypto portability 加分
源码成本口径是 SPY 每股佣金：
- `commission = 0.0035`
- `min_comm_per_order = 0.35`

这和 crypto 的 maker/taker、资金费、滑点、24/7 流动性断层都不是一个世界。也就是说，**当前对象最值钱的是 strategy shell，不是已经被诚实验证过的 crypto continuation alpha**。

## Decisive blocker
单一 decisive blocker：**alpha 本体过度依赖 equity-style open anchor + same-minute historical displacement template；移到 crypto 后，当前证据只能支持“值得研究的 session breakout shell”，不能支持“已经保留独立 continuation pocket 的 fresh intake”**。

这不是“再补一点 anchor ranking 就行”的轻微缺口，因为当前 raw evidence 连 pocket 是否独立存在都没站稳；继续把它留在前排会把一个 session-specific 壳误判成可迁移 alpha。

## System-changing conclusion
`anchor-open displacement × minute-vol breakout continuation` 在当前证据下更像 **equity cash-session 专属的 standardized breakout shell**，不是已经在 crypto / desk 可迁移口径里保住独立 raw alpha 的对象；因此 fresh intake first verdict 应直接收口为 `background / P0`，不升 `P1`。

## State updates required
- 当前小点 `status -> done`
- 当前小点 `result -> 该对象因 session-anchor portability 与 same-minute sigma 定义过度绑在 equity open，首判收口为 background / P0`
- `Fresh intake slot` 顺位前移到下一个尚未首判对象：`research/quant_digests/2026-04-09_2146_postcost-funding-basis-deltaneutral-alpha.md`
- `Background pool.latest_parked` 同步写入本次 verdict
