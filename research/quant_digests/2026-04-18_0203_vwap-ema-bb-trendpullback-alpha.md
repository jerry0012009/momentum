# 别把这份 2026 signal 平台只读成 TA 拼盘：对 short-cycle desk，更该先拆的是「trend-up VWAP reclaim × lower-band pierce」这条 5m raw alpha 候选

- 时间：2026-04-18 02:03 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `packages/strategies/src/entry/vwap-ema-bb.ts` + `packages/strategies/src/presets.ts` + `docs/SIGNAL_PROFITABILITY_RESEARCH.md`）+ Binance USDⓈ-M `BTCUSDT/ETHUSDT/SOLUSDT 5m` 近约 `41.6d` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**短周期 trend pullback continuation**——不是“看到 Bollinger 外侧就反手抄底/摸顶”，而是先要求 `EMA20 > EMA50` 且 `close > VWAP20`（或空头对称条件），只把 **顺短趋势的一次 lower-band / upper-band 瞬时穿刺** 当成回踩后的再入场信号；`VWAP` 和 `EMA` 在这里不是装饰，而是在回答“这是趋势内回踩，还是趋势反转开端”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（repo 这一支更像 **entry module**；alpha body 很清楚，但原生没有把 exit / sizing / friction 闭成 production shell，需我们自己补）
- 主题标签：raw-alpha / single-asset / trend-pullback / continuation / VWAP / EMA / Bollinger / BTC / ETH / SOL / 5m / 15m / repo / public-data / cost / risk
- 证据类型：源码规则 + public-data portability probe

先回答 base alpha：**说得清楚。它不是“VWAP/EMA/BB 三指标拼盘”，而是“短趋势已建立时，逆向 band 穿刺更像 pullback exhaustion，随后回到原方向”的 raw alpha 候选。** 这和纯 BB fade 不一样：纯 fade 是赌均值回归；这条线赌的是 **趋势里的短暂失衡修复后，继续沿原方向走一小段**。

## 1. 这次看了什么
主来源：
- **Author / Owner：** naimkatiman
- **Year：** 2026
- **Title：** *TradeClaw*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/naimkatiman/tradeclaw>
- **Repo URL：** <https://github.com/naimkatiman/tradeclaw>

关键源码文件：
- `packages/strategies/src/entry/vwap-ema-bb.ts`
- `packages/strategies/src/presets.ts`
- `README.md`
- `docs/SIGNAL_PROFITABILITY_RESEARCH.md`

这份 repo 表面上是“AI trading signals 平台”，README 也在讲多 preset、回测 UI、track record 页面。但真正值得 intake 的，不是它整个平台叙事，而是 `vwap-ema-bb.ts` 里那条已经写得很干净的 **entry module**：

- 多头：`EMA20 > EMA50`、`close > VWAP20`、且 **本 bar low 跌穿 lower BB**；
- 空头：`EMA20 < EMA50`、`close < VWAP20`、且 **本 bar high 刺穿 upper BB**；
- 置信度直接用 **穿刺深度 / band width** 来缩放；
- `presets.ts` 里把它明确描述成：
  - `Mean-reversion entries at BB extremes with VWAP and EMA trend confirmation.`

但代码真实在表达的，不是“反转本身”，而是：
> **趋势方向已经先被 `EMA20/EMA50 + VWAP20` 锁定，再用 band 穿刺抓 trend 内 pullback 的 exhaustion 点。**

这正是当前 desk 值得多存一类素材的原因：它不是又一条纯 anti-trend MR，也不是日线级慢信号，而是能直接映射到 `5m / 15m` 的 **短趋势回踩再启动**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的不是“VWAP + EMA + BB 三件套”，而是 **`trend-locked pullback continuation`** 这条 raw alpha 骨架：先确认局部趋势，再把一次反向 band 穿刺当成回踩透支点去顺原方向做。
- **一句话证明方式：** 我先做源码审计，确认 entry 逻辑确实是“趋势内 band pierce”，不是普通 BB fade；再把同一组规则迁到 Binance USDⓈ-M `BTC/ETH/SOL 5m` 近约 `12000` bars（约 `41.6d`）上做 public-data 快检。
- **最重要的 first verdict：** 这条线 **不是 broad-book 通杀型 alpha**。它更像 **asset / side selective pocket**，需要 admission layer，而不是裸跑全币双边。

### 2.1 源码层先给出的结论
`vwap-ema-bb.ts` 的信号定义非常短，但逻辑很明确：
- 多头不是“跌破下轨就买”，而是 **仍站在 VWAP20 上方、且 EMA20 仍压着 EMA50 向上时**，low 瞬时穿破 lower BB；
- 空头对称；
- 也就是说，alpha 本体不是 band，而是：
  1. `EMA20/EMA50` 给出局部趋势方向；
  2. `VWAP20` 给出“价格是否还在短期成交量均值上方/下方”；
  3. `BB pierce` 给出一次短暂失衡；
  4. 最终下注的是 **pullback exhaustion 之后回到原方向**。

