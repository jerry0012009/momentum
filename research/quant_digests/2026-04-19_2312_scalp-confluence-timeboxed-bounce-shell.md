# 别把这个 2026 Coinbase AI Trader 仓只读成“多 agent 大拼盘”：对 short-cycle crypto desk，更该先拆的是「range-regime oversold confluence bounce × 15m hard timeout」这条完整 raw alpha 壳
- 时间：2026-04-19 23:12 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `backend/agents/scalp_agent.py` + `backend/tests/test_scalp_agent.py` + `backend/tests/test_signal_improvements.py`）+ Binance USDⓈ-M `1m/5m` portability probe（`BTC/ETH/SOL`，公开 K 线）
- 主题类型：raw alpha
- 基础 alpha：**在低 ADX 的 range regime 里，抓“多指标同时超卖”的短时反弹；不是单看 RSI，而是 `RSI7 + Bollinger 下轨/中轨 + VWAP 偏离 + StochRSI + OBV slope + MFI7` 的 confluence long，靠 `+30bp TP / -25bp SL / 15m time stop / ATR trail` 快速出清**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/oversold/confluence/range-regime/adx/vwap/bollinger/stochrsi/mfi/obv/time-stop/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 单元测试 + Binance 公共数据最小可复现实验

## 1. 这次看了什么
先回答 base alpha：**这次主题非常明确，是一条可独立复现的单资产短周期均值回归 raw alpha，不是 filter。**

主材料是 GitHub 仓库 **`gl4500/coinbase-ai-trader`**。这个 repo 表面上是个“多 agent AI Trader”，但真正值得 desk intake 的不是它的 CNN-LSTM 外壳，而是源码里单独拎出来的 **`ScalpAgent`**：
- 它不是“AI 自由发挥”，而是**写死规则的 fast-cycle confluence strategy**；
- 进场逻辑很清楚：`score >= 5` 才开仓；
- regime 也写清楚了：**`ADX(10) < 20` 才允许 mean reversion，`ADX(10) > 25` 才切到 momentum 解释**；
- 出场也不是含糊其辞：**`+0.30% TP / -0.25% SL / 15m hard time exit / 1.5x ATR(7) trailing stop`**；
- 资金与容量也给了：**单仓最多 `20%` 资金，最多 `2` 个并发仓位**。

对我们 desk 真正重要的点在于：
> **它把“超卖反弹”从一句概念，写成了可直接落地的 entry / exit / sizing / cost 壳。**

## 2. 源码里到底是什么策略
### 2.1 entry：不是单一 RSI，而是 oversold confluence score
`backend/agents/scalp_agent.py` 里把进场写成了一个满分 `10` 分的打分器，核心规则如下：
- `RSI(7) < 25`：`+2`；`RSI(7) < 35`：`+1`
- 价格触及 `Bollinger lower band`：`+2`；跌破 `BB mid`：`+1`
- 价格显著低于 `VWAP`：`+2`；轻微低于 `VWAP`：`+1`
- `StochRSI < 20`：`+1`
- `OBV slope > 0.15`：`+1`
- `MFI(7) < 25`：`+1`

repo 原文是 `score >= 5` 可以触发，但在 `ADX < 20` 的 ranging regime 下，源码实际上把门槛再抬高了 1 分：
- **range regime：`min_score = 6`**
- trending regime：`min_score = 5`

这很关键，因为它不是“看到超卖就抄底”，而是要求**至少两三条超卖/承接证据同时出现**。

### 2.2 regime：这条 alpha 只该在横盘里做，不该在趋势里硬抄
这份代码最像成熟策略壳的一点，不是指标多，而是它承认：
- **`ADX < 20`：市场偏 range，可以做 mean reversion；**
- **`ADX > 25`：市场偏 trend，不该拿同一套 oversold bounce 逻辑去逆势硬接。**

也就是说，它把 **regime gate** 明确写进了 alpha 本体，而不是回测完以后再补解释。

### 2.3 exit：15 分钟硬超时，比“等 opposite band”更 desk-friendly
这条线真正让我觉得值得单独 intake 的，不只是 confluence entry，而是它的**时间止损很硬**：
- take-profit：`+30bp`
- hard stop：`-25bp`
- trailing stop：`1.5 x ATR(7)`
- **time exit：15 分钟**

