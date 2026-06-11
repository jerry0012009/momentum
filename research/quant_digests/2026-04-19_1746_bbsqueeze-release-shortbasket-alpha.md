# 别把这份 2026 BB Squeeze 仓只读成“波动压缩后双向追突破”：对 short-cycle crypto desk，更该先拆的是「squeeze release breakdown × alt short basket」这条 raw alpha
- 时间：2026-04-19 17:46 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `strategy/technical.py` + `strategy/signal_generator.py` + `params.py` + `core/backtester.py`）+ Binance USDⓈ-M `15m/5m` portability probe（10 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：波动压缩结束后，若价格向下释放且量能/动量同步确认，后续更容易继续走出一段 downside drift
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset-plus-basket/trend/momentum/bollinger-band/keltner-channel/bb-squeeze/release-breakdown/short-basket/atr-exit/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 本地最小 portability probe

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 很清楚，不是 filter。** 主体是 `jicheolha/keltrader`：先找 `BB` 收进 `KC` 的压缩段，等压缩结束后，若价格往外释放、成交量放大、RSI 没过热/过冷，就顺着 breakout 方向开仓，再用 `ATR stop/target + trailing` 管退出。

## 2. 核心结论
- **一句话结论：** 这条线在 crypto perp 上**不是对称双向 breakout alpha**；当前更像一条 **`15m` downside squeeze release short basket**，而不是 broad-book 双边追单系统。
- **一句话证据：** 我按 repo 默认壳重写了最小探针，在 Binance USDⓈ-M `10` 个 liquid majors 上做 `15m/5m` portability 检查，结果显示全样本明显为负，但 `15m` 的 `ETH/XRP/LINK` short pocket 转成了成本后仍为正。

关键数据点：
1. `15m` 全样本 `800` 笔，gross 约 `-5.87 bps/笔`，粗扣 `8 bps` 后约 `-13.87 bps`，说明**双向全市场照抄不成立**。
2. `5m` 更差：全样本 `671` 笔，gross 约 `-9.53 bps/笔`，不适合把 repo 直接压成更高频主信号。
3. 但 `15m` **short-only** 子桶里，`ETH/XRP/LINK` 合并 `110` 笔，gross 约 `+21.26 bps/笔`、net8 约 `+13.26 bps`、胜率约 `50.0%`。
4. 若同刻只做这三个币里 `score` 最高的一档，`top1 short router` 约 `100` 笔，gross 约 `+26.54 bps/笔`、net8 约 `+18.54 bps`、胜率约 `52.0%`。

## 3. 为什么和当前项目有关
这轮值钱的不是“又多了一个 BB 指标”，而是它给了 desk 一条**完整可落地的 raw alpha 壳**：
- entry：`squeeze release + volume ratio + momentum direction + RSI veto`
- exit：`ATR stop / ATR target / trailing`
- sizing：repo 直接按 `squeeze_duration × volume × momentum` 给 `score`，可映射成 router 或 size-up
- risk：天然适合做 `15m` 母信号，再交给 `5m` child execution

## 3.5 策略拆解（必填）
- 方向属性：单资产顺势；也可做横截面 short basket / top1 router
- 基础 alpha：压缩后向下释放的继续下跌 drift
- regime：更像 alt-perp、偏 downside、`15m` 压缩释放，而不是 `5m` 高频噪声
- filter / veto：RSI 过度超卖、成交量不确认、过宽波动带、过短 squeeze 持续都应 veto
- risk / sizing / execution overlay：`ATR stop/target + trailing`；多币同时触发时优先按 `score` strongest-only

## 4. 可复刻的最小实验
- 研究假设：`15m` 上，`BB inside KC` 持续至少 `3` 根后刚释放，且 `volume_ratio>=1.2`、方向向下的事件，在部分 alt 上会继续走弱。
- 最小定义：`prev_squeeze=1 & cur_squeeze=0 & squeeze_bars>=3 & volume_ratio>=1.2 & direction=short`。
- 最小回测切口：Binance USDⓈ-M `ETH/XRP/LINK`，近 `90~120d`，入场后用 `2 ATR stop / 3 ATR target / 32 bar timeout`。
- 最先看：`net bps/trade`、`top1 router vs equal-weight basket`。若仍为正，再测 `15m signal + 5m child execution`。

## 5. 风险与保留意见
- repo 的最优参数是按 Coinbase `2h` 做 walk-forward 调过的；本轮用的是更透明的默认壳做短周期迁移，所以结论是 portability first verdict，不是作者原结果复刻。
- 当前 pocket 明显偏 short-side，说明这条线很可能受市场阶段影响；后续必须补 regime 切片，别把它误当全天候对称 breakout。
- `ETH/XRP/LINK` 的正结果说明 raw alpha 结构能活，但 universe 选择和执行成本都很关键。

## 6. 来源
1. **jicheolha. (2026). _keltrader_. GitHub repository.**
   - Repo URL: https://github.com/jicheolha/keltrader
   - Readable URL: https://github.com/jicheolha/keltrader
2. **Source audit files**
   - README: https://github.com/jicheolha/keltrader/blob/main/README.md
   - technical: https://github.com/jicheolha/keltrader/blob/main/strategy/technical.py
   - signal generator: https://github.com/jicheolha/keltrader/blob/main/strategy/signal_generator.py
   - params: https://github.com/jicheolha/keltrader/blob/main/params.py
   - backtester: https://github.com/jicheolha/keltrader/blob/main/core/backtester.py
3. **Binance Developers. _USDⓈ-M Futures Kline/Candlestick Data_.**
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data

## 7. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_bbsqueeze_release_probe.py`
- Events：`reports/artifacts/quant_digests/2026-04-19_bbsqueeze_release_events.csv`
- Summary：`reports/artifacts/quant_digests/2026-04-19_bbsqueeze_release_summary.csv`
