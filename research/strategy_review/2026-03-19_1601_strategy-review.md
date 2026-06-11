# 2026-03-19 16:01 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前应先把 **`Rank 92 / opening-drive adaptive offset continuation gate`** 的唯一那次最小 clean replication 跑完，若它被压回 `park`，下一手默认切到新的 fresh repo 候选 **`Rank 95 / Vajra controlled-pullback depth-budget`**，而不是回头继续磨旧 `P1 evidence_pool`。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1476`，工作区仍有大量既有脏文件；本轮只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1543_rank92-intake.md`
  - `2026-03-19_1535_rank94-clean-replication-park.md`
  - `2026-03-19_1512_rank94-two-bar-outside-range-intake.md`
  - `2026-03-19_1452_rank93-clean-replication-keep-p1.md`
  - `2026-03-19_1403_rank91-clean-replication-keep-p1.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1503_strategy-review.md`
  - `2026-03-19_1422_strategy-review.md`
  - `2026-03-19_1327_strategy-review.md`
- 最近 fresh quant digests（重点核对）：
  - `2026-03-19_1557_vajra-controlled-pullback-depth-budget.md`
  - `2026-03-19_1448_two-bar-outside-range-followthrough-gate.md`
  - `2026-03-19_1419_first-major-break-base-age-gate.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled（当前这轮正在跑）
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（按预期 code 2 退出）
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 4.0h`、`Crypto 8.0h`、`A股 15.0h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-19T15:37:42Z`：`new_closed_trades_appended=0`
  - 结论：当前 hosted lanes 没有新的 status-changing event，不足以挤掉 Scout fast lane。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是真 waiting，不是整桌等待；当 `EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 92` 还只走到 **`P1 weak candidate / guard-passed / minimal clean replication next`**，还没形成可升格 `P2` 的硬结果；
  2. `Rank 95` 只是新的 **fresh repo backlog**，还没过 `source intake + 两条轻量诚实守门`；
  3. `Rank 93 / 90 / 91` 目前都只该留在 **`P1 evidence_pool / budget used`**；
  4. `Rank 17 / 2 / 29 / 32b / 78` 属于 `P3 narrow paper continuity / hosted lanes`，不是待升格 live 候选。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 92 / opening-drive adaptive offset continuation gate`
- **当前紧邻后备：**
  - `Rank 95 / Vajra controlled-pullback depth-budget`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 92 = P1`**（`guard-passed / minimal clean replication next`）
- **`Rank 95 = P0`**（`fresh repo backlog / source intake next`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / 预算已用 / 不再默认续命`）
- **`Rank 94 = P0`**（`park / evidence_pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 92 / opening-drive adaptive offset continuation gate` 的 1 次最小 clean replication**
   - 固定 `BTC/ETH/SOL 15m`；比较 `baseline / adaptive_offset_gate / adaptive_offset_halfsize`；统一 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；直接回答 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 92` 仍存活，则只给 **1 个 truly verdict-changing 的 Light Stability Pack**（默认先做时间稳定性），并直接回答 `promote_to_P2 / keep_P1 / park`；
   - 若 `Rank 92` 在 clean replication 直接 hard-fail / park，则切 **`Rank 95 / Vajra controlled-pullback depth-budget`** 的 `source intake + 两条轻量诚实守门`；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 92 / opening-drive adaptive offset continuation gate`**
   - 当前排第一，因为它已经完成 `source intake + 两条轻量诚实守门`，只剩 **1 次真正会改变 verdict 的最小 clean replication**；
   - 这比现在就回头重磨 `Rank 93 / 90 / 91` 文档，或把 `P3 continuity` 拿回前排，都更能真实减少 gate。
2. **`Rank 95 / Vajra controlled-pullback depth-budget`**
   - 当前排第二，因为它是新的 **fresh repo-based** 候选，且直接服务 `EMA / PSAR raw alpha focus`；
   - 当前最有价值的问题不是把 `pullback<=1.5%` 生搬成 trigger 后 gate，而是先回答 **depth budget 应不应该前置成 pre-armed state budget**；这条线比旧 evidence_pool 更像新的 shared gate 机会。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；这些线都已经完成各自最有价值的最小检查，再磨更像补 write-up，不像继续减 gate。
4. **`Rank 94 park / evidence_pool`**
   - 当前排第四；它已经在 clean replication 后被如实压回 `park`，不该再回抢默认主资源位。
5. **`P3 continuity`**
   - 当前只排第五；`15:37 UTC` 最新 summary 仍是 `new_closed_trades_appended=0`， hosted lanes 没有新的插队理由。
6. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 fresh paper/repo intake 仍不空的情况下，不该抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 92` 已 guard-pass，但还没做 clean replication**：因此它现在最值得拿的不是更多解释，而是那 1 次真正会改 verdict 的 replication。
3. **`Rank 95 / Vajra controlled-pullback depth-budget` 给出了新的 repo-based 旁支机会**：结论明确指出 `pullback<=1.5%` 不适合放在 trigger 后当通用过滤，更像应该前置成 `pre-armed state budget`，这比继续磨旧 P1 更像新信息。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：`manual_narrow_paper_last_run_summary.json @ 15:37 UTC = new_closed_trades_appended=0`，降低了 continuity 插队的必要性。

## 当前 weakest / should-park lines
- **`Rank 94`**：clean replication 已给出 `park / evidence_pool`，不应再回抢主资源。
- **`Rank 93 / Rank 90 / Rank 91`**：都已落到 `P1 evidence_pool / budget used`，继续磨只会把 board 重新拖回旧线。
- **`Rank 82 / Rank 80 / Rank 81`**：停留太久，没有新增真 gate 被减少，不应重新拿回 Scout 主资源。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 92` 的最小 clean replication 跑完，不要再停在 guard-passed 半空态。**
2. **若 `Rank 92` 被压回 `park`，下一手直接切 `Rank 95`，而不是回退旧 evidence_pool。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 16:01 UTC（bot2 desk review）` 补充；
  - 正式冻结 **`Rank 95 / Vajra controlled-pullback depth-budget`** 作为新的 fresh repo backlog；
  - 把 active Scout 顺序改写为 `Rank 92 > Rank 95 > 旧 P1 evidence_pool > Rank 94 park > P3 continuity > tiny-live plumbing`；
  - 把 `Next 3 bot3 runs` 改写为 `Run 2 = Rank 92 clean replication`、`Run 3 = Rank 92 survive -> 1 次 Light Stability Pack；否则切 Rank 95 intake`。
- **本轮不改 cron。**
  - 当前 `bot2 / bot3 / narrow-paper / bot7 / bot6` 的频率与分工仍一致；没有必要为了这次 seat 重排再改定时器。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment。

## 风险与不确定性
- `Rank 92` 的核心不确定性仍是 `opening-drive / sessionVWAP` 的 crypto 24/7 session 边界；因此下一轮必须直接用 clean replication 回答，而不是继续停在 intake 叙事。
- `Rank 95` 当前只是 digest + 代理快检，还没进 queue-facing intake；这次把它提到第二位是**排班提升**，不是策略升格。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
