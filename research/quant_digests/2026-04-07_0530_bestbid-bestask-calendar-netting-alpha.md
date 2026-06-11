# 别把这份 2026 新 repo 只读成 options RV 工具：对 short-cycle desk，更该先测的是「bestBid > -bestAsk calendar-spread gap × shared-leg netting」这条 raw alpha
- 时间：2026-04-07 05:30 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：同一 BTC 期限结构在不同 venue / 合约路径上的**最优可成交 calendar spread**偶尔会出现 `bestBid(spread) > -bestAsk(spread)` 的可执行倒挂，随后通常向可成交中性区回归。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / calendar-spread / futures-basis / cross-venue / shared-leg-netting / btc / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次主看 2026 新仓库 **`mikehyland-quant/crypto-options-relative-value`**。它表面上像“期权相对价值工具箱”，但对我们 desk 更值钱的旁支其实不是 vol surface 本身，而是 README 明写的 **BTC Futures Tightest-Market Optimizer**：用双路径 Bellman-Ford 找任意 BTC futures spread 的最优可成交 bid / ask，并在 `bestBid[j] > -bestAsk[j]` 时标记可执行套利。这个读法比把它当“又一个期权研究框架”更适合当前 `1m/3m/5m/15m` 短周期素材池。

## 2. 核心结论
- 这份 repo 真正像 raw alpha 的部分，不是“预测方向”，而是**期限价差在不同执行路径上的可成交不一致**。
- 作者把 spread 存成上三角矩阵，并分别优化 bid / ask 路径；这点很关键，因为 short-cycle desk 最怕的不是“理论 mispricing”，而是**理论有边、实际下不出来**。
- README 里给了两个很值钱的工程信号：
  - 数据源覆盖 **Deribit / Bitfinex / OKX / KuCoin / Gemini / CME(IBKR)**；
  - 基准表里 **CME Crypto Calendar Spreads** 一栏给出 **Sharpe 4.0、Max Drawdown -0.7%**。这当然不是我们的已验证结论，但足够说明作者在认真围绕“期限价差”而不是泛泛说 RV。
- 对我们最可迁移的点，不是整套多资产库，而是这句判定：**只在 `bestBid > -bestAsk + hurdle` 时进场**，把手续费、滑点、资金占用、跨腿残差都先写进门槛。

## 3. 为什么和当前项目有关
这条线直接补的是 **relative value / stat-arb 原始素材池**，而且比“固定 z-score 配对”更贴交易现实：
- 它交易的是**期限结构错价**，不是单纯相关性回归；
- 它天然要求把 **entry / path / netting / fee stack / unwind** 一起写清楚；
- 后续还能平移到我们已经在跟的 `perp-perp / spot-perp / options-perp / funding-basis` 几条线，而不是只服务某一个单点形态。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：同一标的、相近到期的 calendar spread 在不同 venue / 合成路径上的可成交倒挂最终收敛
- regime：仅在高流动、盘口连续、跨腿同步性足够好时启用
- filter / veto：`edge_after_fee <= 0`、任一腿深度不足、到期过近、跨腿时间戳错位、单腿成交后另一腿无法对冲
- risk / sizing / execution overlay：按最差腿可成交量限仓；优先 shared-leg netting；严格 time-stop；异常 widening / API stale / margin jump 时强平或撤单

## 4. 可复刻的最小实验
- **研究假设**：在公开 crypto futures 数据里，若某个同标的同期限 bucket 的最优可成交 spread 满足 `bestBid > -bestAsk + cost_buffer`，随后 1~6 个 bar 内会显著向 0 收敛。
- **可计算定义**：
  1. 选 BTC 的近月 / 次近月 / perp；
  2. 对每个时点构造 `far-near` spread 的可成交 bid / ask；
  3. 用 repo 这类图搜索思想求 `bestBid_path` 与 `bestAsk_path`；
  4. 定义 `edge = bestBid_path + bestAsk_path - fee_buffer - slippage_buffer`；仅 `edge > 0` 触发。
- **最小回测切口**：
  - 资产：BTC
  - venue：先做 **Deribit + OKX + Binance** 公共合约行情；
  - 周期：先存成 `1m` 盘口快照，再聚合看 `1m / 3m / 5m / 15m`
  - 样本：近 60~90 天
- **entry / exit / sizing / risk / cost**：
  - entry：`edge > 0` 且最差腿深度通过；
  - exit：`edge` 回到 `<= 25%` 初始值、或 `3~6` bar time-stop、或任一腿失去对冲；
  - sizing：按最小腿 notional 和保证金占用定仓；
  - risk：单次机会不超过组合风险预算，单腿 fail 立即 kill；
  - cost：先看 maker/taker 两档，再加跨腿滑点。
- **先看 2 个指标**：`post-cost edge capture ratio`、`time-to-close / stale-spread rate`。

## 5. 风险与保留意见
- 这类机会最容易被**撮合延迟、时间戳不同步、腿间部分成交**吃掉，纸面 edge 往往比真实 edge 好看。
- README 里的 Sharpe / DD 只是作者自报，不是我们独立复核后的结果，不能直接当 production 证据。
- 若第一轮只能在极少数时刻触发，说明它更像“稀疏 event alpha”，不一定适合重仓常开；但仍值得进研究池，因为它是真正可写成完整策略的 RV 原始 alpha。
- CME / IBKR 分支不适合第一轮；首轮应故意降级到**纯公开 crypto venue**，先验证这条“可成交倒挂是否真会收敛”。

## 6. 来源
1. **Mike Hyland (2026). _crypto-options-relative-value_. GitHub repo.**
   - Repo URL: `https://github.com/mikehyland-quant/crypto-options-relative-value`
   - Readable URL: `https://github.com/mikehyland-quant/crypto-options-relative-value/blob/main/README.md`
   - 关键信息：repo 创建于 `2026-02-24`，README 明写 `BTC Futures Tightest-Market Optimizer`、`bestBid[j] > -bestAsk[j]` 判定、以及 `Deribit / Bitfinex / OKX / KuCoin / Gemini / CME` 数据源覆盖。
2. **Deribit API Documentation**
   - URL: `https://docs.deribit.com/`
3. **Binance Futures API Docs**
   - URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api`
4. **OKX API Docs**
   - URL: `https://www.okx.com/docs-v5/en/`
