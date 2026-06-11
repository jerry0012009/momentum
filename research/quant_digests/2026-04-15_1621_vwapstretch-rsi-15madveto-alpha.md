# 别把 Scalp Radar 只读成“18 策略拼盘”：对 short-cycle desk，更该先拆的是「24h VWAP stretch × RSI exhaustion × 15m ADX veto」这条 5m mean-reversion raw alpha
- 时间：2026-04-15 16:21 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `backend/strategies/vwap_rsi.py` + `backend/core/config.py` + `backend/core/indicators.py` + `config/strategies.yaml`）+ Binance USDⓈ-M `BTCUSDT/ETHUSDT 5m/15m` 近 `60d` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：单资产、短周期的 **stretch-then-snapback mean reversion**——当价格相对 `24h rolling VWAP` 偏离过大、`RSI(14)` 已经极端、同时出现 `2x` 放量，而 `15m ADX` 没有把市场判成强趋势时，未来 `5~30m` 更容易向均值回摆；`15m ADX/DI` 在这里是 **regime/filter**，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / mean-reversion / VWAP / RSI / volume-spike / ADX / regime-veto / BTC / ETH / 5m / 15m / 30m / repo / public-data / cost / risk
- 证据类型：repo 源码 + public-data portability probe

先回答 base alpha：**很清楚，就是“短周期价格对 24h 成交量加权均值的过冲回摆”。** 这不是单纯 filter，也不是“指标越多越神”的 confluence 包装。Scalp Radar 里真正值得 intake 的，不是整套 18 策略大框架，而是 `vwap_rsi.py` 这条已经写成可下单壳的 **5m 原生均值回归策略**。

## 1. 这次看了什么
主来源：
- **Author / Owner：** jackseg80
- **Year：** 2026
- **Title：** *Scalp Radar*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/jackseg80/scalp-radar>
- **Repo URL：** <https://github.com/jackseg80/scalp-radar>

这份 repo 表面上是一个 multi-strategy 平台，但 `vwap_rsi` 这条线已经足够像完整策略壳：
- 主周期固定在 **`5m`**，过滤周期固定在 **`15m`**；
- `VWAP` 用的是 **`288` 根 5m bar = 24h rolling VWAP**；
- 入场阈值写死得很清楚：
  - `RSI(14) < 30` 且 `close < VWAP - 0.3%` 做多；
  - `RSI(14) > 70` 且 `close > VWAP + 0.3%` 做空；
  - 同时要求 `volume > 2 × volume_SMA(20)`；
- `15m ADX > 25` 直接 veto，全局避免在明显趋势盘硬接飞刀；
- `5m` 本地还要通过 regime gate：只允许 `RANGING / LOW_VOLATILITY`；
- 出场也不是只靠固定止盈止损：
  - 默认 `TP = 0.8%`
  - 默认 `SL = 0.3%`
  - 若 trade 已浮盈，且 `RSI` 回到 `50` 另一侧，就触发 `signal_exit`。

源码里最值钱的一点是：**它把 mean reversion 的 alpha body、15m 趋势 veto、5m regime gate、固定 TP/SL、以及 RSI 正常化 exit 分开写清楚了。** 这对当前 desk 很重要，因为它天然适合拆成「base alpha / filter / exit overlay」而不是糊成一团。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的不是“VWAP+RSI 指标组合”这层表皮，而是 **`24h VWAP stretch × RSI exhaustion × volume spike × 15m ADX veto` 这条 5m 原生 raw alpha 壳**。
- **一句话证明方式：** 我先做源码审计，确认 entry / veto / regime / TP / SL / signal-exit 都是闭环的；再把同一组规则迁到 Binance USDⓈ-M `BTCUSDT/ETHUSDT` 近 `60d` 公共 `5m/15m` 数据上做 quick portability probe。
- 这条线最大的优点，不是“信号很多”，反而是 **信号很稀疏**。近 `60d` 里：
  - `BTCUSDT` 只有 `56` 个信号（`26` long、`30` short）
  - `ETHUSDT` 只有 `50` 个信号（`26` long、`24` short）
  - 占全部 `5m` bar 的比例都只有约 **`0.14%~0.17%`**
- 这些信号几乎全部落在 repo 设想的 pocket：**100% 出现在 `5m RANGING` 状态，而不是趋势追单。**
- quick probe 先给出一个很实用的判断：**对 liquid majors，这条母线目前更像“优先做 long-side stretch fade”，而不是对称 long/short 一本通。**
  - `BTCUSDT`：long 信号未来 `15m` 平均 `+7.20 bps`，但 short 只有 `-0.59 bps`
  - `ETHUSDT`：long `+7.96 bps`，short `+7.85 bps`，比 BTC 对称得多
- 再看一个带简化交易壳的 non-overlapping probe（加入 `TP 0.8% / SL 0.3% / RSI signal exit`，并额外加 `12` 根 bar cap 只为界定 quick test）：
  - `BTCUSDT` long：`18` 笔，平均 **`+3.44 bps/笔`**
  - `BTCUSDT` short：`20` 笔，平均 **`-11.42 bps/笔`**
  - `ETHUSDT` long：`21` 笔，平均 **`+13.99 bps/笔`**
  - `ETHUSDT` short：`16` 笔，平均 **`+0.90 bps/笔`**

