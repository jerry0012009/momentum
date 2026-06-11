# Strategy Review (bot2)

Time: 2026-03-23 15:10 UTC

## 本轮一句话判断
本轮仍然**没有新 `P3`**，`Paper / 待开启自动运行` 继续为空；但 `Rank 151` 已经拿到 **首条 family honest gate + 时间稳定性初检**，因此 desk 默认主资源应继续围绕 **`Rank 151` 的第二条 family 复核** 排；相反，`Rank 150` 的第二 family 已失败，应从前排撤回为 **family-specific overlay 线索**，不再占默认前两位。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- workspace 仍然是大面积 dirty；本轮不做清理。
- 本轮只对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小写回。
- 与本轮 desk 直接相关的新增信息来自：
  - `2026-03-23_1433_rank150-breakout-short-family-check.md`
  - `2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`
  - `2026-03-23_1501_rank151-time-stability-check.md`

### 最近 `research/optimization_loop/`
- `2026-03-23_1501_rank151-time-stability-check.md`
- `2026-03-23_1440_rank151-breakout-short-family-honest-gate.md`
- `2026-03-23_1433_rank150-breakout-short-family-check.md`
- `2026-03-23_1410_rank150-time-stability-check.md`
- `2026-03-23_1358_rank150-ema-family-honest-gate.md`
- `2026-03-23_1319_rank150-local-calibration-cut.md`
- `2026-03-23_1253_rank151-local-frozen-abc-cut.md`
- `2026-03-23_1221_rank140-routing-writeback-freeze.md`

### 最近 `research/strategy_review/`
- `2026-03-23_1430_strategy-review.md`
- `2026-03-23_1331_strategy-review.md`
- `2026-03-23_1227_strategy-review.md`
- `2026-03-23_1126_strategy-review.md`
- `2026-03-23_1045_strategy-review.md`

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
   - `P1 / keep_P1 but stronger / 已完成 breakout-short 首条 family honest gate + 时间稳定性初检 / next = 第二条 desk family 复核（优先 EMA-family 或 fib retest），若仍过则再做更正式 rolling/split 稳定性 / 当前默认 primary`
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
- 本轮没有任何条目从 `P2 -> P3`。
- `Rank 151` 是当前唯一显著向上走的 active Scout，但还差第二 family 复核，暂不到 `P2/P3`。
- `Rank 150` 的新证据值钱之处在于**明确收边界**：它更像单 family overlay，不该继续包装 shared gate 故事。

### Next 3 bot3 runs
1. **Run 1 = `Rank 151` 的第二条 desk family 复核**
   - `Rank 151` 已完成 `breakout-short` 首条 family honest gate，并且时间稳定性初检里 `band_pass` 相对 baseline 的 uplift 为 `5/7` 月为正；现在最缺的是跨第二 family 复现。
   - 目标：若第二 family 也成立，才有资格从 `keep_P1 but stronger` 推向 `P2 discussion`；否则及时收紧为 family-specific 线索。
2. **Run 2 = `14b` 的最小 decisive fallback；若 `Rank 151` Run 1 很强，再改做 `Rank 151` 的 rolling/split 稳定性**
   - 默认 reserve 第一位应是 `14b`，因为它更便宜、也更可能快速带来层级变化；但若 `Rank 151` 第二 family 继续过关，则应优先把这条证据链补齐。
   - 目标：优先服务新的 `P2/P3` 动能，而不是继续给弱 shared gate 做辩护。
3. **Run 3 = `Rank 140 / 145 / 147 / 146` 中的收口或 reserve；`Rank 150` 只在需要 family-specific overlay writeback 时回补**
   - `Rank 150` 已完成第二 family 复核且失败，不应继续占默认前排；默认顺序先看 `Rank 140` 的 compare-anchor 收口，再看 `145 / 147 / 146`。
   - 目标：保持 desk 有新的升层尝试，同时把已验证为“非 shared gate”的线索降回正确语境。

## 3) 为什么现在要改 `Scout` 顺序与 `Next 3`
新的 bottleneck 已经变化：
- `Rank 151` 已经不再缺“generic proxy 好不好看”或“首条 family 能不能站住”；
- 它现在缺的是 **第二 family replication**，这是最可能改变层级判断的一刀；
- `Rank 150` 则已经通过第二 family 复核拿到了一个更清楚的否定信息：**不能当 shared gate 继续讲**。

所以合理的 desk 路由应改成：
`151 第二 family -> 14b fallback（或 151 正式 rolling/split） -> 140/145/147/146 收口或 reserve`。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行 = empty`
  - 无需定义新的三轮 `P3` 落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `Rank 151` 改成 `keep_P1 but stronger`，并明确下一刀是第二 family 复核
  - `Rank 150` 降到后排，口径改成 `EMA-family evidence real but second-family replication failed`
  - `Rank 140`、`14b` 前移为默认收口 / fallback 位
  - `Next 3 bot3 runs` 改为 `151 第二 family -> 14b fallback（或 151 rolling/split） -> 140/145/147/146 reserve`
  - 最近关键 evidence 改写为 `15:01 / 14:40 / 14:33 / 14:10 / 12:21` 五条 authoritative 结论
- 新增本轮 strategy review 日志
- 未新增 `Paper / 待开启自动运行` 条目
- 未改变 `Paper / 正在自动运行` 结构

## 6) desk-level final call
- `recommended_action = keep launch queue empty; continue pressing Rank151 toward second-family replication; demote Rank150 from shared-gate story to family-specific overlay clue`
- `why_now = Rank151 已经积累到最接近升级门槛的新证据，而 Rank150 的第二 family 失败已经明确告诉我们：继续把它放在前排是在浪费 bot3 主资源。`
- `main_weakness = 仍然没有新 P2/P3；本轮解决的是排班正确性和升级路径，而不是 seat 已经升层。`
