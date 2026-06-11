# 别把 RL2 当黑箱神谕：这篇 2024 论文更适合先复现「cointegration spread raw alpha + dynamic sizing」完整策略骨架
- 时间：2026-03-24 14:24 UTC
- 类型：论文 + GitHub 复现仓库 + 本地最小快检
- 主题类型：raw alpha
- 基础 alpha：cointegration spread 均值回归（pairs stat-arb）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/dynamic-sizing/cost/1m/3m/5m/15m
- 证据类型：论文证据 + 工程复现仓库 + 本地最小快检

## 1. 这次看了什么
一句话先答：这篇东西的 **base alpha** 是“协整价差偏离后的均值回归”（不是 RL 本身）。本次选的是 Yang & Malik (2024) 的 RL pairs 论文，核心价值在于把一条可独立复现的 pairs raw alpha，直接扩成 `entry/exit/sizing/risk/cost` 的完整策略骨架；并用复现仓库和本地 1m/3m/5m/15m 快检看它在我们 desk 语境下是否可落地。

## 2. 核心结论
- 论文主线不是“神经网络预测涨跌”，而是传统 pairs（价差阈值开平）+ RL 决策层；因此可先把 raw alpha 单独落地，再决定要不要上 RL2 动态仓位。
- 在论文样本中，传统方法年化约 8.33%，RL1（只管时机）约 9.94%，RL2（时机+仓位）约 31.53%。
- 论文给了成本敏感性：0.01% 费率下累计收益约 Gatev 9.43%、RL1 9.88%、RL2 33.99%；到 0.05% 时 RL2 优势明显收敛（约 7.40%）。
- 配对不是拍脑袋：先做相关+协整筛选，文中最优对为 BTCEUR-BTCGBP（1m 下相关约 0.8758、协整统计约 0.5667）。
- 本地最小快检（`reports/artifacts/quant_digests/rl2_dynamic_scaling_probe_20260324/summary_by_tf.csv`）显示：静态仓位在净 bps/笔上更高（如 5m 约 49.96 bps/笔 vs 动态约 17.77），说明“动态仓位”更像风险预算层，不该伪装成 raw alpha 本体。

## 3. 为什么和当前项目有关
当前 desk 正在补“可独立复现、可直接落地”的 raw alpha 池，这篇正好是 `pairs / stat-arb / mean reversion` 路线的完整模板：
- raw alpha 明确（spread 回归）；
- 开平与阈值治理明确（OT/CT/lookback）；
- sizing 层可插拔（先静态，再 RL2/规则化动态）；
- 成本层有明确 fee ladder，可直接映射到 Binance/Bybit 的短周期实盘约束。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 市场中性 / 均值回归
- 基础 alpha：协整配对的 spread z-score 回归
- regime：仅在配对相关+协整稳定窗口内启用；失稳时停机
- filter / veto：最小流动性、最小价差优势（edge > 成本）、极端跳变 veto
- risk / sizing / execution overlay：静态 1x 仓位为基线；动态仓位（RL2 或规则版）按机会质量调节；统一加入手续费/滑点/最大持仓时长/止损

## 4. 可复刻的最小实验
- 研究假设：
  1) `5m/15m` 的 pairs spread 回归在全成本后仍有正净值；
  2) 动态仓位应主要提升“收益/回撤比”，不必然提升“每笔净 bps”。
- 一个可计算定义：
  - `z_t = (eps_t - mean(eps_{t-L:t})) / std(eps_{t-L:t})`，`eps_t` 来自滚动 OLS 残差；
  - 入场：`z_t > OT` 做空 spread，`z_t < -OT` 做多 spread；
  - 出场：`|z_t| < CT` 或触发 time-stop / hard-stop。
- 最小回测切口（资产 / 周期 / 样本）：
  - 资产：先 BTCUSDT-ETHUSDT（数据易得），再扩到更同质 quote 对；
  - 周期：`1m/3m/5m/15m`；
  - 样本：滚动训练+前向验证（例如按月 walk-forward）。
- 最该先看 1~2 个指标：
  - 指标 1：成本后 `net bps/trade`（含手续费+滑点）
  - 指标 2：`Calmar` 或 `return / maxDD`（验证动态仓位是否真在“用风险换效率”）

## 5. 风险与保留意见
- 论文窗口较短（2023Q4），样本外稳定性需要二次验证。
- RL2 结果对奖励函数和动作空间定义敏感，易出现“回测好看、上线退化”。
- 交易摩擦一抬高，优势会显著衰减；必须先过费率阶梯测试。
- 复现仓库含替代交易对（BTCUSDT/ETHUSDT）实现，不能直接等同论文原始市场。

## 6. 来源
1) Yang, H., & Malik, A. (2024). *Reinforcement Learning Pair Trading: A Dynamic Scaling Approach*. Journal of Risk and Financial Management, 17(12), 555.  
   - DOI: `10.3390/jrfm17120555`  
   - DOI URL: `https://doi.org/10.3390/jrfm17120555`  
   - Readable URL: `https://arxiv.org/abs/2407.16103`  
   - Full-text URL: `https://arxiv.org/html/2407.16103v2`

2) FHLiang221 (GitHub, 2025). *RL-Pairs-Trading-Replication*.  
   - Repo URL: `https://github.com/FHLiang221/RL-Pairs-Trading-Replication`  
   - Readable URL: `https://github.com/FHLiang221/RL-Pairs-Trading-Replication`

3) 本地最小快检（2026-03-24）  
   - Artifact: `reports/artifacts/quant_digests/rl2_dynamic_scaling_probe_20260324/summary_by_tf.csv`
