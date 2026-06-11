# 别把这篇 2026 Frontiers paper 只读成 deep-learning pairs 黑盒：对 short-cycle desk，更该先测的是「dynamic-coint spread forecast × percentile trigger」这条完整 raw alpha

- 时间：2026-04-04 18:55 UTC
- 类型：2026 Frontiers 开放获取全文（HTML）source audit
- 主题类型：raw alpha
- 基础 alpha：**动态协整关系下，spread 的下一步方向并非纯随机；当 forecast score 穿越高/低分位阈值时，可做 long/short spread，吃的是 relative-value 的回归/修复，不是单边币价方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/spread-forecast/dynamic-cointegration/johansen/dnn/lstm/dynamic-weighted-ensemble/percentile-threshold/time-stop/market-neutral/crypto/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：open-access paper 全文

## 1. 这次看了什么
一篇 2026 年 Frontiers 论文，把 **dynamic Johansen co-integration + DNN/LSTM + dynamic weighted ensemble** 拼成了一个可交易的 crypto stat-arb 壳。对我们 desk 来说，真正值得 intake 的不是“再上一个深度学习黑盒”，而是它把 **pairs raw alpha** 从“spread 偏离就硬做回归”往前推了一步：**先做 dynamic-coint admission，再预测 spread 下一步方向，只在 forecast score 穿越分位阈值时出手。**

---

## 2) 先回答一句：这篇东西的 base alpha 是什么？
**base alpha = dynamically cointegrated spread 的短窗方向可预测性。**

翻成人话：
- 不是“BTC 明天涨不涨”；
- 也不是“只要 z-score 大就一定回归”；
- 而是：**当一组相关币的相对价差偏离长期均衡后，下一步 spread 更可能朝哪边动，这件事本身可预测。**

所以这篇东西在我们框架里应归类为：
**pairs / stat-arb / relative-value 的 raw alpha**，不是 filter，也不是 overlay。

---

## 3) 为什么这轮值得写，而不是继续补普通 pairs shell
最近 digest 里已经补过很多：
- Engle-Granger / Johansen pair admission；
- z-score fade；
- half-life / Hurst admission；
- cointegration + cost veto / kill-switch。

这篇 paper 的增量在于三点：
1. **不是只做 spread 偏离，而是做 spread forecast。**
2. **不是固定模型，而是 DNN + LSTM 动态加权。**
3. **不是每次偏离都交易，而是用 percentile threshold 决定是否出手。**

也就是说，它补的是我们当前素材池里相对缺的那一层：
> **forecast-driven pairs raw alpha**，而不是又一个 admission-only 或 fade-only 壳。

---

## 4) 论文里真正有用的东西
来源：
- **Johannes Tshepiso Tsoku, Katleho Makatjane (2026), _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_, Frontiers in Applied Mathematics and Statistics.**
- DOI：`10.3389/fams.2026.1749337`

原文核心链路：
1. 用 **dynamic Johansen** 找 time-varying equilibrium；
2. 从协整向量构造 spread / dynamic score；
3. 用 **DNN** 与 **LSTM** 预测 spread；
4. 用 **dynamic weighted ensemble (DWE)** 按近期预测表现动态调权；
5. 只在 forecast score 穿越上下阈值时给 `BUY / SELL / HOLD`。

论文的几个关键数字，足够让它进入研究池：
- 样本：**2018-01-02 ~ 2025-10-31，共 2842 个日频观测**；
- 信号结果：**113 笔信号，81 笔赢、32 笔亏，胜率 71.68%**；
- 风险表现：**Sharpe 1.3662，Sortino 1.1411，MDD -0.2875**；
- 模型误差：DWE 的 **MSE 0.012124 / RMSE 0.110108 / MAE 0.083607**，都优于单独 DNN/LSTM；
- 不确定性：99% prediction interval 的 **平均宽度 0.0772**。

这些数字未必能直接搬到 crypto short-cycle，但至少说明一件事：
**“dynamic-coint spread forecast + thresholded execution” 这条链路不是空想。**

---

## 5) 对 short-cycle desk，真正该抄的不是哪层神经网络，而是哪条策略骨架
如果只把这篇 paper 读成“DNN/LSTM/ensemble 很厉害”，那基本没法落地。

对我们更重要的，是把它拆成下面这条可复现骨架：

### 5.1 Admission
- 每 `6h` 或 `12h` 对 top-liquid perp universe 重跑一次 pair / basket admission；
- 先做 `Johansen / Engle-Granger + residual ADF`；
- 只保留近期仍稳定、成交额足够、非 stale 的组合。

### 5.2 Signal
先别急着上复杂 DWE，第一轮完全可以用更轻的 proxy：
- 当前 spread z-score
- `Δspread`
- rolling vol
- spread slope
- 相关性漂移
- funding / basis 拥挤度（可选）

然后先用：
- logistic / ridge / xgboost 做 `future k-bar spread direction`；
- 目标变量就设成未来 `4/8/12` 根 `15m` 或 `5m` 的 spread 方向。

### 5.3 Trigger
这篇 paper 最值钱的，不是“永远预测”，而是：
**只有 forecast score 穿越高/低分位阈值才出手。**

这非常适合我们：
- `15m` 可用 `80/20` 或 `85/15` percentile；
- `5m` 可以更苛刻，避免信号过密和成本吃掉毛利；
- `1m/3m` 更适合作为 execution confirm，不建议直接当主时钟。

