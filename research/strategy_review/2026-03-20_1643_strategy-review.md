# 2026-03-20 16:43 UTC strategy review

## TL;DR
当前 desk **继续不换 Paper / Live 座位**，但要把 `Scout Seat` 从泛泛 `fresh intake` 收紧成一个明确主点：

- **Paper Seat**：继续是 **`EMA / 创业板ETF 1d active_primary / waiting_not_due`**
- **Live Seat**：继续 **`暂空`**
- **Scout Seat**：从 `Rank 125` 的 keep-P1 留样切回 fresh intake，并明确前推到 **`Rank 126 / deepest retracement hold-quality gate`**（`P1 / source intake + 两条轻量诚实守门 next`）

本轮已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 脏文件：`git status --short | wc -l = 1914`
- 最近 optimization logs：
  - `2026-03-20 16:36 UTC / Rank 125 cost-trade stability -> keep_P1 / budget used`
  - `2026-03-20 16:06 UTC / Rank 125 clean replication`
  - `2026-03-20 15:35 UTC / Rank 125 source intake`
- 最近 strategy review：
  - `2026-03-20 15:44 UTC`
  - `2026-03-20 15:04 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / running
  - `bot3-momentum-auto-opt-13m`：enabled / running
  - `momentum-narrow-paper-lanes-20m`：enabled / running
  - `bot7-quant-digest-30m`：enabled / running
  - `bot6-park-reframe-2h`：enabled
  - `Rank32b live maintenance`：enabled but **连续 error**（独立 32b live/canary 维护面，不改当前 desk seat judgment）

### Paper / hosted lane snapshots
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - `创业板ETF 1d = active_primary / waiting_not_due`
  - `美股 1d+1wk = active_secondary_backstop / waiting_not_due`
  - `Crypto 1d+1wk = active_secondary_backstop / waiting_not_due`
  - `贵州茅台 1d+1wk = active_secondary_backstop / waiting_not_due`
  - `沪深300ETF 1d = shadow_watch / waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T16:11:14Z`
  - `new_closed_trades_appended = 3`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv @ 2026-03-20T15:45:00Z`
  - open paper 仅剩：
    - `Rank 17 / ETH-USD / long`
    - `Rank 17 / SOL-USD / short`
  - `Rank 2 / Rank 29 / Rank 32b` 当前都无 open position
- `Rank 122` 不在 manual-narrow csv 里，但其独立 hosted artifacts 仍在，当前继续按 **`P3 / paper-only / recent-month red-watch`** 管理

---

## 1. 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
### 结论
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d active_primary`。**

### EMA 家族 hosted/backstop lanes
1. `创业板ETF 1d`（active_primary）
2. `美股 1d+1wk（SPY/QQQ/AAPL）`（active_secondary_backstop）
3. `Crypto 1d+1wk（BTC/ETH/SOL）`（active_secondary_backstop）
4. `贵州茅台 1d+1wk`（active_secondary_backstop）
5. `沪深300ETF 1d`（shadow_watch）

### 独立 hosted paper lanes
1. `Rank 122 / ATR compression + ROC ignition short re-arm gate`（`P3 / paper-only / recent-month red-watch`）
2. `Rank 2 / volume_supportflip_higherlow_combo_all`（`P3`）
3. `Rank 17 / pullback_recovery_confirmation`（`P3`）
4. `Rank 29 / trendline_breakout_navigator`（`P3`）
5. `Rank 32b / ema_slope_floor_continuation`（`P3`）

### 当前 open hosted paper positions
- `Rank 17 / ETH-USD / long`
- `Rank 17 / SOL-USD / short`

### desk 读法
这些 hosted lanes 都属于 **`P3 hosted continuity / sidecar only`**，不是新的 seat，也不该在 `EMA = waiting_not_due` 时抢占 bot3 的默认主资源。

---

## 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
### 结论
**继续保持暂空。**

### 原因
1. `Rank 126` 还只是 fresh source，连 `source intake + 两条轻量诚实守门` 都还没跑完。
2. `Rank 125` 虽未被判死刑，但本轮已收口为 **`keep_P1 / budget used / 留样但不再默认续命`**，不够升到 live。
3. `Rank 112 / Rank 111` 都是 `P1 evidence_pool / budget used`，更不该占 Live Seat。
4. `Rank 122 / 2 / 17 / 29 / 32b` 虽处于 `P3`，但它们是 **paper-only hosted lanes**，不是 live challenger。
5. `Rank32b live maintenance` cron 虽在报错，但它是独立 32b live/canary 维护面，不等于 desk 现在就应该重新占一个 `Live Seat`。

### 现在的 honest judgment
- **`P2` 为空**
- **`P4` 为空**
- 所以 `Live Seat = 暂空` 仍是最诚实写法

---

## 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
### 当前主资源位
1. **`Rank 126 / deepest retracement hold-quality gate`**
   - 来源：`joshyattridge/smart-money-concepts` + `2026-03-20 15:57 UTC` quant digest
   - 角色：给 `Fib retest_hold / breakout follow-up / EMA-PSAR` 补一个更诚实的 hold-quality / honesty gate
   - 当前状态：本轮应正式接管 fresh Scout 主位

### 当前仍留在 active Scout 比较表，但不再默认主推
2. **`Rank 125 / range location veto gate`**
   - 当前 verdict：`keep_P1 / budget used / 留样但不再默认续命`
3. **`Rank 112 / basis dislocation short veto`**
   - 当前 verdict：`P1 weak candidate / evidence_pool / budget used`
4. **`Rank 111 / abnormal-return event clock`**
   - 当前 verdict：`P1 evidence_pool / budget used`

### 不应误写成 Scout 主资源的 hosted continuity
5. `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
   - 全部只按 `P3 hosted paper continuity / sidecar only` 处理

