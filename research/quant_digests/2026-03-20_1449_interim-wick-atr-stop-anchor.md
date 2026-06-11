# 别把 15m 初始止损继续写成 `entry ± 1.5 ATR`：`上一根反向 K 线影线 ± 0.25 ATR` 更像 breakout-short / Fib / EMA 的 honest risk anchor
- 时间：2026-03-20 14:49 UTC
- 类型：GitHub 仓库 + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/stop-loss/risk-anchor/interim-candle/wick/atr/execution/risk-overlay/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 本地公开行情代理快检

## 1) 这次看了什么
这轮主看一个很新的仓库 **TheVision333/trading-bot**（初始提交 2026-02-23）。真正值得偷的不是它整套 breakout/retest 流程，而是 `strategy/signals.py` 里把**初始止损**拆成 3 种锚法：
- `sl_atr`：`entry ± 1.5 * ATR`
- `sl_candle_pct`：挂在**最近一根反向颜色 K 线的影线**外，再给固定 `0.2%` buffer
- `sl_candle_atr`：同样挂在最近反向 K 线影线外，但 buffer 改成 `0.25 * ATR`

翻成人话：作者在提醒你，**止损不一定要围着入场价画圆；也可以挂在“最近那次真正反向对抗过趋势的位置”外面。**

## 2) 核心结论（先说人话）
- **一句话核心结论：** 对 15m 的 breakout-short / Fib retest / EMA continuation，`entry ± 1.5 ATR` 往往太像“围着入场点拍脑袋”；把 stop 挂到**最近反向 K 线影线**外，更像尊重结构噪声的初始风险锚。
- **一句话证明方式：** 先读 repo 里的 3 种 stop 实现，再用本地 `BTC/ETH/SOL` 三条基线信号做 `8-bar` 代理快检，比较不同 stop 锚法的距离与早停率。

## 3) 最关键数据点（本地 15m 代理）
口径：`BTC/ETH/SOL`、三条 baseline（`breakout_short / fib_retest_long / ema_psar_long`）共 **198** 笔信号，`next-bar open` 入场，观察入场后 **8 bars** 内是否先被 stop 打掉。

1. **纯 ATR stop 最紧，但最容易被近端噪声扫掉**：
   - `entry ± 1.5 ATR`：stop 中位距离 **0.66%**，`8-bar stop-hit = 52.0%`
   - `反向影线 ± 0.25 ATR`：中位距离 **0.95%**，`8-bar stop-hit = 31.8%`
   - `反向影线 ± 0.2%`：中位距离 **1.01%**，`8-bar stop-hit = 26.8%`
2. **对 breakout-short 最明显**：
   - 纯 ATR：`8-bar stop-hit = 45.9%`
   - 反向影线 ± 0.25 ATR：**16.4%**
   - 反向影线 ± 0.2%：**11.5%**
   说明 short follow-up 很容易被“入场附近的小反抽”打掉；结构锚 stop 更像是在防噪声，而不是单纯放宽风险。
3. **但结构锚不是白送的，它会推大风险半径**：
   - `stopDistancePct > 1.5%` 的占比：纯 ATR **3.5%**，`反向影线 ± 0.25 ATR` **24.7%**，`反向影线 ± 0.2%` **25.8%**。
   - 若先加一个 `1.5%` 距离上限，`反向影线 ± 0.25 ATR` 仍保留 **149/198** 笔，`8-bar stop-hit` 还能压到 **38.9%**；纯 ATR 在同口径下仍有 **52.9%**。

## 4) 为什么这对三条收口线值钱
- **V3 final-verdict / breakout-short follow-up**：现在 short 侧最怕“刚进就被正常回抽打掉”，然后误判成 follow-up 不行。结构锚 stop 更像在测 setup 本身，而不是测入场点附近的噪声运气。
- **Fibonacci confirmation / retest_hold**：如果你真的在做“回踩守住”，那初始 stop 理应更接近**回踩低点 / 最近反向 K 线低点**，而不是只按 entry 做固定 ATR 圆圈。
- **EMA / PSAR raw alpha focus**：raw alpha 本来边就薄；若初始止损过紧，会把“alpha 薄”误读成“alpha 不存在”。但也不能因此无限放宽，所以更像该用 **结构锚 + 距离上限**，而不是裸结构锚。

## 5) 下一步怎么测（最小可执行）
直接做一个 **3×2 风险锚 A/B**：
1. stop 锚法：
   - `ATR-only = entry ± 1.5 ATR`
   - `wick+ATR = 最近反向 K 线影线 ± 0.25 ATR`
   - `wick+pct = 最近反向 K 线影线 ± 0.2%`
2. 风险上限：
   - `uncapped`
   - `cap stopDistancePct <= 1.25% / 1.5%`（超限则 `deny` 或 `half-size`）

在 `BTC/ETH/SOL 15m`、`next-bar open`、`no-overlap`、`6/10/15 bps per side` 下分别接到三条线，只先看四个指标：
- `post_cost_expectancy`
- `premature_stop_rate@4/8 bars`
- `trade_count_retention`
- `stopDistancePct distribution`

**最小判决规则：**
- 若 `wick+ATR + distance cap` 能在不过度砍交易数的前提下压住 `premature_stop_rate`，它就应升格为 shared initial risk anchor 候选；
- 若只有“更宽 stop”才改善，而成本后收益没起色，就把它留在 risk overlay，不要偷渡成 alpha 改善。

## 6) 风险与保留
- 这轮是**代理快检**，不是完整撮合回测；
- 当前只回答“初始 stop 更像该挂在哪”，不回答最终 TP/移动止损怎么接；
- 结构锚 stop 对 `breakout_short` 尤其容易变宽，所以必须和 `stopDistancePct cap` 或 `size-down` 联合测试，不能单独放飞。

## 7) 来源
1. TheVision333. (2026). *trading-bot*. GitHub repository.  
   - Authors: GitHub user `TheVision333`  
   - Year: 2026（repo 初始提交：2026-02-23）  
   - Title: trading-bot  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/TheVision333/trading-bot>  
   - Repo URL: <https://github.com/TheVision333/trading-bot>
2. TheVision333. (2026, code). *strategy/signals.py* / *config.py*.  
   - 关键点：`sl_candle_pct`、`sl_candle_atr`、`sl_atr` 三套 stop 锚法并列实现。  
   - Readable URL: <https://github.com/TheVision333/trading-bot/blob/main/strategy/signals.py>  
   - Readable URL: <https://github.com/TheVision333/trading-bot/blob/main/config.py>  
   - Repo URL: <https://github.com/TheVision333/trading-bot>
3. Binance Futures 公共 K 线（本地缓存来源）  
   - Title: USDⓈ-M Futures Market Data (Kline/Candlestick)  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>  
   - Repo URL: N/A

## 8) 本轮产物
- `reports/artifacts/quant_digests/interim_wick_stop_proxy_rows_2026-03-20.csv`
- `reports/artifacts/quant_digests/interim_wick_stop_proxy_summary_2026-03-20.csv`
- `reports/artifacts/quant_digests/interim_wick_stop_proxy_setup_summary_2026-03-20.csv`
- `reports/artifacts/quant_digests/interim_wick_stop_proxy_asset_summary_2026-03-20.csv`
