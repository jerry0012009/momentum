# 别把 copula pairs 只读成高阶 dependence 拟合：这篇 2023 arXiv 更该先测的是「BTC 参考腿 + 双 spread 条件误价」完整 raw alpha
- 时间：2026-03-28 11:48 UTC
- 类型：2023 arXiv 全文 PDF + 本地全文抽取
- 主题类型：raw alpha
- 基础 alpha：**在以 BTC 为参考腿构造的两条协整 spread 上，用 copula 条件概率判断“哪条 spread 被高估/低估”，做 long 低估 spread / short 高估 spread，吃的是双 spread mispricing 向常态关系回归。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/copula/cointegration/btc-reference/spread-mispricing/conditional-probability/kendall-tau/binance/usdt-perpetual/hourly/15m/5m/1m/3m/paper/public-data/cost
- 证据类型：论文全文证据 + desk 化映射

## 1. 这次看了什么
先把 **base alpha** 说清楚：**这不是 filter，也不是“copula 让 pair 看起来更 fancy”**。它的 raw alpha 本体是——

1. 先用 `BTCUSDT` 做参考腿，给每个 alt 构出 `S_i = BTC - β_i * ALT_i` 这类 spread；
2. 在 formation 期里，从 19 个候选 alt 里挑出和 BTC 关系最稳定、且彼此最适合组成双 spread 的两条；
3. 交易期里不直接看 z-score，而是把两条 spread 过各自边际分布后，放进 copula 里算条件概率 `h_{1|2}, h_{2|1}`；
4. 当一条 spread 相对另一条明显被高估/低估时，开 `long one spread / short the other spread`，吃的是 **relative mispricing 的回归**。

这点和我们最近已经 intake 过的一批 `cointegration + z-score` pairs 主题不一样：**那批主要在“怎么定义 spread 偏离”；这篇真正新增的是“怎么定义 spread 之间的相对误价”**。对当前 desk 来说，它的价值不是再讲一遍 pairs，而是给 stat-arb 素材池补了一个更像 `signal layer upgrade` 的 raw alpha 版本。

## 2. 核心结论
先给结论，不绕：
- **主题类型：raw alpha**
- **基础 alpha：BTC 参考腿下的双 spread 条件误价回归**
- **是否可独立复现：是**
- **是否可直接落地完整策略：是**

论文最值钱的不是“copula 能拟合尾部相关”这种泛结论，而是它给出了一条完整、可复现的策略链：
- **universe**：20 个 Binance USDT-M perpetual；
- **formation / trading**：`3 周 formation + 1 周 trading`，滚动 104 个 cycle；
- **pair funnel**：先做 EG / KSS 协整，再用 Kendall's Tau 排序；
- **signal**：对两条选中的 spread 建边际分布 + copula，直接用条件概率作为误价信号；
- **entry / exit**：`α1` 进场阈值，`α2` 平仓阈值；
- **cost**：显式计入 Binance taker fee，默认按 market order 执行。

更关键的是：**它不是只能作为 pairs 的二级确认层，而是本身就能独立成一个完整的 relative-value / stat-arb 策略。**

## 3. 为什么和当前项目直接相关
最近 desk 已经积累了不少 `cointegration / z-score / OU / Hurst` 路线的 pairs 素材。继续只补同一类“spread 偏离 -> 回归”当然没错，但边际增量会越来越低。**这篇 2023 arXiv 的价值在于，它补的是 signal construction 的另一条主线：不是单看某条 spread 偏离多大，而是看“两条可比 spread 之间，谁相对谁被错定价了多少”。**

这很适合当前研究阶段，原因有三：
1. **它仍然是 raw alpha，不是旁支 filter。**
2. **它天然服务 stat-arb / relative-value 方向的素材池扩充。** 我们当前的 raw alpha 库里，pairs 很多仍是 `single spread + threshold`；这篇多了一层 `cross-spread relative mispricing`。
3. **它比继续找一个泛化 overlay 更值得。** 因为它回答的是“还能不能从公开可得的 Binance perp 数据里，构出一个完整的、可复现的 pairs/stat-arb alpha”，而不是“又多一个可能有帮助的 gate”。

## 3.5 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / mean reversion / market-neutral 倾向**
- 基础 alpha：**两条以 BTC 为锚的协整 spread 之间会出现暂时性相对误价，之后回归常态依赖结构**
- regime：
  - 更适合 **相关结构稳定、leader/reference 腿（BTC）主导性仍在** 的环境；
  - 若 alt 结构断裂、币种轮动极快、或 reference 资产角色失真，则误价关系更容易失效。
- filter / veto：
  - formation 期至少能选出两条通过 EG/KSS 的稳定 spread；
  - Kendall's Tau 不应过低；
  - copula 拟合若 AIC 差异不明显、或边际分布拟合很差，可直接 veto；
  - 流动性 / 成交密度 / funding 异常时禁做。
- risk / sizing / execution overlay：
  - 腿权按 `β` 配比，保证 BTC 中介腿尽量净掉；
  - gross notional 固定或波动率归一；
  - 需要显式计入 taker/maker 成本、滑点、持仓超时退出、并发上限。

