# 别把这篇 2026 deep-learning pairs 论文只读成“LSTM 炫技”：对 short-cycle crypto desk，更该先拆的是「dynamic Johansen spread × forecast-percentile fade」这条 raw alpha 壳

- 时间：2026-04-21 14:38 UTC
- 类型：2026 Frontiers 论文全文 audit + 2026 GitHub repo source audit（`README.md` + `crypto_pairs.py`）+ Binance USDⓈ-M public-data portability probe（`15m/5m`）
- 主题类型：raw alpha
- 基础 alpha：`dynamic cointegration spread mean reversion` —— 先用 rolling Johansen 找会回归的多币 spread，再用 forecasted dynamic score 的极端分位做反向入场
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（可先落成完整 baseline，但当前 short-cycle first verdict 偏负）
- 主题标签：raw-alpha / stat-arb / relative-value / pairs-plus / dynamic-cointegration / johansen / forecast / percentile-entry / mean-reversion / 15m / 5m / paper / repo / public-data / cost / risk
- 证据类型：论文证据 + 工程实现 + 本地最小可移植性验证

## 1. 这次看了什么
这次主看 **Tsoku, J. T., & Makatjane, K. (2026)** 的论文 **_Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_**（*Frontiers in Applied Mathematics and Statistics*，DOI `10.3389/fams.2026.1749337`），以及对应的最小复现仓 `M-man2591/deep-learning-crypto-pairs-trading`。

先把最关键的问题答清楚：

> **这篇东西的 base alpha 是什么？**

答案不是“LSTM 预测价格”，而是：

> **base alpha = 动态协整 spread 会向均衡回归；forecast 模块只是决定“这次偏离值不值得做、该不该现在做”。**

所以它首先是 `raw alpha`，其次才是 ML 增强的 timing 壳。

## 2. 核心结论
- 论文/仓库最值得保留的不是 DNN 或 LSTM 本身，而是这条完整策略骨架：**rolling Johansen → dynamic spread / z-score → forecasted score percentile entry → zero-cross exit**。
- 这条壳天然属于 **pairs / stat-arb / relative-value / mean reversion**，不是 filter，也不是纯 regime 工具。
- 我做的 Binance USDⓈ-M portability probe（`BTC/ETH/LTC/XRP` 四腿 basket）显示：
  - `15m`：`45d`、`14d` formation、`96-bar` z-score 下，`10/90` 分位入场共 `6` 笔，**gross signal hit rate ≈ 47.1%**，**cum net ≈ -1.50%**；说明把日频论文直接压成 `15m`，信号过于粘滞，gross 都还没站稳。
  - `5m`：`20d`、`7d` formation、`180-bar` z-score 下，`10/90` 分位入场 `4` 笔，**cum net ≈ -0.57%**；但若改成更稀疏的 `5/95` strongest-only admission，**gross cum ≈ +0.18%**，扣 `8 bps` round-trip 后转成 **net ≈ -0.22%**。
- 翻成人话：**这条 alpha 壳不是完全死掉，而是“forecast 很容易做出漂亮拟合，但短周期真钱问题主要死在持仓太久和成本太厚”。**

## 3. 为什么和当前项目有关
它和 desk 当前主线的关系很直接：
- 它补的是 **raw alpha 素材池里的 relative-value / stat-arb**，不是又一个趋势或 breakout 变种；
- 它自带完整组件：`entry / exit / turnover / threshold / cost`；
- 还顺手告诉我们一个很现实的研究教训：**预测得准，不等于交易赚得到。**

一句话核心结论：

> **dynamic cointegration spread 这条 raw alpha 在 `5m/15m` 不是不能移植，但不能直接照搬“预测极端分位就一路拿到 zero-cross”这套慢节奏执行。**

一句话证明方式：

> **论文给了方法、repo 给了最小实现，我再用 Binance 公共 `15m/5m` 数据做了 desk-friendly 快检，结果是 forecast 侧看着顺，但 post-cost 侧还不够。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / market-neutral
- 基础 alpha：`dynamic cointegration spread mean reversion`
- regime：协整关系仍稳定、spread 半衰期仍落在可交易区间时才开机
- filter / veto：forecast percentile 必须足够极端；后续应补 half-life / corr / liquidity / funding veto
- risk / sizing / execution overlay：gross-neutral basket sizing、更稀疏的 admission、time-stop 替代死等 zero-cross、maker-first / child execution

## 4. 可复刻的最小实验
**研究假设**：对 liquid-perp basket，dynamic Johansen spread 的 forecast-percentile fade 在 `5m/15m` 仍有 gross edge，但需要比论文更短的持有和更严的入场。

**一个可计算定义**：
1. `BTC/ETH/LTC/XRP` 或更广 liquid basket；
2. rolling Johansen 估权重，EWM 平滑；
3. `spread -> rolling z-score`；
4. 用最近 `30` 个 score 预测 next score；
5. 仅在预测值落到 expanding `5/95` 或更极端分位时开仓；
6. 先比较 `zero-cross exit` vs `time-stop(4/8/12 bars)`；
7. friction ladder 至少做 `4 / 8 / 12 bps`。

**最该先看**：
- `post-cost expectancy / trade`
- `active bar share`（别让信号长期黏在仓位里）

## 5. 风险与保留意见
- 这轮 probe 不是 paper-faithful full replication，而是 desk-friendly first verdict；模型也用轻量预测器替代了论文原始 DNN/LSTM。
- 当前结果最大的问题不是“完全没预测力”，而是 **预测力没有翻译成足够厚的交易边**。
- `15m` 比 `5m` 更差，提示这条壳压到 intraday 后未必是“越慢越稳”，反而可能是**越慢越拖、越容易被持仓成本和 regime 漂移侵蚀**。
- 若后续不加入 time-stop / tighter admission / turnover veto，这条线很容易变成“看起来聪明、实盘不赚钱”的典型 ML stat-arb。

## 6. 来源
1. **Tsoku, J. T., & Makatjane, K. (2026). _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_. Frontiers in Applied Mathematics and Statistics.**
   - DOI：`10.3389/fams.2026.1749337`
   - Readable URL：`https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full`
2. **M-man2591. (2026). _deep-learning-crypto-pairs-trading_. GitHub repository.**
   - Repo URL：`https://github.com/M-man2591/deep-learning-crypto-pairs-trading`
   - Audited files：`README.md`, `crypto_pairs.py`
3. **Local probe artifacts**
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-21_dlcointegration_probe_15m.json`
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-21_dlcointegration_probe_5m.json`
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-21_dlcointegration_thresholdscan_15m.csv`
   - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-21_dlcointegration_thresholdscan_5m.csv`

## 7. 下一步怎么测
先别急着换更复杂模型，先做 3 个最便宜的 A/B：
1. `10/90` vs `5/95` admission —— 先把持仓黏性压下来；
2. `zero-cross exit` vs `4/8/12-bar time-stop` —— 验证是不是“等太久”把 gross edge 耗掉；
3. `single-best basket` vs `all-eligible baskets` —— 看这条壳更像 router 还是 portfolio engine。

如果这三步后 `5m` 能在 `8 bps` 以内保住正的 post-cost expectancy，它才值得进入更正式的 short-cycle stat-arb replication 池。