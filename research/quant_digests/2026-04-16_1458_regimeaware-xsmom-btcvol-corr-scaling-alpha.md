# 别把这份 2026 新仓只读成“风险控制补丁”：对 short-cycle desk，更该先拆的是「cross-sectional momentum × BTC 波动/相关性状态缩放」这条可落地 raw alpha

- 时间：2026-04-16 14:58 UTC
- 类型：GitHub 仓库 + working paper 草稿
- 主题类型：raw alpha（含 regime/overlay）
- 基础 alpha：横截面相对动量（long winners / short losers）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / momentum / relative-value / regime / volatility / correlation / overlay / 1m / 3m / 5m / 15m / repo
- 证据类型：工程实证 + 论文草稿实证

## 1) 这次看了什么
看的是 2026 新仓库 `mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies`：核心脚本 `macro_state_test.py`、`coordination_overlay_test.py`，以及论文草稿 `main1.tex`（作者 Olorato MacDonald Makgolo, Cong Zhang）。

## 2) 一句话结论 + 怎么证明
- 一句话核心结论：**base alpha 不是“状态过滤”，而是标准的横截面动量；BTC 波动率+横截面相关性只是在高压 regime 把杠杆收回去，减少大回撤。**
- 一句话证明方式：**作者在 2015–2026 多币样本上先跑 baseline XSM，再做 regime-conditioned interaction 与 overlay 对照，比较 Sharpe / MaxDD / 因子暴露与稳健性。**

## 3) 核心发现（只保留对 desk 最有用的）
1. 草稿给出的 headline：baseline XSM 年化收益约 21.7%、Sharpe 0.44、MaxDD 约 -85.9%；regime-aware 后年化约 16.7%、Sharpe 0.51、MaxDD 约 -66.4%。
2. 机制上，crypto 横截面在压力期会“共振化”：PC1 解释约 66% 方差，且 PC1 与 BTC 同步性高（相关约 0.85）。这会压垮纯 ranking alpha 的分散化收益。
3. 在高波动状态，动量强度×高波动交互项为负（草稿给出约 -0.233, p<0.05），说明“同一套动量信号”跨状态并不等价。
4. 仓库不是只给结论：给了可复跑的 `build_strategy_returns`、`coordination overlay`、drawdown/成本敏感性导出路径，适合直接拆到我们研究流水线。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值（market-neutral 的 long-short）
- 基础 alpha：过去 K 窗口收益排序（cross-sectional momentum rank）
- regime：BTC 实现波动率分位 + 全市场平均相关性分位
- filter / veto：高压状态下降低 gross exposure；可加 dispersion gate（低分散期降权）
- risk / sizing / execution overlay：vol-target 缩放 + gross cap + 单资产权重上限 + 换手约束 + 成本门槛

## 4) 为什么和当前 1m/3m/5m/15m 直接相关
这套东西最值钱的地方不是“又一个动量”，而是它把 **raw alpha 与风控层严格拆开**：
- raw alpha：仍是可迁移到短周期的 cross-sectional momentum/rank；
- overlay：用 BTC 波动+相关性作为统一 throttle，不改信号定义，只改风险暴露。

这对我们 desk 的价值是：可以把同一个 alpha 内核在 `15m -> 5m -> 3m/1m` 逐级下探时，先用统一状态缩放减小回撤爆点，再看成本后是否存活。

## 5) 可复刻的最小实验（下一步怎么测）
研究假设：**短周期 XSM 的主要失效来自高共振压力期；加入状态缩放后，post-cost Sharpe/Calmar 改善，且极端回撤下降。**

最小实验切口（公开可得数据）：
- 资产：Binance USDⓈ-M majors（先 12–20 个高流动币）
- 周期：
  - Lane A: `15m`（180 天）
  - Lane B: `5m`（90 天）
  - Lane C: `3m/1m`（30–45 天，先验证成本生存）
- base alpha：`score_i(t)=zscore(ret_i, lookback=L)`；按分位做 long top / short bottom，美元中性
- overlay：
  - `sigma_btc(t)`：BTC rolling RV（从同频 bar 聚合）
  - `rho_bar(t)`：当期资产池平均相关性
  - `g(t)=clip(min(sigma_target/sigma_btc, f(rho_bar)), g_min, 1)`
- 执行：每 bar/每 3 bar 再平衡（减少换手）；加 hysteresis（排名变化小于阈值不换仓）
- 成本：taker 费 + 保守滑点（按成交额分层），先做 friction ladder

先看 2 个指标：
1. 成本后 Sharpe（主）
2. MaxDD / Calmar（辅）

## 6) 风险与保留意见
- 仓库样本混合日频与较长持有逻辑，直接下钻到 1m/3m 时，换手与冲击成本会急剧放大。
- CoinGecko/外部数据依赖在实时交易中可能有延迟；实盘应切到本地行情与内部状态计算。
- 如果相关性估计窗口太短，`g(t)` 会抖动，可能把 alpha 收益“过度风控”掉，需要平滑/滞后处理。

## 7) 来源
1. Makgolo, O. M., & Zhang, C. (2026). *Regime-Aware Exposure Scaling in Cross-Sectional Relative Momentum Cryptocurrency Strategies* (working paper draft, `main1.tex`).
   - Venue: Working paper / manuscript
   - DOI: N/A
   - Readable URL: https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies
   - Repo URL: https://github.com/mmakgolo/Regime-Aware-Exposure-Scaling-in-Cross-Sectional-Relative-Momentum-Cryptocurrency-Strategies

2. Jegadeesh, N., & Titman, S. (1993). *Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency*. Journal of Finance.
   - DOI: https://doi.org/10.1111/j.1540-6261.1993.tb04702.x
   - Readable URL: https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.1993.tb04702.x

3. Barroso, P., & Santa-Clara, P. (2015). *Momentum Has Its Moments*. Journal of Financial Economics.
   - DOI: https://doi.org/10.1016/j.jfineco.2014.11.010
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X14002323
