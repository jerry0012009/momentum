# BTC-hedged residual sign fade alpha
- 时间：2026-04-15 03:13 UTC
- 类型：GitHub repo source audit + Binance public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：BTC-hedged residual one-bar fade（先去掉 BTC beta，再反打上一根 residual 的方向）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / mean-reversion / relative-value / BTC-hedged / residual / one-bar-fade / sign / perp / short-cycle / Binance
- 证据类型：repo 源码 + 公开行情 portability probe

## 1. 这次看了什么
这次看的是 **Dastrial / crypto_strat**（2025 GitHub repo，描述是 *Cryptocurrency perpetual futures mean-reversion*）。它非常简陋，但胜在 **base alpha 清楚、最小实验极快**：

1. 先用训练集估计每个币对 BTC 的 beta：
   \[
   \alpha_i = \frac{\operatorname{Cov}(r_i, r_{BTC})}{\operatorname{Var}(r_{BTC})}
   \]
2. 构造去 BTC 市场暴露后的 residual return：
   \[
   r^{res}_i = r_i - \alpha_i r_{BTC}
   \]
3. 下一根直接做反向：
   \[
   position_{t} = -\operatorname{sign}(r^{res}_{i,t-1})
   \]

repo 的核心一行其实就这一句：

```python
mean_reversion_by_portfolio = -np.sign(returns).shift(1).fillna(0) * returns
```

也就是说，它不是在做“pair cointegration”或“多因子 ranking”，而是在做一个更快、更粗暴的 **beta-stripped one-bar contrarian baseline**。

**一句话核心结论：** 这份 repo 的价值不在工程完成度，而在它提供了一条非常快就能 falsify 的 raw alpha 基线：`先去 BTC beta，再反打 residual sign`。  
**一句话证明方式：** 我主要依赖 repo 源码拆解 + Binance USDⓈ-M liquid-major 短周期 probe 来判断它在 `15m/5m` 上是否还有生命体征。

## 2. 核心结论
- **base alpha 很清楚**：不是“全市场反转”，而是 **去掉 BTC 共振后的 idiosyncratic residual 反转**。
- 和最近那类 `BTC-beta-neutral residual momentum ranking` 材料相反，这个 repo 走的是 **residual momentum 的对手盘**：它假设 residual 冲击更像短噪声，下一根倾向回吐。
- 这类思路对 short-cycle desk 的意义很大，因为它几乎是最便宜的 relative-value baseline 之一：
  - 不需要 order book
  - 不需要 funding / OI / basis 外部数据
  - 不需要复杂 pair admission
  - 只需要 `BTC + 一组 liquid alts` 的 bar return
- 但 repo 也很明显 **不够 production**：
  - 没有显式成本
  - 没有退出/持有期设计（本质上每根 bar 都重新定方向）
  - 没有 risk cap / kill switch
  - 没有 admission / filter
  - 没有解决 residual spike 的状态分层

## 3. 为什么和当前项目有关
这个主题虽然不是完整策略壳，但它和当前 desk 很相关，因为它补的是一个 **非常值得有的 fast null baseline**：

> 如果连最基础的 `BTC-hedged residual one-bar fade` 都完全站不住，那后面加各种 regime/filter 大概率只是在给噪声做装修。

换句话说，它适合作为：
- `relative-value / mean reversion` 方向的零阶起点；
- 后续 funding / OI / dispersion / session gate 的母信号；
- 和 residual momentum / lead-lag / stat-arb 主题做对照的最小基线。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / market-beta-stripped mean reversion
- 基础 alpha：BTC-hedged residual return 的一根反转
- regime：repo 未提供，后续可外接 `BTC realized vol / dispersion / session pocket`
- filter / veto：repo 未提供；更合理的扩展是 `|residual|` 分位阈值、liq filter、event veto
- risk / sizing / execution overlay：repo 只有最粗糙的等权平均；缺少明确 risk / cost / execution 设计

## 4. 可复刻的最小实验
**研究假设**：短周期里，很多 alt 的单根冲击本质上只是“BTC 共振 + idiosyncratic overshoot”，先 strip 掉 BTC beta 后，residual sign 的下一根更可能回吐。  
**可计算定义**：
1. universe：`BTC + ETH/SOL/XRP/DOGE/ADA/BNB/LINK/AVAX/DOT/LTC/ATOM`
2. 训练集估计 `alpha_i = cov(r_i, r_BTC)/var(r_BTC)`
3. 生成 normalized residual：`(r_i - alpha_i * r_BTC) / (1 + |alpha_i|)`
4. 信号：`position_t = -sign(residual_{t-1})`
5. 组合：对所有 alt 等权平均
6. cost ladder：`4 / 8 / 12 bps`