这说明当前最该 intake 的 branch 不是“照单全抄双边系统”，而是：
> **保留 `5m VWAP downside stretch long` 这条母线，再决定 short leg 是不是要更强 veto，或者干脆只保留 ETH / 高 beta majors 的 short pocket。**

## 3. 为什么和当前项目有关
这轮选它，是因为它比继续写一篇泛化 filter 摘要更值：
1. **base alpha 说得清楚**：就是 VWAP stretch mean reversion，不是把 ADX/filter 伪装成 alpha；
2. **天然贴近当前主周期**：repo 原生就是 `5m`，并明确接 `15m` 过滤；
3. **只吃公开 K 线和成交量**：不依赖难拿的订单簿、OI、资金费率或私有流；
4. **可以直接扩 raw alpha 素材池**：当前库里虽然已有不少 MR 摘要，但这条特别之处在于它把 **24h VWAP 锚、15m ADX veto、RSI 正常化 exit** 写成了非常清楚的生产骨架。

## 3.5 策略拆解（必填）
- 方向属性：单资产、逆势、均值回归
- 基础 alpha：`price vs 24h rolling VWAP` 的过冲回摆
- regime：`5m RANGING / LOW_VOLATILITY` 才允许开仓
- filter / veto：`15m ADX > 25` 直接否决；`15m DI+/DI-` 用来避免顺着强趋势方向去逆接
- risk / sizing / execution overlay：`TP 0.8% / SL 0.3%`、浮盈后的 `RSI->50` 信号退出、平台层 `weight` / risk manager / backtesting shell

## 4. 可复刻的最小实验
### 4.1 最小研究假设
**在 liquid majors 的 `5m` 上，极端偏离 `24h VWAP` 且放量的 bar，若同时不处于 `15m` 强趋势环境，则未来 `15~30m` 有可交易的 snapback；但这条 edge 可能主要集中在 long leg，而不是对称 short。**

### 4.2 一个可计算定义
在 `5m` K 线上计算：
- `RSI(14)`
- `rolling VWAP(288)`
- `volume / volume_SMA(20)`
- `ATR(14)`、`ATR_SMA(20)`
- `ADX(14), DI+, DI-`

入场规则直接照 repo：
- long：`RSI < 30`、`VWAP deviation < -0.3%`、`vol_ratio > 2`、`15m 非 bearish 趋势`、`5m regime ∈ {RANGING, LOW_VOL}`
- short：对称

### 4.3 先怎么测
1. **先分 long / short，不要先合并净值。** 这条 quick probe 已经说明对称性很差，尤其 BTC short 明显弱。
2. **先扫 `15m / 30m` 持有窗口。** 目前信号后的 `5m` 不是最稳定，`15m` 更像主 pocket。
3. **先做双层 friction ladder：** `2 / 4 / 8 bps` round-trip；因为信号稀疏，但单笔 edge 也不算厚。
4. **只先测 `BTC / ETH / SOL` 三个 liquid majors。** 不要一开始就扩到长尾山寨。
5. **第二轮再加 short veto：** 比如 `BTC short` 额外要求 `15m DI- 明显占优` 或 `5m realized vol` 不过热，验证 short leg 为什么塌得更快。

## 5. 风险与保留意见
- 这次 portability probe 用的是 Binance USDⓈ-M 公共 K 线，不是 repo 原始 Bitget live 环境；执行质量、手续费和滑点都还没 fully matched。
- quick trade sim 加了 `12 bar` cap，只是为了做 bounded first verdict；repo 原始逻辑并没有硬性 time stop，所以不能把这组结果当成 production 回测。
- 信号非常稀疏，优点是少噪音，缺点是样本数也小；近 `60d` 只能先给 first verdict，不能下大结论。
- 当前最值得保留的是 **alpha body + veto structure**，不是参数神圣化。`0.3%` 的 VWAP 偏离、`2x` volume spike、`30/70` RSI 阈值都应该做邻域稳定性检查。

## 6. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-15_1621_vwapstretch-rsi-15madveto-alpha.md`
- portability artifacts：
  - `reports/artifacts/quant_digests/2026-04-15_vwap_rsi_portability_probe.py`
  - `reports/artifacts/quant_digests/vwap_rsi_probe_20260415_1621/signal_summary.csv`
  - `reports/artifacts/quant_digests/vwap_rsi_probe_20260415_1621/signal_details.csv`
  - `reports/artifacts/quant_digests/vwap_rsi_probe_20260415_1621/sim_trades.csv`
  - `reports/artifacts/quant_digests/vwap_rsi_probe_20260415_1621/sim_trade_summary.csv`
  - `reports/artifacts/quant_digests/vwap_rsi_probe_20260415_1621/meta.json`

## 7. 来源
1. **jackseg80. (2026). _Scalp Radar_. GitHub repository.**
   - Readable URL: <https://github.com/jackseg80/scalp-radar>
   - Repo URL: <https://github.com/jackseg80/scalp-radar>
2. **Key source files used in this digest**
   - <https://raw.githubusercontent.com/jackseg80/scalp-radar/main/README.md>
   - <https://raw.githubusercontent.com/jackseg80/scalp-radar/main/backend/strategies/vwap_rsi.py>
   - <https://raw.githubusercontent.com/jackseg80/scalp-radar/main/backend/core/config.py>
   - <https://raw.githubusercontent.com/jackseg80/scalp-radar/main/backend/core/indicators.py>
   - <https://raw.githubusercontent.com/jackseg80/scalp-radar/main/config/strategies.yaml>
