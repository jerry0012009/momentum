# 别把 VWAP 偏离只当确认层：这份 2026 新仓库更该先测的是「5m RSI×VWAP 偏离均值回归 + 15m anti-trend veto」完整 raw alpha
- 时间：2026-03-24 15:58 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年论文地基 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：单币短周期过冲后的均值回归（`VWAP 偏离 + RSI 极值 + 成交量脉冲`）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/vwap/rsi/volume/regime-gate/anti-trend/cost/binance/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：工程仓库 + 论文证据 + 本地公共数据最小快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 是“短周期过冲后的反向回归”**，不是 filter 本身。主材料是 2026 仓库 `jackseg80/scalp-radar` 里的 `vwap_rsi` 策略：`5m` 用 `RSI 极值 + VWAP 偏离 + volume spike` 触发，`15m` 用 `ADX/DI` 做 anti-trend veto，并带有明确的 TP/SL 与提前退出规则。

## 2. 核心结论
- 这条线是**可独立复现、可落地完整策略**的 raw alpha（entry/exit/risk/cost 框架齐全），不是纯解释。
- 但按仓库默认参数直接搬到大币并不成立：我用 Binance USDT perp 公共 5m K 线（BTC/ETH/SOL，2025-09-01~2026-03-24）做最小快检，成本假设 round-trip 10 bps，`TP=0.8% / SL=0.3% / 最长持有12根5m`：
  - **base 版（仅 RSI+VWAP+volume）**：2632 笔，胜率 `32.64%`，平均 `-9.27 bps/笔`
  - **repo 版（再加 15m anti-trend + 5m regime gate）**：399 笔，胜率 `35.09%`，平均 `-7.38 bps/笔`
- 结论翻成人话：**gate 没把负 alpha 变正，但确实把“坏交易密度”砍掉了一截**（交易数明显下降，单位亏损改善）。
- 分资产看，改善最明显在 BTC 与 SOL，ETH 基本持平偏弱，说明这条线对资产结构、波动状态和费用假设都很敏感。
- 因此它更像：**“可交易骨架已具备，但当前默认参数对 majors 不够强；要去更适配的标的池 + 参数区间 + 成本约束里找生存 pocket。”**

## 3. 为什么和当前项目有关
- 它直接补的是我们当前优先级很高的 `mean reversion / single-asset` raw alpha 素材池（不是又一个 breakout/retest 旁支）。
- 相比只讲“RSI 超买超卖”的老套路，这个仓库给了完整工程化分层：
  - alpha 本体：过冲回归
  - regime/filter：`15m ADX/DI` + `5m regime`
  - risk/execution：固定 TP/SL + signal exit
- 对 desk 的现实价值：可以很快进入 `1m/3m/5m/15m` 的最小实验迭代，不需要等难拿的数据源。

## 3.5 策略拆解（必填）
- 方向属性：单币、双向、短周期均值回归（long/short 对称）
- 基础 alpha：`price` 偏离 rolling VWAP 且 `RSI` 进入极值区后，短窗向均值回归
- regime：`5m` 仅在 `RANGING/LOW_VOL` 放行；`15m ADX` 过强趋势时禁做逆向
- filter / veto：`volume > vol_sma20 * k`；`15m ADX>阈值` veto；方向侧 `DI` 不利时 veto
- risk / sizing / execution overlay：
  - entry：信号后 next-bar open
  - exit：`TP/SL/time stop/signal exit`
  - sizing：按 ATR 或波动目标做仓位缩放（仓库默认可扩展）
  - cost：必须显式加手续费+滑点，且做 cost ladder

## 4. 可复刻的最小实验
- 研究假设：
  1) `RSI+VWAP+volume` 的过冲回归在短周期可形成 raw alpha；
  2) `15m anti-trend veto` 主要作用是“降错单密度”，而非直接抬高毛信号。
- 一个可计算定义（仓库语义对齐版）：
  - long: `RSI < rsi_long` 且 `close < vwap*(1-dev)` 且 `volume > vol_sma20*mult`
  - short: 对称镜像
  - veto: `15m ADX > adx_th` 且方向不利时不入场；仅保留 `5m RANGING/LOW_VOL`
- 最小回测切口：
  - 数据源：Binance Futures 公共 `fapi/v1/klines`（公开可得，5m 更新）
  - 资产：先 `BTC/ETH/SOL`，再扩展到流动性足够的中盘 perp
  - 周期：`5m` 执行，`15m` 过滤；再做 `3m` 速度版
- 最先看 3 个指标：
  1) 成本后 `avg net bps/trade`
  2) `trade_count` 与 `win_rate` 的交换比
  3) `tp/sl/time` 退出结构（是否被止损主导）
- **下一步怎么测**：
  1) 做参数平面，不要只测默认值：`vwap_dev(0.2~0.8)`、`rsi阈值(25/30/35)`、`vol_mult(1.5/2/2.5)`；
  2) universe 从 majors 扩到中盘 perp，并加最小成交额与点差门槛；
  3) 做成本阶梯（6/10/14 bps/round-trip）与时间段分桶，找“还能活”的局部口袋。

## 5. 风险与保留意见
- 当前最小快检结果整体仍为负，不能把它当“可直接实盘”的毕业策略。
- 这类均值回归对成本和交易环境非常敏感，默认参数跨资产迁移风险高。
- `gate` 本身也可能只是“减少交易次数”而非提升边际质量，必须用 ablation 继续验证。
- 若后续只在很窄窗口有效，要诚实定位为“条件触发型 pocket alpha”。

## 6. 来源
1) jackseg80. (2026). *scalp-radar*（GitHub repository）.
   - Repo URL: `https://github.com/jackseg80/scalp-radar`
   - Readable URL: `https://github.com/jackseg80/scalp-radar/blob/main/README.md`
   - Key strategy URL: `https://github.com/jackseg80/scalp-radar/blob/main/backend/strategies/vwap_rsi.py`

2) Svogun, I., & Bazán-Palomino, W. (2022). *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?* Journal of International Financial Markets, Institutions and Money, 77, 101601.
   - DOI: `10.1016/j.intfin.2022.101601`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1042443122000130`

3) Binance Futures API Docs（公开市场数据）
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

4) 本地最小快检 artifact（2026-03-24）
   - `reports/artifacts/quant_digests/vwap_rsi_anti_trend_probe_20260324/summary.json`
   - `reports/artifacts/quant_digests/vwap_rsi_anti_trend_probe_20260324/stats_aggregate.csv`