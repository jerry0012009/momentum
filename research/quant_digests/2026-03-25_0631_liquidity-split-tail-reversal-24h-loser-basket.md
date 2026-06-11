# 别把 `last-day return` 当全市场同向信号：这篇 2021 论文更值得先测的是「流动性分层的 24h loser-basket reversal」短周期 raw alpha
- 时间：2026-03-25 06:31 UTC
- 类型：近 5 年论文 + Binance Futures 公共 15m K 线最小快检
- 主题类型：raw alpha
- 基础 alpha：过去 24h 的横截面收益在较低流动性、但仍可交易的币篮子里更像过度反应；因此对 tail bucket 做 `long losers / short winners`，而不是把同一信号统一当成全市场 momentum
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/liquidity-split/last-day-return/loser-basket/short-term-reversal/momentum/binance/perpetual/15m/1h/4h/paper
- 证据类型：论文证据 + 本地公共数据快检

> 先回答 base alpha：**不是 shared filter，也不是纯解释。base alpha 就是“按流动性分层后的横截面收益延续/反转错配”——对 desk 来说，当前最值得先拿来做短周期实验的是 tail bucket 的 `24h loser-basket reversal`。**

## 1) 这次看了什么
主线材料是：
- **Adam Zaremba, Mehmet Huseyin Bilgin, Huaigang Long, Aleksander Mercik, Jan J. Szczygielski (2021), _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_**

我这轮不把它读成“日频文献综述”，而是把它翻成对我们 desk 更有用的一句：

**同一个过去 24h 收益信号，在不同流动性层上的方向不必一样。**

论文主结论里最值钱的分叉是：
- 大量币的低前一日收益，后面更容易反弹（reversal）
- 但少数最大、最可交易的币，反而更偏 momentum

对当前 desk，我认为更该先 intake 的不是“把两条腿都硬上”，而是：

**先把更容易映射到 Binance perp、且更像独立 raw alpha 的那一腿——`tail loser reversal`——单独拉出来做 fast-cycle 版最小实验。**

## 2) 核心结论
- **一句话核心结论：** 不要把 `last-day return` 当统一方向信号；对短周期 desk，更值得先复现的是**流动性分层后的 tail reversal raw alpha**，而不是默认大币 momentum 也会同步成立。
- **一句话证明方式：** 2021 论文在 **3600+** 个币上发现“输家反转、超大流动性币更偏动量”的分层现象；我再用 Binance 永续 **15m** 公共数据做快检，发现成熟次级流动性币篮子的 `24h loser-basket reversal` 在 `1h/4h` 持有上仍有正的净信号，而大币 momentum 腿在最近样本里反而持续为负。

3 个关键数据点：
1. **论文原始发现**：基于 **3600+** 个加密货币的日频横截面，**低 last-day return 组合显著跑赢高 last-day return 组合**；作者把它解释为**广泛存在的 illiquidity / overreaction**，并明确指出**少数最大、最可交易的币更接近 momentum 而非 reversal**。
2. **本地快检（Binance USDⓈ-M，近 90 天，15m bars，rolling 24h rank）**：在 `ADA/LINK/AVAX/TRX/LTC/BCH` 这组成熟 tail bucket 上，做 `long bottom-third / short top-third` reversal，**1h 持有**口径的平均净收益约 **+0.942 bps / rebalance**，净 Sharpe 约 **1.758**。
3. 同一快检里，大币 `BTC/ETH/SOL/XRP/DOGE/BNB` 的 momentum 腿在 `15m / 1h / 4h` 三个持有窗都为负：例如 **1h 持有**时平均净收益约 **-2.055 bps / rebalance**，说明**至少在当前 fast-cycle 映射口径里，不能把“高流动性币 momentum”当默认成立。**

## 3) 为什么和当前 desk 直接相关
- 这是 **raw alpha**，不是 filter。
- 它补的是我们当前研究池里更应该继续扩充的一块：**cross-sectional / relative-value / short-term reversal**，而不是再往 breakout 单线里内循环。
- 它很适合映射到 `15m` 生成信号，再落到 `5m / 3m / 1m` 执行：
  - 信号慢变量：过去 24h 相对表现
  - 执行快变量：盘口、spread、funding、成交冲击
- 更重要的是，这条线天然自带**对照组**：
  - tail reversal
  - majors momentum
  这能让我们很快知道“信号本身有用”，还是“只是在错误 bucket 上做了错误方向”。

## 3.5) 策略拆解（必填）
- 方向属性：cross-sectional / mean-reversion（主腿）
- 基础 alpha：过去 24h 的相对输家，在较低流动性但仍可交易的币篮子中更容易发生短期反弹
- entry：
  - 每个 15m bar 计算 bucket 内过去 `24h` 收益排名
  - 在 tail bucket 内：`long bottom-third losers`，`short top-third winners`
