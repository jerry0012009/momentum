# 别把这篇 2023 论文的 701% gross 当成 production 证据：对 short-cycle desk，更该先测的是「EMA(RSI) 分层 regime 识别 × uptrend-only 约束」这条单资产趋势 raw alpha
- 时间：2026-04-02 22:14 UTC
- 类型：2023 开放获取论文全文 PDF（IJECES article）
- 主题类型：raw alpha
- 基础 alpha：单资产趋势跟随；用 `EMA(7 or 9) of RSI` 先判定市场处于 `uptrend / downtrend / fluctuating`，只在 uptrend 里放行趋势买入，并在 downtrend 用更快的 PSAR/状态切换做退出与 loss protection
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但论文原始结果未计费、未计滑点，且是 long-flat 日频 BTC；desk 版必须重做成本与频率检验）
- 主题标签：raw-alpha / trend / momentum / single-asset / btc / regime-classification / ema-of-rsi / hierarchical-strategy / uptrend-only / psar-exit / loss-protection / long-flat / 15m / 5m / 3m / 1m / paper / public-data / cost
- 证据类型：开放获取全文 + 明确规则阈值 + 年度分解结果 + public-data 可移植

## 1. 这次看了什么
这次不再补一个 pairs / carry / microstructure 旁支，而是补一个**很容易做最小实验、而且和现有 raw alpha 池互补的单资产趋势骨架**。

主材料是：
- **V. S. S. K. R. Naganjaneyulu G, Prashanth G, Revanth M, A. V. Narasimhadhan (2023)**
- **_Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm_**
- **Venue:** *International Journal of Electrical and Computer Engineering Systems*, Vol. 14, No. 7, pp. 765-780
- **DOI:** `10.32985/ijeces.14.7.4`

这篇东西如果只看 headline，很容易被 `MIHCS with EMA7 = 701.8%` 这种 gross 数字带偏；但对我们 desk 真正有价值的，不是“论文说自己赚很多”，而是它把一个**可独立复现的趋势 raw alpha**拆成了：
1. **regime 先判定**，不是任何状态都开趋势单；
2. **uptrend 才放行 BUY**，chop / downtrend 直接收手；
3. **downtrend 用更快的退出逻辑保护**，承认“少赚一点，少死很多”更重要；
4. 全部只依赖 **OHLCV 派生指标**，不需要低频外部数据，能直接映射到 `1m/3m/5m/15m`。

所以这轮我把它定位成：

> **不是“又一篇 TA 教程”，而是一条适合 desk 快速复现的『regime-conditioned single-asset trend raw alpha』。**

## 2. 这条东西的 base alpha 到底是什么
先把一句话说清楚：

> **base alpha = 单资产趋势跟随；核心不是 EMA 本身，而是“只有在 RSI 平滑后确认处于趋势态时，才允许趋势入场”。**

也就是：
- 市场不是一直适合同一套信号；
- 论文先用 `EMA(RSI)` 来判定当前更像：
  - `uptrend`
  - `downtrend`
  - `fluctuating`
- 然后不是三种状态都去做 full trading，而是发现：
  - **Uptrend**：趋势信号最有用；
  - **Downtrend**：重点不是抄底，而是赶紧退出；
  - **Fluctuating**：虽然 RSI 能做一些来回，但对 BTC 这类主流币，追这些小波动经常不值手续费和误判成本。

所以 desk 角度最该 intake 的，不是论文 headline 里的四个策略全家桶，而是这一句：

> **趋势 alpha 要先过 regime gate；最有用的改造不是加更多入场条件，而是把“不该买的时候别买”写死。**

## 3. 论文到底给了什么明确规则
这篇 paper 的好处是：规则不黑箱，阈值也写得相对清楚。

### 3.1 原始单指标基线
作者先测了四类单指标策略：
- **EMA**（文中图示使用 `EMA9` 与 `EMA20`）
- **Bollinger Bands**
- **RSI**
- **PSAR**

