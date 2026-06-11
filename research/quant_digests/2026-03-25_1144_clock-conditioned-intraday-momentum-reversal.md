# 别把 intraday crypto 只写成“动量或反转二选一”：这篇 2022 论文更该先测的是「UTC 时钟分桶的 mode switch」raw alpha
- 时间：2026-03-25 11:44 UTC
- 类型：2022 NAJEF 论文 + Binance Futures 公共 `1h/15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：UTC 时钟分桶下的 own-past intraday return continuation / reversal（同一个短周期收益信号，在不同时钟口袋里可能分别表现为顺势或逆势）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/mean-reversion/intraday/clock-conditioned/mode-switch/time-of-day/own-past-return/binance/perpetual/btc/eth/sol/1h/15m/paper
- 证据类型：论文证据 + 本地公共数据最小快检

## 1. 这次看了什么
先回答一句：**这篇东西的 base alpha 是什么？**

不是“FOMC filter”也不是“low-liquidity gate”，而是：**同一套 own-past intraday return，在某些 UTC 时钟口袋里偏 continuation，在另一些时钟口袋里偏 reversal。**

主来源是 **Wen, Bouri, Xu, Zhao (2022), _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_**。它最适合我们 desk 的读法，不是继续争“crypto 日内到底是动量还是反转”，而是直接接受：**两种都存在，但要先按 clock bucket 拆开。** 这比把信号写成全天候单向追涨/抄底，更像能快速落地的 raw alpha 骨架。

## 2. 核心结论
- **一句话核心结论：** 对 crypto 短周期来说，更值得先测的不是“intraday 动量是否存在”这种大问句，而是 **同一 own-past return 信号在不同 UTC 时钟口袋里要不要切换成 momentum / reversal 两种模式**。
- **一句话它怎么证明：** 论文用 BTC `5m` 高频数据聚成 hourly return，做同日内 earlier-return → later-return 的 IS/OOS 预测，并进一步按 jump、流动性、FOMC、疫情阶段做分样本比较。
- 论文里最值钱的几条：
  1. crypto 的 intraday predictor **不只会给正号**，也会给负号；也就是它不像很多传统市场文献那样，默认读成“早段涨 → 末段继续涨”。
  2. 作者明确写到：predictability pattern 在 **no-jump / no-FOMC / low-liquidity** 子样本里会变，说明这不是一个全天同口径的 bar-bar 信号。
  3. 他们还做了 market-timing economic value 检验，并在 ETH / LTC / XRP 与不同交易平台上做 robustness，说明这条线不是只停在相关系数层面。
- 我补的 Binance Futures 本地快检（`BTC/ETH/SOL`，最近约 `365` 天，`1h` 信号、下一小时收益）更支持 desk 化读法：
  - 如果把 `sign(ret_t)` 当成下一小时方向信号，**全时段 pooled 只有 `+0.84 bps/h` gross**，说明“全天候无脑做”并不厚；
  - 但只保留 **top-5 continuation 时钟**（`02/05/15/16/18 UTC`），pooled gross 提升到 **`+5.76 bps/h`**；
  - 只保留 **top-5 reversal 时钟**（`04/12/13/20/22 UTC`），把同样信号改成反着做，pooled gross 也有 **`+4.31 bps/h`**；
  - 最强单口袋例子：`SOL 15 UTC` continuation 约 **`+15.85 bps/h`**，`BTC 13 UTC` reversal 约 **`+8.32 bps/h`**。
- 但也要诚实：论文提到的 **low-liquidity / no-jump 更强**，在我这版 Binance perp proxy 上并没有明显被放大；所以当前 transfer 最稳的，不是它的 microstructure 解释，而是 **“clock-conditioned mode switch” 这层 raw alpha 结构**。

## 3. 为什么和当前项目直接相关
- 这不是又一篇只讲 filter / overlay 的材料；它给的是 **可独立运行的 raw alpha**。
- 它同时把两类家族都补了：
  - continuation（顺势）
  - mean reversion（逆势）
  只是两者不是全天并存，而是按 **UTC 时钟口袋** 分配。
- 这很适合当前 desk 的 intake 逻辑：
  - 不围着 breakout / retest 内循环；
  - 直接补一个 **可完整落地的短周期 alpha skeleton**；
  - 而且可以自然拆成 `raw alpha + shared gate + execution`，方便后续 admission check。

## 3.5 策略拆解（必填）
- 方向属性：单资产、时钟分桶、可顺势也可逆势
- 基础 alpha：`signal_t = sign(ret_1h,t)`，但是否跟随该符号，取决于 `hour_of_day`
- regime：先用 `UTC 时钟口袋` 作为 primary regime；后续再叠加 `jump / FOMC / liquidity` 作为 secondary regime
- filter / veto：
  - 只在预先选定的高胜任时钟开机；
  - funding 结算前后 / 宏观事件窗先做 blackout；
  - 当过去 `N` 个样本窗口该时钟 edge 明显塌掉时暂停
- risk / sizing / execution overlay：
  - 每个时钟口袋单独 sizing；
  - `1 / realized_vol` inverse-vol 缩放；
  - 信号层保留 `1h`，执行层下沉到 `15m` 分片或 maker-first

## 4. 可复刻的最小实验
- 数据源：Binance USDⓈ-M Futures `1h` K 线（公开可得）
- universe：先做 `BTC/ETH/SOL`，后续可加 `BNB/XRP/ADA`
- 信号定义：
  - `ret_t = close_t / close_{t-1} - 1`
  - `s_t = sign(ret_t)`
  - 对每个 `UTC hour = h` 单独统计 `s_t * ret_{t+1}` 的均值
  - 若该值显著为正，则 `h` 归为 momentum bucket；显著为负，则 `h` 归为 reversal bucket
- 最小回测口径：
  1. 训练段先给每个 `UTC hour` 打标签（momentum / reversal / neutral）
  2. 测试段只在非 neutral bucket 开仓
  3. 持有 `1h`，但执行用 `4 × 15m` 切片模拟
- 最先看两个指标：
  - `gross bps per trade/hour`
  - `cost-after bps`（至少先跑 `4 / 8 / 12 bps` round-trip）

## 5. 下一步怎么测
1. **先做 walk-forward 时钟标注**：不能用全样本先知地挑好时钟；应改成 rolling `60~90` 天训练、后 `14~30` 天测试。  
2. **把 `hour_of_day` 下沉到 `15m` 执行**：信号仍由 `1h` 方向给出，但进场分四笔，比较 `next-hour market` vs `15m TWAP / maker-first`。  
3. **补 secondary regime**：在 clock bucket 之上，再叠 `no-jump / funding window blackout / event blackout / low liquidity`，看是不是能把 `gross` 进一步变厚。  
4. **做 cross-symbol pooling 与按币独立两版**：确认这条线到底是“市场共同 clock effect”，还是主要来自 `SOL/ETH` 这类弹性更大的币。  
5. **补 neutral bucket 不交易机制**：这条线很可能不是“24 小时都要有观点”，而是稀疏开火才对。

## 6. 风险与保留意见
- 论文原文主要是 **BTC `5m→1h`、同日内 earlier/later hourly pair**；我这里做的是对 perp desk 更直接的 **transfer simplification**。  
- 本地快检还没做 purged walk-forward，只是 admission 级 first verdict。  
- 当前结果是 **gross**，没有把 spread、impact、maker/taker 差异完全打进去。  
- `low-liquidity / no-jump` 这条论文里的机制，在 Binance perp proxy 上暂时没有明显增强，所以别把原文机制直接照搬成 desk 结论。  
- 这条线非常容易过拟合到“某几个小时刚好最近一年很灵”，所以 walk-forward 和 clock-stability 是硬门，不是附加项。

## 7. 来源
1. **Wen, Z., Bouri, E., Xu, Y., & Zhao, Y. (2022). _Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both_. The North American Journal of Economics and Finance, 62, 101733.**  
   - DOI: `10.1016/j.najef.2022.101733`  
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1062940822000833`  
   - DOI URL: `https://doi.org/10.1016/j.najef.2022.101733`

2. **Binance Developers. _USDⓈ-M Futures API – Kline/Candlestick Data_.**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地产物
- `reports/artifacts/quant_digests/clock_intraday_predictability_20260325_1140/summary.json`
- `reports/artifacts/quant_digests/clock_intraday_predictability_20260325_1140/hourly_pooled.csv`
- `reports/artifacts/quant_digests/clock_intraday_predictability_20260325_1140/symbol_hour_best_direction.csv`
- `reports/artifacts/quant_digests/clock_intraday_predictability_20260325_1140/panel.csv`
