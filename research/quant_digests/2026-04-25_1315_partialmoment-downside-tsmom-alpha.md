# 别把 Liu–Lu–Wang (2021) 只读成“又一篇 TSMOM 风控论文”：对 short-cycle crypto desk，更该先拆的是「downside-tail-dominant continuation」这条 raw alpha 候选

- 时间：2026-04-25 13:15 UTC
- 类型：2021 论文摘要页 / institutional repository full-text entry audit + Binance USDⓈ-M public-data portability probe（`15m`，`6` 个 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：**当最近一段下跌不只是“跌了”，而是明显由 downside tail 主导时，后续短窗口更容易继续顺着原方向漂，而不是立刻均值回复。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更像先做 `raw alpha + asymmetric router`）
- 主题标签：raw-alpha/single-asset/trend/momentum/downside-continuation/partial-moment/tail-risk/asymmetry/15m/5m/paper/public-data/cost/risk
- 证据类型：paper abstract/repository summary + public futures portability probe

## 1. 这次看了什么
这轮主材料是：

- **Liu, Zhenya; Lu, Shanglin; Wang, Shixuan (2021)**
- **Title:** *Asymmetry, tail risk and time series momentum*
- **Venue:** *International Review of Financial Analysis*, Vol. 78, 101938
- **DOI:** `10.1016/j.irfa.2021.101938`
- **Readable URL:** <https://centaur.reading.ac.uk/100824/>
- **DOI URL:** <https://doi.org/10.1016/j.irfa.2021.101938>

CentAUR 摘要页给出的作者原话很关键：他们不是单纯再讲一次“趋势有效”，而是研究**怎么用 partial moments（上/下偏矩）改进 TSMOM**；并发现 **TSMOM 的反转部分，可以被 tail-distributed upper / lower partial moments 部分预测**，而基于这些信息做的 rule-based 改写，在中国商品期货样本的样本外 Sharpe 有统计显著改善，且对不同 lookback 都稳。

## 2. 一句话结论
- **一句话核心结论：** 这篇东西最值得 desk intake 的，不是“partial moment 很学术”，而是更交易化的一句话：**不是所有 momentum 都一样；由 downside tail 主导的下跌，和普通顺势上涨相比，后续延续/反抽的赔率结构并不对称。**
- **一句话证明方式：** 论文用 commodity futures 的 upper/lower partial moments 去预测 TSMOM reversal 风险，并用 rule-based 改写拿到了更好的样本外 Sharpe；我再用 Binance 公共 `15m` 数据做 quick probe，结果也显示 **downside-conditioned continuation 比 upside-conditioned continuation 更接近可留样本**，但目前还不够厚到直接裸跑。

## 3. 为什么这轮值得做
这轮值得做，因为它虽然看起来像“趋势策略优化”，但实际上服务的是一个更基础的问题：

1. **base alpha 是清楚的。**
   不是抽象 filter，而是 **continuation / TSMOM 本体**。
2. **它补的是我们最近 raw alpha 池里相对少的一块：方向不对称。**
   很多短周期研究默认“涨和跌只是符号相反”，这篇提醒你：**尾部形状不同，后续 drift 也可能不同。**
3. **它天然适合拆成父信号 + 子执行。**
   父层用 `15m`/`1h` 判断“这次 move 是普通波动，还是 downside-tail-dominant”；子层再用 `5m` 做更便宜的入场和 time-stop。

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 顺势 / asymmetry-aware continuation
- 基础 alpha：recent-return continuation（TSMOM）
- regime：优先区分 downside-tail-dominant vs 普通波动 vs upside-tail-dominant
- filter / veto：若 upside-tail-dominant 的 continuation 明显更差，则默认不做 long momentum，或降权
- risk / sizing / execution overlay：
  - 父层 `15m` / `1h` 识别 tail asymmetry
  - 子层 `5m` 做 pullback entry / maker-first
  - 一律带 hard time-stop，避免“本该 continuation 结果横住耗死”

## 4. 这篇 paper 最值得拿走的点

### 4.1 他们不是在加一个“更花哨的波动率指标”
partial moments 翻成人话，就是把“上涨时的波动”和“下跌时的波动”拆开看，而不是只看一个总波动率。对交易员来说，这更接近：

- 这段走势是**平滑地走趋势**，还是
- 带着明显的 downside tail / panic leg 在跑。

### 4.2 论文真正有用的不是 headline，而是“reversal risk 可部分预测”
作者摘要页明确写了：
- TSMOM 的 reversal 可以被 upper/lower partial moments 部分预测；
- 用这个信息做 rule-based 改写，样本外 Sharpe 有统计显著提升；
- 不同 lookback 下都比较稳。

翻成人话：
> **不是去猜每次趋势都能走多久，而是先避开那些“更容易反噬”的 momentum。**

### 4.3 对 short-cycle desk，最自然的 desk 化读法是“downside continuation > upside continuation”先做不对称检验
我不会把它直接翻成“马上上线 partial-moment TSMOM”。
更适合我们的读法是：
- 先把 recent-return continuation 当 base alpha；
- 再问：**负向冲击 + downside-tail-dominant** 是否比正向冲击更适合做 continuation；
- 如果成立，它就能服务：
  - short-bias momentum sleeve
  - downside veto / upside veto
  - 作为现有 trend 策略的 asymmetric admission

