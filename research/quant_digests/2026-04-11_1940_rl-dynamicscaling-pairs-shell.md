# 别把这篇 2024 RL pairs paper 只读成“让 agent 学会开平仓”：对 short-cycle desk，更该先测的是「hedged spread z-score fade × clipped dynamic sizing shell」这条 raw alpha

- 时间：2026-04-11 19:40 UTC
- 类型：2024 论文 + 开源 repo source audit（Crossref/OpenAlex metadata + `README.md` + `envs/env_gridsearch.py` + `envs/env_rl.py` + `envs/mock_trading.py`）+ Binance USDⓈ-M `15m/5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**配对两腿的 hedge-adjusted spread 一旦偏离滚动均值，后续更容易向常态回归；RL / dynamic sizing 服务的是这条 spread mean reversion，而不是另起一条新 alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/dynamic-sizing/reinforcement-learning/hedge-ratio/zscore/binance-perpetual/5m/15m/repo/paper/public-data/cost/risk
- 证据类型：论文摘要元数据 + 开源策略代码 + Binance 公共数据 probe

## 1. 这次看了什么
这次看的是 **Hongshen Yang, Abdul Malik (2024), _Reinforcement Learning Pair Trading: A Dynamic Scaling Approach_, Journal of Risk and Financial Management**，以及作者公开的 repo **`Hongshen-Yang/pair-trading-envs`**。

这篇东西最容易被误读成：

> “又一个把 RL 套到交易上、让 agent 自己学买卖。”

但如果按 desk 视角拆开看，它真正清楚的地方其实是：

> **base alpha 仍然是 pair spread mean reversion；RL 真正想解决的是“仓位要不要 all-in、能不能按偏离强弱动态缩放”。**

Crossref 摘要给的原文关键信息也支持这个读法：作者用 **`BTC-GBP / BTC-EUR` 的 `1m` 数据、共 `263,520` 条样本**，传统非 RL pair trading 年化约 **`8.33%`**，RL 版年化约 **`9.94% ~ 31.53%`**。所以 paper 的亮点不是重新发明 alpha，本质上还是在同一条 spread fade 上，讨论 **dynamic scaling** 有没有价值。

## 2. repo 里最值得拿走的，不是“黑盒 agent”，而是这几个明确零件
### 2.1 rule-based baseline 已经很像完整 shell
`envs/env_gridsearch.py` 给的是很清楚的 baseline：
- spread / z-score 监控；
- `OPEN_THRE=1.6`、`CLOS_THRE=0.4`；
- `zscore > open` 时做 `short leg0 / long leg1`；
- `zscore < -open` 时做反向；
- `|zscore| <= close` 时平仓。

翻成人话就是：**先承认 alpha 本体就是“价差拉太开，后面更容易收回来”**。

### 2.2 RL 版核心不是改方向，而是改仓位表达
`envs/env_rl.py` 里有两条路：
- `RL_FixAmt_PairTrade`：动作还是离散 `{开反向, 平, 开正向}`；
- `RL_FreeAmt_PairTrade`：动作变成连续 `[-1, 1]`，本质是**目标仓位大小**。

这就很关键：
**repo 并没有把 raw alpha 改成别的东西，而是在问——同样的 spread reversion，仓位该不该动态缩放。**

### 2.3 对当前 desk 更值钱的 branch，不一定是“真 RL”，而可能是“clipped size rule”
因为一旦把连续仓位真的逐 bar 重调，最先爆炸的往往不是预测，而是：
- 换手；
- 成本；
- 反复减仓/加仓带来的噪声；
- 本来抓得到的 mean reversion，被 re-hedge 自己吃掉。

所以这份材料最值得先偷的，不一定是 PPO / SAC / DQN 本身，而是：
**能不能把“偏离越大、仓位越大”做成一个更克制的 clipped sizing shell。**

## 3. 这轮 portability probe：把它压到 Binance perp `15m/5m` 上，dynamic sizing 到底有没有用？
### 3.1 快检口径
我没有复现原文的 RL 训练，而是把 repo 的想法改写成 desk 更快能验证的三种壳：

- 标的对：`ETH/SOL`、`XRP/ADA`、`DOGE/ADA`、`ETH/BNB`、`XRP/DOGE`、`BTC/ETH`
- 数据：Binance USDⓈ-M 公共 klines
- 周期：`15m`（近 `90d`）和 `5m`（近 `45d`）
- spread：先对 log price 做 rolling hedge ratio，再算 residual z-score
- 开平规则：沿用 repo 语义，`entry=1.6`、`exit=0.4`
- 成本：每边 **`4 bps`**

三种模式：
1. **fixed**：进场就满仓，直到 exit 才平；
2. **scaled_entry**：只在进场时按 `|z|` 大小给 `0.25~1.0` 的 clipped 仓位，持有期间不频繁重调；
3. **continuous**：每根 bar 都按当前 `|z|` 连续调目标仓位，最接近 repo 的 free-amount 思路。

本地 artifact：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/rl_pair_dynamic_scaling_probe_summary_2026-04-11.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/rl_pair_dynamic_scaling_probe_detail_2026-04-11.csv`

