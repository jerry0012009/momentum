# 2026-04-02 01:59 UTC · Rank 285 / 24h losers-vs-winners XS reversal × dispersion / turnover：P2 exit → one-time P2->P1 re-scope

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`
- 本轮只执行 `cycle_plan` 第 2 个 pending 小点
- 正式结论：`one-time P2->P1 re-scope`

## 1. 本轮只回答的唯一问题
> 在 admission 第一半已经确认“现实 perp edge 只存在于条件化 pocket、不是 broad top-liquid 普适结构”之后，这条线是否已经足够诚实地进入 `P3 / paper launch queue`；如果还不够，是否存在唯一明确的 re-scope 方向，还是应该直接退回 background/P0？

## 2. 本轮允许使用的现有证据
本轮不新增 story，只收口已经落库的几组证据：

1. `research/quant_digests/2026-03-25_0631_liquidity-split-tail-reversal-24h-loser-basket.md`
   - `mature tail` bucket 在 Binance USDⓈ-M perp、`15m` 信号下：
   - `1h hold` 平均净收益约 `+0.942 bps / rebalance`，净 Sharpe 约 `1.758`
   - `4h hold` 平均净收益约 `+3.560 bps / rebalance`，净 Sharpe 约 `1.741`
   - 同次实验中 majors momentum 腿在 `15m/1h/4h` 全为负

2. `research/quant_digests/2026-03-25_1323_xs-interactions-highrv-loser-reversal.md`
   - `high-RV` bucket 的 `24h loser-vs-winner` reversal：
   - `1h hold, 15m rebalance` 平均毛收益约 `+2.31 bps / rebalance`
   - `4h hold, 1h rebalance` 平均毛收益约 `+7.99 bps / rebalance`
   - 文档已明确写出：这条腿的 break-even 更接近 `~8 bps round-trip`
   - 同目录 timeseries 显示 `high_rv` 月度毛收益并不平滑：`2025-12` 约 `-1.59 bps`，`2026-01` 约 `+2.27 bps`，`2026-02` 约 `+1.10 bps`，`2026-03` 约 `+4.62 bps`

3. `research/quant_digests/2026-03-26_0449_repo-xs-reversal-cost-cliff-transfer-check.md`
   - 更宽的 short-term reversal 母体压到 fast-lane perp 后，`1h / 15m` 成本后都明显失败
   - `1h` 版本在 `8 bps` 下约 `Sharpe -3.04 / total return -15.4%`
   - `15m` 版本更差

## 3. 对出口决策最关键的三轴判断

### 3.1 time stability
这条线还不能被诚实描述成“稳定贯穿样本的 ready-to-paper pocket”。

原因不是它完全只靠最后几天爆发，而是：
- `high-RV` 口袋在现有 timeseries 里呈现明显的近期增强：`2025-12` 为负，`2026-01~03` 转正，且 `2026-03` 最强；
- `mature tail` 那条净正证据来自近 `90d` 汇总，不是更长窗口、也还没有更细的分段 OOS 台账；
- 也就是说，当前时间轴更像“最近几个月存在 pocket”，还不够像“已经跨时段稳定到可以直接接 paper runner”。

### 3.2 parameter stability
这条线不是单一参数幻觉，但它确实高度依赖**更慢 cadence / 更窄 bucket**。

已经能明确看到：
- `tail reversal` 在 `15m hold` 成本后为负，`1h/4h hold` 才转成净正；
- `high-RV` 口袋从 `1h hold` 到 `4h hold` 毛边明显变厚，但同时 round-trip break-even 也几乎贴着 `~8 bps`；
- broad fast-lane transfer 明确失败，说明不能把它写成“任意 rebalance/hold 都能活”的通用 reversal alpha。

因此，本轮更诚实的参数结论是：
> 能活下来的不是 broad 版 `24h XS reversal`，而是**只在 `mature liquid tail` 或 `high-RV` 子桶里、并且偏向 `1h~4h` 慢节奏持有**的窄参数面。

### 3.3 honesty / execution realism
这也是本轮最 decisive 的 blocker：
- `high-RV` pocket 当前仍主要是 gross 证据，且 `4h hold` 的 break-even 已经贴近 `~8 bps round-trip`；
- broad 母体压到 perp fast-lane 后，在 `4/8 bps` 下都明显不够；
- 因此如果把对象继续写成“top-liquid broad losers-vs-winners reversal 已足够进入 paper launch”，那是在把条件化、慢节奏、可能偏 maker/mixed 的口袋，误写成普适 ready-to-paper alpha。

这还不是 fatal flaw——没有看到明确 lookahead / leakage / 伪成交的致命作弊——但它已经足够说明：
> 当前对象定义太宽，paper-ready 主语还没站稳。

## 4. 为什么这轮不升 `P3`
因为 `P3` 需要的是一个已经足够诚实、可以直接接 paper wiring 的主语；而 `Rank 285` 当前最可靠的存活部分，已经明显不是 broad `24h losers-vs-winners XS reversal`：

- cross-asset 上，它不是 broad top-liquid 普适结构；
- time 上，现有更厚的 `high-RV` 口袋带有近期增强色彩；
- parameter / execution 上，只有更慢 cadence、窄 bucket 才显示出生存线，fast-lane broad transfer 明确失败。

所以这轮如果强升 `P3`，等于把“条件化 pocket”误报成“paper-ready family”。这不诚实。

## 5. 为什么也不直接 `drop_to_background / P0`
因为这条线并没有被 admission 判死：
- `mature tail` 口袋已经有成本后净正；
- `high-RV` 口袋也有持续为正的 gross 结构，且 `1h~4h` hold sweep 不是单一点孤岛；
- 没看到足以一票否决的致命 honesty flaw。

因此它的问题不是“根本没 alpha”，而是：
> **alpha 的真实适用范围比当前 P2 主语窄得多。**

这正是 policy 允许的一次性 `P2->P1 re-scope` 场景。

## 6. 唯一明确的 re-scope 方向
本轮不允许“再看看”。唯一明确、可执行的 re-scope 方向是：

> **把 `Rank 285` 从 broad `24h losers-vs-winners XS reversal × dispersion / turnover`，一次性收窄成“只面向 `mature liquid tail` / `high-RV` 条件化子桶、并只保留 `1h~4h` 慢节奏持有的 crypto XS reversal pocket`”。**

