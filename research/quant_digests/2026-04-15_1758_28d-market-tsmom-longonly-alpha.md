# 别把这篇 2024 crypto momentum 论文又读成“多空都能做”：对 short-cycle desk，更该先保留的是「28d 自身分位强势 × 5d market long-only」这条 raw alpha——short leg 反而更像 loser-rebound veto 的反面教材

- 时间：2026-04-15 17:58 UTC
- 类型：2024 SSRN 论文全文 PDF
- 主题类型：raw alpha
- 基础 alpha：**当 crypto market proxy 的过去 `28d` 收益落在其自身历史分位的上三分位附近时，只做多并持有 `5d`；不要机械做空下分位，因为 short leg 在 crypto 里更容易被反弹和极端波动破坏。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-book / market-beta / trend / time-series-momentum / long-only / percentile-threshold / 28d-lookback / 5d-hold / crypto-market-proxy / btc-or-ew-basket / 1h / 4h / 15m / 5m / paper / fulltext / cost / liquidation / risk
- 证据类型：论文全文 PDF

## 1. 这次看了什么
主材料是：
- **Authors：** Chulwoo Han, Byeongguk Kang, Jehyeon Ryu
- **Year：** 2024
- **Title：** *Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*
- **Venue：** SSRN Electronic Journal
- **DOI：** `10.2139/ssrn.4675565`
- **DOI URL：** <https://doi.org/10.2139/ssrn.4675565>
- **Readable URL：** <https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf>
- **Mirror PDF：** <https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf>
- **Repo URL：** N/A

先把一句话说清楚：

> **这篇东西最适合拿来做主 digest 的 base alpha，不是“crypto 里也有 momentum”这句空话，而是一条可以直接写成交易规则的 market-level time-series momentum：过去 `28d` 很强时，未来 `5d` 继续偏强，于是做多 market proxy；短侧不要硬做。**

这也是它和今天早些时候那篇 **cross-sectional weekly winner rotation** 的根本区别：
- 那篇的核心是 **横截面强者续强**；
- 这篇我保留的主线是 **市场自身趋势续强**；
- 所以这次不是重复 intake，而是在补 **单书方向性 raw alpha** 素材池。

## 2. 核心结论
### 2.1 一句话核心结论

> **如果按论文的“现实口径”去做——每日 mark-to-market、计入交易成本、考虑 liquidation——最稳的一条不是 crypto cross-sectional long-short，而是 `28d` lookback、`5d` hold 的 long-only market TSMOM。**

### 2.2 为什么这条比“多空一起上”更值钱
这篇最重要的价值，不是再次证明 momentum 这个词，而是把“哪些腿能活、哪些腿会把你坑死”说清楚了：

- **time-series momentum 强；**
- **cross-sectional momentum 弱很多；**
- **short-only 基本不值得信；**
- **很多看上去均值为正的组合，在日内波动和 liquidation 口径下其实并不安全。**

换句话说：

> **这篇论文最值钱的地方，不是再给一个“long-short 都能赚”的漂亮故事，而是明确告诉你：在 crypto 里，最可移植的 raw alpha 更像“只在强 regime 做多 market”，而不是“看到弱就放心做空”。**

## 3. 论文里最该记住的关键数字
### 3.1 样本与现实假设
- **样本：** `2014-01-26 ~ 2023-08-28`
- **核心处理：**
  - 每日 mark-to-market，而不是只看持有期末点收益；
  - 显式考虑 **transaction cost**；
  - 显式考虑 **portfolio liquidation**；
  - lookback / holding 扫描范围约 `1d ~ 56d`。

这点非常关键，因为作者其实是在纠偏很多 crypto momentum 论文常见的乐观偏差：
- 忽略持有期内大波动；
- 忽略账户被打穿的路径风险；
- 只看 t-stat，不看能不能真的活着把钱赚到手。

### 3.2 最强主线：market TSMOM long-only
论文摘要和主表最值得保留的是这组数：
- **最佳 long-only TSMOM：** `lookback = 28d`, `holding = 5d`
- **Sharpe ratio：** **`1.51`**
- **市场组合 Sharpe：** **`0.84~0.85`**
- **累计收益：** **`36,686%~36,786%`**（论文不同位置四舍五入略有差异）
- **市场组合累计收益：** **约 `2,696%`**
- **持仓占比：** **`48%`** 左右样本期
- **最大回撤：** **约 `61%~62%`**，显著低于市场组合 **`89%`** 左右
- **成本口径：** 主表按 **`15 bps`** 交易成本给结果

