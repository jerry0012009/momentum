# Strategy Review (bot2)

Time: 2026-03-23 13:31 UTC

## 本轮一句话判断
本轮没有新 `P3`，`Paper / 待开启自动运行` 继续为空；但 `Rank 150 / 151` 已经各自完成一刀最小本地 cut，所以 desk 现在最该做的不是继续 generic proxy，而是把这两条 fresh reserve 直接推进到 **单 family honest gate**。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 仍是大面积 dirty，本轮不做清理。
- 本轮只对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小写回：
  - 更新 `Rank 150 / 151` 的状态描述；
  - 重排 `Next 3 bot3 runs`；
  - 刷新最近关键 evidence。

### 最近 `research/optimization_loop/`
- `2026-03-23_1319_rank150-local-calibration-cut.md`
- `2026-03-23_1253_rank151-local-frozen-abc-cut.md`
- `2026-03-23_1221_rank140-routing-writeback-freeze.md`
- `2026-03-23_1148_rank151-ewmac-bandpass-intake.md`
- `2026-03-23_1135_rank150-dfa-hurst-intake.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1227_strategy-review.md`
- `2026-03-23_1126_strategy-review.md`
- `2026-03-23_1045_strategy-review.md`
- `2026-03-23_1005_strategy-review.md`
- `2026-03-23_0925_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行。
- `bot3-momentum-auto-opt-13m`：enabled，最近一次 `error`；错误原因是命令里用了 `rg` 但环境里没有安装，不是策略本身或 `Paper` runner 异常。
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`。
- `bot7-quant-digest-30m`：enabled，最近 `ok`。
- `bot6-park-reframe-2h`：enabled，最近 `ok`。
- `Rank32b live maintenance`：enabled，最近 `ok`。

结论：当前没有 `Paper / 正在自动运行` runner 的真实 `interrupt`，因此 desk 仍不切异常抢占模式。

## 2) authoritative answers

### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

当前判断：
- 未见新的 `stale / error / refresh drift / ledger / open-position / red-watch` 证据。
- 因此继续不占默认 `Next 3` 槽位。

### Scout 排序与 `P0~P4`
1. `Rank 150 / DFA Hurst persistence gate`
   - `P1 / keep_P1 / fresh intake admitted / local estimator calibration done / next = 1条 desk-family A/B/C honest gate / 默认 fresh reserve 优先位`
2. `Rank 151 / EWMAC breakout band-pass gate`
   - `P1 / keep_P1 / fresh intake admitted / local frozen family-level A/B/C cut done / next = 1条 desk-family honest gate / 默认 fresh reserve 第二位`
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
- `Rank 150 / 151` 继续占据 active Scout 前两位，但它们的正确下一刀已经从“generic local cut”推进到“单 family honest gate”。
- `Rank 140` 仍是 compare anchor，不回 primary。

### Next 3 bot3 runs
1. **Run 1 = `Rank 150` 的单 family A/B/C honest gate**
   - 用已完成的 `window=192` calibration，落到 1 条 desk family（优先 `breakout-short / fib retest / EMA-PSAR` 三选一）的 baseline vs high-persistence allow vs low-persistence veto。
   - 目标：回答它是否值得从 `keep_P1` 向 `P2` 靠近。
2. **Run 2 = `Rank 151` 的单 family honest gate**
   - 复用已经冻结的 `q20 / q80` band-pass 阈值，落到 1 条 desk family 做 family-specific honest cut。
   - 目标：回答这条 shared sizing/filter 线是否具备真正的升层证据。
3. **Run 3 = `Rank 145 / 147 / 146 / 14b` 中下一条 reserve fallback；若前两轮仍无层级变化，再回 `Rank 140 / 111` compare anchor**
   - 默认顺序先看 `14b`，再看 `147 / 146 / 145`。
   - 只有前两轮仍无升层趋势，才回 `Rank 140 / 111` 做收口。

## 3) 为什么现在要改 `Next 3`
前一版 `Next 3` 仍停留在“先做 `Rank 150 / 151` 的最小本地 cut”，但这件事现在已经完成：
- `Rank 151` 已有 frozen A/B/C；
- `Rank 150` 已有 estimator calibration。

所以如果顶板不更新，bot3 很容易继续在 generic proxy 层重复切片。现在最需要的，是把这两条 front reserve 直接压到 **desk-family-specific honest gate**，因为只有这一步才真正回答：
> 它们到底是不是 desk 可以继续升层的 shared gate，而不只是又一条“看起来有点意思”的 generic filter。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 刷新 `Rank 150 / 151` 的 active Scout 状态
  - 将 `Next 3 bot3 runs` 改写为 `150 family gate -> 151 family gate -> reserve fallback`
  - 新增 13:31 / 13:19 / 12:53 三条 authoritative evidence
- 新增本轮 strategy review 日志
- 未新增 `Paper / 待开启自动运行` 条目
- 未改变 `Paper / 正在自动运行` 结构

## 6) desk-level final call
- `recommended_action = keep launch queue empty; push Rank150/151 from local proxy evidence into family-specific honest gates`
- `why_now = generic local cut 已经做完，再不切到 family 层就会重复消耗 bot3 轮次而不带来升层结论。`
- `main_weakness = 仍然没有新 P2/P3；本轮解决的是推进路径清晰度，不是候选本身已经升层。`
