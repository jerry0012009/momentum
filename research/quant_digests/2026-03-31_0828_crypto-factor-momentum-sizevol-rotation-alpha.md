# 别把 crypto factor 只当日频资产配置：更该先测的是「size / vol sleeve winner rotation」横截面 raw alpha

- 时间：2026-03-31 08:28 UTC
- 类型：2023 *Quantitative Finance* 摘要级证据 + 2022 NBER/2022 *Journal of Finance* 全文 PDF + 2024 *Mathematics* 开放获取摘要
- 主题标签：raw-alpha/cross-sectional/relative-value/factor-momentum/size/volatility/momentum/market-neutral/binance/perpetual/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：论文（1 篇全文细读 + 2 篇摘要/元数据）
- 主题类型：raw alpha
- 基础 alpha：先做可独立交易的横截面 factor sleeves（small-minus-big、low-vol-minus-high-vol、winner-minus-loser），再按这些 sleeves 自身近窗收益做 winner-minus-loser 轮动
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
不是再补一个“单币 K 线形态”，而是补一条当前素材池里还偏缺的 **factor-sleeve / factor-momentum** 主线。核心证据来自两层：

1. **Liu, Tsyvinski, Wu (2022, *Journal of Finance*；NBER w25882 working paper 2019版全文可得)**：在 2014–2018、`109 → 1,583` 个市值超过 100 万美元的币样本里，25 个 price / market-based 特征中有 `9` 个能形成显著 long-short 超额收益；其中最稳的是 **size、1~4 周 momentum、dollar volume、dollar-volume volatility**。作者进一步指出，crypto 横截面可被一个 **market + size + momentum** 三因子模型较好刻画。
2. **Fieberg, Metko, Zaremba (2023, *Quantitative Finance*)**：在 `3900+` 币、`2014–2022` 的 34 个 anomaly sleeves 上，作者发现 **factor momentum** 存在：过去赢的因子继续赢，过去输的继续输；这个效应主要来自 **size 与 volatility anomalies**，而且 crypto 的 factor momentum 还会从 price momentum 传导到 factor 层。
3. **Seabe, Moutsinga, Pindza (2024, *Mathematics*)**：在 `31` 个主流币、`2017-12 ~ 2023-12` 的周频框架下，作者再次发现 **momentum 与 value** 对 crypto 收益有显著预测力，说明“先搭 factor sleeve、再谈组合轮动”不是纯学术玩具。

## 2. 先回答：这篇东西的 base alpha 是什么？
**base alpha 不是 filter，也不是 overlay。**

它的 base alpha 很明确：

- **第一层 raw alpha**：做横截面 long-short factor sleeves；
  - small minus big
  - low dollar-volume-vol minus high dollar-volume-vol
  - short-horizon winner minus loser
- **第二层 raw alpha**：不把这些 sleeves 静态等权，而是做 **factor momentum**——最近表现最强的 sleeve 继续加权，最弱的 sleeve 降权或反向。

这就是一个可以单独跑的完整 market-neutral / relative-value alpha，不需要依赖 breakout、retest、pattern 之类主线来“附着生存”。

## 3. 为什么它值得进当前 desk 的研究池
当前池子里已经有不少：

- 单币短周期动量 / 均值回复
- 跨资产 lead-lag
- same-underlier stat-arb / pairs
- funding / basis / options 价差

但 **“标准化 factor sleeves → sleeve 轮动”** 这条线还不够完整。它的价值在于：

1. **它本身就是 raw alpha**，不是只服务别人的 gate。
2. **它天然能服务至少两类后续工作**：
   - 直接当 market-neutral 主策略；
   - 给后续 microstructure / carry / stat-arb 提供“只在某类 sleeve 里开仓”的 universe router。
3. **它跟短周期执行并不冲突**：信号未必每根 `5m` 都刷新，但完全可以用 `15m/5m` 去执行与控风险。

## 4. 论文里最值得 desk 先抄的，不是“全部 34 个 anomaly”
如果照学术论文一口气复刻 34 个 anomaly sleeves，工程量太大，而且很多特征在 perp 场景里并不干净。

**更适合 desk 的旁支读法** 是：先只做最便宜、最公开、最能快速迁移到 perp 的 3 个 sleeve：

1. **Size sleeve**
   - 学术定义里，small-minus-big 很强。
   - Liu et al. 给出的 weekly 5-1 excess return：
     - `MCAP`: `-3.4%/week`，`t = -2.557`
     - `PRC`: `-3.9%/week`，`t = -2.420`
     - `MAXDPRC`: `-4.1%/week`，`t = -2.483`
   - desk 上不一定非得用全市场 cap；可先用 **流动性 / ADV / OI proxy 的“小票 vs 大票”** 替代，先看是否还有“small basket outperforms”结构。

2. **Short-horizon momentum sleeve**
   - Liu et al. 里最有意思的是 **短 momentum 有效，长 momentum 反而不稳**：
     - `1w mom`: `+2.7%/week`，`t = 1.994`
     - `2w mom`: `+3.3%/week`，`t = 2.442`
     - `3w mom`: `+4.1%/week`，`t = 2.742`
     - `4w mom`: `+2.5%/week`，`t = 2.002`
     - 但 `8w / 16w / 50w / 100w` 都不显著
   - 这很适合我们把 lookback 压到更短：`24h / 72h / 7d`，然后用 `15m` 执行。

3. **Low-vol sleeve（更准确地说是 low dollar-volume-vol）**
   - Liu et al. 的 `STDPRCVOL` 5-1 为 `-3.0%/week`，`t = -2.269`。
   - 直译就是：**long 低 dollar-volume-vol，short 高 dollar-volume-vol**。
   - Fieberg et al. 又补了一层：factor momentum 的自相关主要就来自 **size 与 volatility anomalies**。这意味着 low-vol sleeve 不只可单跑，还可能适合做“赢者加权”。