## 5. 我做的最小 portability probe
### 5.1 数据与口径
- 数据源：Binance USDⓈ-M public `fapi/v1/klines`
- 公开性：公开可得，无需 API key
- 资产：`BTC / ETH / SOL / XRP / DOGE / ADA`
- 周期：`15m`
- 样本：最近约 `60d`
- 事件定义：
  - lookback = `16` 根（约 `4h`）
  - `score = 过去4h累计收益 / 过去4h realized-vol`
  - downside 事件：`score_z <= -1.2`
  - downside-tail gate：`lower partial moment / upper partial moment >= 1.4`
  - upside 事件对称定义
- 持有：`1 / 3 / 6` 根 `15m`
- friction：粗扣 `8 bps` round-trip

### 5.2 快检结果
先看 pooled 结果（所有币合并）：

- **downside baseline**：`hold 6` 平均约 **`-2.75 bps/笔`**
- **downside + partial-moment gate**：`hold 6` 平均约 **`-2.93 bps/笔`**
- **upside baseline**：`hold 6` 平均约 **`-6.88 bps/笔`**
- **upside + partial-moment gate**：`hold 6` 平均约 **`-6.26 bps/笔`**

这组数说明两件事：
1. **当前 pooled 口径下还不够厚，不能直接把它写成可上线 alpha。**
2. **但 downside 条线明显没 upside 那么差。** 换句话说，若要留样本，默认优先留 **short / downside continuation**，而不是 symmetric long-short continuation。

再看当前还能留意的 pocket：
- `DOGE` downside-tail-dominant × `hold 6`：平均约 **`+1.83 bps/笔`**
- `ADA` downside-tail-dominant × `hold 6`：平均约 **`+1.21 bps/笔`**

这还远不到“完整策略已成立”，但已经够说明：**不对称方向值得继续测。**

### 5.3 我的判断
这轮我不会把它升级成“可直接落地完整策略”。
更诚实的判断是：

> **它现在更像一条值得继续做 `downside-only continuation` 的 raw alpha 候选，而不是一条对称的 trend 主引擎。**

## 6. 对当前 desk 最值钱的落地方式
最值得复用的不是 partial moment 这个名词，而是下面这个骨架：

1. 先有一个普通 momentum / continuation 父信号；
2. 再用 `lower-vs-upper partial moment` 判断这次 move 的“尾部形状”；
3. 若是 downside-tail-dominant，则允许 short continuation；
4. 若是 upside-tail-dominant 或不明显，则默认降权、缩短 hold、甚至直接 veto。

这能同时服务：
- 单资产 short-bias continuation
- 现有 trend 信号的 asymmetric admission
- `15m` 父信号到 `5m` 子执行的方向选择

## 7. 下一步怎么测
下一步不要继续在当前 pooled 口径上抠参数，而应该直接做 3 个更 desk 化的最小实验：

### 实验 A：`1h` parent → `5m/15m` child 的 downside-only continuation
- 只保留 negative parent event；
- child 只做 short；
- 比较 `next-open` vs `5m pullback entry`；
- 先看：`post-cost avg bps`、`trade count`。

### 实验 B：把 partial moment 从“主信号”降为现有 trend alpha 的 asymmetric veto
- 裸 trend / continuation 一组；
- + downside-tail-admission 一组；
- + upside-tail-veto 一组；
- 看它到底是 alpha 本体，还是更像 shared gate。

### 实验 C：分 bucket 重测，不要再把 majors 混成一个 pooled 样本
- majors（BTC/ETH/SOL）单独一组；
- high-beta alts（DOGE/ADA/XRP）单独一组；
- 因为当前仅从 quick probe 看，edge 更像出现在高 beta 下跌腿，而不是大币普适成立。

## 8. 风险与保留意见
- 论文证据来自**中国商品期货日频**，不是 crypto `15m`；直接迁移一定会失真。
- 我这轮 public probe 只做了非常轻量的 recent-sample 检验，**当前 pooled 成本后仍为负**。
- partial moment 可能更适合做 **router / veto / downside-only sleeve**，而不是独立 always-on 策略。
- 若继续做，必须把 `trade count`、maker/taker 成本、以及 short-leg markout 单独拆开。

## 9. 本轮产物
- 研究笔记：`/root/clawd/jerry/momentum/research/quant_digests/2026-04-25_1315_partialmoment-downside-tsmom-alpha.md`
- 探针汇总：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_partial_moment_tsmom_probe_summary.csv`
- 事件明细：`/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_partial_moment_tsmom_probe_events.csv`

## 10. 来源
- Liu, Z., Lu, S., & Wang, S. (2021). *Asymmetry, tail risk and time series momentum*. *International Review of Financial Analysis*, 78, 101938.
- DOI: <https://doi.org/10.1016/j.irfa.2021.101938>
- Readable summary: <https://centaur.reading.ac.uk/100824/>
- Repository summary / abstract page used in this round: <https://centaur.reading.ac.uk/100824/>
