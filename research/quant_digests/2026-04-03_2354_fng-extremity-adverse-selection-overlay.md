# 别把 Fear & Greed 只当情绪温度计：这篇 2026 working paper 更适合先落地的是「sentiment-extremity × adverse-selection veto」共享 overlay

- 时间：2026-04-03 23:54 UTC
- 类型：2026 arXiv 全文 HTML + 同名 GitHub repo + Alternative.me / Binance Futures 公共数据最小快检
- 主题类型：overlay
- 基础 alpha：**答不清它自身的独立 base alpha，所以不把它当 raw alpha**；更准确地说，它服务于 **maker spread capture、breakout continuation、shock fade / mean reversion** 这类短周期 raw alpha，作用是识别“点差更宽、毒流更重、应缩仓或停做”的 regime
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（更适合作为共享 gate / veto / sizing overlay）
- 主题标签：overlay/regime/filter/sentiment/fear-greed/adverse-selection/spread/liquidity/market-making/breakout/mean-reversion/btc/eth/15m/5m/3m/1m/paper/repo/public-data
- 证据类型：论文证据 + 工程证据 + 公共数据快检

## 1. 这次看了什么
主材料是 **Murad Farzulla (2026), _The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets_**。先按这轮要求回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：说不清它自身是独立 raw alpha。**
>
> 它真正值得拿走的，不是“Fear & Greed 指示做多还是做空”，而是：**当情绪进入极端 fear / greed 时，市场更像进入 adverse-selection / spread-widening regime，很多短周期 alpha 应该降杠杆、提阈值，甚至直接 veto。**

所以这篇 paper 的正确定位不是 alpha 本体，而是 **shared overlay**。

## 2. 核心结论
- 一句话核心结论：**极端情绪更像“流动性撤退 / 点差变坏 / 噪声变大”的警报，而不是方向信号。**
- 一句话证明方式：**作者用 2018-02 到 2026-01 的 Fear & Greed 全历史、BTC/ETH 数据、spread proxy、Granger 检验和多轮稳健性检验，证明 extreme regime 的 spread/uncertainty 显著高于 neutral。**

最该记住的硬点：
1. **全样本验证**：Fear & Greed 全历史 **N=2,896**；在 volatility quintile 内比较，extreme vs neutral 的 premium 仍显著，**p < 0.001，Cohen’s d = 0.21**。
2. **方向不是重点，强度才是重点**：作者发现 uncertainty → spread 的 Granger 因果很强，**F = 211**；更像“极端情绪导致 liquidity withdrawal”，而不是“乐观看多、悲观看空”这么简单。
3. **可迁移性**：结果**在 ETH 上复现**，并且横跨 **7 个 market cycles 里的 6 个**都能看到同方向现象。
4. **研究者自己也很克制**：full regression 加很多控制后，regime dummy 会被吸收；但非参数分层比较仍成立。翻成人话就是：**它更适合做 regime bucket / veto，不适合硬塞进单条线性因子。**

## 3. 为什么它和当前 desk 直接相关
这篇不是补第 N 条 raw alpha，而是补一个现在很缺、但可以同时服务多条 raw alpha 的部件：

- **maker / market making**：极端情绪时点差更宽、逆向选择更重，maker 应先缩尺或关机。
- **breakout / momentum**：极端日往往波动放大但噪声也放大，不能把“更大波动”误读成“更好打”。
- **mean reversion / fade**：极端情绪会让单次冲击更深、更容易 overshoot，但如果不先做 regime bucket，容易接飞刀。

也就是说，它不回答“买还是卖”，它回答的是：

> **现在这根本该不该打这么大、该不该 maker、该不该放宽入场阈值。**

## 3.5 策略拆解（必填）
- 方向属性：shared regime / overlay / veto
- 基础 alpha：**现有短周期 raw alpha**（maker spread capture、breakout continuation、shock fade / mean reversion）
- regime：`F&G < 25` 或 `F&G > 75` 视为 extremity regime
- filter / veto：extreme regime 时，提高信号阈值；maker-only 策略可直接降档或停机
- sizing / risk：extreme regime 默认减仓 `30%~50%`，或要求更高净 edge 才开仓
- cost / execution：先把 extremity 当作 **spread / slippage / adverse-selection warning**，不是方向预测器