这比单纯 `BB touch + EMA filter` 更贴近我们当前要补的池子：**trend / momentum / pullback continuation**，而不是再加一篇泛化 mean-reversion。

### 2.2 public-data portability probe 先给出的结论
我把 entry 规则直接迁到 Binance USDⓈ-M `5m`：
- 样本：`2026-03-07 10:15 UTC` 到 `2026-04-18 02:10 UTC`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 信号频率很低：
  - `BTC`：`9` 个 long、`12` 个 short，信号占比约 **0.175%**
  - `ETH`：`11` 个 long、`7` 个 short，信号占比约 **0.150%**
  - `SOL`：`14` 个 long、`18` 个 short，信号占比约 **0.267%**

先看 event-style future return：
- **BTC long**：
  - `+3 bars (15m)` 平均 **`+3.26 bps`**
  - `+6 bars (30m)` 平均 **`+3.55 bps`**
  - 到 `+12 bars (60m)` 反而转负到 **`-2.89 bps`**
- **BTC short**：
  - `+1 bar` 还有 **`+2.16 bps`**
  - `+3 / +6 / +12 bars` 分别掉到 **`-7.59 / -5.73 / -18.25 bps`**
- **ETH 双边**：基本都偏负，尤其 long leg 到 `+12 bars` 平均 **`-69.52 bps`**，说明 transfer 很差
- **SOL short**：
  - `+1 bar` **`+7.03 bps`**
  - `+3 bars` **`+7.76 bps`**
  - `+6 bars` 近乎打平
  - `+12 bars` 转负到 **`-5.90 bps`**

如果再用一个**非 repo 原生、只是为了 first verdict 的简化交易壳**（next-bar open 入场、`TP 0.4% / SL 0.3% / max_hold 12 bars`）：
- `BTC long`：`9` 笔，平均 **`+2.69 bps/笔`**
- `BTC short`：`12` 笔，平均 **`+3.51 bps/笔`**，但中位数仍为负，说明分布很歪，靠少数大单撑住
- `ETH long`：`11` 笔，平均 **`-17.27 bps/笔`**
- `ETH short`：`7` 笔，平均 **`-7.63 bps/笔`**
- `SOL long`：`14` 笔，平均 **`+4.82 bps/笔`**
- `SOL short`：`17` 笔，平均 **`+9.00 bps/笔`**，是本轮最健康 pocket

### 2.3 应该怎么读这些结果
这组结果最值钱的，不是“它赚没赚很多”，而是它把 alpha 的真实形状暴露出来了：

1. **它不是广义 BB 回归。**
   如果是纯 MR，应该更容易在所有币上看到对称 pocket；但这里明显不是。

2. **它更像“趋势内 pullback replay”，且 edge 寿命偏短。**
   BTC long 和 SOL short 都是 `15m` 左右最好，拉到 `60m` 就明显衰减。

3. **它强依赖 asset / side admission。**
   同样规则，ETH 基本塌掉，说明这个 alpha 不能裸复制成全币模板。

4. **它值得进池，但应作为“可复现 raw alpha 候选”，不是直接 production-ready 主策略。**
   因为 base alpha 清楚，可快速复现；但没有 exit / sizing / fee shell 前，不适合直接升格成“完整策略”。

## 3. 为什么和当前项目有关
这轮选它，不是因为它比 pairs / carry 更“高级”，而是因为它正好补当前池子里相对稀缺的一块：

1. **它是 raw alpha，不是 filter 伪装。**
   `EMA`、`VWAP` 在这里服务于定义 alpha 本体，不只是 veto。
2. **它天然贴近当前短周期。**
   原始逻辑就是 `20/50` EMA、`20` bar VWAP、`20` bar BB，直接落在 `5m` 很自然。
3. **它补的是 trend-pullback 这条线。**
   我们最近已补了很多纯 MR、cross-sectional、pairs、microstructure；而“趋势已经站住后的一次短暂 band 穿刺再启动”这类形状，最近并不是主 intake。
4. **它能很快做最小实验。**
   只靠公开 K 线和成交量就能跑，不依赖 order book、OI、funding、外部情绪源。

