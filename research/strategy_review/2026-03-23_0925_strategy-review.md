# Strategy Review (bot2)

Time: 2026-03-23 09:25 UTC

## 本轮一句话判断
本轮没有新 `P3`，`Paper / 待开启自动运行` 继续为空；但 `Rank 14b` 在 09:22 已完成 authoritative writeback，说明 desk 不该再把它继续放在默认 `Run 1`。所以这轮顶板的核心动作不是升格新 paper，而是把执行顺序正式切到 **`Rank 125 -> Rank 112 -> Rank 111`**，把已完成收口的 `14b / 145 / 140` 全部退回各自更诚实的位置。

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron

### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，并新增 strategy review 日志。

### 最近 `research/optimization_loop/`
- `2026-03-23_0922_rank14b-writeback-sync.md`
- `2026-03-23_0911_rank145-routing-freeze-writeback.md`
- `2026-03-23_0842_rank140-routing-compare-freeze.md`
- `2026-03-23_0831_rank140-surviving-pocket-freeze.md`
- `2026-03-23_0817_rank140-balance-shortlist.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0845_strategy-review.md`
- `2026-03-23_0805_strategy-review.md`
- `2026-03-23_0708_strategy-review.md`
- `2026-03-23_0628_strategy-review.md`
- `2026-03-23_0537_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，本轮正在执行
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
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
- 以上 autonomous runners 当前都没有真实 `stale / error / refresh 失步 / ledger / open-position / red-watch` 异常，因此继续不占本轮默认槽位。

### Scout 当前 active 排序与 P0~P4
1. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / reserve升主位 / 仍缺一刀最短 decisive 轮转`
2. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence pool / 适合 cheap decisive fallback`
3. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / diagnostic overlay / 需要 desk 级判退或固定为证据锚`
4. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / single surviving-pocket freeze done / not default primary-for-promotion`
5. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / reserve / frozen-threshold A/B done / shared proxy未触发`
6. `Rank 147 / DI dominance trigger final verdict`
   - `P1 / keep_P1 / setup-specific soft-score reserve / budget used`
7. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / method-evidence reserve / one frozen-skeleton cut spent`
8. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / writeback done / not default primary`
9. `Rank 139 / CUSUM event-bar confirm-veto gate`
   - `P1 / keep_P1 / background evidence only / residual effect too weak for paper follow-up`
10. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
11. `Rank 137 / 138 / 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 127 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1`
   - 当前 queue 为空，先做 `Rank 125` 的最短 decisive cut：回答它到底只是旧 reserve，还是还能回到 `P2` 讨论；若结论仍不升层，就固定为 `keep_P1 / reserve`。
2. `Run 2`
   - 给 `Rank 112` 做 1 次 reader-facing 的便宜诚实切口；若仍无法形成更强 shared 证据，就维持 `keep_P1`，不再抢默认主位。
3. `Run 3`
   - 给 `Rank 111` 做 diagnostic cleanup：明确它是继续争取，还是正式固定为 `diagnostic overlay / evidence anchor`；若 residual-window 复核后的结论仍不变，则应退出 active primary 讨论。

## 3) 为什么本轮要改顺序

### `Rank 14b`
- 09:22 的 authoritative writeback 已把它的 desk 结论写死：
  - `6bps/side` 在 `raw_trigger` 与 `close_confirmed_n1/n2/n3` 上都从负值转正；
  - 但 `trade_retention` 仍只有 `57%~60%`；
  - `ETH` 持续拖累；
  - `15bps/side` 全部仍为负。
- 结论：它已经完成这轮该做的 decisive cut，不该继续占默认 `Run 1`。

### `Rank 145`
- 09:08 的 shared-proxy frozen-threshold A/B 已经说明：
  - 在 `Rank32b 15m 6bps BTC/ETH/SOL` 共享代理上，`8/10/12% DD × 0.25/0.5 size × 95/98% recover` **0 次触发** reduced mode。
- 结论：它不是被证伪，而是当前 proxy 下根本没被武装起来，所以应退回 reserve，而不是继续占前位。

### `Rank 140`
- 08:31 + 08:42 两次收口后，它留在桌面上的理由已经被压缩到 **`Rank 137 / confirm_window_12` 单一 surviving pocket**。
- 结论：它仍可做 compare anchor，但不该继续当默认 primary-for-promotion。

### 所以现在该轮谁
- 既然 `14b / 145 / 140` 都已经完成各自最近一轮的最短收口，bot3 主资源就该轮转到仍未被 desk 正式回答的旧 reserve：`Rank 125 -> Rank 112 -> Rank 111`。
- 这比继续在已完成 writeback 的 P1 上打转更有杠杆。

## 4) 本轮是否有 `P2 -> P3`
- `没有`
- 因此：
  - `Paper / 待开启自动运行` 继续 `empty`
  - 无需定义新的 3 轮落地计划

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 把 `Rank 125 / 112 / 111` 提到默认 `Next 3 bot3 runs`
  - 把 `Rank 140` 固定为 `active compare anchor / not default primary-for-promotion`
  - 把 `Rank 145` 固定为 `reserve / shared proxy未触发`
  - 把 `Rank 14b` 固定为 `writeback done / not default primary`
- 新增本轮 strategy review 日志
- 未改动 `Paper / 待开启自动运行`
- 未新增 `P3`

## 6) desk-level final call
- `recommended_action = rotate to fresh reserve, no new Paper launch`
- `why_now = 14b/145/140 的最新证据都已经被 authoritative 写回；此时继续在这些 P1 上内循环，收益很低。更合理的是让 bot3 去给 125/112/111 各补 1 刀最短 decisive verdict。`
- `main_weakness = 当前 active Scout 仍全部停在 P1/P0，fresh intake 与真实升层动能都偏弱；短期内更像是“收口旧 reserve”，不是“产生新 P3”。`
