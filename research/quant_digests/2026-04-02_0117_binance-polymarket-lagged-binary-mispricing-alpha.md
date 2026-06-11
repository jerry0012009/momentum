# 别把这份 2026 cross-market repo 只读成 RL demo：对 short-cycle desk，更该先测的是「Binance impulse × Polymarket 15m lagged binary mispricing」这条完整 raw alpha

- 时间：2026-04-02 01:17 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `TRAINING_JOURNAL.md` + `run.py` + `strategies/base.py` + `helpers/polymarket_api.py` + `helpers/binance_futures.py` + GitHub API metadata + 公共 API live snapshot）
- 主题类型：raw alpha
- 基础 alpha：**快市场 Binance futures 的超短冲击 / order-flow 状态，会先于慢市场 Polymarket 15m crypto binary 价格调整；因此可交易的本体不是“RL”本身，而是 `fast-market fair value - slow-market quoted probability` 的滞后错价。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/lead-lag/relative-value/binary-markets/polymarket/binance-futures/order-flow/cvd/microstructure/15m/5m/3m/1m/repo/public-data/external-data/cost
- 证据类型：repo source + GitHub API metadata + live public endpoint snapshot（repo-based）

## 1. 这次看了什么
这轮看的是一个 **2025-12-29 创建、2026-03-31 仍有高信号活跃度、GitHub 约 366 stars** 的新仓库：`humanplane/cross-market-state-fusion`。

repo headline 写的是 **RL agent fusing real-time Binance futures data into Polymarket prediction markets**，但对我们 desk 来说，最值得 intake 的不是“PPO + MLX + 苹果芯片在线训练”这层外壳，而是它已经把一条 **可独立复现、数据公开可拿、天然对应 15m 持有期** 的 raw alpha 骨架摆出来了：

1. Binance futures 这条快腿提供 `1m/5m/10m return`、`trade_flow_imbalance`、`CVD`、`large trade flag`、`realized vol`；
2. Polymarket 这条慢腿提供实时 binary orderbook / mid / spread / depth；
3. 同一资产（BTC / ETH / SOL / XRP）的 15m binary 合约在信息吸收速度上比 Binance futures 更慢；
4. 于是可以把问题重写成：**“Binance 已经告诉你 fair probability 应该往哪边偏，但 Polymarket 报价还没 fully 跟上。”**

翻成人话：
**别先学它怎么训 RL；先测 `Binance 先动 → Polymarket 15m up/down 概率滞后调整` 这条跨市场错价能不能独立赚钱。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮的 base alpha 很清楚：

- 不是 filter；
- 不是 regime gate；
- 不是“prediction market 解释学”；
- 也不是“RL 学到了什么”的黑箱故事；
- 而是 **same-asset cross-market lead-lag mispricing**。

更具体地说：
**用 Binance futures 的超短价格 / order-flow 冲击去估一个“当前 15m 结算事件的公平上行概率”，然后和 Polymarket 的 `UP` token 中价比较；若 fair probability 显著高于当前 quoted probability，就买 `UP`，反之买 `DOWN`。**

所以这轮应被定性为：
- `raw alpha`
- `cross-market / relative-value / lead-lag`
- 只是交易载体从 spot / perp spread 换成了 **15m binary market**。

## 3. 为什么这轮值得 intake，而不是继续补第 N 条泛 lead-lag
最近池子里已经有不少 BTC→ALT、ETF→BTC、CEX→DEX、spot→futures 的 lead-lag / relative-value 材料；这轮还值得写，有三个原因：

1. **结算钟更硬。** Polymarket 的 15m crypto up/down 合约是明确 hard-expiry 的 binary 载体，不是无限持仓；entry / exit / timeout / near-expiry veto 都天然清晰。
2. **慢腿公开且可实时拿。** `gamma-api.polymarket.com` + `wss://ws-subscriptions-clob.polymarket.com/ws/market` 就能抓 active markets 和 L2 订单簿，不用私有数据。
3. **它不是只能做方向猜测。** 对 desk 更有价值的读法，是把 repo 从 “train PPO policy” 降维成 “估 fair value → 做 quoted-probability mispricing”。这比直接复刻黑箱 agent 更快得到 first verdict。

