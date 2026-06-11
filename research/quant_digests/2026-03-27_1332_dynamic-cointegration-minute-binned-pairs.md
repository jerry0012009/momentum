# 别把 crypto pairs 只做静态二元：这篇 2021 SEF 更该先测的是「dynamic cointegration 选对/选篮子 + minute-binned spread convergence」raw alpha，但当前 `15m` 只在少数 pair pocket 还留净边
- 时间：2026-03-27 13:32 UTC
- 类型：2021 Studies in Economics and Finance 开放获取论文（arXiv 全文 PDF 可读）+ Binance USDⓈ-M Perpetual 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**在可协整的币对/币篮里，短期偏离长期均衡的 spread 会向均值回归；因此应当 long 低估腿、short 高估腿，吃的是 spread convergence，而不是市场单边方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/dynamic-cointegration/minute-binned/pair-selection/basket-selection/johansen/ou-half-life/zscore/binance/perpetual/15m/5m/1m/3m/paper/external-data/cost
- 证据类型：论文全文证据 + 当前公开市场最小 transfer check

## 1. 这次看了什么
先把 **base alpha** 说清楚：**这不是“crypto pairs 可能会均值回归”这种泛结论，而是“先动态找出协整关系最稳定、半衰期最短的 pair / basket，再在 spread 的短期异常偏离上做 long-short 收敛”。**

主材料是 **Masood Tadi, Irina Kortchemski (2021), _Evaluation of dynamic cointegration-based pairs trading strategy in the cryptocurrency market_, Studies in Economics and Finance**。这篇东西比普通 pairs baseline 更适合当前 desk 的地方，不在于又讲一遍 cointegration，而在于它把一条 **可以独立落地的完整 raw alpha 链条** 写得比较全：
- 数据口径不是老派日频，而是 **minute-binned**；
- formation / trading 不是一把梭，而是 **3 个月 formation + 1 周 trading** 动态滚动；
- 不是只做单 pair，还明确测了 **dynamic best-pair** 和 **Johansen basket** 两种版本；
- 不是只看 close-to-close 理想化收益，而是把 **best bid/ask、market trades、maker/taker fee、volume 可得性** 一起放进回测口径。

所以这轮值得 intake，不是因为它“又是一篇 pairs”，而是因为它其实给了我们两个很实用的可拆组件：
1. **dynamic pair-selection funnel**；
2. **multi-leg stationary basket**。

## 2. 核心结论
先给结论，不绕：
- 这篇的 **raw alpha 本体** 是 `spread deviation -> convergence`，不是 filter，也不是 overlay。
- 论文里最强的不是单纯 ADF 还是 KSS，而是：**动态选对 + 半衰期约束 + 真实执行口径**。
- 从结果看，**basket 版比单 pair 版更稳**；但真正能不能落到今天的 `15m`，仍然主要取决于 **换手、成本、pair 选择稳定性**。
- 我做的当前 `15m` transfer check 也支持这个判断：**这条 alpha 不是完全死了，但已经不是“任意 pair 都能活”；它更像要靠 pair pocket 和 cost governance 才能留净边。**

## 3. 为什么和当前项目直接相关
这轮它之所以应该放进当前 desk 的研究池，是因为它正好补上了两个空位：

1. **raw alpha 是完整的**
   - entry：spread z-score 偏离阈值；
   - exit：spread 回归阈值；
   - sizing：按 cointegration beta / Johansen 权重配腿；
   - risk：半衰期、pair stability、最大持有时长；
   - cost：maker/taker + quote availability。

2. **它不是只能服务于“老派双腿 pairs”**
   - 单 pair 版可直接对接我们已有的 `5m/15m` stat-arb 骨架；
   - basket 版可以直接服务后续 `multi-leg relative value / stationary basket / cross-sectional spread` 的拆解。

3. **它对当前 desk 的价值，比再找一篇花哨 filter 更直接**
   - 因为它回答的不是“这个 gate 会不会有帮助”，而是：
   - **spread convergence 这条 raw alpha，在真实 minute-level 执行口径下，到底还能不能做。**

## 3.5 策略拆解（必填）
- 方向属性：**relative value / stat-arb / mean reversion / market-neutral**
- 基础 alpha：**cointegrated spread 的异常偏离会向长期均衡回归**
- regime：更偏向 **相关关系稳定、结构未断裂、非单边爆趋势** 的环境
- filter / veto：
  - formation 期协整显著性
  - half-life 不能太长
  - rolling beta / correlation 漂移过大时禁做
  - volume / quote size 不足时禁做
- risk / sizing / execution overlay：
  - 单 pair：按 OLS beta 配对，gross 归一化
  - basket：按 Johansen 向量整数化权重构建 stationary portfolio
  - 必须显式计入 maker/taker fee、funding（如适用）、quote 可成交性