这比很多“等回到中轨 / 对侧轨 / 均线”类脚本更适合 short-cycle desk，因为它明确表达的是：
> **如果 bounce 没在很短时间内兑现，那就把仓位当作错误，别恋战。**

## 3. 为什么它和今天已写过的几篇“反弹 / 回归”还不一样
今天其实已经写过多条 mean-reversion 线，但这篇仍然值得留下，原因不是“又一个超卖”，而是：

1. **它是完整策略壳，不是单一信号碎片。**
   - 今天有些主题更偏 router、candidate selector、或者“哪种超跌更值得做”；
   - 这篇直接给你完整的 `entry / exit / sizing / cooldown / monitoring`。

2. **它把“时间”当第一等公民。**
   - 不是只看价格回没回，而是先问：**这波 bounce 要不要在 15 分钟内兑现？**
   - 这个思路非常适合 `1m / 3m / 5m` 的实盘组件化。

3. **它天然适合作为“maker-first or child-execution”壳来二次开发。**
   - 因为 TP 只有 `30bp`，所以成本敏感度极高；
   - 这反而逼着我们认真做 `entry placement / partial fill / re-entry cooldown / execution veto`，而不是把 alpha 和 execution 混在一起。

## 4. 本地最小快检：搬到 Binance 公共数据后，edge 还剩多少？
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A：GitHub 公开仓 `gl4500/coinbase-ai-trader`
- 数据源 B：Binance USDⓈ-M 公共 K 线接口 `fapi/v1/klines`
- 公开性：公开可得，无需私钥
- 更新频率：`1m / 5m`
- 本轮最小实验口径：
  - 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
  - 周期：`1m / 5m`
  - 规则：按 repo 的 ScalpAgent mean-reversion 分支做 portable approximation
  - regime：仅保留 `ADX(10) < 20`
  - exit：`+30bp TP / -25bp SL / 15m time exit / 1.5x ATR(7) trail`
  - 成本：先按 **`4bp/side`，round-trip `8bp`** 的保守口径扣费

说明：因为 Binance 公共 K 线拿不到 repo 里 live WS price、Coinbase 真实成交结构、以及完全一致的 VWAP/OBV 内部实现，我这里做的是**可复核的近似版 portability probe**，不是宣称与 repo 回测逐点一致。

### 4.2 最关键数据点
我把 summary 落到了：
- `reports/artifacts/quant_digests/2026-04-19_scalpagent_confluence_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_scalpagent_confluence_probe_events.csv`

其中最值得记住的是这几组数：

1. **1m 版信号并不稀缺，但扣掉 8bp round-trip 后整体仍偏负。**
   - `BTCUSDT 1m`：`22` 笔，净胜率约 `22.7%`，平均单笔净收益约 `-13.1bp`
   - `ETHUSDT 1m`：`35` 笔，净胜率约 `22.9%`，平均单笔净收益约 `-10.8bp`
   - `SOLUSDT 1m`：`43` 笔，净胜率约 `41.9%`，平均单笔净收益约 `-5.9bp`

2. **5m 版也没把问题根治，最好的一组只是接近打平。**
   - `BTCUSDT 5m`：`19` 笔，净胜率约 `47.4%`，平均单笔净收益约 `-3.1bp`
   - `ETHUSDT 5m`：`25` 笔，平均单笔净收益约 `-15.0bp`
   - `SOLUSDT 5m`：`21` 笔，平均单笔净收益约 `-8.0bp`

3. **绝大多数出场并不是 TP，而是 TIME。**
   - `BTCUSDT 1m`：`TIME exit` 占比约 `77.3%`
   - `ETHUSDT 1m`：约 `71.4%`
   - `BTCUSDT 5m`：约 `73.7%`

这说明一个很直白的问题：
> **repo 的 alpha intuition 没错，但在 Binance 公共数据 + 保守摩擦口径下，bounce 经常“会反一点”，却不够快、不够深，来不及在 15 分钟内给出足够覆盖成本的利润。**

## 5. 该怎么理解这组结果
### 5.1 这不是“策略没用”，而是“execution/cost 压力非常真实”
如果一个策略的目标 TP 只有 `30bp`，那它天然就怕三件事：
1. 入场追得太高；
2. 点差/手续费吃掉太多；
3. 反弹不够快，最后被 `TIME exit` 平掉。

