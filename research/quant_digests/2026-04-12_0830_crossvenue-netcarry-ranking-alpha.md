# 别把这份 funding+basis monitor 只读成仪表盘：对 short-cycle desk，更该先测的是「cross-venue net carry differential × executable pair ranking」这条 raw alpha
- 时间：2026-04-12 08:30 UTC
- 类型：GitHub repo + 公共 live API 快检
- 主题类型：raw alpha
- 基础 alpha：**同一标的 perpetual 在不同 venue 上会同时出现 funding、mark/index basis、盘口深度与手续费结构的错配；真正可交易的不是“哪边 funding 高”，而是 `max(net carry) venue vs min(net carry) venue` 的对冲配对，也就是 `funding diff + basis diff - fees - slippage` 最大的那一对。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/relative-value/carry/funding/basis/cross-venue/perpetuals/net-carry/execution-capacity/slippage/fee/ranking/binance/hyperliquid/dydx/30s/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：源码审计 + 公共 live snapshot probe

## 1. 这次看了什么
这轮看的是 **Razrocks (2026), _Funding-Basis---Strategy-Monitor_**。

表面上它是个 **Binance / Hyperliquid / dYdX 的 funding+basis carry dashboard**，但对我们 desk 真正有价值的，不是看板，而是它把一条可复现的 cross-venue raw alpha 写得很清楚：

> **不是单看某个 venue 的 funding 高不高，而是对同一标的，把每个 venue 的 `net carry` 算干净，再做 `最高净 carry venue` 对 `最低净 carry venue` 的相对价值配对。**

翻成人话：
- 如果 A 所短 perp 更赚钱、B 所做反向 hedge 更便宜，
- 而且两边盘口都吃得下、成本没把 edge 吃光，
- 那真正该交易的是 **venue pair**，不是单腿 funding 观点。

这和我们最近看的两类材料都不一样：
- 它不是 `small-cap cross-venue quote gap` 那种 **秒级 BBO 错位回归**；
- 也不是 `same-expiry futures basis differential` 那种 **同期限期货跨所收敛**；
- 它更像 **perp 层的 cross-venue carry relative value**：funding、basis、手续费、slippage、容量一起进分子分母，最后只留下可执行 pair。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的，不是 dashboard 外壳，而是它把「**同标的跨 venue 的净 carry 差**」写成了一条能独立复现的 raw alpha：先分别估每个 venue 的 `funding_apr + basis_apr - fee_cost - slip_cost`，再交易 `max-net-carry` 对 `min-net-carry` 的对冲 pair。
- **一句话证明方式：** 结论来自源码公式、配置假设、订单簿容量模拟，以及我对 Binance / Hyperliquid / dYdX 公共 API 的当次 live 快检，不是 README 宣传词。

源码里最关键的三步是明牌写出来的：
1. **单 venue carry leg**
   - `funding_apr = funding_rate * (seconds_per_year / funding_interval_seconds)`
   - `basis_apr = ((mark/index) - 1) * (seconds_per_year / basis_horizon_seconds)`
   - `net_carry = funding_apr + basis_apr - fee_cost_apr - slippage_cost_apr - borrow_apr`
2. **方向不是主观判断，而是 funding sign 决定**
   - `funding_rate > 0 -> SHORT earns`
   - `funding_rate < 0 -> LONG earns`
3. **跨 venue pair 不是两两枚举拍脑袋，而是直接选**
   - `earn = argmax(net_carry)`
   - `hedge = argmin(net_carry)`
   - `pair_expected = funding_diff + basis_diff - total_fees - total_slippage`

也就是说，这条 alpha 的 base 不是“预测涨跌”，而是：

> **同一资产在不同 perp venue 上的 carry economics 本来就可能不同；只要这个差异在成本后仍显著，而且书上吃得下，就能形成一条 cross-venue raw alpha。**

## 3. 这轮最有用的几个硬信息
### 3.1 repo 自带的可迁移结构
`config.yaml` 直接把短周期 desk 最关心的几个现实问题写死了：
- polling：`30s`
- orderbook polling：`5s`
- depth：`20` 档
- 默认 venue：Binance / Hyperliquid / dYdX
- 默认 capacity tier：`5 / 10 / 25 bps`
- 默认 screening：
  - `min_net_carry_apr = 5%`
  - `min_quality_score = 40`
  - `min_capacity_10bps_usd = 5000`

