# 别把这篇 2024 crypto momentum 论文只读成“TSMOM 强、XSMOM 弱”：对 short-cycle crypto desk，更该先拆的是「cross-sectional rank sign router：不同 bucket / horizon 下，winner-continuation 与 loser→winner fade 会换符号，且 short leg 默认要降权或否决」

- 时间：2026-04-25 11:16 UTC
- 类型：2024 SSRN 论文全文 audit（PDF full text）+ Binance USDⓈ-M public-data portability probe（`1h` parent，`10` 个 majors vs `17` 个 liquid midcaps）
- 主题类型：raw alpha
- 基础 alpha：**横截面相对收益排序本身就是 alpha，但它的“该追强还是反着做”不是常数；在不同 universe bucket 与持有时长下，signal sign 会切换。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但默认应先做 `bucket × sign × hold` 标定，并把 short leg 视为高风险可选项）
- 主题标签：raw-alpha/cross-sectional/relative-value/momentum/mean-reversion/sign-router/bucket-switch/largecap-vs-broad/liquidation-aware/long-only-bias/1h/5m/15m/paper/public-data/cost/risk
- 证据类型：paper full text + public futures portability probe

## 1. 这次看了什么
这轮主材料是 2024 SSRN working paper：

- **Han, Chulwoo; Kang, Byeongguk; Ryu, Jehyeon (2024)**
- **Title:** *Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*
- **Venue:** SSRN working paper
- **Readable URL:** <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565>
- **PDF URL:** <https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf>
- **DOI:** 未见正式期刊 DOI；当前可引用 SSRN `4675565`

我没有把它按论文 headline 直接读成“crypto 里 time-series momentum 比较强，cross-sectional momentum 比较弱”，而是专门抓了一个更适合我们 desk 的旁支：

> **横截面 rank 这个 alpha 本体可能没死，但它的 sign 不是固定的。你不能默认“永远追 winners”，也不能默认“永远 fade winners”。**

翻成人话：
- 先把所有币按过去一段时间涨跌做个横截面排序；
- 这个排序本身有信息；
- 但接下来到底该 **long winners / short losers**，还是 **long losers / short winners**，取决于你看的 bucket、持有多久、以及你愿不愿意承受 short leg 跳涨爆仓风险。

这比单纯记一句“crypto momentum exists / does not exist”更适合进我们短周期素材池。

## 2. 一句话结论
- **一句话核心结论：** 这篇 paper 最值得 intake 的，不是“TSMOM 比 XSMOM 好”这个大标题，而是更细的交易结论：**横截面 rank 要做成 `bucket × sign × hold` 路由器，不能把 sign 当常数；同时 short leg 不是免费中性化，很多时候它才是把策略拖死的那条腿。**
- **一句话证明方式：** 论文里 broad universe 与 top-5% largest-coins 的横截面回归结果会换符号，组合回测里 long-only 又经常优于 long-short；我再用 Binance 公共数据做了一个 `1h` 最小 portability probe，结果也显示 **不同 bucket / hold 的 sign 会变，而且和论文样本期不完全同向。**

## 3. 为什么这轮值得做
这轮值得做，不是因为它又讲了一遍“动量/反转”老故事，而是因为它给了当前 desk 一个很实用的提醒：

1. **base alpha 是清楚的。**
   不是某个模糊情绪 filter，而是横截面 relative-return ranking 本身。

2. **它天然覆盖 raw alpha 两个大类。**
   同一套 rank 框架，既能变成 relative-strength continuation，也能变成 loser→winner mean reversion。

3. **它直接回答我们现在最容易踩的坑。**
   很多 repo / paper 会默认 sign 不变，但这篇 paper 恰好告诉你：**同样是 cross-sectional rank，换 universe、换 horizon，信号方向会漂。**

4. **它能很自然映射到 `1m / 3m / 5m / 15m`。**
   不需要直接把日频论文硬抄成逐根主信号；更合理的做法是：
   - 父层 `1h` / `4h` 做 rank 与 sign 选择；
   - 子层 `15m / 5m` 做更便宜的执行、撤退、减仓。

