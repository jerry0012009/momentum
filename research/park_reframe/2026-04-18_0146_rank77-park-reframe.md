# 2026-04-18 01:46 UTC · Rank 77 park reframe

## Scope
- source rank: `Rank 77 / alt-vs-BTC RS breadth shared gate`
- source evidence read:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/optimization_loop/2026-03-19_0315_rank77-alt-btc-rs-intake.md`
  - `research/optimization_loop/2026-03-19_0334_rank77-breadth-clean-replication.md`
  - `research/park_reframe/2026-04-15_1612_rank14-park-reframe.md`
  - `research/park_reframe/2026-04-15_0609_rank28-park-reframe.md`
- new evidence checked this round:
  - `research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
  - `research/quant_digests/2026-04-14_1914_crosscrypto-leaderbucket-laggercatchup-alpha.md`

## Why Rank 77 this round
- 本轮继续遵守 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，优先仍看 `50~79` 号段。
- `Rank 77` 已 `park`，但最近 7 天内未见这条 `bot6 park-reframe loop` 对它的正式复盘记录。
- 它同时满足“原结论像是 shared 角色放错，而主题本身并未完全失效”的条件，适合做一次低频 residual 审计。

## 1) 原 rank 为什么 park
原 `Rank 77` 被 park，不是因为 cross-asset relative-strength 主题完全没信息，而是因为它把 **alt-vs-BTC RS breadth** 写成了三条 archetype（`ema_psar_long / fib_retest_long / breakout_short`）共用的 `15m shared allow/deny gate`。

最小 clean replication（`2026-03-19_0334_rank77-breadth-clean-replication.md`）已经把这一点审计清楚：
- `baseline @ 6bps` 约 `-5.94%`；
- `breadth_24h_gate @ 6bps` 约 `-3.55%`；
- `breadth_8h_gate @ 6bps` 虽短暂到 `+0.24%`，但改善不稳；
- `breadth_dual_gate @ 6bps` 又回到约 `-4.08%`，且 `positive_asset_ratio` 只有 `33.33%`；
- 几个变体都没有把 `mean_early_fail_rate` 压到比 baseline 更诚实的水平。

所以原 `park` verdict 的审计意义必须保留：
> **旧 Rank 77 作为 queue-facing 的 shared breadth gate，没证明自己提供了跨 archetype、跨方向、跨成本都站得住的独立增量。**

## 2) 它更像 hard park 还是 soft park
结论：**soft park，但比初次 park 时更接近 hard。**

原因：
- `soft` 的部分：cross-asset / relative-strength 主题本身仍有研究价值；
- 更接近 `hard` 的部分：失败点已经很清楚，不是“再调一档 breadth 阈值”就能救，而是 **shared gate 这层职责放错**。

## 3) 有没有“可救信号”
有，但可救信号已经越来越不像旧 `Rank 77` 本体，而更像主题外流：

### A. 2026-04-17 `regime-aware XS momentum`
这条新 digest 明确把主语拆开了：
- **base alpha** 是横截面 relative-strength 排名；
- `BTC realized vol / dispersion` 更像 veto / size-down overlay；
- 也就是说，cross-asset 强弱信息若还有 residual，更自然的宿主是 **ranking / relative-value raw alpha**，而不是旧 `Rank 77` 这种 bar-level shared breadth gate。

### B. 2026-04-14 `leader-basket shock × lagger catch-up ranking`
这条证据继续说明：
- 真正更有活力的对象，是 `leader bucket / lagger catch-up / ranking` 这种 cross-sectional raw alpha；
- 不是把 `breadth_pos / breadth_neg` 直接拿来给现有三条 setup 平铺做 gate。

换句话说：
> 主题没死；
> 死的是“alt-vs-BTC RS breadth 可以当 shared queue-facing gate”这版写法。

## 4) 最值得改的唯一一刀是什么
如果还要保留旧 Rank 77 家族里唯一值得记住的一刀，它只能是：

**把 `shared breadth allow/deny gate` 降级成 `cross-sectional shell` 上的 market-alignment veto / size-down layer。**

但这条“一刀”已经明显在离开旧 Rank 77：
- 它不再服务于 `ema_psar_long / fib_retest_long / breakout_short` 这三条冻结 setup；
- 它更像新宿主（ranking / basket / residual-momentum shell）里的 overlay 语义；
- 因此它不够诚实地再被命名成 `Rank 77b`。

## 5) 是否值得形成新的 derived hypothesis
结论：**不值得。**

本轮不 draft `Rank 77b`，原因：
1. 原 `shared breadth gate` 的 blocker 没被推翻；
2. 新证据救活的是新的 `cross-sectional ranking / leader-laggard raw-alpha` 宿主，而不是旧 `Rank 77`；
3. 若硬写 `Rank 77b`，大概率只是把“cross-asset alignment 应做 overlay”这句已经很泛的主题，重复记账到旧 rank 名下，模糊原 `park` 的审计边界。

## 6) trade on / trade off（只作为不派生的判断说明）
若勉强继续派生，理论上最像的一刀会是：
- `trade on`：把 alt-vs-BTC relative-strength / breadth 只放到 cross-sectional continuation 或 leader-laggard basket 宿主里，当 veto / size-down；
- `trade off`：放弃原 `Rank 77` 的 shared gate 身份，也放弃它服务三条冻结 setup 的 queue-facing 解释。

但这恰好说明它已经不是旧 rank 的窄 reframe，而是新的 raw-alpha / shell family 线索。

## Final verdict
`keep_park`

## Short answer
- 原 rank 为什么 park：因为 `alt-vs-BTC RS breadth` 当作三条 archetype 共用的 `15m shared gate`，只留下局部少亏 pocket，没有证明出稳定独立增量。
- 它更像 hard park 还是 soft park：`soft park`，但已更接近 `hard`。
- 有没有可救信号：有，但已外流到新的 `cross-sectional ranking / leader-laggard raw-alpha` 宿主。
- 最值得改的唯一一刀是什么：把 breadth 从 shared gate 降级成新 cross-sectional shell 上的 veto / size-down layer。
- 是否值得形成新的 derived hypothesis：不值得；本轮不 draft `Rank 77b`。

## File / git hygiene
- 本轮最小改动：
  - 新增本日志；
  - 更新 `research/park_reframe/INDEX.md`；
  - 更新 `docs/PARK_REFRAME_QUEUE.md`。
- 当前工作区可能存在无关脏文件；为避免混提，本轮默认不做 commit。

## 邮件摘要建议标题
- `Rank 77 维持 park，不派生 77b`
