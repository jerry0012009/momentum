# 别把 Liu, Lu, Wang (2021) 只读成“商品 CTA 风控论文”：对 short-cycle crypto desk，更该先拆的是「time-series momentum × partial-moment reversal veto」这层可迁移 overlay

- 时间：2026-04-18 05:08 UTC
- 类型：2021 *International Review of Financial Analysis* 论文全文（CentAUR post-print PDF）+ IDEAS/RePEc 摘要页 + Binance USDⓈ-M `15m/5m` lightweight portability probe
- 主题类型：overlay
- 基础 alpha：**time-series momentum / trend continuation**——先用过去一段累计收益的符号决定顺势多空；本文新增的不是另一个主信号，而是用 **upper partial moment / lower partial moment** 去识别“这段 momentum 可能正在反转”，从而 close / reverse / veto 原始 TSM 持仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（论文给了足够清楚的 rule-based overlay，但它依附于一个已有的 TSM 母体；更适合作为现有 trend alpha 的 reversal gate / veto，而不是独立 alpha 本体）
- 主题标签：overlay / trend / momentum / reversal / partial-moment / upper-partial-moment / lower-partial-moment / veto / drawdown-control / tsmom / commodity-futures / crypto-portability / 15m / 5m / paper / fulltext / public-data / risk
- 证据类型：全文规则 + 论文表格结果 + crypto portability probe

先回答 base alpha：**说得清楚，但不是这篇 paper 自己发明的。**
它的 base alpha 是最普通的 **time-series momentum**：过去一段涨就继续做多，过去一段跌就继续做空。本文真正贡献是：

> **当短窗正负尾部波动的结构开始“不对劲”时，别继续傻抱趋势单；要么平、要么反、要么降暴露。**

所以这轮不该把它包装成新的 raw alpha，而该老老实实归类为：
**服务于 trend / breakout / continuation 母体的一层 reversal overlay。**

---

## 1. 这次看了什么
主来源：
- **Authors：** Zhenya Liu / Shanglin Lu / Shixuan Wang
- **Year：** 2021
- **Title：** *Asymmetry, tail risk and time series momentum*
- **Venue：** *International Review of Financial Analysis*, Vol. 78, Article 101938
- **DOI：** `10.1016/j.irfa.2021.101938`
- **Readable URL：** <https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002581.html>
- **Full-text / post-print URL：** <https://centaur.reading.ac.uk/100824/>
- **PDF：** <https://centaur.reading.ac.uk/100824/1/FINANA-D-21-00329-R1.pdf>

我这轮实际拿到的是：
1. IDEAS/RePEc 摘要页；
2. University of Reading CentAUR 的 post-print PDF 全文；
3. 文中核心表格（Table 2 / 5 / 7 / 9 / 10）；
4. 一个针对 Binance USDⓈ-M `15m/5m` 的最小 portability probe，用来判断这层 overlay 压到 crypto short-cycle 后还有没有增益。

---

## 2. 用人话讲，这篇 paper 到底在干嘛
原始 TSM 很简单：
- 看过去 `J` 期累计收益；
- 正的就多，负的就空；
- 下一期持有；
- 再滚动。

这篇 paper 说：
**真正让 TSM 难受的，不是平时，而是 reversal。**
也就是：
- 上涨趋势里的突然 slump；
- 下跌趋势里的突然 rebound；
- 以及来回锯齿的 sideways 段。

作者的想法不是再发明一个复杂预测器，而是只盯一个更具体的问题：

> **最近几根里，正收益尾部风险和负收益尾部风险，是否开始出现不对称地“翘起来”？**

他们用两个量来做这个判断：
- **UPM（upper partial moment）**：最近短窗里，正收益部分的平方平均；
- **LPM（lower partial moment）**：最近短窗里，负收益部分的平方平均。

论文里的定义是：
- `UPM_i,t = mean(r^2 * 1[r>0])`
- `LPM_i,t = mean(r^2 * 1[r<0])`

翻成人话：
- `UPM` 大，表示最近向上跳的“尾巴”很肥；
- `LPM` 大，表示最近向下砸的“尾巴”很肥。

关键不是单独看大不大，而是看 **UPM / LPM 落在 joint distribution 的哪个区域**。

---

## 3. 论文最值得记住的机制，不是公式，是“4 区域动作表”
作者把 `(UPM, LPM)` 的 joint distribution 用历史 `(80%, 80%)` 分位点切成四个区域：

- **Region 1：** `UPM` 高、`LPM` 也高 → 双尾都肥，最像混乱段 → **close out**
- **Region 3：** `UPM` 不高、`LPM` 也不高 → 尾部没炸 → **继续原始 momentum**
- **Region 2 / 4：** 一边尾部高、一边不高 → 这里最可能提前暴露 reversal 模式