如果要一句话概括这轮为什么比继续补一个 shared gate 更值钱：
**因为它本身就是一条能单独下单、能明确定义成本与 timeout 的 raw alpha，而不是只给现有策略再加一个 veto。**

## 4. 最值得记住的硬数据
### 4.1 repo 自报结果很夸张，但最值得偷的是“错价骨架”，不是收益数字
README / TRAINING_JOURNAL 里给了几组很醒目的数字：

- **Phase 4（share-based PnL）**：`$3,392 PnL`，对应 `170% ROI`
- **Phase 5（LACUNA temporal architecture）**：`~$50K PnL`，`2,500% ROI`
- **Phase 5 duration**：`10+ hours`
- **Phase 5 trades**：`34,730`
- **Win rate**：仅 `23.3%`
- **By asset**：BTC 一条腿就贡献了 `+$40,088`

这些数字明显不能直接当 live edge，相反更该当 warning：
- 全是 **paper trading**；
- 假设接近 mid fill；
- repo 自己也写了 live 可能要打 **20%~50% performance degradation**。

但这些结果仍然提供了一个有用信号：
**即使 win rate 只有 23%，只要 binary 份额定价的不对称 + 慢腿报价滞后是真实的，低胜率也可以赚钱。**

### 4.2 这条线的状态空间已经被 repo 明确拆给你了
repo 没有含糊其辞，它把 state 直接写成 **18 维**：

- Binance futures 动量：`returns_1m`, `returns_5m`, `returns_10m`
- Binance futures order flow：`trade_flow_imbalance`, `cvd_accel`
- Polymarket CLOB：`best_bid`, `best_ask`, `spread`, `order_book_imbalance_l1/l5`
- microstructure：`trade_intensity`, `large_trade_flag`
- regime / timing：`vol_regime`, `trend_regime`, `time_remaining`

这对我们很关键，因为它说明第一轮根本不需要 PPO：
**先做一个 lagged fair-probability baseline（logit / isotonic / ridge / simple rules）就能 honest 地回答“slow-market mispricing 到底存不存在”。**

### 4.3 公开数据现在就拿得到
我直接用 repo helper 做了 live snapshot，当前时刻就能抓到 **4 个 active 15m crypto markets**：

- BTC：`UP 0.545 / DOWN 0.455`
- ETH：`UP 0.495 / DOWN 0.505`
- SOL：`UP 0.540 / DOWN 0.460`
- XRP：`UP 0.550 / DOWN 0.450`

并且同一时刻 Binance futures 公开接口能同步给出 ultra-short returns，例如：

- BTC：`ret_1m = +0.0231%`，`ret_5m = -0.4712%`
- ETH：`ret_1m = +0.2620%`，`ret_10m = +0.4964%`
- SOL：`ret_5m = -0.8626%`

这不代表“单点 snapshot 已经证明有 edge”，但它证明了更重要的一件事：
**数据接线今天就是通的，第一版最小实验不需要等私有 feed。**

## 5. repo 最适合 desk 的读法：别先复刻 PPO，先复刻 fair-value 错价
repo 原始做法是 PPO agent；但更适合我们 desk 的 side branch 其实是：

1. 用 Binance 快腿特征先估 `p_fair_up`；
2. 再和 Polymarket 当前 `p_mid_up` 比较；
3. 只交易 `edge = p_fair_up - p_mid_up` 足够大的时点；
4. 并且把 near-expiry / spread / stale quote / depth imbalance 写成 execution veto。

所以最实用的简化版可以直接写成：

- **signal**：
  - `score_t = w1*z(ret_1m) + w2*z(ret_5m) + w3*trade_flow_imbalance + w4*z(cvd_accel) + w5*large_trade_flag*sign(trade_flow)`
  - 再把 `score_t` 映射成 `p_fair_up`
