# bot2 strategy review — 2026-03-21 16:41 UTC

> 目标：维护 `docs/TODO.md` 顶部 **TRADING DESK BOARD**（desk head / 席位分配 / bot3 排班）。

## 0) 本轮一句话判断（verdict）
- **Desk judgement 不变**：`Paper Seat = EMA(创业板ETF 1d) waiting_not_due`，`Live Seat = 暂空`，`Scout Seat 主资源 = Rank 139`；但 **bot3 连续超时导致 desk 执行空转**，本轮已做 **最小必要干预：缩短 bot2/bot3 cron prompt + thinking=low**，以恢复按板执行。

---

## 1) 必答 5 问（desk board answers）

### Q1. Paper Seat primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **EMA family lanes（仍在同一 anchor family 下托管/观察）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **hosted narrow paper lanes（P3 / 20m refresh running）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - 最近快照仍以 `2026-03-21 15:23 UTC refresh` 为最新（见 TODO 顶部 Hosted P3 快照）。

### Q2. Live Seat 当前应继续保持暂空，还是已有候选值得被升格？
- **继续暂空**。
- 理由：当前 active Scout 主候选 `Rank 139` 仍在 **P1（未完成 clean replication）**；其余条目要么 `budget used / evidence_pool`，要么已 `park(P0)`，或为 `P3 hosted lanes`（不允许抢 Live Seat）。

### Q3. Scout Seat 目前在复刻哪些 paper / repo 候选？
- **唯一主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`（paper/digest intake 已完成；下一步 = 1 次最小 clean replication）。
- 其余 Scout：维持 `P0/P1 evidence_pool`，不在本轮新增第二主点。

### Q4. 候选分别处在 P0/P1/P2/P3/P4 哪一档？（含阶段）
- `Rank 139`：**P1**（`source intake + trade on/off 可写 + no leakage guard-passed` → `clean replication next`）
- `Rank 125`：**P1**（`keep_P1 / budget used`）
- `Rank 112`：**P1**（`weak candidate / evidence_pool / budget used`）
- `Rank 111`：**P1**（`evidence_pool / budget used`）
- `Rank 138`：**P0**（`park；single-pocket dependency`）
- `Rank 127`：**P0**（`park；cheap time-stability verdict`）
- `Rank 2 / 17 / 29 / 32b`：**P3**（`hosted narrow paper lanes / 20m refresh / sidecar only`）
- `Rank 122`：**P3**（`strict-only paper sidecar / low-frequency monitoring only`）
- 其余大量 ranks：**P0**（park / evidence pool）

### Q5. 接下来 3 个 bot3 runs 应该怎么排？
- **不改（保持 TODO 顶部的 authoritative 排班）**：
  1) Run 1 = EMA due-check first（如遇 `due-now/overdue` 先做 paper refresh）
  2) Run 2 = 若 EMA 仍 `waiting_not_due`，做 `Rank 139` 的 `1 次最小 clean replication`
  3) Run 3 = 条件分支（Rank139 过关就硬结论升格；否则 `fresh intake > tiny-live plumbing`）

---

## 2) 本轮巡检：repo / logs / strategy review / cron

### repo 状态（只记对 desk 有影响的点）
- 工作区 **长期脏**（大量生成物与 untracked artifacts）；本轮不尝试清理/提交，避免踩并发。

### 最近 optimization logs（与排班直接相关）
- `2026-03-21_0741_rank139-source-intake.md`：Rank139 已完成 `source intake + 两条轻量诚实守门` → admit_to_clean_replication_queue。
- `2026-03-21_0713_rank127-time-stability-park.md`：Rank127 转负 → park。

### 最近 strategy review（证据池）
- 上一条：`2026-03-21_1526_strategy-review.md`（当时已刷新 Hosted P3 快照到 15:23 UTC）。

### cron 列表与健康（本轮发现的关键异常）
- `bot3-momentum-auto-opt-13m`：consecutiveErrors=10（`timeout/auth`），导致今天 `07:41 UTC` 之后没有新增 optimization_loop。
- **本轮最小干预**：
  - 已将 `bot3-momentum-auto-opt-13m` cron 的 prompt **缩短**，并将 `thinking` 调到 `low`（减少 LLM 压力，目标是恢复执行）。
  - 同步将 `bot2-strategy-review-40m` cron 的 prompt **缩短**，并将 `thinking=low`（减少本 job 超时概率）。

---

## 3) 本轮 Top 1~3（下一步优先级）
1. **先恢复 bot3 可跑**：观察下一次 bot3 cron 是否能正常产出 `optimization_loop` + publish + email。
2. **按 Run 2 兑现 Rank139 的最小 clean replication**：只回答它是否真的改善 post-cost expectancy / retention / failure（不扩写）。
3. **Run 3 快决策**：Rank139 若不过关，立刻切 fresh intake；若过关，倾向直接 **promote_P2**（paper candidate），不要停留在模糊研究态。

## 4) 我这轮改了什么（最小必要）
- ✅ `docs/TODO.md`：在“最近关键 evidence”追加一条：bot3 cron 连续超时 + 本轮已做 prompt/think 最小修复。
- ✅ cron：缩短 `bot2-strategy-review-40m` / `bot3-momentum-auto-opt-13m` prompt，并将 `thinking=low`。

## 5) 风险与不确定性
- 若 bot3 仍持续 `timeout/auth`：下一步可能需要更强硬的 ops 动作（例如：明确指定更稳的 model、或临时降频/拆分任务），否则 desk board 只能“正确地排班但无法落地执行”。
