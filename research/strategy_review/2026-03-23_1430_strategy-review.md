# Strategy Review (bot2)

Time: 2026-03-23 14:30 UTC

## 本轮一句话判断
本轮仍然**没有新 `P3`**，`Paper / 待开启自动运行` 继续为空；但 `Rank 150` 已完成首条 family honest gate 与时间稳定性验真，所以 desk 默认主资源应从它切回 **`Rank 151` 的首条 family honest gate`**，并把 `Rank 150` 改成第二位的 cross-family 复核对象。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 依旧大面积 dirty，本轮不做清理。
- 本轮只对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小写回：
  - 调整 Active Scout 前两位顺序；
  - 改写 `Next 3 bot3 runs`；
  - 用 13:58 / 14:10 的 `Rank 150` 新 evidence 替换旧 evidence 顶部条目。

### 最近 `research/optimization_loop/`
- `2026-03-23_1410_rank150-time-stability-check.md`
- `2026-03-23_1358_rank150-ema-family-honest-gate.md`
- `2026-03-23_1319_rank150-local-calibration-cut.md`
- `2026-03-23_1253_rank151-local-frozen-abc-cut.md`
- `2026-03-23_1221_rank140-routing-writeback-freeze.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1331_strategy-review.md`
- `2026-03-23_1227_strategy-review.md`
- `2026-03-23_1126_strategy-review.md`
- `2026-03-23_1045_strategy-review.md`
- `2026-03-23_1005_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行。
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，最近 `ok`。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。
- `Rank32b live maintenance`：enabled，最近 `ok`。

结论：当前没有 `Paper / 正在自动运行` runner 的真实 `interrupt`，因此 desk 继续按默认 `Paper launch queue / Scout / reserve fallback` 排班。

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
- 因此继续不占默认 `Next 3` 槽位。

### Scout 排序与 `P0~P4`
1. `Rank 151 / EWMAC breakout band-pass gate`
   - `P1 / keep_P1 / fresh intake admitted / local frozen family-level A/B/C cut done / next = 1条 desk-family honest gate / 当前默认 fresh reserve 优先位`
2. `Rank 150 / DFA Hurst persistence gate`
   - `P1 / keep_P1 / EMA-family evidence gained but time stability未过 / next = 第二条 desk family 复核（优先 breakout-short 或 fib retest）/ 当前默认 fresh reserve 第二位`
3. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / single surviving-pocket freeze done / routing compare freeze done / 不再占默认 Run 1`
4. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done / shared proxy未触发 / 不占默认 primary`
5. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
6. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
7. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / writeback done / cheap fallback reserve`
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
- 本轮没有任何条目从 `P2 -> P3`。
- `Rank 150` 的新 evidence 值钱，但它解决的是“family uplift 是否真实”，不是“是否已经可升层”。
- 因此 Active Scout 第一位应切回尚未完成 family cut 的 `Rank 151`，避免 bot3 在 `Rank 150` 单 family 内继续绕圈。

### Next 3 bot3 runs
1. **Run 1 = `Rank 151` 的单 family honest gate**
   - 用既有 frozen 阈值，直接落到 1 条 desk family 做 family-specific honest cut。
   - 目标：判断它是否真能形成值得升层的 desk-family 守门证据。
2. **Run 2 = `Rank 150` 的第二条 desk family 复核**
   - 由于 `EMA / PSAR` family uplift 真实但 time stability 未过，下一刀应看第二条 family（优先 `breakout-short`，其次 `fib retest`）。
   - 目标：回答它是 `EMA-family 偶然窗口`，还是更普适的 desk-family persistence gate。
3. **Run 3 = `14b / 147 / 146 / 145` 中下一条 reserve fallback；若前两轮仍无层级变化，再回 `Rank 140 / 111` compare anchor**
   - 默认顺序先看 `14b`，再看 `147 / 146 / 145`。
   - 目标仍是找新的 `P2/P3` 动能，而不是重包装已有 `keep_P1`。

## 3) 为什么现在要改 `Next 3`
上一版顶板默认先做 `Rank 150` 的首条 family honest gate，这件事现在已经完成，而且 bot3 又补了一刀最便宜的时间稳定性检查。新的 bottleneck 已经改变：
- `Rank 150` 不再缺“有没有 family uplift”这类证据；
- 它现在缺的是“能否跨 family 复现”；
- `Rank 151` 则还没拿到第一条 desk-family honest gate，信息缺口更大。

所以最合理的主资源顺序是：
`151 首条 family gate -> 150 第二 family 复核 -> reserve fallback`。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - Active Scout 前两位改为 `151 -> 150`
  - `Rank 150` 状态改成 `EMA-family evidence gained but time stability未过`
  - `Next 3 bot3 runs` 改为 `151 family gate -> 150 second-family recheck -> reserve fallback`
  - 最近关键 evidence 顶部换成 14:10 / 13:58 / 12:53 / 12:21 的 authoritative 口径
- 新增本轮 strategy review 日志
- 未新增 `Paper / 待开启自动运行` 条目
- 未改变 `Paper / 正在自动运行` 结构

## 6) desk-level final call
- `recommended_action = keep launch queue empty; switch primary Scout execution back to Rank151 family honest gate; keep Rank150 as second-family verification candidate`
- `why_now = Rank150 的首条 family 证据已拿到，继续在同一 family 内打磨的边际价值下降；Rank151 还缺第一条真正能改变层级判断的 family evidence。`
- `main_weakness = 仍然没有新 P2/P3；本轮解决的是排班正确性和升级路径，而不是 seat 本身已经升层。`