- **entry**：
  - 若 `p_fair_up - p_mid_up > entry_edge`，买 `UP`
  - 若 `p_fair_up - p_mid_up < -entry_edge`，买 `DOWN`
- **exit**：
  - edge 回落到 `exit_edge`
  - 或出现 opposite signal
  - 或剩余时间 < `30~60s`
- **position sizing**：
  - 按 `|edge|`、spread、time remaining、盘口厚度，从 `0.25x / 0.5x / 1.0x` 分层
- **risk**：
  - 每资产每个 15m market 最多一笔
  - 同时最多 2~4 个市场敞口
  - stale data > `2s` 不开仓
  - spread > `2~3c` 不追
- **cost**：
  - taker / maker fee
  - bid-ask spread
  - fill slippage
  - expiry 前强平 / 未成交 / legging 风险

这就已经是一条完整策略，不再依赖“RL 学出来什么”这个黑箱前提。

## 3.5 策略拆解（必填）
- **方向属性：** same-asset cross-market / lead-lag / relative-value
- **基础 alpha：** Binance futures 冲击先于 Polymarket 15m binary quoted probability 调整
- **regime：** 高成交 / 低延迟 / spread 不过宽 / 距离到期仍足够时更值得开机
- **filter / veto：** stale quote veto、near-expiry veto、宽 spread veto、top-of-book 反向失衡 veto
- **risk / sizing / execution overlay：** `edge` 分层仓位、单 market 单次开仓、临近到期强制平仓、maker/taker fallback、depth-aware size cap

## 6. 和当前 `1m / 3m / 5m / 15m` 的关系
### 6.1 它天然是 `15m` 主信号，`1m/3m/5m` 做快腿特征与执行
这条线的结算对象本身就是 **15m binary**，所以最自然的映射不是把它硬压成 1m 高频主 alpha，而是：

- `15m`：交易对象 / 持有期 / timeout clock
- `5m`：快腿 return / flow 聚合与状态刷新
- `3m / 1m`：更快的 impulse 捕捉、edge persistence 检验与 child-order timing

换句话说：
**这里的 1m/3m 不是另起一套 alpha，而是给 15m main trade 提供更及时的 fair-value 更新。**

### 6.2 它也能服务纯 crypto desk，而不一定要求真正下 Polymarket
即使最后不做 Polymarket 实盘，这条材料仍有 desk 价值，因为它等价于在问：
**“当一个慢市场价格载体吸收同资产信息更慢时，快腿冲击能否被转写成可执行的概率错价？”**

这层读法可迁移到：
- CEX vs DEX
- spot vs perp
- primary venue vs lagging venue
- options micro-binary / event contracts vs spot/perp

所以它补的不只是一个特定 venue idea，也是一种 **probability-marketized lead-lag 壳子**。

## 7. 数据源、公开性、更新频率、最小可复现实验口径
### 7.1 数据源
- **Polymarket Gamma API（公开）**：拿 active market / event / slug / market metadata
- **Polymarket CLOB WebSocket（公开）**：拿 `book` / `price_change` / best bid/ask / depth
- **Binance USDⓈ-M Futures aggTrade stream（公开）**：约 `100ms` 聚合成交
- **Binance Futures REST（公开）**：`openInterest`、`premiumIndex`、`1m klines`

### 7.2 更新频率
- Polymarket market websocket：事件驱动，近实时
- Binance aggTrade：文档写明 **100ms 聚合 trade stream**
- Binance open interest REST：按请求拉取，repo 默认约每 `10s` 刷新
- Binance klines：`1m` bar

### 7.3 最小可复现实验口径
第一轮不要做 RL，也不要做 full online learning；先做一版最小 honest backtest：

