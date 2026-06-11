# 别把 FPCA 只当预测课题：这篇 2025 论文可先落地成 `15m→5m` 的短周期方向性 raw alpha 骨架
- 时间：2026-03-24 08:40 UTC
- 类型：近 5 年论文（全文）
- 主题类型：raw alpha
- 基础 alpha：用 rolling-FPCA 预测下一时点收益符号（sign），按预测方向做短持有动量/反转切换交易
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（交易规则需工程补全）
- 主题标签：raw-alpha/trend/momentum/intraday/functional-pca/rolling-forecast/sign-prediction/btc/15m/5m/1m/3m/cost
- 证据类型：论文证据（含全文表格结果）

## 1) 先回答：这篇东西的 base alpha 是什么？
**base alpha = 短周期下一段收益“方向可预测”（sign predictability）本身。**  
不是单纯 filter；它可以直接变成 `long/short` 交易决策，是可独立复现的 raw alpha 候选。

## 2) 这篇论文最值钱的结论（人话版）
- 一句话核心结论：**把日内收益看成“函数”再做 rolling-FPCA，比传统离散模型更容易在固定时点上拿到更好的方向预测与更稳的区间估计。**
- 一句话证明方式：作者在 BTC 的 `15m` 与 `1h` 数据上做 out-of-sample 比较（ARMA/VAR/ML 基线），给出 RMSE、Sign 命中率、区间评分与覆盖率。
- 最值得复用点：**rolling-FPCA 的“部分重叠函数 → 下一段收益”映射**（k 步前移、在线更新）天然适配 24/7 crypto。

关键数据点（论文原文）：
1. **15m 一天函数预测（Table 1）**：AR-GARCH-FPCA 的 Sign = **47.9%**，ARMA-FPCA 为 **46.7%**；区间分数 `Sω` **0.607 vs 1.374**（越低越好）。  
2. **1h rolling-FPCA（Table 4）**：SVM 回归版本 RMSE **0.0321**（最佳误差）；Ridge 版本 Sign **62.5%**（最佳方向）。作者引用基线 RW：RMSE **0.0363**、Sign **50.24%**。  
3. **预测时距约束（Section 4.3）**：随着 horizon 增加，解释力下降；`R² > 0.5` 大约只维持到 **k≈10 小时**，提示“短持有优先”。

## 3) 为什么和当前 desk 直接相关
- 当前我们在补 raw alpha 素材池，这篇提供的是**可直接下单的方向性 alpha**，不是纯解释。  
- 论文原生支持 `15m`，与我们默认周期重合；扩展到 `5m` 只需把日内函数分辨率提高并重做主成分。  
- 它与我们已有 mean-reversion / carry / pairs 线互补：可作为**方向 sleeve**，再由成本/流动性 gate 控制是否启用。

## 3.5) 策略拆解（必填）
- 方向属性：短周期方向性（trend/momentum 为主，可配短窗反转 veto）
- 基础 alpha：rolling-FPCA 预测下一 bar（或下一小段）收益符号
- regime：在波动聚集且函数结构稳定阶段更有效（论文通过异方差建模提升区间质量）
- filter / veto：
  - 仅在 `|pred_mean| > θ` 且预测区间不跨 0 时开仓
  - 点差/冲击成本超过阈值时 veto
- risk / sizing / execution overlay：
  - `size ∝ confidence`（可用 |pred_mean|/pred_std）
  - 单笔与组合目标波动约束
  - `1-bar` 固定持有 + 反向信号提前平仓
  - 成本按 maker/taker + spread + impact 三段扣减

## 4) 可复刻的最小实验（先 15m，再 5m）
**研究假设**：rolling-FPCA 对下一 bar 方向有稳定信息，且在成本后仍有正期望分层。

**最小回测切口**：
- 资产：BTCUSDT perp（Binance）
- 周期：先 `15m`（原论文同频），再下钻 `5m`
- 样本：近 12 个月，滚动训练窗 180~250 天

**信号定义（可执行）**：
1. 构造“日内函数”：
   - 15m：每天 96 点；5m：每天 288 点
2. rolling-FPCA + Ridge/SVM 回归得到下一 bar `pred_return`
3. 交易规则：
   - Long：`pred_return > q70`；Short：`pred_return < q30`
   - Exit：下一 bar 强平（或信号翻转）
4. 成本口径：
   - 先跑 `4/6/8 bps` 梯度

**先看 2 个指标**：
- 成本后 `net pnl / trade` 与 hit-rate（按信号分位分层）
- turnover 与容量（参与率约束后是否仍为正）

## 5) 风险与保留意见
- 论文核心贡献偏预测框架，非完整交易系统；交易收益需我们自己补齐执行层。  
- 文中最好 sign 指标出现在 `1h` rolling 场景，迁移到 `15m/5m` 可能衰减。  
- 高分辨率（尤其 1m/3m）维度暴涨，FPCA 稳定性与实时性会成为工程瓶颈。  
- 若只看 sign 命中不看成本/冲击，容易产生“可预测但不可交易”的假阳性。

## 6) 下一步怎么测（明确动作）
1. 先做 `15m` reproducer：复刻 rolling-FPCA + Ridge，拿到基线命中率与成本后 PnL。  
2. 做 `5m` 同构迁移：只改函数分辨率与主成分截断（CPV 85% 起步），看边际是否下降。  
3. 做 `confidence 分桶`：仅交易 top/bottom 分位，检验“强信号是否覆盖成本”。  
4. 与现有 raw alpha 组合：把 FPCA 作为方向 sleeve，和 carry/mean-reversion 做风险平衡。

## 7) 来源
1. **Jasiak, J., & Zhong, C. (2025). _Intraday Functional PCA Forecasting of Cryptocurrency Returns_. arXiv (econ.EM).**  
   - DOI: `10.48550/arXiv.2505.20508`  
   - Readable URL: https://arxiv.org/abs/2505.20508  
   - PDF URL: https://arxiv.org/pdf/2505.20508  
   - Repo URL: 未公开（论文未提供官方代码仓库）
2. **Aue, A., Norinho, D. D., & Hörmann, S. (2015). _On the Prediction of Stationary Functional Time Series_. JASA.**（论文对照基线）
3. **Gradojevic, N., Kukolj, D., Adcock, R., & Djakovic, V. (2023). _Forecasting Bitcoin with Technical Analysis: A not-so-random forest?_. International Journal of Forecasting.**（论文对照基线）
