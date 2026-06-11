# 别把这份 Hyperliquid 验证仓只读成 lead-lag / basis checklist：对 short-cycle desk，更该先拆的是「economically linked market pair × spread z-score fade」这条 raw alpha 壳——但 first live probe 先暴露的是 stale-leg admission

- 时间：2026-04-14 16:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/arb/signals/spreads.py` + `notebooks/03_spread_reversion.py` + `src/arb/backtest/engine.py` + `src/arb/backtest/metrics.py` + `tests/test_signals.py`）+ Hyperliquid public `allMids` live probe
- 主题标签：raw-alpha/relative-value/stat-arb/linked-market/spread-zscore/mean-reversion/hyperliquid/hip-3/spot-vs-linked-market/stale-quote/admission/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：源码规则 + repo 研究框架 + 公共 live mids first verdict

- 主题类型：raw alpha
- 基础 alpha：**把 Hyperliquid 上“经济上强相关 / 同主题 / 同底层映射”的两条市场腿视为 linked pair；当 rolling OLS hedge ratio 下的 spread 明显偏离自身均值时，做 `long cheap leg + short rich leg` 的 z-score fade，赚的是相对错位回归，而不是押单边方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = economically linked market pair spread mean reversion。**

这份新 repo 真正值得 desk 先收下来的，不是“它同时研究 lead-lag、funding、execution”这么泛，而是它把其中最贴 short-cycle raw alpha 的那条支线写得很清楚：

- 先定义两条经济上相关的腿；
- 用 rolling OLS 估 hedge ratio；
- 看 spread 相对自己历史均值偏离了多少；
- 偏得足够远就做反向收敛；
- 回到均值附近就走；
- 再看成本后是否还活着。

翻成人话：
不是赌 SPX、BNB 或 gold proxy 下一根涨跌，
而是赌 **两条本来应该跟得更近的市场腿，暂时错位后会回归。**

所以这不是 filter，也不是 overlay；它本体就是一条 **relative-value / stat-arb / spread-fade raw alpha**。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `prabhathc`
- **Year：** 2026
- **Title：** `natu`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/prabhathc/natu>
- **Repo URL：** <https://github.com/prabhathc/natu>
- **GitHub metadata：**
  - created: `2026-04-14T06:30:38Z`
  - pushed: `2026-04-14T07:42:05Z`
  - description: `HIP-3 cross-venue basis and lead-lag validation program for Hyperliquid`

### 关键源码 / 文档
- `README.md`
- `src/arb/signals/spreads.py`
- `notebooks/03_spread_reversion.py`
- `src/arb/backtest/engine.py`
- `src/arb/backtest/metrics.py`
- `tests/test_signals.py`

### 本轮自建 probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_hyperliquid_linked_market_spread_probe.py`
- 原始采样：`reports/artifacts/quant_digests/hyperliquid_linked_market_spread_probe_2026-04-14_raw.csv`
- 汇总：`reports/artifacts/quant_digests/hyperliquid_linked_market_spread_probe_2026-04-14_summary.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 最值得 desk 先吸收的，是 `linked-market spread z-score fade` 这条 raw alpha 壳；但 live public probe 先暴露出的第一瓶颈不是 z-score 阈值，而是 HIP-3 / deployer 腿在短窗口里经常明显 stale，所以下一层 admission 应先做“freshness / update-rate gate”，再谈 1m/3m/5m 真正迁移。**

### 一句话证明方式
> **证明来自两层：源码里 `spreads.py` 已把 OLS beta、z-entry/z-exit、half-life、post-cost edge 写成可复现规则；而我用 Hyperliquid public `allMids` 做 120 秒 live probe 后看到，`XAUT0/GLD`、`SPY/QQQ`、`BNB/BNB1` 这些 linked pair 的两条腿更新频率极不对称，最典型的是 `XAUT0 17 次 vs GLD 0 次`、`BNB 68 次 vs BNB1 2 次`，说明短周期 first verdict 必须先做 stale-leg veto。**

## 4. 为什么这轮值得写，而不是继续在已有 pairs / basis digest 里打转

这轮仍值得单独写，原因有三层：

1. **它不是又一篇“纯 cointegration 教学对”。**  
   已有很多 digest 在测 `cointegration / pair admission / spread fade`，但大多还是传统 `coin-vs-coin`、`spot-vs-perp`、`cross-venue futures basis`。这份 repo 把目标市场换成了 **Hyperliquid 原生 perp + HIP-3/deployer token + 外部 reference** 的混合 linked-market 宇宙，结构上更接近一条新数据面。

2. **它天然服务于用户现在想补的 raw alpha 池。**  
   这轮不是再讲 breakout、trend filter 或执行 veto，而是明确补一条 **relative-value / stat-arb / pairs / spread MR** 思路，而且能落到 `1s/1m/3m/5m/15m` 的最小实验。

3. **它很诚实地把“prove or kill”写进 repo 目标。**  
   README 明说四类假设要逐条验证，不是假定 edge 一定成立；这很适合 desk intake，因为我们要的是 **first verdict 素材池**，不是漂亮故事。

## 5. repo 真正提供了什么

## 5.1 README 已经把 raw alpha 家族拆开了
README 里把四条假设分成：

- A：lead-lag price discovery
- B：cross-venue spread mean reversion
- C：delta-neutral funding carry
- D：routing / inventory control

其中对本轮最重要的是 **Hypothesis B = structural edge**。
这等于 repo 作者自己已经帮我们把层级划好了：

- A 更像 informational alpha；
- B 是我们这轮最关心的 spread raw alpha；
- C 是 carry；
- D 是执行层。

所以这轮完全可以不被 README 的“大而全”带偏，直接盯住 B。

## 5.2 `spreads.py` 已经把最关键的 raw alpha 骨架写清楚了
`src/arb/signals/spreads.py` 的价值非常直接：

- `hedge_ratio()`：rolling OLS，且是 **no-intercept** 口径；
- `spread_series()`：`price_a - beta * price_b`；
- `z_score_series()`：spread 相对 rolling mean/std 的标准化偏离；
- `half_life()`：用 AR(1) 近似估回归半衰期；
- `signal()`：
  - `z < -z_entry` → `long_a_short_b`
  - `z > z_entry` → `short_a_long_b`
  - `|z| < z_exit` → `exit`
- `compute_stats()`：把 `avg_edge_bp`、`post_cost_edge_bp`、`ADF stationarity` 一起吐出来。

默认阈值也很清楚：
- `z_entry = 2.0`
- `z_exit = 0.5`

翻成人话就是：
> **先别谈 fancy feature，先问 linked pair 的 spread 有没有“偏离够大再回去”的基本形状。**

这正是 raw alpha 最该先回答的问题。

## 5.3 `03_spread_reversion.py` 说明它不是停在公式层
`notebooks/03_spread_reversion.py` 进一步把研究口径写死了：

- 对齐 mid prices 到统一时间网格（默认 `1s`）；
- 跑 stationarity、half-life、post-cost edge；
- 再做 `calm vs stress` 的 breakdown test；
- 明确写着：
  - **如果 `post_cost_edge_bp <= 0` 且 `is_stationary == False`，那这不是 edge，只是噪音。**

这句话很重要，因为它把 raw alpha intake 的录取线说得非常清楚。

## 5.4 回测与 falsification 层也不是空壳
虽然本轮不打算把它吹成“马上能上实盘的完整策略”，但 repo 的 backtest/metrics 层确实比很多新仓库认真：

- `engine.py` 是 event-driven 回放，不是简单 candle 回测；
- quote / trade / funding 分流；
- 可以加 `slippage_multiplier`、`fee_multiplier`、`latency_ms`；
- metrics 层预留了 falsification suite：2x slippage、2x fees、latency shock。

所以更准确的定位不是：
> “这就是一条已经验证完成的策略。”

而是：
> **这是一条 raw alpha 候选 + 一套很像 desk intake 流程的验证壳。**

## 6. 我做的 Hyperliquid public live probe：先看到的不是 edge，而是 freshness 问题

## 6.1 数据与口径
本轮 public probe 很轻，但足够说明问题：

- **数据源：** Hyperliquid public `/info type=allMids`
- **公开性：** 完全公开 REST
- **更新频率：** live mids snapshot，可按秒轮询
- **本轮采样：** `120` 秒、`1s` 一次，共 `120` 个 snapshot
- **观测 pair：**
  - `XAUT0` vs `GLD`
  - `SPY` vs `QQQ`
  - `BNB perp` vs `BNB1 spot`
- **最小实验口径：**
  1. 看每条腿在 120 秒里更新了多少次；
  2. 再看配对后的 `beta / spread_std / current_z / half_life / return corr`；
  3. 判断它像不像“可以持续交易的 live pair”，还是“偶发跳点 + 长时间静止”。

## 6.2 先记最重要的 4 个数

### 数 1：`XAUT0` 动了 `17` 次，但 `GLD` 在 120 秒里是 `0` 次更新
- `XAUT0 abs move ≈ 8.66 bps`
- `GLD abs move = 0`
- summary note：`stale_leg_detected`

这说明什么？
不是 gold proxy 这条线一定没 alpha，
而是 **当一条腿在动、另一条腿基本不动时，短周期 z-score 更像 stale-quote 计数器，而不是可执行的 spread MR。**

### 数 2：`SPY/QQQ` 两条腿在 120 秒里都是 `0` 次更新
- `spread_std = 0`
- note：`stale_leg_detected;zero_spread_variance`

这基本等于直接提醒我们：
> **不能因为 pair 在 registry 里存在，就默认它适合做 1m/3m/5m first verdict。**

### 数 3：`BNB perp` 动了 `68` 次，但 `BNB1` 只有 `2` 次更新
- `BNB abs move ≈ 21.51 bps`
- `BNB1 abs move ≈ 502.31 bps`
- `hedge_ratio ≈ 1.003`
- `spread_std ≈ 1.414`
- `current_z ≈ 0.088`
- `leg_return_corr ≈ 0.169`

这一组更有代表性：
一条腿连续小步动，另一条腿长时间静止、偶尔跳一下，
最后看起来“也不是完全不相关”，但 **它的时间结构根本不像持续、顺滑、可按 spread fade 做管理的 pair。**

### 数 4：`XAUT0/GLD` 的表面 half-life 约 `9.3` samples，不该被误读成“已经证明可做”
因为 `GLD` 这条腿根本没更新，
所以这个 half-life 更可能反映的是 **单腿在对一条冻结锚点做回摆**，
而不是双腿共同构成的 live MR。

这也是本轮最重要的坑：
> **如果不先做 freshness gate，半衰期、z-score、甚至 stationarity 都可能被 stale quotes 污染。**

## 7. 这条线对 short-cycle desk 的正确定位

## 7.1 它是 raw alpha，不该降级成 filter
这一点很明确：

- base alpha 清楚；
- 相对价值错位回归的收益来源清楚；
- 与 breakout / filter / overlay 不是一回事。

所以从题材分类上，它就是 **raw alpha / stat-arb / relative-value**。

## 7.2 但它现在还不是“拿到 repo 就能直接上”的完整策略
我给“是否可直接落地完整策略”打 `否`，原因不是 base alpha 不清楚，
而是：

1. 当前 repo 对 Hypothesis B 仍是 **validation-first**；
2. linked-market universe 里不同腿的更新频率、可成交性、staleness 问题还没被正式纳入 admission；
3. 短周期真正能不能活，先取决于 **两条腿是不是都在动**，然后才轮到 z-score / fee / sizing。

换句话说：
> **不是 alpha 没定义好，而是 live admissibility 这一步还没补齐。**

## 7.3 它为什么仍然值得进素材池
因为它补了一个很有价值的研究问题：

> **在 Hyperliquid 的原生 perp + HIP-3 / deployer token 混合宇宙里，短周期 relative-value 到底应该先看“价差”，还是先看“报价是否还活着”？**

这对 desk 很有价值：
- 如果 freshness gate 过不了，这类 pair 先别浪费回测资源；
- 如果某些子宇宙能过（例如更新更活跃、报价更对称的 pair），那它就可能成为非常好的 1m/3m/5m stat-arb intake lane。

## 8. 下一步怎么测（必须项）

我会把下一步拆成 4 个最小实验，而不是继续空谈“等更多数据”：

### 8.1 先做 **freshness admission**，再做 spread alpha
对每个候选 pair 先打 3 个 admission 指标：

1. `both_leg_updates_per_5m`
2. `stale_gap_p95_s`：两条腿最近一次更新时间差的 p95
3. `active_overlap_ratio`：两腿都在最近 `N` 秒内有更新的样本占比

只有满足例如：
- `both_leg_updates_per_5m >= 10`
- `stale_gap_p95_s <= 3`
- `active_overlap_ratio >= 0.6`

才允许进入真正的 spread MR 回测。

### 8.2 把信号压到最小可复现实验
先不要做太大而全的组合，直接做：

- 频率：`1s` mids → 聚合成 `1m / 3m / 5m`
- formation：滚动 `30m / 2h / 6h`
- signal：
  - OLS `beta`
  - spread z-score
  - `|z| >= 2` 开仓
  - `|z| < 0.5` 平仓
  - `max_hold = 5 / 15 / 30 bars`
- extra veto：若任一腿最近 `3s` 未更新，则不许开仓

### 8.3 成本阶梯要先保守，不要先假设低摩擦天堂
对每个 pair 先跑：
- `2 / 4 / 8 / 12 bps` round-trip
- 同时把 stale-leg 时段剔除前后做对照

这样能先回答：
> **这条线的 alpha 本体到底有多厚，以及它到底是被成本杀死，还是被 stale-leg 假信号污染。**

### 8.4 优先看哪几类 pair
下一轮别铺太宽，先盯 3 类：

1. **原生 perp vs 活跃 deployer token**  
   例如类似 `BNB perp vs BNB1 spot` 这种“有真实共底层映射可能性”的 pair。

2. **commodity / ETF proxy pair**  
   例如 `XAUT0 vs GLD`，但前提是 deployer 腿更新率先过 freshness gate。

3. **index proxy cluster**  
   例如 `SPX / SPY / QQQ / QQQM`，不是默认做 pair，而是先判断哪两条腿真的在 live window 里同时动。

## 9. 这轮的最终判断

我的判断很明确：

> **`natu` 这份 repo 这轮最该被吸收的不是“Hyperliquid 有很多奇怪 token”，而是它把 `linked-market spread MR` 作为独立 raw alpha 假设写得很清楚；但 public first verdict 也很明确：先别急着测收益，第一步先做 stale-leg / freshness admission，否则很多看起来漂亮的 z-score 只是报价冻结造成的幻觉。**

如果只用一句更短的话收束：

> **base alpha 是对的；第一道门不是 beta，也不是 ADF，而是两条腿到底有没有在同一个时间里活着。**

## 10. 来源

### Repo / code
- `prabhathc` (2026), **natu**. GitHub repo.  
  - Repo: <https://github.com/prabhathc/natu>
  - Raw README: <https://raw.githubusercontent.com/prabhathc/natu/master/README.md>
  - Raw `spreads.py`: <https://raw.githubusercontent.com/prabhathc/natu/master/src/arb/signals/spreads.py>
  - Raw `03_spread_reversion.py`: <https://raw.githubusercontent.com/prabhathc/natu/master/notebooks/03_spread_reversion.py>
  - Raw `engine.py`: <https://raw.githubusercontent.com/prabhathc/natu/master/src/arb/backtest/engine.py>
  - Raw `metrics.py`: <https://raw.githubusercontent.com/prabhathc/natu/master/src/arb/backtest/metrics.py>
  - Raw `tests/test_signals.py`: <https://raw.githubusercontent.com/prabhathc/natu/master/tests/test_signals.py>

### Public data used in this note
- Hyperliquid public API: `/info type=allMids`
- Live probe script: `reports/artifacts/quant_digests/2026-04-14_hyperliquid_linked_market_spread_probe.py`
- Live probe outputs:
  - `reports/artifacts/quant_digests/hyperliquid_linked_market_spread_probe_2026-04-14_raw.csv`
  - `reports/artifacts/quant_digests/hyperliquid_linked_market_spread_probe_2026-04-14_summary.csv`
