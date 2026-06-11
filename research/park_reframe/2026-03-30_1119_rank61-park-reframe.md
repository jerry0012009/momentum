# 2026-03-30 11:19 UTC · Rank 61 park reframe review

## Scope
- Source rank: `Rank 61 / lower-TF volume-delta polarity mismatch veto`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: 在不推翻原 `park` 的前提下，`Rank 61` 是否还值得派生一条新的窄 reframe hypothesis。

## Why this rank this round
- 轮转优先级仍先看 `Rank 50+`，且 `Rank 61` 过去 7 天内还没有被 `bot6` 复盘过。
- 它是一个典型的“主题未死、但原角色明显错位”的 parked rank，适合做低频审计。
- 最近又新增了多条与 order-flow / OFI / signed-flow 直接相关的新证据：
  1. `research/quant_digests/2026-03-24_1216_orderflow-xs-imbalance-cost-cliff.md`
  2. `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
  3. `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
  4. `research/quant_digests/2026-03-30_0944_ofi-fillaware-maker-taker-alpha.md`
- 本轮要回答的不是“flow 有没有信息”，而是：这些新证据会不会诚实地支持 `Rank 61b`，还是反而进一步说明原 `Rank 61` 的 residual value 已经上移到更上位的 microstructure raw-alpha / execution family。

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-18_1740_rank61-source-intake.md`
  - `research/optimization_loop/2026-03-18_1800_rank61-clean-replication-park.md`
  - `research/quant_digests/2026-03-24_1216_orderflow-xs-imbalance-cost-cliff.md`
  - `research/quant_digests/2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
  - `research/quant_digests/2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md`
  - `research/quant_digests/2026-03-30_0944_ofi-fillaware-maker-taker-alpha.md`

## 1) 原 rank 为什么 park？
原 `Rank 61` 想验证的是：
- 当 `breakout-short / Fib / EMA-PSAR` 这类 `15m` setup 已经触发时，若入场前最后 `3~5` 分钟 lower-TF volume-delta polarity 与 setup 方向不一致，就用它做 shared veto / confirmation。

最小 clean replication（`BTC/ETH/SOL 120d 15m` 主图 + `1m` 子周期 proxy，`next-bar open + no-overlap + hold 8 bars`）给出的结论很直接：
- `ema_psar_long + opposite_delta_veto` 仍约 `-3.60%`，trade_count_retention 约 `38.10%`
- `fib_retest_long + opposite_delta_veto` 虽留下约 `+0.71%` 的薄 pocket，但 retention 只有约 `36.36%`
- `breakout_short + opposite_delta_veto` 仍约 `-3.28%`，positive_asset_ratio=`0/3`
- `same_direction_gate / strong_same_direction_only` 也没形成可迁移、可部署的跨 setup 增量

翻成人话：
**不是 flow 没信息，而是“把 lower-TF delta 当 15m 三条线共用入场前 veto”这层写法没有救活主线，改善主要只是薄样本筛选。**

## 2) 它更像 hard park 还是 soft park？
**结论：soft park，但现在比原审计时更偏硬。**

原因：
- soft 的部分在于：flow / OFI / signed-volume 主题本身显然还活着，最近 1 周的新 digest 反而继续强化了这一点；
- hard 的部分在于：活下来的位置越来越清楚地不在原 `Rank 61` 这个 `15m shared veto` 角色里，而在更上位的 **1m/3m single-asset microstructure raw alpha / fill-aware execution / event-driven flow shock** family。

所以更诚实的读法不是“Rank 61 还差一点”，而是：
- 原 Rank 61 这层角色摆放本身就错了；
- 且最近新证据并没有把它拉回原角色，反而让它更偏硬。

## 3) 有没有“可救信号”？
**有，但这些信号越来越不像在救 `Rank 61` 本体。**

### 可救信号 A：flow 主题在更短时钟 raw alpha 上确实活着
`2026-03-25_0318_single-asset-microstructure-taker-alpha.md` 与 `2026-03-30_0944_ofi-fillaware-maker-taker-alpha.md` 都在强调：
- 更值得先测的是 `OFI / VWAP pressure / maker-taker split / fill-aware gating` 这种 **完整 raw alpha / execution skeleton**；
- 而不是把 flow 压缩成一条 setup 前最后几分钟的 binary veto。

