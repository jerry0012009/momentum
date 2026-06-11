# 别把这份 2025 新 repo 只读成日频动量作业：对 short-cycle desk，更该先测的是「短窗收益差 × quote-volume ratio × AVR 连击确认」这条 volume-confirmed XS momentum raw alpha

- 时间：2026-04-01 12:48 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/cross-sectional/trend/momentum/volume-confirmation/abnormal-volume-ratio/liquidity-flow/binance/spot/perpetual/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2025 GitHub notebook source audit（`README.md` + `CX_MomXVol_StatArb.ipynb`）+ supporting 2025 GitHub README cross-check

- 主题类型：raw alpha
- 基础 alpha：横截面里**近期相对更强、且量能比过去基线更热的币，更容易继续跑赢；近期相对更弱、且量能确认不足的币，更容易继续落后**，因此可做 `long strong-with-flow / short weak-without-flow` 的 XS continuation
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是“volume filter 本身”，也不是“流动性好所以更容易涨”这种解释层。**

它的 alpha 本体是：
- 先做一条**横截面 momentum / continuation** 排名；
- 再用 `short/long quote-volume ratio` 和 `AVR hit` 去确认这条 momentum 不是空转；
- 最后只交易**强且有流、弱且没流**的那一端。

翻成人话：**这是一条“量能确认过的横截面 continuation raw alpha”**，不是纯 filter，更不是只有 overlay 没有 alpha 本体。

## 2. 为什么这轮值得写，而不是继续补一个只会服务别人的 gate
最近 intake 里 mean reversion / pairs / basis / funding 已经不少，但**纯 continuation / trend 的 raw-alpha 素材池还可以再补**。这份 2025 repo 的价值，刚好在三个点：

1. **raw alpha 清楚。** 它不是只给一个 risk shell，而是给了完整 signal 骨架。
2. **数据负担极低。** 只需要公开 OHLCV / quote volume，不依赖 funding、链上标签、L2 档位或私有订单流。
3. **非常适合做 ablation。** 你可以很快拆成：
   - 只有动量本体；
   - 动量 × volume ratio；
   - 动量 × volume ratio × AVR 连击确认；
   然后直接看哪一层真有增量。

所以它对当前 desk 的意义，不是“又一个日频 notebook”，而是**补一条低数据门槛、可快速压缩到 `15m/5m` 的 XS continuation raw alpha**。

## 3. 这次看了什么
### 3.1 主来源（repo）
- **Author / Repo owner**：tim7park
- **Year**：2025（repo 页面显示最新提交在 2025-10-27 UTC）
- **Title / Repo**：*Crypto-Stat-Arb-CX-Momentum-x-Volume*
- **Repo URL**：https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume
- **Readable URL**：https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume
- **关键文件**：`README.md`、`CX_MomXVol_StatArb.ipynb`

### 3.2 supporting cross-check
- **Author**：Titouan Vasnier
- **Year**：2025
- **Title / Repo**：*Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies*
- **Repo URL**：https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies
- **Readable URL**：https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies
- **用途**：不是主线 alpha 定义来源，而是用来交叉确认“crypto 里的 volume-adjusted momentum 不是单一 repo 的偶然产物”

## 4. 主 repo 里到底怎么定义这条 alpha
### 4.1 数据与 universe
- **市场**：Binance US spot，USDT 计价币池
- **Universe**：77 个币
- **频率**：`1d`
- **样本区间**：自 `2020-01-01`
- **原始字段**：OHLCV + `quote_volume`

### 4.2 核心 signal
repo 的主体不是简单的“过去 N 天涨得多就买”。它的骨架是：

1. 计算短窗和长窗收益均值：
   - `mu_short = rolling_mean(ret, short_window)`
   - `mu_long = rolling_mean(ret, long_window)`
2. 用长窗波动做标准化：
   - `sigma = rolling_std(ret, long_window)`
3. 形成动量强弱分数：
   - `score = sqrt(short_window) * (mu_short - mu_long) / sigma`
4. 再乘上量能比：
   - `vol_signal = qvol_ma_short / qvol_ma_long`
   - `port = score * vol_signal`

也就是说，这份 repo 真正在测的是：
**“短窗相对长窗更强、而且最近 quote volume 也明显 hotter 的币，是否更值得继续持有？”**

### 4.3 AVR 连击确认
repo 里最值得 desk 偷走的，不只是 volume ratio，还有这层 admission：

- `adv_med = rolling_median(qvol, 20)`
- `avr = qvol / adv_med`
- 定义 `avr > 2` 为一次强流量 hit
- 要求最近 `5` 天里至少有 `3` 次 hit，才保留仓位

翻成人话：**不是单日放量就够，而是要连续几次放量，才把它当作可交易 continuation。**

### 4.4 仓位与执行
- 源 repo 是**long-only**：只保留 `port > 0` 的币
- 再做：
  - `tanh` 压缩极端值
  - 横截面归一化
  - `lag_shift` 后再乘后续收益
