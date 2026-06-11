# 2026-03-19 18:56 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续 **暂空**；`Scout Seat` 当前应明确由 **`Rank 97 / RSRS right-skew shared veto + sizing overlay`** 占主资源位，并把后备 fresh source 顺序收紧为 **`Fib placebo-zone honesty gate > CLV asymmetric admission layer reserve`**。当前没有任何候选已经完成到足以抢占 `Live Seat` 的阶段。

## 本轮先检查了什么
- repo 状态：`git status --short | wc -l = 1530`，工作区仍有大量既有脏文件；本轮仍只做 `TRADING DESK BOARD` 最小必要更新、strategy review 记录、首页刷新与邮件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1847_rank97-rsrs-intake.md`
  - `2026-03-19_1825_rank96-clean-replication-park.md`
  - `2026-03-19_1808_rank96-source-intake.md`
  - `2026-03-19_1746_rank95-time-stability-park.md`
- 最近 strategy reviews（重点核对）：
  - `2026-03-19_1818_strategy-review.md`
  - `2026-03-19_1736_strategy-review.md`
- 当前 cron（重点核对）：
  - `bot2-strategy-review-40m` enabled（本轮正在运行）
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot6-park-reframe-2h` enabled
  - `bot7-quant-digest-30m` enabled，但最近一轮报错为 `rg: command not found`；当前属于**非阻塞维护项**，不足以挤掉 Scout 主线
- `Paper Seat` guardrail：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 1.0h`、`Crypto 5.0h`、`A股 12.0h`
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`
- `P3 narrow paper` 托管状态：
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `new_closed_trades_appended=0`
  - 结论：当前 hosted lanes 没有新的 status-changing event，不足以挤掉 Scout fast lane

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是 market clock 的真实等待，不是整桌等待；`EMA` 继续 `waiting_not_due` 时，bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 97` 目前只完成了 `source intake + 两条轻量诚实守门`，还没过最小 clean replication；
  2. `Fib placebo-zone honesty gate` 与 `CLV asymmetric admission layer reserve` 都仍是 fresh reserve，不是 queue-facing 已验证候选；
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍更像 `P1 evidence_pool / budget used`，继续磨它们不等于存在 live challenger；
  4. `Rank 96 / 95 / 92 / 94` 已被压回 `park / evidence pool`；
  5. `Rank 78 / 17 / 2 / 29 / 32b` 属于 `P3 narrow paper continuity / hosted lanes`，不是新的 live 升格候选。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位：**
  - `Rank 97 / RSRS right-skew shared veto + sizing overlay`
- **当前紧邻后备（只在 Rank 97 clean replication 直接 hard-fail 后启用）：**
  - `Fib placebo-zone honesty gate`
  - `CLV asymmetric admission layer reserve`
- **当前只留证据池、不再默认续命：**
  - `Rank 93 / first-major-break base-age gate`
  - `Rank 90 / close-range compression asymmetry`
  - `Rank 91 / same-level consecutive sweep count level-memory gate`
  - `Rank 82 / Rank 80 / Rank 81`
- **当前已 park、不得回抢主资源：**
  - `Rank 96 / AdvancedMA retest-count admission layer`
  - `Rank 95 / Vajra controlled-pullback depth-budget`
  - `Rank 92 / opening-drive adaptive offset continuation gate`
  - `Rank 94 / two-bar outside-range follow-through gate`
- **当前只算托管位、不得误写成新 seat：**
  - `Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 97 = P1`**（`guard-passed / minimal clean replication next`）
- **`Fib placebo-zone honesty gate = P0`**（`fresh paper honesty-gate intake reserve`）
- **`CLV asymmetric admission layer reserve = P0`**（`fresh repo reserve / not yet queue-facing`）
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 = P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 96 / Rank 95 / Rank 92 / Rank 94 = P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b = P3`**（`narrow paper continuity / hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得空转，也不得伪造 refresh。
2. **`Run 2 = Rank 97 / RSRS right-skew shared veto + sizing overlay` 的 1 次最小 clean replication**
   - 固定 `BTC/ETH/SOL | 120d | 15m` 本地 cache；
   - 只比较 `no_overlay / hard_veto(q30-q70) / half_size_overlay / tiered_sizing_overlay`；
   - 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`；
   - 直接回答 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 分支执行`**
   - 若 `Rank 97` clean replication 仍存活，则只给 **1 个 truly verdict-changing 的 `Light Stability Pack`**（默认先做时间稳定性），并直接回答 `promote_to_P2 / keep_P1 / park`；
   - 若 `Rank 97` clean replication 直接 `hard-fail / park`，则**先切 `Fib placebo-zone honesty gate` 的 source intake**；
   - 只有 `Fib placebo` 这一层也 `hard-fail / exhausted`，才轮到 `CLV asymmetric admission layer reserve`；
   - 再之后才允许回退到 `Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 96 / Rank 95 / Rank 92 / Rank 94 park > P3 continuity > tiny-live plumbing`。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 97 / RSRS right-skew shared veto + sizing overlay`**
   - 当前排第一，因为它已经完成 `source intake + guards`，离下一次真实升降级判断只差 **1 次最小 clean replication**；
   - 它补的是当前三条主线共同缺的一个执行问题：**支撑阻力强度应不应该只当 veto / sizing overlay，而不是硬写成二元入场键**；
   - 这比继续磨旧 `P1 evidence_pool` 更可能改变当前 desk judgment。
