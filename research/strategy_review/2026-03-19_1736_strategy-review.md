# 2026-03-19 17:36 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前仍应先把 **`Rank 95 / Vajra controlled-pullback depth-budget`** 的那 1 次 `time-stability` 诚实检查跑完，但这手做完就不该再无限停在 `P1`；若它没有被诚实推到 `P2`，默认下一手直接切到新的 fresh repo 候选 **`Rank 96 / AdvancedMA retest-count admission layer`**。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1491`，工作区仍有大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1716_rank95-clean-replication-keep-p1.md`
  - `2026-03-19_1703_rank95-source-intake.md`
  - `2026-03-19_1632_rank92-time-stability-park.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1641_strategy-review.md`
  - `2026-03-19_1601_strategy-review.md`
- 最新 fresh repo digest（重点核对）：
  - `2026-03-19_1734_advancedma-retest-count-admission-layer.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled（本轮正在运行）
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 2.4h`、`Crypto 6.4h`、`A股 13.4h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T17:08:55Z`：`new_closed_trades_appended=0`
  - 结论：当前 hosted lanes 没有新的 status-changing event，不足以挤掉 Scout fast lane。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 market clock 的真实等待，不是整桌等待；`EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 95` 目前仍只是 **`P1 / mixed but honest`**，还没通过那 1 次真正会改变 verdict 的时间稳定性检查；
  2. `Rank 96` 只是新的 **fresh repo backlog**，还没过 `source intake + 两条轻量诚实守门`；
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81` 都更像 `P1 evidence_pool / budget used`；
  4. `Rank 92 / 94` 已压回 `park / evidence pool`；
  5. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper continuity / hosted lanes`，不是待升格 live 候选。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 95 / Vajra controlled-pullback depth-budget`
- **当前紧邻后备：**
  - `Rank 96 / AdvancedMA retest-count admission layer`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 92 / opening-drive adaptive offset continuation gate`
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 95 = P1`**（`clean replication 已完成 / Light Stability Pack: 时间稳定性 next`）
- **`Rank 96 = P0`**（`fresh repo backlog / source intake + 两条轻量诚实守门 next`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 92 / Rank 94 = P0`**（`park / evidence_pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 95 / Vajra controlled-pullback depth-budget` 的 1 次 truly verdict-changing 时间稳定性检查**
   - 直接复用当前 `clean replication` 的 `trade_log / time_bucket_summary` 口径；
   - 不追新 bar、不改规则；
   - 直接回答 `promote_to_P2 / keep_P1 / park`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 95` 的时间稳定性**清楚通过最小升格阈值**，直接把它写成 `promote_to_P2 / paper candidate`，而不是再补近义检查；
   - 若 `Rank 95` 只是继续 `keep_P1` 或直接 `park`，则**停止继续磨同一条线**，默认切到 `Rank 96 / AdvancedMA retest-count admission layer` 的 `source intake + 两条轻量诚实守门`；
   - 只有 `Rank 96` 这一层也 `hard-fail / exhausted`，才允许回退到 `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 95 / Vajra controlled-pullback depth-budget`**
   - 当前排第一，不是因为它已经强，而是因为它距离一个清晰的 `promote / park / cut` judgment 只差 **1 次 truly verdict-changing 的时间稳定性检查**；
   - 按 desk 纪律，P1 到这一步就不该再无限磨，所以先把这手 cheap honest check 跑完最值钱。
2. **`Rank 96 / AdvancedMA retest-count admission layer`**
   - 当前排第二，因为它是最新的 **fresh repo-based / 15m 相关** 候选，而且已经给出更具体的新 shared 问题：`retestCount>=2` 更像 breakout-short follow-up 的 admission layer，对 Fib / EMA long 只算减亏、不算翻正；
   - 这比回头继续给旧 `P1 evidence_pool` 续命，更可能改变当前 desk judgment。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；这些线都不是零价值，但都更像**预算已用、缺少新 gate**的残留池；
   - 如果这轮继续默认回头磨它们，会违反“先硬门槛、再分级、再限预算”的纪律。
4. **`Rank 92 / Rank 94 park / evidence_pool`**
   - 当前只排第四；都已经在真正会改变 verdict 的检查后被压回 `park`，不应再回抢默认主资源位。
5. **`P3 continuity`**
   - 当前只排第五；`17:08 UTC` 最新 summary 仍是 `new_closed_trades_appended=0`，没有 status-changing event 插队理由。
6. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 fresh paper/repo intake 仍不空的情况下，不应抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 95` 已完成 source intake + clean replication，且当前只剩 1 次 truly verdict-changing 的时间稳定性检查**：这使它比直接切新源更接近一个真实的 `promote / park / cut` 决策。
3. **`Rank 96 / AdvancedMA` 给出的 shared 问题更具体**：`retestCount>=2` 对 short follow-up 更像 admission layer，而 long 侧并未翻正，因此它天然更适合先做 `source intake`，而不是过早宣传成 shared hard gate。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 17:08 UTC = new_closed_trades_appended=0`，降低了 continuity 插队必要性。

## 当前 weakest / should-park lines
- **`Rank 92`**：时间稳定性不过关，已该老实留在 `park / evidence pool`。
- **`Rank 94`**：clean replication 后已明确 `park / evidence pool`，不应回抢资源。
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`**：继续存在，但当前默认都更像 `budget used` 的证据池，而不是应优先继续打磨的 active Scout。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 95` 的时间稳定性检查跑完，并在这一手之后强制做 `promote / park / cut` 判断。**
2. **若 `Rank 95` 没有被诚实推到 `P2`，下一手直接切 `Rank 96` 的 source intake + guards，不要回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 17:36 UTC（bot2 desk review）` 补充；
  - 正式冻结 **`Rank 96 / AdvancedMA retest-count admission layer`** 作为新的 fresh repo backlog；
  - 把 active Scout 顺序改写为 `Rank 95 > Rank 96 > 旧 P1 evidence_pool > Rank 92/94 park > P3 continuity > tiny-live plumbing`；
  - 把 `Next 3 bot3 runs` 收紧为：`Run 2 = Rank 95 time-stability`，`Run 3 = Rank 95 不升格就切 Rank 96 intake`。
- **本轮不改 cron。**
  - 当前 `bot2 / bot3 / narrow-paper / bot7 / bot6` 频率与分工仍一致；没有必要为了这次 fallback 收紧再改定时器。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment。

## 风险与不确定性
- `Rank 95` 当前仍只是 `mixed but honest`，并不是隐性 `P2`；若时间稳定性不过关，就应直接切线，而不是继续奖励更多解释。
- `Rank 96` 目前还是 digest 级线索，不是已完成 queue-facing intake；这次把它排到第二位是**排班提升**，不是策略升格。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
