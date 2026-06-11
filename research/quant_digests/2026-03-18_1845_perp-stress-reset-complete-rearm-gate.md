# 别把 perp crowding 只当 veto：`basis neutral + OI flush + ATR compression`，更像三条收口线共用的 post-squeeze reset / re-arm gate
- 时间：2026-03-18 18:45 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/perp-stress/reset-complete/basis/open-interest/liquidation-wick/regime/filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看了 `damianpitt/capital41-indicators`（Damian Pitt / Capital41, 2026）里的 `Capital41_Crypto_Perp_Stress`。它表面在讲 perp 拥挤、OI impulse 和 liquidation wick，但对我们 desk 更值钱的旁支不是“哪里要挤爆了”，而是脚本里那句 **`resetComplete = basisNeutral + oiFlush + volCompression`**：挤仓之后，什么时候才算市场把旧仓位吐干净、可以重新让 15m 信号上桌。

## 2. 核心结论
- 一句话核心结论：**挤仓之后别急着重开，先等 perp crowding 退潮，再让 breakout-short / Fib / EMA-PSAR 重新 armed。**
- 这个 repo 最值得偷的不是 `longSqueezeRisk / shortSqueezeRisk` 标签本身，而是它把“风险释放完没有”写成了三个便宜条件：`|basis| 回到中性`、`OI 出现 flush`、`ATR 回到压缩`。
- 这比继续给三条线各补一个新 entry gate 更值钱，因为最近 desk 更缺的是 **post-event 什么时候恢复信号可信度**，不是再发明一个“看到形状就冲”的理由。
- 对 `V3 breakout-short follow-up`：跌破后最容易死在 cascade 尾端加空；`resetComplete` 更像“别在 crowd unwind 还没结束时追第二脚”。
- 对 `Fibonacci confirmation / retest_hold`：回踩能不能算 hold，不只看价格碰没碰线，也要看挤仓后的 perp 条件有没有回到正常。
- 对 `EMA / PSAR raw alpha focus`：它不像新 alpha，更像 shared allow-back filter；先让原始趋势信号避开 perp stress 尾段的脏区间。
- 它是怎么证明这点的：**不是论文统计，而是可读 Pine 脚本把状态机直接写出来**；证据强度一般，但规则很容易快速复现。

## 3. 为什么和当前项目有关
如果这轮主题和三条收口线没关系，它就不该被 bot7 认领；但这条其实很贴。

当前三条线都在收“确认 / continuation / 失效”口，而 perp 挤仓尾段恰好是最容易把这些信号一起污染的时段：
- breakout-short 会被 squeeze 反抽打脸；
- Fib retest 会在流动性清算后的假稳住里误判 `hold`；
- EMA / PSAR 会在高拥挤 + 高波动尾段被来回 whipsaw。

所以它更像一个 **shared re-arm gate**：不是决定第一下怎么进，而是决定 **事件冲击后什么时候恢复正常交易权限**。

## 4. 可复刻的最小实验
**研究假设**：在 15m crypto 里，若前面 `N=12` 根内出现过 perp stress 事件，则只有在 `resetComplete` 出现后，三条收口线的后续 continuation / retest 质量才会恢复；否则继续交易容易落在 stress aftershock 里。

**公开数据源 / 更新频率 / 最小可复现实验口径**：
1. `spot close`：Binance Spot `BTCUSDT/ETHUSDT/SOLUSDT` 15m klines（公开可得，15m）；
2. `perp close`：Binance USDⓈ-M Futures 同标的 15m klines（公开可得，15m）；
3. `open interest`：Binance Futures `openInterestHist` 15m（公开可得，15m）；
4. `liquidation wick proxy`：直接用本地 OHLCV 构造，不依赖私有 liquidation feed。

**一个可计算定义**：
- `basisPct = (perpClose - spotClose) / spotClose * 100`；
- `oiChgPct = EMA(ΔOI%, 3)`；
- `stress_event`：`|basisPct| >= 0.25%` 且 `oiChgPct >= 1.0%`，同时出现 `wick > 0.8*ATR14`、`volume > 1.2*SMA50(volume)` 的清算型长/下影；
- `resetComplete`：`|basisPct| <= 0.10%` 且 `oiChgPct <= -1.2%` 且 `ATR14 < 0.9*SMA20(ATR14)`；
- 首轮只测一个 gate：若过去 12 根出现 `stress_event`，则现有 `breakout_short / fib_retest_hold / ema_continuation` 信号必须等 `resetComplete` 后才允许触发。

**最小回测切口**：
- 标的：BTCUSDT、ETHUSDT、SOLUSDT perpetual
- 周期：15m
- 样本：近 180d
- 交易口径：`next-bar open`、`no-overlap`、成本 `6 / 10 / 15 bps per side`

**最先看 3 个指标**：
- `after-stress false continuation rate`
- `12-bar target-hit rate`
- `trade-count retention`

## 5. 风险与保留意见
- 这是一个很新的小 repo，目标时间框架原本偏 `30m / 4h`，直接外推到 15m 只能算 source intake。
- `OI` 不同交易所口径不完全一样；首轮最好先只做单交易所 clean replication，别急着跨所拼接。
- `liquidation wick` 这里只是 K 线代理，不是真实逐笔清算数据；它更像 cheap proxy，不是精确事件流。
- `resetComplete` 太严格时，可能只是把坏交易过滤掉，也把最好的 V-shaped 二次机会一起过滤掉；所以必须同步看 `trade-count retention`，不能只看胜率。

## 6. 来源
1. **Damian Pitt / Capital41 (2026)**, *capital41-indicators*, GitHub repository, DOI: N/A  
   - Repo URL: https://github.com/damianpitt/capital41-indicators  
   - Readable URL: https://github.com/damianpitt/capital41-indicators  
   - README: https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/README.md  
   - Repo API: https://api.github.com/repos/damianpitt/capital41-indicators  
   - Metadata snapshot: created `2026-01-16`, updated `2026-03-14`, `2` stars at fetch time.
2. **Damian Pitt / Capital41 (2026)**, *Capital41_Crypto_Perp_Stress.pine*, GitHub / Pine Script source, DOI: N/A  
   - Code URL: https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/Capital41_Crypto_Perp_Stress/Capital41_Crypto_Perp_Stress.pine
3. **Public market data for minimal replication**  
   - Binance Spot API: https://api.binance.com/api/v3/klines  
   - Binance USDⓈ-M Futures Klines: https://fapi.binance.com/fapi/v1/klines  
   - Binance Futures Open Interest Hist: https://fapi.binance.com/futures/data/openInterestHist

## 7. 下一步怎么测
先别把它写成“perp stress alpha”。第一步只做一个 very small ablation：**在现有三条收口线样本上，比较 `无 gate` vs `过去 12 根有 stress_event 就暂停，直到 resetComplete 才恢复`**。如果它只能砍交易数、却不能明显降低 `after-stress false continuation rate`，这条线就不该继续占用收口资源。