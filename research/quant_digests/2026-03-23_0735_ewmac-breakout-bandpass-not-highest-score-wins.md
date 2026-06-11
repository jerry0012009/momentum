# 别把 EMA/Breakout 分数越高当越好：2025 新仓库更值钱的是“连续仓位 + band-pass gate”
- 时间：2026-03-23 07:35 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检
- 主题类型：filter
- 基础 alpha：breakout continuation（EWMAC/Breakout 事件）
- 是否可独立复现：否（依附 breakout 事件）
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（需与主 setup 联动）
- 主题标签：breakout-short/v3/final-verdict/follow-up/fibonacci/retest-hold/ema/psar/ewmac/continuous-positioning/regime/filter/position-sizing/repo/crypto/15m
- 证据类型：工程证据 + 本地快检（可复现）

## 1. 这次看了什么
这次看的是 **nicolasdd1996 (2025) 的 `crypto-trend-follow`**。它最适合我们 desk 的旁支，不是“再造一个新触发器”，而是把 `EWMAC + breakout` 做成**连续仓位分数**，再叠 **risk-off 过滤** 与执行优化。

## 2. 核心结论
- **一句话核心结论：** 对 15m 三条收口线，`EMA/Breakout` 更像“分档 admission/sizing 分数”，不是“分数越高越该追”的单调 hard gate；极端高分反而常是 late-chase。
- **一句话证明方式：** 用 Binance `BTC/ETH/SOL` 15m（近 180 天）做 `20-bar breakout` 事件，回填 `EWMAC(EMA32-EMA96)/ATR14` 对齐分数，比较不同分位的 `8-bar signed return`。
- 本地快检（`n=3445`）里：
  - baseline 全样本均值约 **+1.84 bps**；
  - `align_score` 中段（q20~q80）均值约 **+9.53 bps**（`n=2067`）；
  - 两端极值（<=q20 或 >q80）均值约 **-9.68 bps**（`n=1378`）。
- 分方向看：
  - `short breakout`：baseline **+8.53 bps** → 中段 band-pass **+17.55 bps**；
  - `long breakout`：baseline **-4.88 bps** → 中段 band-pass **+1.51 bps**。
- 这说明“极端强趋势读数”在 15m breakout 事件里并不自动等于更好 follow-up；很多时候它更像过度伸展后的不对称回抽风险。

## 3. 为什么和当前项目有关
- **V3 final-verdict / breakout-short follow-up**：可先把 `align_score` 作为 post-break 分档，不再把“最强分数”默认当 continuation 放行。  
- **Fibonacci confirmation / retest_hold**：retest 回收后，用 `band-pass`（中段放行、极端降权）比“越强越追”更诚实。  
- **EMA / PSAR raw alpha focus**：EMA 更像连续状态刻度与仓位尺子，PSAR 更适合 fail-safe / 风险托底，而不是把 EMA/PSAR 当同层硬触发。

## 3.5 策略拆解（必填）
- 方向属性：顺势 continuation（分档而非二元）
- 基础 alpha：breakout / retest 事件本体（现有三条线之一）
- regime：risk-off（低质量环境减仓/停机）
- filter / veto：`align_score` 的 band-pass（中段优先，极端尾部降权或 veto）
- risk / sizing / execution overlay：连续仓位（按分数缩放），不是 all-in/all-out

## 4. 可复刻的最小实验
- **研究假设：** 在 15m 事件流里，`EWMAC 对齐分数`呈“中段优于两端”的非线性；band-pass 比 hard-positive 更稳。  
- **一个可计算定义：**  
  - `align_score = event_side * (EMA32-EMA96)/ATR14`；  
  - 事件：`20-bar` 上下突破；标签：`8-bar signed return`。  
- **最小回测切口：** `BTC/ETH/SOL` perpetual，15m，近 180 天；A/B/C 三组：  
  - A: baseline（不过滤）  
  - B: `align_score > 0`（硬对齐）  
  - C: `q20 < align_score <= q80`（band-pass）
- **先看 2 个指标：**
  1) post-cost expectancy（bps）
  2) trade retention（防止靠“砍样本”变好）

## 5. 风险与保留意见
- 本轮是统一事件口径的快检，不是完整成交级撮合回放；用于“是否值得升格到下一轮”而非最终定案。  
- 分位阈值依赖样本窗，必须做 rolling/OOS 稳定性检查。  
- 若 band-pass 只在单一币有效而跨币退化，就只能作为 setup-specific overlay，不应升为 shared hard gate。

## 6. 来源
1. **nicolasdd1996. (2025). _crypto-trend-follow_. GitHub Repository.**  
   - Authors / Year / Title / Venue: nicolasdd1996 / 2025 / crypto-trend-follow / GitHub Repository  
   - DOI: N/A  
   - Readable URL: https://github.com/nicolasdd1996/crypto-trend-follow  
   - Repo URL: https://github.com/nicolasdd1996/crypto-trend-follow
2. **ryanczm. (2024/2025). _Crypto-Stat-Arb_. GitHub Repository.**  
   - Authors / Year / Title / Venue: ryanczm / 2024-2025 / Crypto-Stat-Arb / GitHub Repository  
   - DOI: N/A  
   - Readable URL: https://github.com/ryanczm/Crypto-Stat-Arb  
   - Repo URL: https://github.com/ryanczm/Crypto-Stat-Arb
3. **Binance USDⓈ-M Futures Market Data API（最小实验数据口径）**  
   - 数据源：Binance Developers（公开可得）  
   - 更新频率：分钟级（15m 聚合可直接拉取）  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Continuous-Contract-Kline-Candlestick-Data

## 7. 本地复现产物
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/event_table.csv`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/summary.csv`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/bucket_summary.csv`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/bandpass_summary.csv`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/thresholds.json`
- `reports/artifacts/quant_digests/ewmac_breakout_alignment_20260323/meta.json`
