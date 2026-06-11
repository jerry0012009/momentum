# 2026-03-20 19:19 UTC strategy review

## TL;DR
当前 desk 的三席判断继续收口为：

- **Paper Seat**：继续是 **`EMA / 创业板ETF 1d active_primary / waiting_not_due`**
- **Live Seat**：继续 **`暂空`**
- **Scout Seat**：**继续先给 `Rank 127 / signal→confirm ATR delta phase gate`**，但把最新 fresh paper source 正式挂成 **`Rank 128 / MAX(5m) impulse confirmation tier`** 作为下一顺位 reserve

本轮已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小必要更新：
- 不改 Paper / Live verdict
- 只补当前 authoritative 的 Scout 排序与 `Next 3 bot3 runs`

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 工作区：`git status --short | wc -l = 1946`，继续很脏，不混提
- 最近 optimization logs：
  - `2026-03-20 17:18 UTC / Rank 126 clean replication -> park`
  - `2026-03-20 16:36 UTC / Rank 125 cost-trade stability -> keep_P1 / budget used`
  - `2026-03-20 16:06 UTC / Rank 125 clean replication`
- 最近 strategy review：
  - `2026-03-20 18:39 UTC`
  - `2026-03-20 16:43 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮 running
  - `bot3-momentum-auto-opt-13m`：enabled / 最近连续 timeout
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近运行成功
  - `bot7-quant-digest-30m`：enabled / 最近运行成功
  - `bot6-park-reframe-2h`：enabled / 最近 timeout
  - `Rank32b live maintenance`：enabled / 最近运行成功

### EMA due-check（本轮实际重跑）
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
返回要点：
- `EMA = waiting_not_due`
- `美股 1d+1wk（SPY/QQQ/AAPL） -> 约 38 分钟后到点`
- `Crypto 1d+1wk（BTC/ETH/SOL） -> 约 4.6 小时后到点`
- `创业板ETF 1d -> 约 59.6 小时后到点`
- `require-due` 下脚本以 `code 2` 退出，语义是：**当前没有 due-now / overdue lane，不应伪造 refresh**

### Hosted paper lanes 快照
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T19:08:58Z`
  - `new_closed_trades_appended = 0`
- `manual_narrow_paper_status.csv @ 2026-03-20T18:45:00Z`
  - 当前 open paper positions：
    - `Rank 17 / ETH-USD / long`
    - `Rank 17 / SOL-USD / short`
    - `Rank 29 / BTC-USD / short`
  - `Rank 2 / Rank 32b` 当前无 open position
- `Rank 122` 不在 manual-narrow csv 中，但独立 hosted artifacts 仍在，继续按：
  - **`P3 / strict-only / short-side re-arm / paper-only / recent-month red-watch`**

### 新鲜 source
- `research/quant_digests/2026-03-20_1908_max-impulse-ema-reclaim-confirmation-gate.md`
  - 这是本轮新增、且还未写入顶板排班的新鲜 paper-based 15m 候选
  - 进入 queue-facing 层前，已按顺序赋予新号：**`Rank 128`**

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
- 也不该在 `EMA = waiting_not_due` 时抢 bot3 默认主资源位

---

## 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
### 结论
**继续保持暂空。**

### 原因
1. `Rank 127` 还没做完第一轮 `source intake + 两条轻量诚实守门`
2. `Rank 128` 也只是 fresh paper source reserve，还没进 clean replication
3. `Rank 125` 当前是 **`keep_P1 / budget used`**，不够升到 live
4. `Rank 112 / Rank 111` 都还是 **`P1 evidence_pool / budget used`**
5. `Rank 122 / 2 / 17 / 29 / 32b` 虽在 `P3`，但都是 **paper-only hosted lanes**，不是 live challenger

### honest judgment
- **`P2` 仍空**
- **`P4` 仍空**
- 所以 **`Live Seat = 暂空`** 仍是最诚实写法

---

## 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
### 当前主资源位
1. **`Rank 127 / signal→confirm ATR delta phase gate`**
   - 来源：`ilahuerta-IA/backtrader-pullback-window-xauusd` + `2026-03-20 16:34 UTC` quant digest
   - 角色：给 `breakout-short / Fib retest_hold / EMA-PSAR` 补 **setup-specific confirm / veto** 候选
   - 当前状态：应先做 `source intake + 两条轻量诚实守门`

### 当前 fresh reserve（本轮新增写回）
2. **`Rank 128 / MAX(5m) impulse confirmation tier`**
   - 来源：`Yadav (2025)` + `2026-03-20 19:08 UTC` quant digest
   - 角色：更偏 **`Fib retest_hold / EMA reclaim` long-side continuation-confirmation 分层**，不默认 shared 到 `breakout-short`
   - 当前状态：fresh paper source reserve / 若 `Rank 127` hard-fail，则接棒做 source intake

### 当前仍留在 active Scout 比较表，但不再默认主推
3. **`Rank 125 / range location veto gate`**
   - verdict：`keep_P1 / budget used / 留样但不再默认续命`
