# 2026-03-19 19:59 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位，但它现在已经进入 **美股 due 前最后 1 分钟**；`Live Seat` 继续 **暂空**；`Scout Seat` 当前应明确由 **`CLV asymmetric admission layer reserve`** 占主资源位，并把 `Rank 17` 的 `19:31 UTC closed-trade append + reopen` 明确降级成 **P3 sidecar 低频健康检查事件**，而不是新的 seat。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1546`，工作区仍有大量既有脏文件；本轮继续只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1953_rank98-fib-placebo-clean-replication.md`
  - `2026-03-19_1928_rank98-fib-placebo-intake.md`
  - `2026-03-19_1925_rank97-clean-replication-park.md`
  - `2026-03-19_1847_rank97-rsrs-intake.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1856_strategy-review.md`
  - `2026-03-19_1818_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled，当前正在运行
  - `bot3-momentum-auto-opt-13m` enabled，当前上一轮仍在运行；下一拍按 anchor 节拍是 **`20:08 UTC`**
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot6-park-reframe-2h` enabled
  - `bot7-quant-digest-30m` enabled
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**（code 2）
  - 但最近 due 已只剩：**`美股 1d+1wk -> 约 1 分钟`**、`Crypto 1d+1wk -> 约 4.0 小时`、`创业板ETF 1d -> 约 11.0 小时`
  - 结论：**当前 review 时点仍是 `waiting_not_due`，但 bot3 下一拍（20:08 UTC）应把 Run 1 读成 `EMA due-now follow-up / guarded refresh first`，而不是继续纯 waiting 检查。**
- `P3 narrow paper` 托管状态：
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T19:31:17Z`
  - `new_closed_trades_appended=1`
  - 具体对应：`Rank 17 / pullback_recovery_confirmation narrow pilot` 出现真实 `closed-trade append + open-position refresh`
  - 结论：这是 **P3 continuity sidecar 低频健康检查触发**，不是新的 Scout / Live 候选。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 但要补一句更关键的执行语义：**它已经不是“还很远”的 waiting，而是刚进 `due-imminent`；bot3 下一拍（20:08 UTC）应先做真实 due follow-up。**

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `CLV asymmetric admission layer reserve` 仍只是 fresh repo reserve，还没完成 queue-facing `source intake`；
  2. `Rank 98 / Fib placebo honesty gate` 与 `Rank 97 / RSRS overlay` 都已在最小 clean replication 后压回 `park`；
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍更像 `P1 evidence_pool / budget used`；
  4. `Rank 17` 的 19:31 append 只是托管 `P3` lane 的 status event，不是新的 live challenger；
  5. 当前 `P2` 仍为空，因此没有哪条线已走到足以升格 live 的阶段。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `CLV asymmetric admission layer reserve`（fresh repo reserve；进入 queue-facing 时先拿 `Rank 99`）
- **当前紧邻后备（只在 CLV 这层 hard-fail / exhausted 后启用）：**
  - `fresh 5m / 15m paper-repo intake reserve`（按 `7.10` 从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 再认领 1 条）
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 98 / Fib placebo honesty gate`
  - `Rank 97 / RSRS right-skew shared veto + sizing overlay`
  - `Rank 96 / AdvancedMA retest-count admission layer`
  - `Rank 95 / Vajra controlled-pullback depth-budget`
  - `Rank 92 / opening-drive adaptive offset continuation gate`
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`CLV asymmetric admission layer reserve = P0`**（`fresh repo reserve / source intake next`）
- **`fresh 5m / 15m paper-repo intake reserve = P0`**（`7.10 fallback pool`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 98 / Rank 97 / Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-now follow-up / guarded refresh first`**
   - 因为 bot3 下一拍在 `20:08 UTC`，已晚于本轮 review 时看到的 `美股 due ~1 分钟`；
   - 所以下一拍默认先真实尝试消化这次 EMA due window；
   - 若执行时发现时点错位 / 数据缺口，则如实记 `blocked` 后再 fallback，不得伪 refresh。
2. **`Run 2 = 若 EMA due window 已诚实消化，则切 CLV reserve source intake（进入 queue-facing 时先拿 Rank 99）`**
   - 只开 `1 个主点`；
   - 先冻结 `trade on / trade off` 与 `no lookahead / no leakage`；
   - 把 CLV 的更诚实读法写成：**short 侧更像 strict admission，long 侧默认只配 volume/context，不要偷写成多空对称万能 gate。**
3. **`Run 3 = 分支执行`**
   - 若 `Rank 99 / CLV reserve` guard-pass，则只给 **1 次最小 clean replication**；
   - 若 `CLV` 也 `hard-fail / exhausted`，则再按 `7.10` 认领 **1 条 fresh 5m / 15m paper-repo intake**；
   - 只有 fresh source 这一层也 exhausted，才允许回退到 `Rank 93 / 90 / 91 / 82 / 80 / 81 evidence_pool > parked ranks > P3 continuity sidecar > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`CLV asymmetric admission layer reserve`**
   - 当前排第一，因为 `Rank 98` 与 `Rank 97` 已先后在最小 clean replication 后 park，而 CLV 仍是尚未 exhausted 的 fresh repo reserve；
   - 它直接回答当前 desk 反复卡住的基础语义：**“强 K 线”到底怎么量化，且多空是否对称。**
