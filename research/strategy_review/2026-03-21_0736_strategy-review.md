# 2026-03-21 07:36 UTC strategy review

## 本轮一句话判断
当前 desk 继续应写成：**`Paper Seat = EMA / 创业板ETF 1d（active_primary）/ waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 139 / CUSUM event-bar confirm-veto gate（P1 / source intake + 两条轻量诚实守门）`**。`Rank 127` 已在 07:12 UTC 完成最后一轮 cheap time-stability 检查并降为 `P0 / park`；hosted `P3` lanes 仍只做 continuity 托管，不应抢 bot3 主资源位。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：大量历史脏文件与未跟踪产物仍在；本轮不适合 selective commit
- 最近 optimization logs：
  - `2026-03-21_0713_rank127-time-stability-park.md`
  - `2026-03-21_0636_rank138-clean-replication-park.md`
  - `2026-03-21_0444_rank138-source-intake.md`
  - `2026-03-21_0429_rank137-time-stability-park.md`
- 最近 strategy reviews：
  - `2026-03-21_0659_strategy-review.md`
  - `2026-03-21_0435_strategy-review.md`
  - `2026-03-21_0158_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 当前运行中
  - `bot3-momentum-auto-opt-13m`：enabled / 最近成功
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近带 1 次 error（`rg` 不存在），但不影响当前 desk seat 判断
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### EMA due 守门（07:36 UTC 实跑）
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 仍是：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前状态：`waiting_not_due`
- 距下一次真实 completed bar：约 `16.4h`
- 结论：`Paper Seat` 继续是**被 market clock 合法阻塞**，不是执行停滞；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流

### hosted narrow paper lanes 最新快照（07:17 UTC refresh）
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T07:17:54Z`
- `new_closed_trades_appended = 0`
- 当前真正挂在 `20m refresh` 上跑的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `Rank 122` 仍是 `P3 / strict-only sidecar`，但**不在当前 running hosted refresh lane 集合里**

### active Scout 池 / fresh source
已核对：
- `research/optimization_loop/2026-03-21_0713_rank127-time-stability-park.md`
- `research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 当前 cron 列表

结论：
- `Rank 127` 已经完成最后预算内 cheap check，当前 authoritative verdict 就应是 `P0 / park`
- `Rank 139` 现在是唯一最合理的 Scout 主资源位：先做 `source intake + trade on/off + no leakage` 两条轻量诚实守门
- `Rank 125 / 112 / 111` 继续只是旧 `P1 evidence pool / budget used`，当前边际价值低于 `Rank 139`

### memory 检索
- 已执行 `memory_search`
- 返回的更多是更早的 momentum / desk 背景；本轮实际席位判断仍主要由 repo 内最新 `TODO`、`optimization_loop`、EMA due-check 与 manual narrow paper artifacts 支撑

---

## 1. 本轮对 `TRADING DESK BOARD` 的最小同步
这轮**没有改席位 verdict**，只做了 freshness sync：
1. 把 `Hosted P3 快照` 的最近 refresh 从 `06:40 UTC` 更新到 `07:17 UTC`
2. 把 open positions 可见快照从 `06:15/06:40` 更新到 `07:00/07:17`
3. 把 `最近关键 evidence` 里的 EMA due-check 更新到 `07:36 UTC / 16.4h`
4. 把 manual narrow paper evidence 更新到 `07:17 UTC`

所以：**reader-facing judgment 没变，authoritative board 只是刷新到当前时点。**

---

## 2. 当前 strongest evidence
1. **`Paper Seat` 仍然是 clock-blocked，不是 execution-blocked。**
   - 07:36 UTC `require-due` 实跑再次确认：没有 `due-now / overdue`
   - 所以 bot3 最不该做的是伪 refresh，或回流 hosted `P3 continuity`
2. **`Rank 127` 已经完成最后一轮预算内 cheap honesty check，并给出 `park`。**
   - 07:13 UTC log 已明确：shared uplift 主要集中在 `2026-02`，到 `2026-03` 已转负
   - 这条线已经不该继续卡在 `P1`
3. **`Rank 139 / CUSUM event-bar confirm-veto gate` 已经足够成为新的 Scout 主点。**
   - 它直接服务 breakout-short / Fib / EMA-PSAR 共同缺的 `event-confirm / veto` 层
   - 当前应先做 `source intake + 两条轻量诚实守门`，而不是继续磨旧 `P1`
4. **hosted `P3` 仍然只是托管 continuity。**
   - 07:17 UTC refresh 仍无 `new_closed_trades_appended`
   - open paper position 仍只有 `Rank 17` 两腿
   - `Rank 122` 仍只是 strict-only sidecar，不是 running hosted lane

---

## 3. 本轮必须回答的 5 个问题
### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d（active_primary）`。**

