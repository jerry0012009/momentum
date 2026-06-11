# 别把这篇 2022 *Financial Review* BTC 论文只读成“固定时钟效应”：对 short-cycle desk，更该先测的是「pseudo-open overnight sign × pseudo-close half-hour continuation」这条 raw alpha

- 时间：2026-04-13 12:20 UTC
- 类型：2022 *The Financial Review* 论文全文可读版（University of Reading accepted version）+ Crossref 元数据 + Binance USDⓈ-M `5m` public-data portability probe
- 主题标签：raw-alpha/intraday/single-asset/time-series-momentum/pseudo-session/pseudo-open/pseudo-close/overnight-sign/half-hour-continuation/btc/eth/sol/binance-perpetual/5m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文 + 元数据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**把“前一 pseudo-close 到当天 pseudo-open+30m 的 overnight+early-session 方向”当成主信号，去交易同一 pseudo-day 最后 30 分钟的同向 continuation；也就是 `r_ONFH -> r_LH`，而不是泛泛地说“BTC 有固定时钟 seasonality”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么

这轮看的是一篇 2022 年的 BTC 日内动量论文。它真正值钱的地方，不是“BTC 某个 UTC 时段常涨常跌”这种 seasonality 概括，而是一个更尖锐、也更容易翻成 desk 语言的命题：

> **pseudo-day 开头那段 overnight + first-30m 的方向，能不能预测同一 pseudo-day 最后 30 分钟的方向？**

论文原始表达是：
- Bitcoin 没有股票那种天然开收盘；
- 所以作者用**成交量尖峰**当作“开盘”代理，用 **5pm EST**（CME Bitcoin futures 日内休市开始）当“收盘”代理；
- 然后测试 `first half-hour / overnight+first-half-hour` 能否预测 `last half-hour`。

翻成人话就是：
- 这不是普通的“开盘追涨”；
- 也不是简单的“某个小时更强”；
- 它更像一条**伪会话（pseudo-session）内的首尾动量传导 alpha**。

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = `r_ONFH -> r_LH` 的同向传导。**
> 其中 `r_ONFH` 是“上一 pseudo-close 到本 pseudo-open+30m”的收益，`r_LH` 是“本 pseudo-close 前最后 30m”的收益。

为什么这仍然是 `raw alpha`，不是 `filter / regime / overlay`？

因为它本身就能独立定义：
1. **entry**：用 `r_ONFH` 的符号给出方向；
2. **holding window**：只持有 pseudo-close 前最后 30m；
3. **exit**：pseudo-close 平掉；
4. **risk**：可直接做 fixed notional / fixed risk cap；
5. **cost**：可以直接压 taker/maker 假设去看净值是否还活着。

也就是说，这条线不是“依附别的信号才成立”的 gate，而是一条可以单独回测的 session-pocket raw alpha。

## 3. 来源

### 主来源（paper）
- **Authors：** Dehua Shen, Andrew Urquhart, Pengfei Wang
- **Year：** 2022
- **Title：** *Bitcoin intraday time series momentum*
- **Venue：** *The Financial Review*, 57(2), 319–344
- **DOI：** <https://doi.org/10.1111/fire.12290>
- **Readable URL：** <https://centaur.reading.ac.uk/100181/>
- **Publisher URL：** <https://onlinelibrary.wiley.com/doi/10.1111/fire.12290>
- **Repo URL：** N/A

### 元数据复核
- **Crossref JSON：** <https://api.crossref.org/works/10.1111/fire.12290>

### 本轮本地 artifacts
- Probe script：`reports/artifacts/quant_digests/2026-04-13_pseudoopen_pseudoclose_tsmom_probe.py`
- Probe metrics：`reports/artifacts/quant_digests/2026-04-13_pseudoopen_pseudoclose_tsmom_probe_metrics.csv`

## 4. 论文里真正值得 desk 记住的点

### 4.1 作者不是随便拍脑袋选时段
论文里给的 pseudo-session 锚点是：
- **open proxy**：成交量尖峰附近；
- **close proxy**：**5pm EST**，因为 CME Bitcoin futures 在这个点开始 60 分钟休市；
- 另外作者还强调了 **8:30am ET** 的 GDP / CPI 宏观发布时间，所以 overnight+early-session 段天然会吸纳一部分“先于美股开盘被 BTC 定价”的信息。

所以它的真正读法不是“5pm 有 magic”。
而是：
> **BTC 会不会先在 pseudo-open 吃掉 overnight / macro / 流动性冲击，再把方向传导到 pseudo-close 前最后半小时？**

