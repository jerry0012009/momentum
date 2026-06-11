# 别把这篇 2023 crypto XS momentum 只读成“买强者老故事”：对 short-cycle desk，更该先保留的是「30d 横截面强者续强 × 7d weekly rotation」这条 raw alpha——但 recent liquid-major perp 迁移版 first verdict 明显偏负

- 时间：2026-04-15 14:36 UTC
- 类型：2023 SSRN 元数据 + Starkiller Capital 可读研究页（HTML 全文可读）+ Binance USDⓈ-M `1h` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**对 crypto 做横截面排序：过去 `30d` 相对最强的一组，在接下来 `7d` 里更容易继续相对跑赢；交易上对应 weekly rebalance 的 top-quintile rotation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / momentum / relative-value / top-quintile / 30d-lookback / 7d-hold / weekly-rotation / btc-trend-overlay / liquid-majors / binance-perpetual / 1h / 15m / paper / readable-web / public-data / cost / risk
- 证据类型：SSRN 元数据 + 可读研究页 + 本地 public-data portability probe

## 1. 这次看了什么
主材料是：
- **Authors：** Leigh Drogen, Corey Hoffstein, Kevin Otte
- **Year：** 2023
- **Title：** *Cross-sectional Momentum in Cryptocurrency Markets*
- **Venue：** SSRN Electronic Journal / Starkiller Capital research note
- **DOI：** `10.2139/ssrn.4322637`
- **Readable URL：** <https://www.starkiller.capital/post/cross-sectional-momentum-in-cryptocurrency-markets>
- **DOI URL：** <https://doi.org/10.2139/ssrn.4322637>
- **Repo URL：** N/A
- **Metadata URL：** <https://api.semanticscholar.org/graph/v1/paper/DOI:10.2139/ssrn.4322637?fields=title,abstract,authors,year,venue,url,openAccessPdf,citationCount,externalIds>

先把一句话说清楚：

> **这篇东西的 base alpha，不是“crypto 也有 momentum”这句大话，而是一个很具体的 cross-sectional continuation 规则：按过去 `30d` 相对收益排序，买 top quintile，持有 `7d`，按周轮动。**

我还补了一个面向 desk 的最小 public-data portability probe：
- **数据源：** Binance USDⓈ-M public klines
- **频率：** `1h`（信号本身是 weekly slow rotation，所以这里先用 `1h` 对齐周切点；执行层后续再落到 `15m/5m`）
- **资产池：** `BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK/LTC/AVAX`
- **样本：** `2025-10-01 ~ 2026-04-15`
- **规则：** 每周四 `00:00 UTC` 按前 `30d` 收益排序，等权做多 top quintile，持有到下一个周四
- **产物：**
  - `reports/artifacts/quant_digests/2026-04-15_cross_sectional_momentum_crypto_probe_summary.json`
  - `reports/artifacts/quant_digests/2026-04-15_cross_sectional_momentum_crypto_probe_weekly.csv`

## 2. 核心结论
### 2.1 一句话核心结论

> **这篇 2023 研究页最值得保留的是一条非常干净的 raw alpha：`30d` 横截面强者在接下来 `7d` 继续赢；但我把它迁到 recent liquid-major Binance perp 上做 first verdict 后，结果明显偏负，所以它现在更像一个“必须保留的 slow-book baseline / 对照组”，还不是现成 production 候选。**

### 2.2 它是怎么证明这个结论的

> **作者的证据来自 2018-2022 的大样本 crypto 横截面分组回测；我这边补的证据来自 recent Binance USDⓈ-M `1h` fixed-major portability probe。前者说明历史上这条 alpha 确实存在，后者说明 recent liquid-major perp 直译版并不自动成立。**

### 2.3 论文/研究页给出的关键数字
作者最核心的设定很明确：
- **lookback：** `30 day`
- **holding / rebalance：** `7 day`
- **rebalance 时点：** 周四 `00:00 UTC`
- **样本：** `2018-04-05 ~ 2022-11-06`
- **in-sample：** `2018-04-05 ~ 2021-03-01`
- **交易宇宙过滤：** 过去 `30d` 中至少一半时间满足 **平均美元成交额 >= `$5M`**；并人工剔除 rebase token、超高手续费/交易惩罚 token 等异常对象。

研究页里最该记住的 8 个数：
- **full sample top quintile：** **`37.8% annualized`**
- **bottom quintile：** **`-33.8% annualized`**
- **equal-weight universe：** **`11.7% annualized`**
- **Bitcoin benchmark：** **`28.7% annualized`**
- **in-sample top quintile：** **`69.17% annualized`**
- **out-of-sample top quintile：** **`-2.35% annualized`**
- **out-of-sample equal-weight：** **`-29.93% annualized`**
- **out-of-sample BTC：** **`-37.82% annualized`**

