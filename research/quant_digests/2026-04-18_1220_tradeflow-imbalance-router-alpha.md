# Trade-flow imbalance 不是“又一个盘口指标”：对 short-cycle crypto desk，更该先测的是「极端 taker buy dominance × cross-sectional router」这条 raw alpha
- 时间：2026-04-18 12:20 UTC
- 类型：2026 论文元数据/版本线索 + Binance USDⓈ-M `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：主动买盘显著占优后，未来几个 bar 是否继续同向漂移；若同时出现多个候选，则只做当下 **taker buy imbalance** 最强的一档
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / order-flow / taker-imbalance / continuation / cross-sectional / router / binance / 5m / 15m
- 证据类型：论文线索 + 自建公开数据快检

## 1. 这次看了什么
主线来源是 Anastasopoulos, Gradojevic, Liu, Maynard, Tsiakas 的 2026 论文 **Order flow and cryptocurrency returns**（*Journal of Financial Markets*；DOI `10.1016/j.finmar.2026.101047`，前序 SSRN 版本 DOI `10.2139/ssrn.5020002`）。这轮没拿到稳定全文，所以没有假装“已完整复刻论文结论”；真正可落地的部分，是把 Binance 永续 K 线里公开可得的 `taker_buy_quote_volume / quote_volume` 直接翻成短周期 **trade-flow imbalance** 代理量并做 portability probe。

## 2. 核心结论
- **一句话核心结论**：这条线在当前 Binance majors 上，不像“所有极端失衡都值得追”，更像 **只追极端买盘主导**，而且更适合作为 `15m` cross-sectional router。
- **一句话证明方式**：不是靠口头直觉，而是直接用 Binance USDⓈ-M 公共 `5m/15m` K 线里的 taker-buy 成交额构造 `flow_imb = 2*taker_buy_quote/quote_volume - 1`，再看未来 `1/3/5/12` bar 的 signed drift。
- 全样本把 `|flow_imb|` 做到滚动 `q90` 后，**并不存在稳定的“见极端就追”**：`15m` 全样本 next `3/5/12 bar` gross 仅约 `+0.27 / +0.09 / +1.19 bps`，明显不够直接当主信号。
- 但把方向拆开后，**buy-dominant 与 sell-dominant 很不对称**：`5m` 的 `buy_dom_q90` 在 next `3/5/12 bar` gross 约 `+1.59 / +1.09 / +4.33 bps`，而 `sell_dom_q90` 同期约 `-1.97 / -2.01 / -2.69 bps`，说明“强卖盘继续砸”这层在当前样本里反而不稳。
- 更像策略壳的是 **cross-sectional router**：每根 `15m` bar 只在 `q90 + vol_z>0 + flow_imb>0` 的候选里，买入 `flow_imb` 最强那一档；该路由在近约 `16d`、8 个 majors 上共 `161` 笔，next `5/12 bar` gross 约 `+9.03 / +13.83 bps`，粗扣 `8bps` 后 net 约 `+1.03 / +5.83 bps`。
- 当前 symbol mix 不是只靠单一币硬撑：router 触发里 `BTC/ETH/BNB/ADA/DOGE/LINK/SOL/XRP` 都有贡献，其中计数约 `29/24/21/20/18/20/15/14`。

## 3. 为什么和当前项目有关
这条线补的是我们最近素材池里相对缺的 **trade-flow / aggressor-flow raw alpha**，它和此前做过的 `order-book imbalance` 不同：前者看的是“谁在主动打成交”，后者看的是“挂单簿哪边更厚”。对当前 desk，更值钱的不是再堆一个盘口解释，而是把它变成：
- 一个能独立运行的 **短持有 continuation raw alpha**；
- 一个能挂在 `1m/3m/5m` 执行层之上的 **15m router / admission layer**；
- 一个能和现有 momentum / breakout 壳做交叉验证的 **flow confirmation** 组件。

## 3.5 策略拆解（必填）
- 方向属性：横截面 + 事件驱动顺势
- 基础 alpha：极端 **taker buy dominance** 后的短窗 continuation
- regime：默认先不加宏观 regime；当前更像“高主动买盘 + 有成交量配合”时才开机
- filter / veto：`|flow_imb| >= rolling q90`、`flow_imb > 0`、`vol_z > 0`
- risk / sizing / execution overlay：每根 bar 最多只选 1 个标的；固定持有 `5` 或 `12` 个 `15m` bar；单笔固定风险，先按 taker `8bps` 粗成本验尸，再决定是否改 maker/child slicing

## 4. 可复刻的最小实验
- 研究假设：公开 taker-buy 成交额足够做代理流向；当 `15m` 出现极端正向失衡时，majors 里最强那一档还会继续漂一小段。
- 可计算定义：`flow_imb = 2 * taker_buy_quote_volume / quote_volume - 1`。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`，主实验用 `15m`；事件为 `flow_imb > 0` 且 `|flow_imb| >= rolling q90` 且 `vol_z > 0`；每个时间戳只保留 `flow_imb` 最大的 1 个标的。
- entry / exit / sizing / cost：bar close 生成信号，下一 bar 开盘进；持有 `5` 与 `12` bar 两档；等权单票；先粗扣 round-trip `8bps`。
- 最先看两项：`post-cost mean bps/trade` 与 `positive-window ratio`；其次看是否被单一币或单一日期垄断。

## 5. 风险与保留意见
- 这轮**没拿到稳定全文**，所以不把 paper headline 当作已复刻事实；当前最硬证据仍是自建 public-data probe。
- Binance K 线里的 taker-buy 只是公开代理，不等于完整逐笔 order flow；若后面能拿到逐笔 aggressor 数据，结果可能变化。
- `5m` 裸追不够厚，说明这条线目前更像 `15m context -> 5m/1m child execution`，而不是无脑分钟级追单。
- 当前 buy/sell 明显不对称，后续不要默认把“极端卖盘”也按镜像策略处理。

## 6. 来源
- Alexia Anastasopoulos, Nikola Gradojevic, Fred Liu, Alex Maynard, Ilias Tsiakas. (2026). *Order flow and cryptocurrency returns*. *Journal of Financial Markets*.
- DOI: `10.1016/j.finmar.2026.101047`
- Readable URL: `https://doi.org/10.1016/j.finmar.2026.101047`
- Preprint DOI: `10.2139/ssrn.5020002`
- Preprint URL: `https://doi.org/10.2139/ssrn.5020002`
- 本地 portability probe：`reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_probe.py`
- 本地产物：
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_events.csv`
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_signed_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-18_tradeflow_imbalance_router_summary.csv`
