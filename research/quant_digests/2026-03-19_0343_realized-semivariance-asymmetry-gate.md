# 别把波动过滤只做成单轴阈值：`RS+ / RS-` 非对称拆分，更像 breakout-short / Fib / EMA-PSAR 的方向性 veto + sizing gate
- 时间：2026-03-19 03:43 UTC
- 类型：论文
- 主题标签：breakout-short / fibonacci / retest-hold / ema / psar / realized-semivariance / asymmetry / reversal / regime / filter / sizing / paper / crypto / 15m
- 证据类型：论文证据（**可读全文 + DOI 元数据**）

## 1) 这次看了什么（为何不是重复题）
这轮主看的是一篇近 5 年论文：
- **Liu, Z., Lu, S., Li, B., & Wang, S. (2023)**  
  *Time series momentum and reversal: Intraday information from realized semivariance*  
  Journal of Empirical Finance, 72, 54–77.

和我们刚做过的 `realized-vol mid-band` 不同，这篇给的可迁移旁支不是“高波动就别做”，而是：
- 把波动拆成 **上行半方差（RS+）** 与 **下行半方差（RS-）**；
- 用两者的**非对称关系**去区分“延续”vs“反转/过热”。

这更直接服务当前三条收口线（breakout-short / Fib retest_hold / EMA-PSAR）的**方向性确认与否决**，而不只是再加一个通用抗噪阈值。

---

## 2) 论文里最关键、且可迁移的事实

## 2.1 论文到底做了什么（口径）
- 市场：**中国商品期货 31 合约**，日级组合回测。  
- 样本：约 **2007-01 ~ 2018-12**（按品种起始日不同）。  
- 高频输入：用 **5 分钟收益**构造 RS+ / RS-，并做最近 5 个交易日聚合。  
- 基线：20 日 lookback 的经典 TSM（日频调仓），并做 volatility scaling。  
- 调参方式：用过去 250 个交易日滚动分布给出 `(80%,80%)` 参考点，把 RS+/RS- 平面划分成 4 个区域，再对原始动量信号做“保留/反转/平仓”。

## 2.2 论文里可直接引用的关键数字（非口号）
以下都来自文中表格/正文：
1. **全样本 Sharpe（2008–2018）**：TSM `1.37`，TTSM-S1 `1.62`，TTSM-S2 `1.78`。  
2. **全样本最大回撤**：TSM `26.02%`，TTSM-S1 `16.70%`，TTSM-S2 `14.77%`。  
3. **考虑成本后的 Sharpe（同表）**：TSM `1.30`，TTSM-S1 `1.51`，TTSM-S2 `1.64`。  
4. **2013–2018 子样本（20d lookback）Sharpe**：TSM `1.22`，TTSM-S1 `1.52`，TTSM-S2 `1.77`。  
5. **无波动缩放版本（全样本）Sharpe**：TSM-NVS `0.95`，TTSM-S1-NVS `1.20`，TTSM-S2-NVS `1.36`。  
6. 论文正文给出：在不同 lookback（30~250d）下，TTSM 对 TSM 的 Sharpe 提升在第二子样本“平均接近 **30%**”，并报告一日执行延迟下结果仍稳健。

## 2.3 对 15m desk 最有价值的“旁支结论”
最可迁移的不是整套商品日频 TTSM，而是这条：
- **同样是“高波动”，方向信息不同：RS+ 高 vs RS- 高，不该给同一个交易动作。**

翻成人话：
- 如果最近主要是“向上冲出来的波动”（RS+占优），做空延续要更谨慎；
- 如果最近主要是“向下砸出来的波动”（RS-占优），追空/防守空头更合理；
- 如果两边都很高，很多时候更像过热/混乱区，应该先降仓或 veto。

---

## 3) 为什么它比继续泛化更值得（对三条收口线的直接映射）

1. **V3 breakout-short follow-up**  
   现在最缺的是“哪些 break 值得继续追空、哪些是最后一脚”。RS+/RS- 能给**方向型 continuation gate**，而不是只看总波动。

2. **Fib confirmation / retest_hold**  
   retest_hold 本质是“回踩后谁在主导”。RS+占优更支持 long hold，RS-占优更像 hold 失败风险上升。

