# 2026-03-20 18:39 UTC strategy review

## TL;DR
当前 desk **继续不换 Paper / Live 座位**，但 `Scout Seat` 已不能再停在 `Rank 126`：

- **Paper Seat**：继续是 **`EMA / 创业板ETF 1d active_primary / waiting_not_due`**
- **Live Seat**：继续 **`暂空`**
- **Scout Seat**：从 `Rank 126 / deepest retracement hold-quality gate`（已 `park`）切到新的 fresh source **`Rank 127 / signal→confirm ATR delta phase gate`**（`P1 / source intake + 两条轻量诚实守门 next`）

本轮已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 工作区：仍极脏，不混提
- 最近 optimization logs：
  - `2026-03-20 17:18 UTC / Rank 126 clean replication -> park`
  - `2026-03-20 16:36 UTC / Rank 125 cost-trade stability -> keep_P1 / budget used`
  - `2026-03-20 16:06 UTC / Rank 125 clean replication`
- 最近 strategy review：
  - `2026-03-20 16:43 UTC`
  - `2026-03-20 15:44 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮 running
  - `bot3-momentum-auto-opt-13m`：enabled / 最近连续 timeout
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近运行成功
  - `bot6-park-reframe-2h`：enabled / 最近 timeout
  - `bot7-quant-digest-30m`：enabled / 最近 timeout
  - `Rank32b live maintenance`：enabled / 连续 error

### Paper / hosted lane snapshots
- 刚刚再次实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前仍无 `due-now / overdue` lane
  - 最近 due：
    - `美股 1d+1wk -> 约 1.3h`
    - `Crypto 1d+1wk -> 约 5.3h`
    - `创业板ETF 1d -> 约 60.3h`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T18:28:27Z`
  - `new_closed_trades_appended = 1`
- `manual_narrow_paper_status.csv @ 2026-03-20T18:00:00Z`
  - 当前 open paper positions：
    - `Rank 17 / ETH-USD / long`
    - `Rank 17 / SOL-USD / short`
    - `Rank 29 / BTC-USD / short`
  - `Rank 2 / Rank 32b` 当前无 open position
- `Rank 122` 不在 manual-narrow csv 里，但其独立 hosted artifacts 仍在，继续按 **`P3 / strict-only / short-side re-arm / paper-only / recent-month red-watch`** 管理

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
这些 hosted lanes 继续只算 **`P3 hosted continuity / sidecar only`**。即便 `18:28 UTC` 又追加了 `1` 笔 closed trade，它们也不是新 seat，不该在 `EMA = waiting_not_due` 时抢占 bot3 默认主资源位。

---

## 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
### 结论
**继续保持暂空。**

### 原因
1. `Rank 126` 已在 `17:18 UTC` clean replication 后被压回 **`P0 / park / evidence pool`**。
2. `Rank 125` 虽未被判死刑，但当前已收口为 **`keep_P1 / budget used`**，不够升到 live。
3. `Rank 112 / Rank 111` 都还是 **`P1 evidence_pool / budget used`**。
4. `Rank 122 / 2 / 17 / 29 / 32b` 虽在 `P3`，但它们是 **paper-only hosted lanes**，不是 live challenger。
5. `Rank 127` 还只是 fresh source，连 `source intake + 两条轻量诚实守门` 都还没做完。
6. `Rank32b live maintenance` cron 虽在报错，但那是独立 `32b live/canary` 维护面，不等于当前 desk 应重新占一个 `Live Seat`。

### 当前 honest judgment
- **`P2` 为空**
- **`P4` 为空**
- 所以 **`Live Seat = 暂空`** 仍是最诚实写法

---

## 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
### 当前主资源位
1. **`Rank 127 / signal→confirm ATR delta phase gate`**
   - 来源：`ilahuerta-IA/backtrader-pullback-window-xauusd` + `2026-03-20 16:34 UTC` quant digest
   - 角色：给 `breakout-short / Fib retest_hold / EMA-PSAR` 补 **确认阶段 ATR 变化方向** 的 setup-specific confirm/veto 候选
   - 当前状态：本轮应正式接管 fresh Scout 主位

### 当前仍留在 active Scout 比较表，但不再默认主推
2. **`Rank 125 / range location veto gate`**
   - 当前 verdict：`keep_P1 / budget used / 留样但不再默认续命`
3. **`Rank 112 / basis dislocation short veto`**
   - 当前 verdict：`P1 weak candidate / evidence_pool / budget used`
4. **`Rank 111 / abnormal-return event clock`**
   - 当前 verdict：`P1 evidence_pool / budget used`