这组数最重要的含义是：
- 它不是“全样本靠 BTC 牛市带起来”的伪 alpha；
- 至少在作者的样本里，**相对赢家继续赢、相对输家继续输** 这条关系是存在的；
- 但它也不是一个无脑 buy-strongest 永动机，因为 out-of-sample 并没有漂亮到可以忽略实现细节。

### 2.4 研究页里最值钱的旁支，不是再讲 momentum，而是 BTC trend overlay
研究页后半段其实给了一个很 desk-friendly 的旁支：
- 用 **BTC `5/50` 日 EMA crossover** 给 top-quintile long-only 书做 beta gate；
- `5 > 50` 时持有 top quintile，`5 < 50` 时转现金；
- 作者给出的 headline 是：
  - **top quintile + trend overlay：`93.3% annualized`**
  - **基础 top quintile：`37.8% annualized`**
  - **max drawdown：`75% -> 45%`**

这部分对我们特别有用，因为它说明：

> **这篇材料不只是一条 raw alpha，本身还顺带暴露了一个很像 production 组件的 beta-exposure gate：大币下行趋势里，slow-rotation 动量书应该主动缩掉或转现金。**

## 3. 我补的 recent Binance perp portability probe：结论先别太乐观
我用更贴近 desk 的 recent liquid-major perp 口径，做了一个故意朴素的 first verdict：
- fixed current liquid majors，避免调 universe 魔法；
- weekly Thursday `00:00 UTC` rebalance；
- `30d` ranking，top quintile equal weight；
- 不加复杂 gate、不做个股 veto，先看最原始的 continuation 是否还活着。

结果并不好：

### gross 结果（`22` 次周度换仓）
- **portfolio total return：`-54.49%`**
- **portfolio annualized return：`-84.44%`**
- **portfolio weekly Sharpe：`-3.84`**
- **portfolio max drawdown：`-54.54%`**
- **equal-weight universe total return：`-41.92%`**
- **BTC total return：`-31.70%`**
- **avg weekly turnover：`1.136`**
- **hit rate：`31.8%`**

### cost ladder（按 `bps * turnover`）
- **10 bps：** total return `-55.64%`
- **25 bps：** total return `-57.32%`
- **50 bps：** total return `-59.99%`
- **125 bps：** total return `-67.08%`

一句话解释：

> **至少在 recent liquid-major Binance perp 这段样本上，原汁原味的 `30d winner -> next 7d continuation` 没有打赢 equal-weight，也没打赢 BTC，甚至 gross 都不过线。**

这和研究页并不矛盾：
- 作者样本是 **2018-2022 spot-oriented broad universe**；
- 我这里是 **2025-2026 recent liquid-major perp fixed universe**；
- 两者最大的不同，正是 desk 今天最该关心的：**universe 变了、市场结构变了、major-only crowding 也变了。**

## 4. 这东西为什么仍值得 intake，而不是直接丢掉
### 4.1 它补的是“XS continuation”而不是“XS reversal”
最近 digest 里，横截面题材已经有不少是：
- loser-bounce / reversal
- lead-lag catch-up
- pair spread fade
- residual sign fade

但这篇保留下来的，是另一条镜像主线：

> **不是买跌得最多的，而是买最近已经最强的。**

这对素材池是有增量的，因为未来任何新的 XS continuation / rotation / factor-momentum / theme-momentum 候选，都应该先和这条 baseline 对照。

### 4.2 它的失败画像很有价值
这轮本地 probe 的价值，不是“又找到一条能马上上线的策略”，而是把失败画像说清楚了：
- **recent liquid-major perp** 不支持这条慢速强者续强基线；
- **weekly turnover 并不低**，但真正的问题甚至不是成本，而是 **gross 就弱**；
- 所以后续如果还想做 XS continuation，就不能再偷懒写成“top-quintile weekly rotation”。

这让后续改造方向变得很明确：
- 不是继续抠 30d/7d 参数；
- 而是改 universe、改信号形态、改执行 admission。

### 4.3 它还顺手提供了一个好用的 beta gate 雏形
研究页自己给出的 `BTC 5/50 EMA` overlay，非常适合转写成 desk 里的 shared gate：
- slow rotation 类书在 **BTC downtrend** 里默认 size-down / cash / veto；
- 这既可服务本篇的 XS continuation，也可服务后续其它 alt-beta 较强的 long-only / relative-strength 书。

## 5. 对 short-cycle desk 的正确读法
### 5.1 不要把它误读成“15m 直接追强势币”
这篇东西的经济时间是：
- 信号更新慢：`30d`
- 组合持有慢：`7d`
- 它更像一个 **slow alpha book**，而不是逐根短 bar directional trigger。

所以它和当前 desk 的关系应该是：
- **signal layer 慢**；
- **execution layer 快**（`15m/5m`）；
- **risk gate 更重要**。

