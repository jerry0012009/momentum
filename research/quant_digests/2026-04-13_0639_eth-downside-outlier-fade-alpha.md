# 别把这篇 2021 overreaction 论文只读成“极端事件异象”：对 short-cycle desk，更该先测的是「ETH downside outlier fade × Europe-hours veto」这条 raw alpha

- 时间：2026-04-13 06:39 UTC
- 类型：2021 论文摘要/元数据复核（OpenAlex + Crossref）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/single-asset/mean-reversion/event-driven/outlier-shock/overreaction/eth/btc/session-veto/europe-hours/binance-perpetual/15m/60m/120m/paper/public-data/cost/risk
- 证据类型：论文证据 + 公共数据 portability probe

- 主题类型：raw alpha
- 基础 alpha：**当 `ETHUSDT` 在 `15m` 上出现足够极端的 downside outlier（第一版先定义为：当前 `15m` log return `<= -3σ`，其中 `σ` 为过去 `672` 根 `15m` 收益的滚动标准差）时，后续 `60~120m` 更像 overreaction bounce，而不是继续线性下坠；但 `08:00–16:00 UTC` 这段默认先 veto。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = “极端下跌后的定向反打”。** 对当前 desk，更有交易意义的不是泛泛地讨论“crypto 有没有 overreaction”，而是把它翻成一个可执行的事件型 raw alpha：**ETH 在 `15m` 级别出现足够深的 downside shock 后，下一小时更容易回补。**

翻成人话：
- 不是平时所有下跌都去抄底；
- 只盯 **足够极端** 的短时冲击；
- 也不是全市场通用、全天候通用；
- 目前最像能落到 desk 上的，是 **ETH 单币 downside shock fade**，而不是把 BTC / ETH / Tether 的论文 headline 原样照抄。

所以这条线不是 `filter / regime / overlay`。Europe-hours veto 只是后面补上的 admission/filter，**alpha 本体仍然是 downside outlier fade**。

## 2. 这次看了什么

### 主来源（paper）
- **Authors：** Mark Schaub
- **Year：** 2021
- **Title：** *Outlier Events in Major Cryptocurrency Markets: Is There Evidence of Overreaction?*
- **Venue：** *The Journal of Wealth Management*
- **DOI：** <https://doi.org/10.3905/jwm.2021.1.155>
- **Readable URL：** <https://doi.org/10.3905/jwm.2021.1.155>
- **Metadata used：**
  - Crossref: <https://api.crossref.org/works/10.3905/jwm.2021.1.155>
  - OpenAlex: <https://api.openalex.org/works/https://doi.org/10.3905/jwm.2021.1.155>
- **Repo URL：** N/A

这篇 paper 从摘要层面给出的关键信息很直接：
- 对 **negative outlier events**，**Bitcoin 和 Ethereum** 都出现了显著 reversal，说明极端负冲击后存在 overreaction；
- 对 **positive outlier events**，结果更混：**Ethereum** 更像 continuation，**Tether** 才出现 reversal；
- 也就是说，它不是一句“crypto 都会反转”能概括的对称规律，而是 **sign split + asset split** 的事件响应。

对我们 desk 来说，最值得抽出来的不是 Tether，也不是“所有正负极端都做”，而是：

> **把 paper 的 negative-overreaction 分支，重写成 ETH `15m` downside shock fade。**

## 3. 为什么这条分叉值得进当前研究池

它满足这轮 intake 最重要的几条：

1. **一句话能说清 base alpha。**
   - ETH 短时极端下跌后，下一小时更像反打。
2. **可独立复现。**
   - 只要公开 `15m` K 线，不需要私有 order book 或外部付费数据。
3. **可直接写成完整策略壳。**
   - event definition / entry / exit / sizing / veto / cost 都能拆清楚。
4. **它补的是 raw alpha，不是再加一层解释。**
   - 最近池子里 pairs / carry / maker / cross-venue 很多；这条是更朴素但可直接交易的 **single-name event-driven mean reversion**。

## 4. desk 化重写：别复刻“论文里的三币事件研究”，先测最可交易的一条

我这轮没有尝试复刻 paper 的原始日频事件定义，而是先做一个更适合 `15m` perp desk 的最小翻译版：

### 信号定义（第一版）
对 `ETHUSDT`：
1. 用 `15m` close 计算 log return；
2. 用过去 `672` 根 `15m` 收益（约 `7d`）估计滚动波动；
3. 若当前 `15m` return `<= -3σ`，记为 **negative outlier event**；
4. 下一根 bar open 做多；
5. 分别测试 `60m`（4 bars）与 `120m`（8 bars）时间退出。

### 为什么先用这版
- `3σ` 是为了先抓“真极端”，不是普通回调；
- `7d` 波动窗够短，能适应 crypto 当前状态变化；
- `60m / 120m` 是因为 paper 的机制是 **overreaction 之后的回补**，而不是几秒级盘口反弹。

## 5. public-data portability probe：这条 downside-overreaction 分叉，在今天的 Binance `15m` perp 上还活着吗？

