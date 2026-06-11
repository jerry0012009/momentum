# 别把这份 2026 cross-exchange repo 只当“搬砖脚本”：对 desk 更该先测的是「same-contract perp quote gap × maker-one-leg / taker-one-leg」完整 raw alpha

- 主题类型：raw alpha
- 基础 alpha：同一标的、同一类永续合约在不同 venue 的最优买卖盘会短时失衡；当 **Lighter bid 明显高于 EdgeX maker-buy 成本**，或 **EdgeX ask 明显高于 Lighter maker-buy 成本** 时，后续更可能向跨 venue 收敛方向回落
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但对成交细节和单腿风险非常敏感
- 时间：2026-03-31 19:29 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/same-underlier/same-contract/perp-perp/quote-gap/maker-taker/edgex/lighter/1m/3m/5m/repo/public-data/execution/cost/risk
- 证据类型：2026 GitHub 新仓库 source audit（`strategy/edgex_arb.py` + `strategy/order_manager.py` + `strategy/position_tracker.py` + `strategy/data_logger.py` + `exchanges/edgex.py` + `exchanges/lighter.py`）+ Lighter 公共 `orderBooks` endpoint live sanity check

## 1. 这次看了什么

这次主材料不是论文，而是一份 **2026 新 repo：`wavyjay1/cross-exchange-arbitrage`**。

它表面上是一个“EdgeX 与 Lighter 之间做 cross-exchange arbitrage 的机器人”，但如果按我们当前 desk 的优先级来读，真正值得单独拎出来进素材池的，不是“跨所机器人”这几个字，而是它给了一条相当完整、而且非常适合短周期 desk 做最小实验的 raw alpha 壳：

**同一标的、同一类 perp，在两个 venue 的 BBO 短时错位；在一个 venue 争取 maker 进场，在另一边用 taker 对冲，赚的是跨 venue quote gap 的回收。**

翻成人话：
这不是长周期 funding 套利，也不是 pair formation，不是“预测涨跌”，而是更原子的相对价值口袋：

- 资产相同；
- 合约类型相同；
- 风险中性方向很清楚；
- 边来自 **venue A 与 venue B 的盘口不同步**。

这类题材和我们最近写的 spot-perp / funding / stablecoin / options relative value 不一样的地方在于：

**这里的 base alpha 更短、更薄、更执行驱动。**

## 2. 为什么它值得进当前研究池

最近几轮 digest 已经补了很多：

- spot-perp basis / premium reversion；
- funding carry；
- stablecoin parity；
- pairs / basket stat-arb；
- options parity / box / butterfly。

但当前池子里还缺一条非常“台面下”、却很像真实交易 desk 的原始 alpha：

**same-contract、cross-venue、盘口级价差回收。**

这份 repo 值得补，有 4 个原因：

1. **base alpha 很清楚**：不是 filter，不是 overlay，就是同一合约跨 venue BBO 错位；
2. **是完整策略壳**：有 entry、hedge、timeout、position cap、日志；
3. **天然更接近 `1m / 3m`**：不是等 K 线走形态，而是等盘口 pocket；
4. **非常适合做最小 falsification**：只要能持续录两边 BBO，就能先回答“机会有没有厚到足以盖过 taker + legging”。

## 3. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = 同一资产、同一类永续合约在两个 venue 的最优买卖盘会短暂失衡；当这个 gap 大到足以覆盖 one-leg maker + one-leg taker 的真实成交壳时，随后更可能向跨 venue 收敛方向回落。**

所以它本质上是：

- `relative-value`
- `stat-arb`
- `same-underlier, same-contract, cross-venue`
- 但交易对象不是 spot-vs-perp，也不是 two-coin pair，而是 **perp-vs-perp 的盘口错价**。

## 4. 核心来源

### 4.1 主仓库
- **Author / Owner**：wavyjay1
- **Year**：2026（repo 最近一次更新为 2026-03-31）
- **Title**：*cross-exchange-arbitrage*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL**：https://github.com/wavyjay1/cross-exchange-arbitrage
- **Repo URL**：https://github.com/wavyjay1/cross-exchange-arbitrage