2. **`Fib placebo-zone honesty gate`**
   - 当前排第二，因为它不是泛研究，而是对 `Fib confirmation / retest_hold` 的**根问题 honesty gate**；
   - 如果它成立，能直接把 Fib 线从“神位”降级成普通几何坐标系，属于高边际价值的 status-changing 检查；
   - 它比 `CLV reserve` 更该排前，是因为当前 desk 还在收 Fib 这条线，而 placebo check 更可能减少自欺。
3. **`CLV asymmetric admission layer reserve`**
   - 当前排第三；它有现成 repo 规则和本地 proxy，方向也贴 breakout-short / Fib / EMA-PSAR 三条主线；
   - 但它已经有一轮 digest 级 proxy，且当前更像备用 fresh repo，不应先于 `Rank 97` 或 `Fib placebo` 抢主资源。
4. **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool`**
   - 当前只排第四；这些线不是零价值，但大多已接近“继续磨只是在补近义写法”的状态；
   - 若默认回头续命，会违反当前 Scout fast-lane 的纪律。
5. **`Rank 96 / Rank 95 / Rank 92 / Rank 94 park / evidence_pool`**
   - 当前只排第五；都已经在真正会改变 verdict 的检查后被压回 `park`，不应回抢默认主资源位。
6. **`P3 continuity`**
   - 当前只排第六；本轮 `new_closed_trades_appended=0`，没有新的 status-changing event。
7. **`tiny-live plumbing`**
   - 继续只作更后层 fallback；在 paper/repo fresh intake 仍不空的情况下，不应抢前排。

## 当前 strongest evidence
1. **EMA guardrail 再次实查仍是 `waiting_not_due`**：当前没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 97` 已完成 `source intake + 两条轻量诚实守门`**：它当前不是模糊 backlog，而是离 clean replication 只差一步的 active Scout。
3. **`Rank 96` 已在最小 clean replication 后被如实压回 park**：说明当前 desk 没有奖励“几乎打平”的近义续命。
4. **`P3` hosted lanes 本轮无新增 closeout 事件**：降低了 continuity 插队必要性。
5. **`Fib placebo` 与 `CLV reserve` 都来自 paper/repo based 5m/15m 方向**：因此即便 `Rank 97` fail，Scout 也仍有合规 fresh intake，不需要滑回泛维护。

## 当前 weakest / should-park lines
- **`Rank 96`**：最小 clean replication 后没有把 `post-cost return / cross-asset consistency / fail-rate` 一起改善到足以继续占位。
- **`Rank 95`**：时间稳定性不过关，已应老实留在 `park / evidence pool`。
- **`Rank 92 / Rank 94`**：都已在更诚实的检查后给出 `park` verdict，不应回抢资源。
- **`Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81`**：继续存在，但当前默认都更像 `budget used` 的证据池，而不是应优先继续打磨的 active Scout。

## 建议优先级 Top 1~3
1. **立刻把 `Rank 97` 的最小 clean replication 跑完，并在这一手之后强制做 `promote / keep / park` 判断。**
2. **若 `Rank 97` 不能被诚实推到 `P2`，下一手先切 `Fib placebo-zone honesty gate`，再看 `CLV reserve`，不要回头续命旧 `P1 evidence_pool`。**
3. **继续保持 `Live Seat = 暂空`，并把 `P3 continuity` 严格留在 hosted / low-frequency 层。**

## TODO / roadmap / web / cron 的改动或建议
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`（最小必要更新）**：
  - 新增 `2026-03-19 18:56 UTC（bot2 desk review）` 补充；
  - 正式把当前 seat judgment 写死为：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat = Rank 97`；
  - 把 active Scout 顺序收紧为 `Rank 97 > Fib placebo > CLV reserve > 旧 P1 evidence_pool > 已 park ranks > P3 continuity > tiny-live plumbing`；
  - 把 `Run 3` fallback 明确写成：`Rank 97 hard-fail -> Fib placebo intake -> CLV reserve -> 旧 evidence pool`。
- **本轮不改 cron。**
  - 尽管 `bot7` 最近一轮有 `rg` 缺失报错，但当前 Scout 主线并未 blocked；按 desk 顺序还不该让 bot3转去做这类维护。
- **reader-facing 落点已满足**：`TODO 顶板` 已同步本轮 judgment。

## 风险与不确定性
- `Rank 97` 当前仍只是 `guard-passed / minimal clean replication next`，不是隐性 `P2`；若 clean replication 不诚实，就应直接切线。
- `Fib placebo` 当前还是 fresh paper honesty-gate，不是已经排到 clean replication 队列里的正式 rank；若进入 queue-facing 层，仍需按 desk 规则先拿明确顺序 rank。
- `CLV reserve` 当前是备用 repo source，不宜因已有 proxy 就被误读成“已通过 intake”。
- repo 工作区继续很脏；本轮仍避免混改，只做顶板、review、首页与邮件这条最小链路。