### 可救信号 B：order-flow shock 更像事件型 alpha，不像 shared confirmation
`2026-03-28_1613_stablecoin-orderflow-shock-path-alpha.md` 指向的是：
- signed order-flow shock 之后的 `1 bar` 延续 / `5m` inventory fade；
- 这更像 **事件驱动路径 alpha**，而不是给三条 `15m` setup 做统一 pre-entry 盖章。

### 可救信号 C：横截面 / execution 版本也说明它不该继续停留在 Rank 61 角色层
`2026-03-24_1216_orderflow-xs-imbalance-cost-cliff.md` 虽然有 cost cliff，但已经把 flow 的残余价值推向：
- cross-sectional short-horizon flow alpha / execution family；
- 不是 `15m breakout/fib/ema` 的 shared veto-only layer。

## 4) 最值得改的唯一一刀是什么？
如果硬要继续保留与 `Rank 61` 的血缘关系，**唯一还算诚实的一刀**只会是：

- **把 `lower-TF volume-delta polarity mismatch` 从 `15m` shared confirmation/veto，彻底改写成 `1m/3m` single-asset flow-shock / OFI raw alpha` 的 entry skeleton。**

但这刀本轮**不值得立项**，因为：
1. 这已经不是原 Rank 61 的窄 reframe，而是在换赛道、换职责层、换 alpha 本体；
2. 它会和最近的 `OFI / VPIN / signed-flow / stablecoin order-flow shock` 新 family 高度重合；
3. `bot6` 本轮只该判断旧 parked rank 是否还能诚实派生出一个窄 reframe，不该把它硬重命名成新的 microstructure 主线。

## 5) 是否值得形成新的 derived hypothesis？
**结论：不值得。最终 verdict=`keep_park`。**

原因不是 flow 主题死了；恰好相反，最近证据说明它仍然很活。
但活下来的东西越来越像：
- `single-asset OFI / VWAP-pressure taker alpha`
- `fill-aware maker/taker split alpha`
- `signed order-flow shock -> continuation / inventory fade`
- `cross-sectional taker-flow imbalance with explicit cost/execution`

而不是新的 `Rank 61b`。

## 6) 如果勉强要写 trade on / trade off，会是什么？
仅作为“不立项”的澄清：

- `trade on`：当 `1m/3m` OFI / signed-flow shock / maker-taker split 达到 frozen threshold，且执行成本 / fill condition 仍允许时，直接做短时钟 continuation 或 fade。
- `trade off`：只出现一个模糊的 lower-TF delta polarity 提示、但没有明确事件强度 / 执行骨架 / cost survival 时，不把它包装成 `15m` setup 的 shared veto。

但这已经明显是在定义另一条 microstructure raw-alpha family，不是 `Rank 61` 的诚实 queue-only 派生，因此本轮明确不写成 `Rank 61b`。

## why now
因为最近 1 周关于 OFI / signed flow / microstructure 的新 digest 很容易制造一个错觉：
- “既然 flow 主题又连续冒出新证据，Rank 61 也许该补一条 61b。”

本轮就是把这层错觉切干净：
- **flow 主题还活着；**
- **但它活在更短时钟、执行敏感、raw-alpha/execution 的 family 里；**
- **不再诚实地活在 `Rank 61` 的 15m shared veto 血缘里。**

## suggested initial state
- 不适用；本轮不是 `derived_hypothesis_drafted`。

## Final template answers
1. **原 rank 为什么 park？**
   - 因为 lower-TF delta polarity 作为 `15m` 三条 setup 共用 veto/confirmation，并没有形成跨 setup、跨资产、成本后的稳定增量；主改善只来自薄样本筛选。
2. **它更像 hard park 还是 soft park？**
   - soft park，但现在比原审计时更偏硬。
3. **有没有“可救信号”？**
   - 有，但信号指向的是更上位的 `1m/3m microstructure raw-alpha / execution family`，不是新的 `Rank 61b`。
4. **最值得改的唯一一刀是什么？**
   - 若硬改，只能把 lower-TF delta polarity 从 shared veto 改写成 single-asset flow-shock / OFI raw alpha skeleton。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。
6. **为什么不立 `Rank 61b`？**
   - 因为新证据已经越过原 rank 的窄 reframe 边界，进入另一条更完整的 microstructure raw-alpha family；继续写 `61b` 会污染原 `park` 的审计边界。

## Queue write-back
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条最近复盘记录；不新增 `Rank 61b`
- `research/park_reframe/INDEX.md`：追加本轮索引
- `docs/TODO.md`：不改

## Git / commit
- 本轮不做 commit。
- 原因：工作区存在大量与本轮无关的脏文件与并行改动，不适合安全 selective commit。