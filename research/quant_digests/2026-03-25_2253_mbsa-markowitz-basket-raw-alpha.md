# 别把 stat-arb 篮子管理只当组合层：这篇 2025 MBSA 论文更该先测的是「moving-band spread 的 top-N Markowitz 篮子」raw alpha
- 时间：2026-03-25 22:53 UTC
- 类型：2025 Journal of Asset Management 论文 + 2024 Optimization and Engineering 伴随方法论文 + 官方 repo + Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**若一组 spread / residual 组合本身围绕 rolling midpoint 来回摆动，那么 base alpha 仍是这些 moving-band stat-arb 的均值回归；2025 这篇文章新增的，不是另一个 overlay，而是“当同时有多条 raw alpha 在跑时，怎样用 cost-aware / risk-aware Markowitz 把它们装成一个可交易篮子”**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/mean-reversion/moving-band/markowitz/basket-construction/top-n/risk-budget/cost-aware/binance/perpetual/15m/5m/paper/repo
- 证据类型：全文论文证据 + 官方 repo + 本地公共数据快检

> 先回答 base alpha：**这不是单独的 risk overlay。base alpha 还是 spread / residual 偏离 rolling midpoint 后的回归。** 之所以这轮值得写，是因为 desk 最近已经补了很多 `pair selection / Hurst / dynamic factor / PCA residual`，但还缺一张更上层的卡：**当你已经有一批可交易 spread 时，不要默认 equal-weight 硬堆；应先问“哪些该进篮子、每条给多少权重、成本和风险约束后还剩多少边”**。

## 1. 这次看了什么
主线其实是两篇连着看的论文 + 一个官方代码库：

1. **Kasper Johansson, Thomas Schmelzer, Stephen Boyd (2025), _A Markowitz Approach to Managing a Dynamic Basket of Moving-Band Statistical Arbitrages_, Journal of Asset Management**
2. **Kasper Johansson, Thomas Schmelzer, Stephen Boyd (2024/2025), _Finding moving-band statistical arbitrages via convex–concave optimization_, Optimization and Engineering**
3. **官方 repo：`cvxgrp/cvxstatarb`**

一句话讲人话：
- 2024 那篇先回答“**什么样的组合可以算 moving-band stat-arb**”；
- 2025 这篇再回答“**如果你同时找到了很多条 stat-arb，怎么把它们装进一个真的能交易的 long-short 篮子**”。

对当前 desk 最相关的，不是美股背景本身，而是它把 relative-value raw alpha 拆成了两层：
- **alpha discovery**：找到会围绕移动中枢摆动的 spread；
- **alpha allocation**：在多条 spread 同时活跃时，用 cost / risk / size limit 决定谁上、上多少、什么时候自然退场。

这正好衔接我们最近的学习进展：
- 近期 intake 已经补了 `Hurst pairs / dynamic factor residual / stable pair selection / PCA residual / same-coin multi-quote`；
- 但这些大多还停在“**先找到 spread，再开仓**”；
- 这篇补的是下一层：**raw alpha 不只要会找，也要会装篮子**。

## 2. 核心结论
- **一句话核心结论：** 不要把多条 stat-arb 默认 equal-weight 拼盘；对于同时活跃的 moving-band spread，`alpha_t = μ_t - p_t` 本身就能进入一个 cost-aware / risk-aware Markowitz 问题，进而决定 top-N 配置与再平衡节奏。
- 2024 伴随方法论文把单条 MBSA 讲清楚了：
  - 组合价格：`p_t = s^T P_t`
  - rolling midpoint：`μ_t = (1/M) Σ p_τ`
  - alpha：`α_t = μ_t - p_t`
  - 也就是：**价格低于移动中枢就偏多，高于中枢就偏空**。
- 2025 主论文真正值钱的地方，是把多条 active MBSAs 记成 `S_t=[s^(1)...s^(K_t)]`，然后在每期求一个长短仓组合 `q_t`，最大化：
  - `alpha exposure`
  - 减去 `trading cost`
  - 减去 `shorting cost`
  - 同时满足 `cash-neutral`、`collateral`、`per-MBSA size cap`、`risk budget`。
- 这相当于把“spread 发现”和“spread 配资”彻底拆开：**先承认 raw alpha 是 spread 回归，再单独优化如何把多条 spread 放进组合。**

## 3. 3 个关键数据点
1. **论文实证不是 toy sample。** 2025 主论文用的是 **CRSP 15405 只股票、2010-01-04 到 2023-12-30、共 3282 个交易日**；每 **21 个交易日** 搜一次新 MBSA，每天做一次 Markowitz 再平衡。  
2. **绩效很硬。** 论文 Table 给出的组合层结果是：**年化收益 19%，年化波动 12%，Sharpe 1.61，最大回撤 15%**。  
3. **它不是靠 market beta 吃饭。** 论文还给了：**residual return 18%，beta 11%，information ratio 1.53**；也就是说，作者想要的不是“再来一个跟市场一起涨的 long-short 壳”，而是低相关 relative-value alpha。