### 4.2 论文摘要给出的主结论
作者摘要里给了三条对 desk 最有用的信息：
1. **first half-hour 正向预测 last half-hour**；
2. **高 volume / 高 volatility 的 first session，预测力更强**；
3. 这条线更像**liquidity provision 驱动**，不是 late-informed trading。

如果这三句能迁移到当前 perp desk，最自然的翻译就是：
- 优先把它当成 **BTC single-asset session-pocket continuation alpha**；
- 再在上面加 volume / vol / order-flow gate；
- 最后决定它更适合 `5m` taker，还是 `1m/3m` maker-first。

## 5. 为什么它值得进当前研究池

它值得写进池子，不是因为“又找到一个固定时段”，而是因为它补的是一块**当前 raw alpha 素材池里相对少见的 session-internal sign handoff**：

1. **它是 raw alpha，不是解释型综述。**
   - 方向、持有窗口、平仓点都明确；
   - 不依赖外部非公开数据；
   - 公共 K 线就能做最小实验。

2. **它和已有 clock/seasonality digest 不完全同义。**
   - 这条线重点不在“哪个时段均值为正”；
   - 而在“首段收益是否把尾段方向带过去”。

3. **它天然适合做拆件。**
   - `volume-spike open` 可以替换成 Binance perp 自己的 volume-rank open；
   - `5pm EST close` 可以替换成 DST-aware 或 fixed-UTC pseudo-close；
   - `r_ONFH` 还可以再拆成 `overnight` 与 `first 30m` 两段。

## 6. 我这次怎么做最小 portability probe

### 6.1 probe 口径
- **市场：** Binance USDⓈ-M Perpetual
- **标的：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **频率：** `5m`
- **样本：** 近约 `139` 个 pseudo-sessions（约 2025-11-23 到 2026-04-13）
- **pseudo-open proxy：** `13:30 UTC -> 14:00 UTC`，近似论文里的 `08:30 -> 09:00 EST`
- **pseudo-close proxy：** `21:30 UTC -> 22:00 UTC`，近似论文里的 `16:30 -> 17:00 EST`
- **主信号：** `sign(r_ONFH)`
- **交易段：** 只交易最后 `30m` 的 `r_LH`
- **成本：** 当前先看 gross，不含 fee / slippage / funding

### 6.2 这个 probe 故意保留了什么，省略了什么
保留的：
- 论文核心骨架：`r_ONFH -> r_LH`
- pseudo-open / pseudo-close 结构
- high-volume 对照

省略的：
- 真正“按 volume spike 动态找 open”
- 美东 DST 切换
- 盘口级 liquidity-provision 解释
- 交易所现货拼接（论文是多所 BTC 现货）

所以这轮 probe 的定位很明确：
> 不是复刻原文，而是先看这条 raw alpha 骨架在当前 Binance perp 上还剩多少味道。

## 7. 关键结果：论文里的 raw alpha 结构能复现，但**当前直译版很弱**

### 7.1 BTC：有一点 gross，但远没有到“可直接上线”的程度
`BTCUSDT | 5m | 139 pseudo-sessions`
- `sign-hit`：**53.96%**
- `gross`：**+3.33 bps / session**
- `median`：**+2.57 bps / session**
- `r_ONFH -> r_LH` 线性关系：**β = -0.004，p = 0.804，R² = 0.05%**

这组数的意思很直白：
- 如果只看“方向对没对”，它**勉强高于 50%**；
- 但线性解释力几乎没有；
- gross 也只是在成本前勉强露头。

所以当前最合理的判断不是“论文失效”，而是：
> **这条 alpha 还在，但直译成 fixed-UTC + pure taker 的版本，味道已经非常淡。**

### 7.2 论文说“高 volume 更强”，但 recent Binance perp 里没有复现
`BTCUSDT`
- 高 volume tercile `sign-hit`：**48.94%**
- 低 volume tercile `sign-hit`：**56.52%**

这点很重要，因为它直接告诉我们：
- 论文里的“high-volume stronger”**不能直接照搬**到当前 perp；
- 至少在这段 recent sample 上，volume 不能当成无脑绿灯；
- 真正该测的可能不是“高 volume”，而是**macro-release volume spike / US-hours volume spike / funding-reset-adjacent volume spike** 这些更细分的 session state。

### 7.3 ETH / SOL 没有给出更干净的迁移
`ETHUSDT`
- `sign-hit`：**50.36%**
- `gross`：**+4.90 bps / session**
- `r_ONFH -> r_LH`：**p = 0.658**

