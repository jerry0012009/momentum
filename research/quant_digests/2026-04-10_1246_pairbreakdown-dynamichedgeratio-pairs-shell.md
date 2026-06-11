# pair-breakdown veto × dynamic hedge-ratio pairs shell
- 时间：2026-04-10 12:46 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/strategies/pairs_trading.py`）
- 主题类型：raw alpha
- 基础 alpha：`cointegrated spread mean reversion`（价差偏离过大后向均值回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/dynamic-hedge-ratio/pair-breakdown-veto/binance/5m/15m/repo/public-data/cost/risk
- 证据类型：工程证据

## 1. 这次看了什么
看了 **mefai-dev / mefai-autotrade** 里的 `src/strategies/pairs_trading.py`。它不是只给一个“协整 + z-score”口号，而是把 pairs 真正写成了完整策略壳：**先扫 pair，再做 admission，再动态更新 hedge ratio，再在关系失效时强制平仓**。

## 2. 核心结论
- **一句话核心结论：** 对 short-cycle desk，pairs 的关键不只是“spread 到 2σ 就 fade”，而是**持续确认这对资产还值不值得做**；最值钱的分支是 `pair-breakdown veto`，不是固定 z-score 本身。
- **一句话证明方式：** 源码把 pair admission 和存活条件写得很具体：`correlation > 0.7`、`cointegration p < 0.05`、`half-life ∈ [1, 50]`，并且每 `20` 根 bar 重新验证一次；一旦失效就触发 `pair_breakdown` 退出。
- 这份实现里的完整策略骨架很清楚：`entry = |z| >= 2.0`，`exit = |z| <= 0.5`，`stop = |z| >= 3.0`，`hedge_ratio_window = 30`，`lookback = 60`，`max_notional = 10000`，`risk_pct = 1%`。
- 真正适合我们 desk 借的，不是它简化版 ADF 近似本身，而是**admission / revalidation / breakdown exit** 三段式；这让 pairs 不再像“永远有效的静态关系”，而更像可交易、可失效、可撤退的 live alpha。

## 3. 为什么和当前项目有关
当前 `momentum` 已经积累了不少单资产趋势、均值回归、funding/basis、microstructure 线索，但 **pairs / stat-arb 这条线最容易在 short-cycle 里犯的错**，就是只盯 entry 阈值，不盯关系是否已经坏掉。这个 repo 的价值在于把 pairs 拆成 4 层：
1. **pair selection**：不是随便抓两个高相关币；
2. **spread alpha**：偏离够大才做；
3. **dynamic hedge**：仓位比例要滚动更新；
4. **breakdown veto**：关系失效就别继续“等回归”。
这很适合补进我们当前 raw alpha 素材池，而且完全能映射到 `5m/15m` 最小实验。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral / pairs mean reversion
- 基础 alpha：协整 spread 的短周期均值回归
- regime：仅在 pair 仍满足高相关、协整显著、half-life 合理时开机
- filter / veto：`corr > 0.7`、`p < 0.05`、`half-life ∈ [1,50]`、pair revalidation fail 即退出
- risk / sizing / execution overlay：rolling hedge ratio、`2σ` 入场 / `0.5σ` 出场 / `3σ` 止损、名义上限、`risk_pct` 仓位限制

## 4. 可复刻的最小实验
- **研究假设：** 在 Binance 高流动永续里，pairs 的 edge 不主要来自“更花的 entry 公式”，而来自**动态 admission + breakdown exit**；如果不做 live revalidation，很多看似便宜的 z-score fade 会拖成坏关系。
- **一个可计算定义：**
  1. universe 先取 `BTC / ETH / SOL / BNB / XRP / DOGE / ADA / LINK` 等高流动 perp；
  2. 每天或每 `4h` 扫一次 pair：保留 `corr > 0.7`、`EG p < 0.05`、`half-life ∈ [1, 50]`；
  3. `15m` 主交易，`spread_z = (spread - mean_60) / std_60`；
  4. `|z| >= 2` 入场，`|z| <= 0.5` 出场，`|z| >= 3` 止损；
  5. 每 `20` 根 bar 重验 pair；若协整失效直接平仓。
- **最小回测切口：** Binance USDⓈ-M `15m` 为主，`5m` 做 child execution；样本先跑 `2024-01-01` 以来，先只做 top-liquid pairs。
- **最该先看哪 1~2 个指标：**
  1. `post-cost bps / trade`
  2. `breakdown-exit share`（多少亏损单其实来自 pair 已失效却还在等回归）
  第二层再看 `positive-window ratio` 和 `pair survival days`。

## 5. 风险与保留意见
- 这份 repo 的统计检验是**轻量近似版**，不能把它当论文级检验；真正上线前要换成更严谨的 EG/Johansen/rolling OLS 工具链。
- `5m/15m` 下协整关系比日频更脆，revalidation 频率本身也是参数，过慢会放大坏关系，过快会造成 churn。
- 只看相关性和 p-value 还不够，成本、funding、交易时段、单腿流动性差异都会让“看起来中性”的 pair 变成假中性。
- 所以最合理的读法不是“源码参数可以照抄”，而是：**这份 repo 给了一个更像 production 的 pairs 壳——尤其是 live breakdown veto 这一刀。**

## 6. 来源
- mefai-dev. (2026). *Mefai Autotrade*. GitHub repository.  
  Repo URL: `https://github.com/mefai-dev/mefai-autotrade`
- Source file: `src/strategies/pairs_trading.py`  
  URL: `https://github.com/mefai-dev/mefai-autotrade/blob/master/src/strategies/pairs_trading.py`
- Project overview / strategy list:  
  URL: `https://github.com/mefai-dev/mefai-autotrade/blob/master/README.md`
