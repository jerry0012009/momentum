# 别把 jump 论文只读成风险统计：这篇 2024 *Digital Finance* 更该先测的是「BTC confirmed jump → liquid alts 同向跟跳」事件型 raw alpha
- 时间：2026-03-30 13:11 UTC
- 类型：Paper
- 主题类型：raw alpha
- 基础 alpha：当 BTC 出现确认过的高频 jump 后，做未完成同向补涨/补跌的高流动性跟随币（ETH/LTC/XRP/BCH/ETC 等）短窗 follow-through / co-jump
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/jump/contagion/co-jump/follower-basket/lead-lag/btc/eth/alts/high-frequency/tick-data/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：论文实证 + 结构化事件映射

## 1. 这次看了什么
这次主看的是 Saef、Nagy、Sizov、Härdle 在 2024 年发表于 *Digital Finance* 的开放获取论文 **Understanding temporal dynamics of jumps in cryptocurrency markets: evidence from tick-by-tick data**。它不是传统“给你一条现成交易规则”的论文，而是用 `7` 家大所、`6` 个主流币、近 `2.5` 年 tick-by-tick USDT 交易数据，把 **jump 的时间聚集、自激发、跨币污染（contamination）和日内时段性** 拆得很细。

我这里不把它当成“jump 风险统计材料”，而是把它重读成一个很直接的 **短周期事件型 raw alpha scaffold**：
- 触发器不是新闻，不是主观判断，而是 **BTC/ETH 的已确认 jump**；
- 交易对象不是 jump 本币本身，而是 **还没完全反应的 liquid follower basket**；
- 持有周期不是隔夜，而是 **同一交易日内的 `1m/3m/5m/15m` follow-through**；
- 时间过滤也不是拍脑袋，而是直接来自论文里的 **jump seasonality**。

换句话说，这篇 paper 对 desk 最有价值的部分，不是“crypto 里有 jumps”，而是它在告诉我们：**BTC jump 本身可以作为公开、可事件化、可分钟级实现的 alpha anchor**。

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 最值得先测的，不是 jump 检验本身，而是 **BTC confirmed jump 之后，做尚未完成同向反应的 liquid alt basket 的短窗跟随 / 跟跳**。
- **一句话 base alpha：** `leader jump → follower same-sign catch-up`，本质上是一个事件驱动的跨币 lead-lag / contagion raw alpha。
- 论文样本覆盖 `2019-04-12` 到 `2021-09-27`，来自 Binance、Bitfinex、Bitstamp、Coinbase Pro、HitBTC、OKex、Poloniex 的 tick 数据，币种包括 `BTC/BCH/ETC/ETH/LTC/XRP`。这个数据口径虽然不是“直接给你回测 PnL”，但对设计一个 **公开可拿、可在 1m 代理复现** 的短周期策略已经足够具体。
- 论文共检测到 `1,392` 次 jumps，其中约 `61%` 为负 jumps；`BTC` 和 `ETH` 分别在约 `58%` / `32%` 的观测交易日出现 jumps。**这不是一个“极少见到无法研究”的事件。**
- 跳跃的日内分布非常关键：多数 jumps 集中在 `13:00–17:00 UTC`，而 `01:00–06:00 UTC` 明显冷清。对 desk 来说，这几乎天然给了一个 **time-of-day regime gate**：先别 24/7 硬跑，把测试资源优先放到高 jump-density pocket。
- 论文明确写到：**intraday jumps 会显著影响当日收益，但对下一交易日收益没有证据。** 这句话很值钱，因为它把 horizon 直接收窄到了 **同日内、短窗持有**，而不是让我们误把它写成慢频 carry 或隔夜 drift。
- jump cluster 里，多数是单 jump，但 multi-jump cluster 并不少见；`BTC` 单币 jump 次数为 `338`，`ETH` 为 `158`，显著高于其余币。**leader asset 很清楚，先从 BTC 做 anchor 比从尾部小币做 anchor 更靠谱。**
- Table 9 的 co-occurrence / conditional probability 结果也支持这一点：BTC 与 ETH 的共同跳跃关联最强，论文文字直接总结为 **“若 BTC 已经 jump，其他币后续 jump 的可能性更高”**。这正是我们需要的交易型读法。
- 由于负 jumps 不仅更多，而且负向 jump cluster 也更常见，我会默认把 **short-side follower trade** 放在更高优先级，long side 则作为对照组而不是默认主腿。

## 3. 为什么和当前项目有关
当前 desk 在短周期上已经积累了不少 breakout / MR / microstructure / funding 侧素材，但 **“公开事件触发 + follower basket 执行”** 这条 raw alpha 支线还不够厚。

这篇 paper 值得进池，原因很直接：
- **base alpha 很清楚**：不是 filter，也不是纯解释，而是 `BTC jump → followers catch up`；
- **天然适配 `1m/3m/5m/15m`**：论文已经明确说次日无效，意味着 edge 大概率就活在分钟到小时内；
- **公开数据可拿**：即便拿不到跨所 tick 全集，我们也能先用 Binance/OKX/Bybit 公共 `aggTrades` 或 `1s/1m` kline 做最小代理实验；
- **可服务 desk 的事件型 alpha 组件库**：jump trigger、same-sign follower routing、time-of-day gate、negative-asymmetry side split，这些都能复用于别的冲击型 alpha。

所以这不是“再看一篇 market microstructure 综述”，而是给研究池补一条 **事件驱动 / 跨币跟跳** 的 raw alpha 分支。

