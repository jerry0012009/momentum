# 别把 15m 风控只写成“入场前 veto”：`equity drawdown throttle + recovery hysteresis` 更像三条收口线共用的 live-safety overlay
- 时间：2026-03-23 04:22 UTC
- 类型：论文 + GitHub 仓库
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / equity-drawdown / recovery-hysteresis / risk-overlay / position-management / crypto / 5m / 15m
- 证据类型：论文证据 + 工程实现证据

## 1. 这次看了什么
这次不再盯“新入场信号”，而是看一个更适合 desk 当前阶段的旁支：**权益曲线回撤触发的仓位降档 + 恢复滞后机制**。来源是 2026 arXiv 论文 `AdaptiveTrend`（给了回撤控制与稳健性结果）和一个近期开源实现仓库 `xzjh/crypto-daytrading`（给了可直接抄的状态机参数）。

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m 三条收口线来说，最便宜、最可复现、最不改原信号语义的增强，不是再加一个确认指标，而是加一层“权益曲线回撤降档 + 恢复滞后”的仓位覆盖层。  
- **一句话证明方式：** `AdaptiveTrend` 在文内把“动态止损/风险控制”做了模块化比较，并报告该类模块对 Sharpe 与回撤有显著贡献；仓库代码把它落实成明确阈值状态机（`dd>12% -> 仓位降到 25%`，`回到峰值 95% -> 恢复`），可直接落地复测。
- 来自论文/仓库的可复用数字（用于最小实验锚点）：
  1) 论文 OOS（2022–2024）报告：Sharpe `2.41`，MaxDD `-12.7%`；
  2) 文内 ablation 描述：动态风险退出/保护模块可带来明显 Sharpe 抬升与回撤压缩（文中给到约 `+0.73 Sharpe`、`-9.7pp MDD` 量级）；
  3) 工程参数原型：`dd_reduce=0.12`、`reduce_size=0.25`、`recover_to_peak=0.95`（见 `strategies/robust.py` / `eth.py`）。

## 3. 为什么和当前项目有关
它直接服务三条收口线，而且**不要求你先统一 entry 逻辑**：
- `V3 final-verdict / breakout-short follow-up`：当 follow-up 连续受挫时，先自动降档仓位，避免把 path 判错放大成资金曲线断层；
- `Fibonacci confirmation / retest_hold`：回踩确认本来就会遇到“慢磨损”场景，权益降档层比继续堆形态过滤更稳；
- `EMA / PSAR raw alpha focus`：raw 触发仍可能在震荡期反复被成本吃掉，权益层 throttle 可先救回撤，再决定要不要继续改信号。

## 3.5 策略拆解（必填）
- 方向属性：不改变方向判断（可挂在顺势/逆势/多空任意主信号上）
- 基础 alpha：沿用各线既有 alpha（breakout / retest / EMA-PSAR）
- regime：权益曲线自身状态（peak-to-trough drawdown）
- filter / veto：无（不是入场 veto）
- risk / sizing / execution overlay：`DD 触发降仓 -> 恢复阈值再加仓` 的两态/三态状态机（含 hysteresis）

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：在不改 entry/exit 信号的前提下，加“权益回撤降档 + 恢复滞后”可显著压低 MDD，且对收益伤害小于直接砍交易。  

**最小切口（先跑一晚）**
- 资产：BTC / ETH / SOL perpetual
- 周期：15m（可补 5m）
- 样本：近 180 天
- 成本：沿用 desk 现有 friction（6/10/15 bps 三档）

**A/B 设计（每条收口线都跑）**
- A：原策略（baseline）
- B：加 overlay：
  - 当 `equity_dd_from_peak > d`（`d ∈ {8%,10%,12%}`） -> `gross_size *= s`（`s ∈ {0.25,0.5}`）
  - 当 `equity >= 0.95~0.98 * peak_equity` 才恢复正常仓位（hysteresis）

**优先看 4 个指标**
1. `max_drawdown`（第一优先）
2. `calmar`
3. `post_cost_return`
4. `time_in_reduced_mode`（降档占比，防止“长期半死不活”）

**保留门槛（简版）**
- 若 B 相比 A：`MDD 至少改善 15%`，且 `post_cost_return 回撤不超过 10%`，则进入三线共享 overlay 候选池。

## 5. 风险与保留意见
- 这是风险覆盖层，不是 alpha；不能拿它掩盖坏信号。
- 路径依赖强：一次大回撤后可能“恢复过慢”，牛市反弹段会落后。
- 阈值过紧会频繁切档，阈值过松则保护不足；必须做参数平原检查，避免只挑单点最优。

## 6. 来源
1. Bui, D., & Nguyen, T. (2026). *Systematic Trend-Following with Adaptive Portfolio Construction: Enhancing Risk-Adjusted Alpha in Cryptocurrency Markets*. arXiv preprint.
   - DOI: 未见正式 DOI（arXiv 预印本）
   - Readable URL: https://arxiv.org/abs/2602.11708v1
   - PDF URL: https://arxiv.org/pdf/2602.11708v1
   - Repo URL: 文中未给官方实现仓库
2. xzjh (2026). *crypto-daytrading* (GitHub repository).
   - Repo URL: https://github.com/xzjh/crypto-daytrading
   - 关键实现：
     - https://raw.githubusercontent.com/xzjh/crypto-daytrading/main/strategies/robust.py
     - https://raw.githubusercontent.com/xzjh/crypto-daytrading/main/strategies/eth.py
     - https://raw.githubusercontent.com/xzjh/crypto-daytrading/main/core/config.py
   - 仓库描述：Adaptive trend-following system for BTC/ETH with backtesting and walk-forward validation