这说明它不是“只算理论 funding”的 notebook，而是已经把 **能不能成交** 当成主约束。

### 3.2 repo 对“假机会”的处理是对的
这份仓库最值得学的不是收益数字，而是它知道哪些 edge 最容易是假的：
- `Quality Score`：惩罚 funding volatility、basis volatility、极端 z-score、OI shock
- `Trap Tags`：`Funding spike / OI shock / Carry unstable / Basis inversion / Crowded`
- `capacity_at_slippage()`：不是只看 top-of-book，而是看 **在固定 slippage 容忍下真实能吃多少美元 notional**

这很适合我们 desk，因为 cross-venue carry 最怕两类误判：
1. **paper edge 很大，但薄书一打就没了**
2. **funding/basis 看起来便宜，其实已经是拥挤或失稳状态**

### 3.3 我做的当次 live BTC 快检
我直接用三所公共 API 拉了当次 `BTC` perp 快照，并按 repo 公式手动重算了 `25k USD` 规模下的单 venue net carry 与 best pair。

当次快检（2026-04-12 08:30 UTC 左右）有三个很重要的点：

- **1 天持有假设下，三所单腿净 carry 全是负的**：
  - Binance：约 **`-51.96% APR`**
  - Hyperliquid：约 **`-34.38% APR`**
  - dYdX：约 **`-42.05% APR`**
  - 这不是说“不能做”，而是说 **如果你把 round-trip fee/slippage 全摊到 1 天里，成本会极重**。

- **30 天持有假设下，净 carry 排名明显改善**：
  - dYdX：约 **`-2.20% APR`**
  - Hyperliquid：约 **`-15.75% APR`**
  - Binance：约 **`-23.74% APR`**
  - 重点不是绝对值漂亮，而是 **hold horizon 决定 cost amortization，pair ranking 会变**。

- **best pair 的 30 天口径 edge 变成正的**：
  - `earn venue = dYdX`
  - `hedge venue = Binance`
  - `edge_apr ≈ +21.54%`
  - `pair_expected_apr ≈ +19.59%`
  - `pair_capacity ≈ 177,880 USD`（按 10bps 容量约束）

这组数最关键的启发是：

> **同一个 snapshot，在 1 天口径和 30 天口径下，edge 可以从“看起来不值得”变成“pair 级别可讨论”。所以这条 alpha 不是纯秒级/分钟级 book，也不是纯 8h funding book，而是一个“执行 horizon 很关键”的 carry RV。**

## 4. 为什么它和当前项目直接相关
这条线对 `momentum` 的价值很直接，因为我们当前明确想补的是：
- raw alpha 素材池
- relative value / stat-arb / carry / funding / basis 方向
- 能快速做 `1m/3m/5m/15m` 最小实验的结构

这份 repo 刚好补了一个我们还没系统化的空白：

### 4.1 它服务于 raw alpha，不是只当 overlay
虽然它有 quality score、trap tags 这类 filter 成分，但 **base alpha 本体是清楚的**：
- **交易对象：** 同一资产的多 venue perp
- **交易逻辑：** 做多最便宜的 carry side、做空最贵的 carry side
- **收益来源：** funding/basis economics 的 venue-level 错配在一段持有期内兑现或收敛

所以它不是纯 filter，不是纯 regime，不是只会说“别做”。

### 4.2 它天然适合短周期 desk 做最小实验
因为它的数据全是公开且高频可取：
- Binance：`premiumIndex / openInterest / depth`
- Hyperliquid：`metaAndAssetCtxs / l2Book`
- dYdX：`perpetualMarkets / orderbooks`

repo 默认就是：
- `30s` 拉 funding/mark/index/OI
- `5s` 拉 orderbook

所以你完全可以把它压缩成：
- `30s` 原始 event stream
- 然后聚合到 `1m / 3m / 5m / 15m`
- 再看 edge persistence、容量稳定性、与 funding 窗口的关系