## 3.5 策略拆解（必填）
- 方向属性：事件驱动 / lead-lag / 跨币 contagion / same-sign continuation
- 基础 alpha：当 BTC 出现确认过的高频正/负 jump 后，交易尚未完成同向反应的高流动性跟随币，捕捉 `1m~15m` 内的 catch-up move
- regime：优先 `13:00–17:00 UTC`；优先周中；优先高成交、高新闻密度时段；避免 `01:00–06:00 UTC` 的低 jump-density 冷区
- filter / veto：只做高流动性主流 alts；若 follower 在触发前 `k` 根 bar 已经完成同方向大部分位移则 veto；可加 BTC/ETH spread-to-signal 同步确认
- risk / sizing / execution overlay：BTC jump 只做 event anchor；follower basket 做 equal-risk 或 inverse-vol；单币上限、事件并发上限、冷却时间、极端反向 micro-reversal 立即平仓；默认 taker 成交并加事件期滑点惩罚

## 4. 可复刻的最小实验
- **研究假设：** `BTC confirmed jump` 是一个可公开观测的 leader event；在事件后的极短窗口里，部分 liquid alts 会发生 **同向 delayed follow-through**，形成可交易的 follower-basket alpha。
- **数据口径：** 第一版不追求跨 `7` 所 tick 级完全复刻，先用 Binance USDⓈ-M 或 Spot 的 `aggTrades` / `1s` 或 `1m` bar 代理；币种先用 `BTC, ETH, XRP, LTC, BCH, ETC`，与论文 universe 对齐到最小子集；样本先跑近 `90d~180d`。
- **jump 定义（最小代理版）：** 不先硬上复杂 HF jump test。先用两个可快速落地的代理版本并行：
  1. `1m return` 超过自身过去 `30d` 同时段分布 `99.5%` 分位，且伴随 `1m volume` > `95%` 分位；
  2. `3m signed move / rolling realized vol` 超过阈值（例如 `z >= 4`）。
  只要这两种定义都能给出类似方向结果，才值得再升级到 bipower variation / Lee-Mykland 类 jump 检验。
- **交易规则 A（主实验）：**
  - 触发：BTC 出现正/负 jump；
  - 选腿：在 `ETH/XRP/LTC/BCH/ETC` 中筛选过去 `1~3` 根 bar 尚未达到同向阈值的 follower；
  - 入场：下一根 `1m` 或 `3m` bar 开盘按 jump 方向入场；
  - 出场：持有 `3/5/15` 根 bar 三档；或 follower 完成预设 catch-up move（例如达到 BTC 当次 jump 幅度的 `40%~60%`）；或出现反向 micro-reversal 即平；
  - 组合：同一事件最多开 `2~3` 个 follower，equal-risk / inverse-vol 分配。
- **交易规则 B（负向优先版）：** 单独把 negative-jump 事件拎出来，因为论文显示 `61%` jumps 为负，且负向 cluster 更多。若 after-cost 结果明显偏向 short side，则 production 原型优先只保留 negative branch。
- **交易规则 C（time gate 版）：** 只在 `13:00–17:00 UTC` 做事件；与全天跑法对照。若 time-gated 版本 trade count 下降但 `hit-rate / pnl per trade` 上升，说明论文里的 jump seasonality 能直接转成 shared gate。
- **成本模型：** 先用保守 taker 成本：单边 `4~6 bps` 手续费 + `2~6 bps` 事件滑点；事件期总 round-trip 先按 `12~20 bps` 压测。若只有零成本下成立，就不要继续包装成“可实盘”。
- **最先看 6 个指标：** `after-cost pnl/event`、`hit-rate`、`median MFE/MAE`、`BTC→follower lag 分布`、`negative vs positive split`、`time-gate on/off uplift`。
- **下一步怎么测：** 先做一个最朴素的 **BTC jump → follower basket 同向持有 `3/5/15` bars** 的事件研究，再把 `negative-only` 和 `13:00–17:00 UTC only` 两个分支拆开；如果这两层都不能抬高 after-cost 质量，就不要继续上更复杂的 jump estimator。

## 5. 风险与保留意见
- 论文证明的是 jump 的时间结构和条件概率，不是现成的交易 PnL；因此我们是在把它 **转译成策略假设**，不是“论文已经替我们验过 alpha”。
- 论文使用 tick 数据与更严格的 HF jump 识别；如果我们第一轮只用 `1m` 代理，可能把普通大波动误当 jump，导致 signal 污染。
- 事件型 alpha 天生更吃执行：真正 edge 可能集中在 jump 后前几分钟，若成交迟或滑点高，净边会被吃掉。
- follower 是否“还没反应完”是成败关键；如果用过于粗糙的 veto，策略容易退化成 chase already-moved names。
- 样本期覆盖 Covid、Musk tweet、监管冲击等高事件密度阶段；后续样本若事件结构变化，trade count 和 edge 稳定性都可能下台阶。

## 6. 来源
- Saef, Danial; Nagy, Odett; Sizov, Sergej; Härdle, Wolfgang Karl. (2024). **Understanding temporal dynamics of jumps in cryptocurrency markets: evidence from tick-by-tick data**. Venue: *Digital Finance*. DOI: `10.1007/s42521-024-00116-1`. Readable URL: `https://doi.org/10.1007/s42521-024-00116-1`. PDF URL: `https://link.springer.com/content/pdf/10.1007/s42521-024-00116-1.pdf`. Repo URL: N/A
- Related background: Scaillet, O.; Treccani, A.; Trevisan, C. (2020). **High-frequency jump analysis of the Bitcoin market**. Venue: *Journal of Financial Econometrics*. Readable URL: `https://doi.org/10.1093/jjfinec/nbaa006`
- Related market-structure backdrop: Makarov, Igor; Schoar, Antoinette. (2020). **Trading and arbitrage in cryptocurrency markets**. Venue: *Journal of Financial Economics*, 135(2). DOI: `10.1016/j.jfineco.2019.07.001`. Readable URL: `https://doi.org/10.1016/j.jfineco.2019.07.001`
