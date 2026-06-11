# 别把 smart_money_bot 只读成“指标报警器”：对 short-cycle crypto desk，更该先拆的是「15m EMA20 回踩 × 短摆点再突破」这条 raw alpha
- 时间：2026-04-23 20:36 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：顺势环境里，价格先回踩 `EMA20`，随后重新突破最近 `3` 根摆点高/低，做 continuation
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：trend / momentum / pullback / continuation / EMA / breakout / Binance / 15m / 5m
- 证据类型：工程经验 + public-data portability

## 1. 这次看了什么
这次主看 2025 GitHub 仓库 **Aleks942/smart_money_bot**。repo 表面上是“聪明钱衍生品信号 bot”，但真正适合我们 desk 单独拎出来的，不是 funding / liquidations 这些泛监控，而是源码 `continuation_engine.py` 里一条很清楚的 raw alpha：**`EMA20>EMA50>EMA200` 的顺势结构成立后，若最近 `8` 根出现一次回踩 `EMA20`，且当前收盘重新突破最近 `3` 根局部高点，就追随这次恢复；空头反向同理。**

## 2. 核心结论
- 这条线的 **base alpha 很清楚**：不是猜顶底，而是赌“趋势里的浅回踩结束后，价格会继续沿原方向走一段”。
- 它最大的优点是 **规则干净、代码短、最小实验便宜**：只需要 OHLCV，就能在 `15m/5m` 直接复刻。
- 我按 desk 口径补成最小完整策略后（`next bar open` 入场、`1ATR` 止损、`1.5ATR` 止盈、`EMA20` 失守提前走、`8 bars` 超时、round-trip `8bps` 成本），**broad basket 并不成立**。
- 但它也不是完全没料：Binance USDⓈ-M 最近 `1500` 根 `15m` 数据里，**`SOLUSDT` 是唯一费后还保正的 pocket，`78` 笔、平均净收益约 `+0.23bps/笔`**；同口径全池 `8` 个 liquid majors 合计 **`578` 笔、平均净收益约 `-7.44bps/笔`**。
- `5m` 更吵：全池 **`573` 笔、平均净收益约 `-7.95bps/笔`**；说明这条 repo 里的 continuation 骨架更像 **alt-specific 15m pocket**，不是可直接全市场开机的母策略。

## 3. 为什么和当前项目有关
这条线和当前 `momentum` 主线很贴，因为它把“趋势方向过滤 / 回踩确认 / 再突破触发”三层拆得非常清楚：
- **新因子候选**：`EMA20 回踩后再突破` 本身就是 raw alpha；
- **确认层启发**：repo 里的 `compression_detector.py` 可作为前置压缩过滤，不必和 alpha 本体绑死；
- **overlay 启发**：`market_context.py` 用 BTC 大盘方向给同向信号加分，天然适合改写成我们自己的 regime / sizing gate。

## 3.5 策略拆解
- 方向属性：顺势 / 单资产 continuation
- 基础 alpha：`EMA20 pullback -> local swing break continuation`
- regime：`EMA20 > EMA50 > EMA200`（或空头反向）
- filter / veto：最近 `8` 根必须真实回踩过 `EMA20`；可选再加 range compression / BTC 同向 context
- risk / sizing / execution overlay：`next-bar open` 入场，`1ATR` 止损，`1.5ATR` 止盈，`EMA20` 失守提前离场，`8 bars` time stop，单笔固定风险或 ATR target vol sizing

## 4. 可复刻的最小实验
- 研究假设：crypto 的短周期趋势延续，不该靠“裸 breakout”追，而该靠“先回踩、再恢复”的二段式 continuation。
- 可计算定义：直接照 repo 的 `continuation_engine.py`；只把 exit 补完整，不改 entry 语义。
- 最小回测切口：Binance USDⓈ-M `SOL/ETH/BTC/BNB/XRP/DOGE/ADA/LINK`，先跑 `15m`，样本先用最近 `1500` 根；`5m` 只当 portability stress test。
- 最先看两件事：
  1. **费后平均 bps / trade** 是否至少在 `SOL + 1~2` 个 alt 上同向为正；
  2. `EMA20` 失守提前离场，和单纯 fixed-hold / bracket-only 相比，是否真能减少假恢复。

## 5. 风险与保留意见
- 这不是 broad-market alpha；当前最诚实的读法是：**repo 提供了一条可复刻的 continuation 壳，但还没证明它能跨资产 survive。**
- repo 其余 funding / liquidations / BTC context 模块，更像加分器或过滤器，**不能反过来伪装成 alpha 本体**。
- 现在唯一可见 pocket 主要集中在 `SOL 15m`，非常容易受单币弹性、单阶段趋势和费用假设影响。
- 如果下一轮把 `compression` 或 `BTC context` 加进去后，只是靠砍掉大量交易把均值抬起来，就要小心它退化成“好看但不厚”的弱 filter。

## 6. 来源
1. **Aleks942 (GitHub, 2025). _smart_money_bot_.**
   - Readable URL: <https://github.com/Aleks942/smart_money_bot>
   - Repo URL: <https://github.com/Aleks942/smart_money_bot>
   - Raw README: <https://raw.githubusercontent.com/Aleks942/smart_money_bot/main/README.md>
2. **Core source files used in this digest**
   - `continuation_engine.py`: <https://raw.githubusercontent.com/Aleks942/smart_money_bot/main/continuation_engine.py>
   - `compression_detector.py`: <https://raw.githubusercontent.com/Aleks942/smart_money_bot/main/compression_detector.py>
   - `market_context.py`: <https://raw.githubusercontent.com/Aleks942/smart_money_bot/main/market_context.py>
3. **Local portability artifact**
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/smart_money_bot_continuation_probe_2026-04-23.json`
