# 别把 realized variance 只当风险指标：这篇 2025 *JFQA* 更该先测的是「positive-jump variance × anti-lottery cross-sectional long-short」这条 raw alpha

- 时间：2026-04-06 06:19 UTC
- 类型：2025 *Journal of Financial and Quantitative Analysis* 开放获取论文全文（Cambridge PDF）+ Binance public `15m` spot portability probe
- 主题类型：raw alpha
- 基础 alpha：**做多低 realized-variance / 低 positive-jump-variance 币，做空高 realized-variance / 高 positive-jump-variance 币；赚的是“彩票偏好过热后，横截面回报被高波动/高正跳跃币透支”的反向价差。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/anti-lottery/realized-variance/positive-jump/jump-robust/15m/intraday/weekly-sort/spot/coinbase/kaiko/binance/open-access/paper/public-probe/cost/risk
- 证据类型：开放获取论文全文 + 表格/回归结果 + 本地 Binance `15m` 便携性快检

## 1. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = `横截面做多低波动/低正跳跃币，做空高波动/高正跳跃币`。**

翻成人话：
- 不是把 volatility 当成风控变量；
- 而是把 **“谁最近更像彩票、谁刚经历了更多极端正跳跃”** 当成可交易的横截面特征；
- 论文核心不是 generic low-vol，而是更尖一点的：
  - `positive jump variance`（正向极端跳跃的方差）
  - `jump-robust variance`（非跳跃但持续躁动的方差）
  这两块对后续收益的负预测最强。

所以它属于 **cross-sectional / anti-lottery raw alpha**，不是单纯 overlay，也不是只给解释。

## 2. 为什么这轮值得进研究池

当前 mainline 文档和最近 digest 池，已经积累了很多：
- breakout / trend / TSMOM，
- pairs / spread mean reversion，
- funding / basis carry，
- microstructure continuation / reversal。

这篇值得补，是因为它补的是另一块 **可独立站立的 raw alpha**：

1. **它不是再围着 trend/breakout 打转。**  
   这条线直接扩充 `cross-sectional / relative-value / anti-lottery` 素材池。

2. **它的信号来自 intraday realized moments，本质上与 short-cycle infra 是兼容的。**  
   论文直接用高频数据估计 variance，不是拿低频基本面硬套到分钟级。

3. **它还能自然拆成 raw alpha + veto/filter。**  
   主体当然是 long-low / short-high；但即便 desk 最后不直接上 market-neutral 壳，`high positive-jump variance` 也很适合做：
   - 不追涨 veto，
   - 选空优先级，
   - 或 cross-sectional momentum 的 short-side exclusion。

## 3. 来源与材料

### 主论文
- **Authors**：Suzanne S. Lee, Minho Wang
- **Year**：2024 online / 2025 print
- **Title**：*Variance Decomposition and Cryptocurrency Return Prediction*
- **Venue**：*Journal of Financial and Quantitative Analysis*
- **DOI**：<https://doi.org/10.1017/S002210902400022X>
- **Readable URL**：<https://doi.org/10.1017/S002210902400022X>
- **PDF URL**：<https://www.cambridge.org/core/services/aop-cambridge-core/content/view/9995E58095453CB44A3BC3C9C111969F/S002210902400022Xa.pdf/div-class-title-variance-decomposition-and-cryptocurrency-return-prediction-div.pdf>
- **Repo URL**：未见作者公开 companion repo（paper-only）

### 论文数据口径
- **主数据源**：Kaiko 高频 quote / order-book 数据
- **交易场所**：以 Coinbase 为主样本构建基底，并验证其他交易所鲁棒性
- **公开性**：论文主数据并非免费公共源；但方法、公式、回测口径是可读全文可复现的
- **采样频率**：`15m` mid-quote returns
- **样本期**：`2015-10 ~ 2023-06`
- **样本规模**：100 个 crypto（含 delisted coin，作者明确强调 survivorship bias 不是关键问题）