3. **EMA / PSAR raw alpha**  
   这条线已经证明成本敏感。RS+/RS- 更适合作为 **position sizing / veto overlay**，先减少“方向错配但被迫开仓”的磨损。

结论：它是三线共用的 **shared directional filter**，边际价值高于再加一个“单轴波动阈值”。

---

## 4) 5m/15m 最小可复现实验（下一步怎么测）

## 4.1 数据与执行口径（沿用 desk 现成）
- 资产：`BTC/ETH/SOL` perpetual
- 周期：信号 `15m`；半方差底层用 `5m`
- 样本：先跑最近 `120d`
- 执行：`next-bar open + no-overlap + hold 8 bars`
- 成本：沿用当前统一 friction（至少报告 `6 bps/side`，可加 `10/15 bps`）

## 4.2 因子定义（最小版，不追复杂）
在每个 15m 决策时点 t：
- 用最近 `W=12` 根 5m（=1h）收益构造  
  - `RS+_t = Σ max(r_5m, 0)^2`  
  - `RS-_t = Σ min(r_5m, 0)^2` 的绝对平方和
- 定义非对称分数：`A_t = (RS+_t - RS-_t) / (RS+_t + RS-_t)`
- 在过去 `M=960` 个 15m 时点（约10天）上估分位点：`q20, q80`

## 4.3 三条线统一实验臂（同一套 overlay）
- `Arm0`：base（当前三条线原规则）
- `Arm1`：总波动门（对照组，类似单轴 realized-vol）
- `Arm2`：**RS 非对称 veto**（方向错配时 veto）
- `Arm3`：**RS 非对称 sizing**（方向一致 size=1，错配 size=0.5，极端错配 veto）

方向映射（先冻结一版，避免过拟合）：
- long setup：要求 `A_t >= q20`；若 `A_t < q20` 则 veto/half-size
- short setup：要求 `A_t <= -q20`；若 `A_t > -q20` 则 veto/half-size
- 若 `RS+` 与 `RS-` 同时 > 各自 `q80`：统一降仓或 veto（过热/混乱区）

## 4.4 先看这 5 个指标
- `post_cost_return`
- `return_per_trade`
- `trade_count_retention`
- `false_break_or_hold_4bars_rate`
- `MAE/MFE`（至少 MAE）

**晋级门槛（最小）**：
- 相比 Arm0，`post_cost_return` 不降；
- `false_break_or_hold_4bars_rate` 下降；
- 交易数保留率不低于 `35%~40%`（避免“靠几乎不交易变好看”）。

---

## 5) 风险与边界（避免误读）
- 论文是**商品日频组合**，不是 crypto 逐根 15m；我们迁移的是“RS+/RS- 非对称逻辑”，不是直接复刻绩效数字。  
- 文中 tuning 含较多区域动作（反手/平仓），15m 首轮不建议一次性照搬，先做 veto/sizing overlay。  
- 若只在单资产单时段有效，优先判定为 pocket，不应直接升格为全局 gate。

---

## 6) 来源（尽量完整）
1. **Liu, Zhenya; Lu, Shanglin; Li, Bo; Wang, Shixuan (2023)**  
   *Time series momentum and reversal: Intraday information from realized semivariance*  
   Venue: *Journal of Empirical Finance*, Vol.72, pp.54–77  
   DOI: `10.1016/j.jempfin.2023.03.001`  
   Readable URL: `https://www.sciencedirect.com/science/article/pii/S0927539823000334`  
   Open full-text mirror (accepted manuscript): `https://centaur.reading.ac.uk/111035/`  
   Repo URL: 未见作者官方公开策略复现仓库

2. （方法论背景）**Patton, A. J., & Sheppard, K. (2015)**  
   *Good volatility, bad volatility: Signed jumps and the persistence of volatility*  
   Venue: *Review of Economics and Statistics*  
   DOI: `10.1162/REST_a_00503`  
   Readable URL: `https://direct.mit.edu/rest/article/97/3/683/58239/Good-Volatility-Bad-Volatility-Signed-Jumps-and`  
   Repo URL: 未见官方统一仓库