## 4. 论文里真正可直接复现的机制
### 4.1 数据与形成窗口
论文作者：**Masood Tadi, Jiří Witzany**。

数据口径：
- 交易所：**Binance USDT-Margined Futures**
- 样本：**2021-01-01 ~ 2023-01-19**
- 频率：**hourly close**
- 标的：**20 个加密货币合约**
- 交易周期：**每月一个 cycle，其中 3 周 formation、1 周 trading，共 104 个 cycle**

这已经足够 desk 化：它不是日频股票，也不是难拿的数据，而是**公开可得、可直接映射到 perp 的 crypto 衍生品数据**。

### 4.2 参考腿与 spread 定义
论文固定 `BTCUSDT` 为 reference asset，对其他 19 个 alt 分别构造：

`S_i,t = BTCUSDT_t - β_i * P_i,t`

其中 `β_i` 来自 formation 期回归估计。然后：
1. 对 19 条候选 spread 做 **Engle-Granger (EG)** 与 **Kapetanios-Shin-Snell (KSS)** 检验；
2. 对通过 cointegration 的候选，再计算与 BTC reference 相关的 **Kendall's Tau**；
3. 选出 Tau 最高的两条 spread，作为下周 trading 的 `S1, S2`。

翻成人话：**不是任意抓两条 alt spread 乱做，而是先筛出“相对 BTC 最稳定、最可比较”的两条，再看它们彼此的误价。**

### 4.3 Copula 信号怎么定义
形成期里，作者先给 `S1, S2` 各自拟合边际分布（候选包括 Gaussian、Student-t、Cauchy 等），再把 spread 通过各自的 CDF 变成 `U1, U2 ~ Uniform(0,1)`，然后在 `(U1,U2)` 上拟合 copula。

交易期里，每根小时 bar 计算：
- `h_{1|2} = P(U1 <= u1 | U2 = u2)`
- `h_{2|1} = P(U2 <= u2 | U1 = u1)`

信号规则非常直接：
- 若 `h_{1|2} < α1` 且 `h_{2|1} > 1-α1`：**open long S1 / short S2**
- 若 `h_{1|2} > 1-α1` 且 `h_{2|1} < α1`：**open short S1 / long S2**
- 若 `|h_{1|2}-0.5| < α2` 且 `|h_{2|1}-0.5| < α2`：**close both positions**

论文固定 `α2 = 10%`，测试多个 `α1`。最佳结果出现在 **`α1 = 10%`**。

这套规则很值得 desk 直接拿去做最小实验，因为它已经完整覆盖了：
- entry
- exit
- side decision
- pair selection
- cost assumption

## 5. 关键实证结果
### 5.1 哪些 copula 真正在样本里最常出现
104 个 trading week 的模型选择结果里，最常出现的不是 Student-t，而是偏极值/非对称家族：
- **Tawn type 1：23.1%（EG）/ 24.0%（KSS）**
- **BB7：15.4% / 15.4%**
- **Tawn type 2：15.4% / 14.4%**
- **Joe：10.6% / 7.7%**
- **Student-t：只有 6.7% / 4.8%**

这个点很关键：**如果我们 desk 化时只偷懒用 Gaussian / Student-t，很可能已经把论文里最重要的 dependency 形状信息丢掉了。**

### 5.2 收益、Sharpe、回撤
论文表 VI 的结果（均已计交易费）：

**Pairs Trading with EG test**
- `α1 = 0.10`：
  - Total Return **76.2%**
  - Annualized Return **37.1%**
  - Annualized Vol **38.2%**
  - Annualized Sharpe **0.97**
  - Max Drawdown **-35.6%**
  - Number of Transactions **176**
  - Transaction Costs / Gross P&L **11.7%**

**Pairs Trading with KSS test**
- `α1 = 0.10`：
  - Total Return **72.3%**
  - Annualized Return **35.3%**
  - Annualized Vol **37.7%**
  - Annualized Sharpe **0.93**
  - Max Drawdown **-34.0%**
  - Number of Transactions **184**
  - Transaction Costs / Gross P&L **12.9%**

对照组：
- **Bitcoin Buy & Hold**：年化 **-17.0%**，Sharpe **-0.23**，MDD **-77.1%**
- **20 币等权 Buy & Hold 组合**：年化 **14.4%**，Sharpe **0.15**，MDD **-82.2%**

翻成人话：**这篇不是“绝对高 Sharpe 神器”，但它证明了 copula-based dual-spread mispricing 在 Binance perp 公共数据口径下，至少能独立活成一条完整策略，不只是理论花活。**

### 5.3 阈值怎么影响表现
论文一个很实用的结论是：`α1` 提高后，交易次数会增多，但风险调整后表现反而下降。
- EG：年化回报从 `37.1% -> 26.4% -> 25.4%`
- KSS：年化回报从 `35.3% -> 21.8% -> 10.4%`
- Sharpe 也随之下降。

这对短周期 desk 很重要，因为它提醒我们：**copula 信号不是越敏感越好，threshold 宽松化带来的往往是更多噪声交易，而不是更高 edge。**

