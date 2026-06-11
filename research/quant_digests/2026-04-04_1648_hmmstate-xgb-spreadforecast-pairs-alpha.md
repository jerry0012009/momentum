# 别把这份 2025 stat-arb repo 只读成“cointegration 筛对脚本”：对 short-cycle desk，更该先测的是「HMM 状态 × spread 方向预测 × MVO 配对篮子」这条完整 raw alpha
- 时间：2026-04-04 16:48 UTC
- 类型：2025 GitHub repo source audit（`strategy.py` + `main.py` + `market_data_gateway.py` + `OMS.py` + `portfolio_tracker.py`）+ Binance USDⓈ-M 公共 `5m/15m` 最小可移植性快检
- 主题类型：raw alpha
- 基础 alpha：**对 cointegrated pair 来说，spread 的下一步方向在短窗里并非纯随机；可用 `HMM state + lagged spread technical features` 做一阶方向预测，再把 pair 级信号汇总成 market-neutral 组合，吃的是相对价差的可预测变动，而非单边币价方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/spread-forecast/hmm/xgboost/cointegration/adf/mvo/market-neutral/binance-perpetual/5m/15m/3m/1m/repo/public-data/cost/risk
- 证据类型：开源代码仓 + 公共行情最小实验

## 1) 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是“cointegration 本身”，而是“cointegrated spread 的短窗方向可预测性”。**

翻成人话：
- 传统 pairs 常见是 `spread 偏离大了就赌回归`；
- 这份 repo 的旁支更像：`先判 spread 下一步向上还是向下，再决定 long 哪条腿 / short 哪条腿`；
- 再叠 `MVO` 把多条 pair 信号合成组合层仓位。

这条线对我们当前 desk 的价值在于：它不是纯 filter，也不是 overlay，而是**可独立跑成完整策略**的 relative-value raw alpha（entry/exit/sizing/risk/cost 都能落地）。

---

## 2) 本轮主材料与为什么不重复
### 2.1 主材料（repo）
- **Author / Year / Title / Venue**：`timshao8` / 2025 / *Market-Microstructure-* / GitHub
- **Repo URL**：<https://github.com/timshao8/Market-Microstructure->
- **Readable URL**：<https://github.com/timshao8/Market-Microstructure->
- **仓库元数据**：创建 `2025-07-02`，最后 push `2025-07-03`

### 2.2 本轮聚焦的关键源码
- `strategy.py`：cointegration + ADF pair admission，`GaussianHMM + XGBRegressor` 做 spread 方向信号，`mvo()` 做组合权重
- `main.py`：策略驱动与下单流程（含明显执行缺陷）
- `market_data_gateway.py`：当前写死 `1d` 永续 K 线
- `OMS.py` / `portfolio_tracker.py`：权重转订单与持仓管理

### 2.3 为什么和最近 digest 不重复
最近我们有不少 `pairs z-score fade` / `cointegration shell`。这篇最值得 intake 的分歧点是：
1. **signal 层不是单纯 z-score 阈值，而是 spread 方向预测（HMM state + feature stack）**；
2. **组合层显式做了 MVO**，不是每个 pair 等权；
3. 代码里能直接抽出“从 pair alpha 到 portfolio alpha”的接口。

---

## 3) 代码级拆解：真正可抄的与必须修的

## 3.1 可抄的主链路
`strategy.py` 的链路是完整的：
1. `get_pairs()`：
   - 对全组合做 `coint(series1, series2)`；
   - `p < 0.05` 才进候选；
   - 再做 OLS beta + residual ADF（`p < 0.05`）二次过滤。
2. `generate_signal(spread)`：
   - 先拟合 `GaussianHMM` 得 state；
   - 构造 lag / MA / EMA / RSI / MACD 等 feature；
   - 用 `XGBRegressor` 预测下一步 spread；
   - `sign(predicted - last_actual)` 输出方向。
3. `mvo()`：
   - 对各 pair spread return 估均值与协方差；
   - `inv(Sigma) @ mu` 得 raw weights；
   - 以 L1 归一化得到组合权重。

这三步拼起来就是一条完整 raw-alpha 壳，不是“只会筛对”的半成品。

## 3.2 必须修的硬伤（不修不能实盘）
### A) 数据频率写死 1d
`market_data_gateway.py` 取的是 `interval="1d"`。对 short-cycle desk（1m/3m/5m/15m）必须改频率与窗口。

