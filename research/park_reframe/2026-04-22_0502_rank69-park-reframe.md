# 2026-04-22 05:02 UTC · Rank 69 park reframe review

## Selected rank
- `Rank 69`
- selection note: 按 `bot6` 当前低频轮转，默认仍优先 `Rank 50+`。`Rank 69` 上次 park-reframe 是 `2026-04-11 23:25 UTC`，已超过 `7` 天；且 4 月 18~21 又新增了几条更明确的 time/volume 旁证，足够判断这些证据是在救旧 `fixed-clock IVU shared gate`，还是继续把主题外流到新的 raw-alpha 宿主。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-18_2223_rank69-ivu-source-intake.md`
- `research/optimization_loop/2026-03-18_2242_rank69-clean-replication-park.md`
- `research/park_reframe/2026-04-11_2325_rank69-park-reframe.md`
- `research/quant_digests/2026-04-18_0940_us-session-twowindow-drift-alpha.md`
- `research/quant_digests/2026-04-20_1856_speed-volume-momentum-shell-alpha.md`
- `research/quant_digests/2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`

## 1) 原 rank 为什么 park？
原 `Rank 69 / IVU opening-volume uncertainty gate` 的 park 原因没有变化：
它想把固定 `00:00 UTC` session anchor 之后的 `IVU = vol_bar1 / sum(vol_bar1..bar7)` 写成一个跨 `ema_psar_long / fib_retest_long / breakout_short` 的 shared continuation gate，但最小 clean replication 证明，改善主要来自极端砍样本，而不是形成稳定、统一、成本后可用的 shared gate。

authoritative 冻结结果仍然很清楚：
- 主变体 `ivu_allow_q40`：
  - `mean_total_return = -0.84%`
  - `positive_asset_ratio = 11.11%`
  - `mean_trades = 1.78`
  - `mean_trade_count_retention = 8.02%`
  - `mean_failure_before_target_rate = 86.46%`
- setup 层也不统一：
  - `ema_psar_long: base=-3.68% -> q476=+4.22%`（留了 pocket）
  - `fib_retest_long: base=+1.17% -> q476=+1.11% / q40=-0.62%`（没形成增量）
  - `breakout_short: base=-3.55% -> q476=-6.04% / q40=-2.14%`（仍负）

翻成人话：
- `opening impulse / volume state` 不是零信息；
- 但被判死刑的是“固定时钟 IVU 比率 + shared allow gate”这层写法；
- 它没有把开段量结构诚实证明成 desk 可复用的 shared continuation 语言。

## 2) 它更像 hard park 还是 soft park？
**结论：仍是 `soft park`，但比 4 月 11 日那轮更接近 `hard park`。**

为什么还不是纯 hard：
1. `ema_psar_long + q476` 仍留下一点 pocket，说明开段冲击/流动性主题没有完全死；
2. 最近新增的 4 月 18~21 证据也都在重复说明：time/volume 主题本身仍有信息。

为什么又更接近 hard：
1. 新证据越来越清楚地支持的是 **raw alpha / event shell**，不是旧的 fixed-clock shared gate；
2. 原 `Rank 69` 最难看的问题——`retention≈8%` 才显得少亏——没有被推翻；
3. 一旦把它改到看起来更合理，主语就会从 `IVU gate` 变成别的宿主，不再是诚实的 `Rank 69b`。

## 3) 有没有“可救信号”？
**有，但可救信号已经明显不属于旧 Rank 69 本体。**

本轮最 relevant 的新增旁证有三条：
1. `2026-04-18_0940_us-session-twowindow-drift-alpha.md`
   - 说明固定时段的 edge 若还成立，更像 `21:00–23:00 UTC` 这种可独立交易的 time-of-day raw alpha；
   - 它支持的是“session pocket 本身就是主信号”，不是给旧 setup 再挂一个 IVU veto。
2. `2026-04-20_1856_speed-volume-momentum-shell-alpha.md`
   - 说明短窗价格涨速 + 成交量放大若还有信息，更像 short-term strength continuation 的完整壳；
   - 强调的是 impulse shell，不是固定 `bar1/bar1..7` 比率。
3. `2026-04-21_0607_mefai-scalping-microtrend-volspike-shell.md`
   - 进一步把主题推到 `EMA micro-trend × volume-spike / imbalance confirmation × hard-timeout` 这类更快、更局部、更 event-driven 的 raw alpha；
   - 也不是旧 Rank 69 的 shared opening-volume gate。

因此，本轮的“可救信号”只能诚实地写成一句：
> `opening impulse / volume-state` 主题仍有 residual value，但它更像新的 session-pocket / speed-volume / microtrend-volspike raw-alpha family，而不是支持旧 `fixed-clock IVU shared gate` 再派生一条 `Rank 69b`。

## 4) 最值得改的唯一一刀是什么？
如果只保留唯一主修改轴，本轮最值得改的一刀是：

> **把 fixed-clock IVU shared gate 改写成 event-defined opening-impulse / volume-spike raw-alpha host。**

为什么这刀不再诚实地属于 `Rank 69b`：
1. 它把主语从 `gate` 改成了 `host`；
2. 它把事件定义从 `00:00 UTC + bar1/bar1..7` 改成了更局部的 `session pocket / speed-volume / microtrend-volspike`；
3. 它已经不是旧对象里的“窄修补”，而是换宿主、换事件、换职责层。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

原因：
1. 原 `park` blocker 没被推翻：作为 `fixed-clock IVU shared gate`，它仍然主要靠砍样本减亏；
2. 4 月 18~21 的新证据救活的是 time/volume 的 raw-alpha 宿主，不是旧 Rank 69 这层 shared gate；
3. 若现在硬写 `Rank 69b`，本质会是借新的 session/impulse family 给旧 IVU gate 续命，模糊原审计边界。

## Final verdict
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_now`: `soft park，但比 4 月 11 日那轮更接近 hard`
- short note: `4 月 18~21 的 time-of-day / speed-volume / microtrend-volspike 新证据继续说明 opening impulse / volume-state 主题仍有信息，但它救活的是新的 session-pocket / event-defined raw-alpha 宿主，而不是旧 Rank 69 的 fixed-clock IVU shared gate，因此当前不诚实 draft Rank 69b。`

## File actions
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## Commit
- 本轮默认不做 commit。
- 原因：共享工作区存在大量与本轮无关的脏文件，不安全做 selective commit，避免混提。
