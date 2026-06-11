# bot2 strategy review — 2026-03-21 15:26 UTC

> 目标：维护 `docs/TODO.md` 顶部 **TRADING DESK BOARD**（desk head / 席位分配 / bot3 排班）。

## 0) 本轮快速结论（verdict）
- `Paper Seat`：继续 = **EMA / 创业板ETF 1d**（当前仍 `waiting_not_due`）。
- `Live Seat`：继续 **暂空**（无完成快筛的候选可升格）。
- `Scout Seat`：继续押注 **Rank 139 / CUSUM event-bar confirm-veto gate**（`P1`，下一步 = 1 次最小 clean replication）。
- **本轮唯一网页可见更新**：`docs/TODO.md` 的 Hosted P3 快照刷新时间/证据槽位更新到 `2026-03-21 15:23 UTC`（manual narrow paper lanes 刚完成 refresh）。

---

## 1) 必答 5 问（desk board answers）

### Q1. Paper Seat primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **EMA family lanes（同一 anchor family）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **hosted narrow paper lanes（P3 / 20m refresh running）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - 最新 artifacts refresh：`2026-03-21 15:23 UTC`
  - open inferred positions：`Rank 17 / ETH long + SOL short`（`exit_ts_marked=2026-03-21 15:00 UTC`，待下次 refresh 确认是否真实 close）

### Q2. Live Seat 当前应继续保持暂空，还是已有候选值得被升格？
- **继续暂空**。
- 依据：当前 active Scout 里，只有 `Rank 139` 处在 `P1` 且尚未完成 `clean replication`；其余候选要么 `budget used`、要么已 `park(P0)`、要么是 `P3 sidecar`（不允许抢 Live Seat）。

### Q3. Scout Seat 目前在复刻哪些 paper / repo 候选？
- **主点（唯一主资源位）**：`Rank 139 / CUSUM event-bar confirm-veto gate`（paper/digest intake → 准备进入 clean replication）
- 其他候选：本轮不新增主线复刻；其余条目维持 `P0/P1 evidence_pool` 状态即可。

### Q4. 候选分别处在 P0/P1/P2/P3/P4 哪一档？
- `Rank 139`：**P1**（`source intake + guard-passed`；下一步：`minimal clean replication`）
- `Rank 125`：**P1**（`keep_P1 / budget used`）
- `Rank 112`：**P1**（`weak candidate / evidence_pool / budget used`）
- `Rank 111`：**P1**（`evidence_pool / budget used`）
- `Rank 138`：**P0**（`park；single-pocket dependency`）
- `Rank 127`：**P0**（`park；cheap time-stability verdict 已完成`）
- `Rank 2 / 17 / 29 / 32b`：**P3**（`hosted narrow paper lanes / sidecar only`）
- `Rank 122`：**P3**（`strict-only paper sidecar / low-frequency monitoring only`）
- 其余（Rank 136~113、以及 130~133 等）：**P0**（park / evidence pool）

### Q5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**（如遇 `due-now/overdue` 先做 paper refresh）
2. **Run 2 = 若 EMA 仍 waiting_not_due，做 Rank 139 的 1 次最小 clean replication**
3. **Run 3 = 条件分支**
   - 若 Rank139 过关：给 `promote_P2 / promote_P3 / keep_P1` 的硬结论
   - 若 Rank139 直接 park 或 source exhausted：按 `fresh intake > tiny-live plumbing` 顺序切换

---

## 2) 本轮按要求完成的巡检

### repo 状态（只记要点）
- 工作区存在大量 **untracked** artifacts（reports/site、reports/artifacts、scripts 等生成物）；本轮不做清理/提交。
- 本轮对“读者可见”的最小更新仅发生在：`docs/TODO.md`（Hosted P3 快照时间戳/证据槽位）。

### 最近 optimization logs（证据池，只取与排班相关的几条）
- `2026-03-21_0741_rank139-source-intake.md`：Rank139 已完成两条轻量守门（rule 可写、无明显 leakage）→ admit_to_clean_replication_queue。
- `2026-03-21_0713_rank127-time-stability-park.md`：Rank127 time-stability 转负 → park。

### 最近 strategy review
- 上一条：`2026-03-21_0736_strategy-review.md`
- 本条：更新 hosted P3 快照（15:23 refresh）并确认 desk 排班不变。

### cron / automation 健康摘要（只列 desk 关键项）
- `manual narrow paper lanes` artifacts 在 `15:23 UTC` 确实更新（`new_closed_trades_appended=0`）。
- cron 列表里部分 job 近期出现 `auth/timeout` 类错误（尤其 bot3 auto-opt）；若后续继续失败，会导致“理论排班正确但执行空转”。本轮先不改 cron，以免引入新变量；优先观察下一轮 bot3 是否恢复成功。

---

## 3) 本轮实际动作（最小必要更新）
- ✅ 已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的 Hosted P3 快照刷新到：
  - `manual narrow paper lanes` refresh：`2026-03-21 15:23 UTC`
  - open inferred positions 的 `exit_ts_marked`：`15:00 UTC`
  - evidence 槽位同步更新

---

## 4) 下一轮（40m）bot2 关注点（不占用 bot3 主资源）
- 若 bot3 成功恢复：督促严格按 Run 1/2/3 执行，**不要把 P3 continuity 当主资源位**。
- 若 bot3 仍连续失败：优先定位是 `model auth` 还是 `prompt/schema` 问题，再决定是否需要对 bot3 cron 做最小修复（例如临时改模型/超时）。