desk 化最小策略可以写成：
- **selection**：在 formation 窗口内，对候选币对/币篮跑 Engle-Granger / KSS / Johansen，选 `p-value 合格 + half-life 最短` 的候选；
- **signal**：`z_t = (spread_t - rolling_mean) / rolling_std`；
- **entry**：`|z_t| > z_enter` 时，long 低估腿 / short 高估腿；
- **exit**：`|z_t| < z_exit` 或 `max_hold` 到时退出；
- **sizing**：按 `1:beta` 或 cointegration vector 配腿；
- **risk**：若 rolling beta 漂移、quote depth 不足、或 spread 波动结构突变，则整对/整篮 veto；
- **cost**：必须按 round-trip bps 扣费，不能只看 gross。

## 4. 论文里真正可拿来复现的东西
### 4.1 数据与执行口径
- 交易所：**BitMEX**
- 样本：**2018-09-27 ~ 2019-10-02**
- 数据频率：**minute-binned**
- formation / trading：**3 个月 formation + 1 周 trading**，共 **39 个 trading weeks**
- 使用数据：minute close、volume、best bid/ask、market trades
- 合约池：`XBT/USD`, `ETH/USD`, `ETH/XBT`, `EOS/XBT`, `LTC/XBT`, `XRP/XBT`, `BCH/XBT`, `TRX/XBT`, `ADA/XBT`
- 费用口径：
  - maker fee **-0.0250%**
  - taker fee **0.0750%**
  - funding fee（永续）**±0.0100% 每 8 小时**

这点很关键：**它不是“日频收盘价上看起来好看”的论文，而是明确把 crypto 里最常见的 execution friction 放进去了。**

### 4.2 Scenario 1：动态 best-pair，每周换 pair
- formation 期先对候选 pair 做 Engle-Granger / KSS；
- 对通过 cointegration 的 pair，用 OU mean-reversion speed 估 half-life；
- **只选 half-life 最短** 的 pair 进入下周 trading；
- 开平仓规则：
  - `zscore` 穿越 **±2** 开仓；
  - 回到 **±1** 内平仓。

最值得记的数字：
- ADF 版本平均月收益约 **17.3%**；
- KSS 版本平均月收益约 **13.9%**；
- commission profit 占总利润约 **35%（ADF）/ 26%（KSS）**；
- 最大回撤约 **0.15 XBT**；
- Sharpe 约 **6.96（ADF）/ 6.57（KSS）**。

这里最值钱的结论不是“KSS 一定比 ADF 强”，反而是：
- **真正决定可交易性的，不只是谁的统计检验更 fancy，而是 liquidity / execution / half-life 有没有一起过关。**

### 4.3 Scenario 2：Johansen basket，比单 pair 更像 desk 组件
论文第二个版本不再只选一对，而是让多个币共同组成 stationary spread：
- 用 **Johansen test** 找 cointegration vector；
- 组合权重按可交易性和 half-life 约束做筛选；
- 每周滚动更新组合。

这版的数字非常重要：
- total realized P&L 约 **1.44 XBT**；
- 其中 commission profit 约 **0.81 XBT**；
- P&L 标准差约 **24.7%**；
- Sharpe 约 **7.94**。

翻成人话：**如果你不把 spread 固定在双腿，而是允许多个相关币一起形成 stationary basket，风险调整后表现会更好。**
这对我们 desk 很直接，因为它说明后续不少 `relative value / xs spread` 主题，并不一定非要停在 pair level。

### 4.4 Scenario 3：固定 pair 年度全样本，告诉你“哪些 pair pocket 真有东西”
作者还做了一个很实用的 sanity check：
- 不再每周重新优选，而是固定某个 pair，跑完整个研究窗口；
- 这样能看出哪些 pair 天生更适合做 spread convergence。

最强 pocket 很醒目：
- **TRX-ADA**：
  - profitable days **81.69%**
  - pair P&L **3.63 XBT**
  - cumulative return **363.17%**
  - max drawdown **-24.12%**
  - annual pairs Sharpe **20.38**
- 其他强 pair 还包括：
  - **LTC-ADA**：annual pairs Sharpe **12.43**
  - **XRP-ADA**：annual pairs Sharpe **11.06**
  - **BCH-ADA**：annual pairs Sharpe **10.21**

同时，论文明确写到：**同样样本下，buy-and-hold 在所有这些固定 pair 对照里都是负收益。**

这对 desk 的启发非常直接：
- 不是“pairs 都值得做”；
- 而是 **某类币（论文里尤其是 TRX / ADA / XRP）更容易形成可交易的 stat-arb pocket**。

## 5. 这轮最小 transfer check：2026 的 Binance USDⓈ-M `15m` 还剩什么
为了不只复述论文，我做了一个很小但诚实的 desk 映射：
- 市场：**Binance USDⓈ-M perpetual**
- 周期：**`15m`**
- 样本：近 **120 天**（共 **11,520** bars）
- split：前 **60% formation / 后 40% trading**
- pairs：直接优先测论文里最强 pocket 的现代映射：
  - `TRXUSDT/ADAUSDT`
  - `LTCUSDT/ADAUSDT`
  - `XRPUSDT/ADAUSDT`
  - `BCHUSDT/ADAUSDT`
  - `XRPUSDT/TRXUSDT`
- signal：formation 期 OLS beta，trade 期 spread rolling `z-score`
- rule：
  - `|z| >= 2.0` 开仓
  - `|z| <= 0.5` 平仓
  - `max_hold = 16 bars`
