# 别把这个 Bybit 均值回复 bot 只读成“多币对冲框架”：对 short-cycle crypto desk，更该先拆的是「24h 横截面 loser→winner fade × inverse-vol dollar-neutral sizing」这条完整 raw alpha 壳
- 时间：2026-04-22 06:22 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：过去 24 小时相对最弱的币，在接下来 4 小时更容易反弹；过去 24 小时相对最强的币，更容易回吐
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / relative-value / mean-reversion / loser-winner / inverse-vol / dollar-neutral / regime-gate / maker-first / cost / risk
- 证据类型：工程经验 + 公开数据

## 1. 这次看了什么
这轮读的是 `StaithValanthis/mean-reversion`。它不是那种只会说“均值回复有效”的教学仓，而是已经把完整交易壳写出来了：
- `README.md`：给出主策略、交易所、数据下载、回测、live/paper 入口
- `docs/STRATEGY.md`：明确 base alpha 是 **24h 横截面 short-term reversal**
- `config/config.yaml`：给出默认参数：`24h` lookback、`4h` rebalance、`top/bottom 20%`、`BTC ADX+EMA slope` regime gate、`post_only`
- `src/portfolio/weights.py`：给出 inverse-vol + dollar-neutral sizing
- `src/exchange/fees.py` + `src/execution/slippage.py`：把 maker/taker fee 与滑点单独建模

所以它最值得 intake 的点，不是“Bybit 上可以跑”，而是它把 **entry / hold / sizing / risk / cost** 五件事一次性补齐了。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的，不是“均值回复 bot”这层壳，而是一个很干净的完整 raw alpha：`24h loser-long / winner-short`，再用 inverse-vol 和 dollar-neutral 把它变成可交易组合。
- **一句话证明方式：** 作者在文档里把信号、regime gate、仓位、fee/slippage、kill-switch 都写死了；我再把它压到 Binance USDⓈ-M `15m` 的 `24h signal + 4h hold` 口径做 portability probe，看这条边在我们 desk 习惯的时间框架里还剩多少。
- Repo 默认 strongest claim 是：在 Bybit USDT perp 上做 `24h` 排名，`long bottom 20% / short top 20%`，强趋势时再把敞口缩到 `25%`，用 inverse-vol 做等风险配重。
- 我额外做的 Binance USDⓈ-M `15m` probe（近 `120d`，`12` 币池，`24h=96 bars` lookback，`4h=16 bars` hold）显示：**全 12 币篮子**平均每次 rebalance 的 gross 约 **`+9.35 bps`**，但若按 repo 的 maker-first 粗成本口径（`0.2bps maker + 2bps slippage` 单边；组合 round-trip 约 `8.8bps`）去扣，`net total return` 只剩约 **`+0.97%`**，几乎只是勉强活着。
- 更有意思的是，**liquid majors 8 币子集**（`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX`）反而更厚：平均每次 rebalance 的 gross 约 **`+13.76 bps`**，gross cumulative 约 **`+156.1%`**；粗扣 `8.8bps` round-trip 后，`net total return` 仍约 **`+36.8%`**、`net Sharpe ≈ 2.18`。
- 但如果换成更保守的 taker-like round-trip `20bps`，同一个 majors8 pocket 会直接掉到 **`-38.5%`**；这说明它不是“随便怎么打都有边”的策略，而是一个明显依赖 **maker-first / 低冲击执行** 的 relative-value 壳。
- first verdict：**这条线值得进复现池，而且更像 liquid-major `15m` relative-value sleeve；不该被读成 broad alt basket 全天候反转机。**

## 3. 为什么和当前项目有关
这条线和当前 desk 很贴，因为它正好满足现在最缺的几件事：
1. **base alpha 讲得清楚**：就是 `24h` 横截面 loser→winner fade，不是抽象“均值回复可能存在”。
2. **完整策略壳现成**：entry、exit、sizing、risk、cost 都有默认实现，不需要我们自己先脑补半套系统。
3. **能映射到 `15m / 5m / 1m`**：虽然 repo 默认用 `1h` 数据，但本质只是 `24h` ranking + `4h` holding，这个节奏完全可以直接压到 `15m` 做 parent signal，再把 `5m/1m` 留给 child execution。

