# 别把这个 2026 新 repo 只读成“low-volume reversal 真理”：对 short-cycle crypto desk，更该先回答的是「cross-sectional loser→winner fade」这条 raw alpha 先有多厚，再问 volume gate 该不该反着用
- 时间：2026-04-25 16:30 UTC
- 类型：GitHub / repo
- 主题类型：raw alpha
- 基础 alpha：横截面里短期跌得最狠的币，下一小段更容易反弹；涨得最猛的币，下一小段更容易回吐。交易上对应 long losers / short winners 的 cross-sectional reversal
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 给了完整壳，但 volume gate 方向需要先重验，不能照抄）
- 主题标签：raw-alpha / cross-sectional / relative-value / mean-reversion / loser-winner / volume-gate / 15m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo：Parnell Thrower, **Cryptocurrency Statistical Arbitrage**（`PThrower/crypto-start-arb`）。repo 口径很直白：把 `15` 个币的策略拆成两条——一条是 time-series momentum，另一条是 **cross-sectional reversal**；作者的 headline 是“reversal 在 low-volume 时段更有效”，再配 Sharpe-weighted allocation。

- Authors / Year / Title / Venue：Parnell Thrower (2026), *Cryptocurrency Statistical Arbitrage*, GitHub repo
- Repo URL：<https://github.com/PThrower/crypto-start-arb>
- Readable URL：<https://raw.githubusercontent.com/PThrower/crypto-start-arb/main/README.md>
- 关键源码：<https://raw.githubusercontent.com/PThrower/crypto-start-arb/main/crypto-stat-arb.py>

## 2. 核心结论
- **一句话核心结论**：这份 repo 最值得 desk 先拿来测的，不是“low-volume 就一定更适合做反转”这句口号，而是 **`xs loser→winner fade` 这条 raw alpha 本体，在 `15m` 映射后到底有多厚；volume 更像要重新定向校准的 filter**。
- repo 的 base alpha 是清楚的：过去 `24h` 横截面相对最差的币做多、最强的币做空；作者再用 volume z-score 去调制 reversal 和 momentum。这个 base alpha 本身就能独立复现，也能直接写成完整策略壳。
- 但源码里有个值得 desk 警惕的点：README 说“reversal 在 low-volume 更有效”，代码却是把 `reversal` 直接乘上 `tanh(volume_signal)`；如果 `volume_z` 为负，权重会被压成反向或接近关掉，**实现和口头叙述并不完全一致**。所以这轮更适合把它读成：**raw alpha 明确，volume gate 方向待复核**。
- 我补了 Binance USDⓈ-M 公共 `15m` portability probe（`BTC/ETH/SOL/XRP/DOGE/ADA`，约 `11520` bars，lookback=`96`，volume short=`96`，volume long=`2880`）：**unconditional xs reversal** 平均 **gross `+0.22 bps/bar`**、年化 gross Sharpe **`4.72`**，但按 one-way `4 bps` turnover cost 粗扣后平均 **net `-0.46 bps/bar`**。
- 真正反常识的地方在这里：按“只在低成交量时做”的 desk 化 clean gate，`volume_z<0` 后平均 **gross 只有 `+0.09 bps/bar`**，反而比 unconditional 更薄；而 **`volume_z>0` 的 high-volume 子样本 gross `+0.20 bps/bar`**、平均 turnover 还更低（约 `8.41%` vs unconditional `16.95%`），说明 **当前这批 liquid perp 的 `15m` transfer 上，volume gate 至少不该被默认写死成 low-volume admission**。

## 3. 为什么和当前项目有关
这篇东西值得进池，不是因为它已经证明“低量反转在 crypto perp 稳赚”，而是因为它同时满足 bot7 当前最看重的两点：
1. **base alpha 很清楚**：就是横截面 loser→winner fade；
2. **filter 可以单独拆出来重测**：volume 到底该当 admission、veto，还是根本别加。

对当前 desk 更有价值的读法是：先把 **raw xs reversal** 留作素材池，再把 **volume gate** 当作待验组件，而不是把两者一上来绑死。

