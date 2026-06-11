# 别把这篇 2025 open-access 论文只读成“美股和 crypto 有联动”：对 desk 更该先测的是「QQQ / NVDA 5m 冲击 → ETH/BTC 15m 跟随」raw alpha

- 时间：2026-03-30 22:04 UTC
- 类型：2025 *Journal of International Financial Markets, Institutions and Money* 开放获取摘要/Highlights + QQQ/NVDA `5m` 与 Binance `5m` 本地 60d transfer check
- 主题类型：raw alpha
- 基础 alpha：**US tech / semiconductor risk shock 会先走在大币前面；把 `QQQ / NVDA` 的短窗收益当成 leader，用它去交易 `BTC / ETH / DOGE` 的后续 `15m` 回报，本质上吃的是 cross-market lead-lag，而不是泛泛的 risk-on 宏观叙事。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/lead-lag/us-equity/tech/semiconductor/qqq/nvda/btc/eth/doge/us-session/5m/15m/1m/3m/paper/public-data/yfinance/binance/cost
- 证据类型：论文摘要/Highlights 证据 + 公开 `5m` 数据最小 transfer check

## 1. 这次看了什么

这次主看的是一篇 2025 的 open-access 论文，但我不想把它读成“相关性研究”。更值得 desk 先拿走的，是一条能直接落成 `5m -> 15m` 执行骨架的 cross-market raw alpha：

- **Authors**：Elie Bouri, Amin Sokhanvar, Harald Kinateder, Serhan Çiftçioğlu
- **Year**：2025
- **Title**：*Tech titans and crypto giants: Mutual returns predictability and trading strategy implications*
- **Venue**：*Journal of International Financial Markets, Institutions and Money*, Vol. 99
- **DOI**：10.1016/j.intfin.2024.102109
- **Readable URL**：https://www.sciencedirect.com/science/article/pii/S1042443124001756
- **IDEAS / RePEc 摘要页**：https://ideas.repec.org/a/eee/intfin/v99y2025ics1042443124001756.html
- **Repo URL**：未见作者公开配套 repo

如果只用一句人话概括这篇东西：

> **别把美股 tech 只当“背景板”。对短周期 desk，它更像一个外部 leader：先看 tech / semis / NVDA 的冲击，再决定要不要在 crypto 里做后续 15 分钟。**

## 2. 核心结论

先把 base alpha 说清楚：

> **base alpha 不是“股票和 crypto 长期相关”。base alpha 是“tech / semiconductor / Nvidia 的收益冲击，会在若干滞后后对 BTC / ETH / DOGE 形成可交易的方向性预测”。**

论文摘要和 Highlights 给出的关键信息有 4 点：

1. **研究对象就是 returns predictability，不是静态相关性。** 作者明确检验的是 U.S. technology sector、semiconductor subsector、Nvidia 与 BTC/ETH/DOGE 之间的方向性预测关系。
2. **这种 predictability 不是单向的，但对 crypto desk 最有价值的是“tech -> crypto”这半边。** 因为外部 leader 更适合当 admission trigger。
3. **控制 DXY 与美债市场后，predictability 仍然存在，尤其对 BTC、ETH 更明显。** 这意味着它不只是“美元大跌所以都涨”的单因子故事。
4. **论文说基于 cross-quantilogram 的策略优于 always-long benchmark。** 也就是说，它不是纯解释型文献，作者自己也把它往 trading rule 方向推进了。

一句话核心结论：

> **对 desk 来说，这篇 paper 最值得搬的，不是“tech 和 crypto 互相影响”这句空话，而是“用外部 leader 的尾部冲击做 crypto follow-through / follow-down 交易”。**

一句话说明它怎么证明：

> **论文在日频上用 cross-quantilogram 找到 U.S. tech、semis、NVDA 与 BTC/ETH/DOGE 之间跨 quantile、跨 lag 的显著正向 predictability；而我在本地把它缩到最近 60 天 `5m` 数据后，发现最有意思的短周期 pocket 不是对称 beta，而是 `QQQ 负向 5m 冲击 -> ETH/BTC 未来 15m 继续走弱`。**

## 3. 为什么和当前项目有关

这轮值得 intake，原因很直接：

1. **它是 raw alpha。** 不是“市场情绪解释”，也不是纯 regime 评论。
2. **它给的是一条我们素材池里还不算拥挤的外部 leader 线。** 这和最近很多 `pairs / funding / same-underlier stat-arb / intra-crypto lead-lag` 不同。
3. **它能直接映射到 `5m / 15m`。** 美股现金时段的 `QQQ / NVDA 5m` 数据公开可拿；crypto `5m` 数据更不用说。
4. **它可以独立成策略，也能服务其他 alpha。** 若 standalone pocket 成立，可直接做；若不够强，也能变成 BTC/ETH breakout、alt beta 追随、risk-on 追涨的 shared gate。

