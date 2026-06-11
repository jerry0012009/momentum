# Strategy Review (bot2)

Time: 2026-03-23 10:45 UTC

## 本轮一句话判断
本轮没有新 `P3`，`Paper / 待开启自动运行` 继续为空；但 desk 的主序列需要更明确地切到 **`Rank 148` 这条刚入板的独立 raw-alpha 家族**。`Rank 125 / 112 / 111` 已经完成 cheap decisive 收口并固定为 `keep_P1`，不该再占默认前排。下一轮 bot3 最有杠杆的小步，是直接回答：`Rank 148` 从“大币下限弱”切到“中盘可交易宇宙 + execution/capacity overlay”后，是否还值得保留 `P2` 想象。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的：
  - `Active Scout 排序`
  - `Next 3 bot3 runs`
- 未触碰 `Paper` 队列条目，也未改动运行中 paper runner 的规则。

### 最近 `research/optimization_loop/`
- `2026-03-23_1038_rank148-intraday-cs-reversal-intake.md`
- `2026-03-23_1014_rank111-diagnostic-anchor-writeback.md`
- `2026-03-23_0948_rank112-train-test-consistency-fallback.md`
- `2026-03-23_0937_rank125-train-test-consistency-cut.md`
- `2026-03-23_0922_rank14b-writeback-sync.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1005_strategy-review.md`
- `2026-03-23_0925_strategy-review.md`
- `2026-03-23_0845_strategy-review.md`
- `2026-03-23_0805_strategy-review.md`
- `2026-03-23_0708_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行
- `bot3-momentum-auto-opt-13m`：enabled，但最近一次 `error`
  - 最新报错不再是 `rg` 缺失，而是：`docs/TODO.md` 的 exact-text edit 没匹配上
  - 这更像 **顶板文本漂移导致的写回失败**，不是策略 runner 的真实 interrupt
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：当前没有 autonomous paper runner 的真实 `interrupt`；问题主要在 `bot3` 写回顶板的实现脆弱，而不是 desk 策略排序本身失效。

## 2) authoritative answers

### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122`

补充：
- 上述 autonomous runners 当前没有新的 `stale / error / refresh 失步 / ledger / open-position / red-watch` 信号；继续不占默认 `Next 3` 槽位。

### Scout 当前主序列与 P0~P4
1. `Rank 148 / intraday cross-sectional reversal (US session)`
   - `P1 / keep_P1 / fresh intake admitted / raw-alpha reserve / next cut = mid-cap tradable universe + execution/capacity overlay`
2. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / single surviving-pocket freeze done / not default primary-for-promotion`
3. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done / shared proxy未触发`
4. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
5. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
6. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / writeback done / not default primary`
7. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / reserve冻结 / train-test consistency cut done / 不回 P2 讨论`
8. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence pool / train-test consistency fallback done / 不升 P2`
9. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / fixed evidence anchor / diagnostic overlay / not default primary`
10. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only / residual effect too weak for paper follow-up`
11. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
12. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = Rank 148 follow-up`
   - 做 **中盘可交易宇宙 + 最小 execution/capacity overlay**
   - 目标：更硬地回答 `keep_P1 / promote_P2 / park`
2. `Run 2 = 下一条 fresh intake / raw-alpha reserve 守门`
   - 若 `Rank 148` 仍不形成 `P2` 动能，就继续找新的独立 raw-alpha 候选
   - 重点不是回头续磨 `125 / 112 / 111`
3. `Run 3 = active reserve decisive fallback`
   - 默认先看 `Rank 140`，再看 `145 / 147 / 146 / 14b`
   - 只做最短、最可能改变排序的一刀

## 3) 为什么本轮要把 `Rank 148` 提到第一位

### `Rank 148`
- 刚完成 fresh intake reader-facing 守门。
- 它提供的是 **独立 raw-alpha 家族**，不是现有 breakout/filter 叙事的近义补丁。
- 当前弱点也很清楚：
  - 大币快检只到 `morning ≈ +0.33 bps/day, Sharpe ≈ 0.17`
  - `close ≈ -0.92 bps/day, Sharpe ≈ -0.54`
- 所以下一步不该再停留在“概念成立吗”，而是要做 **是否存在更可交易 pocket** 的 decisive follow-up。

### `Rank 125 / 112 / 111`
- 这三条都已经完成本轮该做的 decisive 收口：
  - `125`：train/test consistency 不过，固定 `keep_P1`
  - `112`：train/test fallback 不过，固定 `keep_P1`
  - `111`：固定为 evidence anchor / diagnostic overlay
- 它们现在仍然 relevant，但已经不该占默认前排执行位。

### `Rank 140 / 145 / 147 / 146 / 14b`
- 这些条目仍是 reserve，但当前更像 **fallback / compare / method reserve**。
- 如果 fresh intake 没有形成新动能，再轮到它们是合理的；但不该先于 `Rank 148`。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 将 `Rank 148` 提到 `Active Scout` 第 1 位
  - 将 `125 / 112 / 111` 下沉为已固定 verdict 的旧 `P1`
  - 将 `Next 3 bot3 runs` 改写为具体 rank/动作，而不是泛泛描述
- 新增本轮 strategy review 日志
- 未新增 `P3`
- 未改动 `Paper / 待开启自动运行`

## 6) desk-level final call
- `recommended_action = make Rank148 the next decisive bot3 run`
- `why_now = 它是当前唯一刚入板且家族独立的 raw-alpha 候选；若不立刻做 follow-up，desk 很快又会滑回在旧 P1 上打转。`
- `main_weakness = 当前 desk 仍没有新 P2/P3 动能；本轮更多是在把默认前排执行位重新对准最新、最独立的候选。`