- 成本：**6 bps round-trip**

### 5.1 组合层结论
五组 pair 等权平均后：
- **gross ≈ +0.062 bps/bar**
- **net ≈ -0.019 bps/bar**
- gross cumulative ≈ **+2.63%**
- net cumulative ≈ **-0.85%**
- active share ≈ **21.3%**
- net annualized Sharpe ≈ **-0.84**

翻译一下：
- **base alpha 还在，但组合平均后已经被成本和不稳定 pair 吃掉。**
- 这说明这条线今天更像 **pair-pocket alpha**，不是 `always-on` 的全对等权篮子。

### 5.2 单 pair 层最重要的发现
1. **TRXUSDT/ADAUSDT 仍然活着**
   - gross ≈ **+0.125 bps/bar**
   - net ≈ **+0.051 bps/bar**
   - gross cumulative ≈ **+5.36%**
   - net cumulative ≈ **+2.12%**
   - active share ≈ **19.7%**
   - net annualized Sharpe ≈ **1.73**

2. 其余大多数论文赢家，到今天 `15m` 已经 mostly cost-negative
   - `LTC/ADA` net ≈ **-0.031 bps/bar**
   - `XRP/ADA` net ≈ **-0.038 bps/bar**
   - `BCH/ADA` net ≈ **-0.069 bps/bar**
   - `XRP/TRX` net ≈ **-0.008 bps/bar**

3. 所以最诚实的 desk 结论是：
   - **不是 pair alpha 整体失效；**
   - 而是 **只有少数 pocket 在当前成本口径下还剩净边，TRX/ADA 是这轮里最清楚的例子。**

## 6. desk 化判断
这篇我会明确归类成：**raw alpha / 可直接落地的完整策略骨架**。

但落地时要说清三件事：
1. **pair selection 比 entry/exit 更重要**
   - 今天最大的分化，不在于 z-score 公式，而在于你选的是不是“还活着的 pair pocket”。

2. **basket 可能比 pair 更值得继续追**
   - 论文里 basket Sharpe **7.94** 高于单 pair 版本；
   - 这说明把 spread 做成多腿 stationary portfolio，可能更接近我们 desk 后续该继续深挖的方向。

3. **当前 `15m` 更像 sparse deployment，不像全 universe always-on**
   - 组合平均后转负；
   - 单 pair 仍有 pocket；
   - 所以正确姿势更像：**先做 stability funnel，再只上线 surviving pairs。**

## 7. 下一步怎么测
### 7.1 第一优先：把 pair-selection funnel 做成显式评分，不再只看一次 formation beta
建议下一轮同时打分：
- cointegration p-value
- half-life
- rolling beta drift
- rolling correlation stability
- depth / spread / fee bucket
- 最近 30 天 trade count 与 active share

### 7.2 第二优先：把 basket 版从 paper 直接迁到 `15m`
这篇最值得继续的，不一定是单 pair，而是：
- 在 Binance perp 大币池里跑 **Johansen / sparse basket cointegration**；
- 然后测 multi-leg stationary spread 的 net edge。

### 7.3 第三优先：只在 surviving pocket 做 maker / passive execution 复测
现在 6 bps round-trip 已经把多数 pair 打回负数。下一步更该测：
- maker-only / maker-heavy 版本
- 按 liquidity bucket 分层的 fee cliff
- quote-life / fill probability / participation 上限

### 7.4 第四优先：把 hold rule 从固定 `max_hold=16` 改成 half-life aware
更合理的版本是：
- `entry` 继续用 `z`
- `hold horizon` 按 estimated half-life 分层
- `exit` 比较 `z->0.5`, `z->0`, `time stop`, `adverse beta drift`

## 8. 风险与保留意见
- 论文样本是 **2018~2019 BitMEX**，市场结构和今天已经不同；
- 我这轮 transfer check 不是 clean replication，只是 desk 化最小映射；
- 但即使如此，paper 和当前数据仍给出同一个方向：
  - **spread convergence 不是伪命题；**
  - **真正难的是 selection stability 和 cost survival。**

所以它的正确定位不是“今天立刻整篮子上线”，而是：
- 作为 **pair/basket stat-arb 家族的高质量 raw alpha 基线**；
- 并且明确告诉我们：**别再把精力只花在 z-score 微调上，真正该卷的是 pair funnel、basket 结构和执行口袋。**

## 9. 来源
1. **Tadi, M., & Kortchemski, I. (2021). _Evaluation of dynamic cointegration-based pairs trading strategy in the cryptocurrency market_. Studies in Economics and Finance, 38(5), 1054–1075.**
   - DOI: `10.1108/SEF-12-2020-0497`
   - Readable URL: `https://arxiv.org/abs/2109.10662`
   - PDF URL: `https://arxiv.org/pdf/2109.10662.pdf`
   - Publisher URL: `https://doi.org/10.1108/SEF-12-2020-0497`
   - Repo URL: `N/A`
2. **Binance USDⓈ-M Futures public klines API**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 10. 本地相关产物
- Digest：`research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
- Artifact：`reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.html`