## 3.5 策略拆解（必填）

- 方向属性：**cross-market / lead-lag / event-driven / US-session directional alpha**
- 基础 alpha：**US tech leader 的短窗收益冲击，能预测 crypto 在后续 `15m` 左右的延续/跟随方向**
- regime：**最适合 U.S. 现金交易时段；财报、FOMC、盘中 halts、巨量单名股事件时需要单独隔离**
- filter / veto：**只在 leader 冲击过分位阈值、crypto 当下 spread/深度正常、且不是重大宏观事件冻结窗时触发**
- risk / sizing / execution overlay：**按 target coin 的滚动波动做 inverse-vol sizing；若 leader 冲击来自单名股（NVDA）而指数未确认，则先降仓；若 crypto 已先走出大同向 bar，则 veto，避免追最后一棒**

## 4. 3 个关键数据点

### 4.1 论文给的原始研究框架并不含糊

摘要里写得很清楚：

- 样本是 **2015-08-07 到 2024-02-08** 的日频数据；
- tech sector、semiconductors、**Nvidia** 都对 crypto returns 有显著 predictive power；
- 控制 **U.S. dollar** 与 **treasury market** 后，这种 predictability 仍然保留；
- 基于这些 cross-quantilogram 关系构建的 trading strategy **优于 always-long benchmark**。

翻成人话：作者不是在讲“风险资产都一起涨跌”，而是在讲 **谁先动、谁后跟**。

### 4.2 本地 60 天 `5m -> 15m` transfer check：最强 pocket 不是对称，而是 QQQ downside -> ETH short

我用：

- `QQQ / NVDA`：Yahoo Finance 公开 `5m` 数据；
- `BTCUSDT / ETHUSDT / DOGEUSDT`：Binance Spot 公开 `5m` K 线；
- 时间窗：最近 **60 天**，仅保留 **U.S. cash session** 重叠时段；
- 规则：leader 当根 `5m` 收益落入自身近 60 天分布的 **上/下 10% 尾部** 时，交易 target 后续 **15m** 回报。

结果里最值钱的是这几个数：

- **QQQ 下 10% 尾部阈值约 `-14.05 bps / 5m`**；一旦触发，**ETH 下一个 `15m` 的 short alpha 平均约 `+11.88 bps`**，**BTC 约 `+6.31 bps`**，三币等权篮子约 **`+6.96 bps`**。
- 同样是 QQQ，上 10% 尾部阈值约 **`+13.78 bps / 5m`**，但对 BTC/ETH 的后续 long 并不强：**ETH long 反而约 `-1.28 bps`**，说明短周期 transfer **明显不对称**。
- **NVDA** 的 5m 尾部阈值更大（约 **±23 bps**），传导更分散：**ETH short 约 `+4.30 bps`**，**DOGE long 约 `+4.19 bps`**，等权篮子 long-short 约 **`+2.07 bps`**。

这组数最重要的含义不是“alpha 已经被确认”，而是：

> **短周期真正值得先测的，不是 tech 正负冲击都对称地传给 crypto，而是“QQQ downside shock 的 follow-down pocket”更像真钱口袋。**

### 4.3 事件数不算稀缺，足够做 first verdict

在最近 60 天重叠样本里：

- `QQQ` 上/下尾部事件各约 **281~282 次**；
- `NVDA` 上/下尾部事件也各约 **282 次**。

也就是说，这不是那种一年才来几次的宏观事件 alpha。哪怕只盯 U.S. cash hours，**事件频率已经足够快**，能支撑 `1m / 5m / 15m` 研发迭代。

## 5. 真正值得 desk 先偷哪一段

最该偷的不是论文里的“mutual predictability”整句，而是这条更窄、更短、更能测的 desk 读法：

1. **先把 leader 缩窄到最易拿的数据源。** 第一轮就只做 `QQQ / NVDA`。  
2. **先把 target 缩窄到最液体的大币。** 第一轮只做 `ETH / BTC`，DOGE 当 beta 扩展样本。  
3. **先测 downside pocket。** 当前本地 transfer check 里，最像真钱的是 `QQQ 负向 5m shock -> ETH/BTC 未来 15m 继续偏弱`。  
4. **别急着做对称 long-short。** 上涨冲击的传导没 downside 那么干净，强行对称会稀释 edge。  

所以这条线更像：

> **先做 `US-tech downside shock short crypto`，再决定是否扩到 upside continuation。**

## 6. 可复刻的最小实验

### 6.1 数据源、公开性、更新频率

- **QQQ / NVDA（Yahoo Finance）**：公开可得；`5m` 足够做第一轮 transfer check
- **BTCUSDT / ETHUSDT / DOGEUSDT（Binance spot/perp）**：公开 REST / WebSocket
- **公开性**：公开可拿，无需私钥
- **最小实验频率**：`5m` 先行；若成立，再降到 `1m/3m`

