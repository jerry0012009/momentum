# 2026-03-19 12:19 UTC — Rank 89 outside-close -> back-inside-close failure verdict intake

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1406`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1201_rank88-clean-replication-park.md`
    - `2026-03-19_1149_rank88_macro_event_overlay_intake.md`
    - `2026-03-19_1126_rank87-clean-replication-park.md`
- 已实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 7.7h`、`Crypto 11.7h`、`A股 18.7h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作必须切到 `Scout Seat / breakout-centric backlog fresh intake`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / outside-close -> back-inside-close failure verdict` source intake + 两条轻量诚实守门
- **紧邻子点**：把这条线正式冻结成顺序 rank，并写回 `TRADING DESK BOARD / Next 3`

## 先比较 active Scout 候选边际价值（3.5）
本轮重新比较当前允许动作：
1. `outside-close -> back-inside-close failure verdict`
2. `close-range compression asymmetry`
3. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，不是为了重新强调 breakout，而是因为：
- 顶板已经明确写死：breakout backlog 里默认先认领它；
- 它更像一条 **post-break failure verdict / re-entry 判决层**，比“看到破位就继续追”更诚实；
- 在 `EMA = waiting_not_due` 时，它比回头给旧 `P1 evidence_pool` 续命更符合当前 desk 纪律。

## 本轮执行内容
### 1) 正式冻结顺序 Rank
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条线现正式冻结为：
  - **`Rank 89 / outside-close -> back-inside-close failure verdict`**

### 2) 两条轻量诚实守门
- **trade on**
  - 只把它降级成 `post-break failure verdict / entry veto or reversal overlay`；
  - 先定义 rolling 区间（默认 `N=16` 根 15m）；
  - 只有先出现 `outside close`，再在 `M=1~4` 根内出现 `back-inside close`，才把这次 break 判成 failure event；
  - 顶部外扩回内优先映射成 short verdict，底部外扩回内优先映射成 long verdict。
- **trade off**
  - 若只是区间内震荡、或 break 后继续沿外侧走但没有回到区间内，就不得硬判成 failure verdict；
  - 它不能偷渡成新的独立 alpha，也不能把任何回踩都包装成 `re-entry setup`。
- **lookahead / repaint / leakage**
  - `zone_high / zone_low`、`outside close`、`back-inside close` 与 breakout sequence extreme 都必须只用 `signal` 当根及之前可得的 `15m/5m` 数据构造；
  - desk 迁移统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
  - 不得把后续 overshoot、future session path 或事后主观画区间倒灌回 gate。

## Hard verdict
- **`Rank 89 = guard-passed / admit_to_clean_replication_queue`**

这轮只做到 intake 与诚实守门，不提前偷跑 clean replication。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/literature/scout_rank89_outside_close_back_inside_failure_source_intake_card.csv`

### reader-facing 网页
- `reports/site/reading/repo_scout/rank89_outside_close_back_inside_failure_source_intake.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `12:19 UTC` 补充，冻结 `Rank 89 / outside-close -> back-inside-close failure verdict = guard-passed / admit_to_clean_replication_queue`；
- 当前 active Scout 顺序改写为：
  1. `Rank 89 / outside-close -> back-inside-close failure verdict`
  2. `close-range compression asymmetry`
  3. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
  4. `P3 continuity`
  5. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 89 已完成 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 89 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 89 clean replication 直接 hard-fail / park，则再切 close-range compression asymmetry；只有这一层也 exhausted，才允许回退到 Rank 82 / 80 / 81 evidence_pool > tiny-live plumbing`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/site/reading/repo_scout/rank89_outside_close_back_inside_failure_source_intake.html`
  - `reports/artifacts/literature/scout_rank89_outside_close_back_inside_failure_source_intake_card.csv`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1406`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接对 `Rank 89` 做唯一允许的那 1 次最小 clean replication；
- 若 `Rank 89` clean replication 直接 hard-fail / park，再切 `close-range compression asymmetry`；
- 仍不要回头给 `Rank 82 / 80 / 81 evidence_pool` 续命，也不要挤占 `P3 continuity`。
