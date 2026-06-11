# 别把这份 intraday crypto repo 继续只读成 close-pocket：对 short-cycle desk，更该补的是「US crypto ETF midday 30m momentum pocket」这条可独立成策略的 cross-market raw alpha

- 研究时间：2026-04-02 01:58 UTC
- 时间：2026-04-02 01:58 UTC
- 主题类型：raw alpha
- 类型：raw alpha
- 基础 alpha：美股常规交易时段里，`IBIT / FBTC / ETHA / FETH` 在 `11:00–11:30 ET` 先走强的品种，往往会在 `11:30–12:00 ET` 继续走强；可直接做 ETF 横截面 long-short，也可转译成 `BTC complex vs ETH complex` 的 crypto perp relative-value continuation。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/us-etf/midday-pocket/momentum/relative-value/btc-vs-eth/ibit-fbtc-etha-feth/regular-session/11:00-11:30/11:30-12:00/5m/15m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub notebook source audit（`Intraday_Crypto_Reversal_Project.ipynb`）+ notebook 内 window sweep / portfolio correlation 输出 + 经典 intraday microstructure 论文链路

---

## 1. 这次看了什么

这次主材料仍来自 **BNeillDickey (2026)** 的 GitHub notebook，但我刻意不重复已经 intake 过的两个分支：

- `US session spot-crypto cross-sectional reversal`
- `US ETF close-window BTC-vs-ETH relative-strength continuation`

这次单独拎出来的，是 notebook 里一个之前没作为主角写过、但对 desk 很实用的 **midday regular-session pocket**：

> **`11:00–11:30 ET` 的 ETF winner，往往会在 `11:30–12:00 ET` 继续赢。**

主材料信息：

- **Author / Year / Title / Venue**: BNeillDickey, 2026, *intraday-crypto-reversal-project*, GitHub research notebook
- **Readable URL**: https://github.com/BNeillDickey/intraday-crypto-reversal-project
- **Repo URL**: https://github.com/BNeillDickey/intraday-crypto-reversal-project
- **Core file**: `Intraday_Crypto_Reversal_Project.ipynb`
- **GitHub metadata**: repo created `2026-03-09`, pushed `2026-03-09`, description 写明覆盖 spot crypto reversal 与 ETF intraday momentum

学术地基不是 crypto-specific headline paper，而是 notebook 明确引用的 3 条 intraday 文献链路：

1. **Heston, Korajczyk & Sadka (2010)**, *Intraday Patterns in the Cross-section of Stock Returns*, *Journal of Finance*, DOI: `10.1111/j.1540-6261.2010.01573.x`
2. **Bogousslavsky (2016)**, *The Cross-Section of Intraday and Overnight Returns*, *Journal of Financial Economics* / earlier SSRN lineages，核心框架是“慢移动资金造成可预测的日内自相关 / 逆相关”
3. **Gao, Han, Li & Zhou (2018)**, *Market Intraday Momentum*, *Journal of Financial Economics*, DOI: `10.1016/j.jfineco.2018.05.009`

对我们来说，这条主题的价值不在“又一个 ETF story”，而在于它给了一个 **公开可得、分钟级、规则简单、可直接落地的 U.S. session raw alpha pocket**。

---

## 2. Base alpha 到底是什么

一句话先答：

> **base alpha 是 U.S.-listed crypto ETF 在常规交易时段中段形成的横截面 momentum pocket，不是 filter，不是 regime 注释。**

最直接的策略化定义：

1. 在纽约时间 `11:00–11:30` 统计 `IBIT / FBTC / ETHA / FETH` 的 30 分钟收益；
2. 按收益做横截面排序；
3. **long winners / short losers**；
4. 持有 `11:30–12:00`；
5. 每天只做这一段，不拖成全天策略。

翻成人话：

**不是赌全天 macro 叙事，而是赌一个很窄的“午间接力”——11 点到 11 点半先跑出来的那一边，接下来半小时还有惯性。**

对 crypto desk 的更自然转译是：

