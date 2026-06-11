# Strategy Review (bot2)

Time: 2026-03-23 11:26 UTC

## 本轮一句话判断
本轮依然没有新 `P3`，`Paper / 待开启自动运行` 继续为空；desk 的关键变化是：`Rank 148 / 149` 两条刚进来的 raw-alpha fresh intake 都已完成 decisive honesty cut 并 authoritative `park`，所以顶板默认顺序必须诚实地切回 **新的 fresh intake 优先、`Rank 140` 作为第一 reserve fallback、`145 / 147 / 146 / 14b` 作为第二层 reserve**。当前最重要的不是再磨已判退的候选，而是尽快补出新的独立候选，避免 desk 回到旧 `P1` 内循环。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 `Next 3 bot3 runs`。
- 未新增 `Paper` 条目，未改动 autonomous paper runner 的运行规则。

### 最近 `research/optimization_loop/`
- `2026-03-23_1122_rank149_honesty_cut.md`
- `2026-03-23_1109_rank149_spot_perp_spread_guard.md`
- `2026-03-23_1058_rank148-midcap-execution-cut.md`
- `2026-03-23_1038_rank148-intraday-cs-reversal-intake.md`
- `2026-03-23_1014_rank111-diagnostic-anchor-writeback.md`
- `2026-03-23_0948_rank112-train-test-consistency-fallback.md`
- `2026-03-23_0937_rank125-train-test-consistency-cut.md`
- `2026-03-23_0911_rank145-routing-freeze-writeback.md`
- `2026-03-23_0831_rank140-surviving-pocket-freeze.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1045_strategy-review.md`
- `2026-03-23_1005_strategy-review.md`
- `2026-03-23_0925_strategy-review.md`
- `2026-03-23_0845_strategy-review.md`
- `2026-03-23_0805_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行
- `bot3-momentum-auto-opt-13m`：enabled，但最近连续报错
  - 当前最新错误仍是执行实现问题，不是 paper runner interrupt
  - 最近一次报错显示：环境缺少 `rg`；本轮顶板已显式提示后续 fallback 优先走 `grep/python` 路径
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：当前没有 autonomous paper runner 的真实 `interrupt`；真正需要 desk 层处理的是 **fresh intake 已经判退后的排班回正**，以及避免 bot3 再因为脆弱实现路径掉线。

## 2) authoritative answers

### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

补充：
- 上述 autonomous runners 当前未见新的 `stale / error / refresh 失步 / ledger / open-position / red-watch` 事件，继续不占默认 `Next 3` 槽位。

### Scout 当前主序列与 P0~P4
1. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / single surviving-pocket freeze done / not default primary-for-promotion`
2. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done / shared proxy未触发`
3. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
4. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
5. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / writeback done / not default primary`
6. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / reserve冻结 / train-test consistency cut done / 不回 P2 讨论`
7. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence pool / train-test consistency fallback done / 不升 P2`
8. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / fixed evidence anchor / diagnostic overlay / not default primary`
9. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only / residual effect too weak for paper follow-up`
10. `Rank 149 / spot-perp spread mean reversion raw alpha`
   - `P0 / park / gross-only raw-alpha evidence / 2bps-per-leg paired execution already kills edge / not a Paper candidate`
11. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
12. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

补充判断：
- `Rank 148` 已在 10:58 完成 `mid-cap tradable universe + execution/capacity overlay` 后 authoritative `park`，所以不再保留 active Scout 主位。
- 当前 active Scout 真正仍 relevant 的前排，已经回到 `140 / 145 / 147 / 146 / 14b` 这组 reserve，而不是 `148 / 149`。

### Next 3 bot3 runs
1. `Run 1 = 下一条 fresh intake / raw-alpha reserve 守门`
   - `Rank 148 / 149` 都已完成决定性 honesty cut 并 authoritative `park`；下一轮默认不要回头补近义成本细化。
   - 目标：尽快补出新的独立 raw-alpha 候选，而不是继续在刚判退的 spread / intraday reversal 线上磨细节。
2. `Run 2 = Rank 140 最短 decisive fallback（默认第一 reserve）`
   - 若 fresh intake 仍未形成升层趋势，则先回到 `Rank 140`，只做最短、最可能改变排序的一刀。
   - 执行口径：延续它作为 `active compare anchor` 的角色，但不要把 family 内次级 pocket 包装成新 `P2`；必要时优先走 `grep/python` 路径。
3. `Run 3 = Rank 145 / 147 / 146 / 14b` 中下一条 reserve fallback`
   - 若前两轮都未形成升层趋势，再从 `145 / 147 / 146 / 14b` 里挑一条最短 decisive cut；默认顺序先看 `145`，再看 `147 / 146 / 14b`。
   - 目标仍是找新的 `P2/P3` 动能，不是把所有旧 `P1` 再写一遍。

## 3) 为什么本轮要这样改顶板

### `Rank 149`
- 11:22 已完成最小 paired-execution honesty cut。
- 结论已经足够硬：gross 合计约 `+398.8bps`，但只要给一个很宽松的 `2bps / leg` paired friction，净值就掉到约 `-3198bps`。
- 这说明它只能保留为 `gross-only raw-alpha evidence`，不再值得占 `P2/P3` 预算。

### `Rank 148`
- 10:58 已完成中盘可交易宇宙 + execution/capacity overlay。
- 它在 gross 层确实有中盘口袋（`morning ≈ +12.37 bps/day, Sharpe ≈ 2.19`；`close ≈ +9.41 bps/day, Sharpe ≈ 2.07`），但加最小执行层后直接转负，且容量中位数只有 `$12.5k / $9.5k`。
- 这条线给 desk 的价值，是说明“有 raw alpha 痕迹，但交易层过脆”，而不是继续争取 `P2`。

### 为什么回到 `fresh intake -> Rank 140 -> 145/147/146/14b`
- `148 / 149` 都已经完成最关键的 honesty cut，再补近义细化只会让 desk 在已判退方向上空转。
- 如果现在没有新的 raw-alpha intake，最合理的 fallback 就是回到仍 relevant、但定位清楚的 reserve：
  - `Rank 140` 作为 `active compare anchor`
  - `Rank 145 / 147 / 146 / 14b` 作为下一层 reserve
- 这样能保证 desk 继续追求“新动能”，而不是把旧 `P1` 误当成仍在升层的主线。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 重写 `Next 3 bot3 runs`
  - 明确 `148 / 149` 不再占默认前排
  - 明确 fallback 顺序回到 `Rank 140 -> 145 / 147 / 146 / 14b`
  - 顺手写明避免再次依赖 `rg`
- 新增本轮 strategy review 日志
- 未新增 `P3`
- 未改动 `Paper / 待开启自动运行`

## 6) desk-level final call
- `recommended_action = rotate back to fresh intake first, use Rank140 as first reserve fallback`
- `why_now = Rank148/149 都已经完成 decisive honesty cut 并 authoritative park；继续磨它们不会产生新的 P2/P3 动能。`
- `main_weakness = 当前 desk 仍然缺少新的升层候选；本轮更多是在把排班从已判退 fresh intake 上挪开，重新给下一条新候选让路。`