- 最终给出一条聚合的 daily 策略收益曲线

### 4.5 最优 gross 参数（源 repo）
notebook 打印出的 best gross combo：
- **short window**：`3`
- **long window**：`150`
- **lag shift**：`11`
- **gross Sharpe**：`1.3608`

注意：**这个参数不能机械按比例照搬到 `15m/5m`。** desk 该拿走的是“结构”，不是“3/150/11 这个数字本身”。

## 5. 最值得拿走的硬数据点
### 5.1 主 repo：full sample 不是弱信号
主 repo README / notebook 给出的全样本结果：
- **Gross Sharpe**：`1.36`
- **Alpha t-stat vs BTC**：`2.27`
- **BTC buy-and-hold Sharpe**：`1.09`

这至少说明一件事：**signal 本体不是没有。**

### 5.2 walk-back 没完全塌
repo 给的 walk-back / earlier regime 结果：
- **2020–2023 walk-back Sharpe**：`1.29`
- **Alpha t-stat**：`1.84`

这不是“某一个近端窗口刚好撞上牛市”的完全偶然结果。

### 5.3 最近样本有衰减，但没衰减到完全没信息
repo 对 2023–2025 的描述：
- **alpha t-stat**：`1.00`

它说明的是：**edge 在衰减，不能神化；但也没衰减到完全不用看。**

### 5.4 supporting repo 给了第二条旁证
Titouan Vasnier 的 2025 repo（weekly crypto momentum）给出的 OOS 结果：
- **XS-MOM Sharpe**：`0.68`
- **Weekly volume-adjusted Sharpe**：`0.81`
- **Vol-weighted blend Sharpe**：`1.57`
- **交易成本**：`20 bps` 每次再平衡

它不是同一条信号，但至少说明：**在 crypto 横截面里，把 volume 放进 momentum 里，不是完全离谱的孤例。**

## 6. 对当前 desk，最该拿走的不是 long-only 日频，而是这套可迁移骨架
我认为这轮真正值得 intake 的，不是“77 币日频 long-only 最优参数”，而是下面这三件可复用组件：

1. **fast-minus-slow return spread**
2. **short-vs-long quote-volume ratio**
3. **重复 abnormal-volume hit 的 admission**

这套骨架的优点是：
- 数据全公开；
- 容易先做最小实验；
- 很适合压到 `15m` 做 raw alpha first verdict；
- 还能自然拆成 raw alpha vs confirmation 的 ablation。

## 7. 对 `1m / 3m / 5m / 15m` 的 desk 化读法
### 7.1 不要硬按时间比例照抄 3/150/11
源 repo 是日频、长窗、long-only；我们要迁到的是短周期 perp desk。真正该保留的是：
- **短窗相对长窗更强**
- **最近量能相对过去更热**
- **这种热不是 1 根 bar 偶然爆出来，而是有连续 hit**

### 7.2 一个更诚实的 `15m` first-pass
建议先做这个最小版：

- **Universe**：同 venue top `12~20` 个 liquid perps
- **Bar**：`15m`
- **动量本体**：
  - `mu_short`: 最近 `3` 或 `6` 根 bar 的收益均值
  - `mu_long`: 最近 `96` 根 bar（约 1 天）或 `192` 根 bar（约 2 天）的收益均值
  - `sigma_long`: 同长窗标准差
- **分数**：
  - `score_i = ((mu_short_i - mu_long_i) / sigma_long_i) * (qvol_ma_short_i / qvol_ma_long_i)`
- **AVR gate**：
  - `avr_i = qvol_i / median(qvol_i, 96)`
  - 先试 `avr > 1.8` 且最近 `4` 根里至少 `2` 次 hit
- **组合**：
  - long top `20%`
  - short bottom `20%`
  - side-neutral / dollar-neutral
- **持有**：`4 / 8 / 12` 根 bar（1h / 2h / 3h）

### 7.3 为什么我建议把源 repo long-only 改成 long-short
因为当前 desk 要的是**独立 raw alpha**，而不是被大盘 beta 吞掉的长偏置 notebook。 

源 repo 的 long-only 设计可以保留做对照，但真正适合 intake 的版本应优先是：
- **横截面对称**
- **perp 可执行**
- **明确 after-cost**

否则你很难判断自己赚的是 signal，还是恰好踩中了市场方向。

### 7.4 `5m` 版本可以更快，但别一上来就卷到 `1m`
如果 `15m` first-pass 有信息，再下钻到：
- `5m` bar
- `mu_short = 6 / 12`
- `mu_long = 288`（约 1 天）
- hold `12 / 24 / 36` 根

但我不建议第一刀就上 `1m`，因为那样更容易把研究资源耗在 execution noise，而不是先判断 alpha 本体有没有。

## 8. 可以怎样落成完整策略骨架
### 8.1 Entry
每个 rebalance 时点：
1. 计算每个币的 `score`
2. 计算 `AVR gate`
3. 只在通过 gate 的币里做横截面排序
4. long top tail，short bottom tail
5. next bar 开始执行