### 3.2 first verdict：**continuous free-amount 在 short-cycle 上明显被换手拖死**
先看 6 对资产的平均结果：

#### `15m`
- `fixed`：平均累计收益约 **`-4.26%`**，平均换手约 **`331x`**
- `scaled_entry`：平均累计收益约 **`-0.80%`**，平均换手约 **`111x`**
- `continuous`：平均累计收益约 **`-16.78%`**，平均换手约 **`683x`**

#### `5m`
- `fixed`：平均累计收益约 **`+1.05%`**，平均换手约 **`186x`**
- `scaled_entry`：平均累计收益约 **`+0.59%`**，平均换手约 **`56.5x`**
- `continuous`：平均累计收益约 **`-15.85%`**，平均换手约 **`604x`**

一句话：
**同一条 pairs raw alpha，在 `5m/15m` 上最先死掉的不是信号方向，而是 continuous re-sizing 的换手。**

### 3.3 但“进场时按偏离强度缩放仓位”这条 branch 是有价值的
几个更有代表性的 pair：

- **`BTC/ETH 15m`**：
  - `fixed`：约 **`-4.44%`**
  - `scaled_entry`：约 **`+0.15%`**
  - 换手从约 **`325x`** 降到 **`106.8x`**
- **`ETH/BNB 15m`**：
  - `fixed`：约 **`-7.51%`**
  - `scaled_entry`：约 **`-0.44%`**
- **`XRP/DOGE 5m`**：
  - `fixed`：约 **`+0.63%`**
  - `scaled_entry`：约 **`+1.01%`**

这说明 repo 对 desk 最可迁移的，不是“continuous control agent”，而是：

> **pair MR alpha 可以保留，但 sizing 最好离散化、区间化、clip 化。**

## 4. 为什么它和当前项目直接相关
最近 intake 里我们已经补了很多 pairs / stat-arb raw alpha，但大多还停在：
- 选哪对；
- 怎么算 spread；
- 用什么 threshold。

这篇补的是另一层：
**同一条 raw alpha，仓位表达怎么写，才不会被成本先杀死。**

所以它不是单纯 overlay 话题，因为它服务的对象非常明确：
- base alpha：spread mean reversion
- branch value：dynamic sizing / action representation
- 适用场景：`5m/15m` pairs、basket residual fade、甚至后续 funding/basis convergence shell

## 5. 策略拆解（必填）
- 方向属性：market-neutral / relative-value / mean reversion
- 基础 alpha：hedged spread 的 z-score 极端偏离后更容易回归
- regime：只在高相关、半衰期可接受的 pair 上启用
- filter / veto：`|z|` 不到开仓带、不在高相关 / 可回归 pair、或成本阈值不过线时不做
- risk / sizing / execution overlay：固定满仓、entry-time clipped sizing、continuous resizing 三种表达；成本至少按 `4bps/side` 压测

## 6. 下一步怎么测
先别急着真训练 RL。更合理的下一步是：

1. **把 sizing 离散成 3~5 档**，而不是 continuous `[-1,1]`；
2. 在现有 `5m/15m` pairs shell 上做 **固定仓位 vs clipped 分档仓位** 的正式 friction ladder；
3. 把 pair admission 接回去——只在 `corr / half-life / residual-vol` 合格的窗口启用 sizing shell；
4. 若离散分档在成本后仍稳定优于 fixed，再考虑是否值得用 RL 学“分档切换”，而不是直接学连续仓位。

## 7. 风险与保留意见
- 原论文主样本是 **`BTC-GBP / BTC-EUR 1m`**，更像同一 underlying 的 cross-quote pair；我这里用的是 **cross-asset perp pairs**，所以是 portability，不是 strict replication。
- 这轮没有复现原文 agent 训练，只验证了 **repo 想表达的 sizing 命题** 在 Binance short-cycle 上是否值得继续追。
- 当前 probe 还没接更真实的 maker/taker path、腿间成交不同步、资金费率与流动性上限，所以只能当 first verdict。

## 8. 来源
- **Yang, H., & Malik, A. (2024).** *Reinforcement Learning Pair Trading: A Dynamic Scaling Approach*. **Journal of Risk and Financial Management**.
- DOI: <https://doi.org/10.3390/jrfm17120555>
- Readable URL: <https://doi.org/10.3390/jrfm17120555>
- Repo URL: <https://github.com/Hongshen-Yang/pair-trading-envs>
- README: <https://raw.githubusercontent.com/Hongshen-Yang/pair-trading-envs/main/README.md>

## 9. 一句话带走
**别把这篇 paper 的卖点理解成“RL 会替你找到新 alpha”；它真正对 desk 有价值的是：pairs 的 raw alpha 还是 spread fade，但仓位最好做成 clipped dynamic sizing，而不是 continuous 来回拧。**