### 边际价值比较
- **为什么不是继续磨 Rank 125？**
  - 因为 Rank 125 这轮已经做完 clean replication + 成本/交易数稳定性，结论是 `keep_P1` 而不是 `promote_P2`；继续磨它的边际价值明显下降。
- **为什么优先 Rank 126？**
  - 它是新的 paper/repo-based 15m crypto 候选；
  - 更直接服务 `hold-quality honesty`，能同时影响 `Fib / breakout follow-up / EMA-PSAR` 的 desk judgment；
  - 比 stop-anchor 这类更偏 risk overlay 的线更像真正的 scout fast-lane 主点。

---

## 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
### P1
- `Rank 126 / deepest retracement hold-quality gate`
  - **`P1`**（`fresh repo source intake / 两条轻量诚实守门 next`）
- `Rank 125 / range location veto gate`
  - **`P1`**（`keep_P1 / budget used / 留样但不再默认续命`）
- `Rank 112 / basis dislocation short veto`
  - **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`
  - **`P1`**（`evidence_pool / budget used`）

### P0
- `Rank 124 / interim wick + ATR stop anchor`
- `Rank 123 / RSI state-machine admission`
- `Rank 121 / 120 / 119 / 118 / 117`
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
   - 继续先跑 guarded due-check；若仍 `waiting_not_due`，不得空转。

2. **Run 2 = Rank 126 / deepest retracement hold-quality gate 的 source intake + 两条轻量诚实守门**
   - 先冻结：
     - `trade on / trade off`
     - `current_retracement_pct + deepest_retracement_pct`
     - `1-bar shift / trailing-only / no future fill-back`
   - 只做这一条主点，不并开多个 fresh source。

3. **Run 3 = 条件分支**
   - 若 `Rank 126` 已 guard-pass 且 `EMA` 仍 `waiting_not_due`：
     - 只给 **1 次最小 clean replication**
   - 若 `Rank 126` 当场 hard-fail / exhausted：
     - 立刻回 **fresh intake reserve**
   - 只有 fresh intake 这一轮也 exhausted 后：
     - 才允许 `tiny-live plumbing fallback`

---

## 6. 为什么这轮要改 TODO 顶板
因为 `16:36 UTC` 之后，顶板虽然已经写了“回 fresh intake”，但还停在**泛池子**口径。按照本轮要求，bot2 不能只说“回 fresh pool”，而要把：
- 当前 `Paper Seat` 的 anchor 与 hosted lanes
- `Live Seat` 为什么仍空
- `Scout Seat` 的主资源位到底是谁
- active Scout 的分级
- `Next 3`

写成更明确、可执行的 authoritative 读法。

本轮最小必要更新就是：
- 维持 `EMA` 不动；
- 明确 `Live Seat = 暂空`；
- 把 `Scout Seat` 从“泛 fresh intake”收紧成 **`Rank 126`**。

---

## 7. 本轮 reader-facing judgment 是否变化
**有变化。**
- 变化点不是 `Paper Seat` 或 `Live Seat`，而是 **`Scout Seat` 主资源位**：
  - 从泛泛 `fresh intake` 收紧为 **`Rank 126 / deepest retracement hold-quality gate`**
- 因此已同步更新：
  - `docs/TODO.md` 顶部 `TRADING DESK BOARD`

---

## 8. 本轮后的 authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 126 / deepest retracement hold-quality gate`；`Rank 125` 留样但不再默认续命；`Rank 122 / 2 / 17 / 29 / 32b` 继续只按 hosted paper continuity 管。
