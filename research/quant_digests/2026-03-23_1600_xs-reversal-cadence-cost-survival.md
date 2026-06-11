# 别把横截面反转写成“调个 H 就行”：这份 2026 新仓库更值钱的是 `signal × 调仓频率 × 成本` 生存线
- 时间：2026-03-23 16:00 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年方法论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：cross-sectional short-horizon reversal（做多短窗输家、做空短窗赢家）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/reversal/mean-reversion/relative-value/rebalance-cadence/turnover/cost/liquidity-filter/perp/crypto/5m/15m
- 证据类型：工程证据 + 论文证据 + 本地快检（可复现）

## 1. 这次看了什么
先回答 base alpha：**这篇东西的基础 alpha 是横截面短周期反转（loser-minus-winner）**，不是 filter/overlay。

这次主看 **Jamestilfords (2026)** 的仓库 *statarb-crypto*。它把“横截面 momentum vs reversal”放在同一框架里，用 4H 币圈数据对比，并把 `entry/portfolio/execution/cost` 写成可直接复现的策略骨架。对我们 desk 最有用的点不是“某个最优 H”，而是：**同一条 raw alpha 在不同调仓节奏和成本下会不会还活着**。

## 2. 核心结论
- **一句话核心结论：** 这条 raw alpha 不是“有信号就能做”，而是必须先过 `调仓频率 × 成本` 生存线；频率太快时，反转 alpha 会被换手成本直接吃掉。  
- **一句话证明方式：** 仓库公开了参数扫面与成本压力测试；我再把它压到 Binance perp 15m 做最小快检，直接看 gross/net 与 turnover 的关系。
- 仓库 README 的关键数字（4H 框架）很直白：`H=3` 反转在 `20 bps` 下可到 **Sharpe 3.596 / CAGR 2.062**，但到 `40 bps` 近乎归零（Sharpe 0.159），`60 bps` 变成明显负值（Sharpe -2.910）。
- 本地 15m 快检（8 个主流 perp，`H∈{4,8,12,16}`，调仓间隔 `2/4/8` bars，成本口径 `6 bps`）：**最好的组合也没活下来**。最佳是 `H=16, rebalance=8, liq_filter=True`，`gross ≈ -0.03 bps/bar`、`net ≈ -0.88 bps/bar`、Sharpe `-11.74`。
- 快调仓最差：`H=4, rebalance=2, liq_filter=False` 时，虽然 `gross ≈ +0.29 bps/bar`，但因 `AvgTurnover ≈ 0.547`，`net ≈ -3.00 bps/bar`，说明“有点毛利 ≠ 可交易”。

## 3. 为什么和当前项目直接相关
- 它是 **可独立复现的 raw alpha**，不依赖 breakout/retest 主线。
- 它天然是完整策略：
  - entry：按短窗累计收益做横截面排序
  - exit：下一调仓点换仓
  - sizing：top/bottom 分位等权多空
  - risk：最小可交易资产数 + liquidity mask
  - cost：turnover-based 成本
- 对 `1m/3m/5m/15m` 研发特别关键：这条线明确告诉我们，先验重点应放在 **节奏与成本生存**，而不是先堆更多信号变体。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回归
- 基础 alpha：短窗赢家-输家存在下一窗反向回归
- regime：更适合横截面离散度高但可交易性尚可的时段
- filter / veto：可交易资产数不足、流动性过薄、成本阈值超限时停机
- risk / sizing / execution overlay：分位多空等权、降低调仓频率、成交额分层、成本前置闸门

## 4. 可复刻的最小实验（下一步怎么测）
- **研究假设：** 15m 反转并非完全无效，但只有在“低换手 + 低成本 + 流动性筛选”联合约束下才可能转正。  
- **最小定义：**
  - universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK`（先做主流下限）
  - signal：`score_t = -sum(r_{t-H+1...t})`
  - portfolio：每次做 `top/bottom 25%` 多空，美元中性
  - cadence：调仓间隔先测 `{8,12,16}` bars（15m）
  - cost：至少三档 `4/6/8 bps`（turnover-based）
- **下一步先看 4 个指标：** `post-cost bps/bar`、`AvgTurnover`、`净胜率（按日）`、`成本 break-even 曲线`。
- **下钻顺序：** 先让 15m 出现可存活 pocket，再下钻 5m/3m；若 15m 都不过成本门，默认不进入 1m。

## 5. 风险与保留意见
- 仓库原始结果来自其样本与交易口径，不能直接外推到我们交易成本与成交约束。
- 本地快检目前是“主流币 + 简化成交成本”口径，更像 first-fail 证据，不是最终否决。
- 这条 raw alpha 很容易受样本窗与成交假设影响，必须固定数据切片和成本口径再做对比。

## 6. 来源
1. **Jamestilfords. (2026). _statarb-crypto: Cross-sectional momentum vs reversal stat-arb on liquid Binance USDT pairs (4H), with transaction cost and robustness tests_. GitHub Repository.**  
   - Authors / Year / Title / Venue: Jamestilfords / 2026 / statarb-crypto / GitHub Repository  
   - DOI: N/A  
   - Readable URL: https://github.com/Jamestilfords/statarb-crypto  
   - Repo URL: https://github.com/Jamestilfords/statarb-crypto
2. **Yu, J.-R., Wei, C.-H., Lai, C.-J., & Lee, W.-Y. (2023). _Extending the Omega model with momentum and reversal strategies to intraday trading_. PLOS ONE, 18(9), e0291119.**  
   - DOI: `10.1371/journal.pone.0291119`  
   - Readable URL: https://doi.org/10.1371/journal.pone.0291119
3. **Heston, S. L., Korajczyk, R. A., & Sadka, R. (2010). _Intraday Patterns in the Cross-Section of Stock Returns_. The Journal of Finance, 65(4), 1369-1407.**  
   - DOI: `10.1111/j.1540-6261.2010.01564.x`  
   - Readable URL: https://doi.org/10.1111/j.1540-6261.2010.01564.x

## 7. 本地复现产物
- `reports/artifacts/quant_digests/cs_reversal_repo_proxy_20260323/summary.csv`