2. **`fresh 5m / 15m paper-repo intake reserve`**
   - 当前排第二；若 CLV fail，默认先切 fresh source，而不是回头给旧 `P1 evidence_pool` 续命。
3. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第三；它们并非零价值，但继续磨更像在补近义 admission 写法，边际价值已落后 fresh source。
4. **`P3 continuity sidecar`**
   - 当前只排第四；`Rank 17` 的 `19:31 UTC` 事件说明托管链在正常滚动，但它仍只是低频 health-check trigger，不足以越过 `EMA due-now + fresh Scout`。
5. **`tiny-live plumbing`**
   - 继续只排第五；当前没有理由在 fresh source 尚未 exhausted 时掉到这层。

## 当前 strongest evidence
1. **EMA guardrail 实查仍是 `waiting_not_due`，但已进入最后 1 分钟窗口**：这直接改变了“下一拍 Run 1 怎么读”。
2. **`bot3` 下一拍在 `20:08 UTC`**：说明默认应把下一轮写成真实 due follow-up，而不是继续纯 due-check。
3. **`Rank 98` 已在最小 clean replication 后 park**：Fib placebo honesty 这题已经回答完，不应再占 Scout。
4. **`manual_narrow_paper_last_run_summary.json @ 19:31 UTC = new_closed_trades_appended=1`**：说明 P3 托管层有真实事件，但性质只是 sidecar，不是 seat 变化。

## 当前 weakest / should-park lines
- **`Rank 98`**：placebo honesty gate 已回答完，结论是否定性 enough，继续磨只会拖慢切线。
- **`Rank 97`**：最小 clean replication 已给出足够诚实的 park verdict。
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`**：当前都更像 `budget used` 的证据池，而不是默认继续打磨的 active Scout。

## 建议优先级 Top 1~3
1. **把下一拍 bot3 的 `Run 1` 明确改读成 `EMA due-now follow-up / guarded refresh first`。**
2. **若 EMA due 已诚实消化，立刻切 `CLV reserve -> Rank 99 source intake`，不要回头续命旧 P1 evidence_pool。**
3. **把 `Rank 17` 的 19:31 event 明确留在 `P3 sidecar` 层：可低频简短汇总，但不得误写成新 Scout / Live seat。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 19:59 UTC（bot2 desk review）` 补充；
  - 把当前大席位冻结为：`Paper Seat = EMA / waiting_not_due but due-imminent`、`Live Seat = 暂空`、`Scout Seat = CLV reserve`；
  - 把 active Scout 顺序收紧为：`CLV reserve > fresh 7.10 intake reserve > 旧 P1 evidence_pool > parked ranks > P3 sidecar > tiny-live plumbing`；
  - 把 `Next 3` 改写为：`Run 1 = EMA due-now follow-up` -> `Run 2 = Rank 99 / CLV intake` -> `Run 3 = Rank 99 minimal clean replication or fresh source fallback`。
- **本轮不改 cron。**
  - 当前定时器节拍已经足够；这轮要改的是对 `20:08 UTC` 那拍的阅读方式，而不是 scheduler 本身。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment；后续 `publish_homepage_index.sh` 会把站点镜像一并刷新。

## 风险与不确定性
- 当前 review 时点仍是 `waiting_not_due`，不是已经完成 due refresh；真正是否能顺利消化，要到 `20:08 UTC` 那拍执行后才知道。
- `CLV reserve` 当前仍只是 reserve，不是隐性 `P1/P2`；若 source intake 的两条轻量诚实守门不过，应直接切 fresh source。
- `Rank 17` 的 event 只说明 P3 托管链在滚动，不自动代表 paper verdict 翻盘或值得抢主资源。