### 4.2 这次实际重点看的文件
- `strategy/edgex_arb.py`
- `strategy/order_manager.py`
- `strategy/position_tracker.py`
- `strategy/data_logger.py`
- `exchanges/edgex.py`
- `exchanges/lighter.py`

### 4.3 公开数据 / 公开接口线索
- **Lighter public REST**：`https://mainnet.zklighter.elliot.ai/api/v1/orderBooks`
- **edgeX public quote websocket（repo 配置）**：`wss://quote.edgex.exchange`
- **edgeX public trading site**：`https://pro.edgex.exchange`
- 数据公开性：至少 Lighter order book 为公开 REST，edgeX quote feed 在 repo 中按公开 ws 地址接入
- 更新频率：秒级 / 子秒级，天然更适合 `1m / 3m`

## 5. repo 里最该拿走的硬点

### 5.1 它交易的不是“抽象价差”，而是非常具体的 maker/taker 壳

`EdgexArb` 的主逻辑非常明确：

- **maker leg 在 EdgeX**：先挂 post-only 限价单；
- **hedge leg 在 Lighter**：maker leg fill 后，用更激进的价格去吃掉对手盘；
- 默认参数：
  - `long_ex_threshold = 10`
  - `short_ex_threshold = 10`
  - `fill_timeout = 5s`
  - `max_position` 受外部配置约束。

也就是说，这不是“看两个 mid price 的差值”，而是明确写成：

1. 先在一边争取 maker；
2. 一旦成交，另一边马上 taker 对冲；
3. 赌的是 **gap 回收 + maker 节省的那一点壳**。

这点很重要，因为很多跨所 alpha 写到最后都会偷换成 mid-mid backtest，但这份 repo 至少把真实成交层放进来了。

### 5.2 信号方向清楚，但原始实现仍然偏乐观：触发口径和可成交口径并不完全一致

`trading_loop()` 里真正的两条触发条件是：

- 若 `lighter_bid - ex_best_bid > long_ex_threshold`：
  - 视为可做 `long EdgeX / short Lighter`
- 若 `ex_best_ask - lighter_ask > short_ex_threshold`：
  - 视为可做 `short EdgeX / long Lighter`

但注意一个很 desk 的细节：

- 真正执行 `buy on EdgeX` 时，订单价格是 `best_ask - tick_size`；
- 真正执行 `sell on EdgeX` 时，订单价格是 `best_bid + tick_size`；
- 也就是说，**信号判断用的是 BBO gap，执行却是 inside-spread 的 maker 价格**。

这对 repo 使用者是个提醒：

**原始信号并不是严格的“可成交净价差”。**

如果直接照抄，会把边看得偏厚。对 desk 来说，更正确的改法应该是直接把信号改写成：

- `long_gap_exec = lighter_bid * (1 - fee_lighter_taker) - edgex_buy_price_exec`
- `short_gap_exec = edgex_sell_price_exec - lighter_ask * (1 + fee_lighter_taker)`

而不是继续用裸 `bid-bid` / `ask-ask` 去判。

### 5.3 fill 逻辑暴露了这条 alpha 的真实难点：不是方向，而是第二条腿能不能安全补上

`order_manager.py` 里最值得抄的，不是某个 fancy signal，而是 **交易状态机本身**：

- EdgeX maker leg 最多等 **5 秒**；
- 若还没成交就撤；
- 一旦 EdgeX fill，马上触发 Lighter 对冲；
- Lighter buy 用 `best_ask * 1.002`；
- Lighter sell 用 `best_bid * 0.998`；
- Lighter 最多等 **30 秒**；
- 整笔交易最多等 **180 秒** 完成。

翻成人话：

repo 非常坦白地承认了一件事：

> 这条 alpha 不是“看见 gap 就一定能无风险锁住”，真正决定它值不值得做的，是 **maker 先成交后，第二腿是不是还能用可接受成本补上。**