### 5.2 更合理的 desk 化方向不是“原样照抄”，而是 3 个分支
如果继续沿这条线推进，我更愿意优先测下面 3 个分支，而不是再重跑同一套周度 long-only：

1. **alt-only continuation**  
   把 BTC 从 ranking universe 里拿掉，只把它保留成 benchmark / gate，避免“最强者经常就是 BTC 本人”把 alpha 混成 beta。

2. **beta-neutral or residual continuation**  
   不是直接做 top-quintile long-only，而是先去 BTC beta，再做 residual strength ranking，看是否只剩下真正的 idiosyncratic continuation。

3. **BTC trend gate 先行**  
   先用大币趋势把坏 regime 切掉，再看 weekly XS continuation 是否只在 risk-on / beta-up 段里活着。

换句话说：

> **本篇现在更像“XS continuation baseline + beta gate seed”，而不是可直接进 production 的完整策略。**

## 6. 策略拆解（必填）
- **方向属性：** cross-sectional / relative-value / long-only rotation
- **基础 alpha：** 最近 `30d` 横截面赢家，未来 `7d` 继续相对跑赢
- **regime：** 更偏 broad-universe spot-like environment；recent liquid-major perp 不自然支持这条基线
- **filter / veto：** 研究页最有价值的旁支是 **BTC `5/50 EMA` trend gate**；此外还应补 liquid-major crowding / dispersion / BTC-dominance state 过滤
- **risk / sizing / execution overlay：** top-quintile equal-weight、weekly rebalance、turnover-aware cost ladder；落到 desk 时需改成 `15m/5m` child execution 与 beta exposure cap

## 7. 可复刻的最小实验
### 7.1 数据源、公开性、更新频率
- **数据源：** Binance USDⓈ-M public klines
- **公开性：** 完全公开 REST
- **更新频率：** `1h` 已足够做 weekly signal；后续执行层可落到 `15m/5m`
- **最小可复现实验：** 每周四 `00:00 UTC` 计算 `30d` return rank，做多 top quintile，持有 `7d`

### 7.2 下一步怎么测
下一步别先重写成大而全模型，先做下面 4 个最小 A/B：

1. **alt-only 版**  
   从 universe 里移除 BTC，本体只看 alt 对 alt 的 continuation。

2. **BTC gate on/off**  
   加入 `BTC 5/50 EMA` 或更贴近 desk 的 `BTC 1d / 4h trend veto`，观察 gross 是否从负变成“至少能打平 equal-weight”。

3. **residualized continuation**  
   用最近 `30d` 对 BTC 做 rolling beta / market-model residual，再按 residual strength 排序，而不是按原始收益排。

4. **short-cycle execution only**  
   信号仍然 weekly，不动；只把成交拆成 `15m` TWAP / time-sliced child orders，看实际换手与冲击能否改善。不要一上来把信号频率提快。

### 7.3 第一批必须看的指标
- `gross vs equal-weight vs BTC`
- `turnover / rebalance`
- `winner leg concentration`
- `BTC contribution vs alt contribution`
- `gate on/off` 前后收益与回撤差
- `residualized` 后 top-quintile 是否仍有 rank monotonicity

## 8. 风险与保留意见
- **这条线当前不能被写成“可直接落地完整策略”。**  因为 recent fixed-major perp 迁移版 gross 已明显偏负。
- **研究页是可读全文页，不等于正式 peer-reviewed full paper。**  但它已经足够给出规则骨架、样本设定与关键统计。
- **作者主样本更接近 broad-universe spot。**  我们 desk 真正关心的是 liquid-major perps，这两者并不等价。
- **如果后续继续推这条线，最有希望救活的不是继续调 `30d/7d`，而是改 universe 与去 beta。**

## 9. 来源
1. Drogen, L., Hoffstein, C., & Otte, K. (2023). *Cross-sectional Momentum in Cryptocurrency Markets*. SSRN Electronic Journal / Starkiller Capital.
   - DOI: `10.2139/ssrn.4322637`
   - Readable URL: <https://www.starkiller.capital/post/cross-sectional-momentum-in-cryptocurrency-markets>
   - DOI URL: <https://doi.org/10.2139/ssrn.4322637>
2. Semantic Scholar metadata:
   - <https://api.semanticscholar.org/graph/v1/paper/DOI:10.2139/ssrn.4322637?fields=title,abstract,authors,year,venue,url,openAccessPdf,citationCount,externalIds>
3. 本地 portability probe 产物：
   - `reports/artifacts/quant_digests/2026-04-15_cross_sectional_momentum_crypto_probe_summary.json`
   - `reports/artifacts/quant_digests/2026-04-15_cross_sectional_momentum_crypto_probe_weekly.csv`
