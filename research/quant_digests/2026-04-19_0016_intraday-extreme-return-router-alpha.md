# 别把 Wen et al. (2022) 只读成“BTC 日内可预测性论文”：对 short-cycle crypto desk，更该先拆的是「extreme recent return × strongest-only continuation router」这条 raw alpha

- **主题类型：** raw alpha
- **基础 alpha：** 同一币种在刚出现足够强的短窗单边波动后，后续 `1h~2h` 往往不是立刻均值回复；更适合 desk 的读法是：**只做当下全市场最强的那一个方向冲击**，而不是把所有币的日内 predictability 一股脑都交易。
- **是否可独立复现：** 是
- **是否可直接落地完整策略（entry/exit/sizing/risk/cost）：** 是

## 先回答一句：这篇东西的 base alpha 是什么？

**base alpha 不是“BTC 某几个小时能预测当天后面某几个小时”这句学术 headline 本身，而是：`intraday own-past return continuation`。**

更适合我们 desk 的翻译是：

> **过去 `2h` 刚走出很强的单边冲击、而且这是全市场当下最极端的一档时，接下来 `2h` 仍可能继续顺着原方向漂。**

所以这轮我没有把 paper 硬抄成“日内小时矩阵预测”，而是抽出一个更容易搬到 `15m`、更像完整策略壳的旁支：

> **`recent 2h return z-score` 排名 + `volume positive` 确认 + `strongest-only router` + 固定 `2h` time-box exit**

---

## 这篇论文讲了什么，为什么值得 intake

**来源**
- **Authors：** Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao
- **Year：** 2022
- **Title：** *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*
- **Venue：** *The North American Journal of Economics and Finance*
- **DOI：** <https://doi.org/10.1016/j.najef.2022.101733>
- **Readable URL：** <https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833>
- **Mirror / text extraction used this round：** <https://r.jina.ai/http://www.sciencedirect.com/science/article/abs/pii/S1062940822000833>
- **Repo URL：** 本轮未拿到作者官方仓库

**我为什么选它**
1. 它是近 5 年正式期刊论文，不是只靠社区经验；
2. 主题直接是 **crypto intraday predictability**，和 `1m/3m/5m/15m` 研发有天然关系；
3. 更重要的是，它明确说 **crypto 的日内预测关系不只有正向 momentum，也有负向 reversal**，这非常适合我们 desk 做“别交易所有信号，只路由 strongest pocket”的二次拆解。

---

## 论文里最重要的几个硬点

基于本轮拿到的正文前言/section snippet，可确认的硬信息有：

1. **作者用的是 BTC `5m` 高频数据，再聚成 hourly return 做同日内各小时之间的预测矩阵。**
   这不是日频或周频慢研究，而是真正往 intraday 靠。

2. **结论不是单一“只有 momentum”。**
   论文明确写到：在 crypto 里，日内 predictor 的符号**既可能是正，也可能是负**；这和传统标准化市场里“多半正向延续”的读法不完全一样。

3. **predictability 在某些环境里更强：**
   - **no jump**
   - **no FOMC announcement**
   - **low liquidity**

4. **作者不只做 in-sample，还做 OOS 检验与 timing strategy。**
   论文不是只报回归显著性，而是明确讨论了经济价值。

5. **robustness 还扩到 ETH / LTC / XRP 与不同交易平台。**
   所以它不是只在 BTC 单点样本里讲故事。

一句话核心结论：

> **crypto 的 intraday predictability 确实存在，但它不是“永远追涨”或“永远反转”这么粗；真正值钱的是先找出哪一类短窗冲击还会继续走。**

一句话证明方式：

> **作者用 BTC 高频数据，把同一天内各小时收益做 IS/OOS 预测矩阵和 timing strategy，并在 jump / liquidity / FOMC / 其他币上做分样本和稳健性检查。**

---

## 对我们 desk 最有价值的翻译

如果照论文 headline 直译，你很容易写出一个不太 desk-friendly 的东西：
- “第 `i` 小时收益预测第 `j` 小时收益”
- 同一天内一堆 hour-slot 矩阵
- 很学术，但不够像可直接复现的 `15m` 策略

更适合当前 desk 的读法其实是：

### 1. 不要交易“所有 intraday predictability”
论文已经提醒：有些地方是 continuation，有些地方是 reversal。那就说明：
**值钱的不是 always-on 全开，而是 router。**

### 2. 对 liquid-major perp，router 比 plain 单币更重要
我这轮用 Binance USDⓈ-M `15m`、10 个 liquid majors（`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`）做了一个 portability probe：
- 先算每个币过去 `8` 根 `15m`（约 `2h`）收益；
- 再滚动标准化成 `z-score`；
- 每个时点只挑 **`abs(z)` 最大** 的那一档；
- 若 `|z|>=1.5` 且 `volume_z>0`，就顺着过去 `2h` 方向做 `2h` continuation；
- 固定持有 `8` 根 `15m` 后退出。

这个 strongest-only 读法，比“每个币都做 continuation”更像桌面可用信号。

---

## 本轮 portability probe：最值得记的 3 个数