### 已退出 active Scout 主资源的最近候选
5. **`Rank 126 / deepest retracement hold-quality gate`**
   - 当前 verdict：`P0 / park / evidence pool`
   - 原因：`current_only` 还有一点信息，但 `current_plus_deepest` 一加上去就更像砍样本，不足以支撑升格

### 不应误写成 Scout 主资源的 hosted continuity
6. `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
   - 全部只按 `P3 hosted paper continuity / sidecar only` 处理

### 边际价值比较
- **为什么不是继续磨 Rank 125？**
  - 因为它这轮已经做完 clean replication + 成本/交易数稳定性，结论是 `keep_P1 / budget used`，继续磨它的边际价值明显下降。
- **为什么优先 Rank 127？**
  - 它是新的 paper/repo-based 15m crypto 候选；
  - 更直接服务三条主线共同面对的“确认阶段波动该怎么读”的问题；
  - 它当前最值得先回答的不是“能不能 shared”，而是**该不该 setup-specific**，这比继续围着旧 `P1` 补 admission wording 更值钱。

---

## 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
### P1
- `Rank 127 / signal→confirm ATR delta phase gate`
  - **`P1`**（`fresh repo source intake / 两条轻量诚实守门 next`）
- `Rank 125 / range location veto gate`
  - **`P1`**（`keep_P1 / budget used / 留样但不再默认续命`）
- `Rank 112 / basis dislocation short veto`
  - **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`
  - **`P1`**（`evidence_pool / budget used`）

### P0
- `Rank 126 / deepest retracement hold-quality gate`
- `Rank 124 / interim wick + ATR stop anchor`
- `Rank 123 / RSI state-machine admission`
- `Rank 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
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
   - 继续先跑 guarded due-check；当前美股 due 约 `1.3h`，若仍 `waiting_not_due`，不得空转。

2. **Run 2 = Rank 127 / signal→confirm ATR delta phase gate 的 source intake + 两条轻量诚实守门**
   - 先冻结：
     - 它是不是 **setup-specific confirm/veto**，而不是 shared 单阈值；
     - `trade on / trade off` 是否应拆成：`breakout_short mid-phase re-arm` / `fib_retest expanding confirm` / `ema_psar expansion veto` 这类分线口径；
     - `ATR delta` 只能来自 signal 当根及之前、已完成 bar 的 trailing 序列，禁止 future refill。

3. **Run 3 = 条件分支**
   - 若 `Rank 127` guard-pass 且 `EMA` 仍 `waiting_not_due`：
     - 只给 **1 次最小 clean replication**，直接比较 `baseline / shared_gate / setup_specific_gate`
   - 若 `Rank 127` 当场 hard-fail / exhausted：
     - 立刻回 **fresh intake reserve**
   - 只有 fresh intake 这一轮也 exhausted 后：
     - 才允许 `tiny-live plumbing fallback`

---

## 6. 为什么这轮要改 TODO 顶板
因为 `17:18 UTC` 之后，`Rank 126` 已经从 fresh Scout 主位被如实压回 `P0 / park`，而 `18:00 UTC` 的 manual narrow-paper 状态也显示 hosted paper 的 open-position 结构已经变成：
- `Rank 17 / ETH long`
- `Rank 17 / SOL short`
- `Rank 29 / BTC short`

也就是说：
- `Paper Seat` 仍然没变；
- `Live Seat` 仍然没人够格升；
- 真正需要更新的是 **`Scout Seat` 主资源位** 与 **hosted paper 当前运行面貌**。

本轮最小必要更新就是：
- 维持 `EMA` 不动；
- 维持 `Live Seat = 暂空`；
- 把 `Scout Seat` 从 `Rank 126` 切到 **`Rank 127`**；
- 把 hosted paper 当前 open-position 读法更新到 `Rank 17 + Rank 29`。

---

## 7. 本轮 reader-facing judgment 是否变化
**有变化。**
- 变化点一：**`Scout Seat` 主资源位**从 `Rank 126` 切到 **`Rank 127 / signal→confirm ATR delta phase gate`**。
- 变化点二：hosted paper 的当前运行面貌已不再是“只剩 Rank 17 open”，而是 **`Rank 17 + Rank 29`** 同时有 open position。

因此已同步更新：
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`

---

## 8. 本轮后的 authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 127 / signal→confirm ATR delta phase gate`；`Rank 126` 已 park，`Rank 125` 留样但不再默认续命；`Rank 122 / 2 / 17 / 29 / 32b` 继续只按 hosted paper continuity 管。
