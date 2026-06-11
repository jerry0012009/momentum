# 别把 breakout 后回踩确认写成“摸线就行”：`retest 后重破 impulse extreme` 更像 15m 的 continuation gate
- 时间：2026-03-19 21:54 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/orb/retest/bos/impulse-extreme/follow-through/confirmation/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
主来源是 GitHub 仓库 **Abdelrahman-7gab / orb-backtester (2025)**：它把 `NY ORB → retest → BOS` 写成可运行状态机，关键细节是 **回踩后要在限定窗口内重破“回踩前 impulse 极值”**，而不是只看“价格回到 breakout level”。

## 2. 核心结论
- **一句话核心结论**：对我们 5m/15m desk，更值得偷的是“`retest 后必须快速重破 impulse extreme`”这层确认，而不是把 ORB 原策略整套搬来做主信号。
- **一句话证明方式**：仓库 `trader/backtester.py` 明确写了 `candlesToWait=5`、`breakCandles=6`，并要求 long/short 分别突破 `impulse_high_up / impulse_low_dn` 才触发 BOS 进场。
- 该逻辑天然对应三条收口线：
  1) `V3 breakout-short follow-up`：回抽后若迟迟不能再破 impulse 低点，更像 failure；
  2) `Fib retest_hold`：回踩后不只看守位，还要看是否“重夺前高/前低”；
  3) `EMA/PSAR`：把 EMA/PSAR 留在方向层，`impulse re-break` 做执行确认层。
- 本地代理快检（BTC/ETH/SOL 永续，15m，近 120 天，20-bar breakout、0.2% retest、等待 5 bars、确认窗 6 bars）显示：
  - retest 事件里仅 **24.9%** 能在窗口内完成 impulse re-break（门槛不低）；
  - 通过确认组 4-bar 中位 signed return 约 **+43.8 bps**，未通过组约 **-6.7 bps**；
  - 通过确认组 4-bar 失效率约 **2.3%**，未通过组约 **38.8%**。

## 3. 为什么和当前项目有关
这是在继续帮三条主线收口，而不是开新坑：它直接回答“breakout/retest 后什么时候算真延续、什么时候该 veto”。相比继续堆新因子，先把这层 confirmation 做实，更能提高 `final verdict` 的一致性。

## 4. 可复刻的最小实验
### 研究假设
在 15m 上，给 breakout-short / Fib retest_hold / EMA-continuation 共用一层 `impulse re-break` gate，能显著降低“回踩后假延续”。

### 一个可计算定义
- 先定义 breakout level（可用 Donchian/区间边界/Fib 关键位）；
- 出现 retest 后，记录 `impulse_extreme_pre_retest`：
  - long 用回踩前局部最高价；
  - short 用回踩前局部最低价；
- 仅当 retest 后 `N` 根内（建议 `N=6`）**收盘价重破该极值**才放行；否则 veto/降仓。

### 最小回测切口
- 资产：BTC/ETH/SOL perp
- 周期：15m（可加 5m 做执行细化）
- 样本：近 120 天滚动
- 成本：`6/10 bps per side`
- 对照：
  1) baseline（现有三线原规则）
  2) baseline + level retest（二元）
  3) baseline + `impulse re-break gate`（本轮）

### 最先看 3 个指标
1. `post_cost_return`
2. `false_follow_through_4bars`
3. `max_drawdown` / `left-tail(5% trade pnl)`

## 5. 风险与保留意见
- 该仓库主语境是 NY session ORB，不是 24/7 crypto 原生框架；我们借的是“确认机制”，不是交易时段假设。
- 本轮快检是代理实验，不是完整策略回测；不能把 bps 结果当最终可交易结论。
- `wait=5 / confirm=6` 对不同币种可能需要再做稳健性扫描（`wait∈{3,5,7}`，`N∈{4,6,8}`）。

## 6. 来源
1. Abdelrahman-7gab. (2025). *NY ORB + Retest + BOS Backtester*. GitHub Repository.  
   - Authors: Abdelrahman-7gab  
   - Year: 2025  
   - Title: NY ORB + Retest + BOS Backtester  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/Abdelrahman-7gab/orb-backtester/master/README.md  
   - Repo URL: https://github.com/Abdelrahman-7gab/orb-backtester
2. Abdelrahman-7gab. (2025). *Strategy State Machine Implementation* (`trader/backtester.py`).  
   - Authors: Abdelrahman-7gab  
   - Year: 2025  
   - Title: backtester.py (NY ORB + Retest + BOS logic)  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://raw.githubusercontent.com/Abdelrahman-7gab/orb-backtester/master/trader/backtester.py  
   - Repo URL: https://github.com/Abdelrahman-7gab/orb-backtester
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data* (`/fapi/v1/klines`).  
   - Authors: Binance  
   - Year: 2026  
   - Title: USDⓈ-M Futures API Docs  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  
   - Repo URL: N/A