## 3.5 策略拆解（必填）
- 方向属性：单资产、双边、短周期 trend-pullback / continuation
- 基础 alpha：`局部趋势成立 + 反向 band 穿刺 → 顺原方向回放`
- regime：当前 repo 没有单独 regime 模块；`EMA20/EMA50 + VWAP20` 本身就在承担“局部趋势有效”的 regime 判定
- filter / veto：可后续补 `ADX`、`ATR expansion`、`session`、`funding bias`，但这些都不是当前 alpha 本体
- risk / sizing / execution overlay：repo 原生缺位；需我们自己补 `fixed horizon / ATR stop / maker-first / cost ladder`

## 4. 可复刻的最小实验
### 4.1 最小研究假设
**在 `5m` 上，当局部趋势已由 `EMA20/EMA50 + VWAP20` 锁定时，反向 Bollinger 穿刺不是反转起点，而更像 pullback exhaustion；未来 `15~30m` 更可能沿原趋势继续一小段。**

### 4.2 一个可计算定义
在 `5m` K 线上计算：
- `EMA20`, `EMA50`
- `rolling VWAP20`
- `BB(20, 2)`

信号：
- long：`EMA20 > EMA50`、`close > VWAP20`、`low <= lower_BB`
- short：`EMA20 < EMA50`、`close < VWAP20`、`high >= upper_BB`

### 4.3 本轮最小快检
- 数据：Binance USDⓈ-M public `5m klines`
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 样本：近约 `12000` bars（约 `41.6d`）
- 两种看法：
  1. **event return**：看未来 `1 / 3 / 6 / 12 bars`
  2. **toy trading shell**：`next-open` 入场，`TP 0.4% / SL 0.3% / 12-bar cap`

### 4.4 下一步怎么测
1. **先加 asset-ranking / admission layer。**
   当前 first probe 已说明这不是 broad-book alpha；下一步先按 `rolling hit-rate / expectancy / realized trendiness` 对币和方向分层，不要全币裸跑。
2. **先把最佳持有窗收窄在 `15~30m`。**
   多数 pocket 到 `60m` 已经衰减甚至反转，说明它不是 swing hold，edge 更像短促 replay。
3. **给 short leg 单独做 veto。**
   BTC short 到中长窗明显恶化，可能需要加 `15m downside trend strength` 或 `higher-timeframe close < VWAP` 的二次确认。
4. **补一个 honest exit shell。**
   可以先试 `ATR stop + fixed-horizon exit + reversion fail-fast`，再比 `TP/SL` 硬阈值是否更稳。
5. **成本要用双层 friction ladder。**
   先测 `2 / 4 / 8 bps` round-trip，别因为这轮 toy shell 有小正值，就误判它足够厚。

## 5. 风险与保留意见
- 这份 repo 的 `vwap-ema-bb` 更像 **entry module**，不是完整 production strategy；所以这轮结论只能是“alpha 候选值得 intake”，还不能说“可直接上线”。
- 本轮 quick probe 样本不长，且信号稀疏，很多 bucket 只有个位数或十几笔；只能给 first verdict。
- `TP 0.4% / SL 0.3% / 12 bars` 是我为了快检临时补的 toy shell，不是 repo 原始规则，不应被误读成作者结论。
- 当前 transfer 强烈依赖标的与方向，尤其 `ETH` 基本负样本；说明后续必须把 **asset/side admission** 放在前面。

## 6. first verdict
这条线**可以进 raw alpha 素材池**，但它当前更适合被标成：

> **`可独立复现的 raw alpha 候选`，而不是“已闭环完整策略”。**

更具体地说，当前最像真的不是“全币双边 BB 信号”，而是：
- **BTC long：trend-up + pullback pierce → 15~30m replay**
- **SOL short：trend-down + relief spike → 15m replay**

如果下一轮 admission layer 能把币种 / 方向 / 持有窗筛清楚，这条线是有资格继续往完整策略壳推进的。

## 7. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
- portability script：`reports/artifacts/quant_digests/2026-04-18_vwap_ema_bb_probe.py`
- portability outputs：`reports/artifacts/quant_digests/vwap_ema_bb_probe_20260418_0203/`

## 8. 来源
1. **naimkatiman. (2026). _TradeClaw_. GitHub repository.**
   - Readable URL: <https://github.com/naimkatiman/tradeclaw>
   - Repo URL: <https://github.com/naimkatiman/tradeclaw>
2. **Key source files used in this digest**
   - <https://raw.githubusercontent.com/naimkatiman/tradeclaw/main/README.md>
   - <https://raw.githubusercontent.com/naimkatiman/tradeclaw/main/packages/strategies/src/entry/vwap-ema-bb.ts>
   - <https://raw.githubusercontent.com/naimkatiman/tradeclaw/main/packages/strategies/src/presets.ts>
   - <https://raw.githubusercontent.com/naimkatiman/tradeclaw/main/docs/SIGNAL_PROFITABILITY_RESEARCH.md>
