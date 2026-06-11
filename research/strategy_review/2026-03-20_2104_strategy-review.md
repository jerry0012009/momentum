# 2026-03-20 21:04 UTC strategy review

## TL;DR
当前 desk 的三席判断收口为：

- **Paper Seat**：继续是 **`EMA / 创业板ETF 1d active_primary / waiting_not_due`**
- **Live Seat**：继续 **`暂空`**
- **Scout Seat**：从泛泛 `fresh intake` 收紧为 **`Rank 130 / cross-market leader impulse nonlinear gate`**（下一顺位主点）

本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小必要更新：
- 不改 `Paper Seat`
- 不改 `Live Seat`
- 只把 `Scout Seat` 的 fresh intake 主点具体化到 **`Rank 130`**，并同步收紧 `Next 3 bot3 runs`

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 工作区：`git status --short | wc -l = 1971`，继续很脏，不混提
- 最近 optimization logs：
  - `2026-03-20 20:59 UTC / Rank 129 source intake -> hard park`
  - `2026-03-20 20:47 UTC / Rank 128 minimal clean replication -> park`
  - `2026-03-20 20:28 UTC / Rank 128 source intake + 两条轻量诚实守门`
  - `2026-03-20 20:16 UTC / EMA 美股 due window 真实续写`
- 最近 strategy review：
  - `2026-03-20 19:19 UTC`
  - `2026-03-20 18:39 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮 running
  - `bot3-momentum-auto-opt-13m`：enabled / 当前 running
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### EMA due-check（本轮实际重跑）
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
返回要点：
- `EMA = waiting_not_due`
- 最靠前 lane：`Crypto 1d+1wk（BTC/ETH/SOL） -> due_soon / 约 2.9 小时后到点`
- 其它 lane（`创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d / 美股 1d+1wk`）都已回到 `waiting_not_due`
- `require-due` 下脚本明确要求继续等待下一根 completed bar，不能伪造 refresh

### Hosted paper lanes 快照
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T20:50:45Z`
  - `new_closed_trades_appended = 0`
- `manual_narrow_paper_status.csv @ 2026-03-20T20:30:00Z`
  - 当前 open paper positions：
    - `Rank 17 / ETH-USD / long`
    - `Rank 17 / SOL-USD / short`
    - `Rank 29 / BTC-USD / short`
  - `Rank 2 / Rank 32b` 当前无 open position
- `Rank 122` 不在 manual-narrow csv 中，但独立 hosted artifacts 仍在，继续按：
  - **`P3 / strict-only / short-side re-arm / paper-only / recent-month red-watch`**

---

## 1. 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
### 结论
**Primary paper anchor 继续是：`EMA / 创业板ETF 1d active_primary`。**

### EMA 家族 hosted/backstop lanes
1. `创业板ETF 1d`（active_primary）
2. `美股 1d+1wk（SPY/QQQ/AAPL）`（active_secondary_backstop）
3. `Crypto 1d+1wk（BTC/ETH/SOL）`（active_secondary_backstop）
4. `贵州茅台 1d+1wk`（active_secondary_backstop）
5. `沪深300ETF 1d`（shadow_watch）

### 独立 hosted paper lanes
1. `Rank 122 / ATR compression + ROC ignition short re-arm gate`（`P3 / strict-only / paper-only / recent-month red-watch`）
2. `Rank 2 / volume_supportflip_higherlow_combo_all`（`P3`）
3. `Rank 17 / pullback_recovery_confirmation`（`P3`）
4. `Rank 29 / trendline_breakout_navigator`（`P3`）
5. `Rank 32b / ema_slope_floor_continuation`（`P3`）

### 当前 open hosted paper positions
- `Rank 17 / ETH-USD / long`
- `Rank 17 / SOL-USD / short`
- `Rank 29 / BTC-USD / short`

### desk 读法
这些 lane 继续只算：
- **`P3 hosted continuity / sidecar only`**
- 不是新的 seat
- 在 `EMA = waiting_not_due` 时，也不该抢 bot3 默认主资源位

---

## 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
### 结论
**继续保持暂空。**

### 原因
1. `Rank 127 / ATR delta` 已进入 **`P1 weak candidate / budget used`**，没有新证据支持升格
2. `Rank 125 / range location veto` 仍是 **`keep_P1 / budget used`**
3. `Rank 112 / 111` 也都还是 **`P1 evidence_pool / budget used`**
4. `Rank 128 / Rank 129` 已在最近两轮被压回 **`P0 / park / evidence pool`**
5. `Rank 122 / 2 / 17 / 29 / 32b` 虽在 `P3`，但都是 **paper-only hosted lanes**，不是 live challenger

### honest judgment
- **`P2` 仍空**
- **`P4` 仍空**
- 所以 **`Live Seat = 暂空`** 仍是最诚实写法

---

## 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
### 当前主资源位
1. **`Rank 130 / cross-market leader impulse nonlinear gate`**
   - 来源：`Xu, Li, Singh, Li (2024)` + `2026-03-19 05:58 UTC` quant digest
   - 角色：给 `breakout-short / Fib retest / EMA-PSAR` 补一个 **shared follow-up gate**，把 `leader impulse` 收紧成 **`low-z continuation / high-z veto`**，而不是“越强越追”
   - 当前状态：**`P1 / fresh paper source intake next`**

### 当前仍留在 active Scout 比较表，但不再默认主推
2. **`Rank 127 / signal→confirm ATR delta phase gate`**
   - verdict：`P1 weak candidate / budget used / evidence_pool`
3. **`Rank 125 / range location veto gate`**
   - verdict：`P1 keep_P1 / budget used / 留样但不再默认续命`
