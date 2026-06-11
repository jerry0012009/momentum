# 别把这份 2026 options/MM repo 只读成 A-S 教材：对 short-cycle desk，更该先测的是「predicted-optimal spread × inventory-skew quote ladder」这条完整 maker raw alpha
- 时间：2026-04-07 17:11 UTC
- 类型：GitHub repo source audit（`README.md` + `strategies/market_making/xgboost_spread.py` + `strategies/market_making/avellaneda_stoikov.py`）
- 主题类型：raw alpha
- 基础 alpha：maker spread capture（在低毒性/可成交的盘口状态下，动态报出更合适的双边价差去吃 spread）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / market-making / microstructure / order-book / spread-prediction / xgboost / inventory / options / 1m / 3m / 5m
- 证据类型：工程经验

## 1. 这次看了什么
这次主看 **signorloops (2026) 的 `crypto-options-research-platform`**，但不再把它只读成经典 Avellaneda-Stoikov 教材，而是直接抽其中更适合我们 desk intake 的分支：`strategies/market_making/xgboost_spread.py`。这条线的 **base alpha 很清楚**：不是赌方向，而是赌“当前这段盘口状态下，报多宽的 spread 最容易在扣掉 adverse selection / inventory / 交易成本后留下真钱”。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值钱的，不是“又上了 ML”，而是它把 maker alpha 写成了一个可直接训练的完整壳：先用盘口特征预测“最优报价宽度”，再把 inventory skew 和 size control 接到下单层。
- **一句话证明方式：** 代码不是空谈，它直接把历史窗口特征 → 候选 spread 网格 → 未来窗口模拟收益/成本 → 最优 spread 标签 这条训练链写了出来。
- 特征层很朴素但够 desk：`rv_short(20)`、`rv_long(100)`、盘口 `imbalance`、`bid/ask_volume_ratio`、`spread_percentile`、`price_change_5/20`、`inventory_ratio`，基本都能从公开 L2/L1 或聚合盘口快速移植。
- 标签层不是分类涨跌，而是从候选 spread 网格里选最优值：代码默认用 **10 档候选 spread（5~80 bps）**，对每个候选 spread 做未来窗口模拟，目标函数里显式扣掉 **inventory holding cost** 和 **execution cost**。
- 执行层也不是“预测完就完了”：预测出来的 spread 会再被 **`min/max_spread_bps`** 夹住，同时用 `inventory_skew = inventory_ratio * 0.25` 把 bid/ask 做非对称偏移，并在库存逼近上限时把 quote size 线性缩小。

## 3. 为什么和当前项目有关
这条线和我们最近已经 intake 的 maker 主题（A-S、OFI reservation price、inventory-bounded quoting）是**同一家族但不同一层**：前几篇更多是在写“理论 fair value 怎么偏移”，这篇更像在补 **quote width / quote aggressiveness** 这一层。对 short-cycle desk 来说，它不是附属 overlay，而是能独立成策略壳的 raw alpha：
- 当你已经接受“maker 赚的是 spread capture”后，下一步最值钱的问题就是：**什么时候该报窄一点抢成交，什么时候该报宽一点防毒性？**
- 这份 repo 给了一个很直接的工程答案：先别上复杂 RL，先用可解释的短窗特征去学 **optimal spread bucket**。

## 3.5 策略拆解（必填）
- 方向属性：流动性提供 / 微观结构 / 偏中性
- 基础 alpha：predicted-optimal spread 下的 maker spread capture
- regime：低毒性、mid 相对稳定、盘口厚度尚可的时段更适合开机
- filter / veto：高 realized vol、极端 imbalance、库存逼近上限时应 widen / size-down / no-quote
- risk / sizing / execution overlay：`min/max spread clamp`、inventory skew、inventory-limited size、future-window cost simulation、cancel/replace quote ladder

## 4. 可复刻的最小实验
**研究假设：** 在 `BTCUSDT / ETHUSDT` 的 `1s` 或更细盘口上，用最近 `20~100` 个观测构造的微观结构特征，可以把下一段 `30~60s` 的“最优 maker spread bucket”分出来；按模型报动态 spread，会优于固定 1 档 spread。

**最小回测切口：**
- 资产：`BTCUSDT`, `ETHUSDT`
- 周期：主测 `1m / 3m`，`5m` 只做聚合观察
- 样本：先做最近 `14~30d` walk-forward
- 对照组：
  1. 固定 spread（如 `8bps`）
  2. A-S / 固定 inventory skew baseline
  3. XGBoost predicted spread bucket

**先看 2 个指标：**
1. 成本后 `PnL / quote-hour` 或 `PnL / notional`
2. adverse-selection share（成交后短窗 markout 为负的比例）

## 5. 风险与保留意见
- 这类策略最容易把 **future-window label** 做成 lookahead 幻觉，训练/验证必须严格 walk-forward，不能把全样本最优 spread 倒灌回去。
- 代码里的收益模拟仍然偏 research shell；如果没有 queue position、partial fill、撤单延迟、taker hedge slippage，回测很容易偏乐观。
- 这是 options/MM repo 的实现思路，移植到 perp/spot maker 时，撮合速度、手续费阶梯、盘口厚度和成交密度都可能变。

## 6. 来源
1. **signorloops. (2026). _crypto-options-research-platform_. GitHub repository.**  
   - Venue：GitHub  
   - Readable URL：`https://github.com/signorloops/crypto-options-research-platform`  
   - Repo URL：`https://github.com/signorloops/crypto-options-research-platform`
2. **signorloops. (2026). _strategies/market_making/xgboost_spread.py_.**  
   - Readable URL：`https://github.com/signorloops/crypto-options-research-platform/blob/master/strategies/market_making/xgboost_spread.py`  
   - Raw URL：`https://raw.githubusercontent.com/signorloops/crypto-options-research-platform/master/strategies/market_making/xgboost_spread.py`
3. **signorloops. (2026). _strategies/market_making/avellaneda_stoikov.py_.**  
   - Readable URL：`https://github.com/signorloops/crypto-options-research-platform/blob/master/strategies/market_making/avellaneda_stoikov.py`
4. **Avellaneda, M., & Stoikov, S. (2008). _High-frequency trading in a limit order book_. Quantitative Finance.**  
   - DOI：`10.1080/14697680701381228`  
   - Readable URL：`https://doi.org/10.1080/14697680701381228`
