# 别把这个 2025 `statarb-crypto` 仓只读成“cross-sectional 教学 notebook”：对 short-cycle crypto desk，更该先拆的是「12h loser→winner fade × liquidity filter」这条 raw alpha

- 时间：2026-04-24 22:24 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `src/crypto_statarb.py` + repo PDF report）+ Binance USDⓈ-M public-data portability probe（10 liquid majors，`1h` parent，`4h` rebalance 映射）
- 主题类型：raw alpha
- 基础 alpha：**横截面短期反转：刚跌得最狠的一组币，下一小段更容易反弹；刚涨得最急的一组币，下一小段更容易回吐。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/mean-reversion/loser-winner/12h-reversal/liquidity-filter/cost-ladder/binance/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo backtest + public-data portability probe

## 1. 这次看了什么
这轮看的是 James Tilford 的 2025 GitHub 仓 **statarb-crypto**，核心材料包括：
- `README.md`
- `src/crypto_statarb.py`
- `Report/Statistical Arbitrage in Cryptocurrencies (4H Bars).pdf`

这个仓不是 pairs，也不是单币指标拼接，而是**横截面 market-neutral 反转 / 动量对照实验**：
- 在一篮子 liquid Binance USDT 币里，按最近 `H` 根收益做排序；
- 做多最弱的 `20%`，做空最强的 `20%`；
- `1 bar lag` 防止未来函数；
- 用 turnover 直接扣交易成本；
- 还能叠一个 **top-50% volume rank** 的流动性过滤。

仓里最值钱的，不是“又一个 stat-arb notebook”，而是它把 **entry / rebalance / cost / bucket diagnostic / train-test split** 都写得很朴素，适合 desk 直接最小复现。

## 2. 一句话结论
- **一句话核心结论：** 这个仓真正值得 intake 的不是“cross-sectional momentum”，而是 `H=3`（约 `12h`）的 loser→winner short-horizon reversal；但它对成本极敏感，属于**毛边不薄、净边很脆**的 raw alpha。
- **一句话证明方式：** repo 侧先用 4H Binance spot 做参数 sweep、bucket test、cost stress 和 train/test；我再把同一思想压到更 desk 化的 Binance USDⓈ-M `1h parent` 快检，看这条 alpha 到了短周期 perp 后还剩多少。

## 3. 为什么和当前项目有关
这条题目和当前 desk 贴得很近，因为它不是泛泛“均值回复理论”，而是能直接落成一条完整策略壳：
1. **raw alpha 本体清楚：** 横截面短期反转；
2. **不是单资产抄底，而是相对价值表达：** long losers / short winners，自带 market-neutral 味道；
3. **非常适合做短周期路由：** `1h` 父层决定哪批 coin 过热/过冷，`15m/5m` 子层再做 maker-friendly 入场；
4. **成本敏感度高，正好逼着我们先做 friction ladder**，这和当前 bot7 的“快出 first verdict”目标一致。

相比继续堆一个趋势 confirmation 小插件，这条至少是在补 **cross-sectional / relative-value raw alpha 素材池**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 均值回复
- 基础 alpha：最近 `H` 根跌最狠的一篮子，下一段更容易反弹；最近 `H` 根涨最猛的一篮子，下一段更容易回吐
- regime：更像发生在流动性尚可、但短线 overshoot 已出现的环境；不是极端趋势单边追涨阶段
- filter / veto：只在 volume rank 进入截面前 `50%` 的币里排序；可再加 funding / spread / listing-age veto
- risk / sizing / execution overlay：top-bottom 各 `20%` 等权，gross=1，`1 bar lag`，先做 `4h` 或 `1h` 定时再平衡；先看 `8 / 12 / 20 bps` friction ladder

## 4. repo 里最值得复用的 4 个点
1. **signal 定义非常干净**：`reversal_score = -(rets.rolling(H).sum())`，没塞花哨特征。
2. **组合逻辑可直接搬**：top/bottom quantile long-short，再 `scale_to_gross_one()`。
3. **成本不是事后嘴炮**：`turnover * cost_bps / 10000` 直接进回测主循环。
4. **bucket diagnostic 有用**：先看“最弱桶下一根是否真更强”，比只盯 Sharpe 更能分辨 alpha 本体是否存在。