而这三件事，刚好都是 short-cycle desk 最擅长继续拆的地方。所以这次 digest 的价值，不是“宣布它已能直接上线”，而是：
- **repo 已经给出了完整 shell；**
- **portable probe 也已经告诉我们壳子最先死在哪——主要死在成本与兑现速度。**

### 5.2 这条 alpha 更像“需要 execution 帮忙”的 raw alpha
因此这条线最合理的定位不是：
- “再加更多指标，直到看起来更神”；

而是：
- **保留 raw alpha 本体：range-regime oversold confluence bounce**；
- 把工程力放在：
  - maker-first / passive entry
  - `1m` 触发后 `3m/5m` child execution
  - 更严格的 liquidity veto
  - 只做最强 `score 7+` 或更深 VWAP 偏离的 subset
  - symbol-specific whitelist

## 6. 这条线为什么仍然算 raw alpha，而不是 filter / overlay
因为这里回答的是：
> **到底开哪种仓，靠什么直接赚钱？**

答案很清楚：
- 开的是**单资产 long-side bounce 仓位**；
- 赚钱来源是**极短期 oversold 回归**；
- ADX、VWAP、StochRSI、MFI 这些不是独立 overlay，而是在定义这条 bounce alpha 本体的 admission 条件。

所以它不是“给别的策略打分”的 filter，而是**自己就能独立开仓、独立平仓、独立计费**的一条 raw alpha。

## 7. 风险与保留意见
1. **repo 的交易成本假设偏 Coinbase 友好。**
   源码注释里写的是 maker `0.006%/side`，round-trip `0.012%`；但如果你拿更保守的 Binance 短周期口径去测，edge 会被显著压缩。

2. **15m hard timeout 很可能既是优点，也是当前主要损失源。**
   它控制了拖泥带水，但也让大量“慢一点但方向对”的反弹来不及兑现。

3. **这条线不是全市场通杀。**
   从这次最小 probe 看，`SOL` 明显比 `BTC/ETH` 更接近可挽救；说明它可能更适合高 beta、局部 overshoot 更深的币，而不是最成熟的大币永远一把尺子通吃。

4. **它很容易和今天其他均值回归 digest 看起来“像一家人”。**
   但真正不同之处在于：这条线给了一个非常明确的**timeboxed shell**，而不是“跌多了会弹”这种泛泛说法。

## 8. 下一步怎么测
1. **先做 stronger admission 子集，而不是立刻全量实盘。**
   - 只保留 `score >= 7`
   - 或要求 `close <= BB lower` 且 `vwap_dist <= -25bp`
   - 或只做 `SOL + 1~2` 个高 beta symbol

2. **把 execution 单独拆出来测。**
   - 比较 `signal-close taker`、`next-bar passive bid`、`2~3 slice child execution`
   - 问题不是“会不会反”，而是“能不能低成本拿到这段反弹”

3. **测试 15m vs 20m/30m timeout。**
   - 如果 TIME exit 占比长期 `> 70%`，那就该认真测：
   - 是 alpha 太弱，还是 timeout 太紧

4. **加入简单流动性 veto。**
   - 例如只在最近 `N` 根 bar 的 realized spread / ATR / volume 达标时做
   - 避免把“薄流动性中的假超卖”也一起抄进去

5. **把它升级成 router，而不是全市场平均开火。**
   - 每个 bar 只选当下 oversold score 最高的 `top1 / top2`
   - 这通常比“所有满足阈值都买”更接近 desk 真实容量分配

## 9. 来源
1. **gl4500. (2026). _coinbase-ai-trader_. GitHub repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/gl4500/coinbase-ai-trader
   - Repo URL: https://github.com/gl4500/coinbase-ai-trader
   - Created: `2026-04-12`
   - Recently pushed: `2026-04-19 22:53:52 UTC`
2. **Source audit files**
   - README: https://github.com/gl4500/coinbase-ai-trader/blob/main/README.md
   - Scalp agent: https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/agents/scalp_agent.py
   - Scalp tests: https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/tests/test_scalp_agent.py
   - ADX-related tests: https://github.com/gl4500/coinbase-ai-trader/blob/main/backend/tests/test_signal_improvements.py
3. **Binance USDⓈ-M public market data**
   - Klines: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 10. 本地产物
- Probe summary：`reports/artifacts/quant_digests/2026-04-19_scalpagent_confluence_probe_summary.csv`
- Probe events：`reports/artifacts/quant_digests/2026-04-19_scalpagent_confluence_probe_events.csv`