### 5.1 数据口径
- **市场：** Binance USDⓈ-M Perpetual
- **频率：** `15m`
- **样本：** `2025-10-01 ~ 2026-04-13 UTC`
- **标的：** `BTCUSDT / ETHUSDT`
- **事件：** 当前 `15m` log return `<= -z * rolling_sigma_672`
- **持有窗：** `60m / 120m`
- **执行：** 先按 next-bar close-to-close 近似；真正下单层下一步再细化到 `5m`

### 5.2 本轮本地 artifacts
- Probe script：`reports/artifacts/quant_digests/2026-04-13_major_neg_outlier_fade_probe.py`
- Probe summary：`reports/artifacts/literature/major_neg_outlier_fade_probe_2026-04-13.csv`
- Session split：`reports/artifacts/literature/major_neg_outlier_fade_session_splits_2026-04-13.csv`
- Cost ladder：`reports/artifacts/literature/major_neg_outlier_fade_costladder_2026-04-13.csv`

## 6. 最关键结果：paper 的“negative overreaction”在 ETH 上能转成 `15m` raw alpha，但必须做 session-level veto

### 6.1 先看不加 veto 的全样本
当我们只看 **negative `3σ` shock**：

#### `BTCUSDT`
- `60m`：**`170` 次**事件，平均 **`+0.74 bps` gross**
- `120m`：**`170` 次**事件，平均 **`-0.28 bps` gross**

这几乎可以视为：
> **BTC 全样本上不够干净，不能直接当主交易版本。**

#### `ETHUSDT`
- `60m`：**`170` 次**事件，平均 **`+10.08 bps` gross**，中位数 **`+10.68 bps`**
- `120m`：**`170` 次**事件，平均 **`+6.28 bps` gross**，中位数 **`+9.00 bps`**

这说明 paper 的 negative-overreaction 逻辑，放到今天的 `15m` perp 上，**ETH 比 BTC 明显更像可交易载体**。

### 6.2 真正值钱的是 session split
把负向 `3σ` shock 按事件发生时段拆开后，差异非常大：

#### `ETHUSDT`，`60m` 持有
- **Asia+US bucket（`00:00–08:00` + `16:00–24:00 UTC`）**
  - **`96` 次**事件
  - 平均 **`+36.66 bps` gross**
  - 中位数 **`+12.73 bps`**
  - 胜率 **`52.1%`**
- **Europe hours（`08:00–16:00 UTC`）**
  - **`74` 次**事件
  - 平均 **`-24.40 bps` gross**
  - 中位数 **`+8.90 bps`**
  - 胜率 **`51.4%`**

#### `ETHUSDT`，`120m` 持有
- **Asia+US bucket**：**`96` 次**，平均 **`+21.23 bps` gross**，中位数 **`+13.88 bps`**，胜率 **`57.3%`**
- **Europe hours**：**`74` 次**，平均 **`-13.10 bps` gross**，中位数 **`-17.14 bps`**，胜率 **`47.3%`**

这组数说明：
1. **ETH 的负向极端冲击并不是全天都该 fade；**
2. `08:00–16:00 UTC` 这段虽然中位数有时仍是正的，但 mean 被明显拖成负值，说明有 **left-tail continuation risk**；
3. 所以对 desk 来说，更正确的读法不是“ETH 暴跌就抄底”，而是：

> **ETH downside outlier fade + Europe-hours veto。**

### 6.3 BTC 只能作为弱对照，不该和 ETH 混做
同样的负向 `3σ` shock、`60m` 持有：
- `BTCUSDT` 全样本只有 **`+0.74 bps` gross**；
- 即便只看 Asia+US bucket，也只是 **`+11.97 bps` gross**；
- Europe hours 则是 **`-17.40 bps` gross**。

所以这条线当前更像：
- **ETH = 主交易腿**
- **BTC = 机制参照物 / veto 变量候选**

而不是“BTC/ETH 一起抄底”。

## 7. 成本视角：这条线不是零成本幻觉

对当前最像的版本：
- `ETHUSDT`
- negative `3σ` shock
- `60m` hold
- 只做 `00:00–08:00` 与 `16:00–24:00 UTC`

其 gross 平均约 **`+36.66 bps/次`**。

按 round-trip 成本压力测试：
- `4 bps`：约 **`+32.66 bps/次` net**
- `8 bps`：约 **`+28.66 bps/次` net**
- `10 bps`：约 **`+26.66 bps/次` net**

但这里要明确：
- 这个 mean 明显不是高胜率系统堆出来的；
- 胜率只有约 **`52%`**，说明更像 **少数大反打覆盖多数平庸小单**；
- 所以别把它误读成“稳定捡 30bp”——它更像 **convex bounce pocket**。

## 8. 策略拆解（必填）

- 方向属性：single-asset / mean-reversion / event-driven
- 基础 alpha：`ETH 15m downside outlier fade`
- regime：仅在 `15m` 负向极端冲击后触发；当前 probe 下默认避开 `08:00–16:00 UTC`
- filter / veto：第一版只有 **Europe-hours veto**；第二版再测是否叠加 `BTC` 同步负向极端冲击 veto
- risk / sizing / execution overlay：固定 notional 或 vol-scaling；真实执行层用 `5m` 做入场细化；成本先压 `4 / 8 / 10 bps`