4. **`Rank 112 / basis dislocation short veto`**
   - verdict：`P1 weak candidate / evidence_pool / budget used`
5. **`Rank 111 / abnormal-return event clock`**
   - verdict：`P1 evidence_pool / budget used`

### 已退出主资源位的近邻候选
6. `Rank 126 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
   - 统一视作 **`P0 / park / evidence pool`**

### 不应误写成 Scout 主资源的 hosted continuity
7. `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
   - 全部只按 **`P3 hosted paper continuity / sidecar only`** 处理

### 边际价值比较
- **为什么 `Rank 127` 仍排第一？**
  - 它还没消耗掉第一轮 cheap honest check
  - 它直接作用于三条主线共同面对的确认阶段质量问题
  - 下一手最关键的问题很明确：它是否只该作为 **setup-specific gate** 存在
- **为什么 `Rank 128` 暂时排第二？**
  - 它是新鲜、真实可用的 paper-based source
  - 但当前更像 `Fib / EMA reclaim` 的 long-side confirmation tier，scope 比 `Rank 127` 更窄
  - 它还带着明显的 `cost-survival` 问题，更适合做下一顺位 reserve，而不是立刻抢主位
- **为什么不是继续磨 `Rank 125 / 112 / 111`？**
  - 因为这三条都已经进入 `budget used / evidence_pool` 区
  - 继续补 admission wording 或近义说明页，不再减少真实 gate

---

## 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
### P1
- `Rank 127 / signal→confirm ATR delta phase gate`
  - **`P1`**（`fresh repo source intake / 两条轻量诚实守门 next`）
- `Rank 128 / MAX(5m) impulse confirmation tier`
  - **`P1`**（`fresh paper source intake reserve next`）
- `Rank 125 / range location veto gate`
  - **`P1`**（`keep_P1 / budget used / 留样但不再默认续命`）
- `Rank 112 / basis dislocation short veto`
  - **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock`
  - **`P1`**（`evidence_pool / budget used`）

### P0
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
   - 当前美股 lane 距 due 约 `38m`
   - 每一轮都先检查；若到点则先走 paper refresh，不得跳过

2. **Run 2 = Rank 127 / signal→confirm ATR delta phase gate 的 source intake + 两条轻量诚实守门**
   - 先冻结：
     - 它是不是 **setup-specific confirm/veto**，而不是 shared 单阈值
     - `trade on / trade off` 是否应拆成：`breakout_short mid-phase re-arm` / `fib_retest expanding confirm` / `ema_psar expansion veto`
     - `ATR delta` 只能来自 signal 当根及之前、已完成 bar 的 trailing 序列，禁止 future refill

3. **Run 3 = 条件分支**
   - 若 `Rank 127` guard-pass 且 `EMA` 仍 `waiting_not_due`：
     - 只给 **1 次最小 clean replication**，直接比较 `baseline / shared_gate / setup_specific_gate`
   - 若 `Rank 127` 当场 hard-fail / exhausted：
     - 立刻切 **`Rank 128 / MAX(5m) impulse confirmation tier`** 的 source intake + 两条轻量诚实守门
   - 只有 `Rank 128` 这一轮也 exhausted 后：
     - 才允许 `tiny-live plumbing fallback`

---

## 6. 为什么这轮要改 TODO 顶板
因为 `18:39 UTC` 之后，桌面事实有两点变化：
1. **bot3 这 40 分钟没有新的 Scout deliverable**，所以不能假装 `Rank 127` 已推进；
2. **`19:08 UTC` 新增了一条可用 fresh paper source**，若仍只写“fresh intake reserve”，就不够具体，也不符合当前要把下一顺位资源写死的 desk 纪律。

所以本轮最小必要更新是：
- 保持 `Paper Seat` 不动
- 保持 `Live Seat = 暂空`
- 保持 `Scout Seat = Rank 127`
- **补挂 `Rank 128` 为下一顺位 reserve**
- 把 `Run 3` 从泛泛“回 fresh reserve”改成更具体的：`127 fail -> 128 intake`

---

## 7. 本轮 reader-facing judgment 是否变化
**有变化。**
- 变化点不是 `Paper Seat` 或 `Live Seat`
- 变化点是：
  1. `Scout Seat` 的 active 排序更精确了：从 `127 > 125 > 112 > 111`，改成 **`127 > 128 > 125 > 112 > 111`**
  2. `Next 3 bot3 runs` 的 fallback 不再写成泛泛 fresh reserve，而是明确到 **`Rank 128`**

因此本轮已同步更新：
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`

---

## 8. 本轮后的 authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due，距美股 due 约 38m）`；`Live Seat = 暂空`；`Scout Seat = Rank 127 / signal→confirm ATR delta phase gate`；`Rank 128 / MAX(5m) impulse confirmation tier` 作为下一顺位 fresh reserve；`Rank 125 / 112 / 111` 继续只留在 P1 evidence pool，不回头续磨。