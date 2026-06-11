# 2026-03-19 11:50 UTC bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 **EMA / running paper / waiting_not_due** 占位；`Live Seat` 继续**暂空**；`Scout Seat` 当前正式切到 **`Rank 88 / macro-event blackout + size-down risk overlay`**，它现在是唯一值得拿下一手 **minimal clean replication** 的 fresh candidate，`P2` 仍空、`P4` 仍空。

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 仍显示大量既有脏文件；本轮不混改无关文件。
- 最近 optimization logs（重点核对）：
  - `2026-03-19_1037_rank86-time-stability-park.md`
  - `2026-03-19_1102_rank87-volume-clock-intake.md`
  - `2026-03-19_1126_rank87-clean-replication-park.md`
  - `2026-03-19_1149_rank88_macro_event_overlay_intake.md`
- 最近 strategy review：
  - `2026-03-19_1107_strategy-review.md`
  - `2026-03-19_1012_strategy-review.md`
  - `2026-03-19_0908_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m`、`bot3-momentum-auto-opt-13m`、`bot7-quant-digest-30m`、`momentum-narrow-paper-lanes-20m`、`bot6-park-reframe-2h` 均启用；
  - `momentum-narrow-paper-lanes-20m` 最近一次 `2026-03-19T11:48:48Z`，`new_closed_trades_appended=0`；
  - `bot6-park-reframe-2h` 最近一轮报错是 `rg: command not found`，但它不改变本轮桌面席位判断。
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 仍无 `due-now / overdue` lane；
  - 最近 due 点：`美股约 12.9h`、`Crypto 约 16.9h`、`A股约 23.9h`；
  - 结论：`Paper Seat = EMA / running paper / waiting_not_due`。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA baseline family / EMA-PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 含义：这是真 waiting，不是 desk 停摆；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 88` 当前只到 **`P1 / source intake guard-passed / minimal clean replication next`**；
  2. `Rank 87 / 86 / 85 / 84 / 83` 都已明确回到 **`P0 park / evidence_pool`**；
  3. `Rank 82 / 80 / 81` 继续只是 **`P1 evidence_pool`**；
  4. `Rank 78 / 17 / 2 / 29 / 32b` 是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active 主资源位：**
  - `Rank 88 / macro-event blackout + size-down risk overlay`
- **当前紧邻 backlog（尚未拿主资源）：**
  - `outside-close -> back-inside-close failure verdict`
  - `close-range compression asymmetry`
- **当前只留在证据池、不再默认续命：**
  - `Rank 82 / ETF lead regime gate`
  - `Rank 80 / first-30m impulse quality gate`
  - `Rank 81 / RS semivariance asymmetry gate`
  - `Rank 87 / volume-clock + CS spread interaction gate`
  - `Rank 86 / SignalPro penetration×ATR admission`
  - `Rank 85 / fresh pullback -> reclaim re-arm gate`
  - `Rank 84 / volume-price interaction admission layer`
  - `Rank 83 / Fib trend-strength admission layer`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 88 / macro-event blackout + size-down risk overlay = P1`**（`source intake / 两条轻量诚实守门已过；minimal clean replication next`）
