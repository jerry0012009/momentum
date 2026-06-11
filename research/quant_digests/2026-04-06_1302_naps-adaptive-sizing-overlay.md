# 别把 NAPS 读成又一个通用 ML 包装：对 short-cycle desk，更值得先测的是「raw-alpha score × uncertainty × risk-state adaptive sizing」

- 主题类型：overlay
- 基础 alpha：**无独立 raw alpha；这是把已有 raw alpha 的方向/强度信号，和不确定性、组合风险状态一起映射成动态仓位的 sizing overlay，服务 trend / breakout / mean reversion / cross-sectional / stat-arb 等现有 alpha**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-06 13:02 UTC
- 类型：2026 Zenodo 预印本元数据 + 2026 GitHub repo source audit（`README.md` + `configs/default.yaml` + `naps/training/objective.py` + `naps/data/features.py` + `naps/baselines/risk_parity.py`）
- 主题标签：overlay / position-sizing / risk-management / uncertainty / transformer / cross-attention / drawdown-penalty / turnover-penalty / risk-parity / kelly / crypto / 1m / 3m / 5m / 15m / repo / paper / public-code
- 证据类型：repo-based + paper-metadata-based

## 1. 为什么这轮不是继续补 raw alpha，而是补一个 sizing overlay？

先说结论：**这轮不是因为找不到 raw alpha，而是因为新 intake 里更干净、且不和近几天 digest 重复的 raw alpha 候选很少；反过来，这个 2026 新 repo 给的是一个能直接服务整池 raw alpha 的“仓位层组件”**。

这件事对当前 desk 有现实价值：

- raw alpha 池已经连续补了很多：`trend / breakout / XS / relative value / funding / options / microstructure`
- 但“**同一条 alpha 在什么状态下该上 0.25x / 0.5x / 1.0x，什么时候该直接缩到 0**”这层，还是更多靠人工规则和简单 inverse-vol
- 如果这层能做成统一可学习模块，它对素材池的复用率，反而高于再补一条边际相近的新 entry rule

所以这篇 note 的定位必须老实：

> **它不是新 raw alpha，而是一个可以挂在现有 raw alpha 上的 adaptive sizing overlay。**

## 2. 先回答任务里那句关键话：base alpha 是什么？

这篇东西的 **base alpha 说不成独立 raw alpha**。

更准确地说：

> **它假设你已经有一个方向/强度信号，然后学习“这次该下多大”。**

所以它不能冒充 `raw alpha`；更诚实的定位是：

- `overlay`
- `position sizing / risk management layer`
- `shared component`

但它依然值得进研究池，因为它满足另外一档高优先级条件：

> **它能同时服务至少 2 类以上 raw alpha，并且能直接落地到已有 1m/3m/5m/15m 策略骨架里。**

## 3. 这次看了什么

### 3.1 论文 / 预印本元数据
- **Authors**: 仓库与 README 未明确作者全名；Zenodo 条目标题为 *NAPS: Neural Adaptive Position Sizing for Risk-Aware Algorithmic Trading*
- **Year**: 2026
- **Title**: *NAPS: Neural Adaptive Position Sizing for Risk-Aware Algorithmic Trading*
- **Venue**: Zenodo 预印本；`README.md` 自述为“NeurIPS 2026”，当前未单独核验正式会议收录页
- **DOI**: <https://doi.org/10.5281/zenodo.19425642>
- **Readable URL**: <https://doi.org/10.5281/zenodo.19425642>

### 3.2 代码仓库
- **Repo URL**: <https://github.com/Thanh-Van-2001/NAPS-Neural-Adaptive-Position-Sizing>
- **Repo created_at**: 2026-04-03
- **Repo pushed_at**: 2026-04-03

### 3.3 这份 repo 真正在做什么
不是去学“涨跌方向”，而是学：

```text
已有信号 + 信号不确定性 + 风险状态 + 市场上下文
    -> bet fraction f_t in [0, f_max]
```

仓位不是二选一，而是连续值；默认 crypto `f_max = 0.25`。

## 4. 源码里最值得 desk 抄走的 5 个部件

## 4.1 输出不是方向，而是有上限的 bet fraction
`README.md` 与 `configs/default.yaml` 一致写明：

- output: `f_t in [0, f_max]`
- crypto `f_max = 0.25`
- equities `f_max = 0.40`
- forex `f_max = 0.30`

这点很关键，因为它天然适合挂在我们现有 raw alpha 后面：

- alpha 决定方向与是否触发
- NAPS 风格模块决定 `0 ~ 25%` 的下注强度

对 short-cycle desk 来说，这比直接让模型输出 long/short 更实用，也更容易审计。

## 4.2 输入不是只看价格，还显式吃三类信息
根据 `README.md` 与 `naps/data/features.py`，输入被拆成三组：