所以这不是“纯解释型综述”。它是一个**明确服务 raw alpha intake 的 routing 结论**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / sign-conditional momentum-or-reversal
- 基础 alpha：过去一段时间在同篮子里相对更强或更弱的币，未来一小段仍存在系统性相对收益差
- 关键分歧：这个相对收益差是 **continuation** 还是 **reversal**，要由 bucket / horizon 决定
- regime：优先用 universe bucket（largest-coins / majors / midcaps）+ 持有时长决定 signal sign；不是先加复杂宏观 filter
- filter / veto：
  - short leg 默认先降权或直接 veto
  - 极端单币跳涨 / 新币 / 疑似脏流动性优先排除
  - 若 parent rank 与 child execution 同向 markout 很差，则缩短 hold 或回退到 long-only
- risk / sizing / execution overlay：
  - 父层 `1h` 产出 rank 与 sign
  - 子层 `15m/5m` 做 maker-first / pullback entry / time-stop
  - gross 先常数，别一上来做复杂动态杠杆
  - short leg 使用更低 notional cap、更紧 stop、更严格 admission

## 4. paper 里最值得拿走的 6 个点

### 4.1 作者不是只做“均值 t 检验”，而是把真实交易约束放进来了
paper 明确强调：
- 只看 holding-period 终点收益，会低估中途大幅波动和爆仓风险；
- 因此他们按日 mark-to-market；
- 还把 **transaction cost、tick size、slippage、futures shortability、margin liquidation** 都放进评估里。

这点很重要：它让我们能更放心地把结论翻译成 desk 语言，而不是停留在“学术上的显著性”。

### 4.2 broad universe 的横截面回归，短窗里大多是负号
paper 的 Table 12（all coins）最值得记住的一点不是“某个单格显著”，而是整体形状：

- lookback `1~7` 天、holding `1~7` 天附近，很多系数是 **负的**；
- 翻成人话就是：
  **在更广的币池里，短窗相对强弱很多时候不是延续，而是更接近短期反转。**

也就是说，broad universe 下，默认去追 winners，并不是最稳的先验。

### 4.3 但 largest 5% bucket 里，很多系数又翻成正号
paper 的 Table 13（largest 5% coins）给出的恰好是另一个方向：

- 当只看最大的 5% 币时，很多短 lookback / 短 hold 组合又转为 **正系数**；
- 作者原文的表述就是：当只用 top 5% coins 时，许多系数转正，且 **lookback 和 holding period 都偏短时，momentum effect 更强**。

这意味着：

> **同一个 cross-sectional rank，在 broad universe 里更像 reversal，在 largest bucket 里又可能更像 continuation。**

这就是本轮最值得 intake 的“sign router”思想。

### 4.4 long-only 往往比 long-short 更像可活下来的版本
paper 的组合结果（Table 14）对我们尤其有用：

- 论文里很多 long-short portfolio 虽然均值为正，但风险并不友好；
- 一些组合在样本期内直接被 liquidated；
- **long-only 往往比 long-short 更稳，且经常有更好的 Sharpe。**

翻成人话：
- “做空 losers 来中性化 beta”这件事，在 crypto 里经常不是降风险，而是在捡 jump risk；
- 你以为自己加了 market-neutral，实际可能只是给组合挂上一条最容易炸的腿。

### 4.5 论文自己也给了几个记忆点
几个最有用的数字：

1. **time-series momentum long-only 的最好 Sharpe 大约到 `1.51`**（paper 摘要与正文总结层面）
2. **cross-sectional best long-short after-cost Sharpe 大约 `1.31`（`(1,7)`）**
3. **`(14,7)` long-short after-cost 虽有很高累计收益，但 7 个 rebalancing-day 账户里有 3 个被 liquidated**

这些数字的 desk 含义很简单：
- 不是说 XSMOM 没 edge；
- 而是说 **short leg 与路径风险会严重改变“看起来有效”的 alpha 真实可交易性。**

### 4.6 真正该学的不是某个固定参数，而是“先分 bucket 再定 sign”
如果只抄论文 headline，很容易写成：
- “crypto 里 TSMOM 强，XSMOM 弱”；
或
- “largest coins 做 momentum，broad universe 做 reversal”。

这都还不够 desk 化。

更好的落地方式是：
1. 先定 universe bucket；
2. 再扫描 sign（continuation / reversal）；
3. 再找最适合的 hold；
4. 最后才接 child execution。

