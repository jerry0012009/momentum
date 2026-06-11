# 2026-03-22 16:53 UTC — bot2 strategy review

## 本轮一句话判断
作战板维持：`Paper=EMA(创业板ETF 1d) running paper pilot / waiting_not_due`；`Live Seat=暂空`；`Scout 主资源继续锁 Rank 140（PBO/CSCV/DSR honesty gate, P1）`，但由于 **canonical impl smoke-run + DSR source lock 已完成**，下一轮 Run3 应转为：**把 scorecard 接到 1 条 fresh scout family（一次只接 1 条）**；hosted P3 继续事件驱动。

## 1) 本轮必查
### Repo 状态
- repo 仍为 **大量 untracked/变动**（research 日志 / scripts / tmp / artifacts 等）。本轮不做清理与 commit。

### 最近 `research/optimization_loop/`
- `2026-03-22_1647_rank140-source-intake_dsr.md`（DSR 权威参考锁定 + 人话落地口径）
- `2026-03-22_1539_rank140-canonical-offline-impl.md`（Rank140 canonical offline implementation smoke-run 已跑通）

### 最近 `research/strategy_review/`
- `2026-03-22_1515_strategy-review.md`

### 当前 cron 列表（desk 相关）
- `bot2-strategy-review-40m`
- `bot3-momentum-auto-opt-13m`
- `momentum-narrow-paper-lanes-20m`
- `bot7-quant-digest-30m`（最近连续 timeout，非本轮主干预点）

## 2) TRADING DESK BOARD 顶部核对 & 最小必要更新
- 已重读 `docs/TODO.md` 顶部作战板。
- **已做最小更新**：把 `Rank 140` 从“source intake / canonical implementation next（二选一）”更新为“已完成 smoke-run + DSR source lock；下一步接到 1 条 fresh scout family 输入”。
  - 更新点：`Scout Seat 当前主点` 一行
  - 更新点：`Next 3 bot3 runs -> Run3` 说明

## 3) 明确回答（按 desk head 要求）
### 3.1 Paper：primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### 3.2 Live Seat 是否空
- **Live Seat**：`暂空`（继续保持空；只有当 Scout 候选已足够接近 paper/tiny-live review 才升格）。

### 3.3 Scout Seat 复刻/推进对象
- **Scout 主点**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
  - 当前档位：`P1`
  - recommended_action：`keep_P1`
  - why_now：已完成 smoke-run + DSR 权威参考锁定，边际价值最高的下一步是把它变成“对任何 candidate family 都能复用的 honest scorecard”。

### 3.4 候选分档（P0~P4）快照
- **P4**：空
- **P3（hosted narrow paper / continuity）**：`Rank 2 / 17 / 29 / 32b`（20m refresh）；sidecar：`Rank 122 / Rank 139`
- **P2**：当前无 active P2
- **P1**：`Rank 140`（主点）、`Rank 125`、`Rank 112`、`Rank 111`
- **P0**：其余 parked ranks

### 3.5 Next 3 bot3 runs（排班）
1. **Run 1 = EMA due-check first**：只在 `due-now/overdue` 才 refresh；否则立刻切下一允许动作。
2. **Run 2 = Hosted P3 continuity（事件驱动）**：仅 `status-changing event` 才认领，否则跳过。
3. **Run 3 = Rank 140 单点交付**：把 canonical `PBO/CSCV/DSR` scorecard **接到 1 条 fresh scout family**（一次只接 1 条），并在输出里写清 `K(候选搜索半径)` 备注；禁止再做近义 intake/proxy/demo。

## 4) strongest evidence / weakest / Top 1~3
### strongest evidence
- Rank140 已从“概念/口号”进入“可复跑实现 + 权威来源”层：
  - canonical offline impl smoke-run 已跑通；
  - DSR 权威参考已锁定并口径化。
  这会直接提升所有 alpha 候选的 honesty 守门质量，减少被样本内赢家诱导。

### weakest / should-avoid
- 避免把 hosted P3（尤其 `Rank 139`）拉回 Scout 主资源做近义 health-check；除非出现真实 status-changing event。

### Top 1~3
1. `Rank 140`：接入 1 条 fresh scout family，产出 scorecard（PBO/CSCV/DSR + K）
2. `EMA Paper`：到点再做 due refresh + week-1 review continuity（按 clock，不抢跑）
3. `bot7`：若继续 timeout，下一轮考虑降复杂度/加 timeout/降频中的 **1 个最小干预**

## 5) 风险与不确定性
- repo 持续“脏”会提升误操作风险（尤其 scripts 与 artifacts 混杂），但当前仍不应抢走 seat 排班主线；建议后续单开一次工程卫生窗口处理。
