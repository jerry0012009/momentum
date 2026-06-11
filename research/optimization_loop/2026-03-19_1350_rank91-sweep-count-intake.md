# 2026-03-19 13:50 UTC — Rank 91 same-level consecutive sweep count intake

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1431`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
    - `2026-03-19_1300_rank90-close-range-compression-intake.md`
    - `2026-03-19_1252_rank89-clean-replication-park.md`
- 已再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（命令按预期以 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 6.1h`、`Crypto 10.1h`、`A股 17.1h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮不能伪造 refresh，也不该回头挤占 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / Rank 91 / same-level consecutive sweep count level-memory gate` source intake + 两条轻量诚实守门
- **紧邻子点**：把这条线正式冻结成 queue-facing `Rank 91`，并写回 `TRADING DESK BOARD / Next 3`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板与 `13:27 UTC` strategy review 重排当前允许动作：
1. `Rank 91 / same-level consecutive sweep count level-memory gate`
2. `Rank 92 / opening-drive adaptive offset continuation gate`
3. `Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，因为：
- `Rank 90` 已在 13:26 UTC 收口为 `keep_P1 / evidence_pool`，不再值得继续霸占主资源；
- `Rank 91` 是新的 paper / repo based `5m / 15m crypto` fresh intake，且比 `Rank 92` 更便宜：不需要先冻结 opening-drive / session 边界；
- 它更像三条主线可共用的 **level-memory gate**，而不是继续放大 breakout 叙事。

## 本轮执行内容
### 1) 正式冻结顺序 Rank
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条线现正式冻结为：
  - **`Rank 91 / same-level consecutive sweep count level-memory gate`**

### 2) 两条轻量诚实守门
- **trade on**
  - 只把它降级成 `shared level-memory gate`，不是新的独立 alpha；
  - 基础 setup 继续负责方向与价位；这层只回答候选 level 在最近 `10` 根左右是否已经出现过一次同价位 sweep 记忆；
  - 首轮冻结为：
    - bull gate：`low < priorLow && close >= priorLow && vol_ratio >= 1.2`
    - bear gate：`high > priorHigh && close <= priorHigh && vol_ratio >= 1.2`
    - level 对齐：若与上一次 sweep 的 level 距离不超过约 `0.5% * close` 且间隔不超过 `10` 根 bar，则记作 `same-level consecutive sweep`
    - 默认只让 `consec2+` 参与 gate
- **trade off**
  - 若只是单次 wick / 单次 close-back-inside，或 level 对齐并不成立，就不得硬说它形成了 level memory；
  - 这条线不能单独开仓，也不能偷渡成新的 breakout 主叙事；
  - 若后续改善主要来自极端缩样本，它也只能当 veto / admission 过滤层，而不是 promotion 证据。
- **lookahead / repaint / leakage**
  - prior high/low、volume ratio、same-level 容差与 consecutive count 都必须只用 `signal` 当根及之前可得的 `15m` 数据构造；
  - desk 迁移统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
  - 不得把后续几根 bar 是否 hold / fail 的结果反写回 count，也不得事后重选更漂亮的 level 容差。

## Hard verdict
- **`Rank 91 = guard-passed / admit_to_clean_replication_queue`**

这轮只做到 intake 与诚实守门，不提前偷跑 clean replication。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/literature/scout_rank91_same_level_sweep_count_source_intake_card.csv`

### reader-facing 网页
- `reports/site/reading/repo_scout/rank91_same_level_sweep_count_source_intake.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `13:50 UTC` 补充，冻结 `Rank 91 / same-level consecutive sweep count level-memory gate = guard-passed / admit_to_clean_replication_queue`；
- 当前 active Scout 顺序改写为：
  1. `Rank 91 / same-level consecutive sweep count level-memory gate`
  2. `Rank 92 / opening-drive adaptive offset continuation gate`
  3. `Rank 90 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  4. `P3 continuity`
  5. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 91 已完成 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 91 已 guard-pass 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 91 clean replication 直接 hard-fail / park，则切 Rank 92 source intake`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/site/reading/repo_scout/rank91_same_level_sweep_count_source_intake.html`
  - `reports/artifacts/literature/scout_rank91_same_level_sweep_count_source_intake_card.csv`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1431`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接对 `Rank 91` 做唯一允许的那 1 次最小 clean replication；
- 若 `Rank 91` clean replication 直接 hard-fail / park，再切 `Rank 92 / opening-drive adaptive offset continuation gate` source intake；
- `P3 continuity` 继续只保留在 fresh Scout 之后。