这正是本文最值钱的地方：
它把“趋势单什么时候更容易被打脸”这件事，写成了一个 **离散、可执行、可回测** 的动作表。

### 3.1 在 2008–2012 子样本里（MTSM-S1）
论文发现：
- upward momentum 下，**Region 2** 更容易亏；
- downward momentum 下，**Region 4** 更容易亏。

所以他们设计 **MTSM-S1**：
- Region 1：平仓
- Region 2：把原本 long 改成 **short all**
- Region 3：继续原始 momentum
- Region 4：把原本 short 改成 **long all**

### 3.2 在 2013–2019 子样本里（MTSM-S2）
结构变了：
- upward momentum 下，亏损更偏向 **Region 4**；
- downward momentum 下，亏损更偏向 **Region 2**。

于是他们把 Region 2 / 4 的动作对调，得到 **MTSM-S2**。

这点很重要：
**作者没有把 overlay 假设成永远不变，而是承认 reversal pattern 会随市场结构迁移。**
这对 crypto short-cycle desk 很有启发：
如果要搬，用它的“判反转框架”，别生搬它在某一市场、某一年代的固定动作表。

---

## 4. 论文里最硬的几个结果

### 4.1 原始 TSM 在中国商品期货里本身是赚钱的
Table 2 给的 baseline 先不差：
- 全样本（2008–2019），`J=30` 时原始 TSM：
  - **Annual Return 20.25%**
  - **Sharpe 1.05**
  - **MDD 28.71%**
- 第一子样本（2008–2012），`J=30`：
  - **Annual Return 26.29%**
  - **Sharpe 1.10**
- 第二子样本（2013–2019），`J=30`：
  - **Annual Return 15.93%**
  - **Sharpe 1.04**

所以别误读：
这篇不是在证明 “TSM 不行”。
它是在说：
**TSM 行，但会被 reversal drawdown 咬得很疼。**

### 4.2 Overlay 的主要价值不是多赚很多，而是更稳
Table 7 是最关键的 performance 表：

#### 第一子样本（2008–2012）
- 原始 TSM：
  - **Annual Return 26.29%**
  - **Sharpe 1.10**
  - **MDD 28.71%**
  - **Sortino 1.65**
- **MTSM-S1**：
  - **Annual Return 25.11%**
  - **Sharpe 1.25**
  - **MDD 25.62%**
  - **Sortino 1.91**

也就是：
- 年化收益略降；
- 但 Sharpe 从 `1.10 → 1.25`；
- MDD 从 `28.71% → 25.62%`；
- Sortino 从 `1.65 → 1.91`。

#### 第二子样本（2013–2019）
- 原始 TSM：
  - **Annual Return 15.93%**
  - **Sharpe 1.04**
  - **MDD 18.73%**
  - **Sortino 1.68**
- **MTSM-S2**：
  - **Annual Return 14.30%**
  - **Sharpe 1.25**
  - **MDD 11.13%**
  - **Sortino 2.13**

这里更明显：
- 收益略降；
- 但 **Sharpe 提升约 20%**；
- **MDD 从 18.73% 砍到 11.13%**；
- Sortino 从 `1.68 → 2.13`。

这已经很接近一个 desk 真会在意的结论：
**如果你本来就有一条能赚钱的 TSM / breakout / continuation 母体，这种 overlay 的职责不是把收益翻倍，而是让资金曲线少塌。**

### 4.3 这种改进不是只在一个 lookback 上偶然出现
Table 9 显示，在作者的市场里，跨多组 look-back windows，MTSM 仍能保持大致 **约 20% 的 Sharpe 提升**。

这意味着它不像那种只对单一参数灵敏到离谱的脆弱 patch；
至少在 paper 的原生场景里，它更像一个**稳定的 reversal-risk management layer**。

### 4.4 极端波动段里，overlay 的价值更像真价值
COVID 段（Table 10，2019-12 到 2020-05）：
- 原始 TSM：
  - **Annual Return 26.26%**
  - **Sharpe 1.39**
  - **MDD 8.51%**
- **MTSM-S2**：
  - **Annual Return 23.73%**
  - **Sharpe 1.79**
  - **MDD 4.81%**

也就是：
- 收益还是略降；
- 但 Sharpe 提升；
- **最大回撤几乎砍半**。

这很适合作为 short-cycle desk 的一个思考起点：
**有些 overlay 在平时看着只是“赚少亏也少”，但真到 crash / whipsaw 段时，它是在保命。**

---

## 5. 为什么这东西对当前 crypto short-cycle desk 仍有意义
### 5.1 它不是 raw alpha，但它服务的是最常见、最容易死在 whipsaw 里的 raw alpha
这篇 paper 不是又一条新趋势信号。
但它服务的对象非常具体：
- trend-following
- breakout continuation
- time-series momentum
- trend-pullback continuation