### B) 下单后立刻平仓
`main.py` 在 `weights_to_order(...)` 后直接 `close_positions(...)`，等于“刚开就平”。
这在研究/实盘里会把 alpha 全部变成手续费。

### C) 工程完整性不足
- `main.py` 里 `from Risk import RiskManager`，但仓库里没有对应文件；
- 有硬编码 API key 示例；
- 缺少 README 与可复现实验说明。

结论：
> **这不是可直接运行的 production repo，但它提供了有价值的“signal + portfolio” alpha 母板。**

---

## 4) 最小可移植性快检（Binance 公共 5m/15m）
我先不复刻 HMM/XGB 全链路（依赖与工程不完整），先测最核心可迁移假设：

> **同样 pair admission 思路下，短窗 spread 在极端偏离后是否存在可交易的回摆/修复口袋。**

### 4.1 数据与口径
- 数据源：Binance USDⓈ-M public klines（公开、免 key）
- 标的（repo 原始 10 币中可用者）：`BTC/ETH/BNB/XRP/SOL/ADA/DOGE/LTC/AVAX`
- `MATICUSDT` 现货口径检查显示已失活（见 4.2）
- 样本：最近 `1000 bars`
  - `5m`：`2026-04-01 05:24:59 UTC ~ 2026-04-04 16:39:59 UTC`
  - `15m`：`2026-03-25 06:59:59 UTC ~ 2026-04-04 16:44:59 UTC`
- pair 统计：每对 OLS beta 构 spread，rolling z-score；当 `|z| >= 1.5` 记为极端事件；
  统计未来窗口内“向均值方向移动”的 hit-rate
  - 5m 用 `12 bars`（约 1h）
  - 15m 用 `4 bars`（约 1h）

### 4.2 关键数据点（本轮）
1. **MATIC 失活证据**：`MATICUSDT` 最近 5 根 `15m` bar 最后时间停在 `2024-09-11 09:44:59 UTC`，且成交量均为 `0`。这说明 repo 原 universe 直接照抄会污染当下样本。  
2. **5m 口径（36 对）**：极端事件的 pair 中位回摆 hit-rate 约 **53.7%**；最强 pair `SOL-AVAX` hit-rate 约 **79.8%**。  
3. **15m 口径（36 对）**：中位 hit-rate 约 **51.9%**；最强 pair `XRP-DOGE` hit-rate 约 **64.2%**。

解释：
- 这不是“闭眼可印钞”的证据；
- 但它支持了一个现实结论：**pair spread edge 明显是分层/分组的，不是全市场均匀存在**。
- 这恰好支持 repo 的设计方向：要做 pair admission + 动态信号 + 组合层加权，而不是全对等权硬上。

### 4.3 产物路径
- `reports/artifacts/quant_digests/hmm_xgb_pairs_shell_transfer_20260404/summary.json`
- `reports/artifacts/quant_digests/hmm_xgb_pairs_shell_transfer_20260404/pair_reversion_probe_5m.csv`
- `reports/artifacts/quant_digests/hmm_xgb_pairs_shell_transfer_20260404/pair_reversion_probe_15m.csv`

---

## 5) 给 desk 的可落地版本（entry/exit/sizing/risk/cost）
下面给一版直接可做最小实验的策略壳（先 ML-lite，再上 HMM/XGB）：

### 5.1 Universe / Admission
1. 动态 universe：排除 stale/零成交合约（例如本轮 MATIC）。
2. 每日（或每 6h）重跑 pair admission：
   - `coint p < 0.05`
   - residual `ADF p < 0.05`
   - 最近 N 天最小成交额门槛。

### 5.2 Signal（先 ML-lite，再升级）
- **ML-lite baseline**：
  - spread zscore、Δspread、rolling vol、短中长斜率、跨币相关性漂移；
  - 逻辑回归 / 线性模型预测未来 `k` bar spread 方向。
- **升级版**（对齐 repo）
  - 加 HMM state 特征；
  - 替换为 XGBoost（或 lightgbm）。

### 5.3 Entry / Exit
- Entry：`|score| > threshold` 且 pair 在可交易白名单；
- 方向：预测 spread 上行 => long spread（long A short βB）；反之 short spread；
- Exit：
  1) 预测翻向；
  2) spread 回到中性带；
  3) time stop（例如 8~16 bars）；
  4) 硬止损（pair 级 max adverse）。

