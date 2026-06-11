# 别把这个高星 Binance Futures bot 只读成“策略菜单”：对 short-cycle crypto desk，更该先拆的是「triple EMA stack × RSI veto × ATR bracket」这条 trend raw alpha 壳
- 时间：2026-04-21 13:58 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当 `EMA9 > EMA21 > EMA50`（或反向空头排列）时，短趋势延续概率上升；`RSI<70 / >30` 不是第二条 alpha，而是避免在已过热/过冷末端盲追；出场用 `1.5×ATR` 止损、`2×ATR` 止盈
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：trend / momentum / ema-stack / RSI / ATR / bracket-exit / Binance / 15m / 5m
- 证据类型：repo 工程规则 + public-data first probe

## 1. 这次看了什么
看的是 **Janis174756 (2026), Binance-Futures-Trading-Bot**。仓库信息：创建于 `2026-03-07`，GitHub API 显示约 `554` stars、`366` forks。真正值得 intake 的不是它罗列了十几种策略，而是 `strategies/trading_strats.py` 里那条最清楚的壳：`tripleEMAStochasticRSIATR`。源码把规则写得很直接：`EMA9/21/50` 同向堆叠给方向，`RSI14` 仅作不过热/不过冷 veto，风险用 `ATR14` 定 `1.5x` stop 与 `2.0x` target。来源：
- Repo URL: <https://github.com/Janis174756/Binance-Futures-Trading-Bot>
- README: <https://raw.githubusercontent.com/Janis174756/Binance-Futures-Trading-Bot/main/README.md>
- Strategy code: <https://raw.githubusercontent.com/Janis174756/Binance-Futures-Trading-Bot/main/strategies/trading_strats.py>
- Indicators: <https://raw.githubusercontent.com/Janis174756/Binance-Futures-Trading-Bot/main/strategies/indicators.py>

## 2. 核心结论
- **一句话核心结论：**这条东西的 base alpha 是最朴素的 `trend continuation`，不是“ATR/RSI 拼盘”；真正要回答的是：**短周期上，EMA 堆叠后的延续厚度，够不够盖住频繁止损与手续费。**
- **它怎么证明：**repo 给出可直接执行的规则壳；我再把同一逻辑迁到 Binance USDⓈ-M 公共 K 线做 `15m/5m` quick probe，看这条壳在 liquid majors 上有没有 pocket。
- `15m`、10 个 liquid majors、最近约 `16` 天、合计 `1413` 笔：gross 加权均值约 **`+1.54 bps/笔`**，若粗扣 `8 bps` round-trip 后约 **`-6.46 bps/笔`**；说明它**不是 broad taker alpha**。
- 但 `15m` 仍有 symbol pocket：`ETH ≈ +5.82 bps/笔`、`ADA ≈ +5.16`、`XRP ≈ +4.89` gross，接近“可以继续做 maker-first / veto 加强”的候选；`BTC`、`AVAX` 明显偏弱。
- `5m` 更差：10 币合计 `1303` 笔，gross 加权均值约 **`-0.79 bps/笔`**，粗扣成本后约 **`-8.79 bps/笔`**。说明这条壳若要活，默认更像 **`15m parent signal`**，而不是裸 `5m` 高频主信号。

## 3. 为什么和当前项目有关
这条规则的价值不在“又一个 EMA 策略”，而在它把一个最容易快复现的 trend 壳拆得很干净：
- `EMA stack` = base alpha
- `RSI veto` = 简单不过热确认
- `ATR bracket` = 先验盈亏比与波动适配出场

对当前 `momentum` 来说，它比继续围绕更花的形态/概念转圈更有用，因为它能直接作为 **趋势 raw alpha baseline**，拿去和已有的 breakout、volume-confirmation、pullback-confirmation 做对照或拼接。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：`EMA9 > EMA21 > EMA50`（或反向）后的短趋势延续
- regime：默认无；当前版本没有独立 market regime gate
- filter / veto：`RSI14 < 70` 才做多，`RSI14 > 30` 才做空
- risk / sizing / execution overlay：`ATR14` 定 `1.5x` 止损与 `2.0x` 止盈；repo 还有全局 `leverage/order_size/trailing_stop`，但**没有认真处理成本、time-stop 与 admission**

## 4. 可复刻的最小实验
- 研究假设：在 liquid majors 上，`15m` 的 EMA stack continuation 本身边不厚，但经过 symbol/router 过滤后，可能变成可用的趋势 parent signal。
- 最小口径：
  1. universe 先用 `BTC/ETH/SOL/XRP/DOGE/ADA/AVAX/LINK/BNB/LTC`
  2. `15m` 主测、`5m` 只做 child confirmation 对照
  3. 信号按 repo 原式：`EMA9/21/50` + `RSI14` + `ATR14`
  4. 入场用下一根开盘；出场先按 `1.5xATR / 2xATR`，再对照 `8-bar / 12-bar` time-stop
  5. friction ladder 至少测 `0 / 4 / 8 / 12 bps`
- 本轮产物：`reports/artifacts/quant_digests/2026-04-21_janis_tripleema_rsi_atr_probe_summary.csv`

## 5. 下一步怎么测
1. **先别全池做。** 把 `ETH/ADA/XRP` 作为 pocket pool，和 `BTC/AVAX` 做 A/B，对比是不是 alt middle-tier 趋势延续更厚。
2. 给它补一个最便宜的 **shared gate**：只在 `quote_volume z-score > 0` 或 `ATR percentile` 不过低时启用，检验是否能减少“慢磨型假趋势”。
3. 把出场拆开：`ATR bracket` vs `time-stop` vs `trailing stop`，确认问题到底出在 entry 还是出在 exit 过早/过慢。
4. 若仍要上 `5m`，不要把它当 standalone alpha；改成 **`15m EMA stack 给方向，5m pullback / breakout 给触发`**，否则成本基本吃光。 

## 6. 风险与提醒
- 这不是完整策略：repo 没有严肃的成本建模、pairing/universe admission、time-stop discipline。
- 当前 probe 样本短（`15m` 约 16 天，`5m` 约 5 天）且只用公共 K 线；它只够给 `first verdict`，不够给 admission。 
- 更重要的是：这条壳说明 **“EMA 堆叠本身并不稀缺”**；若没有 volume / regime / execution 过滤，短周期里很容易变成频繁小亏的手续费捐赠机。