最重要的解释不是“收益有多夸张”，而是：

> **这条策略的大部分优势来自“只在顺风段持有、其余时间不硬扛”，所以它更像 regime-selective long beta，而不是全天候趋势永动机。**

### 3.3 短侧为什么不该当主菜
论文给出的结论很直接：
- **short-only portfolios 基本都不行；**
- **加上 short leg 后，long-short 往往不如 long-only；**
- 原因不是“空头完全没收益波动”，而是 **均值被侵蚀、风险却没换来足够补偿**。

这和 short-cycle desk 很相关，因为它直接提醒我们：

> **不要把“底部弱势”误读成“下一段一定还能继续跌”。在 crypto 里，弱侧更容易变成 violent rebound，尤其当你真的按路径风险和 liquidation 去算时。**

### 3.4 entry threshold 不是越极端越好
论文还专门测了不同入场阈值。对 `(28,5)` 这条 long-only 线：
- **10% 最强分位** 时，持仓期内 Sharpe 最高，可到 **`2.14`**；
- 但因为机会太少，**整段样本期 overall 表现反而不如更宽松阈值**；
- **30%~50% 阈值** 往往给出更好的“信号强度 × 机会频率”折中；
- 其中：
  - **50% threshold：Sharpe `1.37`，持仓比 `61.58%`**
  - **30% threshold：Sharpe `1.36`，持仓比 `43.74%`**
  - **10% threshold：Sharpe `0.94`，持仓比 `19.25%`**

这点对 desk 很有用，因为它说明：

> **最适合 production baseline 的，不一定是“只在最极端强势时追”。对真实资金更重要的是：既要有 edge，也要有足够稳定的出手机会。**

## 4. 这条 alpha 对 short-cycle desk 的正确读法
### 4.1 它是慢信号，不是逐根 K 线 trigger
这条策略本体的时间尺度是：
- **signal formation：** `28d`
- **holding：** `5d`
- **rebalance / re-check：** 日级

所以它不是“15m 上直接追 breakout”的信号，而更像：
- **慢速 raw alpha / direction book**
- 用 `1h/4h` 做状态计算
- 再用 `15m/5m` 做 execution 和风险控制

也就是说，它服务 short-cycle desk 的方式应该是：

> **把大方向交给 slow regime-aware raw alpha，把进出场拆给快执行层。**

### 4.2 desk 化时最自然的 market proxy
论文里的市场组合更接近 broad crypto market。落到我们这边，第一批 proxy 我会按下面优先级做：

1. **BTC 单资产 proxy**
   - 最容易复现
   - 流动性最好
   - execution 也最干净

2. **BTC/ETH cap-weighted proxy**
   - 比纯 BTC 更接近 crypto beta
   - 仍然容易在 perp 上执行

3. **Top-N liquid majors equal-weight / cap-weighted basket**
   - 更接近论文里的 market portfolio
   - 但执行和 roll 管理更复杂

我的判断是：
- **第一轮最小实验先拿 BTC 或 BTC+ETH 做 proxy 就够了；**
- 先验证“强 regime 才持有”这件事有没有信息量；
- 再决定值不值得扩到 multi-coin basket。

## 5. 为什么这篇值得 intake，而不是再去找一个更花哨的 ML/XS 题
### 5.1 它补的是我们当前更缺的“方向性 raw alpha 母板”
最近 digest 里已经有不少：
- cross-sectional
- pairs / spread fade
- residual / relative-value
- funding / basis / carry
- shock-reversal

但真正**明确、可复现、paper-faithful、还能直接写成完整规则**的单书方向性 alpha 母板并不多。

这篇补上的正是：

> **不是结构件，不是 filter，不是 overlay，而是一条可以独立站住的 market-level raw alpha。**

### 5.2 它顺手给了一个很强的反面结论
这篇另一个价值是：

> **在 crypto 里，别默认 short leg 和 long leg 对称。**

这对后续所有类似主题都有约束力：
- 不管是 time-series momentum 还是 cross-sectional momentum；
- 只要组合的一半利润预期来自空头继续塌；
- 就应该优先怀疑它会不会死在 rebound / liquidation 上。

这其实比“再发现一条新 trick”更值钱，因为它能帮我们少走很多弯路。