**最小回测切口**：
- 先做 `15m`
- 若 `15m` 连 gross 都不过线，就别急着下钻 `5m`
- 若 `15m` gross 有点生命，再看 `5m` 是否只是更差的高换手版本

## 5. portability probe
我先补了一个 **Binance USDⓈ-M public-data quick probe**。第一版为了快，用的是运行时 `24h quoteVolume` top-25 合约 + BTC hedge leg 的动态 universe，所以它更适合做 **方向性 first verdict**，不该被误当最终定版回测。

`15m` 结果很直接：
- 矩阵规模约 `1321 x 26`（含 BTC），alt 侧 `25` 个组合；
- `median |alpha| ≈ 0.80`，说明大部分币对 BTC 的 beta 不低；
- `avg turnover / bar ≈ 0.91`，已经在提醒这条线极度换手；
- **gross 已经为负**：约 `-2.04 bps / bar`；
- 扣 `4bps` 后约 `-5.67 bps / bar`，测试段累计约 `-22.03%`；
- 扣 `8bps / 12bps` 后测试段累计进一步恶化到约 `-33.46% / -43.21%`。

也就是说，这条 repo baseline 至少在这版短周期 perp probe 里，不是“有点 edge 但被费用打掉”，而是 **gross 就已经明显不过线，cost 只是雪上加霜**。

`5m` 清洗版本来想继续跑，但在第二轮抓取时碰到 Binance 临时 rate-limit ban；因此这轮先把 `15m` 当 first verdict，`5m` 放到下一步固定 liquid-major 干净样本里复核。

## 6. 风险与保留意见
- 这种 one-bar fade baseline 最大问题通常不是 admission，而是 **换手太高**；这轮 probe 的 `avg turnover / bar ≈ 0.91` 基本已经把这个问题直接暴露出来了。
- 一旦用 BTC 对冲，名义上虽然更 market-neutral，但实际多了一条 BTC hedge 腿，成本只会更敏感。
- 这轮更糟的是 **gross 先坏掉**，说明问题不只是费用，也可能是“逐根反打 residual sign”本身在当前 short-cycle perp 环境里过于生硬。
- 如果 post-cost 不行，不代表 residual 方向完全错；更可能意味着：
  - 需要 `thresholded residual` 而不是全量逐根翻仓；
  - 需要 `hold 2~3 bars` 而不是 1 bar；
  - 需要只在高-dispersion / 非 BTC trend rush 时启用。

## 7. 下一步怎么测
1. **先做 threshold 版**：只在 `|residual_{t-1}|` 超过 rolling `70% / 80% / 90%` 分位时才入场。  
2. **再做 hold-horizon 扫描**：对比 `1 / 2 / 3 / 4 bar` 持有，不要默认一根就平。  
3. **加最少量 regime gate**：`BTC realized vol`、`cross-sectional dispersion`、`US session / Asia session` 三个就够。  
4. **若仍不过线**：这条线应从“主信号”降级成 `shared veto / fade overlay`，服务于更强的 residual momentum / lead-lag / event-driven raw alpha。

## 8. 来源
- Authors: Dastrial（GitHub handle）
- Year: 2025
- Title: *crypto_strat*
- Venue: GitHub
- DOI: N/A
- Readable URL: `https://github.com/Dastrial/crypto_strat`
- Repo URL: `https://github.com/Dastrial/crypto_strat`
- 关键源码：
  - `datas/fetch_hourly_data.py`
  - `datas/train_test_split.py`
  - `portfolios/btc_hedged_portfolios.py`
  - `strategy/basic_mean_reversion.py`
  - `strategy/plotSignal.py`
  - `statistic_tests/autoCorrelsEMAThreshold.py`
- 本地探针：
  - 汇总：`reports/artifacts/quant_digests/2026-04-15_btc_hedged_residual_fade_probe_summary.json`
  - 脚本（后续 fixed-major clean rerun 用）：`reports/artifacts/quant_digests/2026-04-15_btc_hedged_residual_fade_probe.py`