### 5.4 Exit
最朴素、最容易先验的方式：
1. forecast 翻向就平；
2. spread 回到中性带就平；
3. `time stop`：`4/8/12` bars；
4. pair break / vol shock / venue issue 直接 kill-switch。

### 5.5 Sizing
- pair notional 可按 `signal confidence / realized vol` 缩放；
- 组合层保持 dollar-neutral 或 beta-neutral；
- 单 pair cap 先保守，不要因为一对相关币短时共振就把 book 集中爆掉。

### 5.6 Cost
这类策略最怕“模型先进，成本更先进”。

第一轮必须主表写清：
- maker/maker
- maker/taker
- taker/taker
- signal lag
- residual leg risk
- hold time 分布

否则 paper 里的 Sharpe 只能当灵感，不能当可交易结论。

---

## 6) 这篇 paper 的限制，必须先说清
这篇文章有三个明显限制：

### A. 原文主样本是日频，不是 `5m/15m`
所以它给我们的是**结构模板**，不是可直接搬的参数。

### B. 标题写 pairs trading，但正文更像 dynamic-coint 的多资产 spread
文中实际展示的协整向量里，**USDT 系数极大（-270.904）**，更接近一个多资产 equilibrium score，而不只是传统两腿 pair。  
这点反而提醒我们：
> **desk 第一版最好先回到最简单的两腿或小篮子 spread，不要一上来做太宽的 basket。**

### C. 论文没有把真实交易成本写到我们需要的精细程度
因此 production relevance 取决于：
- 你的 venue；
- 你的 fee tier；
- 你能否 maker-first；
- 以及你的残腿控制是否够好。

---

## 7) 为什么它依然值得进 raw alpha 池
因为它回答了一个很实用的问题：

> 在 pairs / stat-arb 里，我们是不是只能做“偏离即回归”的老套路？

这篇 paper 给出的答案是：**不必。**

你完全可以把 pairs 这件事拆成两层：
1. **dynamic-coint 决定谁值得看；**
2. **forecast score 决定现在要不要做。**

这个思路对 `5m/15m` 非常有价值，因为：
- 它天然适合 signal thinning；
- 它比纯 z-score shell 更容易和成本约束结合；
- 它也更容易后接 regime gate，而不把 gate 误当 alpha 本体。

---

## 8) 下一步怎么测（直接可排）
按优先级给四步：

1. **先做 ML-lite baseline，而不是直接复刻 DWE**
   - universe：`BTC/ETH/BNB/LTC/XRP/SOL/ADA/DOGE` 这类高流动 perp；
   - 时钟：优先 `15m`，再下钻 `5m`；
   - 目标：future `4/8` bars spread direction。

2. **做 A/B 对照：forecast shell vs z-score fade shell**
   - 同一 admission、同一成本模型、同一 time stop；
   - 比：净 Sharpe、换手、平均持仓、尾部回撤。

3. **把 trigger 做成 percentile，而不是固定阈值**
   - 看 `80/20`、`85/15`、`90/10`；
   - 目标不是提高信号数，而是提高每笔的净后质量。

4. **只有当 ML-lite 明显优于 z-score baseline，才上更重的模型**
   - 再考虑 LSTM / XGBoost / ensemble；
   - 否则很可能只是把简单 alpha 包成复杂工程。

一句话，真正该测的是：
**dynamic-coint spread forecast 是否能在成本后打赢 plain z-score fade。**
如果打不赢，就别被 paper 里的深度学习叙事带跑。

---

## 9) 本轮结论（短版）
这篇 2026 Frontiers paper 值得 intake，但不是因为它用了 DNN/LSTM，而是因为它给了我们一条更像样的 pairs raw alpha 升级路径：

**从“spread 偏离就做”升级到“dynamic-coint admission × spread direction forecast × percentile trigger”。**

对当前 desk 来说，它最适合落地成：
- `15m` 主时钟的 forecast-driven pairs shell；
- `5m` 的更快版本只保留高置信度阈值；
- `1m/3m` 仅做执行确认与残腿控制。

如果第一轮 A/B 测试里它能在成本后稳定优于 plain z-score fade，这条线就值得升格成正式复现项目。

---

## 10) Sources
1. **Tsoku, Johannes Tshepiso; Makatjane, Katleho (2026). _Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs_. Frontiers in Applied Mathematics and Statistics.**
   - Year: 2026
   - Venue: Frontiers in Applied Mathematics and Statistics
   - DOI: `10.3389/fams.2026.1749337`
   - Readable URL: `https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full`
   - PDF URL: `https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/pdf`
   - Repo URL: 未见公开 repo

2. **Johansen, Søren (1988). _Statistical analysis of cointegration vectors_. Journal of Economic Dynamics and Control.**
   - DOI: `10.1016/0165-1889(88)90041-3`
   - Readable URL: `https://doi.org/10.1016/0165-1889(88)90041-3`

3. **Gatev, Evan; Goetzmann, William N.; Rouwenhorst, K. Geert (2006). _Pairs Trading: Performance of a Relative-Value Arbitrage Rule_. Review of Financial Studies.**
   - DOI: `10.1093/rfs/hhj020`
   - Readable URL: `https://doi.org/10.1093/rfs/hhj020`