### 5.4 Sizing
- pair 层按 `confidence / realized vol` 缩放；
- 组合层用 `inv(Sigma)@mu` 或 risk-parity 近似；
- 单 pair 与单腿 notional 设 cap，防极端集中。

### 5.5 Risk / Cost
- 成本最少两档：
  - maker-taker 混合（乐观）
  - 全 taker（保守）
- 必做约束：
  - 每日 turnover cap
  - 单腿冲击成本估计
  - 相关性聚集上限
  - 交易时段黑名单（超低流动）。

---

## 6) 为什么这条线现在值得进素材池
1. **是 raw alpha，不是 filter 伪装**：可以独立开平仓并产生成交序列。  
2. **能服务我们现有 pairs 家族**：把“纯 z-score 触发”升级为“状态感知 + 方向预测 + 组合汇总”。  
3. **短周期友好**：公开数据可得、5m/15m 可快速出第一轮实证，不需要私有订单流起步。

---

## 7) 下一步怎么测（必须执行）
按优先级给三步，先快后慢：

### Step 1（今天可做）
把当前 pairs baseline 拆成 A/B：
- A: `z-score fade`
- B: `spread-direction score`（先 logistic）
统一成本与执行，比较：净收益、换手、持仓时长、尾部回撤。

### Step 2（1~2 天）
在 B 上加 `regime gate`：
- 用 HMM state（2-state 足够）只做“是否交易/降仓”，不直接决定方向；
- 看是否改善成本后 Sharpe 与回撤。

### Step 3（2~4 天）
再上 repo 同构升级：
- 用 XGBoost 替换线性方向模型；
- 组合层从等权切到 MVO/risk-parity；
- 跑 walk-forward（至少月度滚动）。

成功门槛建议：
- 成本后胜率或 hit-rate 不要求极高，但**净 Sharpe、回撤、容量**至少一项明显优于 z-score baseline；
- 若只在极少数 pair 有效，则转为“pair routing alpha”，不要硬做全市场普适版。

---

## 8) References / Sources
1. **timshao8. (2025). _Market-Microstructure-_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/timshao8/Market-Microstructure->  
   - Repo URL: <https://github.com/timshao8/Market-Microstructure->  
   - Source URLs:  
     - <https://raw.githubusercontent.com/timshao8/Market-Microstructure-/main/strategy.py>  
     - <https://raw.githubusercontent.com/timshao8/Market-Microstructure-/main/main.py>  
     - <https://raw.githubusercontent.com/timshao8/Market-Microstructure-/main/market_data_gateway.py>  
     - <https://raw.githubusercontent.com/timshao8/Market-Microstructure-/main/OMS.py>

2. **Engle, R. F., & Granger, C. W. J. (1987). _Co-integration and Error Correction: Representation, Estimation, and Testing_. Econometrica.**  
   - Venue: Econometrica, 55(2), 251–276  
   - DOI: <https://doi.org/10.2307/1913236>  
   - Readable URL: <https://www.jstor.org/stable/1913236>

3. **Rabiner, L. R. (1989). _A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition_. Proceedings of the IEEE.**  
   - Venue: Proceedings of the IEEE, 77(2), 257–286  
   - DOI: <https://doi.org/10.1109/5.18626>  
   - Readable URL: <https://ieeexplore.ieee.org/document/18626>

4. **Chen, T., & Guestrin, C. (2016). _XGBoost: A Scalable Tree Boosting System_. KDD.**  
   - Venue: Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining  
   - DOI: <https://doi.org/10.1145/2939672.2939785>  
   - Readable URL: <https://dl.acm.org/doi/10.1145/2939672.2939785>

5. **Avellaneda, M., & Lee, J.-H. (2010). _Statistical Arbitrage in the U.S. Equities Market_. Quantitative Finance.**  
   - Venue: Quantitative Finance, 10(7), 761–782  
   - DOI: <https://doi.org/10.1080/14697680903124632>  
   - Readable URL: <https://doi.org/10.1080/14697680903124632>

---

## 9) 一句话收口
**这份 2025 repo 真正值得 intake 的，不是“又一个 cointegration 框架”，而是它把 pairs raw alpha 往前推进了一步：从 `spread 偏离触发` 升级到 `状态感知的 spread 方向预测 + 组合层权重分配`；下一步该做的是先用 5m/15m 的 ML-lite 版验证净后优势，再决定是否上完整 HMM/XGB。**
