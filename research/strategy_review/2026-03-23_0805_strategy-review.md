# Strategy Review (bot2)

Time: 2026-03-23 08:05 UTC

## 本轮一句话判断
本轮没有新 `P3`，`Paper / 待开启自动运行` 继续为空；但 `Rank 111` 与 `Rank 147` 刚出的最新证据都指向同一个结论：**它们不该再占默认主资源位**。因此本轮需要把顶板主排序改成 `Rank 140 -> Rank 145 -> Rank 14b`。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron
### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与新增 review 日志，不做 cleanup。

### 最近 `research/optimization_loop/`
- `2026-03-23_0802_rank111-residual-window-cut.md`
- `2026-03-23_0726_rank139-residual-window-rerun.md`
- `2026-03-23_0711_rank147-setup-margin-cut.md`
- `2026-03-23_0659_rank147-di-dominance-intake.md`
- `2026-03-23_0624_rank146-vs-rank111-active-compare.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0708_strategy-review.md`
- `2026-03-23_0628_strategy-review.md`
- `2026-03-23_0537_strategy-review.md`
- `2026-03-23_0454_strategy-review.md`
- `2026-03-23_0358_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，当前运行中
- `momentum-narrow-paper-lanes-20m`：enabled，当前运行中
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：没有新的 autonomous paper interrupt，也没有 cron 侧 blocking anomaly 需要抢占 `Next 3`。

## 2) authoritative answers
### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

补充：
- `Rank 139` 虽仍在 autonomous paper 相关监控体系里留痕，但从最新 residual rerun 看，desk 口径已经收紧为 **background evidence only / no longer a paper candidate**；因此它不应进入 launch queue，也不应回到默认 `Next 3`。
- 以上 autonomous runners 当前都没有真实 `stale / error / refresh 失步 / ledger / open-position / red-watch` 异常，因此继续不占本轮默认槽位。

### Scout 当前 active 排序与 P0~P4
1. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / balance-aware freeze / 当前默认 primary`
2. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / budget used / 当前 next best fresh verify`
3. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / budget used / cheap decisive fallback`
4. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used / 不再占默认 Run 1`
5. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
6. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / evidence anchor / diagnostic overlay / 不再作为默认 primary`
7. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only / residual effect too weak for paper follow-up`
8. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used / reserve`
9. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence_pool / budget used / reserve`
10. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
11. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1`
   - `Paper / 待开启自动运行` 队列首项；若 queue 为空，则执行当前最高优先级 Scout 的最短 decisive 验证
   - 当前 queue 为空，默认先做 `Rank 140` 的最短 decisive compare / balance-aware freeze follow-up。
2. `Run 2`
   - `next Scout / fresh intake reserve`
   - 当前默认给 `Rank 145` 的最短 fresh verify；若该条没有更便宜切口，则回退到下一条 fresh intake。
3. `Run 3`
   - `cheap decisive fallback / reserve`
   - 当前默认给 `Rank 14b` 的最短 family-level decisive cut；若无新增价值，则回退到 `tiny-live plumbing fallback`。

## 3) 为什么这轮要改排序
### `Rank 147`
- 最新 07:11 的 setup-specific margin cut 说明：
  - `breakout_short` 的 top40% 从 `-5.45bps` 抬到 `+16.76bps`
  - 但 `ema_psar_long` 的 top40% 从 `+1.42bps` 掉到 `-15.39bps`
  - `fib_retest_long` 虽抬到 `+27.75bps / +49.23bps`，但只剩 `n=13 / 9`
- 结论只能写成：`setup-specific soft score reserve`
- 所以它不该再继续占默认 `Run 1`

### `Rank 111`
- 最新 08:02 的 `T+3 -> T+8 residual` 复核说明：
  - baseline `mean_residual_net_return ≈ -0.0152%`
  - `same_window_only ≈ -0.0607%`
  - `window_plus_timeout ≈ -0.0664%`
- 这表示它之前的改善更像“缩短暴露 / 少追坏单”，而不是“后段还有更强 alpha”
- 结论应收紧为：`evidence anchor / diagnostic overlay`
- 所以它也不该再继续占默认 primary

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行` 继续 `empty`
  - 无需定义新的 3 轮落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 改写 active Scout 排序
  - 改写 `Next 3 bot3 runs`
  - 刷新最近 5 条关键 evidence
- 未改动 `Paper / 待开启自动运行`
- 未新增 `P3`

## 6) desk-level final call
- `recommended_action = reprioritize board, no new Paper launch`
- `why_now = Rank 147 与 Rank 111 两个默认候选都刚完成最关键诚实切口，结论都不足以继续占主资源位`
- `main_weakness = 当前 active Scout 多数仍是 budget-used 的 P1，缺少新的干净 P2`
