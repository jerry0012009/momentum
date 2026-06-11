# 别把 EMA 回踩写成“碰线就算守住”：`close reclaim` 在 15m 只够给 Fib / EMA long 减亏，不够救活 raw alpha，也不该镜像给 breakout-short
- 时间：2026-03-20 04:26 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/ema-bounce/close-reclaim/continuation/asymmetry/filter/repo/crypto/15m
- 证据类型：工程证据（仓库源码）+ 代理快检（公开行情）

## 1. 这次看了什么
这轮主看两个 Pine 脚本的交集，而不是它们整套模板。
- **tweakerID / `EMA Bounce Strategy`**：把“EMA 回踩后守住”写成一个很干净的条件——上一根 `low` 还在 EMA 上方，这一根先刺穿 EMA，但 **收盘重新站回 EMA 上方**，才算 `Bull Bounce`。
- **juanchodeespada / `Trend Continuation`**：提醒我们这类回踩不要裸做，最好放回更宽的 EMA 趋势骨架里理解，例如 `EMA20 > EMA50 > EMA200` 一类 stacked trend。  

所以这轮真正要回答的是：**对 15m crypto，`碰到 EMA` 和 `碰后收回 EMA` 到底是不是两回事？如果是，它更像 raw alpha，还是只是一个 long-side 的 admission / damage-control layer？**

## 2. 核心结论
- **一句话核心结论**：`EMA close reclaim` 在 15m 上确实比“只碰到 EMA 但没收回”更像样，但它目前只够当 **Fib retest / EMA continuation 的 long-side 减亏层**，还不够把 `EMA / PSAR raw alpha` 救成正经可交易母信号。
- **一句话它怎么证明**：源码把 bounce 明确写成 `prev low > EMA`、本 bar `low < EMA` 且 `close > EMA`；我再用 `BTC/ETH/SOL perp, 15m, 近120天` 做代理快检，把“有 touch 的回踩”拆成 **收回 EMA** vs **没收回 EMA** 两组，比较后续 `4 bars / 8 bars` 表现。 

### 2.1 repo 里最值得偷的不是“EMA 本身”，而是判定边界
`tweakerID` 这份脚本最值钱的地方，不是单 EMA 策略，而是它把 retest 写得很诚实：
- long bounce：`low[1] > ema[1]` 且 `low < ema` 且 `close > ema`
- short bounce：`high[1] < ema[1]` 且 `high > ema` 且 `close < ema`

这对我们当前 desk 很关键，因为它把 **“碰线”** 和 **“收回防守线”** 分开了。对 `Fib retest_hold` 来说，这基本就是同一个哲学：别再把触位本身误写成守住。

### 2.2 本地 15m 代理快检：long 有减亏价值，但还不够翻正
我先用最小代理做：
- 数据：`BTC/ETH/SOL` perp，`15m`，近 `120d`
- 趋势底座：long 用 `EMA50 > EMA200`，short 用镜像
- 事件分组：同样都是先发生 `touch EMA20` 的回踩，再拆成：
  1. `bounce_close_reclaim`
  2. `touch_no_reclaim`
- 评估：看后续 `4 bars` 与 `8 bars` signed return

#### long 侧：close reclaim 比 touch-only 少亏一些，但还没变真 alpha
在基础趋势过滤（`EMA50 > EMA200`）下：
- `bounce_close_reclaim`：`n=559`，未来 `4 bars` 均值 **-3.16 bps**，中位 `MAE` **-29.17 bps**
- `touch_no_reclaim`：`n=483`，未来 `4 bars` 均值 **-5.88 bps**，中位 `MAE` **-31.50 bps**

也就是说，**收回 EMA** 比没收回好，大约少亏 **2.72 bps**，但 aggregate 还是负的。它更像“别做太烂的那种回踩”，还不是“这就能直接开火”。

#### 放回更强的 stacked trend 后，long 侧才更像 admission layer
如果再要求 `EMA20 > EMA50 > EMA200`：
- `bounce_close_reclaim`：`n=470`，未来 `4 bars` 均值 **-1.74 bps**，`8 bars` 均值 **-2.17 bps**
- `touch_no_reclaim`：`n=417`，未来 `4 bars` 均值 **-7.18 bps**，`8 bars` 均值 **-5.27 bps**

差值变成：
- `4-bar mean` 改善约 **+5.44 bps**
- `8-bar mean` 改善约 **+3.10 bps**
- `win rate` 提升约 **+1.19 pct-pts**
- `median MAE` 收窄约 **4.49 bps**

这说明它比较像：**必须嵌在更强趋势骨架里的 long-side admission / damage-control gate**。