#### EMA family lanes
- `创业板ETF 1d`（`active_primary`）
- `Crypto 1d+1wk（BTC/ETH/SOL）`（`active_secondary_backstop`，当前最靠前、但仍 `waiting_not_due`）
- `美股 1d+1wk（SPY/QQQ/AAPL）`（`active_secondary_backstop`）
- `贵州茅台 1d+1wk`（`active_secondary_backstop`）
- `沪深300ETF 1d`（`shadow_watch`）

#### 当前 running hosted paper lanes
- 真正挂在当前 `20m refresh` 上跑的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `Rank 122` 可算 `P3 hosted sidecar`，但**不在当前 running hosted refresh lane 集合里**，更准确读法仍是 `strict-only / low-frequency monitoring only`

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有已完成 fast-screen 且值得进 `tiny-live review` 的 `P2/P4` 候选
- `Rank 127` 已从最后 cheap check 直接压回 `P0 / park`
- `Rank 139` 还只在 `P1 / source intake + honesty guards` 阶段
- hosted `P3` lanes 是 paper continuity / sidecar，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 139 / CUSUM event-bar confirm-veto gate`**
  - 当前阶段：`P1 / source intake + 两条轻量诚实守门`
  - 角色：更像 breakout-short / Fib / EMA-PSAR 共用的 `event-confirm / veto` 层，而不是新主 alpha

#### 当前仍在比较池、但不该抢主资源的旧 P1
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

一句话：**当前真正应被 bot3 继续复刻推进的 Scout 候选只有 `Rank 139`；旧 `P1` 只是比较池，不应一起铺开。**

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 139`：`P1（fresh paper candidate / source intake + honesty guards）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
- `Rank 127`：`P0（park / 最后 1 次 cheap time-stability check 已完成）`
- `Rank 138`：`P0（park / minimal clean replication completed / single-pocket dependency）`
- `Rank 137`：`P0（park / minimal time-stability verdict completed / single-pocket dependency + post-cost collapse）`
- `Rank 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3（hosted narrow paper lanes / 20m refresh running / continuity only）`
- `Rank 122`：`P3（strict-only / hosted sidecar / low-frequency monitoring only）`

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍 `waiting_not_due`，立即切走，不得空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 139 / CUSUM event-bar confirm-veto gate` 的 `source intake + 两条轻量诚实守门`**
   - 输出必须收紧成：`keep_P1 / admit_to_clean_replication_queue / park`
   - 不做泛研究扩写

3. **Run 3 = 条件分支，但仍先服务 Scout Seat**
   - 若 `Rank 139` guard-pass：给 **1 次最小 clean replication**
   - 若 `Rank 139` 直接 park 或 source exhausted：按 `fresh intake > tiny-live plumbing` 顺序认领下一条高边际值新 source
   - 只有 `Scout` 侧也真实 exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback

---

## 4. Active Scout 边际价值比较
### 为什么主资源现在应该给 `Rank 139`
- `Rank 127` 已经完成最后预算内 cheap check，并给出 `park`
- `Rank 139` 是当前唯一既新鲜、又明确服务三条主线共同缺口的 fresh intake
- 它符合当前约束：**paper / repo based、5m/15m crypto、先过硬门槛再分级**

### 为什么不是继续磨旧 `P1`
- `Rank 125 / 112 / 111` 继续磨下去，当前更像补说明或延续旧 evidence pool
- 它们现在都缺少比 `Rank 139` 更强的“会改变 verdict 的下一步”

### 为什么不是回 `P3 continuity`
- 07:17 UTC hosted refresh 没有新的 `status-changing event`
- narrow-paper 已有独立 `20m refresh` cron 托管
- `Rank 122` 也只是 strict-only sidecar，不是当前 desk 的新主位

---

## 5. 本轮结论（authoritative one-liner）
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 139（P1 / source intake + honesty guards）`；当前 running hosted paper lanes 仍是 `Rank 2 / 17 / 29 / 32b`，open paper positions 仍只剩 `Rank 17 / ETH long + SOL short`；因此接下来 bot3 应按 `EMA due-check -> Rank 139 source intake + honesty guards -> 若 guard-pass 再做最小 clean replication` 排，而不是回头磨 `Rank 127` 或把 hosted `P3` continuity 误当主资源位。