## 6. 和当前短周期（1m/3m/5m/15m）的关系
原论文频率是 **1h**，所以它对我们最自然的映射不是直接压到 `1m`，而是：
- **15m**：最适合做 signal bar；
- **5m / 3m**：最适合做 execution slicing 与更快出场；
- **1m**：更适合做成交成本/盘口 veto，而不是直接复刻 copula 本体。

更具体地说，这篇最值得我们搬的不是“1h alpha 本身”，而是这四个 desk 组件：
1. **BTC reference spread construction**
2. **weekly rolling formation/trading schedule**
3. **copula conditional-probability entry/exit**
4. **threshold sensitivity / cost-aware deployment**

如果要映射到 `15m`，一个自然做法是：
- formation：最近 `14d~21d` 的 `15m` bar；
- trading：后续 `3d~7d`；
- reference：仍固定 `BTCUSDT`；
- universe：只保留高流动 majors / liquid midcaps；
- execution：信号在 `15m` 生成，订单在 `5m/1m` 切片完成。

## 7. 最小可复现实验（现在就能做）
### 7.1 公开数据源
- **Binance USDⓈ-M Futures Kline**：公开可得，支持 `1m/3m/5m/15m/1h`
- 若要补成本：
  - 公开成交费率表
  - funding history
  - 最好再叠一层盘口/成交笔数代理

### 7.2 最小实验口径
我会建议第一轮别直接追求 full replication，而是做一个 **15m desk transfer MVP**：

1. **Universe**：`BTC, ETH, SOL, XRP, ADA, DOGE, BNB, LINK, LTC, TRX` 等高流动 perp。
2. **Formation**：滚动 `21d` 的 `15m` 数据。
3. **Spread 构造**：
   - 对每个 alt 估 `β_i`，构 `BTC - β_i * ALT_i`；
   - 过 EG / KSS，保留显著者；
   - 对显著者算 Kendall's Tau，挑前 2 条。
4. **Signal**：
   - 分别拟合两条 spread 的边际分布；
   - 用候选 copula 家族（至少 Gaussian / Student-t / Gumbel / Clayton / Frank / Joe / BB7 / Tawn）按 AIC 选最优；
   - 生成 `h_{1|2}, h_{2|1}`。
5. **Entry / Exit**：
   - 先测 `α1 ∈ {0.10, 0.15, 0.20}`；
   - `α2 = 0.10`；
   - 再补 `max_hold`，例如 `16 bars / 32 bars`，避免卡死。
6. **Cost**：
   - 至少测 `6 / 10 / 14 bps round-trip` 三档；
   - funding 单独记账，别混进 price PnL 里糊掉。

## 8. 下一步怎么测（必须）
1. **先做 “copula vs plain z-score” 正面对照。**
   - 同一批候选 spread、同一 formation/trading split、同一成本口径；
   - 比较 `single-spread z-score`、`dual-spread z-score`、`dual-spread copula` 三种信号。

2. **把原论文的 1h 逻辑迁到 `15m`，但不要一上来压到 `1m`。**
   - 先验证 `15m` 上 conditional-probability mispricing 是否仍有净边；
   - 再用 `5m/1m` 只做执行优化与成本 veto。

3. **加入 max-hold 与 structure-break veto。**
   - 论文默认依赖条件概率回到中性区平仓；
   - desk 版应补 `time stop` 与 `beta drift / cointegration breakdown veto`。

4. **只在高流动 bucket 里测。**
   - 这篇的胜负手很可能不只是 signal，而是“你是不是在 low-liquidity alt 上被点差和 funding 吃掉”。

5. **记录 copula 家族稳定性。**
   - 若最优 copula 家族频繁跳变，说明你在拟合噪声；
   - 若某几类（例如 Tawn / BB7）稳定出现，才值得继续把它做成正式组件。

## 9. 风险与保留意见
- 原论文用的是 **hourly**，对 `1m/3m` 不能直接硬搬；
- 它的信号层明显比 plain pairs 更重，若 universe 太大、滚动太频繁，计算与参数不稳定性都会放大；
- copula 过拟合风险是真实存在的，尤其在样本窗口压短之后；
- 论文假设 market order，已经较保守，但 desk 真落地时还要单独核算 funding 与持仓并发占用；
- 所以这条线的正确定位不是“替代所有 pairs alpha”，而是：**给现有 pairs/stat-arb 家族补一个更强的 conditional mispricing signal layer。**

## 10. 来源
1. **Tadi, M., & Witzany, J. (2023). _Copula-Based Trading of Cointegrated Cryptocurrency Pairs_. arXiv preprint.**
   - Authors: Masood Tadi; Jiří Witzany
   - Year: 2023
   - Venue: arXiv / q-fin.TR
   - DOI: `10.48550/arXiv.2305.06961`
   - Readable URL: `https://arxiv.org/abs/2305.06961`
   - PDF URL: `https://arxiv.org/pdf/2305.06961.pdf`
   - Repo URL: `N/A（文中未给公开代码仓库）`

2. **Binance Developers. USDⓈ-M Futures API – Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地相关产物
- Digest：`research/quant_digests/2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-28_1148_btc-reference-copula-spread-mispricing-alpha.html`
