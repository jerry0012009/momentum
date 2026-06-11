# 别把这份 2026 新 repo 只读成 cointegration 教程：对 short-cycle desk，更该先测的是「AVAX/ICP spread MR × cost-aware scaling × Roll-slippage sanity」
- 时间：2026-04-07 08:28 UTC
- 类型：GitHub 仓库 + repo 内回测产物 / 源码审计
- 主题类型：raw alpha
- 基础 alpha：`15m` 上 `AVAXUSDT/ICPUSDT` 的 cointegration spread mean reversion
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / cost-aware / roll-slippage / alt-pair / binance-spot / 15m / 5m
- 证据类型：工程经验

## 1. 这次看了什么
看的是 2026 新仓库 `Rah9742/Crypto-Stat-Arb`，重点读了 `README.md`、`config/default.yaml`、`src/crypto_trader/signals/pairs.py`、`data/processed/pairs/selection/pair_selection_2024-01-01_2026-03-23_15m.csv`、`data/processed/costs/strategy_comparison.csv` 与 `roll_slippage_summary.csv`。一句话说，这不是“找个 cointegrated pair 然后机械做 z-score”的学生作业，而是一个把 **pair admission → signal shell → cost ladder** 串起来的可复现 15m pairs 原型。

## 2. 核心结论
- 这篇东西的 **base alpha** 很清楚：**稳定 cointegrated 的 alt-pair spread 偏离均值后会回归**，不是 filter，不是 overlay。
- repo 先做滚动 pair ranking，再做交易。`AVAXUSDT/ICPUSDT` 在 `2024-01-01 ~ 2026-03-23` 的 `15m` pair selection 里排 **第 2**，说明作者不是先拍脑袋挑 pair，再回测。
- 执行壳是完整的：滚动 OLS hedge ratio、`|z|` 入场、均值回归出场、`stop z-score`、`max holding`、`gross cap`、`cost-aware scale` 全都有，能直接翻成 desk 可跑策略。
- 更值钱的是它把“成本后还剩多少”摆到台面上：pair 线在测试段 `2025-11-10 ~ 2026-03-23`，**gross return 38.17% → net return 25.74%**，共 **23 笔**，平均持有 **47.39 bars**，`net_sharpe = 1.18`。这说明 alpha 不是只活在 frictionless 幻觉里，但也提醒你：一旦把滑点认真加进去，收益会被明显削掉。
- 一句话核心结论：**值得抄的不是“AVAX/ICP 这个名字”，而是“先滚动筛 pair，再用成本感知的 spread MR 壳去吃回归”。**
- 一句话证明方式：**repo 直接给了滚动 pair 评分表、交易配置、回测对账表和 Roll slippage 估计，不是只放一张漂亮净值图。**

## 3. 为什么和当前项目有关
这条线和我们 desk 现在要补的 raw alpha 素材池是直接相关的：它不是 breakout/filter，也不是解释型综述，而是一条能单独成立的 **relative-value / pairs raw alpha**。更重要的是，它天然适配 `5m/15m` 研究节奏：先做 pair admission，再做 spread trade shell，最后补 cost/risk。对我们来说，可复用的不是“spot 上 AVAX/ICP 一定好”，而是三层结构：
1. **pair admission**：用 rolling cointegration 显著性、稳定性、half-life 先筛；
2. **signal shell**：spread `z-score` 偏离后回归；
3. **cost sanity**：交易前先过 slippage / turnover / hold-time 这层门。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 均值回复
- 基础 alpha：稳定 cointegrated alt-pair 的 residual spread 在大偏离后回归均值
- regime：只在 rolling formation 窗口内仍显著 cointegrated、half-life 不失控的 pair 上交易
- filter / veto：rolling significance、hedge-ratio stability、`exit_zscore`、`stop_zscore`、`max_holding_period`
- risk / sizing / execution overlay：`gross_exposure_cap`、`gross_allocation_fraction`、`cost_aware_min_scale`、asset-level Roll slippage、transaction cost bps

## 4. 可复刻的最小实验
- 研究假设：`15m` 上的 liquid alt-pair 不是“所有 pair 都能做”，而是**先筛出稳定 pair，再做 spread MR** 才有希望在成本后活下来。
- 一个可计算定义：
  - formation：`126d ~ 182d`
  - signal：rolling OLS spread z-score
  - entry：`|z| >= 1.75 ~ 2.25`
  - exit：`|z| <= 0.25 ~ 0.75`
  - stop：`|z| >= 3.5 ~ 4.5`
  - time stop：`32 ~ 48h`
- 最小回测切口：先只跑 `AVAX/ICP`，再扩到 top-3 shortlisted pairs；频率先做 `15m`，再下钻 `5m` 看 half-life 是否仍成立；市场先用 Binance spot 或 perp mid-price proxy。
- 最该先看 2 个指标：
  1. **成本后 Sharpe / positive-window ratio**
  2. **turnover 与平均持有时长是否匹配 half-life**

## 5. 风险与保留意见
- 这条线在 repo 里主要落在 **Binance spot**；如果迁到 perp，要额外吃 funding、冲击成本、强平尾部，不要直接照搬收益。
- Roll slippage 比“完全不加滑点”诚实，但仍可能低估真实 taker 成本，尤其在单边冲击和小币种拥挤时。
- `AVAX/ICP` 这类 alt pair 的协整关系容易被叙事、上币、单币事件打断，所以 pair admission 必须滚动更新，不能静态白名单。
- 这类策略常见死法不是“均值不回归”，而是**回归前先继续扩散 + 成本把边磨平**；所以 stop/time-stop 不能省。

## 6. 来源
- Rah9742. (2026). *Crypto-Stat-Arb*. GitHub.
  - Readable URL: `https://github.com/Rah9742/Crypto-Stat-Arb`
  - Repo URL: `https://github.com/Rah9742/Crypto-Stat-Arb`
- 关键源码/产物：
  - `https://github.com/Rah9742/Crypto-Stat-Arb/blob/main/config/default.yaml`
  - `https://github.com/Rah9742/Crypto-Stat-Arb/blob/main/src/crypto_trader/signals/pairs.py`
  - `https://github.com/Rah9742/Crypto-Stat-Arb/blob/main/data/processed/pairs/selection/pair_selection_2024-01-01_2026-03-23_15m.csv`
  - `https://github.com/Rah9742/Crypto-Stat-Arb/blob/main/data/processed/costs/strategy_comparison.csv`
  - `https://github.com/Rah9742/Crypto-Stat-Arb/blob/main/data/processed/costs/roll_slippage_summary.csv`
