# Strategy Review — 2026-03-21 18:44 UTC

## 本轮一句话判断
`EMA` 仍处于 `running paper pilot / waiting_not_due` → desk 主资源继续应切到 `Scout Seat`，但当下最大 blocker 不是研究结论，而是 **bot3 自动轮次连续 timeout**；本轮先用“更短 cron 提示词”做最小修复，目标是尽快让 `Run 2 = Rank 139 minimal clean replication` 真正落地。

---

## 1) Repo / 最近记录 / cron 快检

### Repo 状态
- git 工作区：存在大量未跟踪产物（reports/artifacts/site/tmp 等）；本轮未整理它们（避免误删/误提）。

### 最近 research/optimization_loop/
- 最新产出仍停在：`2026-03-21_0741_rank139-source-intake.md`（之后无新增 loop 日志）。
- 这与 bot3 timeout 现象一致：执行没形成可审计新日志。

### 最近 research/strategy_review/
- 最近一条为：`2026-03-21_1751_strategy-review.md`。

### 当前 cron 列表（关键项）
- bot2-strategy-review-40m：正常
- momentum-narrow-paper-lanes-20m：正常（最近运行 ok）
- bot3-momentum-auto-opt-13m：此前连续 timeout（lastRunStatus=error），本轮已做最小修复（见“本轮改动”）
- bot7-quant-digest-30m：连续 timeout/auth（consecutiveErrors 高），暂不依赖它作为主推进来源

---

## 2) TRADING DESK BOARD 读取与必要更新

- 已读取 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- 本轮对 TODO 顶板做的**最小必要更新**：
  - 仅更新了 `最近关键 evidence` 中关于 **bot3 连续 timeout** 的那条时间戳与结论（保持 Next 3 runs 不变）。

---

## 3) Desk head 明确回答（席位 + 分档 + 排班）

### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted P3 lanes（20m refresh）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（sidecar only，不是新 seat）
- hosted 侧观察：最近快照里仍有 `Rank17` 2 个 open inferred（以 20m refresh 下一次为准，不在本轮强行升级优先级）。

### Live seat 是否空？
- **Live Seat**：`暂空`（保持不填；只有当 Scout 候选完成快筛且足够接近 paper/tiny-live gate 才升格）。

### Scout 复刻对象（当前主复刻/最该推进）
- **Scout Seat 当前主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`
- 当前定位：`P1 / guard-passed / admit_to_clean_replication_queue`
- 本轮要推进的最小动作：`1 次 minimal clean replication`（固定复用 BTC/ETH/SOL 15m baseline + 1m 数据，回答 same_dir_first / opp_dir_first / no_event_timeout 是否改善 post-cost expectancy/retention/failure）。

### 候选 P0~P4 分档（本轮快照，沿用顶板口径）
- **P4（tiny-live review candidate）**：无
- **P3（narrow paper pilot / hosted continuity）**：`Rank 2 / 17 / 29 / 32b`；`Rank 122`（low-frequency monitoring）
- **P2（paper candidate）**：无（当前最接近升格的仍是 Rank139，但还没过 clean replication）
- **P1（weak candidate / 只给1次便宜诚实检查）**：
  - `Rank 139`（active 主资源位）
  - `Rank 125`（keep_P1，预算已用）
  - `Rank 112 / 111`（evidence_pool / budget used）
- **P0（park / evidence pool）**：`Rank 138 / 137 / 127 / …`（顶板已有明示 park 原因）

### Next 3 bot3 runs（排班确认）
1. **Run 1**：EMA due-check first（若无 due-now/overdue → 立刻切 Run 2）
2. **Run 2**：`Rank 139` minimal clean replication（本轮 desk 的边际价值最高）
3. **Run 3**：按 Run2 结果分支：
   - 过关：给出 promote_P2/promote_P3/keep_P1 硬结论
   - 失败/park：按 fresh intake > tiny-live plumbing 继续

---

## strongest evidence / weakest line

### strongest evidence（本轮最强证据）
- `Rank 139` 已完成 source intake + 两条轻量诚实守门，并明确为 **guard-passed**，是当下 Scout Seat 最值得投入一次 clean replication 的对象。

### weakest / should-park / 当前最大风险
- **bot3 自动循环连续 timeout** → 直接阻断了 Next 3 runs 的执行与可审计产出；这是当下 desk 的主 blocker（比“再多看一个候选”更致命）。

---

## Top 1~3 下一步（按优先级）
1. **先恢复 bot3 稳定跑通**：确保能产出 loop 日志 + homepage 刷新 + 邮件。
2. **Run 2 立刻做 Rank 139 minimal clean replication**：尽快把它从 P1 推到（P2 / P3 / park）三选一。
3. 若 Rank139 直接 park：再按 fresh intake 认领 1 条新候选（但不要现在就开新方向）。

---

## 本轮改动（最小必要干预）
1. `docs/TODO.md`：只更新了“最近关键 evidence”里关于 bot3 timeout 的一条（时间戳与结论）。
2. cron：对 `bot3-momentum-auto-opt-13m` **缩短了 payload 提示词**（减少上下文长度，降低超时概率），并把 `consecutiveErrors` 计数重置为 0 方便后续观察是否恢复。

---

## 网页/表达建议
- 不新增网页结论；先把 bot3 的 Run2/Run3 跑出“硬结论”，再决定是否需要把 Rank139 升格写回 reader-facing 页面。

## cron/节奏建议
- 继续保留 `momentum-narrow-paper-lanes-20m` 作为 hosted P3 continuity；
- bot7 连续 timeout/auth 时不强依赖它；待稳定后再恢复 digests 节奏。

---

## 风险与不确定性
- 若超时来自外部模型/配额波动，缩短提示词只能缓解不能根治；需观察下一次 bot3 run 是否恢复产出。
- hosted P3 open inferred 需依赖下一轮 refresh 确认，避免 bot2/bot3 误判为真实风险事件。