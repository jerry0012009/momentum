# 2026-04-18 16:06 UTC · Rank 72 park reframe review

## Scope
- source rank: `Rank 72 / realized-vol mid-band cost-survival gate`
- original verdict stays: `park / evidence pool`
- this round only asks: **after the newer mid-April liquidity / vol / overlay evidence, does old Rank 72 deserve a fresh narrow reframe, or should it stay parked?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-19_0013_rank72-source-intake.md`
  - `research/optimization_loop/2026-03-19_0032_rank72-midband-clean-replication.md`
  - `research/park_reframe/2026-04-07_1847_rank72-park-reframe.md`
  - `research/quant_digests/2026-04-01_1426_lowfreq-liquidity-proxy-gate-overlay.md`
  - `research/quant_digests/2026-04-02_0448_utc-slot-costmap-route-veto-overlay.md`
  - `research/quant_digests/2026-04-16_0639_liquiditybeta-armagarch-ts-alpha.md`
  - `research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
  - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/per_asset_summary.csv`
  - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/window_summary.csv`

## Why this rank this round
- 继续遵循 `bot6` 的低频轮转，本轮仍优先看 `Rank 50+` 的 parked rank。
- `Rank 72` 上次 park-reframe 复盘是 `2026-04-07 18:47 UTC`，已超过 7 天，符合“同条 rank 避免高频重复”的约束。
- 这条线很适合再看一次，因为它原本就是“波动/成本生存信息是否能当 shared gate”的典型案例；而 4 月中旬又新增了几条更明确把 vol / liquidity 信息往 **overlay 或新 raw-alpha 宿主** 上推的证据。

## 1) 原 rank 为什么 park？
原 `Rank 72` 被 park，不是因为波动状态完全无信息，而是因为它写成 **shared realized-vol mid-band allow/deny gate** 后，证据仍然主要表现为“砍样本换表面改善”：

- `ema_psar_long @ 6bps`
  - `baseline = -4.11%`
  - `rv_midband_q20_80 = +1.78%`
  - 但 `mean_trade_count_retention ≈ 21.49%`
- `fib_retest_long @ 6bps`
  - `baseline = -0.22%`
  - `rv_midband_q20_80 = -1.22%`
  - `mean_trade_count_retention ≈ 21.90%`
- `breakout_short @ 6bps`
  - `baseline = -3.36%`
  - `rv_midband_q20_80 = -2.53%`
  - `mean_trade_count_retention ≈ 17.76%`

更细看也没有形成统一 desk 价值：
- `ema_psar_long` 的改善主要由 `SOL` 支撑，`BTC` 仍负、`ETH` 仅接近打平；
- `fib_retest_long` 在三币上都没有 clean rescue；
- `breakout_short` 三币全负，且 ETH 只剩 `3` 笔、retention 仅 `10%`。

所以原始 park 的审计重点很明确：
- 否掉的是 **“realized-vol mid-band 可以诚实做 shared entry gate”** 这层写法；
- 不是否掉所有 vol / liquidity / tradeability 信息本身。

## 2) 它更像 hard park 还是 soft park？
**结论：仍是 `soft park`，但比 4 月 7 日那轮更接近 `hard with consumed residual`。**

原因：
- soft 的部分在于，vol / liquidity / cost-survival 主题显然还在活跃，甚至 mid-April 还有新证据；
- hard 的部分在于，这些新证据越来越清楚地说明：它们活着的方式，已经不是 old `Rank 72` 这种 `15m shared mid-band gate`。

换句话说：
- 主题没死；
- 但 old `Rank 72` 的职责定义已经基本死透了。

## 3) 有没有“可救信号”？
**有 residual signal，但它继续外流到更上位宿主，不足以支持新的 `Rank 72b`。**

### 还能看到的 residual
1. `2026-04-01` 的 liquidity-proxy digest 明确把 `CS/AR spread proxy × Amihud × realized-vol trigger` 定位为 **shared liquidity/cost overlay**，而不是方向信号。
2. `2026-04-02` 的 UTC slot cost-map digest 更进一步，把真正值钱的东西收敛成 **时段成本地图 × routing × execution veto**。
3. `2026-04-16` 的 liquidity-adjusted ARMA-GARCH digest 甚至把 vol/liquidity 信息抬成了 **新的 raw alpha 主语**：先做流动性校正，再预测下一期收益符号。
4. `2026-04-17` 的 regime-aware XS momentum digest 也把 `BTC realized vol` 明确降级成 **已有 raw alpha 的 veto / size-down 层**，不是 alpha 本体。

### 为什么这不等于“救 Rank 72”
这些新证据共同说明的其实是：
- 若 vol / liquidity 信息要继续活，
- 它更像：
  - 新的 **liquidity-adjusted raw alpha** 宿主，或
  - 更完整的 **execution / cost / sizing overlay** 宿主；
- 而不是 old `Rank 72` 那种只用 `rv_pct q20~q80` 去统一裁三条 setup 的 shared allow/deny gate。

所以可救信号存在，但不再属于 old `Rank 72` 的 distinct residual。

## 4) 最值得改的唯一一刀是什么？
**唯一还说得通的一刀，仍然只是：把 `shared allow/deny gate` 降级成 `cost-aware size-down / veto overlay`。**

也就是：
- 不让 `realized-vol mid-band` 决定 setup 能否入场；
- 只在已有 setup 触发后，用它做 `size-down / veto / route-aware abstain`；
- 第一刀最多也只该测 `baseline vs vol-aware size-down/veto`。

但问题也正出在这里：
- 这已经不再是 `Rank 72` 保持 distinct 的单轴残余；
- 它越来越像 `2026-04-01 / 04-02 / 04-17` 那批更上位 overlay family 的通用语言。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。最终结论：`keep_park`。**

原因：
1. old `Rank 72` 的 blocker 没被推翻：作为 shared gate，它仍主要靠 retention 压到 `~18%–22%` 才显得好看；
2. mid-April 新证据没有把它拉回 old thesis，反而更明确地把 residual 推向新的 raw-alpha / execution-overlay family；
3. 如果现在硬 draft `Rank 72b`，大概率只是在把 old `realized-vol mid-band gate` 偷换成泛化的 `tradeability / sizing overlay`，会稀释原 `park` verdict 的审计意义。

## 6) 如果硬写 trade on / trade off，会是什么？
本轮**不新增** derived hypothesis，因此不正式入队。

仅作审计备注，唯一仍可保留的 residual 读法是：
- `trade on`：vol / liquidity 信息更适合服务已有 raw alpha 的后置 `size-down / veto / route selection`；
- `trade off`：一旦把它重新写成 shared entry gate，就极易重新退化成“靠砍交易数美化结果”。

但这不足以诚实构成新的 queue-facing 提案。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park, but now even closer to hard park with consumed residual`

## Minimal audit note
This round does **not** overturn the original `park`.
Compared with the 2026-04-07 review, the newer mid-April evidence makes the story even clearer: if vol / liquidity information still has value, it now lives more naturally inside **new liquidity-adjusted raw alpha shells** or **higher-level execution / cost overlays**, not as another honest extension of old `Rank 72`.

## Git
- 本轮只做最小必要文档更新；未做 commit。
- 原因：git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