## 6. 策略拆解（必填）
- **方向属性：** single-book / market-beta / time-series momentum / long-only
- **基础 alpha：** 过去 `28d` 市场收益足够强时，未来 `5d` 继续偏强
- **entry：** 市场 proxy 的 `28d` return 落入其自身历史分位的高位区间（论文原始主线是 top third；更细阈值测试显示 `30%~50%` 更适合整体表现）
- **exit：** 持有 `5d` 后退出；若重新评估后不再满足高分位强势，则保持空仓
- **sizing：** paper-faithful baseline 可先用 `1x notional long market proxy / else flat`；落地时再叠加 vol targeting 或 risk budget
- **risk：** 每日 mark-to-market；必须把路径内 drawdown 和 liquidation 显式算进去；不要把 short side 当默认对称腿
- **cost：** 论文主结果使用 `15 bps`；我们迁移到 perp 时应至少做 `5/10/20/30 bps` cost ladder
- **filter / veto：** 这篇主线本身已内含 regime filter 含义；如果再加 filter，我更偏向只加 execution veto，不先加第二层方向滤波，避免和 alpha 本体混淆

## 7. 可复刻的最小实验
### 7.1 数据源、公开性、更新频率
- **数据源：** Binance USDⓈ-M perpetual public klines
- **公开性：** 完全公开 REST / historical kline
- **更新频率：** `1h` 足够做 slow signal；执行层可落到 `15m/5m`
- **最小可复现实验口径：**
  1. 选 `BTCUSDT` 或 `BTC+ETH` basket 作为 market proxy；
  2. 每天固定 UTC 时点计算过去 `28d` 收益；
  3. 用 expanding window 或至少 `2y` rolling history 把该收益映射为历史分位；
  4. 若分位进入 `top 30%~50%` 区间，则下一交易日开多；
  5. 固定持有 `5d`，期间每日 mark-to-market；
  6. 到期平仓，不做自动翻空。

### 7.2 下一步怎么测
下一步别急着复杂化，先做下面 4 个 A/B：

1. **proxy A/B：BTC vs BTC+ETH**  
   看 alpha 到底更像 BTC trend，还是更像 broader crypto beta。

2. **threshold A/B：33% vs 50% vs 20%**  
   复核论文所说的“极端阈值持仓内更强，但 overall 不一定最好”。

3. **execution A/B：日级收盘进场 vs `15m` TWAP 进场**  
   慢信号不变，只比较快执行能否降低滑点和入场时点噪声。

4. **no-short vs symmetric short**  
   显式验证：把下分位翻译成空头，是否真的只会恶化 Sharpe / drawdown / liquidation 画像。

### 7.3 第一批必须盯的指标
- `gross / net Sharpe`
- `exposure ratio`（在场时间占比）
- `max drawdown`
- `liquidation-aware path PnL`
- `threshold` 变化后的机会频率
- `BTC proxy` 与 `basket proxy` 的收益差
- `no-short` 与 `with-short` 的回撤与爆仓事件差

## 8. 风险与保留意见
- **这条策略虽然可直接落地，但它本质上是慢方向书，不是逐 bar alpha。** 不要把它硬包装成 `5m` 主信号。
- **论文样本覆盖 2014~2023 的大牛熊循环。** recent post-ETF / post-microstructure-change 环境下，信号强度可能漂移。
- **market proxy 的定义会显著影响迁移结果。** 用 BTC、BTC+ETH、还是 top-N basket，结论可能不同。
- **如果 desk 最终只能在单币 perp 上跑，这条策略的真实价值可能更多是“slow directional gate”，而不是独立大收益来源。**
- **short leg 的负面结论非常重要。** 后续若有人想把这篇改写成 long-short momentum，一定要先过 liquidation-aware 检验。

## 9. 来源
1. Han, C., Kang, B., & Ryu, J. (2024). *Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*. SSRN Electronic Journal.
   - DOI: `10.2139/ssrn.4675565`
   - DOI URL: <https://doi.org/10.2139/ssrn.4675565>
   - Readable PDF: <https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf>
   - Mirror PDF: <https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf>
2. Crossref metadata:
   - <https://api.crossref.org/works/10.2139/ssrn.4675565>
3. 本地全文抽取参考：
   - `/tmp/crypto_tsmom_xsmom_realistic_assumptions.pdf`
   - `/tmp/crypto_tsmom_xsmom_realistic_assumptions.txt`
