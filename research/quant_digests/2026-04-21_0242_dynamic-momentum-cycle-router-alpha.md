# 别把 Borgards (2021) 只读成“crypto 有动量”：对 short-cycle crypto desk，更该先拆的是「dynamic momentum-cycle continuation × strongest-only router」这条 raw alpha
- 时间：2026-04-21 02:42 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：价格已经进入同向的动态 momentum cycle 后，若再次放量、扩波动并突破近几根极值，后面 `30~60min` 往往还有一小段同向延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / trend / momentum / continuation / dynamic-cycle / breakout / router / 5m / 15m / Binance
- 证据类型：论文证据（摘要页 + 导言片段）+ public-data portability probe

## 1. 这次看了什么
看的是 Oliver Borgards (2021) 的 *Dynamic time series momentum of cryptocurrencies*。这篇论文最值钱的点，不是再说一遍“动量存在”，而是把 time-series momentum 从固定 `N` 根收益，改写成**动态 momentum period / turning-point sequence**。翻成人话就是：**市场不是每根都在趋势里，但一旦已经走出一段单边，后面的再加速，往往比“从零开始猜方向”更值得跟。**

## 2. 核心结论
- 一句话核心结论：**这篇论文真正值得 desk 拿来试的，不是长样本 buy-and-hold 对比，而是“先识别动态 momentum cycle，再只做 cycle 内的再加速 continuation”。**
- 一句话证明方式：**论文用 turning-point / smoothing filter 的动态建模来定义 formation period 与后续 momentum period；我再把它翻成 short-cycle 版本，用 Binance USDⓈ-M `5m/15m` 公共 K 线做便携性快检。**
- 论文摘要页给出的主结论很硬：作者对 `20` 个 crypto 做动态建模，发现 formation period 后接 momentum period 的比例很高，而且 crypto 的 momentum period **更长、更多、风险调整后优于被动持有**。
- 但直接搬到当前 liquid-major short-cycle 并不自动成立：我做的宽口径 `15m` continuation probe（`BTC/ETH/SOL`，最近约 `6000` 根）整体偏弱，`15m` broad 版本大多转负，说明**“只要在动态趋势里就追”太粗**。
- 真正还能留下 pocket 的，是更窄的 `5m` 版本：要求 `EMA-smoothed` 同向 run 已持续、同时本根放量（`vol_z>0`）且有 ATR 扩张，再突破近 `6` 根高/低。这个版本里：
  - `ETHUSDT 5m` next `6/12` bars 约 `+4.74 / +6.61 bps gross`，样本 `n=168 / 168`；
  - `BTC/ETH/SOL` 同刻只做 strongest 一档时，next `6/12` bars 约 `+1.83 / +1.17 bps gross`，样本 `n=373 / 372`；
  - `BTC/SOL` 单独跑仍偏负，说明这更像**有 symbol 选择的 router pocket**，不是 broad always-on trend signal。

## 3. 为什么和当前项目有关
这条线和 desk 现在补的 raw alpha 素材池是直接相关的：它不是纯 filter，也不是抽象机制解释，而是一条**可下单的 trend / momentum continuation raw alpha**。更重要的是，它补的是当前素材池里相对缺的一块：**不要只用静态过去收益做动量，还要学会把“趋势已经形成到哪一步”写成 causal 的动态状态机。** 这既能单独做 `5m` alpha，也能给现有 breakout / trend sleeve 提供一个更像样的 state router。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 单资产，可扩成 strongest-only router
- 基础 alpha：dynamic momentum cycle 内的再加速 continuation
- regime：更适合已进入单边、但还没进入极端拥挤尾段的短时趋势环境
- filter / veto：`vol_z > 0`、`ATR expansion > 0.9`、近 `6` 根突破；若 broad market 同时出现大面积反向冲击，可 veto
- risk / sizing / execution overlay：下一根开盘顺势入场；先看 fixed hold `6/12` bars；单笔风险固定，粗扣 round-trip `4~8bps`；可只做 top1 strongest signal 降低同时持仓数

## 4. 可复刻的最小实验
- 研究假设：**已经进入动态趋势状态的币，在“再次放量 + 再次扩波动 + 再次突破”时，接下来 `30~60min` 仍更容易顺着走。**
- 可计算定义（当前便携版）：
  - `ema = close.ewm(span=10)`
  - `dir_run >= 6`
  - `close > rolling_high(6)` 做多，`close < rolling_low(6)` 做空
  - 同时要求 `vol_z > 0`、`(high-low)/ATR > 0.9`
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL` 先跑最近 `60~90d` 的 `5m`；再扩到 `10~20` 个 liquid majors 做 top1 strongest router
- 最先看两个指标：`gross/net bps per trade`、`symbol concentration`；第三个看 `post-cost positive share`
- 下一步怎么测：
  1. 把当前 `5m` pocket 扩到 top20 liquid majors，验证 edge 是否只集中在 ETH；
  2. 比较 `broad all-signals` vs `top1 router` vs `top2 capped`；
  3. 加入 maker-first / pullback child entry，看 `1~3bps` gross pocket 能否留到成本后；
  4. 对比“静态过去 `k` 根收益动量”与“动态 cycle continuation”，确认增量价值到底来自 state 定义还是只是换皮 breakout。

## 5. 风险与保留意见
- 这轮拿到的是 ScienceDirect 摘要页与导言片段，不是全文逐节 audit；因此**论文层面的细参数与交易细节我没有装作已经完全读透**。
- 当前 liquid-major `15m` broad transfer 明显不过线；所以别把它误读成“又一条稳健的 15m 趋势主信号”。
- `5m` strongest-only 目前只有小幅 gross edge，本质上很吃成本；如果不能做低摩擦执行，它很容易被手续费和滑点吃掉。
- 这条线更像“趋势状态 router / selective continuation pocket”，不是无差别全市场追涨框架。

## 6. 来源
- Oliver Borgards. (2021). *Dynamic time series momentum of cryptocurrencies*. *The North American Journal of Economics and Finance*.
- DOI: `10.1016/j.najef.2021.101428`
- Readable URL: `https://www.sciencedirect.com/science/article/abs/pii/S1062940821000590`
- DOI URL: `https://doi.org/10.1016/j.najef.2021.101428`
- Repo URL: `N/A`
- Probe artifacts:
  - `reports/artifacts/quant_digests/dynamic_tsmom_cycle_filtered_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/dynamic_tsmom_cycle_filtered_detail_2026-04-21.csv`
  - `reports/artifacts/quant_digests/dynamic_tsmom_cycle_filtered_router_2026-04-21.csv`
