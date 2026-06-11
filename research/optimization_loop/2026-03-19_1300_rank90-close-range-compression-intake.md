# 2026-03-19 13:00 UTC — Rank 90 close-range compression asymmetry intake

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1417`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1252_rank89-clean-replication-park.md`
    - `2026-03-19_1219_rank89-outside-inside-intake.md`
    - `2026-03-19_1201_rank88-clean-replication-park.md`
- 已再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 7.0h`、`Crypto 11.0h`、`A股 18.0h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作必须切到 `Scout Seat / close-range compression asymmetry intake`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / close-range compression asymmetry` source intake + 两条轻量诚实守门
- **紧邻子点**：把这条线正式冻结成顺序 `Rank 90`，并写回 `TRADING DESK BOARD / Next 3`

## 先比较 active Scout 候选边际价值（3.5）
本轮重新比较当前允许动作：
1. `close-range compression asymmetry`
2. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
3. `P3 continuity`
4. `tiny-live plumbing`

当前把第 1 条排第一，不是为了重新强调 breakout，而是因为：
- 顶板已经明确写死：`Rank 89` hard-fail / park 后，下一步就是认领这条 backlog；
- 它更像一条 **shared long-admission + short-veto gate**，仍直接服务当前 paper / repo 主线；
- 在 `EMA = waiting_not_due` 时，它比回头给 `Rank 82 / 80 / 81` 续 1 次便宜检查更符合当前 Scout 预算纪律。

## 本轮执行内容
### 1) 正式冻结顺序 Rank
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条线现正式冻结为：
  - **`Rank 90 / close-range compression asymmetry`**

### 2) 两条轻量诚实守门
- **trade on**
  - 只把它降级成 `shared admission / veto gate`；
  - 沿用 digest 的 close-range compression 骨架：`consolidating(t-1)` 负责回答最近 `N` 根 close 是否压在窄区间内；
  - long 侧只有 `consolidating + 向上 breakout` 才允许放行；
  - short 侧默认不是 breakout amplifier，而是若 breakdown 仍落在压缩释放语境里，则更偏向 `veto / half-size`。
- **trade off**
  - 若只是普通区间波动、没有明确 compression，就不得硬说它提供 admission；
  - short 侧不能因为“向下突破”就自动包装成 continuation edge；
  - 它不能偷渡成新的独立 alpha，也不能单独开仓。
- **lookahead / repaint / leakage**
  - `consolidation window`、区间高低、以及 breakout / breakdown 判定都必须只用 `signal` 当根及之前可得的 `15m/5m` 数据构造；
  - desk 迁移统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
  - 不得把后续 4~8 bar continuation、future session path 或事后挑出的更漂亮窄区间倒灌回 gate。

## Hard verdict
- **`Rank 90 = guard-passed / admit_to_clean_replication_queue`**

这轮只做到 intake 与诚实守门，不提前偷跑 clean replication。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/literature/scout_rank90_close_range_compression_asymmetry_source_intake_card.csv`

### reader-facing 网页
- `reports/site/reading/repo_scout/rank90_close_range_compression_asymmetry_source_intake.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `13:00 UTC` 补充，冻结 `Rank 90 / close-range compression asymmetry = guard-passed / admit_to_clean_replication_queue`；
- 当前 active Scout 顺序改写为：
  1. `Rank 90 / close-range compression asymmetry`
  2. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
  3. `P3 continuity`
  4. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 90 / close-range compression asymmetry 已完成 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 90 已 guard-pass 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 90 clean replication 直接 hard-fail / park，则才允许回退到 Rank 82 / Rank 80 / Rank 81 evidence_pool；P3 continuity 与 tiny-live plumbing 继续不得插队`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/site/reading/repo_scout/rank90_close_range_compression_asymmetry_source_intake.html`
  - `reports/artifacts/literature/scout_rank90_close_range_compression_asymmetry_source_intake_card.csv`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1417`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接对 `Rank 90` 做唯一允许的那 1 次最小 clean replication；
- 若 `Rank 90` clean replication 直接 hard-fail / park，再回退到 `Rank 82 / 80 / 81 evidence_pool`；
- 仍不要让 `P3 continuity` 插队。