## 4. 为什么和当前短周期 desk 有关
### 4.1 它服务的是哪类 raw alpha
- 分类：**relative-value / stat-arb / mean-reversion raw alpha**
- 不是：
  - 纯 risk overlay
  - 纯 portfolio cosmetics
  - 只解释不落地的组合理论

### 4.2 它补的是当前素材池里还缺的一环
最近几轮 raw alpha intake 已经能找到很多“可交易 spread”：
- Hurst anti-persistence
- dynamic factor residual
- PCA residual
- stable pair selection funnel
- volume-ranked lead-lag spread

但如果后续实盘真进入“同一时刻多条 spread 同时亮灯”，会立刻遇到几个现实问题：
1. 是否所有 signal 都该上？
2. equal-weight 会不会把相关腿重复堆满？
3. 成本、再平衡、资金占用如何限制？
4. 某条 stat-arb 老化后，怎么自然退场？

这篇就是直接回答这几个问题的，而且回答方式很 desk：**不是再造黑箱，而是把它写成一个透明的 convex / SOCP 组合问题。**

## 3.5 策略拆解（必填）
- 方向属性：market-neutral / relative-value / stat-arb
- 基础 alpha：单条 MBSA 的 `α_t = μ_t - p_t`，即 spread 相对 rolling midpoint 的回归
- entry：默认不是二元开关，而是让 `α_t` 连续进入仓位优化；实务里可叠加 `|z|` / top-N 门槛
- exit：
  - `α_t` 回落
  - spread 老化 / decommission
  - 风险预算或 size cap 逼仓位自然缩小
- sizing：通过 `q_t` 解一个 Markowitz 问题，而不是每条 spread 固定 equal-weight
- risk：论文用 `||Σ_t^{1/2} q|| <= σ c` 约束的是“组合偏离各自 midpoint 的波动风险”，不是只看普通资产收益协方差
- cost：目标函数里显式扣掉 `trading cost` 与 `shorting cost`
- decommission：单条 MBSA 活跃期后，size cap `ξ_t^(k)` 可线性降到 0，让组合自然淘汰旧 spread

## 5. 这篇论文最值得直接偷的 4 个细节
1. **把 alpha 定义在 stat-arb 自己的价格空间里。** 不是先预测资产收益，而是先构造 spread 价格 `p_t`，再用 `μ_t - p_t` 做 alpha。  
2. **risk 也定义在“偏离中枢”的空间里。** 论文不是直接把风险写成普通 return variance，而是估计 `(p_t-μ_t)` 的协方差，再约束 `q`。这点很适合 spread desk。  
3. **组合层显式现金中性。** 论文要求 `p_t^T q = 0`，避免“看起来是 stat-arb，实际上偷带市场 beta”。  
4. **老 spread 不是靠主观拍脑袋下架。** 论文让每条 MBSA 在生命周期后半段逐步缩到 0；这比 desk 上常见的“一刀切删掉”更平滑，也更利于控制换手。

## 6. 本地最小快检：把它翻成 Binance `15m` spread 篮子后，值不值得继续？
我做了一个**明确不 faithful，但很适合 desk first verdict** 的 proxy：
- 数据：Binance USDⓈ-M Futures 公共 `15m` K 线
- 样本：**2026-01-06 20:15 UTC ~ 2026-03-25 23:00 UTC**
- 标的：`BTC / ETH / BNB / SOL / XRP / ADA`
- spread：两两配对，`spread = logA - β logB`，`β` 用 rolling OLS
- alpha proxy：`(rolling midpoint - spread) / rolling std`
- 活跃集：每个 bar 只留 **|z|>1.8 且 <2.6 的 top-2 spread**
- 组合层：每 **16 根 15m bar（约 4h）** 再平衡一次，对比
  - **naive equal-weight top2**
  - **Markowitz-smoothed top2**（带持仓惩罚与单 spread cap）

### 6.1 关键结果
1. **管理层确实有增益，但不大。** 不计成本时：  
   - naive：**+8.31%**，Sharpe **2.37**  
   - Markowitz-smoothed：**+9.30%**，Sharpe **2.61**  
2. **2 bps 后差距开始有意义。**  
   - naive：**-1.28%**，Sharpe **-0.28**  
   - Markowitz-smoothed：**-0.21%**，Sharpe **+0.03**  
   这说明 basket 管理层至少能把边保住一点，不至于 equal-weight 一上成本就直接塌得更快。  
