# 2026-03-20 22:05 UTC strategy review

## 本轮一句话判断
当前 desk 仍维持：**`Paper Seat = EMA / 创业板ETF 1d active_primary`、`Live Seat = 暂空`、`Scout Seat = Rank 131 / fib violation-cluster + 1-bar memory gate`**。本轮只做了一个最小必要板面修正：把 `docs/TODO.md` 顶部 `Hosted P3` 的 open-position 快照更新到 `2026-03-20 22:00 UTC`，确认 **`Rank 29` 已回到 flat，当前真正在开的 hosted open positions 只剩 `Rank 17 / ETH long + SOL short`**。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 工作区：`git status --short` 仍极脏；本轮不混提，只做最小局部更新
- 最近 optimization logs：
  - `2026-03-20 22:00 UTC / Rank 131 intake + honesty gate passed`
  - `2026-03-20 21:41 UTC / Rank 130 minimal clean replication -> park`
  - `2026-03-20 20:59 UTC / Rank 129 intake -> park`
  - `2026-03-20 20:16 UTC / EMA 美股 due window 真实续写`
- 最近 strategy review：
  - `2026-03-20 21:04 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 当前运行中
  - `bot3-momentum-auto-opt-13m`：enabled / 当前运行中
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近 `22:00 UTC` 成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 最新 hosted paper lane 快照
读取：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`

结论：
- `run_at_utc = 2026-03-20T22:00:13Z`
- `new_closed_trades_appended = 0`
- 当前 open paper positions 只剩：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 29 / BTC-USD` 已不再 open，当前回到 `flat / no open position`
- `Rank 2 / Rank 32b` 当前也无 open position

### 最新 EMA / Paper Seat 读法
- 最新真实 due-check 仍来自 `22:00 UTC / Rank 131` 那轮之前的 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 当前 authoritative 结论仍是：
  - `EMA = waiting_not_due`
  - 最近 due 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`
  - 其余 lane（创业板ETF / 贵州茅台 / 沪深300ETF / 美股）都仍在 `waiting_not_due`

---

## 1. 当前 strongest evidence
1. **`Rank 131` 已经完成 `source intake + 两条轻量诚实守门`，当前是唯一仍在主资源位上的 fresh Scout。**
   - 规则清楚：`Fib retest_hold` 上的最近 `1~2` 根 violation-cluster 只配当 `confirmation / veto gate`，不是独立 alpha
   - 诚实门已过：只能用 `signal 当根及之前、已完成 bar` 的历史破位记忆
2. **`Rank 130` 已在最小 clean replication 后如实压回 `P0 / park`。**
   - 这说明当前 board 没有继续奖励“旧 P1 反复磨文案”的低杠杆行为
3. **`Paper Seat` 仍是被 market clock 阻塞，而不是执行失灵。**
   - `EMA` 当前是 `waiting_not_due`
   - 这继续支持 desk 默认导流：`Scout Seat > tiny-live plumbing > 其他维护`
4. **hosted P3 lanes 的最新状态更收敛了。**
   - `Rank 29` 当前已 flat
   - 当前真有 open paper position 的 hosted lane 只剩 `Rank 17`
   - 这进一步说明 hosted continuity 现在更不该被误写成新的主 seat

---

## 2. 当前 weakest / should-park lines
1. **`Rank 130 / 129 / 128`**
   - 已经完成该给的最小诚实检查
   - 当前都应继续留在 `P0 / park / evidence pool`
2. **`Rank 127 / 125 / 112 / 111`**
   - 都是 `P1`，但默认预算已用过
   - 本轮没有新的 status-changing evidence，继续回头磨它们会降低边际价值
3. **任何把 hosted `P3` continuity 误当作新的 Scout 主资源位的写法**
   - 当前尤其不该把 `Rank 29` 的托管状态误写成“还在开仓推进”
   - 最新事实是：`Rank 29 = hosted lane 仍在托管，但当前 flat`

---

## 3. 本轮必须回答的 5 个问题
### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d active_primary`。**

#### EMA 家族 hosted/backstop lanes
- `创业板ETF 1d`（active_primary）
- `Crypto 1d+1wk（BTC/ETH/SOL）`（active_secondary_backstop，当前最近 due）
- `美股 1d+1wk（SPY/QQQ/AAPL）`（active_secondary_backstop）
- `贵州茅台 1d+1wk`（active_secondary_backstop）
- `沪深300ETF 1d`（shadow_watch）

#### 独立 hosted paper lanes
- `Rank 122 / ATR compression + ROC ignition short re-arm gate`（`P3 / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / volume_supportflip_higherlow_combo_all`（`P3`）
- `Rank 17 / pullback_recovery_confirmation`（`P3`）
- `Rank 29 / trendline_breakout_navigator`（`P3`）
- `Rank 32b / ema_slope_floor_continuation`（`P3`）

#### 当前真正在开的 hosted open positions（22:00 UTC 最新快照）
- `Rank 17 / ETH-USD / long`
- `Rank 17 / SOL-USD / short`