因此，这条题材对 desk 的核心不是预测，而是：

- legging risk；
- quote stale；
- 盘口深度；
- hedge urgency；
- orphan leg 风险。

### 5.4 它已经给了一个简单但够用的风险壳

`position_tracker.py` 和 `edgex_arb.py` 里有几条很重要的守门：

- 开仓前会同步查询两边当前仓位；
- 若 `abs(net_position) > 2 * order_quantity`，直接 `sys.exit(1)`；
- `max_position` 控制单方向累计敞口；
- BBO 数据与成交数据全部落 CSV。

这说明这份 repo 的正确读法不是“套利脚本”，而是：

**一个已经把单腿失控当真问题处理的 execution shell。**

### 5.5 公开接口快检：Lighter 的订单簿与费率字段是公开可取的，而且当前返回 maker/taker 均为 0

我对 `https://mainnet.zklighter.elliot.ai/api/v1/orderBooks` 做了 live sanity check：

- 接口返回 `200`；
- 当前可直接拿到大量 perp 市场配置；
- 返回字段中包含：
  - `symbol`
  - `market_id`
  - `min_base_amount`
  - `supported_size_decimals`
  - `supported_price_decimals`
  - `maker_fee`
  - `taker_fee`
- 快检样本里多个市场显示：
  - `maker_fee = 0.0000`
  - `taker_fee = 0.0000`

这点对 desk 很重要：

如果一边 venue 的 taker 壳真的接近 0，那么这类 alpha 的 admission hurdle 会明显下降；
但如果另一边 maker rebate / taker fee 没有同步纳入，回测还是会高估。

## 6. 这条思路怎么 desk 化

### 6.1 正确的时间尺度：主看 `1m / 3m`，`5m` 只做统计，不拿来当主触发

这条线本质上是盘口 pocket，不是 bar-pattern。

所以最自然的读法是：

- **信号采样层**：250ms ~ 5s
- **研究统计层**：`1m / 3m`
- **`5m`**：只用于汇总 pocket 频率 / 持续时长 / venue health
- **`15m`**：不适合做主触发，最多用来做 regime veto

### 6.2 它更像“执行型 stat-arb”，不是“方向型信号”

这类 alpha 的研发顺序，不应该是：

1. 先搞复杂模型；
2. 再看能不能成交。

而应该反过来：

1. 先定义 **可成交净价差**；
2. 再看 pocket 有没有足够频率；
3. 再看延迟 / 滑点 / orphan leg 后还能不能活；
4. 最后才考虑做更好的 routing / threshold adaptation。

## 7. 这份 repo 最重要的 desk 化结论

### 7.1 这是一条完整 raw alpha，不是 filter

这点要说清楚：

- 它不是用来确认 breakout；
- 不是用来做 regime；
- 不是 position overlay；

它自己就是 alpha 本体：

**same-contract cross-venue quote gap reversion**。

### 7.2 但 repo 的默认阈值不能直接照抄

默认 `threshold = 10` 是绝对价格单位，不是 bps。

这会带来两个问题：

1. **不同币种不可比**：10 美元对 BTC 和对小币完全不是一回事；
2. **不同波动环境不可比**：同一币在高波和低波时，10 美元也不是同一层级。

所以对 desk 来说，第一步不是回测全 universe，而是把 admission 改写成：

- bps / ticks / spread-vol 标准化阈值；
- 再叠加 fee-adjusted executable gap。

### 7.3 repo 真正值钱的是“单腿风控状态机”，不是那两个 10-unit threshold

这份材料最该留下来的，不是：

- `10` 这个数字；
- 或“EdgeX/Lighter 这对 venue 一定长期有边”；

而是：

- maker 先手；
- hedge 立即跟；
- timeout 明确；
- orphan leg 直接当事故处理；
- 用日志回放交易过程。

也就是说，**对 desk 最值钱的不是参数，而是这条 alpha 的 execution grammar。**