3. **但 4 bps 仍然过不去。**  
   - naive：**-10.02%**  
   - Markowitz-smoothed：**-8.89%**  
   也就是说，这条线当前更像 **15m spread discovery + 低频篮子再平衡框架**，还不是 `15m bar-close taker` 成熟策略。

### 6.2 这组快检该怎么读
- 好消息：**论文强调的“不要 equal-weight 硬堆”在 crypto transfer 上有点用。**
- 坏消息：**当前这版 proxy 的换手仍偏高，`4 bps` 下还活不下来。**
- 所以更诚实的 desk 定位是：
  - raw alpha 本体成立；
  - 篮子管理层有边际改善；
  - 但第一站应是 **15m 生成 spread 候选 + 1h/4h 再平衡 + 5m 执行切片**，不是直接 bar-bar 冲。

## 7. 这条线现在该怎么放进研究池
我的判断：**值得进池，而且优先级不低。**

原因不是它证明了一个新的 headline alpha，而是它把我们已经积累的一堆 raw alpha 候选，接上了“怎么真正装成一个篮子”的下一段工程骨架。对 desk 来说，这很关键：
- 之前的 intake 更像“找到 spread”；
- 这篇开始回答“多个 spread 同时活跃时，怎么避免互相打架、怎么做 cost-aware 筛选、怎么让老 signal 自然退场”。

## 8. 下一步怎么测
1. **别再用全 pair 暴力扫。** 先把已有 intake（Hurst、dynamic factor、PCA residual、same-coin quote spread）产出的候选 spread 喂给这个组合层。  
2. **把再平衡再放慢一档。** 重点测 `15m signal + 1h / 4h rebalance + 5m execution`，不要急着做 `15m bar-close taker`。  
3. **把 no-trade / decommission 写成显式实验。** 比较 `top-1 / top-2 / top-3`、线性退场窗口、持仓惩罚 λ，对 turnover 和净收益的影响。  
4. **补真实 perp friction ladder。** 至少分层测 `2 / 4 / 6 bps`、maker fill ratio、funding carry、深度容量；这条线非常容易“毛收益有、净收益没”。  
5. **做与 equal-weight 的 A/B 固化。** 后续凡是新 spread basket，都默认先对比：equal-weight、inverse-vol、Markowitz-smoothed 三种篮子层，不再只报 signal 本体。  
6. **若 15m/4h 能活，再下钻 5m。** `5m` 更像 execution 与 inventory slicing 层，而不是第一版 alpha 发现层。

## 9. 风险与保留意见
- 论文主实证是 **美股日频**，不是 crypto；当前本地结果只能算 desk transfer 审计。  
- 我这里的 proxy 没有 faithful 复刻 2024 论文里的 MBSA discovery，而是用 `rolling OLS beta spread + midpoint z-score` 近似。  
- 当前 active 比例仍偏高，说明候选 spread 的 admission 还不够苛刻；若不先压缩 turnover，成本仍会吞掉净值。  
- 所以它现在最诚实的标签应是：**raw alpha 篮子化骨架已成立，但短周期落地要靠更慢再平衡与更强成本治理。**

## 10. 来源
1. **Johansson, K., Schmelzer, T., & Boyd, S. (2025). _A Markowitz approach to managing a dynamic basket of moving-band statistical arbitrages_. Journal of Asset Management, 26(4), 377–385.**  
   - DOI: `10.1057/s41260-025-00405-3`  
   - Readable URL: `https://web.stanford.edu/~boyd/papers/portfolio_of_SAs.html`  
   - DOI URL: `https://doi.org/10.1057/s41260-025-00405-3`
2. **Johansson, K., Schmelzer, T., & Boyd, S. (2025). _Finding moving-band statistical arbitrages via convex–concave optimization_. Optimization and Engineering, 26, 1203–1224.**  
   - DOI: `10.1007/s11081-024-09933-0`  
   - Readable URL: `https://web.stanford.edu/~boyd/papers/cvx_ccv_stat_arb.html`  
   - DOI URL: `https://doi.org/10.1007/s11081-024-09933-0`
3. **Repo: `cvxgrp/cvxstatarb`**  
   - Repo URL: `https://github.com/cvxgrp/cvxstatarb`
4. **Binance Developers – USDⓈ-M Futures Kline/Candlestick Data**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 11. 本地产物
- `reports/artifacts/quant_digests/mbsa-markowitz-basket-probe_20260325_2253/summary.json`
- `reports/artifacts/quant_digests/mbsa-markowitz-basket-probe_20260325_2253/nav_curves.csv`
- `reports/artifacts/quant_digests/mbsa-markowitz-basket-probe_20260325_2253/asset_weights_markowitz.csv`
- `reports/artifacts/quant_digests/mbsa-markowitz-basket-probe_20260325_2253/README.md`
