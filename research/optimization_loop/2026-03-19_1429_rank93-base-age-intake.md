# 2026-03-19 14:29 UTC — Rank 93 first-major-break base-age gate intake

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short | wc -l = 1449`
  - 最近 optimization logs 最新到：
    - `2026-03-19_1403_rank91-clean-replication-keep-p1.md`
    - `2026-03-19_1350_rank91-sweep-count-intake.md`
    - `2026-03-19_1326_rank90-clean-replication-keep-p1.md`
- 已再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（命令按预期以 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 5.5h`、`Crypto 9.5h`、`A股 16.5h`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮不能伪造 refresh，也不该回头挤占 `P3 continuity`。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / Rank 93 / first-major-break base-age gate` source intake + 两条轻量诚实守门
- **紧邻子点**：把这条线正式冻结成 queue-facing `Rank 93`，并写回 `TRADING DESK BOARD / Next 3`

## 先比较 active Scout 候选边际价值（3.5）
本轮按顶板与 `14:22 UTC` strategy review 重排当前允许动作：
1. `Rank 93 / first-major-break base-age gate`
2. `Rank 92 / opening-drive adaptive offset continuation gate`
3. `Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

当前把第 1 条排第一，因为：
- `Rank 91` 已在 14:03 UTC 收口为 `keep_P1 / evidence_pool`，不再值得继续霸占主资源；
- `Rank 93` 是新的 paper / repo based `5m / 15m crypto` fresh intake，且比 `Rank 92` 更便宜：不需要先冻结 opening-drive / session 边界；
- 它更像三条主线可共用的 **duration / base-age gate**，而不是继续放大 breakout 叙事。

## 本轮执行内容
### 1) 正式冻结顺序 Rank
- 为遵守“进入 queue-facing 层必须先拿顺序 Rank”的规则，这条线现正式冻结为：
  - **`Rank 93 / first-major-break base-age gate`**

### 2) 两条轻量诚实守门
- **trade on**
  - 只把它降级成 `shared admission + size-down overlay`，不是新的独立 alpha；
  - 首轮冻结成：
    - `up_break_event = close > rolling_high_20.shift(1)`
    - `down_break_event = close < rolling_low_20.shift(1)`
    - 再计算最近一次同方向 break 距今经过的 bar 数 `base_age`
  - long 侧仅当最近 `L=4` 根内出现过同方向 up-break，且 `base_age >= 24/36` 时才放行；
  - short 侧若 recent down-break 不 fresh（如 `base_age < 24/36` 或没有 fresh down-break），则默认 `half-size / veto`，不把它偷渡成 short amplifier。
- **trade off**
  - 若当前 setup 前根本没有 fresh 同方向 first break，或只是反复破来破去的旧 level 噪音，就不得硬说这次 continuation / retest 值得放行；
  - 这条线不能单独开仓，也不能把“不是 first break”倒灌成事后解释。
- **lookahead / repaint / leakage**
  - `rolling_high/low_20`、break event 与 `base_age` 都必须只用 `signal` 当根及之前可得的 `15m` 数据构造；
  - desk 迁移统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
  - 不得把后续 overshoot、future path 或事后挑出的更漂亮 base 区间倒灌回 gate。

## Hard verdict
- **`Rank 93 = guard-passed / admit_to_clean_replication_queue`**

这轮只做到 intake 与诚实守门，不提前偷跑 clean replication。

## 新增产物（deployable / reader-facing）
### artifact
- `reports/artifacts/literature/scout_rank93_first_major_break_base_age_source_intake_card.csv`

### reader-facing 网页
- `reports/site/reading/repo_scout/rank93_first_major_break_base_age_source_intake.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `14:29 UTC` 补充，冻结 `Rank 93 / first-major-break base-age gate = guard-passed / admit_to_clean_replication_queue`；
- 当前 active Scout 顺序改写为：
  1. `Rank 93 / first-major-break base-age gate`
  2. `Rank 92 / opening-drive adaptive offset continuation gate`
  3. `Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`
  4. `P3 continuity`
  5. `tiny-live plumbing`
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = Rank 93 已完成 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 93 已 guard-pass 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 93 clean replication 直接 hard-fail / park，则切 Rank 92 source intake`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/site/reading/repo_scout/rank93_first_major_break_base_age_source_intake.html`
  - `reports/artifacts/literature/scout_rank93_first_major_break_base_age_source_intake_card.csv`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件（`1449`）。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要空转；
- 直接对 `Rank 93` 做唯一允许的那 1 次最小 clean replication；
- 若 `Rank 93` clean replication 直接 hard-fail / park，再切 `Rank 92 / opening-drive adaptive offset continuation gate` source intake；
- `P3 continuity` 继续只保留在 fresh Scout 之后。