更重要的是，它不是继续在 breakout / pullback 那条线上内循环，而是补了一条更正宗的 **cross-sectional / relative-value raw alpha**，刚好符合当前 intake 应该扩充素材池的方向。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / 逆势
- 基础 alpha：`24h` 横截面 loser→winner reversal
- regime：BTC 进入强趋势时，均值回复腿容易被 trend 压过去，因此应缩仓或 veto
- filter / veto：只做高流动性 perp universe；点差异常、极端波动、数据不足、强趋势环境时降权或停做
- risk / sizing / execution overlay：inverse-vol 配重、dollar-neutral、单币上限、gross cap、maker-first、daily loss cap、drawdown cap、circuit breaker

## 4. 可复刻的最小实验
- **假设：** 过去 `24h` 相对最差的 liquid majors，在接下来 `4h` 更容易相对反弹；最强者更容易回吐。
- **定义：** 每 `4h` 做一次排名；`long bottom 20% / short top 20%`；先用 equal-weight 验证方向，再切 repo-faithful 的 inverse-vol + dollar-neutral sizing。
- **最小回测切口：** Binance USDⓈ-M `15m`，`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX`，最近 `90~180d`；`lookback=96 bars`，`hold=16 bars`。
- **最该先看：** `avg gross bps / rebalance`、`friction ladder 8.8 / 12 / 20 bps`、换仓后极值 tail、以及 BTC 强趋势期是否真该 scale down 到 `25%`。
- **和短周期的关系：** 这条线本质上是 `15m` parent selector；真正决定能不能活下来的，大概率是 `5m/1m` 的 maker queue、分批撤单和持仓延续处理，而不是再把 rank window 抠小数点。

## 5. 风险与保留意见
- 我这轮 probe 先用了 **repo-faithful 的 alpha 定义 + 简化版持有篮子成本**，还没有把“上一轮持仓和下一轮持仓部分重叠时的真实 turnover 减免”细算进去；所以目前成本口径偏保守。
- 反过来说，我也还没把 **funding、maker 排队失败、事件期冲击放大** 精细建模进去；所以不能把 `+36.8% net` 当成已确认可实盘的收益承诺。
- 这条线对 **universe 选择** 很敏感：全 12 币只剩勉强正，majors8 才明显变厚，midcap6 反而在 maker-like 成本后接近打平；所以“更多币=更多 alpha”在这里并不成立。
- 它本质是高频率相对价值换仓，天然怕 **taker 化、流动性抽干、强单边趋势**。如果 child execution 做不好，gross edge 会非常快被磨平。

## 6. 下一步怎么测
1. **先做 repo-faithful rerun：** 把 BTC `ADX(14) + EMA(50) slope` regime gate 真正补进 Binance `15m` 回测，验证 `scale_factor=0.25` 是否真能改善 majors8 的 tail。
2. **再做真实 turnover 版净值：** 不按“每次全平全开”粗扣，而是按相邻 rebalance 的持仓变化量扣成本，确认前面 `8.8bps` 是否过于保守。
3. **最后做 child execution admission：** 在 `5m/1m` 上对同一批 rebalance 事件做 maker-first fill 模拟，重点看 `queue failure / timeout / partial fill` 会吃掉多少 edge；如果吃不掉，再考虑进更正式的 clean replication。

## 7. 来源
- StaithValanthis. `mean-reversion`（GitHub repo，2025/2026 活跃仓）
- Repo URL: <https://github.com/StaithValanthis/mean-reversion>
- Readable URL: <https://github.com/StaithValanthis/mean-reversion>
- Audited files:
  - `README.md`
  - `docs/STRATEGY.md`
  - `config/config.yaml`
  - `src/portfolio/weights.py`
  - `src/exchange/fees.py`
  - `src/execution/slippage.py`
- Public data portability probe: Binance USDⓈ-M perpetual `15m` klines (`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX/LINK/LTC/DOT/NEAR`)
- Probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-22_staith_xs_reversal_probe.py`
  - `reports/artifacts/quant_digests/2026-04-22_staith_xs_reversal_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-22_staith_xs_reversal_probe_trades.csv`