### 4.3 它和我们已经写过的主题互补，而不是重复
- 不是 `same-contract cross-venue quote gap`：那条线主要赚 **BBO 价差瞬时收敛**。
- 不是 `same-expiry futures basis differential`：那条线主要赚 **跨所期货曲线偏离**。
- 这条线赚的是 **venue-level net carry ranking**，而且把 **funding + basis + fees + slippage + capacity** 串成一个统一分数。

## 5. 策略拆解（必填）
- 方向属性：**cross-venue / relative-value / carry / stat-arb / market-neutral**
- 基础 alpha：**同一标的 perp 在不同 venue 的净 carry（funding+basis-成本）会出现持续性差异；做 `最高净 carry venue` 对 `最低净 carry venue` 的配对，是一条可独立成立的 raw alpha。**
- regime：
  - 更适合 funding 机制差异明显、basis 偏离不完全同步、流动性分层清楚的时段
  - 在拥挤或 funding spike 时要更谨慎，不能把极端值误当稳定 carry
- filter / veto：
  - `quality_score >= 40`
  - `capacity_10bps_usd >= 5000`
  - `trap_tags` 不能过多
  - `funding_only=False` 时 basis 才一起参与排序
- risk / sizing / execution overlay：
  - 仓位上限取 pair 两边 10bps 容量较小者
  - horizon 必须单独扫描（`1d/3d/7d/30d` 至少四档）
  - 需要事件止损：edge collapse、trap tag 激增、数据 stale、下一 funding 预测翻向

## 6. 可复刻的最小实验
### 6.1 数据源 / 公开性 / 更新频率
- **Binance**：`/fapi/v1/premiumIndex`、`/fapi/v1/openInterest`、`/fapi/v1/depth`
- **Hyperliquid**：`POST /info` 的 `metaAndAssetCtxs`、`l2Book`
- **dYdX**：`/v4/perpetualMarkets`、`/v4/orderbooks/perpetualMarket/{market}`
- **公开性**：公开，无需 key
- **更新频率**：分钟内可多次刷新；repo 默认 `30s` + `5s` 级别

### 6.2 最小信号定义
对每个 symbol、每个 venue，在每个时间点计算：
1. `funding_apr`
2. `basis_apr`
3. `slippage_bps(size)`
4. `net_carry_apr(size, hold_days)`

然后在同一时刻做：
- `earn = argmax(net_carry_apr)`
- `hedge = argmin(net_carry_apr)`
- `edge_apr = earn.net_carry_apr - hedge.net_carry_apr`
- `pair_expected_apr = funding_diff + basis_diff - fees - slippage`

### 6.3 最小可复现实验口径
- 标的：先从 `BTC / ETH / SOL` 开始
- 频率：先存 `30s` 原始快照，再聚合到 `1m / 3m / 5m / 15m`
- 仓位：先看 `10k / 25k / 50k` 三档
- 持有：至少扫 `1d / 3d / 7d / 30d`
- admission：
  - `pair_expected_apr > 0`
  - `pair_capacity_usd >= size`
  - `quality_min >= 40`
  - `max(trap_tags_union) <= 2`

### 6.4 先做什么，不要做什么
- **先做：** event-study，统计 edge 出现后在未来 `30m / 1h / 4h / 8h / 1d` 是否持续、是否塌缩、是否跨 funding window 兑现。
- **不要先做：** 直接把瞬时 leaderboard 当生产信号，因为没有历史 persistence 和成交路径，你只是在盯看板，不是在测 alpha。

## 7. first verdict
我的 first verdict 是：

> **这是一个合格的 raw alpha intake，而且很适合当前 desk。**

原因不是它已经是完整生产策略，而是：
- base alpha 说得清；
- 公开数据随手能取；
- 既能做 `30s/1m` 的高频 event-study，也能做 `5m/15m` 的低频聚合验证；
- 跟我们现有的 quote-gap / basis / funding 线形成互补。

但也要明确：
- **它不是“现在就能直接跑实盘”的完整策略**，因为 repo 没有真正的 entry/exit/execution book；
- **它更像一个 pair-ranking alpha kernel**，后面需要我们自己补：
  - edge persistence
  - horizon selection
  - maker/taker 现实成交
  - next-funding 前后 path dependency