补一句最重要的人话：**hosted P3 lane 仍在跑，但当前有 open position 的只剩 `Rank 17`；`Rank 29` 当前已 flat。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- `P2` 当前仍空
- `Rank 127 / 125 / 112 / 111` 都还是 `P1 / budget used / evidence_pool`
- `Rank 131` 还只到 `guard-passed / minimal clean replication next`，离 `P2` 甚至 `P3` 都还有距离
- `Rank 122 / 2 / 17 / 29 / 32b` 虽然是 `P3`，但都属于 **paper-only hosted lane**，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 131 / fib violation-cluster + 1-bar memory gate`**
  - 当前阶段：`source intake 已完成，minimal clean replication next`
  - 角色：给 `Fib retest_hold` 补一层“最近连续破位记忆”的 honest veto/confirm gate

#### 当前仍留在 active Scout 比较表，但不再默认主推
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 不应误写成 Scout 主点的 hosted continuity
- `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - 继续只按 `P3 hosted paper continuity / sidecar only` 处理

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 131`：`P1`（`guard-passed / minimal clean replication next`）
- `Rank 127`：`P1`（`weak candidate / budget used / evidence_pool`）
- `Rank 125`：`P1`（`keep_P1 / budget used`）
- `Rank 112`：`P1`（`weak candidate / evidence_pool / budget used`）
- `Rank 111`：`P1`（`evidence_pool / budget used`）

#### P0
- `Rank 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 122`：`P3`（`narrow paper pilot / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3`（`hosted narrow paper lanes / continuity only`）

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若有真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍是 `waiting_not_due`，不能空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，则只给 `Rank 131` 1 次最小 clean replication**
   - 对照：`baseline / t-1 veto / t-1,t-2 cluster veto`
   - 统一口径：`signal 当根及之前数据 + next-bar open + no-overlap`

3. **Run 3 = 条件分支**
   - 若 `Rank 131` 出现 honest uplift：补 `1` 个真正会改变级别的最小稳定性切片，并明确写 `park / keep_P1 / promote_P2 / promote_P3`
   - 若 `Rank 131` hard-fail / exhausted：直接回 `fresh intake reserve`
   - 只有 fresh intake 也 exhausted 后，才允许 `tiny-live plumbing fallback`

---

## 4. Active Scout 边际价值比较（why now）
### 为什么 `Rank 131` 继续排第一
- 它是当前唯一一个**刚完成 intake、且已经过了两条轻量诚实守门**的新鲜 paper-based 候选
- 它直接服务 `Fib retest_hold`，同时能给 `breakout-short` 的假守住/假确认边界提供补充
- 它下一步就是那 `1` 次最小 clean replication，符合当前 `Scout Seat` 的快筛节奏

### 为什么不是回头磨 `Rank 127 / 125 / 112 / 111`
- 这些线都已经拿过它们该拿的那 `1` 次关键诚实检查
- 当前没有新的证据足以触发 `升格 / park / 重开预算`
- 再做更像 admission write-back，而不是减少真实 gate

### 为什么也不是继续盯 hosted `P3`
- `EMA` 仍 `waiting_not_due`
- 今天的 hosted continuity 已有独立 cron 在托管
- 最新快照里 `Rank 29` 甚至已 flat，说明这层更该被当作 sidecar，而不是主资源位

---

## 5. 建议优先级 Top 1~3
1. **继续保持 `Run 2 = Rank 131 minimal clean replication` 不变**
2. **若 `Rank 131` 不成，就立刻切 fresh intake，不回头磨旧 P1**
3. **继续把 hosted `P3` 只当 low-frequency 托管层，不让它们回流抢 Scout 预算**

---

## 6. TODO / web / cron 的改动或建议
### 本轮实际改动
- 已最小更新 `docs/TODO.md` 顶部 `Hosted P3 快照`：
  - 把 open-position 快照同步到 `2026-03-20 22:00 UTC`
  - 明确写出 `Rank 29 = 当前 flat / no open position`

### 为什么这轮只做这一个小改
- 席位判断没有变：`Paper = EMA`、`Live = 暂空`、`Scout = Rank 131`
- `Next 3 bot3 runs` 也没有变
- 但 hosted paper 的 reader-facing 状态确实发生了变化：**当前 open position 只剩 Rank 17**
- 所以本轮最小必要动作是修正板面快照，而不是重写排班

### cron / 节奏建议
- 暂不改 cron
- 当前 cron 结构已经基本匹配 desk 分工：
  - `bot2` 负责排兵布阵
  - `bot3` 负责主资源位执行
  - `momentum-narrow-paper-lanes-20m` 负责 hosted P3 continuity
- 这轮没有看到需要额外收紧 prompt 的新信号

---

## 7. 风险与不确定性
1. **`Rank 131` 目前还只有 intake / honesty-gate 证据，没有 clean replication。**
   - 不能提前把它写成 `P2`
2. **`EMA` 的最近 due 仍在今晚稍后。**
   - 不能把 `due_soon` 误当 `due-now`
3. **manual narrow paper 的 open/flat 状态依赖 20 分钟级刷新。**
   - 当前 `Rank 29 flat` 是最新 authoritative 快照，但仍应继续交给 hosted cron 托管，不要把这层状态更新误写成新的 Scout 任务

---

## 8. authoratitive one-liner
> `Paper Seat = EMA（继续 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 131 / fib violation-cluster + 1-bar memory gate`；hosted P3 lane 仍按 `122 / 2 / 17 / 29 / 32b` 托管，但当前 open paper positions 只剩 `Rank 17 / ETH long + SOL short`，`Rank 29` 已 flat。
