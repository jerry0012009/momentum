# 别把开盘放量都当趋势确认：`IVU < 0.476 + 高开盘量`，更像 breakout-short / Fib / EMA 的 shared continuation gate
- 时间：2026-03-18 22:29 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume/uncertainty/regime/filter/paper/crypto/15m
- 证据类型：论文证据
- 证据强度提示：**中等偏强**（有全文与明确实证；但原样本是中国股票 30m，不是 crypto 15m）

## 1. 这次看了什么
这次看的论文是 **Yang, He (2026)**：*Enhancing Intraday Momentum Prediction: The Role of Volume-Based Information Uncertainty in the Chinese Stock Market*（IJFS）。我重点不拿它当“再来一个方向信号”，而是抽出更适合我们 desk 的旁支：**用开盘量分布做 uncertainty gate，给已有信号加“是否值得做 continuation”的闸门**。

## 2. 核心结论
- **一句话核心结论**：同样是“开盘有动量”，只有在 `高开盘量 + 低 IVU（高不确定性）` 这个组合里，后续延续性才明显更强；这更像 shared regime gate，不像独立主信号。
- **一句话说明它怎么证明**：作者在 **CSI300、2018-07 到 2025-06、30 分钟分段**上，先用 threshold regression 找阈值，再用 logistic + XGBoost 做方向预测和交易回测。
- IVU 定义：`IVU_t = V_{t,1} / sum(V_{t,1..7})`（首段量占比）；阈值回归给出显著临界值 **0.476225（p < 0.001）**。
- 在 `高开盘量 + 低 IVU` 子样本中，logistic 方向准确率 **63.04%**；XGBoost OOS 准确率 **71.43%**。
- 子组对比里，`High V - Low IVU` 准确率 **0.7143**，显著高于全样本 **0.5373**（+32.9% 相对提升）。
- 论文回测（含交易成本假设）里，ML 策略总收益 **117.99%**、Sharpe **3.02**（7 年期）。

## 3. 为什么和当前项目有关
这轮和三条收口线是直接相关的：
- **V3 final-verdict / breakout-short follow-up**：break 后最怕追在噪声续段；`高开盘量 + 低 IVU` 可先当 continuation allow 条件，其他状态降仓或 veto。
- **Fibonacci confirmation / retest_hold**：回踩守住不是“碰线即真”；若处于低质量量分布状态，可把 hold 判定从“进场”降级为“观察”。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 原始触发先天易被 chop 吞噬，把 IVU 作为 shared gate 比继续炼参数更便宜。

## 4. 可复刻的最小实验
### 研究假设
在 crypto `15m`（必要时联动 `5m` 执行）中，给现有三条收口线叠加 `IVU gate`，能提升成本后期望并降低“触发后快速失效”比例。

### 一个可计算定义（crypto 版）
- 会话锚点先用 `00:00 UTC`（后续再做 `08:00/13:30 UTC` 稳健性）。
- 每个锚点后 8 根 15m：
  - `IVU = vol_bar1 / sum(vol_bar1..bar7)`
  - `open_vol_high = vol_bar1 > rolling_median(vol_bar1, 60d)`
- gate：`allow = open_vol_high & (IVU < q_IVU)`；首轮可同时对比 `q_IVU=0.476`（论文阈值移植）与资产内分位数（如 q40）。

### 最小回测切口
- 标的：`BTC/ETH/SOL` perpetual
- 周期：信号 15m，执行可用 5m next-bar open
- 样本：近 180~365 天
- 成本：`6/10/15 bps per side`
- 仅改一件事：**不改原 entry/exit，只叠 IVU allow/deny 与 1 档降仓规则**

### 最该先看 4 个指标
- `post_cost_expectancy`
- `failure_before_target`（触发后 N 根内反向失效率）
- `trade_count_retention`
- `positive_window_ratio`

## 5. 风险与保留意见
- 原论文是股票日内开收盘结构；crypto 24/7，session anchor 选择会明显影响 IVU 稳定性。
- `0.476225` 不一定可直接迁移；更现实是“论文阈值 + 资产内分位阈值”并行测试。
- 高准确率子组可能伴随样本变少，需防止“砍单换胜率”。
- 这条线定位应是 **regime gate / sizing overlay**，不是伪装成逐根 15m 主信号。

## 6. 来源
1. **Yang, D., & He, Q. (2026).** *Enhancing Intraday Momentum Prediction: The Role of Volume-Based Information Uncertainty in the Chinese Stock Market.* International Journal of Financial Studies.
   - DOI: https://doi.org/10.3390/ijfs14020047
   - Readable URL: https://www.mdpi.com/2227-7072/14/2/47
   - PDF URL: https://mdpi-res.com/d_attachment/ijfs/ijfs-14-00047/article_deploy/ijfs-14-00047.pdf?version=1771044487
   - Repo URL: N/A（论文未提供官方复现实验仓库）
2. **XGBoost reference implementation**
   - Repo: https://github.com/dmlc/xgboost

## 7. 下一步怎么测
先做一个 **2x2 gate A/B**：`有/无 IVU gate` × `有/无降仓 overlay`，其余交易规则完全冻结。若 `post_cost_expectancy` 与 `failure_before_target` 同时改善，且 `trade_count_retention` 不低于基线的 60%，再进入 OOS rolling；否则直接降级为 `parked filter`，不继续占主线预算。