- **`outside-close -> back-inside-close failure verdict = P0`**（`fresh digest backlog / source intake pending`）
- **`close-range compression asymmetry = P0`**（`fresh digest backlog / source intake pending`）
- **`Rank 82 / ETF lead regime gate = P1`**（`evidence_pool / 不再默认续命`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / evidence_pool`）
- **`Rank 81 / RS semivariance asymmetry gate = P1`**（`minimal clean replication 已用 / evidence_pool`）
- **`Rank 87 / 86 / 85 / 84 / 83 = P0`**（`park / evidence_pool`）
- **`Rank 78 / 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency hosted lanes`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 若脚本仍返回 `waiting_not_due`，不得伪造 refresh，也不得空转。
2. **`Run 2 = Rank 88 / macro-event blackout + size-down risk overlay minimal clean replication`**
   - 固定 `BTC/ETH/SOL 15m` 与现有三条 archetype；只比较 `baseline / blackout / size_down / hybrid`；统一 `signal 当根及之前数据 + next-bar open + no-overlap`；做完直接回答 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 若 Rank 88 clean replication 直接 hard-fail / park，则回到两条 breakout-centric fresh backlog；只有 fresh backlog 也 exhausted，才回退到 Rank 82 / 80 / 81 evidence_pool > tiny-live plumbing`**
   - `P3 continuity` 继续只算 low-frequency sidecar，不得默认抢主资源。

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 88 / macro-event blackout + size-down risk overlay`**
   - 当前排第一，因为它是 shared risk overlay，同时服务 breakout-short / Fib retest_hold / EMA-PSAR，且已完成 `source intake + honesty gate`，离改变层级判断最近。
2. **两条 breakout-centric fresh backlog**
   - 只保留第二层；在 `Rank 88` 还没出 minimal clean replication verdict 前，不应抢跑并开。
3. **`Rank 82 / 80 / 81`**
   - 继续只留 `P1 evidence_pool`；它们都已用掉便宜检查或最小 clean replication，当前再磨更像补文案而不是减 gate。
4. **`Rank 78 / 17 / 2 / 29 / 32b`**
   - 继续只算 `P3` 托管位；本轮没有新的 status-changing event，不该插队。

## 当前 strongest evidence
1. **EMA guardrail 继续明确显示 `waiting_not_due`**：本轮没有任何 `due-now / overdue` lane，说明 `Paper Seat` 继续 keep 完全诚实。
2. **`Rank 87` 已完成最小 clean replication 后如实 park**：减少了继续误分配 fast-lane 预算的风险。
3. **`Rank 88` 已完成 source intake + 两条轻量诚实守门**：当前已从 fresh queue 升到 **`P1 / minimal clean replication next`**，是当前最靠近改变层级判断的一条线。
4. **P3 托管层当前无新异常**：`manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有理由让 `Rank 78 / 17 / 2 / 29 / 32b` 抢回主资源。

## 当前 weakest / should-park lines
- **`Rank 87 / volume-clock + CS spread interaction gate`**：clean replication 改善主要来自 retention 断崖式下降，已应继续视为 **park**。
- **`Rank 86 / SignalPro penetration×ATR admission`**：时间稳定性检查后已明确 **park**。
- **`Rank 85 / fresh pullback -> reclaim re-arm gate`**：最小 clean replication 已给完，继续应视为 **park**。
- **`Rank 84 / volume-price interaction admission layer`**：clean replication 未证明 shared interaction 方案可稳定升格，继续应视为 **park**。

## TODO / web / cron 的改动或建议
- **本轮不再改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。**
  - 原因：`11:47 UTC` 的最新板面已经把 `Rank 88 = P1`、`Rank 87 = P0 park`、以及最新 `Next 3` 如实写回；当前 desk judgment 与板面一致，不需要再做重复写回。
- **本轮不改 cron。**
  - 仅记录：`bot6-park-reframe-2h` 当前有 1 次 `rg` 缺失报错，但不影响本轮 desk 排兵布阵。
- **reader-facing 落点已足够**：当前已有 `TODO 顶板 + Rank 88 source-intake 页面 + 本轮 strategy review`，无需额外扩写 closure 页。

## 风险与不确定性
- `Rank 88` 当前仍只到 `P1`，不是升格结论；下一手必须是 **1 次最小 clean replication**，而不是继续补宏观叙事页。
- 当前 repo 工作区依旧很脏；本轮继续避免混改，只做 review 记录、首页刷新与邮件。
- 若 `Rank 88` 的改善主要来自大幅砍 trade count，而不是更诚实地降低坏交易，它也应快速压回 `park`，不能因为“宏观 overlay 听起来高级”而续命。
