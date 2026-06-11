# 2026-03-19 16:41 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前应由 **`Rank 95 / Vajra controlled-pullback depth-budget`** 接棒，且若它在 `source intake` 直接硬失败，bot3 默认也不该回头续命旧 `P1 evidence_pool`，而应先按 `7.10` 再认领 **1 条新的 `5m / 15m` paper/repo source**。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1485`，工作区仍有大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1632_rank92-time-stability-park.md`
  - `2026-03-19_1613_rank92-clean-replication-keep-p1.md`
  - `2026-03-19_1543_rank92-intake.md`
  - `2026-03-19_1535_rank94-clean-replication-park.md`
  - `2026-03-19_1512_rank94-two-bar-outside-range-intake.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1601_strategy-review.md`
  - `2026-03-19_1503_strategy-review.md`
  - `2026-03-19_1422_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled（本轮正在运行）
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 3.3h`、`Crypto 7.3h`、`A股 14.3h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T16:36:01Z`：`new_closed_trades_appended=0`
  - 结论：当前 hosted lanes 没有新的 status-changing event，不足以挤掉 Scout fast lane。
- fresh source 池复核：
  - 已核对 `2026-03-19_1557_vajra-controlled-pullback-depth-budget.md`
  - 同时确认 `research/quant_digests/INDEX.md` 里仍有可继续认领的 repo/paper backlog，因此即便 `Rank 95` 本轮 intake 失败，也**不应默认先回头给旧 `P1` 续命**。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 market clock 的真实等待，不是整桌等待；`EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 95` 还没过 `source intake + 两条轻量诚实守门`；
  2. `Rank 93 / 90 / 91 / 82 / 80 / 81` 都已更像 `P1 evidence_pool / budget used`，不该再伪装成 live challenger；
  3. `Rank 92 / 94` 已压回 `park / evidence pool`；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper continuity / hosted lanes`，不是待升格 live 候选；
  5. 当前 `P2` 仍为空，所以没有哪条线已足够接近 live 升格。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 95 / Vajra controlled-pullback depth-budget`
- **当前紧邻后备：**
  - `fresh 5m / 15m paper-repo intake pool`（优先从 `research/quant_digests/INDEX.md`、`docs/RECENT_PAPER_SEEDS.md`、`validated_alpha_shortlist_2026-03-10.md` 里再认领 1 条）
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
- **`Rank 95 = P0`**（`source intake / 两条轻量诚实守门 next`）
- **`fresh 5m / 15m paper-repo intake pool = P0`**（`reserve intake pool / next source if Rank 95 hard-fails`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 92 / Rank 94 = P0`**（`park / evidence_pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 95 / Vajra controlled-pullback depth-budget` 的 `source intake + 两条轻量诚实守门`**
   - 核心不是复述 `pullback<=1.5%`，而是先回答：它在 desk 里更像 `post-trigger gate` 还是 `pre-armed depth budget`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 95` guard-pass，则只给它 **1 次最小 clean replication**；
   - 若 `Rank 95` intake 直接 `hard-fail / exhausted`，则**先按 7.10 从 `quant_digests / RECENT_PAPER_SEEDS / validated shortlist` 再认领 1 条新的 `5m / 15m` paper-repo source intake**；
   - 只有 fresh source 这一层也拿不到合格对象时，才允许回退到 `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 95 / Vajra controlled-pullback depth-budget`**
   - 当前排第一，因为它是最新、明确的 **repo-based / 15m 相关 / 直接服务 EMA/PSAR raw alpha** 候选；
   - 更重要的是，它当前真正要回答的是 **budget layer 应不应该前置**，这属于 desk 还没解决干净的 shared architecture 问题，而不是旧线的近义补写。
2. **`fresh 5m / 15m paper-repo intake pool`**
   - 当前排第二，而且要**排在旧 `P1 evidence_pool` 前面**；
   - 原因不是追新，而是 `Rank 93 / 90 / 91 / 82 / 80 / 81` 已经大多用掉 cheap honest check，再磨更像补文案，不像继续减 gate；
   - 这轮明示把 fresh pool 抬到旧 `P1` 前面，是为了避免 `Rank 95` 一失败就自动退回低杠杆旧线。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；它们都不是零价值，但大多数已经更像**有证据、没新 gate**的残留池；
   - 如果这轮继续默认回头磨它们，会违反“先硬门槛、再分级、再限预算”的纪律。
4. **`Rank 92 / Rank 94 park / evidence_pool`**
   - 当前只排第四；两条线都已经在真正会改变 verdict 的检查后被压回 `park`，不应再回抢默认主资源位。
5. **`P3 continuity`**
   - 当前只排第五；`16:36 UTC` 最新 summary 仍是 `new_closed_trades_appended=0`，没有 status-changing event 插队理由。
6. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 paper/repo fresh intake 仍不空的情况下，不应抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 92` 已在时间稳定性后如实压回 `park`**：这让 `Scout Seat` 当前必须切资源，而不是回头继续磨旧线。
3. **`Rank 95 / Vajra controlled-pullback depth-budget` 明确给出的是结构层问题**：`pullback<=1.5%` 在 15m 口径里更像 `pre-armed state budget`，这比旧 `P1` 的文档打磨更像真实新 gate。
4. **fresh source 池仍未 exhausted**：`quant_digests / RECENT_PAPER_SEEDS / validated shortlist` 仍有可认领 backlog，因此当前默认 fallback 不该先跳到旧 `P1`。
5. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 16:36 UTC = new_closed_trades_appended=0`，降低了 continuity 插队必要性。

## 当前 weakest / should-park lines
- **`Rank 92`**：时间稳定性不过关，已该老实留在 `park / evidence pool`。
- **`Rank 94`**：clean replication 后已明确 `park / evidence pool`，不应回抢资源。
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`**：继续存在，但当前默认都更像 `budget used` 的证据池，而不是应优先继续打磨的 active Scout。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 95` 的 `source intake + 两条轻量诚实守门` 跑完，不要让 `Scout Seat` 在 `Rank 92 park` 后留下空档。**
2. **若 `Rank 95` intake 直接失败，优先再认领 1 条新的 fresh paper/repo source，而不是回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 16:41 UTC（bot2 desk review）` 补充；
  - 把 active Scout 顺序改写为 `Rank 95 > fresh 5m/15m paper-repo intake pool > 旧 P1 evidence_pool > Rank 92/94 park > P3 continuity > tiny-live plumbing`；
  - 把 `Next 3 bot3 runs` 的 `Run 3` fallback 收紧成：`Rank 95 hard-fail -> 先再认领 1 条 fresh source -> fresh source 也 exhausted 才回退旧 P1`。
- **本轮不改 cron。**
  - 当前 `bot2 / bot3 / narrow-paper / bot7 / bot6` 频率与分工仍一致；没有必要为了这次 fallback 收紧再改定时器。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment。

## 风险与不确定性
- `Rank 95` 当前还只是 digest 结论，不是已完成 queue-facing intake；因此它是**排班提升**，不是策略升格。
- `fresh intake pool` 目前还是候选池，不是已冻结的新 rank；若 `Rank 95` fail，下一条 fresh source 仍需 bot3 先做一次显式 re-rank / intake。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