这些正是 short-cycle desk 最容易碰到的母体。

所以它的价值是：
**给 trend alpha 补一层“别在最容易被反杀的时候还硬抱”的 veto / reversal management。**

### 5.2 它用的输入变量很便宜
如果你想把它搬到 `1m/3m/5m/15m`：
- 不需要外部 API；
- 不需要 OI / funding / sentiment；
- 不需要 order book；
- 只要 bar return 序列。

这点非常 desk-friendly：
**实现成本低，适合作为现有 trend alpha 的一层通用 gate。**

### 5.3 它补的是“趋势策略最疼的那块”
很多 trend / breakout raw alpha 的问题，不是 baseline 完全没 edge，
而是：
- 反手太慢；
- 遇到 whipsaw 时净值掉坑；
- 明明只是一层延续 alpha，却承受了本不该吃的 reversal 尾部风险。

partial-moment overlay 正是在解决这个问题。

---

## 6. 但要诚实：这篇东西不该被直接翻译成 `5m/15m` 上的固定动作表
为了避免把论文写成空话，我做了一个 **lightweight crypto portability probe**：
- 市场：Binance USDⓈ-M public klines
- 周期：`15m` / `5m`
- 币种：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 对照：
  - 原始 `TSM`
  - 论文后半段更贴近现代样本的 `MTSM-S2`
- 成本代理：每次仓位变动按 **3 bps** turnover cost 扣减
- 注意：这是最小实验，不是严格逐项复刻 paper 的日频组合回测

### 6.1 `15m` 上的 first verdict：overlay 并没有自动带来增益
几个最值得记住的数：

#### BTCUSDT `15m`
- `J=96, n=20` 原始 TSM：
  - **net return +2.76%**
  - **Sharpe 1.83**
- 同参数 `S2` overlay：
  - **net return -4.69%**
  - **Sharpe -2.94**

#### ETHUSDT `15m`
- `J=30, n=5` 原始 TSM：
  - **net return +9.76%**
  - **Sharpe 4.45**
- 同参数 `S2` overlay：
  - **net return -2.41%**
  - **Sharpe -0.92**

#### SOLUSDT `15m`
- `J=30, n=5` 原始 TSM：
  - **net return +0.36%**
  - **Sharpe 0.42**
- 同参数 `S2` overlay：
  - **net return -3.41%**
  - **Sharpe -1.42**

#### BNBUSDT `15m`
- 两边都偏弱，但 `S2` 更差。

### 6.2 `5m` 上的 verdict：有些币上能缓和亏损，但整体仍谈不上可直接上线
例如：

#### BTCUSDT `5m`
- `J=60, n=15` 原始 TSM：**Sharpe -2.62**
- `S2` overlay：**Sharpe -0.44**

它在 BTC 5m 上确实把烂结果变得没那么烂；
但这离“可直接上线”还很远。

#### ETHUSDT `5m`
- `J=60, n=15` 原始 TSM：**Sharpe 6.94**
- `S2` overlay：**Sharpe 0.32**

在 ETH 这里，overlay 反而明显拖后腿。

### 6.3 这组 probe 真正说明了什么
不是“论文错了”，而是：

1. **paper 的动作表是市场结构条件化的，不是跨市场常数。**
   中国商品期货 2013–2019 的 Region 2/4 动作，不应该无脑抄到 2026 crypto `5m/15m`。
2. **更值得迁移的是“反转识别框架”，不是 S1 / S2 的硬编码动作。**
3. **对 crypto short-cycle desk，这层东西更像 veto / size-down / flat gate，而不是 reverse-all 的机械反手器。**

这点非常关键。
如果硬抄论文最显眼的“反手”动作，极可能把一个本来可用的 trend 母体搞得更差。

---

## 7. 对当前项目最有价值的落地方向
### 7.1 正确定位：shared reversal-risk overlay
我会把它定位成：
- 可服务于至少 2 类 raw alpha 的 **shared gate / overlay**
  - breakout continuation
  - trend-pullback continuation
  - funding-cycle continuation
  - path-shape continuation

### 7.2 比较推荐的 crypto 改写方式
不要直接照抄 “Region 2 做多 / Region 4 做空” 这种硬动作。
更合理的是三层版本：

#### 版本 A：veto-only
- 原始 trend signal 先照常产出；
- 若 `(UPM, LPM)` 落入高风险区域，**只做 flat / skip**；
- 不做反手。

这是最稳妥、也最值得先测的版本。

#### 版本 B：size-down
- 原始 signal 不取消；
- 但当 `UPM` / `LPM` 尾部不对称升高时，仓位从 `1.0x` 降到 `0.5x` 或 `0.25x`。

这更贴近它在 paper 里的真正价值：
**控制 reversal tail risk**，而不是赌每一次都能精确反向。