更直白地说：
- 不再把 `majors` 或 broad top-liquid 普适性写进主语；
- 不再默认 fast-lane `15m` taker/mixed 壳子；
- 后续若要重开，应只围绕这个窄版对象检查：
  1. `mature tail` 与 `high-RV` 两个 pocket 是否能被统一成一个诚实的 narrow paper spec；
  2. 在 `1h~4h`、更慢 rebalance、maker/mixed realism 下是否仍保留足够净边；
  3. 时间稳定性是否不只是 2026Q1 的局部 burst。

## 7. 正式 verdict
`Rank 285 / 24h losers-vs-winners XS reversal × dispersion / turnover`：`one-time P2->P1 re-scope`

一句话收口：

> `Rank 285` 的 broad `24h XS reversal` 叙事还不够诚实进入 `P3`：当前成本后净边主要来自 `mature liquid tail` 与 `high-RV` 条件化子桶，且更依赖 `1h~4h` 慢节奏持有；但对象也未被判死，因此本轮不升 P3、也不回 P0，而是一次性从 P2 回到 P1，重写成只面向条件化子桶与慢节奏执行的窄版 reversal pocket。

## 8. 对 runtime 的写回语义
- `Active P2 slot`：本轮出口决策已完成，`Rank 285` 不再保留为 active P2
- `Background pool`：记录该对象本轮不是 fatal drop，而是带着明确 re-scope 方向退出前排
- `cycle_plan[2]`：写成 `done`

## 9. 一句话 result
`Rank 285` 的 broad `24h XS reversal` 还不够诚实地直接进 P3：当前成本后净边主要由 `mature liquid tail` 与 `high-RV` 条件化子桶、以及 `1h~4h` 慢节奏持有支撑；因此本轮执行 `one-time P2->P1 re-scope`，不再把 broad top-liquid 普适 reversal 继续留在 Active P2。