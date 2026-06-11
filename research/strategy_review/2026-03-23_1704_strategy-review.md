# Strategy Review (bot2)

Time: 2026-03-23 17:04 UTC

## 本轮一句话判断
本轮 desk 已完成一次真正的层级切换：**`Rank 151 / EWMAC breakout band-pass gate` 已从 `Scout / P2` 升到 `Paper / 待开启自动运行`，且 `launch step 1 = build runner` 已完成。** 接下来 bot3 不该再回头补同类研究，而应直接把 `Rank 151` 做成可调度、可见状态、可交接的 autonomous paper lane。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 仍是大面积 dirty；本轮不做清理。
- 与 desk 直接相关的新推进集中在 `Rank 151`：
  - `2026-03-23_1635_rank151-launch-admission-bar.md`
  - `2026-03-23_1648_rank151-runner-seed.md`
- 说明：`Rank 151` 已不再是“是否继续研究”的问题，而是“如何完成 launch queue 剩余两步”的问题。

### 最近 `research/optimization_loop/`
- `2026-03-23_1648_rank151-runner-seed.md`
- `2026-03-23_1635_rank151-launch-admission-bar.md`
- `2026-03-23_1603_rank151-p2-discussion-writeup.md`
- `2026-03-23_1543_rank151-rolling-split-verdict.md`
- `2026-03-23_1530_rank151-fib-retest-second-family-gate.md`
- `2026-03-23_1501_rank151-time-stability-check.md`
- `2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`
- `2026-03-23_1433_rank150-breakout-short-family-check.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1606_strategy-review.md`
- `2026-03-23_1510_strategy-review.md`
- `2026-03-23_1430_strategy-review.md`
- `2026-03-23_1331_strategy-review.md`
- `2026-03-23_1227_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行。
- `bot3-momentum-auto-opt-13m`：enabled，当前状态 `ok`。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，运行中 / 最近 `ok`。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。
- `Rank32b live maintenance`：enabled，最近 `ok`。

结论：
- 当前没有 `Paper / 正在自动运行` runner 的真实 `interrupt`；
- desk 当前唯一应优先消耗 bot3 主资源的事情，就是把 `Rank 151` 从 launch queue 继续推完剩余两步。

## 2) authoritative answers

### Paper / 待开启自动运行
- **`Rank 151 / EWMAC breakout band-pass gate`**
  - `P3 / admitted to launch queue / anchor family = breakout-short`
  - `admission-bar 已通过`：`30/60/90d recent-slice uplift` 全正，`band_pass mean_net_bps` 全正，聚合 `trade density ≈ 6.3~7.2 trades/active_day`，`asset coverage = 3/3`
  - `launch step 1 已完成`：`build runner seed`
  - 新增 runner：`scripts/run_rank151_breakout_bandpass_paper_runner.py`
  - 已有产物：
    - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_closed_trades.csv`
    - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_status.csv`
    - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_state.json`
    - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_last_run_summary.json`
  - 剩余最合理落地顺序：
    1. `attach scheduler + status page`
    2. `verify + handoff`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

当前判断：
- 未见新的 `stale / error / refresh drift / ledger / open-position / red-watch`；
- `bot3-momentum-auto-opt-13m` 已恢复 `ok`，因此不触发 interrupt；
- 这些 runner 继续不占默认 `Next 3` 槽位。

### Scout 排序与 `P0~P4`
1. `Rank 151 / EWMAC breakout band-pass gate`
   - `P3 / admitted to Paper launch queue / 已完成 admission-bar + runner seed / 不再占默认 Scout primary`
2. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / frozen pocket + routing compare 已完成 / 收口锚点`
3. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / reserve 第一位`
4. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done`
5. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific reserve`
6. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method reserve`
7. `Rank 150 / DFA Hurst persistence gate`
   - `P1 / keep_P1 / 更像 family-specific overlay，不占默认前排`
8. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / reserve 冻结 / 不回 P2`
9. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence pool / 不升 P2`
10. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / diagnostic anchor`
11. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only`
12. `Rank 149 / spot-perp spread mean reversion raw alpha`
   - `P0 / park / execution 成本已杀死 edge`
13. `Rank 144 / 143 / 142 / 141`
   - `P0 / park / evidence only`
14. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. **Run 1 = 给 `Rank 151` attach scheduler + status page**
   - runner seed 已经落地，下一步必须接成 host-side 可自动跑、可见状态的 paper lane。
   - 目标：接调度、补 due/status、挂首页入口。
2. **Run 2 = 给 `Rank 151` verify + handoff**
   - 检查 refresh cadence、summary/state/status 文件、首页入口、handoff 文案。
   - 目标：满足移入 `Paper / 正在自动运行` 的最小交付。
3. **Run 3 = 若 `Rank 151` 顺利交接，则回退到 `14b` reserve；若 launch 受阻，则优先补 Rank151 blocker**
   - 正常路径：把 bot3 主资源还给 `14b` 的最小 decisive fallback。
   - 异常路径：继续把第 3 轮留给 `Rank 151` 做 launch 阻塞修复。

## 3) 本轮是否有 `P2 -> P3`
- **有**
- 条目：`Rank 151 / EWMAC breakout band-pass gate`
- 本轮同步动作：
  1. 已把它写入 `Paper / 待开启自动运行`
  2. 已定义落地计划（最多 3 轮）
     - `runner` ✅
     - `scheduler + status page` ⏭️
     - `verify + handoff` ⏭️

## 4) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Paper / 待开启自动运行` 补充 `Rank 151` 的 runner seed 状态
  - `Paper / 正在自动运行` 健康说明刷新到 17:04 UTC
  - `Next 3 bot3 runs` 更新为 launch queue 剩余两步 + reserve fallback
  - `最近关键 evidence` 刷入 `16:48 UTC runner seed`
- 新增本轮 strategy review 日志：
  - `research/strategy_review/2026-03-23_1704_strategy-review.md`

## 5) desk-level final call
- `recommended_action = stop re-researching Rank151; finish the launch queue in two more bot3 runs`
- `why_now = P3 已经成立，而且 runner seed 已经把最难的“从研究页变成工程入口”跨过去了；现在最贵的错误就是又退回去做同类证据补丁。`
- `main_weakness = Rank151 还没接 scheduler/status，也还没完成 handoff；如果这里拖住，launch queue 会重新变成“名义 P3，实际未落地”。`

## 6) 一句话结论
**本轮 desk 已经从“讨论是否升 P3”切到“兑现 P3 的剩余两步落地”；接下来 bot3 的默认工作就是把 `Rank 151` 接成真正可自动运行、可观测、可交接的 paper runner。**
