# 别把这份 2026 multi-strategy repo 只读成“大而全框架”：对 short-cycle desk，更该先拆的是「CVD trend × bar-delta / large-trade bias × divergence exit」这条 stacked order-flow raw alpha shell
- 时间：2026-04-11 20:10 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：**短窗主动买卖压力失衡（CVD trend + recent bar delta + large-trade bias）会对接下来几根 `1m/3m` K 线产生方向性漂移；delta divergence / absorption 更像 state-flip admission 与 exit，而不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/microstructure/order-flow/cvd/delta/large-trade-bias/divergence/absorption/continuation/state-flip/atr-stop/binance-perpetual/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：工程经验 + 本地 portability probe

## 1. 这次看了什么
看了 `mefai-dev/mefai-autotrade` 这个 2026 新仓库，重点不是它 README 里“20+ strategies”的大而全，而是其中 `src/strategies/order_flow.py` 已经把一条 **可直接拆成 raw alpha + reversal admission/exit 的订单流策略壳** 写得很清楚：`CVD trend / delta divergence / absorption / recent bar delta / large-trade bias` 五路打分，分数过线才开仓，仓位和止损则交给统一风险层。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得先测的，不是“footprint 很酷”，而是它把 **短窗主动流方向漂移** 写成了一条可落地的 score shell；其中 `divergence / absorption` 更适合当反转 admission 与 exit，不该和主 alpha 混成一句“order flow 有效”。
- **一句话证明方式：** 结论来自源码拆解 + 一个最小 public-data portability probe，而不是 README 宣传。
- 源码里 5 个分量的权重是明牌的：`CVD trend 0.30`、`delta divergence 0.30`、`absorption 0.25`、`recent bar delta 0.20`、`large-trade bias 0.15`；默认入场阈值 `0.50`，说明它本质上是 **stacked vote**，不是单一指标策略。
- 风险壳也算完整：默认 `risk_pct=1%`、`ATR stop=2x`、`TP=2R`，并在持仓中用 `cvd_reversal` 与 `exhaustion` 做提前出场；这比很多只给 entry、不给 exit 的 repo 更接近可复现实验对象。
- 我用 Binance USDⓈ-M 公共 `1m` K 线里的 taker-buy volume 做了一个**很粗的 continuation core 代理快检**（`delta_ratio>0.3 & cvd_trend`，最近 `1000` 根，`BTC/ETH/SOL`）：合计 `762` 个信号，后 `1m` 平均仅 `+0.26bps`、后 `3m` 仅 `+0.41bps`，方向胜率分别 `42.8% / 47.8%`。这说明**只拿最粗的 bar-level pressure continuation 单飞，并不够强**。
- 分币看也不整齐：`ETH` 代理信号后 `3m` 平均 `+2.31bps`，但 `BTC` 只有 `+0.03bps`，`SOL` 反而 `-0.15bps`。所以这条线更像 **asset-specific + tape-quality-sensitive** 的快策略，不像一条一套参数全市场通吃的干净 alpha。

## 3. 为什么和当前项目有关
当前 `momentum` 池里已经有不少 pairs / basis / cross-sectional / breakout 素材，但**“如何把 microstructure raw alpha 写成可回测、可风控、可退出的完整壳”** 这层还不够统一。这份 repo 的价值正好在这里：
- 它给了一个能拆清楚的 **order-flow continuation 主体**；
- 同时把 `divergence / absorption` 放进**反转 admission / exit**，提醒我们别把所有订单流特征都塞进同一个方向假设里；
- 对 desk 来说，这比再看一个泛泛的 indicator mashup 更有用，因为它能直接补 `1m/3m` 快策略素材池。

## 3.5 策略拆解（必填）
- 方向属性：**单资产 / microstructure directional / 以 continuation 为主，夹带 state-flip 反转提示**
- 基础 alpha：**主动买卖失衡延续：`CVD trend + recent bar delta + large-trade bias -> next-few-bar drift`**
- regime：更适合高流动、成交连续、trade tape 质量高的时段；低成交或假量时容易退化
- filter / veto：`delta divergence`、`absorption`、`exhaustion`；它们更像 reversal admission / early-exit，而不是主信号本体
- risk / sizing / execution overlay：`1%` 风险仓位、`2x ATR` 止损、`2R` 止盈、`cvd reversal / exhaustion` 提前出；**但真实成交成本、撮合延迟、逐笔分类精度仍需外接**

## 4. 可复刻的最小实验
- **研究假设：** 在 `1m/3m` crypto perp 上，真正可迁移的不是“某个 footprint 图形”，而是 **净主动流同向推进是否能给出短窗 continuation；而 divergence / absorption 是否能把坏 continuation 挡掉或提前出清。**
- **最小信号定义：**
  1. continuation 书：`delta_ratio > q`、`cvd > ma(cvd)`、`large_trade_buy > sell * k` 做多；空头镜像
  2. reversal / veto 书：价格创新高但 `CVD` 不创新高，或高成交低位移（absorption）时，不追 continuation，改做减仓/退出/反向候选
- **最小数据口径：** 先用 Binance USDⓈ-M `1m` K 线自带 `taker_buy_base_volume` 做第一版；通过后再升级到 `aggTrades` / 逐笔成交重建真正 CVD 与 large-trade bias。
- **评估顺序：** 先看 `next 1/3/5 bar expectancy (bps)`，再跑 `0/2/4/6/8 bps` friction ladder，最后看 `BTC/ETH/SOL` 分币与欧美时段分层。
- **下一步怎么测：**
  1. 把 repo 的五路打分拆成两本账：`continuation core` 与 `reversal/exit helpers`
  2. 先单测 `CVD trend + bar delta`，再逐项加入 `large_trade_bias`、`divergence`、`absorption`
  3. 用 `1m` 进场、`3m/5m` 出场做 horizon sweep，检查 edge 是秒级、分钟级还是已经衰减
  4. 必须做分币表；若 edge 只在 `ETH` 类出现，就别把它包装成 market-wide alpha

## 5. 风险与保留意见
- 这份实现把 `footprint` 在无逐笔数据时回退成 **由蜡烛结构估算买卖量**，这对真实 order flow 研究是明显降级；不能把回测结果当成 tape-level 证据。
- `CVD trend` 在源码里用的是相对 `MA` 的简单阈值判断，不是更稳定的 event-time / volume-time 标准化版本，容易受币种活跃度影响。
- 当前快检只验证了最粗的 continuation core，结果偏弱，说明**真正的 edge 可能在“stacked vote + 更真 trade tape + 更短执行延迟”**，而不是纯 bar proxy。
- 因此这轮更适合把它放进 **可复现素材池**，而不是直接当 production-ready alpha。

## 6. 来源
- mefai-dev. (2026). *Mefai Autotrade*. GitHub repository.
- Repo URL: `https://github.com/mefai-dev/mefai-autotrade`
- README: `https://github.com/mefai-dev/mefai-autotrade/blob/master/README.md`
- Strategy code: `https://github.com/mefai-dev/mefai-autotrade/blob/master/src/strategies/order_flow.py`
- Base strategy / risk helpers: `https://github.com/mefai-dev/mefai-autotrade/blob/master/src/strategies/base.py`
- Repo metadata（GitHub API probe）: created `2026-03-25`, pushed `2026-04-08`
- 本地 probe：Binance USDⓈ-M public `1m` klines（字段含 taker buy base volume），`BTCUSDT/ETHUSDT/SOLUSDT` 最近 `1000` 根，用于 continuation core 粗代理，不代表完整 order-flow 还原
