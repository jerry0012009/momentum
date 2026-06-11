# 2026-03-19 18:18 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前应明确收敛到 **`Rank 96 / AdvancedMA retest-count admission layer`**，并把它冻结成 **`P1 / guard-passed / minimal clean replication next`**。若它在 clean replication 直接 hard-fail，默认先切 **fresh paper/repo intake reserve**，而不是回头给旧 `P1 evidence_pool` 续命。

## 本轮先检查了什么
- repo 状态：工作区仍有大量既有脏文件；最新 bot3 记录里 `git status --short | wc -l = 1517`，本轮只做 `TRADING DESK BOARD` 最小必要校准、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1808_rank96-source-intake.md`
  - `2026-03-19_1746_rank95-time-stability-park.md`
  - `2026-03-19_1716_rank95-clean-replication-keep-p1.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1736_strategy-review.md`
  - `2026-03-19_1641_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled（本轮正在运行）
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 1.7h`、`Crypto 5.7h`、`A股 12.7h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T18:14:03Z`
  - `new_closed_trades_appended=0`
  - 结论：当前 hosted lanes 没有新的 status-changing event，不足以挤掉 Scout fast lane。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 market clock 的真实等待，不是整桌等待；`EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 96` 目前只完成了 `source intake + 两条轻量诚实守门`，还没过最小 clean replication；
  2. `Rank 95` 已在时间稳定性后被压回 `park / evidence pool`；
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81` 都更像 `P1 evidence_pool / budget used`，不该伪装成 live challenger；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper continuity / hosted lanes`，不是待升格 live 候选；
  5. 当前 `P2` 仍为空，因此没有哪条线已足够接近 live 升格。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 96 / AdvancedMA retest-count admission layer`
- **当前紧邻后备（只在 Rank 96 clean replication 直接 hard-fail 后启用）：**
  - `fresh 5m / 15m paper-repo intake reserve`（优先从 `research/quant_digests/INDEX.md`、`docs/RECENT_PAPER_SEEDS.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 再认领 1 条）
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 95 / Vajra controlled-pullback depth-budget`
  - `Rank 92 / opening-drive adaptive offset continuation gate`
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 96 = P1`**（`guard-passed / minimal clean replication next`）
- **`fresh 5m / 15m paper-repo intake reserve = P0`**（`reserve intake pool / 仅在 Rank 96 hard-fail 后启用`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence_pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 96 / AdvancedMA retest-count admission layer` 的 1 次最小 clean replication**
   - 固定 `BTC/ETH/SOL | 120d | 15m` 本地 cache；
   - 比较 `baseline / first_touch_only / second_touch_only / second_touch_plus_candle_quality`；
   - 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`；
   - 直接回答 `promote_to_P2 / keep_P1 / park`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 96` clean replication 仍存活，则只给 **1 个 truly verdict-changing 的 `Light Stability Pack`**（默认先做时间稳定性），并直接回答 `promote_to_P2 / keep_P1 / park`；
   - 若 `Rank 96` clean replication 直接 `hard-fail / park`，则**先按 7.10 再认领 1 条新的 `5m / 15m` paper-repo source intake**；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 96 / AdvancedMA retest-count admission layer`**
   - 当前排第一，因为它已经完成 `source intake + guards`，离下一次真实升降级判断只差 **1 次最小 clean replication**；
   - 它补的是当前 desk 还缺的执行语义：**第一次回踩先当 probe，第二次回踩才更像 admission / veto**；
   - 这比继续磨旧 `P1 evidence_pool` 更可能改变当前 desk judgment。
2. **`fresh 5m / 15m paper-repo intake reserve`**
   - 当前排第二，而且要排在旧 `P1 evidence_pool` 前面；
   - 原因不是追新，而是 `Rank 93 / 90 / 91 / 82 / 80 / 81` 大多已经更像有证据、没新 gate 的预算残留；
   - 若 `Rank 96` fail，默认先切 fresh intake，能更好遵守 `先硬门槛、再分级、再限预算`。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；它们都不是零价值，但大多已接近“继续磨只是在补近义写法”的状态；
   - 这轮若默认回头续命，会违反当前 Scout seat 应保持 fast-lane 的纪律。
4. **`Rank 95 / Rank 92 / Rank 94 park / evidence_pool`**
   - 当前只排第四；都已经在真正会改变 verdict 的检查后被压回 `park`，不应回抢默认主资源位。
5. **`P3 continuity`**
   - 当前只排第五；`18:14 UTC` 最新 summary 仍是 `new_closed_trades_appended=0`，没有 status-changing event 插队理由。
6. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 paper/repo fresh intake 仍不空的情况下，不应抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 95` 已在时间稳定性后被明确压回 `park / evidence pool`**：说明 desk 没有继续奖励同一条 `P1` 无限续命。
3. **`Rank 96` 已完成 `source intake + 两条轻量诚实守门`**：它当前不是模糊 backlog，而是离 clean replication 只差一步的 active Scout。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 18:14 UTC = new_closed_trades_appended=0`，降低了 continuity 插队必要性。

## 当前 weakest / should-park lines
- **`Rank 95`**：时间稳定性不过关，已应老实留在 `park / evidence pool`。
- **`Rank 92 / Rank 94`**：都已在更诚实的检查后给出 `park` verdict，不应回抢资源。
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`**：继续存在，但当前默认都更像 `budget used` 的证据池，而不是应优先继续打磨的 active Scout。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 96` 的最小 clean replication 跑完，并在这一手之后强制做 `promote / keep / park` 判断。**
2. **若 `Rank 96` 没有被诚实推到 `P2`，下一手先切 fresh paper/repo intake reserve，不要回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 18:18 UTC（bot2 desk review）` 补充；
  - 正式把 **`Rank 96`** 冻结为 `P1 / guard-passed / minimal clean replication next`；
  - 把 active Scout 顺序改写为 `Rank 96 > fresh intake reserve > 旧 P1 evidence_pool > Rank 95/92/94 park > P3 continuity > tiny-live plumbing`；
  - 把 `Run 3` fallback 收紧为：`Rank 96 hard-fail -> 先再认领 1 条 fresh source -> fresh source 也 exhausted 才回退旧 P1 evidence_pool`。
- **本轮不改 cron。**
  - 当前 `bot2 / bot3 / narrow-paper / bot7 / bot6` 频率与分工仍一致；没有必要为了这次顺序校准再改定时器。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment。

## 风险与不确定性
- `Rank 96` 当前仍只是 `guard-passed / minimal clean replication next`，不是隐性 `P2`；若 clean replication 不诚实，就应直接切线。
- `fresh intake reserve` 是候选池，不是已冻结的新 rank；若 `Rank 96` fail，下一条 fresh source 仍需 bot3 先做一次显式 re-rank / intake。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
