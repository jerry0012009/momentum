# 别把这份 2026 Kraken bot 只读成多指标堆叠：对 short-cycle desk，更该先测的是「HTF EMA gate × 15m RSI pullback continuation」
- 时间：2026-04-08 04:05 UTC
- 类型：GitHub / source audit
- 主题类型：raw alpha
- 基础 alpha：**顺势延续**；更具体地说，是 **高周期趋势已成立后，低周期做一次浅回踩 continuation**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / pullback / multi-timeframe / EMA / RSI / ATR / execution / risk
- 证据类型：工程经验 / 源码证据

## 1. 这次看了什么
这次主看一个刚更新的 repo：**Boschkoo (2026), _Kraken Trading Bot_**。我没把它当“又一个 EMA+RSI 教学 bot”，而是直接按 desk 语言拆：**base alpha 不是 MACD、也不是 Fear & Greed，而是“1h/4h 已经向上时，15m 出现轻微回踩但短均线结构未坏，随后继续顺势”**。源码里这条线已经被写成完整交易壳：`15m` 扫描、`1h+4h` 趋势门控、入场过滤、ATR 定仓、止损止盈、break-even、trailing、全局熔断，一条链是闭合的。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值得 desk 抄的，不是“六个指标同时亮灯”，而是 **HTF 趋势门控 + LTF 浅回踩 continuation** 这条完整 raw alpha。
- **一句话它怎么证明：** 不是论文统计，而是直接从 `README + KrakenBot.py + .env.example` 里看到可执行规则：哪些条件决定开仓、哪些条件只是 veto、仓位怎么按 ATR 缩放、出场怎么落地。
- 代码里入场是明确的：`15m` 上要求 `EMA9 > EMA21`、`40 < RSI < 65`、`MACD line > signal`、价格仍在 **Bollinger 中轨下方**、`ATR >= 5 EUR`，且 `1h` 与 `4h` 都满足 **close > EMA200**。
- 它不是纯信号脚本，而是完整策略：单笔风险默认 `3 EUR`、最大仓位 `50 EUR`、最多同时 `3` 个仓，止损 `2 ATR`、止盈 `3 ATR`、盈利 `+1%` 后提保本、随后 `0.5%` trailing，连续 `3` 亏或总回撤到 `-15%` 自动停机。
- 对 short-cycle desk 最值钱的启发是：**把“趋势本体”和“确认/过滤层”彻底拆开**。这里的 raw alpha 是 continuation；`RSI/MACD/BB/Fear&Greed` 更像把 entry 压到“没那么追高”的一侧。

## 3. 为什么和当前项目有关
这条线和我们现在最匹配的，不是“指标新颖”，而是它**直接补一个可落地的完整趋势壳**：
- 可以扩充 raw alpha 素材池：不是 breakout，也不是纯均线穿越，而是 **trend pullback continuation**；
- 可以训练我们把组件分层：
  - `EMA200(1h/4h)` 是 regime / direction gate；
  - `EMA9/21` 是低周期趋势未坏；
  - `RSI 40~65 + price<BB mid` 是“别买在最热那一下”的 pullback filter；
  - `ATR / break-even / trailing / global DD stop` 是 risk shell。
- 对当前 desk 尤其有用，因为它默认就是 `15m` 主框架，也很容易下采样到 `5m` 或上卷成 `1m/3m` 高频触发版。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：HTF 上涨趋势内的 LTF 浅回踩 continuation
- regime：`1h close > EMA200` 且 `4h close > EMA200`
- filter / veto：`EMA9 > EMA21`、`40 < RSI < 65`、`MACD>signal`、`close < BB mid`、`Fear&Greed >= 25`、`ATR` 不得过低、最多 `3` 个同时持仓
- risk / sizing / execution overlay：仓位 `min(3 EUR / (2*ATR), 50 EUR/price)`；止损 `2 ATR`、止盈 `3 ATR`、`+1%` 保本、`0.5%` trailing、连续亏损与总回撤熔断

## 4. 可复刻的最小实验
**研究假设：** 在 crypto 短周期里，真正值钱的不是追突破，而是 **高周期已顺风时，低周期的小回踩恢复**。

**最小定义：**
1. 标的：BTC/ETH/SOL/BNB 四个高流动 perp；
2. 周期：主实验 `15m`，附加一个更快版 `5m entry + 1h gate`；
3. gate：`1h close > EMA200`；
4. entry：`15m EMA9 > EMA21`，且 `RSI(14)` 落在 `40~65`，同时 `close < BB mid`；
5. 可选确认：`MACD line > signal`；
6. 出场：`SL=2 ATR`，`TP=3 ATR`，或先测一个更简单的 `time stop = 12 bars`；
7. 成本：先打 `8~10 bps` round-trip，再看是否还能活。

**先看两件事：**
- `post-cost expectancy / trade` 是否明显高于裸 `EMA9>EMA21` continuation；
- `win rate × payoff` 是否来自真的“回踩恢复”，而不是靠少量大单抬出来。

## 5. 风险与保留意见
- 这是 **源码证据**，不是论文证据；当前不能把 repo README 里的“能跑”自动等同于“有稳健 alpha”。
- 它本质是 **长偏 / long-only** 壳；若要迁移到 perp desk，最好单独设计一个 bearish 镜像版本，而不是直接反号。
- `ATR >= 5 EUR` 这种绝对阈值不适合多资产迁移，落地时应改成 **ATR/price 分位** 或 `ATR%`。
- 过滤条件很多，容易把交易次数压得过低；所以 first verdict 一定要做 **逐层剥皮**：`HTF gate only -> +EMA9/21 -> +RSI zone -> +MACD -> +BB mid`，别一上来就全套照抄。

## 6. 来源
1. **Boschkoo. (2026). _Kraken Trading Bot_. GitHub repository.**  
   Repo URL: `https://github.com/Boschkoo/kraken-bot`
2. **核心源码：** `KrakenBot.py`  
   Raw URL: `https://raw.githubusercontent.com/Boschkoo/kraken-bot/main/KrakenBot.py`
3. **配置样例：** `.env.example`  
   Raw URL: `https://raw.githubusercontent.com/Boschkoo/kraken-bot/main/.env.example`
