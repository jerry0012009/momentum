# 2026-03-22 18:31 UTC — bot2 strategy review

## 本轮一句话判断
Desk 主线继续不变：`Paper Seat = EMA / 创业板ETF 1d (running paper pilot, waiting_not_due)`；`Live Seat = 暂空`；`Scout Seat` 继续锁定 `Rank 140 / pbo-cscv deflated sharpe honesty gate`，但**本轮结论更明确**：它已经完成 `Rank125` 与 `Rank112` 两条 single-family scorecard 接线且都 `guard_failed`，因此下一轮 bot3 不该继续盲目扩 family，而应先把 aligned returns matrix 升级成 **显式三臂 returns** 再重跑 canonical scorecard。

---

## 1) 本轮必查

### Repo 状态
- `git status`：工作区仍有大量未跟踪/未提交文件（research logs / scripts / artifacts / site pages / tmp）。
- 本轮只做 **最小必要更新**：调整 `docs/TODO.md` 顶部 desk board，并新增本轮 strategy review 日志；不做清理与 commit。

### 最近 research/optimization_loop（只看本轮最相关）
- `2026-03-22_1805_rank140-rank112-aligned-scorecard.md`
  - Rank140 接入 `Rank112` 单 family aligned matrix；scorecard `PBO=1.0` → `guard_failed`。
- `2026-03-22_1704_rank140-rank125-aligned-scorecard.md`
  - Rank140 接入 `Rank125` 单 family aligned matrix；scorecard `PBO≈0.571` → `guard_failed`。
- `2026-03-22_1647_rank140-source-intake_dsr.md`
  - DSR 权威来源和落地口径已锁定。

### 最近 research/strategy_review
- `2026-03-22_1733_strategy-review.md`
  - 上轮已给出方向：不要继续扩 family，优先升级 aligned matrix 语义。

### 当前 cron 列表（desk 相关）
- `bot2-strategy-review-40m`：正常运行中（本任务）。
- `bot3-momentum-auto-opt-13m`：当前 `consecutiveErrors=1`，最近一次报错 `Unexpected end of JSON input`；需保持关注，但暂不改变 desk 主线。
- `momentum-narrow-paper-lanes-20m`：正常。
- `bot7-quant-digest-30m`：正在运行。
- 其他 cron 多为旁路任务，与本轮 seat 排兵无直接冲突。

---

## 2) TRADING DESK BOARD 顶部核对 & 最小必要更新
本轮已重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，并做了 **最小必要更新**：

1. `Scout Seat` 主点说明补充：
   - `Rank 140` 已完成 `Rank125/112` 两条 single-family scorecard；
   - `next` 明确切到：**显式三臂 returns matrix 后重跑 canonical scorecard**。

2. `Next 3 bot3 runs` 的 Run 3 更新为：
   - 不再写“继续接 1 条 family”；
   - 改成“先升级 aligned returns matrix 的 arm 语义，再重跑”。

3. `最近关键 evidence` 更新为最近 5 条真实改变排兵布阵的事实：
   - 18:05 `Rank112 scorecard guard_failed`
   - 17:04 `Rank125 scorecard guard_failed`
   - 12:15 `Rank139` 退出 Scout 主资源位
   - 01:46 `Rank140` fresh intake
   - 01:05 `Rank139` hosted pilot runner 落地

结论：顶板现已与最新证据对齐。

---

## 3) Desk head 明确回答（强制项）

### 3.1 Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted lanes / family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **Hosted P3 continuity / sidecar**：
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m hosted narrow paper lanes）
  - `Rank 139`（independent hosted pilot runner）
  - `Rank 122`（low-frequency sidecar）

### 3.2 Live Seat 是否空
- **Live Seat = 暂空**。
- 当前没有任何 Scout 候选已接近 `tiny-live review` 到足以抢占 Live Seat 的程度；不为了“桌面好看”强行塞人。

### 3.3 Scout 复刻对象
- **Scout 主资源继续复刻/推进对象**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
- 当前最该做的不是换题，而是把这个 honesty gate 的 scorecard 输入定义做严谨：
  - 从“event 二分类映射 arms”
  - 升级为“显式三臂 returns（baseline / gate-kept / gate-veto）”。

### 3.4 候选 P0~P4 分档（本轮快照）
- **P4**：空
- **P3**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b / Rank 139 / Rank 122`
- **P2**：空
- **P1**：
  - `Rank 140`（当前 Scout 主点）
  - `Rank 125`
  - `Rank 112`
  - `Rank 111`
- **P0**：其余 parked / evidence-pool 候选（含 `Rank 137 / 138 / 127 / 136 / 135 / 134 / ...`）

### 3.5 Next 3 bot3 runs 排班
1. **Run 1 = EMA due-check first**
   - 只有出现真实 `due-now / overdue` 才 refresh；否则不得伪刷新。
2. **Run 2 = Hosted P3 continuity（低频、事件驱动）**
   - 只在 `status-changing event` 时认领；若无事件，直接跳过。
3. **Run 3 = Rank 140 单点**
   - 不再继续扩更多 family；
   - 先把 aligned returns matrix 升级成 **显式三臂 returns**，再重跑 canonical scorecard；
   - 仍保持“一次只动 1 个主点 + 1 个紧邻子点”。

---

## 4) strongest evidence / weakest / why now

### strongest evidence
- `Rank 140` 已经不是“概念层候选”，而是已经能跨 family 输出可审计 scorecard 的真正 honesty-layer 管线。
- 但 `Rank125` 与 `Rank112` 两次接线都给出 `guard_failed`，说明现在最值钱的信息不再是“能不能接线”，而是“当前 arm 语义是不是太粗，导致 scorecard 只是在测噪声”。

### weakest / should-avoid
- 不要在当前 matrix 定义仍粗糙时继续接第 3、第 4 条 family；那只会制造更多难解释的 `guard_failed`，却不能提高决策质量。
- 不要把 hosted P3 lanes 拉回 Scout 主资源做近义 health-check。
- 不要因为 `bot3` 最近一次 JSON parse error 就把整个 desk 排兵切成“先修 cron 再研究”；除非错误连续扩大或阻塞后续轮次，否则先保持 desk 主线不变、只在日志中标记风险。

### why now
- 当前 EMA 确实 `waiting_not_due`；Paper Seat 没有合法 refresh 动作。
- Hosted P3 lanes 无 status-changing event。
- 因此本轮唯一高杠杆动作就是把 Scout 资源收紧到 **Rank140 的语义修正**。

---

## 5) 风险 / watch items
- `bot3-momentum-auto-opt-13m` 最近出现一次 `Unexpected end of JSON input`；若下一两轮继续报同类错误，bot2 下轮应把它提升为显式 desk 风险并考虑加入 Run 2 前置检查。
- repo 持续大量脏文件；当前还能容忍，但会提高后续误操作与审计难度。

---

## 6) 本轮结论
- **Paper anchor**：仍是 `EMA / 创业板ETF 1d`。
- **Hosted lanes**：仍是 `Rank2 / Rank17 / Rank29 / Rank32b / Rank139 / Rank122`。
- **Live Seat**：继续空。
- **Scout 主点**：继续 `Rank140`。
- **P 档位**：`P3` continuity 池不变，`P1` 仍以 `Rank140/125/112/111` 为主。
- **Next 3 bot3 runs**：`EMA due-check → hosted P3 event-driven continuity → Rank140 显式三臂 returns matrix 重跑`。