## 9. 跟当前 `1m / 3m / 5m / 15m` desk 的关系

这条信号本体在 `15m`，但非常适合做成：
- **`15m` 事件识别**
- **`5m` 执行细化**

### 推荐第一版策略壳
- **Universe：** 先只做 `ETHUSDT`
- **Signal TF：** `15m`
- **Entry trigger：** `ret_15m <= -3 * rolling_sigma_672`
- **Execution TF：** `5m`
  - 事件 bar 结束后，不建议直接冲；
  - 第一版可先做 next-bar open；
  - 第二版再比较 `next 5m` 立即进 / `first 5m stop-down exhausted` 再进。
- **Exit A：** `60m`
- **Exit B：** `120m`
- **Sizing：** 每次固定风险预算；若事件 bar 自身 range 过大，则按 realized vol 缩仓
- **Cost：** 先压 `4 / 8 / 10 bps`

所以它不是全天普适抄底，也不是低频宏观 gate；它是一个**能直接服务 `15m` 主信号，再交给 `5m` 执行层打磨**的 raw alpha。

## 10. 下一步怎么测（必须项）

按优先级，我建议下一轮别继续泛化叙事，直接做这 `4` 个最小实验：

1. **执行细化**
   - 对 `ETHUSDT` 的负向 `3σ` 事件，比较：
     - `next-bar open` 进场
     - `next 5m` 立即进场
     - `next 5m` 先等一次 micro lower-low fail 再进
   - 先看 `60m` 退出谁最好。

2. **事件强度 sweep**
   - 同样只做 ETH，测 `2.5σ / 3.0σ / 3.5σ`；
   - 目标不是追最高 mean，而是找 **事件数 × post-cost mean × median** 最平衡的口袋。

3. **BTC 共振 veto**
   - 加一个条件：若同一根 `BTCUSDT` 也出现负向 `3σ` 冲击，则减少仓位或不做；
   - 这能回答：ETH bounce 更像 idiosyncratic overshoot，还是系统性 risk-off 下的假反弹。

4. **session 更细化**
   - 先把当前粗分桶拆成 `00–04 / 04–08 / 16–20 / 20–24 UTC`；
   - 看看 edge 是来自特定 handoff（Asia close / US open / US close），还是单纯“非欧洲时段”。

## 11. 风险与保留意见

- 这轮对 paper 的使用主要是 **abstract + metadata grounding**，不是全文表格复刻；
- 当前 probe 样本只有约 `6.5` 个月，仍然偏短；
- `3σ` 与 `7d` 波动窗是 desk portability 设定，不是 paper 原始唯一正统定义；
- 当前最强结果明显依赖 **session veto**，所以这不是“任何极端下跌都该抄”的粗规则；
- 胜率不高，说明 PnL 形态更偏 **fat-right-tail bounce**，要严防少数 continuation tail 把均值打坏。

## 12. 一句话结论

> 这篇 2021 overreaction paper 真正适合当前 short-cycle desk intake 的，不是泛泛地说“crypto 有极端事件反转”，而是从里面抽出一条更可交易的 raw alpha：**ETH 在 `15m` 上出现极端 downside outlier 后，下一小时存在可复验的反打 pocket；但 `08:00–16:00 UTC` 这段默认别碰。** 在 `2025-10-01 ~ 2026-04-13` 的 Binance public probe 里，这条 desk 化版本在 Asia+US bucket 上有 **`96` 次**事件、`60m` 平均约 **`+36.66 bps gross`**、`120m` 平均约 **`+21.23 bps gross`**，已经值得进下一轮 `5m` 执行细化清单。

## 13. 本轮产物

- 研究笔记：`research/quant_digests/2026-04-13_0639_eth-downside-outlier-fade-alpha.md`
- Probe script：`reports/artifacts/quant_digests/2026-04-13_major_neg_outlier_fade_probe.py`
- Probe summary：`reports/artifacts/literature/major_neg_outlier_fade_probe_2026-04-13.csv`
- Session split：`reports/artifacts/literature/major_neg_outlier_fade_session_splits_2026-04-13.csv`
- Cost ladder：`reports/artifacts/literature/major_neg_outlier_fade_costladder_2026-04-13.csv`

## 14. 来源
1. **Schaub, Mark (2021). _Outlier Events in Major Cryptocurrency Markets: Is There Evidence of Overreaction?_ The Journal of Wealth Management.**
   - DOI: <https://doi.org/10.3905/jwm.2021.1.155>
   - Crossref: <https://api.crossref.org/works/10.3905/jwm.2021.1.155>
   - OpenAlex: <https://api.openalex.org/works/https://doi.org/10.3905/jwm.2021.1.155>

2. **Binance USDⓈ-M Futures Public API**（本轮 portability probe 实际使用）
   - Kline / Candlestick Data: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