`SOLUSDT`
- `sign-hit`：**49.64%**
- `gross`：**+5.02 bps / session**
- `r_ONFH -> r_LH`：**p = 0.508**
- 反而 `r_SLH -> r_LH` 稍有一点末端自相关：**β = 0.216, p = 0.028**

翻成人话：
- 这条线不是“随便扩到 majors 就更强”；
- ETH/SOL 没给出明显更漂亮的首尾动量传导；
- SOL 倒更像**尾盘内部 60m -> 30m 的末端惯性**，而不是论文原本那条 pseudo-open to pseudo-close alpha。

## 8. 对当前 desk 的落点：先别把它当 broad session alpha，更像一个待拆的 BTC raw-alpha pocket

我现在对它的结论是：

1. **它仍然是 raw alpha 候选。**
   - 因为 entry/exit 足够明确；
   - 因为用公开数据可复现；
   - 因为不是单纯解释机制。

2. **但当前不适合直接当完整策略上线。**
   - recent Binance perp 直译版太弱；
   - volume 过滤没有复现论文主结论；
   - 跨资产扩展也不干净。

3. **更合理的定位是：BTC pseudo-session router 的一个子模块。**
   - 可以跟已有 `US close / NYSE open / pseudo-session open` 相关 digest 组合对照；
   - 也可以和 funding / OI / top-trader / OFI 这类 state 叠加，看看什么时候首尾传导才会变强。

## 9. 如果要继续拆，最值得先拆哪三刀

### 9.1 不要把 `r_ONFH` 当整体，先拆成两段
拆成：
- `overnight return`（prev close -> pseudo-open）
- `first 30m return`（pseudo-open -> pseudo-open+30m）

因为 desk 真正要知道的是：
- 是 overnight gap 在传导？
- 还是 macro release 后 first 30m 的 order-flow 在传导？
- 还是两段方向一致时才有 alpha？

### 9.2 不要再用 fixed UTC，当成最终版
下一轮要直接比较：
- `fixed EST proxy`
- `fixed ET/DST-aware proxy`
- `volume-spike detected pseudo-open`
- `funding-reset-adjacent pseudo-close`

否则现在这个 fixed-UTC probe 很可能把真正的 session state 稀释掉了。

### 9.3 volume filter 要改成“事件型 volume”，不是粗暴 tercile
论文里的 high-volume stronger，更可能是：
- 宏观数据发布时的集中交易；
- 美股 / CME 相关会话的 liquidity handoff；
- 不是“日常任何高成交日”都更强。

所以要优先测试：
- CPI / GDP / FOMC days
- US cash-equity open-adjacent days
- funding extreme + volume spike 共振 days

## 10. 策略拆解（当前版本）

- 方向属性：single-asset / intraday / session-pocket / long-short 对称可测
- 基础 alpha：`pseudo-open overnight+first-30m sign -> pseudo-close last-30m sign`
- 主信号：`sign(r_ONFH)`
- 交易窗口：pseudo-close 前最后 `30m`
- 执行：先测 taker，后测 maker-first / join-on-pullback
- 风控：notional cap、single-slot exposure cap、重大宏观事件日单独分桶
- 成本：优先压 `4 / 6 / 8 / 10 bps round-trip` 后再决定是否保留

## 11. 下一步怎么测（必须项）

1. **把 `r_ONFH` 拆成 overnight 与 first-30m 两腿，做 2x2 sign router。**
   - `overnight_sign`
   - `first30_sign`
   - `agreement vs disagreement`

2. **把 pseudo-open 从 fixed UTC 改成 volume-spike detected open。**
   - 每天找 US-hours 附近 rolling 30m 最大成交段；
   - 再看这个“真实 open proxy”是否更贴近论文。

3. **只在事件型 days 上复测。**
   - CPI / GDP / FOMC / 非农等；
   - 看论文口中的“macro + liquidity handoff”是不是其实只在这些天有效。

4. **叠加已有 desk state，再看 alpha 有没有被放大。**
   - `OI quadrant`
   - `funding extreme`
   - `top-trader skew`
   - `OFI / taker imbalance`

5. **把 BTC 与 ETH/SOL 分开，不要假设跨资产共用一个 session alpha。**
   - 当前更像 BTC 研究题，不像全市场模板。

## 12. 一句话结论

这篇 2022 论文真正给 desk 的，不是“某个固定时钟会涨”，而是**`pseudo-open` 那段先发生的方向，会不会在 `pseudo-close` 前最后 30 分钟再传一次**。这条 raw alpha 在论文里很干净，但在 recent Binance perp 直译版上已经明显变淡——所以它现在更适合作为 **BTC session-router 的待拆模块**，而不是直接上线的完整策略。