### 本轮本地 portability probe（公开数据）
- **数据源**：Binance spot public API `15m` klines
- **公开性**：公开可得，无 key
- **最小实验字段**：`close`
- **本地产物目录**：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-06_variance-jump-crosssection-alpha/probe_summary_all.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-06_variance-jump-crosssection-alpha/major_alts_summary.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-06_variance-jump-crosssection-alpha/speculative_alts_summary.csv`

## 4. 论文里最该拿走的硬信息

## 4.1 方法不是“低波动因子”空话，而是高频 realized moment 拆解

作者不是只看一个粗糙的 daily volatility，而是：
- 用 `15m` mid-quote returns 估计 realized variance；
- 再把总方差拆成：
  - `positive jump variance`
  - `negative jump variance`
  - `jump-robust variance`
- 每周做横截面排序；
- 用**前一个月**的高频观测估计这些 realized measures，预测**下一周**超额收益。

这点很关键：

> 论文真正的 edge 不是“波动大所以可能跌”，而是“用高频数据更及时地刻画谁刚变成彩票资产”。

作者也明确拿 daily-data volatility 做对照，发现 **daily volatility 系数不显著**，而 intraday-based realized variance 显著。

## 4.2 最关键结论：高 realized variance 币，后续周收益显著更差

论文 Figure 2 / Table 4 最核心的数字：

- **总 realized variance 排序**：
  - Low 组下一周 EW excess return：**+0.1%**
  - High 组下一周 EW excess return：**-3.6%**
  - `Low - High`：**+3.7%/周**
  - VW 口径 `Low - High`：**+3.0%/周**

这不是小 edge。

更重要的是，作者继续拆分后发现：

- **positive jump variance 排序**：
  - EW `Low - High`：**+3.6%/周**
  - VW `Low - High`：**+2.3%/周**
- **jump-robust variance 排序**：
  - EW `Low - High`：**+3.2%/周**
  - VW `Low - High`：**+2.6%/周**

换句话说：
- 不只是“高波动”坏；
- **“刚出现很多大阳线式正跳跃”** 更坏；
- **“即便不是跳跃，而是整体持续躁动”** 也坏；
- 反而 **negative jump variance 不是主要驱动**。

## 4.3 回归层面：positive jump variance 是最硬的解释变量

Fama-MacBeth 回归里，作者给出的几个特别值得记住的系数：

- `total variance` 系数：**-0.221***
- `jump variance` 系数：**-0.669***
- `positive jump variance` 系数：**-1.470***
- `jump-robust variance` 系数：**-0.152***
- `daily volatility` 系数：**-0.134`（不显著）`

最有用的一句就是：

> **用高频估出来的 variance 有预测力；用日频粗波动替代，不行。**

这对我们 desk 很重要，因为它意味着：
- 这不是传统资产里那种慢吞吞 low-vol story；
- 它和 `5m/15m` 研究栈是有技术兼容性的。

## 4.4 机制不是“风险补偿”，更像“彩票偏好 + 零售追逐”

论文给出的机制读法很适合 desk：

- 高 variance / 高 positive-jump variance 币通常：
  - **更小市值**
  - **更低价格**
  - **更宽 bid-ask spread**
  - **更高 retail trading proportion**
  - **更高正向情绪/买入舆情**
- 作者把它解释成 **lottery preference / speculative retail trading**。

也就是：
- 市场不是因为这些币“风险高所以应该给更高回报”；
- 而是因为很多人愿意为了“可能再来一个大阳线”先把价格抬贵；
- 所以后续反而给出更差回报。

这对 crypto 尤其合理，因为彩票偏好和追热点资金，本来就是这里的常见定价力量。

## 5. 对 short-cycle desk，最诚实的读法是什么？

## 5.1 诚实版：它是慢一点的横截面 raw alpha，不是逐根 5m 主信号

必须老实讲：
- 论文交易频率是 **周级排序、周级持有**；
- 信号估计用的是 **过去一个月** 的 intraday returns；
- 所以它不是那种“下一根 5m K 线涨跌”的 ultra-short predictor。

但这不妨碍它服务当前 desk，因为它完全可以读成：

**一个由高频数据驱动、但 refresh 较慢的横截面 raw alpha sleeve。**

更具体点：
- execution 可以在 `5m/15m`；
- 但 signal refresh 不一定每根 bar；
- 完全可以是：
  - 每 `4h` / `1d` 刷一次横截面分层；
  - 组合执行和风控仍在 `5m/15m` 完成。

## 5.2 这条线真正适合 desk 的支线读法

这篇 paper 对我们最值得先拆的，不只是完整的 long-short 组合，还有两条支线：

### 支线 A：short-side candidate ranker
- 把 `high positive-jump variance` 当成优先做空池；
- 尤其在情绪高涨、山寨追涨很拥挤时，优先找“最像彩票”的那一篮子。

### 支线 B：momentum / breakout 的追涨 veto
- 若一个币刚出现很大的正跳跃方差，别把它继续当最舒服的 breakout 跟随对象；
- 它更可能已经被过度追逐，后续 risk-reward 变差。

所以即便完整 long-short 最后不进 production，`positive jump variance veto` 也很值。

## 6. 我做的最小 portability probe：直接搬到 Binance `15m`，近期样本先别急着上

为了避免只抄 paper，我做了一个很小但诚实的最近窗口快检。

### 6.1 实验口径
- 数据：Binance spot 公共 API，最近 `1000` 根 `15m` bars（约 10.4 天）
- 信号：
  - `rv_1d`：过去 `96` 根 `15m` 的 realized variance
  - `psv_1d`：过去 `96` 根 `15m` 的 positive semivariance proxy
  - `bv_1d`：过去 `96` 根 `15m` 的 bipower variation proxy（jump-robust variance 近似）
- 排序：每个时间点做横截面三分位
- 组合：`long low tercile - short high tercile`
- 评估 horizon：`1h / 4h / 1d`
- 两组 universe：
  - `major_alts`：SOL/XRP/DOGE/BNB/ADA/AVAX/... 这类液态大中盘 alt
  - `speculative_alts`：SHIB/BONK/PIXEL/ONT/... 这类更偏投机的中小盘 alt

### 6.2 结果：**最近这段 Binance tape，信号短期是反着的**

#### major_alts
- `rv_1d` 的 `Low - High`：
  - `1h`：**-0.0062%**
  - `4h`：**-0.0526%**
  - `1d`：**-0.3729%**
- `psv_1d` 的 `Low - High`：
  - `1h`：**-0.0160%**
  - `4h`：**-0.0692%**
  - `1d`：**-0.3591%**

#### speculative_alts
- `rv_1d` 的 `Low - High`：
  - `1h`：**-0.0342%**
  - `4h`：**-0.1577%**
  - `1d`：**-0.7310%**
- `psv_1d` 的 `Low - High`：
  - `1h`：**-0.0415%**
  - `4h`：**-0.1682%**
  - `1d`：**-0.3854%**

也就是说，在**最近这 10 天左右的 Binance `15m` 样本**里：

> 不是低 variance 币更强，而是高 variance / 高 positive-jump 币继续更强。

这和 paper 的周级结论相反。

### 6.3 这不代表论文没用，代表我们不能“频率偷换”

最合理的解释不是“paper 错了”，而是：

1. **paper 的 alpha 是周级横截面，不是近 10 天 15m 的追踪误差游戏；**
2. **当前 tape 更像投机追涨环境，高方差币正处在被继续买的阶段；**
3. **作者的效应更强于长期、更广的 Coinbase/Kaiko 横截面，并且更偏小币/零售拥挤环境；**
4. **我们这里的 recent-window probe 更像在测“这条周级 alpha 能不能直接压缩成短线版本”，答案目前是：不能直接照搬。**

这反而是好事，因为它告诉我们：
- 这条线 **值得测**，
- 但 **不能粗暴降频率/缩 horizon**。

## 7. desk 版该怎么落地，才不算乱改论文

## 7.1 先做 paper-faithful replication

第一步不要自作聪明，先复原它的结构：
- universe：尽量广的 spot coin 横截面
- sampling：`15m`
- feature window：过去 `1 month`
- rebalance：每周
- portfolio：
  - `long low positive-jump variance tercile`
  - `short high positive-jump variance tercile`
- weighting：先 equal-weight，再加 liquidity cap

这是**主验证**，不是可选项。

## 7.2 然后才是 desk adaptation

### 版本 A：慢因子 + 快执行
- signal 每 `1d` 或 `4h` 刷新一次；
- 执行 bar 在 `15m`；
- 组合仍是 market-neutral cross-sectional long-short。

### 版本 B：short-side ranker
- 只取 `high positive-jump variance` 分位做 short candidate 池；
- 再叠一个 `breadth weakening / BTC not impulsing up` 的环境确认。

### 版本 C：trend / breakout veto
- breakout 本来想追多的币，如果它的 `positive-jump variance` 已在横截面顶部分位，先降权或 veto。

对当前 desk，**版本 B / C 反而可能比直接上完整 long-short 更快。**

## 8. 一条最小可执行策略骨架

## 8.1 Universe
- Binance spot 或 perp 流动性前 `30~80` 币
- 剔除：稳定币、包装资产、明显不可借不可空标的
- 首轮优先：spot 做研究；能成立再映射 perp

## 8.2 Signal
- bar frequency：`15m`
- 每个币估计：
  - `RV = sum(r_t^2)`
  - `PSV = sum(max(r_t, 0)^2)`
  - `BV ≈ (π/2) * sum(|r_t||r_{t-1}|)`
- window：
  - Paper-faithful：`~30d`
  - Desk-minimal：先从 `3d / 7d / 14d / 30d` 四档试
- 排序：横截面 tercile / quintile

## 8.3 Entry / Exit
### Paper-faithful 版
- 周末或固定 UTC 时间做一次排序
- 下周持有整周

### Desk-adapted 版
- 每 `4h` 或 `1d` 刷一次排序
- 固定持有 `1d / 3d`
- 不要先上 per-bar 动态翻仓，不然 turnover 会把 edge 吃掉

## 8.4 Sizing
- equal-weight 起步
- 再加：
  - 单币权重上限
  - ADV cap / trade-count cap
  - inverse-vol 微调，但不要把 alpha 又冲淡成 generic risk parity

## 8.5 Risk / Cost
- 手续费：先按 taker 双边 `4~8 bps`
- 做空可得性：优先在 perp 验证，但注意 funding 不要把 alpha 和 carry 混起来
- 风险项：
  - squeeze risk（尤其 short 高 positive-jump 币时）
  - crowding / meme continuation
  - regime dependency（risk-on 疯涨阶段，信号容易翻面）

## 9. 这篇 paper 目前最适合放在我们研究栈里的位置

我的判断：

- **主标签仍然是 `raw alpha`**，因为 base alpha 很清楚；
- 但对当前 `1m/3m/5m/15m` desk，**最优先的不是直接把它压成下一根 K 线预测器**；
- 更适合先作为：
  1. **慢横截面 alpha sleeve**
  2. **short-side ranker**
  3. **trend/breakout 的 anti-lottery veto**

这比把它硬伪装成“分钟级主信号”诚实得多，也更可能跑出东西。

## 10. 下一步怎么测

按优先级，我建议直接做这 4 组实验：

### P0：paper-faithful replication（必须先做）
- 数据：尽量广的 spot 横截面，`15m` 或更高质量 intraday 数据
- 信号：`RV / PSV / BV`
- 窗口：`30d`
- rebalance：weekly
- 输出：`Low/Mid/High` 分组收益、`Low-High` spread、turnover、成本后收益

### P1：desk 适配版慢刷新
- 用 Binance / Bybit 可拿到的公开数据
- `15m` bar 估 `7d/14d/30d` variance family
- refresh：`4h` / `1d`
- hold：`1d` / `3d`
- 验证这条线是不是只能慢做，还是能压缩到我们现有 infra

### P2：regime split
把样本按以下条件切开：
- BTC `1d` 涨幅分位
- alt breadth
- high-beta risk-on / risk-off
- meme season proxy

核心问题：

> `anti-lottery` 这条线是不是只在 risk-off / overheat-cooling 阶段成立，而在纯 risk-on 追涨阶段翻面？

### P3：把它变成 veto，而不是强行当主 alpha
- 在现有 breakout / winner-only / market TSMOM / cross-sectional momentum 壳上，加入：
  - `positive-jump variance top decile veto`
  - `jump-robust variance top decile size-down`
- 看它能不能改善：
  - entry timing
  - short-side hit rate
  - MDD

## 11. 一句话结论

这篇 2025 *JFQA* 给的不是“vol 高要小心”这种废话，而是一条很清楚的 **anti-lottery cross-sectional raw alpha**：

> **做多低 realized-variance / 低 positive-jump-variance 币，做空高 realized-variance / 高 positive-jump-variance 币。**

但我这轮 public `15m` 快检也很明确：

> **它不能被粗暴压缩成最近 10 天 Binance `15m` 的短线版本；当前 tape 里，高 variance 币反而在继续赢。**

所以最该做的，不是把它误读成逐根信号，而是：
- 先做 paper-faithful 周级 replication；
- 再把它拆成 `slow cross-sectional sleeve / short-side ranker / anti-lottery veto` 三条线。

## 12. 参考链接

- Paper DOI：<https://doi.org/10.1017/S002210902400022X>
- Paper PDF：<https://www.cambridge.org/core/services/aop-cambridge-core/content/view/9995E58095453CB44A3BC3C9C111969F/S002210902400022Xa.pdf/div-class-title-variance-decomposition-and-cryptocurrency-return-prediction-div.pdf>
- JFQA article landing（DOI 跳转）：<https://doi.org/10.1017/S002210902400022X>
