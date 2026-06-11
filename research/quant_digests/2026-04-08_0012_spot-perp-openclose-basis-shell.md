# 别把 Hummingbot 的 `spot_perpetual_arbitrage` 只读成 carry 教程：对 short-cycle desk，更该先测的是「spot-perp executable basis × open/close hysteresis shell」
- 时间：2026-04-08 00:12 UTC
- 类型：GitHub mature strategy source audit（repo metadata + `spot_perpetual_arbitrage.py` + `arb_proposal.py` + `spot_perpetual_arbitrage_config_map.py` + `start.py`）
- 主题类型：raw alpha
- 基础 alpha：同一标的 spot 与 perpetual 的**可成交 basis**一旦偏离到足以覆盖双边费用、滑点与持仓 frictions，后续往往会向平衡收敛；因此可用 delta-neutral 双腿做「开仓吃偏离、平仓吃回归」
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / carry / basis / spot-perp / delta-neutral / open-close-hysteresis / binance / hummingbot / 1m / 3m / 5m / 15m
- 证据类型：工程证据

## 1. 这次看了什么
这次主看 **Hummingbot Foundation** 的成熟策略模块 **`spot_perpetual_arbitrage`**。它真正有价值的，不是“funding 高就去收 carry”这种泛化说法，而是把一条**可直接下单的 spot-perp 相对价值策略壳**写得很完整：
- 先同时计算两种方向的可成交 spread；
- 再按开仓阈值决定是否做 `spot buy + perp sell`，或 `spot sell + perp buy`；
- 开完后不立刻反手，而是等到**另一侧 close spread** 达到平仓阈值才退出。

也就是说，这东西的 base alpha 很清楚：**交易的不是 funding 排行榜，而是 same-underlier、可成交、可净额化的 basis 偏离与回归。**

## 2. 核心结论
- 这条线最值得 intake 的地方，是它把 **raw alpha + entry/exit + sizing/risk + cost** 一次性放进同一个壳里。对当前 desk，它比“只会说 basis 可能回归”的论文摘要更接近可直接复现的完整策略。
- `arb_proposal.py` 里的收益定义很朴素，也很诚实：
  - 若做 `spot buy / perp sell`，看的是 **`(perp_sell - spot_buy) / spot_buy`**；
  - 若做 `spot sell / perp buy`，看的是 **`(spot_sell - perp_buy) / spot_sell`**。  
  这不是 mid-price 幻觉，而是**可成交报价差**。
- 源码默认参数本身就给了 3 个很有用的工程提示：**开仓阈值默认 `1%`、平仓阈值默认 `-0.1%`、双腿 slippage buffer 默认都为 `0.05%`**，另有 **`120s` reopen delay** 与 **`5x` perpetual leverage**。一句话：它默认不是“见价差就追”，而是明确采用 **open/close hysteresis**。
- `spot_perpetual_arbitrage.py` 里把状态机写成 **`Closed -> Opening -> Opened -> Closing`**，并要求 perpetual 端使用 **`ONEWAY`** 模式。这一点对实盘很关键：它不是单次 basis snapshot，而是把**持仓生命周期**显式建模了。
- 一句话核心结论：**别把 spot-perp 只读成慢速 carry；更适合 short-cycle desk 的读法，是“可成交 basis 偏离 × 双阈值开平仓壳”这条完整 raw alpha。**
- 一句话它怎么证明：**不是靠论文回测，而是直接把 spread 公式、双向 proposal、开平仓阈值、slippage、budget check、position mode 和冷却时间都写进策略源码。**

## 3. 为什么和当前项目有关
这篇东西对 `momentum` 当前最有价值的地方，是它补了一个我们很需要、但之前 mostly 只在论文/小 repo 里零散见过的组件：

1. **它是完整策略，不只是 alpha 口号。**  
   之前我们已经收了不少 `basis / funding / carry` 主题，但很多更像“哪边更贵”的线索；这次拿到的是一个**把 entry / exit / slippage / leverage / reopen delay 都定义出来的执行壳**。

2. **它天然适合 `1m / 3m / 5m / 15m` 的最小实验。**  
   这条线不依赖日频财报、低频宏观或复杂链上数据；只要有同标的 spot + perp 报价，就能开始做最小实验。

3. **它能服务于当前 desk 的已有 basis/funding 素材池。**  
   你完全可以把这个壳理解成：
   - raw alpha 本体 = executable basis dislocation
   - regime/filter = funding、深度、波动、结算时点、延迟风险
   - risk overlay = leverage / time-stop / max-open-duration / fill veto  
   这比继续泛泛讨论“carry 有没有用”更值钱。

