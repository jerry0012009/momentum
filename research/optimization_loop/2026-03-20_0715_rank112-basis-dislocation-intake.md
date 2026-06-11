# 2026-03-20 07:15 UTC · Rank 112 basis dislocation short veto intake

## 本轮先检查了什么
- repo status：`master`
- dirty files：`git status --short | wc -l = 1696`
- 最近 optimization logs：最新到 `2026-03-20_0652_rank111_event_clock_clean_replication.md`
- EMA due guardrail：当前全 desk 已回到 `waiting_not_due`
  - 最近 due：`美股 1d+1wk -> 2026-03-20 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`
  - `创业板ETF 1d -> 2026-03-23 07:00 UTC`
- narrow paper 托管：`manual_narrow_paper_last_run_summary.json @ 2026-03-20T06:52:36Z` 仍为 `new_closed_trades_appended=0`

## 顶板执行判断
- 当前 authoritative `Next 3`（`docs/TODO.md` 顶板 `2026-03-20 07:06 UTC`）要求：
  1. `Run 1 = EMA due-check first`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 basis dislocation short veto 1 次 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 basis guard-pass，则只给它 1 次最小 clean replication；若 basis hard-fail / exhausted，则切 alpha-beta abstain / profit-window 的 ex-ante honesty gate source intake`
- 实测 `EMA` 已在 `07:01 UTC` 完成 A 股 primary refresh，当前仍是 `waiting_not_due`；因此本轮合法主动作明确落在 `Scout Seat`。
- 重新比较 active Scout 的当前边际价值后，这轮仍应只认领一个主点：
  1. `basis dislocation short veto`（fresh paper+public-data reserve / source intake next）
  2. `alpha-beta abstain / profit-window`（紧邻 reserve；仅当 basis hard-fail 才接手）
  3. `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`，不再默认续命）

## 本轮动作
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这轮把 `basis dislocation short veto` 正式冻结为 **`Rank 112 / basis dislocation short veto`**。
- 完成了它的 **`source intake + 两条轻量诚实守门`**，不并开 `alpha-beta`，也不回头挤占 `P3 continuity`。

## 两条轻量诚实守门结果
### 1) trade on / trade off 是否能清楚写出来？
可以，而且需要收得很窄：
- `trade on`：只在既定 `breakout-short / breakdown` 触发已出现后，把 `basis dislocation` 当作 **no-short veto**；若触发前最近一个已完成窗口里，`basis_pct_30d <= 10%` 且 `oi_delta_1h <= 0`，则默认 `skip short`。
- `trade off`：它不是独立 alpha、也不是逐根 15m 主信号；不能脱离 base setup 单独开仓，也不能把 funding / basis 的事后极值直接翻译成新入场键。

### 2) 是否存在明显 lookahead / repaint / data leakage？
当前未见一眼判死刑的结构性作弊，但必须把边界写死：
- `basis` 必须取 `signal` 当根之前最后一个已完成 premium-index 窗口，或等价的 signal 前冻结 snapshot；
- `basis_pct_30d` 只能按各 symbol 自身 rolling history 事先标准化，不能事后用整段样本重算阈值；
- `oi_delta_1h` 只能由 signal 前可见的公开 OI 序列构成；
- 下一轮 clean replication 强制统一到 **`signal 当根及之前数据 + next-bar open + no-overlap`**，禁止用 signal 后 mark/index 漂移、未来 funding、或事后更换窗口倒灌当前 veto。

## 本轮 hard verdict
**`Rank 112 / basis dislocation short veto = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线值得拿 **1 次最小 clean replication** 预算；
- 但它当前只配先作为 **breakout-short 的拥挤/透支 veto** 来验证，不能偷渡成新的 shared alpha，更不能直接越级去争 `Live Seat`。

## Reader-facing 落点
- source-intake artifact：`reports/artifacts/literature/scout_rank112_basis_dislocation_short_veto_source_intake_card.csv`
- reader-facing page：`reports/site/reading/repo_scout/rank112_basis_dislocation_short_veto_source_intake.html`

## 本轮后席位判断
- `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = Rank 112 / basis dislocation short veto`

## 更新后的 active Scout 顺序
1. `Rank 112 / basis dislocation short veto`（`P1 weak candidate / guard-passed / admit_to_clean_replication_queue`）
2. `alpha-beta abstain / profit-window`（`P0 / fresh paper+repo reserve / ex-ante translation honesty gate first`）
3. `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）
4. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
5. `Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
6. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 hosted continuity / sidecar only`）

## 下一拍 Next 3
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 112 1 次最小 clean replication`
3. `Run 3 = 若 Rank 112 clean replication hard-fail / exhausted，则切 alpha-beta abstain / profit-window 的 ex-ante honesty gate source intake；只有这层也 exhausted 后，才允许回退到 tiny-live plumbing`