## 5. 我做的最小 portability probe：近期 Binance perp 不会原样复现论文方向
为了避免只写文献摘抄，我额外用 Binance USDⓈ-M 公共数据做了一个很小的 portability probe。

### 5.1 数据口径
- 数据源：Binance Futures REST `fapi/v1/klines`
- 公开性：公开可得，无需私钥
- 更新时间：实时可取历史 K 线
- 本轮口径：
  - bar: `1h`
  - 样本：每个币最近 `1000` 根 `1h` close
  - majors：`BTC ETH BNB SOL XRP ADA DOGE TRX LINK AVAX`
  - midcaps：`ATOM LTC BCH DOT NEAR ARB OP SUI APT INJ RUNE AAVE UNI ETC FIL ENA WIF`
- 最小策略壳：
  - lookback = `24h`
  - 每次排序后 long bottom 3 / short top 3（reversal）或 long top 3 / short bottom 3（momentum）
  - hold = `1h / 2h / 4h / 6h / 8h / 12h / 24h`
  - round-trip friction：`2 bps/side` 的粗略扣减

### 5.2 快检结果
结果并没有“原样复现 paper 的 sign 结论”，反而说明 **近期 Binance perp 下 sign 更需要重新标定**：

#### majors bucket（10 个大币）
- `24h lookback + 6h hold` reversal：Sharpe ≈ **2.03**
- `24h lookback + 12h hold` reversal：Sharpe ≈ **3.07**
- `24h lookback + 24h hold` reversal：Sharpe ≈ **3.95**
- 同口径 momentum 在这些 hold 上都还是明显负的

#### midcaps bucket（17 个 liquid midcaps）
- `24h lookback + 12h hold` momentum：Sharpe ≈ **1.36**
- `24h lookback + 24h hold` momentum：Sharpe ≈ **3.32**
- 同口径 reversal 基本一直为负

### 5.3 这组快检说明什么
至少说明三件事：

1. **paper 的方向不能直接照抄到当前 Binance perp。**
   样本期、可交易 universe、listing 筛选、futures 结构都不一样。

2. **sign 的确会切换。**
   只是这次切换方式和 paper 样本不完全一致：
   - paper 更像“largest continuation / broad reversal”；
   - 当前快检更像“majors reversal / liquid-mid momentum”。

3. **这反而强化了本轮主题。**
   我们真正要 intake 的不是“固定 sign 结论”，而是：
   **cross-sectional rank 要先做 bucket × sign × hold 的 calibration。**

## 6. 对 desk 最值钱的可移植版本是什么
我不会把本轮主题落成“又一个论文复述版 XSMOM”。

我会把它落成下面这个更实用的 raw-alpha shell：

### A. parent alpha 层
- 每 `1h` 计算一次 cross-sectional return rank
- 对不同 universe bucket 分开维护两种假设：
  - winner continuation
  - loser→winner reversal

### B. sign router 层
- 不是写死 sign，而是按 bucket 选择：
  - majors 一套 sign / hold
  - midcaps 一套 sign / hold
- 每周或每月滚动重估，不要逐日乱跳

### C. short-leg veto 层
- 若该 bucket 的 short leg 历史 jump risk 太高：
  - 改成 long-only winners 或 long-only losers rebound
  - 或 short leg 只给 half size

### D. child execution 层
- `15m / 5m` 只负责：
  - pullback better-fill
  - maker-first
  - 超时未成交转 taker
  - time-stop / adverse-move kill

这比“固定做多强币做空弱币”更诚实，也更贴近当前 desk 的复现节奏。

## 7. 我的判断：该 intake，但读法必须改
我的判断不是“论文结论已经证明某个 sign 就是标准答案”。

我的判断是：

> **这篇 paper 很值得 intake，但要 intake 的是“sign router 思路”，不是某个固定的 cross-sectional momentum 参数表。**

具体来说：
- **值得保留的部分**
  - rank 本体是清楚的 raw alpha
  - broad vs largest 会换符号
  - long-only 往往比 long-short 更像真实可交易版本
  - 路径风险与 liquidation risk 不能省略

- **不能直接照抄的部分**
  - sign 方向
  - 具体 lookback / hold
  - broad universe 定义
  - 2014~2023 样本期下得到的稳定性印象

## 8. 它和当前 `1m / 3m / 5m / 15m` 的关系
这题和我们当前短周期 desk 的关系，不是“直接把日频论文缩成 5m 逐根主信号”。