## 3.5 策略拆解（必填）
### Base alpha
- 横截面短时超跌/超涨会出现相对价格回归：做多最近一段最弱的币，做空最近一段最强的币。

### Regime
- 暂不先加复杂 regime；先固定 liquid-major universe，看 `15m` 与后续 `5m` child execution 是否保留 gross edge。

### Filter / veto
- repo 主张的 volume gate 应先重做 A/B：`low-volume only`、`high-volume only`、`no gate` 三套并列，而不是默认信作者口头结论。

### Risk / sizing / execution overlay
- 先做 dollar-neutral / gross exposure 固定；
- 成本必须按 turnover 扣；
- 若 active names 太少（例如只剩 1 边），直接 veto，不要硬做伪中性。

## 4. 它是怎么证明这件事的
repo 自己的证据主要来自回测 summary：reversal Sharpe 写到 **`3.68`**，combined 策略写到 **`2.10`**，并声称 annual trading cost 只有 **`0.16%`**。但真正有价值的，不是照单全收这些 headline，而是把源码翻开后发现：
- reversal lookback = **`6` 个 `4h` bar（24h）**；
- volume short/long = **`6 / 180` 个 `4h` bar**；
- 成本口径写的是 **`20 bps`**，但 repo 的组合级 annualized cost 很低，和 short-cycle perp desk 的现实摩擦并不完全一致。

我补的 public-data probe 更像 first verdict：在 `15m` perp transfer 上，**raw alpha 本体还有一点 gross，但不厚；low-volume gate 没有帮忙，high-volume pocket 反而更像值得继续测**。

## 5. 对当前 desk 的可复现启发
最值得复用/复现的点有 3 个：
1. **先把 raw alpha 和 gate 拆开**，别把 repo 打包结论整包吞；
2. **先在 liquid-major 做诚实 turnover 成本检验**，再决定要不要扩到 mid-cap；
3. 若 high-volume pocket 持续更厚，这条线就不该叫“low-volume reversal”，而更像 **`xs reversal + information/flow-aware router`**。

## 6. 最小实验怎么做
建议先做一个很小但可直接复跑的实验：
- universe：`BTC/ETH/SOL/XRP/DOGE/ADA` USDⓈ-M perp
- timeframe：`15m`
- raw alpha：过去 `96` 根（24h）横截面平均收益排序，long losers / short winners
- gate A/B：`none` vs `volume_z<0` vs `volume_z>0`
- cost：按 turnover 扣 one-way `2/4/6 bps` 三档
- 先看 2 个指标：**gross bps/bar**、**cost 后 net bps/bar**

## 7. 下一步怎么测
下一步别再泛泛讲“横截面反转 + 成交量”，直接测这 4 件事：
1. **把相同 24h reversal 信号下沉到 `5m` child execution**，比较 `15m signal / 5m entry` 能否把成本压下来；
2. **扩到 mid-cap basket**（如 `LINK/AVAX/UNI/ATOM/APT/ARB/OP`），检查 repo 的 low-volume 逻辑是否其实只在次级流动性币种才成立；
3. **把 volume gate 改成 cross-sectional breadth gate**：不是逐币看量，而是看“今天是否普遍拥挤”；
4. **做 maker-first / staggered rebalance**，确认这条线到底是 raw alpha 不够厚，还是只是被 taker turnover 吃掉。

## 8. 风险与边界
- 这条线当前更像 **raw alpha 候选 + filter 重验任务**，不是现成可上线结论；
- liquid majors 上 edge 很薄，说明它很容易被执行方式和手续费吃光；
- repo 的 headline 很吸引人，但源码与叙述之间有偏差，所以**必须先尊重代码和 public probe，而不是尊重故事**。

## 9. 本地实验产物
- `reports/artifacts/quant_digests/2026-04-25_xs-lowvol-reversal_probe.py`
- `reports/artifacts/quant_digests/2026-04-25_xs-lowvol-reversal_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_xs-lowvol-reversal_probe_detail.csv`
