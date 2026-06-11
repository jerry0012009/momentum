# 别把这份 2025 hybrid XS/TS momentum repo 只读成日频作业：对 short-cycle desk，更该先测的是「breadth-conditioned XS momentum × shallow-bear sign-flip router」
- 时间：2026-04-07 14:12 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `crypto_stat_arb_momentum.ipynb` + GitHub repo metadata）
- 主题类型：raw alpha
- 基础 alpha：横截面强弱排序；市场只负责决定当前做 `winner continuation` 还是 `shallow-bear loser bounce`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/reversal/regime-router/volume-adjusted/top-bottom/binance/15m/5m/3m/repo/cost/risk
- 证据类型：工程经验

## 1. 这次看了什么
主看 `964quanyuan/crypto-strategy`。README 很短，真正有价值的是 notebook `crypto_stat_arb_momentum.ipynb`：它把一篮子 Binance majors 做成 `XS + TS` 混合动量。对 short-cycle desk 来说，最值得偷的不是整套日频 MVO，而是其中一条可直接拆出来的 raw alpha：**先做横截面强弱排序；只有当全市场 aggregate return 轻微转负时，才把这本 momentum 书短暂翻成 reversal；若跌得更深，则直接 flat。**

## 2. 核心结论
- **base alpha 很清楚**：不是 regime 本身，而是一篮子币的 `cross-sectional momentum / reversal` 路由；regime 只负责决定当前该跑 continuation 还是 shallow-bear fade。
- repo 用 **15 个 Binance majors**（`BTC/ETH/LTC/DOT/MATIC/SOL/ETC/ALGO/BNB/AVAX/ATOM/NEAR/XRP/ADA/LINK`），样本 `2021-10-15` 到 `2025-05-31`，训练到 `2024-03-31`，`2024-04-01` 之后做 holdout。
- XS 信号不是裸收益，而是 **过去 98 日累计收益 × 成交量相对 EWMA 强度**，再做 `rank-demean-normalize`；这点很适合 intraday 直接改成 `15m` 版。
- 最值钱的旁支是 **浅跌翻书**：当 basket aggregate return `0 > r_mkt > -0.5%` 时，把 XS momentum 暂时翻成 reversal；若 `r_mkt <= -0.5%`，则直接 flat。它比“永远追强势”更像 desk 能快速验证的 regime-aware raw alpha。
- notebook 给出的 repo 级证据不差：in-sample XS 这一腿 **alpha = 0.1253%/day，t-stat = 3.42**；TS 腿 **alpha = 0.2407%/day，t-stat = 2.49**。holdout 里两种 blend 的 Sharpe 约 **1.81 / 1.98**，都高于 benchmark 的 **1.35**；其中 `81:19 XS/TS (Alternative)` 组合仍有 **alpha = 0.1103%/day，t-stat = 2.23**。这已经足够支持做最小复现，而不是只把它当课程展示。

## 3. 为什么和当前项目有关
最近几轮 intake 里，pairs / carry / maker / prediction-market 已经不少；这篇更适合补 **cross-sectional raw alpha** 这一格。关键是它没有把 `regime` 伪装成 alpha，而是先承认真正赚钱的本体是 **winner-minus-loser / loser-bounce 路由**，再用一个非常便宜的 market-breadth 条件决定该用哪一本书。对 `1m/3m/5m/15m` desk 来说，这比再抄一层复杂 MVO 更直接。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：`volume-adjusted cross-sectional momentum`，浅跌时切成 `cross-sectional reversal`
- regime：basket aggregate return 的 shallow-bear 区间判断
- filter / veto：深跌区（`r_mkt <= -0.5%`）暂停交易；只保留流动性足够的 liquid-major universe
- risk / sizing / execution overlay：top-bottom 等权或 rank-weight；每 bar / 每 3 bar 调仓；单币权重上限 + turnover cap + 成本阈值

## 4. 可复刻的最小实验
- **研究假设**：在 liquid-major perp/spot 篮子里，“横截面强弱”本身有 edge；但当全市场只出现**浅负 breadth**时，短期更容易从 continuation 切到 loser-bounce。
- **可计算定义**：
  1. `xs_raw_i = ret_i(L) * (vol_i / EWMA(vol_i, L))`
  2. 对全篮子做 `rank-demean-normalize`，得到 `w_xs`
  3. `r_mkt = mean(ret_i(Lm))`
  4. 若 `r_mkt > 0`：交易 `w_xs`；若 `0 > r_mkt > -θ`：交易 `-w_xs`；若 `r_mkt <= -θ`：`w = 0`
- **最小回测切口**：`Binance / Bybit` liquid majors（先 8~12 个），`15m` 主实验、`5m` 复核；`L = 32~96 bar`，`Lm = 8~24 bar`，`θ = 0.3%~0.8%`；top 20% long、bottom 20% short，`next-bar open` 成交。
- **下一步先看**：`post-cost Sharpe` 与 `turnover / cost cliff`。如果浅跌翻书只在高换手下成立，就别进主池。

## 5. 风险与保留意见
最大问题是 **repo 原始证据是日频**，直接搬到 `5m/15m` 很容易把“浅跌翻书”变成噪音开关，所以必须先测 turnover、滑点和 funding。第二个风险是 universe 偏 major bias / survivorship，说明它更像 **liquid-major XS sleeve**，不是全市场通吃。第三个风险是 `-0.5%` 这种阈值在日频成立，不代表 intraday 也同口径有效，必须重做 threshold sweep 与 out-of-sample。

## 6. 来源
1. **964quanyuan. (2025). _crypto-strategy_. GitHub repository.**
   - Repo URL: <https://github.com/964quanyuan/crypto-strategy>
   - Readable URL: <https://github.com/964quanyuan/crypto-strategy>
   - README: <https://raw.githubusercontent.com/964quanyuan/crypto-strategy/main/README.md>
   - Notebook: <https://raw.githubusercontent.com/964quanyuan/crypto-strategy/main/crypto_stat_arb_momentum.ipynb>
2. **GitHub repository metadata**
   - Repo API: <https://api.github.com/repos/964quanyuan/crypto-strategy>
   - Created: `2025-07-30`
   - Updated: `2025-10-16`
