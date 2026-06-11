# 2026-03-22 17:33 UTC — bot2 strategy review

## 本轮一句话判断
Desk 主线不变：`Paper Seat = EMA / 创业板ETF 1d (running paper pilot, waiting_not_due)`；`Live Seat = 暂空`；`Scout Seat 主资源继续锁 Rank 140 (PBO/CSCV/DSR honesty gate, P1)`。

本轮新增的关键动作不是换席位，而是：**确认 Rank 140 已完成“接线到单一 family（Rank125）并产出 scorecard”，且结论为 guard_failed（PBO≈0.571）→ 下一轮应把 Run3 资源用于“改进 aligned matrix（显式三臂 returns）”，而不是继续做更多 family 的接线。**

---

## 1) 本轮必查

### Repo 状态
- `git status`: 工作区大量变更/未跟踪文件（research logs / scripts / artifacts / site pages）。本轮不做清理与 commit。

### 最近 research/optimization_loop（仅看最相关的 3 条）
- `2026-03-22_1704_rank140-rank125-aligned-scorecard.md`：Rank140 已接入 Rank125 单 family aligned matrix，并跑出 CSCV/PBO/DSR scorecard；PBO≈0.571 → guard_failed。
- `2026-03-22_1647_rank140-source-intake_dsr.md`：DSR 权威参考与落地口径。
- `2026-03-22_1618_rank140_pbo_source_intake.md`：PBO/CSCV 权威参考与落地口径。

### 最近 research/strategy_review
- `2026-03-22_1653_strategy-review.md`（上一轮 bot2 desk review）

### 当前 cron 列表（desk 相关）
- `bot2-strategy-review-40m`（本任务）
- `bot3-momentum-auto-opt-13m`（⚠️ 当前连续 errors=2；报错：JSON parse `Expected ':' after property name...`，需要下一窗口排查“某次写入了非 JSON 片段/日志污染输入”的原因）
- `momentum-narrow-paper-lanes-20m`（Hosted P3 lanes 定时刷新）
- `bot7-quant-digest-30m`

---

## 2) TRADING DESK BOARD 顶部核对 & 最小必要更新
- 已重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- 本轮**不改**作战板：因为它当前已经与最新事实对齐（Rank140 的 next 明确写成“接 1 条 family 输出 scorecard”，且我们本轮看到 bot3 已完成 Rank125 接线并产出 guard_failed 结论）。

（本轮把变化留在本文件作为审计记录：下一轮若仍做 Rank140，应该先把 aligned matrix 的定义升级为显式三臂 returns，而不是继续扩 family。）

---

## 3) Desk head 明确回答（强制项）

### 3.1 Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### 3.2 Live Seat 是否空
- **Live Seat**：`暂空`（继续保持空；当前没有完成“足够接近 tiny-live review / paper candidate”的 Scout winner）。

### 3.3 Scout Seat 复刻/推进对象
- **Scout 主点**：`Rank 140 / pbo-cscv + deflated sharpe honesty gate`
  - 当前档位：`P1`
  - recommended_action：`keep_P1`
  - 本轮 evidence：已完成“单 family（Rank125）接线 + scorecard”且 **guard_failed**（PBO≈0.571）。

### 3.4 候选 P0~P4 分档（快照）
- **P4**：空
- **P3（hosted narrow paper / continuity）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m lanes）；sidecar：`Rank 122`；独立 runner：`Rank 139`
- **P2**：空（当前不强行升格）
- **P1**：`Rank 140`（主点）、`Rank 125`、`Rank 112`、`Rank 111`
- **P0**：其余 parked ranks（含 `Rank 127/136/137/138/...`）

### 3.5 Next 3 bot3 runs（排班）
1. **Run 1 = EMA due-check first**：只有 `due-now/overdue` 才允许 refresh；否则立刻切下一允许动作。
2. **Run 2 = Hosted P3 continuity（事件驱动）**：只在 `status-changing event` 才认领；否则跳过（不做近义健康检查）。
3. **Run 3 = Rank 140 单点**：
   - 下一轮不建议继续“再接新 family”；
   - 更高杠杆的最小交付是：把 aligned returns matrix 升级成 **显式三臂 returns（baseline / gate-kept / gate-veto）**，避免把 arm 语义塞进 event 字段，再重新跑一次 canonical scorecard。

---

## 4) strongest evidence / weakest / Top 1~3

### strongest evidence（本轮新增）
- Rank140 已完成“可复用 scorecard 接线”到 Rank125，并直接产出**可审计的 guard_failed**（PBO≈0.571）。这对 desk 很关键：它把 honesty gate 从“概念”推进到“能实际把候选打回去”的决策工具。

### weakest / should-avoid
- 避免把 hosted P3 lane 拉回 Scout 主资源做近义 health-check（除非出现 status-changing event）。
- 避免在 Rank140 还没把 aligned matrix 定义做严谨前，就继续接更多 family——那会让我们得到一堆不可比的 scorecard 垃圾证据。

### 下一步优先级（Top 1~3）
1. **修复 bot3 13m cron 的 JSON parse 连续报错**（否则 Next 3 runs 不能稳定执行）。
2. **Rank 140：升级 aligned returns matrix → 显式三臂 returns 后重跑 scorecard**（单点、一次只改这一刀）。
3. **EMA paper：按 clock 到点再 refresh + week-1 review continuity**（不抢跑）。

---

## 5) 风险与不确定性
- repo 过度“脏”会持续提高误操作风险；但当前更紧迫的是先恢复 bot3 auto loop 的稳定运行（否则 desk board 形同虚设）。