## 5. 本轮最小 portability probe
我把 repo 的逻辑先 desk 化成一个最小快检：
- **数据：** Binance USDⓈ-M 公共 `1h` klines，10 个 liquid majors（`BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC`）
- **信号：** `reversal_score = -过去 H 根 1h 收益和`
- **组合：** top `20%` long / bottom `20%` short，gross=1
- **再平衡：** 每 `4` 根 `1h` bar（相当于 repo 的 `4h` / `daily-on-4H` 思路往短周期压一层）
- **执行：** `1 bar lag`
- **过滤：** 对照 `unfiltered` 与 `liq50`（当前 bar volume rank 前 50%）

先给 repo 自带的 3 个关键数：
1. **repo 最优反转窗**：`H=3 (~12h)`
2. **repo 在 20 bps 下的 unfiltered reversal（H=3）**：`Sharpe 3.596`、`CAGR 2.062`、`MaxDD -0.261`
3. **同一策略到 40 bps / 60 bps**：Sharpe 从 `3.596` 直接掉到 `0.159 / -2.910`，说明它是典型 **cost cliff alpha**

再给我这轮 perp portability probe 最有用的 4 个数：
1. **最佳口径是 `H=12`，不是 repo 的 `H=3`**：说明短周期 perp 上需要更慢一点的父层 overshoot 才勉强不那么差
2. **`liq50 + H=12 + 8 bps`**：Sharpe `-2.459`，final equity `0.952`
3. **`unfiltered + H=12 + 8 bps`**：Sharpe `-8.530`，final equity `0.884`
4. **到 `20 bps` 后几乎全面失真**：`liq50 + H=12` final equity `0.690`，`unfiltered + H=12` final equity `0.659`

翻成人话：
- **repo 里的 4H spot 反转思路本身是清楚的。**
- **但压到我们更关心的短周期 perp 口径后，原始 alpha 先没过线。**
- 流动性过滤确实有帮助，但更像“少亏一点”，还没到“可直接进复现队列”。

## 6. 风险与保留意见
1. **资产与场地变了。** repo 主要是 Binance spot 4H；我快检是 Binance perp 1H。标的微结构、费用和 funding 侵蚀都不同。
2. **现在只能说 raw alpha 在 perp 上未过线，不代表题目没价值。** 更可能说明原策略依赖更低成本 / 更慢节奏 / 更干净的现货截面。
3. **H=3 在 repo 强，不代表 desk 该照抄。** perp 上 `H=12` 相对最好，说明 portability 本身就是关卡。
4. **当前快检还没做 child execution。** 若 `1h parent` 后改成 `15m/5m` 子层限价分批，净值可能比“整根 taker”口径好一些，但不该先乐观假设。

## 7. 下一步怎么测
1. **先做 spot-vs-perp split**：同样的 `H=3/6/12`、同样 universe，同时跑 Binance spot 和 USDⓈ-M，先确认 edge 是死在 funding/fees，还是死在信号本体。
2. **做 `1h parent -> 15m child` execution test**：父层只负责选 long-loser / short-winner basket；子层在 `15m` 用 VWAP pullback 或 maker-first 入场，看能否把成本从 `8~12 bps` 压下来。
3. **做更硬的 tradability filter**：除了 top-50% volume，再加 `spread / quote depth / listing-age / funding sign`，判断这条反转是不是只在“中等流动性但没被 funding 扭曲”的币上能活。
4. **做 bucket monotonicity**：不要只看组合收益，先看短周期 `bucket 0 -> bucket 4` 的下一根回报是否仍单调；若单调性都没了，就别急着炼执行层。

## 8. 来源
- James Tilford. (2025). *Crypto Statistical Arbitrage (4H Binance Spot): Momentum vs. Short-Horizon Reversal*. GitHub repository / accompanying PDF report.
- Repo URL: <https://github.com/Jamestilfords/statarb-crypto>
- README: <https://raw.githubusercontent.com/Jamestilfords/statarb-crypto/main/README.md>
- Source code: <https://raw.githubusercontent.com/Jamestilfords/statarb-crypto/main/src/crypto_statarb.py>
- Notebook: <https://github.com/Jamestilfords/statarb-crypto/blob/main/notebooks/Crypto_Statistical_Arbitrage.ipynb>
- PDF report: <https://github.com/Jamestilfords/statarb-crypto/blob/main/Report/Statistical%20Arbitrage%20in%20Cryptocurrencies%20%284H%20Bars%29.pdf>

## 9. 本轮 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-24_xs_reversal_statarb_portability_probe.csv`