- 先把 `IBIT + FBTC` 看成 **BTC complex**；
- 把 `ETHA + FETH` 看成 **ETH complex**；
- 再把 ETF 相对强弱转成 `BTC perp vs ETH perp` 的分钟级 RV continuation。

---

## 3. 为什么这轮值得写它，而不是继续补一个泛 filter

因为它满足当前 intake 优先级里最重要的几条：

- **raw alpha**，不是纯 gate；
- **能独立复现**，不是只能贴在老 breakout 上；
- **能直接写成 entry / exit / sizing / risk / cost**；
- **是新的时间 pocket**，而不是继续在 close-window 内循环。

更关键的一点：

此前从同一 notebook 已经拿过 **U.S. close / after-hours** pocket；
这次的 `11:00–11:30 -> 11:30–12:00` 则补上了 **regular-session 中段**。

也就是说，它对 desk 的意义不是“又多一个 ETF 指标”，而是：

- 给 `BTC-vs-ETH` / `BTC,ETH single-leg bias` 增加一个 **不同于 close 的 session component**；
- 给 `5m / 15m` 管线补一个 **分钟级外部 price-discovery trigger**；
- 给后续组合提供一个和已有 close-window pocket **相关性更低** 的时段 alpha。

---

## 4. Notebook 里最重要的硬数据

### 4.1 数据面板

Notebook 用的是公开可拿的 Yahoo / `yfinance` prepost bars：

- 标的：`IBIT`, `FBTC`, `ETHA`, `FETH`
- 主面板：`60m` bars
- 样本区间：`2024-02-26 -> 2026-02-25`
- 面板大小：`8311 x 4`

这里最重要的点是：

- 数据公开；
- 分钟级可复现；
- 对 crypto desk 来说没有额外 vendor 门槛。

### 4.2 全窗口 sweep：best regular-session pocket 是 midday momentum

Notebook 一共扫了 **612 组** session-window / mode 组合。

在 **regular session** 里，排在最前面的不是 open，也不是 close，而是：

- **zone**: `regular`
- **set**: `ALL`
- **signal**: `11:00–11:30`
- **hold**: `11:30–12:00`
- **mode**: `momentum`
- **Sharpe**: `2.91`
- **days**: `499`

这条结果很重要，因为它说明：

> **常规交易时段里也存在独立 pocket，不需要把所有 ETF alpha 都理解成“收盘效应”。**

### 4.3 它不是从 close-window 机械复制出来的

同一个 notebook 里，作者给出的 anchor 策略是：

- `15:30–16:00 signal -> 16:00–17:00 hold`
- momentum `SR = 3.29`

midday pocket 的 SR 虽然低于 close anchor，
但 notebook 在组合测试里给出的相关性矩阵显示：

- **anchor close momentum vs best regular-session momentum 的日度 PnL 相关性只有 `0.014`**

这意味着什么？

不是“再来一条差不多的信号”，而是：

> **它更像一个独立时段组件，可以和 close pocket 并列，而不是简单替代。**

### 4.4 组合后而不是单条孤立，更像 portfolio building block

同一个 notebook 用 3 条 ETF pocket 做 equal-weight portfolio：

- anchor close momentum：`SR ≈ 3.21`
- best regular-session momentum：`SR ≈ 2.96`
- best after-hours momentum：`SR ≈ 8.61`（注意 AH 成本可能被低估）
- **equal-weight portfolio Sharpe：`6.917`**

对我们更重要的启示不是把 `6.9` 当成可直接搬运的纸面收益，
而是：

- midday regular pocket 有独立增量；
- 可以被当成一个 **session-sliced alpha block**；
- 很适合拿来做短周期组合的“时段组件化”。

---

## 5. 这条 alpha 的 desk 化读法

### 5.1 原始可独立策略：直接做 ETF 横截面 momentum

最朴素版本：

- universe：`IBIT / FBTC / ETHA / FETH`
- signal window：`11:00–11:30 ET`
- rank signal：30m return
- direction：**momentum**（long winners / short losers）
- hold：`11:30–12:00 ET`
- weighting：top half vs bottom half 等权、dollar-neutral
- TC：按 notebook 用 `7 bps/side` turnover-based cost 起步

