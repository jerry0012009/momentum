# 别把这篇 2022 NAJEF 论文只读成“动量还是反转”：对 crypto short-cycle desk，更该先拆成「ultra-short continuation × post-jump 1h sign fade」两条 raw alpha
- 时间：2026-04-10 00:47 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：lagged intraday return sign 会在不同持有窗上表现出可交易的 continuation / reversal；对 desk 更实用的读法是把它拆成超短 continuation sleeve 与 post-jump fade sleeve
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：intraday / momentum / reversal / horizon-router / jump / liquidity / BTC / ETH / XRP / 5m / 1m
- 证据类型：论文证据（摘要 / 搜索摘录）+ Binance USDⓈ-M 公共数据 portability probe

## 1. 这次看了什么
这次看的是 **Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao (2022), _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_, The North American Journal of Economics and Finance**。虽然正文页受限，但从 DOI / Crossref 元数据、DuckDuckGo / EconPapers 摘录可确认：论文主问题非常直接——**crypto 的日内收益，到底是延续、反转，还是两者并存？**

## 2. 核心结论
- **一句话核心结论：** 这篇东西最值钱的，不是泛泛说“crypto 也有 intraday predictability”，而是提示你：**同一个 lagged-return alpha，随着 horizon、jump 和 liquidity 状态切换，会在 momentum 与 reversal 间翻面。**
- **一句话证明方式：** 论文用 Bitcoin 高频样本（搜索摘录显示约 `2013-03-03 ~ 2020-05-31`）做主检验，并补充 ETH / LTC / XRP，结论是同时存在 intraday momentum 与 reversal，且模式会随 **large intraday price jumps、FOMC、liquidity、COVID-19** 改变；基于这些 intraday predictors 的 timing strategy 还能跑赢 always-long / buy-and-hold 基准。
- 这篇东西的 **base alpha 很清楚**：`lagged intraday return sign -> next short-horizon return sign/size`。不是情绪解释，不是宏观综述，而是一条可直接下手做 `1m/5m/15m` 最小实验的 raw alpha。
- 对我们 desk，更值得抄的不是“到底动量还是反转”这个 headline，而是把它拆成两条可复现子假设：
  1. **ultra-short continuation**：刚发生的 very-short impulse 往往还有 1 根左右的惯性；
  2. **post-jump sign fade**：当过去 `1h` 方向已经被 jump / 高流动性 bursts 推得过头，下一小段时间更像反手回吐，而不是继续追。
- 我用 Binance USDⓈ-M 公共 `BTC/ETH/SOL/XRP/ADA/DOGE` 做最近窗口 portability probe：
  - 在近约 `41d` 的 `5m` 数据上，若只看 **过去 1 根 `5m` 的方向**，next-bar signed return 平均约 **`+0.29 bps/bar`**，说明 ultra-short continuation 还活着；
  - 但若看 **过去 `12` 根 `5m`（约 `1h`）的方向**，未来 `4` 根的 signed return 平均约 **`-0.18 bps/4-bar`**，已经更像 reversal；
  - 若只看 recent jump bucket，`1h sign` 的未来 `4` 根 signed return 约 **`-1.95 bps`**；在 `jump + high-liquidity` bucket 里约 **`-2.09 bps`**，说明“涨/跌了一小时后再追”在 jump 状态下尤其危险。
- `1m` 上我也做了快检，但信号更噪：整体更像 **可见弱 edge、但不适合当前直接主攻**。高置信结论是：这条线优先级应是 **`5m` 先立 horizon router，再往 `1m/3m` 压缩**，而不是反过来。

## 3. 为什么和当前项目有关
最近 desk 已经补了不少 trend / carry / pairs / funding 线，但“**同样是短周期 lagged-return，什么时候该顺着打、什么时候该反着接**”这层还缺一篇真正贴近 crypto intraday 的母论文。它和当前项目直接相关，因为它提供的不是单个形态，而是一种更通用的 raw-alpha 拆法：
- `same-sign continuation sleeve`
- `overextended-jump fade sleeve`
- 再往外套 `jump / liquidity / macro timestamp` 这些 regime gate

换句话说，这篇可以同时服务：
- 单资产 micro-momentum
- shock 之后的短反转
- breakout / trend 信号的追涨否决层

## 3.5 策略拆解（必填）
- 方向属性：同一母信号可拆成 continuation 与 reversal 两个子 sleeve
- 基础 alpha：lagged intraday return sign 对下一小段收益有预测力
- regime：recent jump / non-jump；high-liquidity / low-liquidity；必要时叠 FOMC 等时点门控
- filter / veto：当过去 `1h` 的方向移动伴随 jump 与高流动性放大时，不要机械继续追方向单
- risk / sizing / execution overlay：先用 `bar-close -> next-bar` 和 `bar-close -> next-4-bar` 测 expectancy；过第一关后再加 taker/maker、time-stop、vol-target

## 4. 可复刻的最小实验
**研究假设 A（continuation sleeve）：** `5m` 上，过去 `1` 根 bar 的方向会在下一根继续一小段。  
**研究假设 B（fade sleeve）：** `5m` 上，过去 `12` 根 bar（约 `1h`）若已形成明显单边位移，且刚经历 jump / 高流动性放大，则未来 `1~4` 根更容易反向回吐。

**最小实验：**
1. 资产：Binance / OKX top-liquid perps，先 `BTC/ETH/SOL/XRP/ADA/DOGE`；
2. 周期：先 `5m`；
3. 信号：
   - Continuation：`sig_c = sign(ret_1bar)`；
   - Fade：`sig_f = -sign(ret_12bar)`，但只在 `abs(ret_1bar)` 进入近 `288` 根 `90%` 分位以上、且 quote volume 高于 rolling median 时启用；
4. 出场：先测持有 `1` 根与 `4` 根；
5. 对照：`always momentum` vs `always fade` vs `jump-gated router`。

**最先看 2 个指标：**
- `post-cost expectancy bps/trade`
- `jump bucket` 与 `non-jump bucket` 的 edge 差值是否稳定

## 5. 风险与保留意见
- 这篇论文当前我拿到的是 **摘要 / 搜索摘录级证据**，不是全文逐表复刻，所以 paper-level 数值细节不应过度脑补。
- 我本地 probe 用的是 **Binance perp 最近窗口**，与论文的 Bitstamp / 现货长样本并不等价；它只能说明 portability，不等于复现原文结果。
- 当前 probe 里 `5m` edge 仍偏小，若全吃 taker，很多版本会被成本吞掉；因此更合理的位置是 **router / veto / sleeve selector**，而不是无脑 every-bar 交易。
- `1m` 噪声显著更大，说明这条线不应先在最短周期上硬压榨。

## 6. 来源
- Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*. *The North American Journal of Economics and Finance*.
- DOI: `10.1016/j.najef.2022.101733`
- Readable URL: `https://doi.org/10.1016/j.najef.2022.101733`
- SSRN abstract DOI: `10.2139/ssrn.4080253`
- SSRN URL: `https://doi.org/10.2139/ssrn.4080253`
- Crossref metadata: `https://api.crossref.org/works/10.1016/j.najef.2022.101733`

## 7. 一句话带走
**别把这篇 paper 读成“动量和反转都存在”这种废话；对 desk 真有用的翻译是：`5m` 里 ultra-short impulse 还能顺着打一小段，但 `1h` 单边位移一旦叠上 jump / 高流动性，更该先测 fade 而不是继续追。**