### A. 市场特征（20 维）
- 5 个原始 OHLCV
- 15 个技术特征：`SMA20 / SMA50 / EMA12 / EMA26 / MACD / Bollinger width / ATR14 / OBV / Stoch / Williams %R / CCI20 / ADX14 / RSI14`

### B. regime features（3 维）
- `20-day realized volatility`
- `60-day rolling correlation with market index`
- `20-day trend strength`

### C. portfolio state（5 维）
- current drawdown
- cumulative P&L
- days since peak
- current aggregate exposure
- recent trade-outcome serial correlation

翻成人话就是：

> **它不是只看“市场像不像要涨”，而是同时看“这信号稳不稳、你最近顺不顺、当前组合有没有已经太满”。**

这非常适合我们现在的多 alpha 素材池。

## 4.3 它把“不确定性”单独留了一个通道，而不是塞进 feature soup
`README.md` 明写：

- signal 输入是 `(direction + magnitude)`
- uncertainty 输入来自 `MC-dropout`
- 再和 risk state 通过 `cross-attention` 融合

这件事对 desk 的现实意义比论文味更重：

> **同样是 +1 的方向信号，“确定的 +1”和“很虚的 +1”不该下同样仓位。**

这是很多现有策略骨架里缺失的一层。

如果不想上完整神经网络，最小也可以先抄一个弱版本：

```text
size = raw_score_strength × confidence_discount × risk_budget_multiplier
```

其中 `confidence_discount` 可以先用：

- 信号 ensemble 分歧
- rolling hit-rate
- bootstrap CI 宽度
- regime mismatch 惩罚

## 4.4 训练目标不是只拼 Sharpe，而是把 drawdown 和 turnover 一起写进 loss
`naps/training/objective.py` 给出的组合 loss 是：

```text
L = -Sharpe + lambda1 * drawdown_penalty + lambda2 * turnover_penalty
```

默认参数：

- `tau = 0.15`：最大回撤阈值 15%
- `lambda1 = 5.0`：回撤惩罚
- `lambda2 = 1.0`：换手惩罚
- `cost_bps = 10`：单边 10 bps
- `W = 252`

这比“先预测，再在回测里顺手调仓位”更像真正可部署的方法，因为它直接把现实里最痛的两件事写进目标：

- 回撤别太深
- 仓位别抖得太厉害

对于 1m/3m/5m/15m desk，我反而觉得 **turnover penalty** 比它的 transformer 壳还值钱。

## 4.5 repo 给出的 crypto 结果，提升主要来自“更稳的 sizing”，不是更神的 signal
`README.md` 的 Table 2 摘要写的是：

- **Crypto Sharpe**：`Risk Parity 0.74 -> NAPS 0.91`
- **Avg. MDD**：`16.8% -> 11.6%`
- 相对 best classical baseline：**Sharpe +23%**、**Max Drawdown -31%**

这里最重要的不是绝对值，而是改善方向：

> **它不是靠更准的方向预测赢，而是靠更好的仓位分配把同样的信号榨得更稳。**

这正符合它作为 overlay 的定位。

## 5. 这东西和 `1m / 3m / 5m / 15m` 的关系是什么？

### 5.1 可以直接服务哪些 raw alpha
至少可以接这几类：

1. **trend / breakout / continuation**
   - strong trend + low uncertainty + low portfolio DD -> 放大 size
   - same signal but choppy/high-vol/high-DD -> 缩小 size

2. **mean reversion / stat-arb / pairs**
   - spread 触发一样，但在 high-vol / high-correlation-break regime 下，size 应显著下降

3. **cross-sectional alpha**
   - 横截面 rank 不变，但把“强 rank + 低 crowding proxy + 低组合 DD”的腿放大

4. **carry / funding / basis**
   - carry 口袋没变，但在组合连续回撤或相关性上升时自动 gross-down

### 5.2 不能直接照搬 repo 的地方
repo 默认是日频结构：

- `lookback = 60 trading days`
- `initial_train = 252`
- `test_size = 63`
- regime features 也按 day 级构造

所以对 short-cycle desk 不能机械复制；必须做 **bar-level rescaling**。

## 6. 我建议的最小实验，不是“先训个大模型”，而是三层递进

## 实验 A：先做无模型版 NAPS-lite（最快）
目标：先验证“**不确定性 + 风险状态 + 换手惩罚**”是不是比 fixed fraction / inverse-vol 更有增量。

### 做法
在已有任一 raw alpha 上，把原始方向信号转成：

- `sign_t`：方向
- `score_t`：强度（比如 z-score / rank strength / edge estimate）

再定义：

```text
base_size_t = clip(k * |score_t|, 0, f_max)
conf_discount_t = 1 / (1 + uncertainty_t)
risk_discount_t = g(drawdown_t, exposure_t, recent_serial_corr_t)
final_size_t = base_size_t * conf_discount_t * risk_discount_t
```