### Probe 口径
- **市场：** Binance USDⓈ-M perpetual
- **周期：** `15m`
- **样本：** 10 个 liquid majors，近约 `60d`
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-19_intraday_predictability_ts_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_intraday_router_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_intraday_router_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_intraday_router_meta.json`

### 结果 1：plain 最近 `2h -> 后续 2h` continuation 只是轻微正，不够直接 taker
在全样本里，`L=8 bar`、`H=8 bar` 的 **top1 abs-z strongest-only** 组合，平均只有 **`+0.81 bps` gross**，不够厚。

### 结果 2：但加上 `|z|>=1.5 + volume_z>0` 后，edge 明显抬起来
同样是 strongest-only、顺着过去 `2h` 方向做 `2h` continuation：
- **`n = 1376`**
- **mean ≈ `+8.43 bps gross / trade`**
- **win rate ≈ `48.8%`**

胜率不高，但均值由少数大单边拉开，说明它更像 **convex continuation pocket**，不是稳定小赚型信号。

### 结果 3：若把它当 cross-sectional long-short fade，当前 liquid majors 反而不够厚
同样近 `60d`、每个 `15m` 时点做过去 `2h` loser-vs-winner：
- `top1 loser - top1 winner` next `2h` 约 **`+4.63 bps gross`**；
- `q20 basket` 约 **`+3.80 bps gross`**；
- 以常见 long-short taker 粗算 `16bps` round trip，当前明显不够厚。

所以这轮更值得保留的是：

> **单腿 strongest-only continuation router，而不是把论文硬翻成 market-neutral loser-winner fade。**

---

## 3.5 策略拆解（必填）

- **方向属性：** 顺势 / router
- **基础 alpha：** `extreme recent return continuation`
- **regime：** 论文提示 `no jump / no FOMC / low liquidity` 更强；本轮 public-data 代理版尚未显式加这三层 gate
- **filter / veto：** `|lag_return_z| >= 1.5`，且 `volume_z > 0`
- **risk / sizing / execution overlay：** strongest-only；固定 `2h` time-box exit；先按单腿 taker 粗扣 `8bps` 做生死线判断

---

## 它为什么比继续补某个 filter 更值得

因为这轮能先回答一个非常实用的问题：

> **“当下 market 里最极端的 2h 冲击，到底该追还是该反手？”**

结果不是泛泛的“都可以”，而是更清楚的：
- **全市场 strongest-only + 强度门槛 + volume 确认** 时，追随比反手更像可研究 pocket；
- 若没有这些 router 条件，plain continuation 很薄；
- 若改成横截面 loser-winner fade，当前 liquid-major perp 口径也不够厚。

这比单纯再补一个 overlay 更直接扩充 raw alpha 素材池。

---

## 最小可复刻实验

### 最小策略壳
在 `15m` universe 上，每根 bar 做：
1. 对每个币计算过去 `8` 根 `15m` 收益 `ret_8`；
2. 对每个币计算 rolling `96` 根的 `z(ret_8)`；
3. 只选 `abs(z)` 最大的 1 个币；
4. 若 `|z|>=1.5` 且 `volume_z>0`：
   - `ret_8 > 0` 就做多；
   - `ret_8 < 0` 就做空；
5. 持有固定 `8` 根 `15m`（约 `2h`）后退出；
6. 不叠仓，下一笔必须等前一笔结束。

### 先看哪两个指标
1. **gross / net bps per trade**（先粗扣 `8bps`）
2. **MFE/MAE 或 tail contribution**：确认收益是否被少数极端大单支撑

### 紧接着该测什么
1. **加入 jump veto**：若当前 bar 已是超大单根冲击，是否反而更差？
2. **加入 event veto**：避开 FOMC / CPI / funding settlement 边界，看看 paper 里的环境差异能否迁移到 perp。
3. **改成 `5m child execution`**：保持 `15m` 母信号，但把入场细化成 `5m` pullback / micro pullback，以争取把 `gross 8.43bps` 留到 `net`。

---

## 风险与保留意见

1. **这不是论文原始策略的严格复刻。**
   原文是同日内小时收益矩阵；我这轮是把它翻成 desk 更可用的 `15m strongest-only router`。

2. **当前 edge 很靠大尾部，median 仍偏负。**
   `top1_absz_ge_1p5_volpos` 的 `p50` 约 **`-2.02bps`**，说明它不是“多数单子小赚”的 smooth alpha。

3. **成本边缘不厚。**
   单腿 taker 若粗扣 `8bps`，当前只剩大约 **`+0.43bps`**；要么靠更细执行，要么靠更强 gate。

4. **样本只做了 liquid-major perp portability。**
   论文谈的是 BTC hourly predictability 与其他币 robustness，不等于 2026 Binance perp 的所有币都还能直接照抄。

5. **可能和已有 shock/continuation 家族重叠。**
   下一步必须和 `price burst`、`trade-flow imbalance`、`queue pressure`、`retail-chasing` 那几条做 horse race，确认它是不是独立 pocket。

---

## 我对这条线的当前判断

这轮我把它定为：

> **可独立复现、且能直接落成完整策略壳的 raw alpha 候选。**

但不是因为论文 headline 本身就能直接上线，而是因为它被翻译成：
- `15m` 母级别强度识别
- strongest-only router
- `2h` 固定退出
- 可继续叠 `5m` child execution

这让它更像一个**可马上进入 first-verdict / cost / execution honesty check** 的短周期素材，而不只是“学术上很有意思”。

---

## 来源

- Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*. *The North American Journal of Economics and Finance*, 62, 101733.
- DOI: <https://doi.org/10.1016/j.najef.2022.101733>
- Readable URL: <https://www.sciencedirect.com/science/article/abs/pii/S1062940822000833>
- Text mirror used this round: <https://r.jina.ai/http://www.sciencedirect.com/science/article/abs/pii/S1062940822000833>