更自然的映射是：

- **`1h` parent**：
  做 universe 内相对收益排序，决定今天/这几个小时是更适合追 winners 还是抄 losers。

- **`15m` child**：
  做入场优化，例如 pullback entry、maker-first、事件后第 2 根再进。

- **`5m / 3m / 1m` child**：
  只做更细的执行与风险控制，不承担“重新定义 alpha sign”的任务。

也就是说，这轮主题更像：
- `1h` 决定 **信号方向与篮子**
- `15m/5m` 决定 **怎么更便宜地把它做进去**

## 9. 风险与保留意见
1. **paper 与当前市场状态可能不一致。**
   近期 perp 结构、上币节奏、memecoin 权重、资金面都可能改变 sign。

2. **short leg 依旧是最大雷区。**
   无论论文还是快检，都说明 short 不是免费对冲器。

3. **bucket 划分本身会影响结果。**
   你用 market cap、成交额、可做空性、上币年龄去分，结论都可能不同。

4. **`1h` parent 的信号不应被误读成 `5m` 逐根信号。**
   高频执行只是降低成本，不是替代 alpha 本体。

5. **当前 portability probe 很粗。**
   这里只是一个 sign quick-check，不是正式回测；还没有做 funding、maker fill、真实成交冲击、delist / listing age control。

## 10. 下一步怎么测
只做最小必要实验，不要直接炼丹。

### 实验 1：bucket × sign × hold 网格扫描
在 Binance USDⓈ-M 上先固定一个 `20~30` 币 universe，再分成：
- top majors
- upper-mid liquid
- lower-mid liquid

对每个 bucket 扫：
- lookback = `6h / 12h / 24h / 48h`
- hold = `1h / 2h / 4h / 8h / 12h / 24h`
- sign = momentum / reversal

目标不是先追最高 Sharpe，而是先看 **sign 热区是否稳定**。

### 实验 2：long-only vs long-short vs half-short
对最优 3 组 parent 参数，各跑：
- long-only winners
- long-only losers rebound
- long-short full size
- long-short half short

目标：确认 short leg 到底是在增益，还是只是拖累。

### 实验 3：`1h parent -> 15m/5m child` execution
固定 parent rank + sign 后，在 child 层对比：
- 下一根 taker 直接进
- `15m` pullback 限价
- maker-first，超时 `30m/60m` 转 taker

摩擦至少做三档：
- `4 bps`
- `8 bps`
- `12 bps`

### 实验 4：listing age / funding / jump veto
给 raw alpha 接最少量但最有用的 veto：
- 上市未满 `30d/60d` 剔除
- funding 绝对值过高时 short leg 降权
- 单币过去 `24h` 出现极端跳涨时 short leg 暂停

目标：先修最容易炸的尾部，不要先加十几个花哨指标。

## 11. 最小可复现实验口径（给后续复现的人）
- 数据源：Binance USDⓈ-M `fapi/v1/klines`
- 公开性：公开 REST，可直接抓
- parent 周期：`1h`
- child 周期：`15m / 5m`
- universe：先从 `20` 个高流动 USDT perpetual 开始
- rank 指标：过去 `24h` 收益在同篮子中的横截面排序
- 组合版本：
  - winner continuation
  - loser→winner reversal
  - long-only / long-short / half-short
- 成本：先做 `4/8/12 bps` 梯度
- 风控：单币权重上限、bucket gross cap、time-stop、jump veto、listing-age filter

## 12. 来源
- Han, C., Kang, B., & Ryu, J. (2024). *Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*. SSRN Working Paper.
- Authors：Chulwoo Han; Byeongguk Kang; Jehyeon Ryu
- Year：2024
- Title：*Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions*
- Venue：SSRN
- DOI：N/A（当前未见正式期刊 DOI）
- Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565>
- PDF URL: <https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf>
- SSRN mirror marker in paper: `Electronic copy available at: https://ssrn.com/abstract=4675565`
- Public data API reference: <https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data>

## 13. 这轮最该记住的一句话
**横截面 rank 不是问题，真正的问题是你不能把它的 sign 当常数；先按 bucket 定 sign，再决定要不要保留 short leg，才是这篇 paper 对 short-cycle crypto desk 最值钱的读法。**
