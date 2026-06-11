# 别把高 VPIN 当 15m 方向确认：它更像 breakout-short / Fib / EMA-PSAR 的 two-speed jump-risk overlay
- 时间：2026-03-23 05:10 UTC
- 类型：近 5 年论文 + 开源实现仓库 + Binance 公共数据最小快检
- 主题类型：overlay
- 基础 alpha：breakout-short / fib retest / ema-psar continuation（既有 setup）
- 是否可独立复现：否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：breakout-short/final-verdict/fibonacci/retest-hold/ema/psar/vpin/order-flow-toxicity/jump-risk/regime-gate/position-sizing/risk-overlay/crypto/5m/15m
- 证据类型：论文证据 + 工程实现 + 公共数据快检

## 1. 这次看了什么
这次主读的是 **Kitvanitphasu, Kyaw, Likitapiwat, Treepongkaruna (2025/2026)**：*Bitcoin wild moves: Evidence from order flow toxicity and price jumps*。它最值得我们 desk 借的旁支，不是“再造一个入场 alpha”，而是把 `order-flow toxicity (VPIN)` 定位成 **jump-risk 的 regime 层**。实现参考用的是开源仓库 `hanxixuana/flowrisk`（VPIN 递归估计器）。

## 2. 核心结论
- **一句话核心结论：** VPIN 在 15m 上更像“这段行情会不会突然乱跳”的风险温度计，不该直接当 breakout-short/Fib/EMA 的方向确认键。
- **一句话证明方式：** 论文用高频微观结构建模（VAR + jump test）证明 `VPIN -> future jumps` 有预测力；我再用 Binance 公开 1m/15m 数据做了最小代理快检，验证“高 VPIN 提升 jump 概率，但不稳定提升方向胜率”。
- 论文层面：作者报告 **VPIN 对未来 price jump 有显著预测力**，且 VPIN 与 jump size 具有正序列相关；这支持它做风险/状态指标，而非单向预测器。
- 本地快检（2026-02-21~2026-03-23，BTC/ETH/SOL，1m 构造 VPIN、映射到 15m）：高 VPIN（Top20%）相对低 VPIN（Bottom20%）的 `jump_proxy hit rate` 平均约 **1.10x**（BTC `1.07x`，ETH `1.13x`，SOL `1.11x`）。
- 同期 `|future 4-bar return|` 在高 VPIN 组平均约为低 VPIN组的 **1.18x**，说明更像“波动放大/路径更毛刺”。
- 但对 `short breakout` 方向并不友好：在 20-bar 跌破代理事件里，高 VPIN 组 4-bar short PnL 均值约 **-0.17%**，低 VPIN 组约 **+0.16%**；且 short failure（4根内收回破位线）平均高出约 **+9.6pp**。=> 高 VPIN 更像“更乱”，不是“更顺”。

## 3. 为什么和当前项目有关
- **V3 final-verdict / breakout-short follow-up：** 高 VPIN 不是 continuation-confirmation，反而提示“路径更跳”，应优先用于 `tighten timeout / 降仓 / 提高否决阈值`。
- **Fibonacci confirmation / retest_hold：** 在高 VPIN 段，回踩更容易 overshoot + 快速反抽，`retest_hold` 需要更严格（例如额外要求 reclaim + 下一根不失守）才更诚实。
- **EMA / PSAR raw alpha focus：** EMA/PSAR 可以继续做方向骨架；VPIN 负责风险速度挡位（low=normal，mid=halfsize，high=tight/甚至veto），避免把“噪声跳动”误判为趋势质量。
- 这题比继续横向发散更值得的原因：它是三条收口线都能共用的一层 risk overlay，而且公开数据可分钟级拉取，最小实验可当天复现。

## 3.5 策略拆解（必填）
- 方向属性：顺势框架上的风险覆盖层（非独立方向 alpha）
- 基础 alpha：沿用 breakout-short / Fib / EMA-PSAR 现有触发
- regime：`VPIN` 分位 + jump-risk 状态（low / mid / high）
- filter / veto：高 VPIN 时提高 entry-confirmation 门槛，或对“弱确认”直接 veto
- risk / sizing / execution overlay：`size × {1.0, 0.5, 0~0.25}` + 更短 timeout + 更快 fail-fast

## 4. 可复刻的最小实验
- **研究假设：** 在 15m 策略上，`VPIN two-speed overlay` 相比 always-on，可降低假 follow-up 和尾部回撤，而不显著破坏可交易样本。
- **数据源（公开可得）：**
  1. Binance USDⓈ-M `fapi/v1/klines` 1m（含 taker buy volume，公开 REST）；
  2. Binance USDⓈ-M `fapi/v1/klines` 15m（事件与绩效评估）；
  3. 更新频率：1m/15m 持续更新，免费可拉取。
- **最小口径：**
  1. 用 1m `taker_buy_volume` 与 `sell_volume` 做 volume-bucket VPIN（bucket≈日均成交量/50，VPIN窗=50 buckets）；
  2. 映射到 15m 后按滚动分位分成 `low(<q40) / mid(q40~q80) / high(>q80)`；
  3. 把三条策略现有触发分别跑三组：`base` vs `base+binary(high veto)` vs `base+two-speed sizing`。
- **先看 2 个指标：**
  1. `post-cost short/long expectancy`（按方向拆开，不合池）；
  2. `N-bar failure rate`（breakout 回收、Fib 失守、EMA/PSAR 假翻转）。
- **下一步怎么测（必须项）：**
  - 第一轮先固定 `BTC/ETH/SOL, 15m, 180d, no-overlap, 6/10/15 bps`，只比 `binary veto` 和 `two-speed sizing`；
  - 若 `two-speed` 仅在降低回撤有效、但收益拖累过大，则保留为 `risk-only mode`；
  - 若在 breakout-short 上出现“失败率下降且收益不塌”，再考虑把它升级到 V3 follow-up 默认风控层。

## 5. 风险与保留意见
- 本轮 VPIN 是基于 Binance 1m taker volume 的可复现代理，不是完整订单簿级 microstructure 还原。
- 样本窗口仅约 30 天，结论用于“是否值得进入研究池”而非“直接上线”。
- VPIN 可能更像“噪声+流动性压力”联合温度计：适合风控和仓位，不适合直接当方向信号。

## 6. 来源
1. Kitvanitphasu, A., Kyaw, K., Likitapiwat, T., & Treepongkaruna, S. (2025). *Bitcoin wild moves: Evidence from order flow toxicity and price jumps*. **Research in International Business and Finance** (2026 print, Vol.81, 103163).  
   DOI: `10.1016/j.ribaf.2025.103163`  
   Readable URL: `https://doi.org/10.1016/j.ribaf.2025.103163`  
   Repo URL: `N/A（论文未给官方代码仓库）`

2. Han, X. (hanxixuana). (2018, updated). *flowrisk: A Python Implementation of Measures for Order Flow Risk, e.g. VPIN*. GitHub Repository.  
   Readable URL: `https://github.com/hanxixuana/flowrisk`  
   Repo URL: `https://github.com/hanxixuana/flowrisk`

3. Easley, D., López de Prado, M., & O’Hara, M. (2012). *Flow toxicity and liquidity in a high-frequency world*. **Review of Financial Studies**, 25(5), 1457–1493.  
   DOI: `10.1093/rfs/hhr100`  
   Readable URL: `https://doi.org/10.1093/rfs/hhr100`

4. Binance Developers. (n.d.). *USDⓈ-M Futures API – Kline/Candlestick Data*.  
   Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

- 本轮最小快检产物：`reports/artifacts/quant_digests/vpin_jump_toxicity_proxy_20260323/`