这个版本本身就是完整 raw alpha。

### 5.2 更适合 crypto desk 的转译：BTC complex vs ETH complex

如果不想直接做 ETF，而是把它当作 crypto 外部信号，最自然的转译是：

- `r_BTCETF = mean(r_IBIT, r_FBTC)`
- `r_ETHETF = mean(r_ETHA, r_FETH)`
- `spread_sig = r_BTCETF - r_ETHETF`

交易规则：

- 若 `spread_sig > q`：做 `long BTC perp / short ETH perp`
- 若 `spread_sig < -q`：做 `long ETH perp / short BTC perp`
- 若 `|spread_sig| <= q`：空仓

这里的 `q` 不要先拍死，先测：

- rolling `60%`
- rolling `70%`
- rolling `80%`
- rolling `90%`

这比直接把 4 ETF 权重硬映射进 crypto 更稳，因为 desk 里最可执行的还是 **BTC-vs-ETH relative-value shell**。

### 5.3 再往前一步：单腿 directional bias 版本

如果不做 pair，也可以做更简单版本：

- 当 `BTC complex` 是 clear winner，就只开 `BTC perp` 多；
- 当 `ETH complex` 是 clear winner，就只开 `ETH perp` 多；
- 当 winner 归属不清或 cross-sectional spread 太小，就不做。

这会损失市场中性，但执行更简单，适合作为最小实验对照组。

---

## 6. 为什么它对 `1m / 3m / 5m / 15m` 有意义

### 6.1 不是低频变量，是真正能下钻到分钟级的公开数据

这类 ETF 数据不是日线 / 周线宏观代理。

它至少有两层公开可得粒度：

- `60m`：足够复现 notebook 的主结果；
- `5m`：足够把 signal / hold 拆成更细的 execution window。

所以它符合本轮要求：

> **公开可得 / 能较快拿到 / 能映射到 `1m / 3m / 5m / 15m` 最小实验。**

### 6.2 对 crypto perp 最自然的映射是 5m，而不是日频慢变量

建议先这样映射：

- `15m`：先做存在性验证，看 proxy alpha 是否还在；
- `5m`：做主版本，因为 `11:00–11:30` 和 `11:30–12:00` 本来就是两个 30m pocket；
- `3m / 1m`：只做 execution slicing，不要先改 alpha 定义。

也就是说：

- **alpha 定义仍是 30m signal / 30m hold**；
- `1m/3m/5m` 负责的是更细的入场、滑点、止损和减仓。

---

## 7. 成本、容量与风险怎么想

### 7.1 比 after-hours 更干净的点：regular session 成本更诚实

这条主题比 notebook 里最强的 after-hours pocket 更适合 desk，原因很简单：

- after-hours ETF 有明显 spread / 深度问题；
- notebook 自己也提醒了 `AH TC may be understated`；
- **midday regular session** 至少在 ETF 这侧，成交与价差都更正常。

因此这条 regular-session pocket 比 AH pocket 更像一个“先复现、再转译”的稳妥入口。

### 7.2 转到 crypto perp 时要重新做成本会计

如果信号表达切到 Binance / Bybit / OKX perp，不能偷用 ETF 的 7bps 假设。

需要单独重建：

- maker / taker 费率；
- 5m bar 内冲击成本；
- entry 延迟 `0 / 1 / 2` bar 的 alpha 留存；
- BTC-vs-ETH pair 的 beta-neutral sizing 是否比 dollar-neutral 更稳。

### 7.3 风险点

主要有 4 个：

1. **U.S. session dependency**：只在特定纽约时段有效，不应外推到全天；
2. **proxy mismatch**：ETF 强弱不一定一比一传导到 crypto perp；
3. **small universe**：4 个 ETF 的横截面很窄，容易被个别新闻扰动；
4. **event contamination**：宏观数据、Fed speaker、ETF-specific headlines 可能放大或扭曲 pocket。

所以这条策略最适合：

- 做固定时段；
- 先做 RV；
- 配一个最简单的 event veto（CPI / FOMC / NFP / ETF issuer headline day）。

---

## 8. 下一步怎么测