### 6.2 最小可复现实验口径

1. **时段**：只做 U.S. cash session（约 `13:30-20:00 UTC`）
2. **leader**：`QQQ`, `NVDA`
3. **target**：`ETHUSDT`, `BTCUSDT`（可选 `DOGEUSDT` 做 beta 扩展）
4. **信号定义**：
   - `leader_ret_5m = close_t / close_{t-1} - 1`
   - 用最近 20~60 个交易日同一时段分布做 rolling percentile
5. **入场**：
   - **主版本先只做 short**：若 `QQQ_ret_5m <= rolling_p10`，在下一根开头 short `ETHUSDT` / `BTCUSDT`
   - **备选 long**：若 `NVDA_ret_5m >= rolling_p90`，小仓位 long `DOGEUSDT` 或 beta basket
6. **出场**：
   - 固定持有 `15m`；
   - 或 leader 均值回撤 / target 先 hit `0.75 ATR` 就提前平
7. **仓位**：
   - 单币独立 notional cap
   - target 侧 inverse-vol；当 NVDA 单名股信号与 QQQ 方向冲突时减半仓位
8. **成本**：
   - 先按 Binance perp taker round-trip `8 bps` 粗估
   - 后续再补 maker/taker mix 与 spread drift

### 6.3 第一轮先回答什么

- `QQQ downside -> ETH short` 在 `5m / 10m / 15m / 30m` 哪个持有窗最厚？
- 这条边在 **BTC/ETH** 哪个更稳定？是否只有 ETH 更像高 beta 传导腿？
- 若用 **QQQ + NVDA 同向确认** 才开仓，事件数下降多少、净边提升多少？
- 扣掉 `8 bps` round-trip 后，哪些 pocket 还活着？

## 7. 这张卡最容易错在哪里

- **错法 1：** 把它做成全天候 alpha。实际上它更像 **U.S. 时段事件口袋**。  
- **错法 2：** 假设正负冲击对称。当前快检更像 **downside 传导强于 upside**。  
- **错法 3：** 用单名股 leader 不加指数确认。NVDA 单名股噪音会更大。  
- **错法 4：** leader 冲击出来时 crypto 已经先走了一大段，还去追第二棒。  
- **错法 5：** 看到日频论文就直接搬成日频 overlay。对 desk 真正有价值的是 **把它压缩成 intraday admission trigger**。  

## 8. 为什么值得进入研究池

它值得进池，不是因为这篇论文已经把 `5m/15m` 版本证明完了，而是因为它满足当前最重要的几条：

1. **base alpha 清楚。** 外部 leader 冲击 -> crypto 滞后跟随。  
2. **公开数据就能先做最小实验。** 不需要稀有链上标签，也不需要私有订单流。  
3. **和现有素材池互补。** 它不是又一篇 intra-crypto pairs / funding / residual MR。  
4. **既能 standalone，也能当 shared admission layer。** 这对后续 BTC/ETH/alt beta 交易都很有用。  

## 9. 下一步怎么测

1. **先把 `QQQ downside -> ETH short` 做成单腿 first verdict。** 只测 `5m shock -> 15m hold`，不要一开始就做对称组合。  
2. **加入 rolling intraday percentile。** 不要用全样本固定阈值，避免不同时段波动尺度不同。  
3. **做 4 组对照：**
   - `QQQ-only`
   - `NVDA-only`
   - `QQQ & NVDA same-sign confirm`
   - `QQQ shock + crypto 本地波动 veto`
4. **把 target 从 spot 扩到 perp。** 明确扣掉 funding / taker / spread 之后，看净边还剩多少。  
5. **若 ETH 成立、BTC 较弱，就把这条线定义成“高 beta follow-down pocket”，而不是强行扩大全市场。**

## 10. 本次本地 artifact

- `reports/artifacts/quant_digests/us_tech_crypto_leadlag_20260330/event_stats.csv`

## 11. 来源

### 论文 / 摘要页
- Bouri, E., Sokhanvar, A., Kinateder, H., & Çiftçioğlu, S. (2025). *Tech titans and crypto giants: Mutual returns predictability and trading strategy implications*. *Journal of International Financial Markets, Institutions and Money*, 99.
- DOI: https://doi.org/10.1016/j.intfin.2024.102109
- Readable URL: https://www.sciencedirect.com/science/article/pii/S1042443124001756
- IDEAS / RePEc: https://ideas.repec.org/a/eee/intfin/v99y2025ics1042443124001756.html

### 公开数据接口 / 数据源
- Yahoo Finance `QQQ`, `NVDA` `5m`
- Binance Spot Klines: https://api.binance.com/api/v3/klines