#### short 镜像不成立，别硬塞给 breakout-short
在 `EMA20 < EMA50 < EMA200` 的 strong short stack 里：
- `short bounce_close_reclaim`：`n=631`，未来 `4 bars` 均值 **+3.32 bps**
- `touch_no_reclaim`：`n=436`，未来 `4 bars` 均值 **+5.90 bps**

也就是 short 侧 **close-back-below-EMA** 并没有变得更好，反而更差。对我们现在的 `V3 breakout-short follow-up`，这轮更值钱的信息不是“找到一个 short gate”，而是：**别把 long 的 honest retest 逻辑直接镜像到 short。**

## 3. 为什么和当前三条收口线直接相关
- **Fibonacci confirmation / retest_hold**：这轮最直接的启发就是，`touch` 和 `close reclaim` 必须拆开；后者才更像“守住”，前者最多只是“碰到过”。
- **EMA / PSAR raw alpha focus**：即便用了 `close reclaim`，long 侧 aggregate 仍未翻正，说明它顶多是 admission layer，不该被误报成 raw alpha 已经被救活。
- **V3 final-verdict / breakout-short follow-up**：short 镜像没占优，说明这套 bounce 逻辑目前不适合直接认领 breakout-short 的 shared follow-up gate。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
`EMA close reclaim` 只应作为 **Fib retest_hold / EMA continuation 的 long-side 质量过滤层**；它不该被当成多空对称默认 admission，更不该单独宣称自己是 raw alpha。

### 一个可计算定义
- `ema_fast = EMA20`
- long trend template：`EMA20 > EMA50 > EMA200`
- long reclaim：`low[1] > ema_fast[1]` 且 `low < ema_fast` 且 `close > ema_fast`
- short 镜像只保留为对照组，不默认纳入生产规则

### 最小回测切口
优先做三臂 honesty test：
1. **touch-only**：回踩触到 `EMA20` 就允许进
2. **close reclaim**：必须 `close > EMA20`
3. **close reclaim + stacked trend**：再加 `EMA20 > EMA50 > EMA200`

### 建议场景
- 资产：`BTC/ETH/SOL` perp
- 周期：`15m` 判定，`5m` 可做执行细化
- 样本：最近 `180~365d`
- 成本：先看 `6 / 10 / 15 bps per side`
- 优先挂到：`Fib retest_hold long` 与 `EMA continuation long`

### 最先看 4 个指标
1. `post_cost_return`
2. `trade_count`
3. `positive_asset_ratio`
4. `MAE / fail-fast rate`

## 5. 风险与保留意见
- 这轮证据主体是仓库源码与最小代理快检，不是正式论文结论。
- 代理快检没有把完整出场、资金费率、冲击成本和多因子上下文全部纳入，所以更像 **状态边界测试**，不是完整策略回测。
- long 侧虽然 `close reclaim` 明显比 `touch-only` 好，但 aggregate 仍偏弱，**不要把“少亏一点”误读成“已经可单独交易”。**
- short 侧镜像不占优，当前默认应把它视为 **not-shared / not-default**，而不是继续强行做成 breakout-short follow-up。

## 6. 来源
1. tweakerID. (accessed 2026). *EMA Bounce Strategy*. GitHub code file / mirrored Pine script.  
   - Authors: tweakerID  
   - Year: N/A  
   - Title: EMA Bounce Strategy  
   - Venue: GitHub code file  
   - DOI: N/A  
   - Readable URL: <https://raw.githubusercontent.com/hasnocool/tradingview-pine-scripts/main/EMA%20Bounce%20Strategy.pine>  
   - Repo URL: <https://github.com/hasnocool/tradingview-pine-scripts>
2. juanchodeespada. (accessed 2026). *Trend Continuation*. GitHub code file / mirrored Pine script.  
   - Authors: juanchodeespada  
   - Year: N/A  
   - Title: Trend Continuation  
   - Venue: GitHub code file  
   - DOI: N/A  
   - Readable URL: <https://raw.githubusercontent.com/hasnocool/tradingview-pine-scripts/main/Trend%20Continuation.pine>  
   - Repo URL: <https://github.com/hasnocool/tradingview-pine-scripts>
3. Binance. (2026). *USDⓈ-M Futures REST API — Kline/Candlestick Data*.  
   - Authors: Binance  
   - Year: 2026  
   - Title: Kline/Candlestick Data  
   - Venue: Binance Developers  
   - DOI: N/A  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>  
   - Repo URL: N/A

## 7. 本轮落地产物
- `reports/artifacts/quant_digests/ema_bounce_proxy_events_2026-03-20.csv`
- `reports/artifacts/quant_digests/ema_bounce_proxy_summary_2026-03-20.csv`
- `reports/artifacts/quant_digests/ema_bounce_proxy_side_delta_2026-03-20.csv`