## 5. 对短周期 desk，最像完整策略的版本
### 策略骨架
- **方向**：cross-sectional / market-neutral / relative-value
- **交易对象**：Binance USDⓈ-M perpetual 主流流动性币池
- **alpha 结构**：`size sleeve + vol sleeve + short-horizon momentum sleeve`
- **组合层**：对 sleeves 做 factor momentum rotation

### 最小可复现实验
**Universe**
- 过去 `30d` 日均成交额前 `20~40` 个 USDT perp
- 上线满 `90d`
- 过滤极低价币、异常 funding、持续限价保护标的

**Signal construction（先做 3 个 sleeve）**
1. **size proxy**：过去 `7d` 的 ADV / OI / quote volume 排序
   - long bottom 30%
   - short top 30%
2. **vol sleeve**：过去 `7d` 的 dollar-volume volatility 或 quote-volume volatility 排序
   - long bottom 30%
   - short top 30%
3. **mom sleeve**：过去 `24h / 72h` 收益排序
   - long top 30%
   - short bottom 30%

**Factor-momentum overlay**
- 计算每个 sleeve 自身过去 `1d / 3d / 5d` 的 long-short PnL
- 只保留最近最强的 `1~2` 个 sleeve，弱 sleeve 降到零或半权
- 也可做更保守版本：
  - if sleeve trailing z-score > 0：开权
  - else：停权

**Execution**
- sleeve 成员每 `4h` 刷一次
- 订单在 `15m` 上分两到三笔 TWAP 进场
- 单个 position 默认持有 `4h~24h`
- `5m` 只负责微观执行与风控，不强行把 factor 信号伪装成每根 K 线都更新的主信号

**Sizing / risk**
- 组合先做美元中性，再做 BTC beta 近中性
- 单币权重上限 `10%`
- 单 sleeve 风险预算上限 `40%`
- 若可交易币数 `< 12`，直接不做
- funding / fee / spread 过高的币只可入 short list，不可强行双边对冲

**Cost 假设**
- 先用 `10 bps` one-way 全包成本做第一轮否决
- 第二轮再拆成 maker / taker / slippage / funding
- 如果 turnover 高到把 size / vol sleeve 吃没，优先降 refresh 频率，不要先乱调阈值

## 6. 这条线最该先看什么，不该先看什么
### 最该先看
1. **sleeve 自身是否仍有净边**，尤其是 `mom(24h/72h)` 与 `low-vol`
2. **sleeve momentum 是否真能筛掉烂 sleeve**
3. **边是否集中在某些 regime**：大盘 trend、alt season、risk-off 周

### 不该先做
1. 一上来堆满 20+ academic anomalies
2. 没确认 sleeve PnL 序列可交易，就急着做复杂 optimizer
3. 把低频 factor ranking 硬装成逐笔高频 alpha

## 7. 我对这条线的判断
这条线现在最有价值的地方，不是“论文说 crypto 也有 factor zoo”，而是：

**它给了我们一条能独立落地、又能和现有 raw alpha 池互补的标准化横截面主线。**

如果近期想继续补 **raw alpha 素材池**，我会把优先级放成：

1. `short-horizon momentum sleeve`
2. `low-vol sleeve`
3. `size sleeve`
4. `winner sleeve rotation`

也就是先把最容易用公开交易所数据复现的部分搭起来，再决定要不要把 value / on-chain 因子补进来。

## 8. 下一步怎么测
直接做一个 **3-sleeve × 3-lookback** 的最小矩阵，不要一次搞大：

1. **sleeves**：`size / low-vol / momentum`
2. **lookback**：
   - sleeve ranking：`24h / 72h / 7d`
   - sleeve momentum：`1d / 3d / 5d`
3. **holding**：`4h / 12h / 24h`
4. **execution**：统一 `15m` TWAP，记录 `5m` 实际滑点
5. **输出指标**：
   - gross / net spread return
   - turnover
   - capacity proxy（ADV 占比）
   - BTC beta
   - sleeve-level hit rate
   - factor-momentum 开关前后 Sharpe 变化

如果第一轮结果显示：
- **静态 sleeve 有边，但 rotation 没增益**：保留 sleeves，砍掉 factor momentum。
- **rotation 只在 trend 周期有效**：把它降级为 regime-gated overlay。
- **只有 momentum sleeve 活着**：那就诚实收缩成“XS momentum 主策略 + size/vol 只做 admission”。

## 9. 来源
1. **Liu, Y., Tsyvinski, A., & Wu, X. (2022). _Common Risk Factors in Cryptocurrency_. The Journal of Finance.**  
   - Working paper / readable PDF: https://www.nber.org/papers/w25882  
   - DOI (journal): https://doi.org/10.1111/jofi.13119  
   - NBER PDF: https://www.nber.org/system/files/working_papers/w25882/w25882.pdf
2. **Fieberg, C., Metko, D., & Zaremba, A. (2023). _Cryptocurrency factor momentum_. Quantitative Finance.**  
   - DOI: https://doi.org/10.1080/14697688.2023.2269999  
   - Readable URL: https://onlinelibrary.wiley.com/doi/10.1080/14697688.2023.2269999
3. **Seabe, P. L., Moutsinga, C. R. B., & Pindza, E. (2024). _Optimizing Cryptocurrency Returns: A Quantitative Study on Factor-Based Investing_. Mathematics, 12(9), 1351.**  
   - DOI: https://doi.org/10.3390/math12091351  
   - Readable URL: https://www.mdpi.com/2227-7390/12/9/1351