## 8. 下一步怎么测

### 实验 1：先录可成交净价差，而不是录裸 BBO

对每个时点都记录：

- `edgex_best_bid / ask`
- `lighter_best_bid / ask`
- `tick_size`
- venue fee / rebate

然后定义：

- `edgex_buy_exec = edgex_best_ask - tick`
- `edgex_sell_exec = edgex_best_bid + tick`
- `long_gap_exec = lighter_bid - edgex_buy_exec - fee_stack`
- `short_gap_exec = edgex_sell_exec - lighter_ask - fee_stack`

先看：

- after-fee positive gap 出现频率；
- gap 的 `p95 / p99`；
- pocket 持续时长分布。

### 实验 2：做事件窗，不急着先做“回测收益曲线”

对所有 `gap_exec >= θ` 的时刻做 event study：

- 1s / 5s / 15s / 30s / 60s 之后是否收敛；
- 收敛 hit-rate；
- 最大不利扩张；
- time-to-close。

这一步最能回答：

**它到底是真回归，还是只是经常一闪而过，根本来不及补第二腿。**

### 实验 3：把 legging risk 直接写进模拟

至少做 3 档延迟：

- `100ms`
- `500ms`
- `1s`

并模拟：

- maker 未成交撤单；
- maker 部分成交；
- hedge taker price-through；
- Lighter 30s 未成单 fallback。

如果一加延迟边就消失，这条线就只适合更低延迟的基础设施，不适合当前 desk。

### 实验 4：把阈值从绝对值改成标准化口径

第一版先测：

- `gap_bps >= {2, 4, 6, 8}`
- `gap_ticks >= {2, 4, 6}`
- `gap / short-horizon spread-vol >= {1.0, 1.5, 2.0}`

目标不是找 best cell，而是看：

**是否存在一整片在成本后仍然活着的参数 pocket。**

## 9. 结论

这份 repo 值得进研究池，但要用对读法。

它真正该留下来的不是：

- “跨所机器人”这个泛标题；
- 默认 `10` 单位阈值；
- 或“看见 gap 就等于无风险套利”。

而是这条对短周期 desk 非常直接的 raw alpha：

**same-contract perp 在两个 venue 的盘口会短时失衡；如果你能在一边拿到 maker、另一边迅速 taker 对冲，就有机会赚到 quote gap 的回收。**

当前最关键的 desk 结论是：

1. **这条 alpha 本体成立，而且不是 filter；**
2. **repo 已经把它写成完整的 entry / hedge / timeout / risk shell；**
3. **真正该先测的不是“10 这个阈值对不对”，而是 after-fee executable gap 在真实延迟下有没有厚度；**
4. **这条线最自然服务于 `1m / 3m` 高强度 alpha intake，而不是 `15m` bar-pattern。**

如果只给一个最小动作：

**先录两边 BBO 7 天，做 `after-fee executable gap` 的事件窗和延迟敏感性。**

这一步最省时间，也最能决定这条 same-contract cross-venue alpha 值不值得进下一轮复现。

## 10. Sources

1. **wavyjay1, 2026, _cross-exchange-arbitrage_**, GitHub repository, Venue: GitHub, DOI: N/A  
   - Readable URL: `https://github.com/wavyjay1/cross-exchange-arbitrage`  
   - Repo URL: `https://github.com/wavyjay1/cross-exchange-arbitrage`

2. **Lighter public orderBooks endpoint**, public REST market metadata / order book listing  
   - Readable URL: `https://mainnet.zklighter.elliot.ai/api/v1/orderBooks`

3. **edgeX public trading / quote endpoints as referenced in repo config**  
   - Trading site: `https://pro.edgex.exchange`  
   - Quote websocket: `wss://quote.edgex.exchange`

## 11. 这篇 digest 产出物

- Markdown：`research/quant_digests/2026-03-31_1929_edgex-lighter-samecontract-crossvenue-arb-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-31_1929_edgex-lighter-samecontract-crossvenue-arb-alpha.html`