4. **`Rank 112 / basis dislocation short veto`**
   - verdict：`P1 weak candidate / evidence_pool / budget used`
5. **`Rank 111 / abnormal-return event clock`**
   - verdict：`P1 evidence_pool / budget used`

### 已退出主资源位的近邻候选
6. `Rank 128 / MAX(5m) impulse confirmation tier`
   - `P0 / park / evidence pool`
7. `Rank 129 / chip cost-band reclaim + winner-ratio re-expansion`
   - `P0 / park / evidence pool`
8. 更早 `Rank 126 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - 统一视作 **`P0 / park / evidence pool`**

### 不应误写成 Scout 主资源的 hosted continuity
9. `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
   - 全部只按 **`P3 hosted paper continuity / sidecar only`** 处理

### 边际价值比较
- **为什么 `Rank 130` 现在排第一？**
  - 它是真正新的、paper-based、5m/15m crypto 直接可测的候选
  - 它能同时服务 breakout-short / Fib / EMA 三条主线，不会把 Scout 资源重新缩成 breakout-only continuity
  - 它的 `trade on / trade off` 很具体：`low-z continuation / high-z veto`
- **为什么不是继续磨 `Rank 127 / 125 / 112 / 111`？**
  - 因为这些线都已进入 `budget used / evidence_pool` 区
  - 再磨一轮 admission wording 或 closeout docs，已经不再减少真实 gate
- **为什么不是先拿 `20:08 UTC` 的 skew band？**
  - skew band 更偏 breakout-short 单线 follow-up
  - 当前 desk 默认不再把 breakout 当唯一主资源位；`Rank 130` 的共用性和具体可测性更高

---

## 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
### P1
- `Rank 130 / cross-market leader impulse nonlinear gate`
  - **`P1`**（`fresh paper source intake next`）
- `Rank 127 / signal→confirm ATR delta phase gate`
  - **`P1`**（`weak candidate / budget used / evidence_pool`）
- `Rank 125 / range location veto gate`
  - **`P1`**（`keep_P1 / budget used / 留样`）
- `Rank 112 / basis dislocation short veto`
  - **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`
  - **`P1`**（`evidence_pool / budget used`）

### P0
- `Rank 129 / chip cost-band reclaim + winner-ratio re-expansion`
  - **`P0`**（`park / evidence pool`）
- `Rank 128 / MAX(5m) impulse confirmation tier`
  - **`P0`**（`park / evidence pool`）
- `Rank 126 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - 统一视作 **`P0 / park / evidence pool`**

### P2
- **当前为空**

### P3
- `Rank 122 / ATR compression + ROC ignition short re-arm gate`
  - **`P3`**（`narrow paper pilot / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - **`P3`**（`hosted narrow paper lanes / continuity only`）

### P4
- **当前为空**

---

## 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 当前最靠前 lane 是 `Crypto 1d+1wk -> due_soon / 约 2.9h`
   - 每一轮都先检查；若到点则先走 paper refresh，不得跳过

2. **Run 2 = Rank 130 / cross-market leader impulse nonlinear gate 的 source intake + 两条轻量诚实守门**
   - 先冻结：
     - 它是不是 **shared follow-up gate**，而不是新的独立 alpha
     - `trade on / trade off` 是否应写成：`low-z continuation / high-z veto`
     - leader z-score 只能来自 **signal 当根及之前、已完成 bar** 的跨市场序列，禁止 future refill

3. **Run 3 = 条件分支**
   - 若 `Rank 130` guard-pass 且 `EMA` 仍 `waiting_not_due`：
     - 只给 **1 次最小 clean replication**，直接比较 `baseline / low_z_only / high_z_veto`
   - 若 `Rank 130` 当场 hard-fail / exhausted：
     - 继续回 **fresh intake reserve**，不要回头磨旧 `P1`
   - 只有 fresh intake 这一层也 exhausted 后：
     - 才允许 `tiny-live plumbing fallback`

---

## 6. 为什么这轮要改 TODO 顶板
因为 `20:59 UTC` 之后，桌面事实有两点变化：
1. `Rank 129` 已被如实 hard-park，不能继续把 `Scout Seat` 写成泛泛 fresh intake 而不具体落点；
2. 当前旧 `P1` 候选的边际价值，已经整体低于再认领一条更具体、paper-based、跨三条主线都能直接服务的 fresh candidate。

所以本轮最小必要更新是：
- 保持 `Paper Seat` 不动
- 保持 `Live Seat = 暂空`
- 把 `Scout Seat` 的下一顺位主点具体化到 **`Rank 130`**
- 把 `Run 2 / Run 3` 从泛泛 fresh intake 改成更具体的：`130 intake -> 130 clean replication`

---

## 7. 本轮 reader-facing judgment 是否变化
**有变化。**
- 变化点不是 `Paper Seat` 或 `Live Seat`
- 变化点是：
  1. `Scout Seat` 的 fresh intake 主点从泛泛 reserve，改成 **`Rank 130 / cross-market leader impulse nonlinear gate`**
  2. `Next 3 bot3 runs` 不再写成抽象的“继续 fresh intake”，而是明确到 **`Rank 130`**

因此本轮已同步更新：
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`

---

## 8. 本轮后的 authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due，Crypto lane 约 2.9h 后 due）`；`Live Seat = 暂空`；`Scout Seat = Rank 130 / cross-market leader impulse nonlinear gate`；`Rank 127 / 125 / 112 / 111` 继续只留在 `P1 evidence pool / budget used`，`Rank 128 / 129` 留在 `P0 park / evidence pool`。