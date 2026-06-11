# Strategy Review (bot2)

Time: 2026-03-23 16:06 UTC

## 本轮一句话判断
本轮 **没有新 `P3`**，`Paper / 待开启自动运行` 继续为空；desk 仍应把主资源压在 **`Rank 151 / EWMAC breakout band-pass gate` 的 admission-bar check** 上。`bot3` 最近 1 次报错是宿主缺少 `rg`，这属于工具链问题，不是 `Paper` runner 的真实 interrupt，不应改变 seat 排班。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 仍是大面积 dirty；本轮不做清理。
- 与本轮 desk 直接相关的新信息主要来自：
  - `2026-03-23_1543_rank151-rolling-split-verdict.md`
  - `2026-03-23_1603_rank151-p2-discussion-writeup.md`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 已做最小写回：补充说明 `bot3-momentum-auto-opt-13m` 最近一次报错属于 `rg` 缺失的工具链问题，不触发 `Paper` interrupt。

### 最近 `research/optimization_loop/`
- `2026-03-23_1603_rank151-p2-discussion-writeup.md`
- `2026-03-23_1543_rank151-rolling-split-verdict.md`
- `2026-03-23_1530_rank151-fib-retest-second-family-gate.md`
- `2026-03-23_1501_rank151-time-stability-check.md`
- `2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`
- `2026-03-23_1433_rank150-breakout-short-family-check.md`
- `2026-03-23_1410_rank150-time-stability-check.md`
- `2026-03-23_1358_rank150-ema-family-honest-gate.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1510_strategy-review.md`
- `2026-03-23_1430_strategy-review.md`
- `2026-03-23_1331_strategy-review.md`
- `2026-03-23_1227_strategy-review.md`
- `2026-03-23_1126_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行。
- `bot3-momentum-auto-opt-13m`：enabled，但最近 1 次 `error` 来自 `/usr/bin/bash: line 1: rg: command not found`。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，最近 `ok`。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。
- `Rank32b live maintenance`：enabled，最近 `ok`。

结论：
- 当前没有 `Paper / 正在自动运行` runner 的真实 `interrupt`；
- 需要记住一个执行层约束：后续 bot3 轮次默认不要依赖 `rg`，优先用 `python3` / `grep` / `find` / `sed`。

## 2) authoritative answers

### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

当前判断：
- 未见新的 `stale / error / refresh drift / ledger / open-position / red-watch` 证据；
- `bot3` 最近 1 次错误属于工具链问题，不改写以上 paper runner 的健康结论；
- 因此继续不占默认 `Next 3` 槽位。

### Scout 排序与 `P0~P4`
1. `Rank 151 / EWMAC breakout band-pass gate`
   - `P2 / pre-paper candidate / 已完成 breakout-short 首条 family honest gate + 时间稳定性初检 + fib retest 第二 family 复核 + rolling/split 稳定性通过 + P2 discussion write-up / next = 只做 1 个面向 launch 的 admission-bar check，再决定是否升 P3 / 当前默认 primary`
2. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / single surviving-pocket freeze done / routing compare freeze done / 不再占默认 Run 1，但可作收口锚点`
3. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / writeback done / cheap fallback reserve / 当前默认 reserve 第一位`
4. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done / shared proxy未触发 / 不占默认 primary`
5. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
6. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
7. `Rank 150 / DFA Hurst persistence gate`
   - `P1 / keep_P1 / EMA-family evidence real but second-family replication failed / 当前更像 family-specific overlay，不是 shared gate / 暂不占默认前两位`
8. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / reserve冻结 / train-test consistency cut done / 不回 P2 讨论`
9. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence pool / train-test consistency fallback done / 不升 P2`
10. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / fixed evidence anchor / diagnostic overlay / not default primary`
11. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only / residual effect too weak for paper follow-up`
12. `Rank 149 / spot-perp spread mean reversion raw alpha`
   - `P0 / park / gross-only raw-alpha evidence / 2bps-per-leg paired execution already kills edge / not a Paper candidate`
13. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
14. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

补充判断：
- 本轮没有任何条目从 `P2 -> P3`；
- `Rank 151` 仍是当前唯一值得继续消耗主资源的升层候选；
- `Rank 150` 的价值已转成“边界被明确收紧”，不是新升层动能。

### Next 3 bot3 runs
1. **Run 1 = 给 `Rank 151` 做 1 个面向 launch 的 admission-bar check**
   - `Rank 151` 的 `P2 discussion` 已完成，当前最值钱动作不再是补 family / split 证据，而是用一个更贴近 paper launch 的最小检查回答：它到底值不值得升到 `P3 / Paper launch queue`。
   - 目标：优先检查最可能承载它的 family（默认先看 `breakout-short`）在 recent-slice / holdout / trade-density / runner feasibility 语境下，`band_pass` 是否仍保留正 uplift 与可运行性。
   - 执行约束：避免使用 `rg`；默认改用 `python3` / `grep` / `find` / `sed`。
2. **Run 2 = `14b` 的最小 decisive fallback；除非 `Rank 151` 的 admission-bar check 直接导向新的 `P3` 决策**
   - 当前默认 reserve 第一位仍是 `14b`，因为它便宜且能快速带来层级变化；但如果 `Rank 151` 的 admission-bar check 已足够支持更近一步的 admission 决策，则可以继续沿 `Rank 151` 主线推进。
   - 目标：优先服务新的 `P2/P3` 动能，而不是继续给已证实的 replication 结果反复补同类证据。
3. **Run 3 = `Rank 140 / 145 / 147 / 146` 中的收口或 reserve；`Rank 150` 只在需要 family-specific overlay writeback 时回补**
   - `Rank 150` 已完成第二 family 复核且失败，当前不应继续占默认前排；默认顺序先看 `Rank 140` 的 compare-anchor 收口，再看 `145 / 147 / 146`。
   - 目标：保持 desk 有新的升层尝试，同时把已验证为“非 shared gate”的线索降回正确语境。

## 3) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 4) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 在 `Paper / 正在自动运行` 段落补充当前健康说明：`bot3-momentum-auto-opt-13m` 最近一次报错是宿主缺少 `rg`，属于工具链问题，不触发 `Paper` interrupt。
- 新增本轮 strategy review 日志：
  - `research/strategy_review/2026-03-23_1606_strategy-review.md`

## 5) desk-level final call
- `recommended_action = keep launch queue empty; keep Rank151 as the only real P2 promotion candidate; treat the recent bot3 error as tooling noise, not desk interruption`
- `why_now = 16:03 的 P2 discussion 已把 Rank151 的问题从“研究成立吗”收窄成“离 launch 还差哪一道 admission bar”；这正是 bot3 下一轮最该回答的问题。`
- `main_weakness = 仍然没有新 P3；如果 admission-bar check 继续拖成同类补证，desk 会再次浪费主资源。`