结论很直白：
- **EMA** 是单指标里最强的；
- **PSAR** 次之；
- **RSI / BB** 在他们的默认阈值下都一般，尤其 BB 很弱。

五年合并（2018-2022）结果：
- **EMA：`394.1%` profit percentage，`35` 笔交易**
- **PSAR：`113.8%`，`67` 笔**
- **RSI：`-64.5%`，`19` 笔**
- **BB：`-71.7%`，`17` 笔**

这个 baseline 很重要，因为它先说明：

> **paper 里的“新意”不是发现 EMA 有 alpha，而是发现“EMA 只在特定 regime 里开仓，会比裸跑 EMA 更干净”。**

### 3.2 MIHS：先判 regime，再分层使用指标
作者构造了 **MIHS (Multi-Indicator based Hierarchical Strategy)**。

核心规则：
1. 先算 **RSI**；
2. 再对 RSI 做 **EMA7 或 EMA9 平滑**；
3. 用这个 `EMA(RSI)` 判状态：
   - `EMA(RSI) > 60` → **Uptrend**
   - `EMA(RSI) < 40` → **Downtrend**
   - 中间区域 → **Fluctuating**
4. 状态识别后再分配交易逻辑：
   - **Uptrend**：使用 **EMA 趋势 BUY**
   - **Downtrend**：使用 **PSAR 更快 SELL / 保护**
   - **Fluctuating**：使用 **RSI 45/55** 做来回交易

这里最关键的不是 60/40 这两个具体数，而是：

> **他们不是拿 RSI 当入场信号，而是拿 RSI 的平滑值当“市场结构分类器”。**

这对 short-cycle desk 很有启发，因为我们完全可以把它当一个**shared state machine**，而不只是一个老派指标。

### 3.3 MIHCS：真正值得 desk 先测的 branch
作者后来发现，问题出在：
- 从 uptrend 向 chop / downtrend 切换时，`EMA(RSI)` 本身有滞后；
- 这段过渡期里，fluctuating 状态下的 RSI/PSAR BUY 容易把人带进坑里；
- 为了抓那些不大的震荡利润，反而会在突然下跌里付出更大代价。

于是他们进一步做了 **MIHCS (Multi-Indicator based Hierarchical Constrained Strategy)**：

> **把 fluctuating / downtrend 场景里的 BUY 直接砍掉。**

翻成人话就是：
- 只在确认 uptrend 后允许做多；
- 不再试图在震荡和下跌状态里“聪明抄底”；
- 代价是放弃一些 chop 里的小收益；
- 回报是明显更好的 loss protection。

这正是我觉得最值得 desk 先复现的部分。

## 4. 这篇 paper 里最有信息量的数字
### 4.1 单指标基线：EMA 比裸 RSI/BB 强很多
五年合并结果：
- **EMA：`394.1%`，35 笔**
- **PSAR：`113.8%`，67 笔**
- **RSI：`-64.5%`，19 笔**
- **BB：`-71.7%`，17 笔**

说明在 BTC 这种大币上，作者样本里最先活下来的不是均值回复，而是**趋势主导**。

### 4.2 regime gate 确实改善了策略骨架
多指标版本五年合并结果：
- **EMA baseline：`394.1%`，35 笔**
- **MIHS7：`437.5%`，49 笔**
- **MIHS9：`154.5%`，49 笔**
- **MIHCS9：`256.3%`，20 笔**
- **MIHCS7：`701.8%`，20 笔**

这组数里最有用的信息不是 `701.8%` 本身，而是两个结构事实：
1. **`EMA7` 比 `EMA9` 更好**：说明 regime classifier 太慢会伤害趋势信号；
2. **constrained 版把交易数从 `49` 压到 `20`**：说明真正有价值的改进，更像是**交易许可收紧**，而不是更频繁地下单。

### 4.3 2022 熊市里，loss protection 的价值很明显
2022 年单年结果：
- **EMA：`-52.8%`**
- **MIHS7：`-45.0%`**
- **MIHCS9：`-42.7%`**
- **MIHCS7：`-38.7%`**