这部分必须给清楚。

### 最小实验 A：直接复现 ETF 原始策略

目标：确认 notebook 的 regular-session best pocket 能在我们自己的管线里复现。

1. 拉 `IBIT/FBTC/ETHA/FETH` 的 `5m` 和 `15m` prepost 数据；
2. 定义 `11:00–11:30` signal、`11:30–12:00` hold；
3. 做四 ETF 横截面 momentum long-short；
4. 成本先测 `3/5/7 bps per side` 三档；
5. 输出：Sharpe、mean bps/trade-day、hit-rate、turnover、最大回撤。

### 最小实验 B：crypto desk 版本的 BTC-vs-ETH RV 映射

目标：判断这条 ETF pocket 是否真能转成 crypto raw alpha。

1. 用同一时间 pocket 生成 `spread_sig = r_BTCETF - r_ETHETF`；
2. 在 Binance perp 上做 `BTCUSDT vs ETHUSDT`；
3. 比较三种 sizing：
   - dollar-neutral
   - beta-neutral（rolling 20d / 60d beta）
   - vol-neutral
4. hold 先测：
   - `30m`
   - `45m`
   - `60m`
5. admission 先测：
   - no threshold
   - `|spread_sig| > 60%ile`
   - `|spread_sig| > 75%ile`
   - `|spread_sig| > 90%ile`

### 最小实验 C：directional 单腿对照组

目标：验证 alpha 的来源到底更像 pair signal 还是 underlier directional pressure。

1. 若 BTC complex 胜出明显，只开 BTC 多；
2. 若 ETH complex 胜出明显，只开 ETH 多；
3. 用 pair 版本做对照。

如果 pair 版明显更稳，说明它更像 **relative-value price discovery**；
如果单腿也能活，说明这条 pocket 还有一部分是 **directional continuation**。

### 明确的 go / no-go 判据

我建议先用很硬的阈值，别拖：

- ETF 原始版本：`net SR > 1.5` 才保留；
- crypto 映射版本：`net SR > 1.0` 且 `avg trade-day alpha > all-in cost` 才进下一轮；
- 若只有无阈值版本有效、加一点 admission 就塌，则降级为 **弱信号 / 组合组件**，不单独推进。

---

## 9. 我对这条主题的判断

我会把它定性成：

> **值得进入素材池，而且优先级高于一般 ETF 解释型主题。**

原因：

- 它是 **raw alpha**，不是宏观 commentary；
- 它有 **固定时段、固定 entry/exit**；
- 它和已 intake 的 close-window pocket **不是一回事**；
- 它更适合做 **session component**，而不是全天神因子；
- regular-session 成本环境比 after-hours 更可控，适合先做复现。

如果这条线后续在 crypto 映射上还能站住，
它最可能的角色不是“单独撑起一本书”，
而是成为：

- `BTC-vs-ETH` RV 书里的 **U.S. midday pocket**；或
- directional / RV 组合里的 **时段 alpha block**。

这对当前 desk 来说，已经足够有研究价值。

---

## 10. 来源链接

### 主来源

- BNeillDickey (2026), *intraday-crypto-reversal-project*, GitHub: https://github.com/BNeillDickey/intraday-crypto-reversal-project
- Raw notebook: https://raw.githubusercontent.com/BNeillDickey/intraday-crypto-reversal-project/main/Intraday_Crypto_Reversal_Project.ipynb

### 学术地基

- Heston, S., Korajczyk, R. A., & Sadka, R. (2010). *Intraday Patterns in the Cross-section of Stock Returns*. *Journal of Finance*. DOI: https://doi.org/10.1111/j.1540-6261.2010.01573.x
- Gao, L., Han, Y., Li, S. Z., & Zhou, G. (2018). *Market intraday momentum*. *Journal of Financial Economics*. DOI: https://doi.org/10.1016/j.jfineco.2018.05.009
- Bogousslavsky, V. (2016/2021 lineage). *The Cross-Section of Intraday and Overnight Returns*. Journal / SSRN lineage; used here as slow-moving-investor intraday-pattern background rather than a crypto-specific headline signal.