## 3.5 策略拆解（必填）
- 方向属性：relative value / delta-neutral / carry-basis hybrid
- 基础 alpha：same-underlier 的 executable spot-perp basis 偏离后向平衡回归
- regime：高流动主力币、spot 与 perp 深度都足够、可稳定双腿成交的时段
- filter / veto：
  - net spread 扣完双腿 fee/slippage 后仍为正
  - funding 结算前后若延迟/冲击过大则 veto
  - 深度不足、盘口跳动过快、网络异常、position mode 不匹配则 veto
- risk / sizing / execution overlay：固定 `order_amount` 起步；perp 端单向仓位；双腿同步执行；开仓后只有在 close spread 达标或达到 time-stop 时才退出；必要时加 `max-open-duration` 与 funding-window veto

## 4. 可复刻的最小实验
- **研究假设**：在 `1m / 5m` 的可成交 quote 口径下，BTC/ETH 等 liquid majors 的 spot-perp basis 偏离，经过双腿成本后，仍存在可交易的**开仓-平仓 hysteresis**。
- **可计算定义**：
  1. 对每个时间点计算两条 executable spread：  
     - `open_short_carry = (perp_bid - spot_ask) / spot_ask`  
     - `open_long_carry = (spot_bid - perp_ask) / spot_bid`
  2. 若当前无仓，且任一 spread > `entry_threshold_net`，则开对应 delta-neutral 双腿。
  3. 若已有仓，则用反向 close spread 判断是否平仓；也就是别只盯开仓 spread，要看**能否在另一边把仓位平掉**。
  4. 成本至少包含：spot fee、perp fee、双边滑点、持有期间 funding（若跨 funding 时间点）。
- **最小回测切口**：
  - 标的：先做 `BTCUSDT / ETHUSDT` 的 Binance spot + perp
  - 周期：先 `1m` quote snapshot，再做 `5m` bar 内 executable proxy
  - 阈值：不要机械照搬源码默认 `1%`；对 majors 应先扫 `10 / 20 / 30 / 50 bps` entry，close 先扫 `-5 / 0 / +5 bps`
  - 持有：直到 close spread 触发，或 `30 / 60 / 120` 分钟 time-stop
- **最该先看**：
  1. `after-cost net spread capture / trade`
  2. `trade count × median open duration`
  3. 是否主要被 funding 窗口或极端盘口事件驱动
- **第一版 A/B**：
  - A：纯 threshold shell
  - B：threshold + depth / funding-window veto
  如果 B 的净收益更稳、但 trade count 没被砍废，说明这条线可以进入复现池。

## 5. 风险与保留意见
- 这份 repo 证明的是**工程可落地性**，不是“今天在 Binance majors 上一定还有 1% 肉”。默认阈值更像保守模板，不是你该直接照抄的 production 参数。
- 若双腿都按 taker 执行，很多 basis edge 会被费用直接吃掉；所以 quote source、费率层级和是否能做 maker-first，决定了这条线还能不能活。
- same-underlier 并不代表一定会快回归；极端单边行情、资金费率结算前后、现货/合约流动性失衡时，basis 可能持续扩张而不是马上收敛。
- 只用 bar close 做回测很容易高估 fill quality；如果拿不到逐笔/盘口，第一轮至少要做 conservative executable proxy，而不是用 mid-price 自嗨。

## 6. 来源
1. **Hummingbot Foundation**（2019–2026 活跃维护）. **`hummingbot/hummingbot`**. GitHub repository.  
   - Venue: GitHub  
   - DOI: 无  
   - Repo URL: `https://github.com/hummingbot/hummingbot`  
   - Readable URL: `https://github.com/hummingbot/hummingbot`
2. **Strategy logic:** `hummingbot/strategy/spot_perpetual_arbitrage/spot_perpetual_arbitrage.py`  
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/spot_perpetual_arbitrage/spot_perpetual_arbitrage.py`
3. **Profit formula helper:** `hummingbot/strategy/spot_perpetual_arbitrage/arb_proposal.py`  
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/spot_perpetual_arbitrage/arb_proposal.py`
4. **Config defaults:** `hummingbot/strategy/spot_perpetual_arbitrage/spot_perpetual_arbitrage_config_map.py`  
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/spot_perpetual_arbitrage/spot_perpetual_arbitrage_config_map.py`
5. **Strategy wiring:** `hummingbot/strategy/spot_perpetual_arbitrage/start.py`  
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/spot_perpetual_arbitrage/start.py`