这正是对 desk 最有价值的信号：

> **这个框架的亮点不是牛市多赚多少，而是熊市少亏多少。**

也就是说，它更像一条**带 regime veto 的趋势壳**，不是裸 beta。

## 5. 我对这些结果的判断：别把 headline 当真，但骨架值得收
必须老实说，这篇 paper 的原始结果有很重的学术/教学实验味：
- **只测 BTC**
- **日频数据**（作者明确写了 `1 sample per day`）
- **long-flat**，不是 long-short
- **未见严肃 transaction cost / slippage / fee / funding 处理**
- 使用的是 **Yahoo Finance** 数据

所以：
- `701.8% gross` 不能直接当 production 证据；
- 这不是“拿来就能跑实盘”的成品；
- 但它确实给了我们一个**很干净、极易复现的 raw alpha 骨架**。

我会把这篇 paper 的正确读法写成：

> **不要抄它的收益率，要抄它的状态机。**

## 6. 和我们 `1m / 3m / 5m / 15m` desk 的关系
这条东西的好处，是它不依赖低频外部数据，完全可以直接下沉到短周期。

### 6.1 为什么它值得进当前素材池
因为我们最近 intake 很多：
- pairs / stat-arb
- funding / basis carry
- OFI / microstructure
- event-driven shock

但相对缺一个**特别轻量、特别容易先跑出来的单资产 trend shell**。

这篇 paper 正好补这个空位：
- base alpha 清楚；
- 原始规则可写成几十行；
- public data 足够；
- 可以直接拿 Binance / OKX / Bybit 的 `1m/5m/15m` klines 快速转译；
- 还能顺手测出一个共享组件：`EMA(RSI)` regime gate。

### 6.2 desk 版应该怎么读
对我们来说，最合理的 desk 化读法不是“照抄 long-flat 日频 BTC”，而是：

- **raw alpha 本体**：趋势跟随
- **核心改造**：`EMA(RSI)` regime gate
- **最有价值的约束**：只在 uptrend 放行 trend entry
- **次优先 branch**：把 fluctuating 状态单独拆成另一个 MR sleeve，而不是和趋势混在同一条策略里

也就是说，这篇东西更像是在告诉我们：

> **趋势和震荡回复最好拆开研究，别在同一套入场权限里混用。**

## 7. 最小可复现实验：先做 15m 主实验，再下钻 5m / 3m
我建议不要先碰 1m；先把骨架跑明白。

### 实验 A：论文思想的最小 short-cycle 版
**标的**：BTCUSDT perp / spot（先单资产）

**bar**：`15m`

**状态机**：
1. 计算 `RSI(14)`
2. 计算 `EMA7(RSI14)` 与 `EMA9(RSI14)`
3. regime：
   - `> 60` → uptrend
   - `< 40` → downtrend
   - else → fluctuating

**raw alpha entry**：
- 使用 `EMA9 close` vs `EMA20 close` 做趋势 cross
- 仅当 `regime == uptrend` 且 `EMA9 > EMA20` 时开多

**exit**：
- `PSAR` flip 向下，或
- `EMA(RSI) < 55` 先减仓，`< 40` 全平，或
- `EMA9 < EMA20`

**sizing**：
- 先固定 notional / 1x
- 再加简单 ATR 或 realized vol target

**成本**：
- taker 2-6 bps 双边扫
- maker / taker 分开记
- funding 单独记账

### 实验 B：验证“constrained 版是不是核心增益来源”
同一数据，至少平行跑 4 条：
1. **裸 EMA9/20 趋势**
2. **EMA9/20 + regime gate（只在 uptrend 开多）**
3. **2 + PSAR emergency exit**
4. **2 + 允许 fluctuating 内 RSI bounce**

要回答的问题不是谁收益最高，而是：
- 谁的 **net Sharpe / Calmar / turnover-adjusted return** 最好？
- 哪条策略的 **熊市回撤压得最明显**？
- `EMA7(RSI)` 是否稳定优于 `EMA9(RSI)`？