#### 版本 C：hold-shortening
- 趋势信号仍可进场；
- 但 overlay 告诉你这段更像 late-trend / whipsaw zone 时，把 hold horizon 缩短。

这个版本尤其适合 `5m/15m`。

---

## 8. 最小可复现实验怎么做
### 8.1 数据
- Binance USDⓈ-M `1m/3m/5m/15m` klines
- 只需 OHLCV
- 公开可得，更新频率足够

### 8.2 母体 alpha
先不要从 0 开始发明，用现有 desk 更常见的 trend 母体：
- `ret_8 ~ ret_32` sign continuation
- breakout above rolling high
- VWAP reclaim continuation
- trend-pullback continuation

### 8.3 overlay 特征
在 bar returns 上构造：
- `UPM_n = mean(r^2 * 1[r>0])`
- `LPM_n = mean(r^2 * 1[r<0])`
- rolling quantiles of `UPM_n` / `LPM_n`
- `up_tail_only`, `down_tail_only`, `double_tail`

### 8.4 最小对照组
至少测 4 组：
1. 原始 alpha
2. alpha + veto-only
3. alpha + size-down
4. alpha + reverse-all

如果 reverse-all 最差，而 veto-only / size-down 更稳，
那就说明这篇 paper 对 crypto 的正确迁移方式是 **risk overlay**，不是 **反手 alpha**。

---

## 9. 下一步怎么测
这是本轮最重要的落地部分。

### 9.1 先别测“独立 partial-moment 策略”，先测“它能不能救现有 trend 母体”
优先挂到下面两类现有 raw alpha 上：
1. `trend-up breakout / continuation`
2. `path-shape / single-direction drift`

### 9.2 动作优先级按这个顺序来
1. **flat veto**
2. **size-down**
3. **time-stop shortening**
4. 最后才是 **reverse-all**

理由很简单：
paper 在原生市场里能反手成功，
不代表 crypto 短周期里 mechanical reverse 也成立。

### 9.3 参数映射建议
不要硬照日频 `30-day / 5-day`。
对 short-cycle 可先测：
- 母体 lookback：`8 / 16 / 32 / 64` bars
- partial-moment window：`4 / 8 / 12 / 20` bars
- quantile：`0.7 / 0.8 / 0.9`

### 9.4 指标别只看 Sharpe
重点看：
- net Sharpe
- max drawdown
- whipsaw cluster 内的 PnL
- reversal day / event window 下的条件收益
- turnover 是否因为 overlay 反而爆炸

---

## 10. 我对这篇东西的最终评级
### 10.1 作为“新 raw alpha”
**不通过。**
因为它本质不是独立 alpha，而是附着在 TSM 母体上的 risk / reversal overlay。

### 10.2 作为“可迁移的 shared gate / overlay”
**值得进研究池。**
原因有三：
1. 逻辑非常清楚；
2. 输入特征便宜；
3. 目标问题明确——就是减少 trend alpha 在 reversal 段的净值塌陷。

### 10.3 作为“可直接照搬到 crypto `5m/15m` 的现成动作表”
**不通过。**
本轮 lightweight probe 已经很明确：
- 原始 paper 的 `S2` 式硬动作表，直接压到 Binance short-cycle，并没有稳定增益；
- 真正值得搬的是 **partial-moment asymmetry 这套状态识别框架**。

---

## 11. first verdict
一句话：

> **这篇 paper 值得保留，但该保留的是“partial-moment reversal veto 框架”，不是它在中国商品期货上的固定反手动作表。**

如果放到当前 `/root/clawd/jerry/momentum` 的研究池里，我会这样标：
- **主题类型：overlay**
- **服务对象：trend / breakout / continuation raw alpha**
- **当前 verdict：适合做 shared veto / size-down 层；不适合直接当独立主策略，更不适合无脑 reverse-all**

---

## 12. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-18_0508_partialmoment-tsmom-reversal-overlay.md`
- portability summary：`reports/artifacts/quant_digests/2026-04-18_partialmoment_tsmom_crypto_probe_summary.json`

---

## 13. 来源
1. **Liu, Z., Lu, S., & Wang, S. (2021). _Asymmetry, tail risk and time series momentum_. International Review of Financial Analysis, 78, 101938.**
   - DOI: <https://doi.org/10.1016/j.irfa.2021.101938>
   - Readable URL: <https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002581.html>
   - Full-text landing page: <https://centaur.reading.ac.uk/100824/>
   - PDF: <https://centaur.reading.ac.uk/100824/1/FINANA-D-21-00329-R1.pdf>
2. **IDEAS/RePEc abstract page**
   - <https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002581.html>
3. **This round lightweight crypto portability probe**
   - Binance USDⓈ-M public klines API (`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`, `15m/5m`)