### 8.2 Exit
第一轮别过拟合，先用最朴素的：
- 固定持有 `1h / 2h / 3h`
- 或者 `score` 翻符号就提前平仓

优先先验证：**固定时间退出下，after-cost 还能不能活。**

### 8.3 Sizing
建议先用三层就够：
- **signal layer**：每侧 equal-weight 或 inverse-vol weight
- **risk layer**：单币 notional cap、单侧 gross cap、组合 gross cap
- **execution layer**：participation cap（例如近 `1h` 成交额的 `x%`）

### 8.4 Risk / veto
最值得先加的是：
1. **极端新闻 / 上线 / 下线 veto**：防止把 event spike 当 continuation
2. **组合 beta cap**：避免横截面策略被 market direction 绑架
3. **最小流动性门槛**：top-of-book 深度或近 `n` bar dollar volume 不够就不做
4. **同主题拥挤控制**：与现有 trend / breakout sleeve 高相关时自动减仓

### 8.5 Cost
必须至少跑三档：
- maker-ish
- mixed
- taker-heavy

如果一个版本只有在理想 maker 成本下才勉强活，那它就不是 ready，只能算候选。

## 9. 最小可复现实验（直接面向当前 desk）
### 实验 A：`15m` liquid-perp volume-confirmed XS momentum
- **标的池**：BTC, ETH, SOL, BNB, XRP, ADA, DOGE, LINK, AVAX, LTC, BCH, DOT
- **bar**：`15m`
- **score**：`(mu_short - mu_long) / sigma_long × volume_ratio`
- **gate**：`avr > 1.8` 且近 `4` 根至少 `2` 次 hit
- **组合**：long top `20%` / short bottom `20%`
- **持有**：`4 / 8 / 12` 根
- **回答问题**：volume ratio + AVR 是否真的给 XS continuation 带来净增量？

### 实验 B：ablation ladder
同样的 universe / 持有 / 成本，只比较三档：
1. **纯 momentum 本体**
2. **momentum × volume ratio**
3. **momentum × volume ratio × AVR gate**

这是这条线最该先跑的实验，因为它能直接回答：**增量到底来自哪里。**

### 实验 C：`5m` faster transfer
- `5m` bar
- `mu_short = 6 / 12`
- `mu_long = 288`
- hold `12 / 24 / 36` 根
- 先只测 top liquidity bucket

目的不是立刻上实盘，而是判断：**压快之后 edge 会增强，还是只会把 turnover 和滑点同时放大。**

## 10. 下一步怎么测
建议顺序非常简单：

1. **先只用 OHLCV + quote volume 重建 signal**
2. **先跑 ablation ladder**：本体 / +volume ratio / +AVR gate
3. **再跑 cost ladder**：maker / mixed / taker
4. **再看 edge 分布**：
   - 按 liquidity bucket 分层
   - 按 market regime 分层
   - 按 top/bottom tail 宽度分层
5. **如果只有最液体 bucket 还能活**
   - 就把它收敛成一个可部署 sleeve
6. **如果 gross 都不稳定**
   - 直接 park，不要继续在 execution 上过度打磨

一句话说：**先确认“volume confirmation 到底有没有真增量”，再决定要不要把它升格成短周期主线。**

## 11. 风险与局限
1. 主证据来自 **GitHub repo，不是 peer-reviewed paper**；可信度够做 intake，但不该过度神化。
2. 主 repo 是 **daily spot long-only**；迁到 `15m/5m` perp long-short 本身就是 transfer hypothesis，必须实测。
3. AVR gate 可能会把**事件驱动 spike / 上币异动**和真正的 continuation 混在一起。
4. repo 没有给出很细的实盘冲击成本处理；短周期版本更不能忽略 turnover。
5. 若 universe 太宽，很容易把“量能更热”错误地读成“更适合冲进去”，最后被容量反噬。

## 12. 一句话结论
这份 2025 repo 最值得 desk intake 的，不是那组 long-only 日频参数，而是：**把“短窗强于长窗”的 XS momentum，本体再乘上 volume ratio，并用 AVR 连击确认后，可能形成一条数据门槛很低、适合先做 `15m signal + 5m execution` 的 continuation raw alpha；下一步最该做的是 ablation，而不是先神化它。**

## 13. 来源链接
1. **tim7park. (2025). _Crypto-Stat-Arb-CX-Momentum-x-Volume_. GitHub repository.**  
   - Repo URL: https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume  
   - Readable URL: https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume  
   - Key file: `CX_MomXVol_StatArb.ipynb`
2. **Titouan Vasnier. (2025). _Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies_. GitHub repository.**  
   - Repo URL: https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies  
   - Readable URL: https://github.com/TitouanVasnier/Quant-Research-Project-TS-VS-XS-Momentum-Crypto-Strategies