先不用神经网络，先和以下基线比较：

- fixed fraction
- half Kelly
- inverse-vol / risk parity
- simple DD throttle

### 适合先接的 raw alpha
优先接 2 条已经比较像实盘骨架的：

- `2026-04-06_0940_quality-weighted-squeeze-release-alpha.md`
- `2026-04-06_0558_btc-lead-liquidity-lag-alt-alpha.md`

一个偏 trend，一个偏 lead-lag，正好看 overlay 是否可跨 alpha 复用。

## 实验 B：把 uncertainty 单独做出来（中等成本）
如果实验 A 有增量，再补“signal uncertainty”这层。

对 short-cycle 最实用的 4 个 uncertainty proxy：

1. **ensemble disagreement**：同一 alpha 的多参数版本是否同向
2. **bootstrap CI width**：滚动窗口里 edge 估计区间有多宽
3. **regime mismatch**：当前状态离训练 pocket 有多远
4. **microstructure stress**：spread / impact / slippage proxy 是否突然恶化

这一步通常比直接上 cross-attention 更值。

## 实验 C：最后再上 learnable sizing head（完整 NAPS）
只有在 A/B 已经证明确有增量时，再上完整模型。

### 15m 起步参数建议
不要抄日频的 252 天，直接改成：

- `market lookback`: `60 bars`
- `regime vol`: `96 bars`（约 1 天）
- `market corr`: `288 bars`（约 3 天）
- `trend strength`: `96 bars`
- `walk-forward train`: `30 ~ 45 days`
- `test`: `5 ~ 7 days`
- `f_max`: `0.20 ~ 0.25`

### 成本口径建议
repo 用的是：

- one-way `10 bps`

对我们 desk，建议改成分层：

- majors taker: `3 ~ 5 bps`
- alts taker: `6 ~ 12 bps`
- maker rebate / partial fill：单独跑一版

否则会把 sizing 层的价值和过粗的成本假设混在一起。

## 7. 这篇东西最值得抄走的，不是“神经网络”，而是三个原则

### 原则 1：仓位问题要和信号问题分开
很多策略把“是否触发”和“下多大”绑死在一起。

NAPS 的价值在于强行把两件事拆开：

- raw alpha 负责找方向/edge
- overlay 负责决定赌注

### 原则 2：不确定性必须显式入模
如果一个策略只有 score，没有 uncertainty，它的 size 往往会在最不该放大的时候放大。

### 原则 3：换手惩罚应当前置到优化目标
这对短周期特别重要。

很多短周期 alpha 不是方向没用，而是：

> **仓位曲线太抖，收益没死在 signal，先死在 turnover。**

## 8. 我对这份材料的判断

### 值得进研究池的点
- **新**：2026 新 repo + 2026 新预印本元数据
- **通用**：能服务多类 raw alpha，不绑某个形态
- **可最小复现**：先做 NAPS-lite，不需要一上来训练大模型
- **与 desk 当前阶段相关**：我们已经有一堆 raw alpha 候选，确实需要更统一的 sizing 层

### 不要高估的点
- `README.md` 里“NeurIPS 2026”目前只算 repo 自述
- 公开可见的结果摘要还不够细，暂时不能把表格直接当结论
- 默认结构偏日频，迁移到 `1m / 3m / 5m / 15m` 时必须重做窗口和成本口径

## 9. 一句话结论

如果今天只能抄走一件事，我不会先抄它的 transformer，
我会先抄这条：

> **把已有 raw alpha 的方向/强度信号，和“不确定性 + 组合风险状态 + 换手惩罚”分开建模，做成统一 adaptive sizing overlay。**

这比继续补一条边际相近的新 entry rule，更可能直接提升当前素材池的实盘可用性。

## 10. 下一步怎么测

### 最小实验（建议本周内可做）
1. 选两条现有 raw alpha：一条 trend、一条 MR/lead-lag
2. 对每条 alpha 生成：`sign / score / uncertainty proxy`
3. 实现 4 个 sizing baseline：
   - fixed fraction
   - inverse-vol
   - DD throttle
   - **NAPS-lite**（score × uncertainty × risk-state）
4. 在 `15m` 先跑；确认有增量后再下钻 `5m`
5. 指标只看 6 个：
   - net Sharpe
   - max DD
   - turnover
   - return / turnover
   - tail loss per trade
   - alpha 间 capital efficiency

### 是否值得继续到完整 learnable NAPS 的判据
只有当 NAPS-lite 同时满足以下两条，再继续：

- 相比 inverse-vol，**Sharpe 不降且 max DD 明显下降**
- 相比 fixed fraction，**turnover / drawdown 至少改善一项且收益不显著变差**

否则就别急着上深度模型，先把 overlay 维持在规则层。
