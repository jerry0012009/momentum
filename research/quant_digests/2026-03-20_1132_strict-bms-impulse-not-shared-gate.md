# 别把 strict BMS impulse 直接升成三条线 shared gate：`3 连续动量 + body≥60% + 距离>0.5ATR` 在 15m 过稀疏，且 short 侧不稳
- 时间：2026-03-20 11:32 UTC
- 类型：GitHub 仓库 + Binance 公共数据代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/bms/impulse/momentum-candles/body-ratio/atr-distance/continuation/failure/filter/repo/crypto/15m
- 证据类型：仓库代码（工程证据）+ 公开 OHLCV 最小代理快检

## 1. 这次看了什么
这轮主看一个很新的仓库 **Madrycrypto/fibo71-bot（2026）**。我没有复刻它“Fib 71-79”主叙事，而是只抽其中更适合我们 desk 的旁支：`src/indicators/bms_detector.py` 里把 BMS 冲击质量写成可计算规则——**3 根同向动量K、每根 body≥60% 区间、且突破距离>0.5ATR(14)**。

## 2. 核心结论
- **一句话核心结论：** strict BMS impulse 在 15m 更像“高确信度少量样本”标记，不适合直接当 breakout-short / Fib / EMA-PSAR 的 shared admission gate。  
- **一句话证明方式：** 按 repo 的 strict 口径，我在 Binance Futures 公开 `BTC/ETH/SOL` 近 120 天 15m 做事件快检，对比 `raw breakout` 与 `strict impulse breakout` 的 4-bar signed return 与 re-entry 率。
- 关键数据点 1（覆盖率）：long 侧 `raw=2385`，strict impulse 只有 `10`（**0.42%**）；short 侧 `raw=2560`，strict impulse `33`（**1.29%**）。它太稀疏，直接 shared 化会明显压缩交易频次。
- 关键数据点 2（方向不对称）：long 侧 strict impulse 均值约 **+35.5 bps**（raw 为 **-2.4 bps**）有改善迹象；但 short 侧 strict impulse 均值约 **-16.5 bps**（raw 为 **+1.1 bps**）反而更差。
- 关键数据点 3（路径质量）：strict impulse 的 `4-bar re-entry` 显著更低（long **10.0%** vs raw **44.1%**；short **9.1%** vs raw **39.3%**），说明它确实更“冲得直”，但 short 侧仍不保证收益方向。

## 3. 为什么和当前三条收口线有关
- **V3 final-verdict / breakout-short follow-up**：这轮最关键是给 short 侧踩刹车——strict impulse 不该做 breakout-short 的共享放行键，更像 `high-conviction subset` 或 `size-down 反向否决` 参考。  
- **Fibonacci confirmation / retest_hold**：对 Fib 线更有价值的是“前段冲击质量”标签，可用于区分哪些 retest 值得等，但不该把 strict 规则硬设成必选门。  
- **EMA / PSAR raw alpha focus**：raw alpha 当前最怕 trade count 过快塌缩；strict impulse 适合作为实验分层（A/B 桶），不适合上来就当默认 admission。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
`strict BMS impulse` 作为 shared gate 会过度降频；把它降级为“打分项/分层项”后，可能在不显著砍交易数的前提下改善 follow-up 质量。

### 一个可计算定义
- `strict_impulse=1` 当且仅当：
  1) 最近 3 根K 与 breakout 同向；
  2) 每根 `|close-open|/(high-low) >= 0.60`；
  3) `break_distance / ATR14 > 0.5`。
- 下一轮加一个软版本（对照组）：`2/3` 满足 + `median body>=0.50` + `distance>0.25ATR`。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m（后续可补 5m 执行层）
- 样本：滚动近 120 天
- 执行：next-bar open + no-overlap
- 成本：6/10/15 bps per side

### 先看哪 2 个指标
1. `post-cost expectancy`（按 long/short 分开）
2. `trade retention`（相对 baseline 的留存率，防止“只靠极端降频换好看”）

## 5. 风险与保留意见
- 这轮是 repo 规则 + 公共数据代理快检，不是完整策略级回测；
- strict 规则样本非常稀疏（尤其 long 仅 10 例），统计不稳定；
- short 侧资产分歧明显（BTC 负、SOL 正），不能直接全资产共享；
- 结论应理解为“先定角色边界”，不是“strict impulse 无效”。

## 6. 来源
1. **Madrycrypto. (2026). _fibo71-bot: Fibo 71 Trading Bot - Fibonacci retracement strategy with BOS detection_. GitHub repository.**  
   - Authors: GitHub user `Madrycrypto`  
   - Year: 2026  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/Madrycrypto/fibo71-bot`  
   - Repo URL: `https://github.com/Madrycrypto/fibo71-bot`  
   - Key files:  
     - `https://github.com/Madrycrypto/fibo71-bot/blob/main/src/indicators/bms_detector.py`  
     - `https://github.com/Madrycrypto/fibo71-bot/blob/main/README_BMS_STRATEGY.md`

2. **Binance. (2026). _USDⓈ-M Futures REST API — Kline/Candlestick Data_.**  
   - Authors/Org: Binance  
   - Year: 2026 (live docs)  
   - Venue: Official API docs  
   - DOI: `N/A`  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`  
   - Data URL example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`  
   - 公开性：公开可得  
   - 更新频率：逐根 K 线更新（5m/15m/1h）  
   - 最小可复现实验口径：BTC/ETH/SOL perp，15m 事件法 + no-overlap

---
快检文件：
- `reports/artifacts/literature/strict_bms_impulse_pool_summary_2026-03-20.csv`
- `reports/artifacts/literature/strict_bms_impulse_asset_summary_2026-03-20.csv`
- `reports/artifacts/literature/strict_bms_impulse_event_examples_2026-03-20.csv`
- `reports/artifacts/literature/strict_bms_impulse_metadata_2026-03-20.json`
- `reports/artifacts/literature/strict_bms_impulse_all_events_2026-03-20.csv`