- exit：
  - 先从 `1h` 与 `4h` 两档持有窗开始
  - 或当 z-score / 相对收益回到中性带时提前平仓
- sizing：
  - 先等权 long-short
  - 第二步再改成 `inverse-vol` 或 `ADV-cap` 限制仓位
- risk / veto：
  - 单币 notional 上限
  - funding 极端同向时降权
  - spread / 成交额 / open-interest 异常时 veto
  - 只做成熟可交易尾部，不碰新上币和极端事件币
- cost：
  - 必须显式加入手续费 + spread
  - 本次快检用的是**5 bps one-way per unit turnover** 的简化成本口径

## 4) 这条线最该怎么读：不是“论文 headline 照抄”，而是“挑最适合 desk 的那一腿”
如果机械照抄论文 headline，很容易写成：
- “输家反转 + 大币动量，同时做”

但对当前 desk，更诚实的做法应该是：
1. **先把 tail reversal 当主策略候选**
2. **把 majors momentum 当强制对照腿**
3. 如果对照腿在当前市场不工作，就不要为了尊重论文而硬保留

换句话说：
**这轮最值钱的不是‘论文说了 reversal 和 momentum 都存在’，而是‘我们可以很快验证到底哪一腿还能活着进素材池’。**

## 5) 可复刻的最小实验（5m/15m 起步）
**数据源与公开性**：
- 数据源：Binance USDⓈ-M Futures Klines
- 公开性：公开可得，无需 API key
- 更新频率：`1m / 3m / 5m / 15m` 均可

**最小实验口径**：
- buckets：
  - majors：`BTC/ETH/SOL/XRP/DOGE/BNB`
  - tail：`ADA/LINK/AVAX/TRX/LTC/BCH`
- signal：过去 `24h` 横截面收益排序
- rebalance：每 `15m`
- holding：先测 `1h / 4h`
- cost：`fee + spread`，先用 `5 bps one-way` 粗口径，再做 maker/taker 拆分

**最先看 5 个指标**：
1. `avg net bps / rebalance`
2. `net Sharpe`
3. `turnover`
4. `bucket stability`（换 bucket 后还成不成立）
5. `cost break-even`（几 bps 之上 edge 才死）

## 6) 下一步怎么测（直接可执行）
1. **先做更诚实的 bucket 构造**：不要只按当下成交额拍脑袋分组；改成 `rolling ADV + listing age + spread` 三维筛选，避免新上币和事件币污染 tail bucket。
2. **把 24h 信号切成多尺度**：并行测 `6h / 12h / 24h / 48h` 排名，看这条 edge 到底更像“隔夜反转”还是“更长窗口的拥挤回吐”。
3. **做执行下钻**：信号仍在 `15m` 生成，但执行改到 `5m / 3m / 1m`，比较 `close-entry` 与 `VWAP-slice` 两种入场方式，确认 edge 是不是被开仓冲击吃掉。
4. **加 funding / OI overlay**：如果 loser 同时伴随 crowding unwind（负 funding 修复 / OI 回落），看是否能把 tail reversal 的质量再提高一档。
5. **做完全对照矩阵**：
   - tail reversal
   - tail momentum
   - majors reversal
   - majors momentum
   不要只回测“自己喜欢的那条腿”。

## 7) 风险与保留意见
- 论文是**日频横截面**，我这里做的是**短周期 desk 映射**，两者不是同一层级，不应假装是“全文复现”。
- 本地快检只是最小 sanity check，不是最终生产回测。
- 这次 `1h / 4h` forward-return 口径存在**重叠持有窗**，所以这里更应看 **avg bps / Sharpe**，不应把累计收益当最终实盘曲线。
- tail bucket 的定义对结果很敏感；如果混入新币、事件币或超低流动性币，结论会被严重污染。

## 8) 来源
1. **Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_. International Review of Financial Analysis, 78, 101908.**
   - DOI: `10.1016/j.irfa.2021.101908`
   - Readable URL: `https://doi.org/10.1016/j.irfa.2021.101908`
2. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance, 62, 101733.**
   - DOI: `10.1016/j.najef.2022.101733`
   - SSRN DOI: `10.2139/ssrn.4080253`
   - Readable URL: `https://doi.org/10.1016/j.najef.2022.101733`
   - 说明：本轮主要把它当 companion reference，用来确认“动量 / 反转并存”这个研究方向，而非直接抽取详细估计值。
3. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9) 本地产物
- `reports/artifacts/quant_digests/liquidity_split_tail_reversal_20260325/summary.json`
- `reports/artifacts/quant_digests/liquidity_split_tail_reversal_20260325/summary.csv`
- `reports/artifacts/quant_digests/liquidity_split_tail_reversal_20260325/notes.txt`