- **资产**：BTC / ETH / SOL / XRP
- **样本**：最近 `2~4` 周的 Polymarket 15m crypto markets + Binance futures 同步数据
- **标签**：市场到期时 `UP/DOWN` binary outcome，或更保守地用中途 probability reversion / convergence 做 first-stage label
- **特征**：`ret_1m`, `ret_5m`, `ret_10m`, `trade_flow_imbalance`, `cvd_accel`, `large_trade_flag`, `spread`, `ob_imbalance`, `time_remaining`
- **模型**：先从 `logit / ridge / isotonic / threshold rule` 开始
- **执行**：必须用 one-tick / one-sample lag，不能 same-tick 幻觉成交
- **成本**：至少扣 spread + fee；第二轮再补 market impact

## 8. 下一步怎么测
1. **先做 non-RL baseline。** 用 `Binance features -> fair probability`，直接检验 quoted-probability mispricing 是否存在。
2. **先做 edge decile 曲线。** 看 `p_fair_up - p_mid_up` 分位越极端，最终到期正确率 / 中途收敛收益是否单调上升。
3. **把 timing 单独 ablation。** 比较 `>10m`、`5~10m`、`<5m` 三个 time-to-expiry bucket，确认 edge 是不是只活在 early / mid window。
4. **把 spread veto 单独测。** 很多 paper edge 会死在宽 spread；这条线必须先回答 `edge/spread ratio` 是否够厚。
5. **做 same-asset 对照。** 同时跑“直接做 Binance 方向”与“做 Polymarket 错价”两版，确认真正的增益来自 slow-market lag，而不只是 Binance 本身的 continuation。
6. **若 baseline 存活，再上 PPO。** 否则直接上 RL 只是在用复杂度掩盖“本体 edge 可能不够厚”。

## 9. 风险与保留意见
1. **repo 结果极可能乐观。** 它自己也承认 live trading 会因 latency / slippage / market impact 明显衰减。
2. **15m binary 市场容量有限。** edge 可能存在，但可容纳资金未必大。
3. **share-based PnL 会鼓励低价合约。** 这符合 binary economics，但也可能放大 tail-risk / fill-risk / quote staleness 风险。
4. **Paper trading 的 mid fill 假设很危险。** 若真实执行主要吃 ask / bid，很多“看起来够厚”的 edge 会被 spread 吃掉。
5. **repo 里 Phase 5 的收益高度集中在 BTC。** 说明 shared policy 未必稳健迁移到其他资产。

所以我对它的定位是：
**高信号 repo intake，base alpha 很清楚；但 first verdict 必须靠非 RL、cost-first、lagged execution 的最小实验来给。**

## 10. 来源
- **Author / Maintainer：** `humanplane`
- **Year：** 2025-2026
- **Title：** *Cross-Market State Fusion*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/humanplane/cross-market-state-fusion>
- **Repo URL：** <https://github.com/humanplane/cross-market-state-fusion>
- **GitHub API metadata：** <https://api.github.com/repos/humanplane/cross-market-state-fusion>
- **Presentation PDF（repo 内）：** <https://github.com/humanplane/cross-market-state-fusion/blob/master/cross-market-state-fusion.pdf>
- **Training journal：** <https://github.com/humanplane/cross-market-state-fusion/blob/master/TRAINING_JOURNAL.md>
- **Polymarket docs / readable URL：** <https://docs.polymarket.com/market-data/fetching-markets>
- **Polymarket market websocket docs：** <https://docs.polymarket.com/market-data/websocket/market-channel>
- **Binance futures aggTrade docs：** <https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/Aggregate-Trade-Streams>
- **Binance open interest docs：** <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest>

## 11. 一句话结论
**这份 2026 repo 最值钱的不是“RL 在 prediction markets 上赚了多少钱”，而是它把一条可公开取数、天然对应 15m、可直接写成 entry/exit/sizing/risk/cost 的 raw alpha 摆在桌上：`Binance fast impulse -> Polymarket slow probability catch-up`。对 desk，第一步该复现的是这条错价，不是 PPO。**
