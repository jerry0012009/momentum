# 别再把 EMA / PSAR raw alpha 写成“均线自己下单”：新 ApexTrend repo 里，EMA 真正值钱的是三段分工，PSAR 甚至根本没上场
- 时间：2026-03-23 02:34 UTC
- 类型：GitHub 仓库
- 主题标签：ema/psar/raw-alpha/breakout/context-gate/momentum-confirm/fast-exit/repo/crypto/5m/15m/fibonacci
- 证据类型：GitHub README + Freqtrade 策略代码

## 1) 这次看了什么
这轮不继续泛找“新指标”，而是直接回答 `EMA / PSAR raw alpha focus` 现在最该收的一句：
**EMA 到底更像触发器，还是更像角色分工明确的辅助骨架？**

我看的对象是一个很新的仓库：**onixenix / fortunalabs (2026)**，里面的主策略叫 **ApexTrend**。它不是 15m crypto 成品，而是一个 `4h` Binance futures 的 Freqtrade breakout 策略；但 repo 里有个非常适合我们 desk 的旁支结论：
**同一个系统里，EMA 被拆成了 3 个完全不同的角色；真正负责“开火”的，仍然是 breakout。**

## 2) 核心结论（先说人话）
- **一句话结论：** 对当前 desk 来说，EMA 更像该被拆成 `macro gate + momentum confirm + fast exit`，而不是继续幻想它自己就是 15m 的 raw alpha 主触发。  
- **一句话证据：** `ApexTrend.py` 的入场是 **`rising EMA236` + `EMA10 > EMA38` + `35-bar high breakout` + `volume > 0.8 × avg20`**，出场则是 **`close < EMA13`**；也就是说，EMA 负责环境、确认、退出，但 **breakout 仍是主触发**，而且 **PSAR 在整套逻辑里根本没出现**。

### 关键数据点（都来自 repo 本身）
1. README 声称其 `4h` 回测（`2025-06` 到 `2026-03`）为：
   - `+37.36%` return
   - `54` 笔交易
   - `53.7%` win rate
   - `5.51%` max drawdown
   - `Sharpe 1.63 / Profit Factor 3.32`
2. 代码里 EMA 被明确拆成三层：
   - `EMA236 + slope>0`：宏观顺风门
   - `EMA10 > EMA38`：动量确认
   - `EMA13`：快节奏退出
3. 真正的 entry 事件不是 EMA cross，而是：
   - `close > rolling 35-bar high`
   - 同时要求 `volume > 0.8 × 20-bar mean`

> 这比“再调一组 EMA 参数”更有用，因为它在角色上已经把事情说透了：**EMA 可以很重要，但不一定该负责按扳机。**

## 3) 为什么和当前项目有关
这题不是离开三条收口线，而是在直接回答其中一条最卡的判断：

- **EMA / PSAR raw alpha focus**：最直接。repo 给出的读法不是“换一组更神的 EMA/PSAR 参数”，而是 **先承认 breakout 是触发，EMA 是分层辅助**；
- **Fibonacci confirmation / retest_hold**：也能借这套角色分工。`Fib retest_hold` 更像只该在 `HTF EMA rising + fast/slow EMA aligned` 的顺风环境里做 long-side 质量确认；
- **V3 breakout-short / follow-up**：反而提醒我们不要镜像滥用。这个 repo 是 **long-only**，所以它更像 long-side 角色判断证据，不能老实地直接翻成 short-side shared gate。

换句话说：这轮最值钱的不是 repo headline 收益，而是它把 **EMA 的岗位职责** 讲清了。

## 3.5) 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：`35-bar breakout`
- regime：`close > rising EMA236`
- filter / veto：`EMA10 > EMA38` + `volume > 0.8 × avg20`
- risk / sizing / execution overlay：`close < EMA13` 快速退出；另有极宽 `ROI / stoploss` 安全网，但更像尾部保护，不像主出场

## 4) 可复刻的最小实验
### 研究假设
对 `15m` desk 来说，**把 EMA 从“触发器”改成“分层 gate / confirm / exit”**，大概率比继续硬救 `EMA / PSAR raw trigger` 更诚实。

### 一个可计算定义
先不要同时改一切，只做 **角色审计实验**：
- `gate_htf = (close_1h > EMA200_1h) & (EMA200_1h - EMA200_1h.shift(5) > 0)`
- `confirm_ltf = EMA10_15m > EMA38_15m`
- `fast_exit = close_15m < EMA13_15m`
- `base_trigger` 先固定为当前已有事件流之一（优先 `EMA / PSAR raw alpha` 或 `breakout-short` 的原始触发）

### 最小回测切口
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`15m` 主框架；若要更像 repo，可把 `1h` 只作为 context
- 样本：近 `180d`
- 对照组：
  - `A` = 当前 raw trigger baseline
  - `B` = `A + gate_htf`
  - `C` = `B + confirm_ltf`
  - `D` = `C + fast_exit`（替换或先并联当前 PSAR/固定退出）

### 最该先看哪 1~2 个指标
- `post-cost expectancy`（先按 `10bps` round-trip）
- `max_drawdown / median hold bars`

我最想先验证的一句是假设：
> **如果 `D` 只是在少交易的同时没有改善成本后收益，那 EMA 依旧只是“看起来有逻辑”；但如果 drawdown 和 hold time 明显改善，说明 EMA 更适合作为角色层，而不是 alpha 层。**

## 5) 风险与保留意见
- 这是 **repo intake**，不是正式 replication；
- repo 主框架是 `4h`、`long-only`、`54` 笔交易，和我们 `5m/15m` desk 不同，不能照抄参数；
- README 的绩效口径来自作者自报，且策略说明写明做过 `500-epoch hyperopt`，**过拟合风险很高**；
- 它的 `ROI 54.4% / stoploss -26.6%` 极宽，说明绩效更可能主要来自大趋势过滤，而不是 exit 精细度；
- **PSAR 完全缺席** 本身是启发，但也意味着这篇材料更适合回答“EMA 应扮演什么角色”，不适合直接替 PSAR 正名或判死刑。

## 6) 来源
1. **onixenix. (2026). _fortunalabs / ApexTrend_. GitHub Repository.**
   - Authors / Org: onixenix
   - Year: 2026（repo `created_at = 2026-03-19`）
   - Title: ApexTrend — 4h trend-following breakout strategy for crypto futures
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/onixenix/fortunalabs>
   - Repo URL: <https://github.com/onixenix/fortunalabs>

2. **onixenix. (2026). _ApexTrend.py_. GitHub source file.**
   - Authors / Org: onixenix
   - Year: 2026
   - Title: ApexTrend.py
   - Venue: GitHub (source file)
   - DOI: N/A
   - Readable URL: <https://github.com/onixenix/fortunalabs/blob/main/ApexTrend.py>
   - Repo URL: <https://raw.githubusercontent.com/onixenix/fortunalabs/main/ApexTrend.py>
   - 关键实现点：`EMA236 slope > 0`、`EMA10 > EMA38`、`hh35 breakout`、`volume > 0.8 × avg20`、`close < EMA13` exit。

## 7) 产出文件（本轮）
- `research/quant_digests/2026-03-23_0234_apextrend-ema-role-split-breakout-primary.md`