## 4. 我做的最小短周期映射快检
为了避免只抄 paper，我用公开数据做了一个很便宜的 short-cycle portability check：
- **Fear & Greed**：Alternative.me 公开历史 API
- **价格数据**：Binance USDⓈ-M `BTCUSDT` perpetual 公共 `15m` klines
- 样本：**2024-01-01 ~ 2026-04-03**

结果很直接：
1. extreme F&G 日的 **15m realized vol** 中位数，是 neutral 日的 **1.48x**。
2. extreme 日的 **平均 15m bar range** 中位数，是 neutral 的 **1.51x**。
3. extreme 日的 **15m p95 bar range** 中位数，是 neutral 的 **1.61x**。
4. 我再拿一个很粗的 **20-bar Donchian breakout，持有 4 根 15m** 做 sanity check：
   - extreme bucket：**1967** 笔，平均 **-3.37 bps / trade**，胜率 **43.3%**
   - neutral bucket：**1206** 笔，平均 **-0.69 bps / trade**，胜率 **46.4%**

翻成人话：**极端情绪确实把短周期市场变“更大、更吵、更难做”，但不自动把 breakout 变成更赚钱。** 所以这条线更像 **veto / sizing overlay**，不是进场 alpha。

## 5. 下一步怎么测
最值得立刻做的不是再研究情绪方向，而是把它挂到现有 raw alpha 上跑 bucket：

1. **把 desk 现有 3 类壳分别按 F&G regime 切桶**：
   - breakout / continuation
   - mean reversion / fade
   - maker / spread-capture
2. **先看 4 个指标**：`trade count`、`avg bps/trade`、`post-cost pnl`、`max adverse excursion`。
3. **先测三档规则**：
   - baseline：不加 overlay
   - soft gate：extreme 时减仓 `50%`
   - hard veto：extreme 时不做 maker，taker 只保留 top-decile 信号
4. 如果 soft/hard gate 都有效，再加第二层：**DVOL / funding / liquidation cluster** 做二次确认，防止 Fear & Greed 只是在替波动率代言。

## 6. 风险与保留意见
- Fear & Greed 本身就内含 volatility / momentum 成分，所以它不是“纯 sentiment”指标。
- 这条线**不适合伪装成逐根 1m/5m 方向信号**；更合适的定位就是 daily regime overlay。
- 若直接把 extreme fear 当成抄底、extreme greed 当成做空，证据远没有“把它当流动性风险警报”那么硬。

## 7. 来源
1. **Farzulla, M. (2026). _The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets_.**
   - Authors / Year / Title / Venue：Murad Farzulla / 2026 / *The Extremity Premium: Sentiment Regimes and Adverse Selection in Cryptocurrency Markets* / arXiv + Dissensus AI Working Paper DAI-2510
   - DOI：`10.48550/arXiv.2602.07018`
   - Readable URL：`https://arxiv.org/abs/2602.07018`
   - HTML URL：`https://arxiv.org/html/2602.07018v2`
   - Repo URL：`https://github.com/studiofarzulla/sentiment-microstructure-abm`
2. **Alternative.me Fear & Greed Index API**
   - 数据源：`https://api.alternative.me/fng/`
   - 公开性：公开可得
   - 更新频率：日频
   - 最小可复现实验口径：按日映射到 `1m/3m/5m/15m` 策略交易日桶
3. **Binance USDⓈ-M Futures Klines**
   - 数据源：`https://fapi.binance.com/fapi/v1/klines`
   - 公开性：公开可得
   - 更新频率：分钟级 / 可取 `15m`

## 8. 本地快检产物
- `reports/artifacts/quant_digests/extremity_overlay_20260403/extreme_vs_neutral_15m_metrics.csv`
- `reports/artifacts/quant_digests/extremity_overlay_20260403/breakout_shell_by_fng_bucket.csv`
- `reports/artifacts/quant_digests/extremity_overlay_20260403/daily_join_sample.csv`