### 实验 C：再下钻到 5m / 3m
当 15m 跑通以后，再做：
- **signal 仍在 15m 生成**
- **execution 下沉到 5m / 3m**
- 看入场滑点、追价偏差、以及 stop 触发效率

这更符合 desk 实际：
- 慢状态机
- 快执行

## 8. 下一步怎么测
我建议按下面顺序，不要一上来就乱加 feature。

### Step 1：先验证 regime gate 是否真的有边际价值
最先回答一句：

> **同样是 EMA9/20 趋势，加入 `EMA7(RSI)>60` 的开仓许可后，净收益和最大回撤有没有稳定改善？**

如果这句都答不出来，就别继续堆 PSAR / RSI / BB。

### Step 2：只测“禁止在 chop / downtrend 买入”这一个动作
也就是复刻 MIHCS 的精神，而不是复刻它的所有细节。

重点看：
- trade count 是否明显下降
- fee drag 是否明显下降
- bull regime 的参与率是否还能接受
- drawdown 是否改善

### Step 3：把 fluctuating 逻辑拆成独立 sleeve
论文把 fluctuating 下的 RSI 交易也放进体系里，但 desk 版我建议先拆开。

可以单独做一个小实验：
- 只有当 `40 <= EMA(RSI) <= 60` 时，才允许 `RSI(45/55)` 震荡回复
- 然后和 trend sleeve 分账

原因很简单：
- 趋势跟随和 chop MR 的胜率 / 持有期 / 成本结构不同；
- 混在一起会看不清是谁在赚钱、谁在赔钱。

### Step 4：最后才做对称 short 版本
论文原始版本是 long-flat。

desk 版可以最后再测镜像：
- `EMA(RSI) < 40` 且 `EMA9 < EMA20` 时开空
- 但这一步必须放在 long 版本验证后，因为 crypto 下跌段的成交、资金费率、反抽结构和多头并不对称。

## 9. 我当前的判断
这条题我会给 **中高优先级**，原因不是它“paper headline 很猛”，而是它满足几个很现实的要求：
- **raw alpha 清楚**：就是单资产趋势，不是解释型故事；
- **能独立成完整策略**：entry / exit / state / sizing 都能立起来；
- **public data 即可**：OHLCV 足够；
- **非常适合最小实验**：15m 几乎当天就能跑；
- **和当前 intake 互补**：补的是单资产 regime-conditioned trend 壳，而不是再加一篇 pairs/carry 变体。

一句话结论：

> **这篇 paper 最值得 intake 的不是 701% gross，而是「EMA(RSI) 先判结构，再只在 uptrend 做趋势」这套极易复现、极适合短周期 desk 做第一轮快检的 raw alpha 壳。**

## 10. 来源与复现入口
### 论文
- **Naganjaneyulu G, V. S. S. K. R.; Prashanth G; Revanth M; Narasimhadhan, A. V. (2023)**
- **Title:** _Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm_
- **Venue:** *International Journal of Electrical and Computer Engineering Systems*, 14(7), 765-780
- **DOI:** `https://doi.org/10.32985/ijeces.14.7.4`
- **Readable URL:** `https://ijeces.ferit.hr/index.php/ijeces/article/view/2517`
- **PDF URL:** `https://ijeces.ferit.hr/index.php/ijeces/article/download/2517/322/10018`
- **Repo URL:** 未见作者公开策略仓库

### 数据口径（论文原始）
- **数据源：** Yahoo Finance BTC-USD
- **公开性：** 公开可得
- **更新频率：** 日频（论文原始）
- **最小可复现实验口径：** Binance / OKX / Bybit 公共 `15m` klines 即可转译短周期版本

### 这篇 digest 的一句话结论
**别把这篇 2023 论文读成“又一个 TA 指标拼接”；对我们的 short-cycle desk，更值得先测的是「EMA(RSI) regime gate × uptrend-only 趋势许可 × PSAR/状态退场保护」这条单资产 raw alpha。**