## 8. 风险与保留意见
- **dYdX 的 basis 被设为 0**（oracle=mark），这让三所比较天然不对称；做研究时要明确这是 API 结构差异，不是经济现实完全没有 basis。
- **predicted funding ≠ realized funding**，尤其 dYdX 用的是 next funding prediction；如果直接把它当已锁定 carry，结果会偏乐观。
- **basis annualization 对 horizon 非常敏感**。repo 默认拿 `1 day` 年化 basis，这对短 hold 来说偏激进，对长 hold 又可能偏粗糙。
- **同一 snapshot 下，hold_days 改一下，pair ranking 就会变。** 这既是优点也是坑：说明 alpha 真实存在，但也说明它极依赖持有框架，不能把 scanner 排名直接当万能答案。
- **最容易犯的错**：把 `edge_apr > 0` 误当成“马上值得打”。真正该关心的是：edge 持续多久、能否跨 funding 窗、两腿容量是否同步、执行后还能剩多少。

## 9. 下一步怎么测
1. **先把 30s 快照存下来，别急着做策略。**
   - 至少存 `BTC/ETH/SOL` 三个 symbol、三所快照、连续 `7~14d`。
2. **做 edge persistence study。**
   - 看 `edge_apr > 10% / 20% / 30%` 出现后，未来 `30m / 1h / 4h / 8h / 1d` 的衰减曲线。
3. **把 hold_days 从配置常数改成研究维度。**
   - 这条线不是固定 30 天才有意义；要明确它更像 `intra-day carry RV`、`pre-funding hold` 还是 `multi-day pair carry`。
4. **做 maker/taker 成本矩阵。**
   - 至少比较 `taker/taker`、`maker/taker`、`maker/maker proxy`，不然很多正 edge 会只是纸面现象。
5. **单独加一个“funding-only vs funding+basis”对照。**
   - 验证真正贡献 edge 的到底是 funding 差、basis 差，还是两者叠加。
6. **如果 persistence 很短，就把它并入现有 cross-venue fast-close book；如果 persistence 能跨 funding window，就升级成独立 carry RV 策略。**

## 10. 来源
1. **Razrocks. (2026). _Funding-Basis---Strategy-Monitor_. GitHub repository.**
   - Readable URL: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor`
   - Repo URL: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor`
2. **本轮实际审计文件**
   - README: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/blob/main/README.md`
   - Config: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/blob/main/config.yaml`
   - Cross-venue core: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/blob/main/core/cross_venue.py`
   - Metrics core: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/blob/main/core/metrics.py`
   - Execution core: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/blob/main/core/execution.py`
   - Venue connectors: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/tree/main/connectors`
   - Tests: `https://github.com/Razrocks/Funding-Basis---Strategy-Monitor/tree/main/tests`
3. **本轮本地源码快照**
   - local clone commit: `0668422a1f4539ca19fcf67caa57b38bc93dacaa`
   - commit time seen locally: `2026-02-22 19:32:05 -0500`
4. **本轮 live public probe 所用公开接口**
   - Binance: `https://fapi.binance.com/fapi/v1/premiumIndex`, `https://fapi.binance.com/fapi/v1/openInterest`, `https://fapi.binance.com/fapi/v1/depth`
   - Hyperliquid: `https://api.hyperliquid.xyz/info`
   - dYdX: `https://indexer.dydx.trade/v4/perpetualMarkets`, `https://indexer.dydx.trade/v4/orderbooks/perpetualMarket/BTC-USD`

## 11. 和当前短周期（1m/3m/5m/15m）的关系
如果只把它看成“30 天 carry 监控器”，会低估它；如果硬把它说成秒级 quote-gap，又会说过头。

更准确的 desk 定位是：
- **底层采样频率**：`30s/5s`
- **研究聚合频率**：`1m / 3m / 5m / 15m`
- **收益兑现频率**：可能从 `数十分钟` 到 `跨 funding 窗` 都有

所以它很适合作为：
1. `1m/3m` 的 **edge-appearance / persistence 事件研究**；
2. `5m/15m` 的 **carry RV 排名与持有窗测试**；
3. 未来和现有 quote-gap / funding / basis 主题做 **router**：不同 edge persistence 走不同执行壳。