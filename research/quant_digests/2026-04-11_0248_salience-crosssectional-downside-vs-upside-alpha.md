# 别把这篇 2024 JBF 论文只读成 behavioral pricing 故事：对 short-cycle desk，更该先测的是「low-salience vs high-salience」这条横截面 raw alpha

- 时间：2026-04-11 02:48 UTC
- 类型：2024 *Journal of Banking & Finance* 论文全文（Liverpool repository PDF）+ Binance USDⓈ-M `5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**做多“最近一段路径里更容易让人盯住 downside 的币”（low ST），做空“最近一段路径里更容易让人盯住 upside 的币”（high ST）；本质是跨币种的 salience-driven mispricing fade。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（alpha 本体清楚，但当前 `5m/15m` transfer 还偏薄，先更像 cross-sectional sleeve / router，不像已能直接上线的完整策略）
- 主题标签：raw-alpha/cross-sectional/relative-value/behavioral/salience/overreaction/attention/mispricing/downside-vs-upside/long-short/binance-perpetual/15m/5m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文证据 + 公共数据 portability probe

## 1. 这次看了什么
主材料是：

- **Charlie X. Cai; Ran Zhao (2024)**
- **Title:** *Salience theory and cryptocurrency returns*
- **Venue:** *Journal of Banking & Finance*, Volume 159, Article 107052
- **DOI:** `10.1016/j.jbankfin.2023.107052`
- **Readable URL:** <https://doi.org/10.1016/j.jbankfin.2023.107052>
- **Full-text manuscript PDF:** <https://livrepository.liverpool.ac.uk/3182764/1/Salience_Theory_on_Cryptocurrency_Market%20%282%29.pdf>
- **Repo URL:** 无公开 repo（paper-only）

这篇东西值钱的地方，不是“behavioral finance 又来了一篇”，而是它把一个很容易讲虚的概念，直接压成了**可排序、可做多空、可横截面轮动**的量化定义：

> **ST（salience effect）= salience-weighted return − equal-weighted return。**

翻成人话：

> **不是看谁涨得多，而是看过去一段路径里，哪只币的“最抓眼球的 payoff”把投资者注意力扭歪得更厉害。**

如果一只币最近的显著状态主要是“上行 payoff 很抓眼”，作者预期它会被高估，后续收益更差；如果显著状态主要是“下行 payoff 很抓眼”，它反而更可能被低估，后续收益更好。

一句话核心结论：

> **真正该先拿走的不是 salience 叙事，而是 `long low-ST / short high-ST` 这条横截面 mispricing alpha。**

一句话证明方式：

> **作者用 2014–2021、4000+ 币的周/月度排序、LTW 三因子 alpha 与 Fama-MacBeth 回归，证明 high-ST 未来更差、low-ST 未来更强，而且这条效应不只是 short-term reversal / skewness / prospect theory 的重命名。**

## 2. 核心结论
1. **原论文里的 base alpha 很明确：** low-ST 多、high-ST 空。作者报告若做反过来的 `buy high-ST / sell low-ST`，月频组合是 **`-25.9%` EW / `-32.4%` VW**；等价地，正确方向就是 **`long low-ST / short high-ST`**。
2. **这不是只靠已知 crypto risk factors 就能解释掉的。** Table 3 显示 ST 组合在 LTW 三因子下仍有 **`3.2%` 周 alpha / `24.6%` 月 alpha**。
3. **它不是一句“彩票效应换个名字”。** 文中明确把 ST 与 momentum、reversal、prospect theory、skewness、downside beta 等做区分；作者的说法是，ST 在 crypto 里更强，而且与短期反转并不等价。
4. **对短周期 desk 最有价值的读法是：** 把它当成一个 cross-sectional router——不是追单币 breakout，而是持续问“现在谁被 upside story 追捧过头，谁被 downside scare 压得过头”。

## 3. 为什么和当前项目有关
当前 digest 池里虽然已经有很多 `MAX / lottery / skewness / reversal`，但这篇仍然不重复，因为它抓的不是：

- 单一 spike 多不多；
- 单一分布矩好不好看；
- 单根 bar 反不反打；

而是：

> **过去一段路径里，投资者注意力被哪类 payoff 扭曲得最厉害。**

所以它更像：

- **raw alpha**：横截面 long/short 排序本体；
- 兼容未来的 **universe router**：给 pairs / XS sleeves / relative-value book 做 rich-vs-cheap admission；
- 而不是单纯 filter / overlay。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / long-short
- 基础 alpha：`long low-ST (downside-salient) / short high-ST (upside-salient)`
- regime：更适合币种分化明显、attention 轮动明显的窗口
- filter / veto：先限于高流动性币池；stablecoin、极低成交额、异常事件币剔除
- risk / sizing / execution overlay：beta / dollar neutral；单腿权重上限；top-k 或 tercile 选币；分层 friction ladder

## 4. 本地 portability probe：Binance `5m/15m` 上，这条线现在像不像短周期 alpha？
我把论文里的 ST 思路缩成一个最小可移植版本：

- 标的：`BTC / ETH / SOL / XRP / DOGE / BNB / ADA / LINK / AVAX`
- `15m`：过去 `96` 根 bar 作为 formation window（约 1 天）
- `5m`：过去 `288` 根 bar 作为 formation window（约 1 天）
- 每根 bar 先算 cross-sectional salience，再对每个币算 `ST = salience-weighted return − equal-weighted return`
- 下一根做：**long bottom 30% ST，short top 30% ST**

本地 artifacts：

- `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_detail_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_last50_15m_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_last50_5m_2026-04-11.csv`

### 4.1 `15m`：方向对了，但毛边还薄
- 平均 next-bar long-short spread：**`+0.43 bps`**
- `t ≈ 1.72`
- 胜率：**`50.8%`**
- long low-ST 腿：**`+0.21 bps`**
- short high-ST 腿：**`-0.22 bps`**

翻成人话：

> **low-ST / high-ST 的方向在 `15m` 上没有翻车，但当前毛边远没厚到足以直接吃掉 `2/4/6 bps` 成本。**

### 4.2 `5m`：更弱，暂时不值得直接当主 lane
- 平均 next-bar long-short spread：**`+0.16 bps`**
- `t ≈ 1.03`
- 胜率：**`51.7%`**

这说明：

> **如果把 salience 直接硬压成“下一根就反映”的 ultra-short alpha，它现在不够强。**

### 4.3 `15m` 更像 sleeve router，不像全市场一把梭
按单币被选中后的 next-bar 表现看，`15m` 上较正面的主要是：

- `LINK`: low-minus-high 约 **`+3.67 bps`**
- `XRP`: 约 **`+1.93 bps`**
- `SOL`: 约 **`+1.46 bps`**
- `ETH`: 约 **`+0.99 bps`**
- `BNB`: 约 **`+0.87 bps`**

但 `DOGE / ADA / BTC` 这轮并不帮忙，说明这条线当前更像：

> **在高 beta、attention 更容易失真的子宇宙里做 cross-sectional router，可能比全 market-neutral 硬铺更合理。**

## 5. 风险与保留意见
1. **论文频率比我们慢很多。** 原文是周/月 formation + 周/月 holding；我这里压到 `5m/15m`，本来就属于 transfer test，不是原样复刻。
2. **当前 next-bar 版本过薄。** `15m +0.43 bps`、`5m +0.16 bps` 都扛不住正常 taker 成本。
3. **没有 repo，只有 paper。** 好处是理论与公式清楚；坏处是工程复现得自己补。
4. **这条线容易和 lottery / skewness / reversal 混淆。** 但 salience 真正的独特点是：它不是某个单指标值，而是**一段路径里的注意力扭曲权重**。

## 6. 可复刻的最小实验
### 数据源 / 公开性 / 更新频率
- Binance USDⓈ-M `fapi/v1/klines`
- 公开可抓
- `1m/3m/5m/15m` 都可映射；本轮优先 `15m`

### 最小研究假设
> 在短周期横截面里，最近一段路径更“upside-salient”的币，未来几根更容易相对跑输；更“downside-salient”的币，未来几根更容易相对跑赢。

### 最小回测切口
- 宇宙：先只做 `ETH / SOL / XRP / LINK / BNB / AVAX` 这类高流动性 alt，暂时把 `BTC` 这种“注意力锚”剔除成 benchmark
- 周期：`15m`
- formation：过去 `96` 根 bar
- holding：不要只看 next bar，优先测 **`2 / 4 / 8 bars`**
- 组合：`top1-bottom1`、`top2-bottom2`、`tercile` 三种壳并排
- 先看两件事：
  1. gross spread bps 是否从 `+0.43` 提厚到能过 `2 bps`
  2. edge 是否主要集中在 alt sleeve，而不是全宇宙平均

## 7. 下一步怎么测
1. **先把 holding horizon 拉长**：别执着 next-bar；这篇 paper 的母体本来就不是 single-bar alpha，优先测 `15m` 持有 `2/4/8` 根。
2. **改成 alt-only sleeve**：先测 `ETH/SOL/XRP/LINK/BNB/AVAX`，把 `BTC/DOGE/ADA` 这种会稀释信号的币与高噪音币分开。
3. **做更稀疏的 top-k 壳**：`top1-bottom1` 或 `top2-bottom2`，而不是默认全 tercile；当前 edge 看起来更像集中分布。
4. **显式 friction ladder**：至少跑 `2 / 4 / 6 bps`，若 `4 bps` 下仍死，就把它降级为 XS router，而不是独立策略。
5. **和已有 lottery / skewness sleeve 做 pairwise compare**：不是为了再造一个重复因子，而是验证它到底有没有额外信息量。

## 8. 来源
- Cai, Charlie X.; Zhao, Ran. (2024). *Salience theory and cryptocurrency returns*. *Journal of Banking & Finance*, 159, 107052.
  - DOI: <https://doi.org/10.1016/j.jbankfin.2023.107052>
  - Readable URL: <https://linkinghub.elsevier.com/retrieve/pii/S0378426623002388>
  - Full-text manuscript PDF: <https://livrepository.liverpool.ac.uk/3182764/1/Salience_Theory_on_Cryptocurrency_Market%20%282%29.pdf>
  - Repo URL: 无公开 repo
- 本地 portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_summary_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_detail_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_last50_15m_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/salience_crypto_probe_last50_5m_2026-04-11.csv`
