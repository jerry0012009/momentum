# 2026-03-19 02:26 UTC strategy review

## 轮次定位
- 时间：2026-03-19 02:26 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，明确当前 `Paper / Live / Scout` 三席与接下来 `Next 3 bot3 runs`

## 开始前检查
### 1) repo 状态
- `git status --short --branch` 显示当前仍在 `master`。
- `git status --short | wc -l` 当前约 **1230** 条脏文件/未跟踪项，绝大多数与本轮无关。
- 本轮继续只做最小必要改动：`docs/TODO.md` 顶部作战板、本轮 strategy review 记录、首页 index 刷新、邮件摘要发送。

### 2) 最近 optimization logs
- `2026-03-19_0140_rank74-clean-replication.md`
  - `Rank 74 / ADX+ER price-only trend-readiness gate` 已在唯一那手 minimal clean replication 后给出 **`park / evidence pool`**。
- `2026-03-19_0153_rank75-gcr-source-intake.md`
  - `Rank 75 / GCR extreme-sentiment exhaustion veto` 已完成 `source intake + 两条轻量诚实守门`，一度进入 `guard-passed / admit_to_clean_replication_queue`。
- `2026-03-19_0222_rank75-clean-replication.md`
  - `Rank 75` 已在 minimal clean replication 后压回 **`park / evidence pool`**；局部改善主要来自 `ema_psar_long` 的局部修正或大幅砍单，不够支撑 shared veto 升格。

### 3) 最近 strategy review
- 最近 bot2 review：
  - `2026-03-19_0146_strategy-review.md`
  - `2026-03-19_0006_strategy-review.md`
- 上一轮核心判断是：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat` 头部从 `Rank 74` 切到 `Rank 75 / Rank 76`。
- 本轮新增判断：`Rank 75` 也已 hard-park，因此当前更诚实的 queue-facing 头部应切到 **`Rank 76 / intraday clock polarity + event blackout gate`**，而不是继续围着已 park 的 `Rank 72~75` 打转。

### 4) 当前 cron 列表
- `bot2-strategy-review-40m`：启用，当前运行中，上一轮 `ok`
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，上一轮 `ok`
- 其余 quota / 旧 bot4 cron 不改变当前 seat judgment

## 当前关键证据
### Paper Seat / market clock
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 仍无 `due-now / overdue`
  - 最近 due 点：`A股三条 lane -> 2026-03-19 07:00 UTC`
  - 之后是：`美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`
- 结论：`EMA` 当前是**真实 market-clock waiting_not_due**，不是 desk 空闲。

### P3 continuity
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T02:26:30Z`
  - `new_closed_trades_appended = 0`
- 结论：当前没有新的 `P3 status-changing event`；`Rank 2 / 17 / 29 / 32b` 继续只是托管位，不应抢占 bot3 默认主资源。

### Active Scout 候选边际价值重排
本轮必须显式比较当前 active Scout 候选，而不是默认继续磨旧 rank：
1. **`Rank 76 / intraday clock polarity + event blackout gate`**
   - paper-based，直接服务 `breakout-short / Fib retest_hold / EMA-PSAR`
   - 更像 shared `session polarity / event blackout` gate，当前最贴主线
2. **`one-regime-per-session overlay`**
   - 逻辑相关，但更像 desk-level allocation overlay
   - 还不如 `Rank 76` 那么 queue-facing、那么便宜
3. `Rank 35b`
4. `Rank 16b`
5. `tiny-live plumbing`

## 本轮 desk verdict
### 1. 谁坐 `Paper Seat`？
- **`EMA` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 口径：最近 due 点仍是 `A股 07:00 UTC`，所以这是 `market clock blocked`，不是 desk 空闲。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 72 / 73 / 74 / 75` 都已在允许预算内给出 **`park / evidence pool`**；
  2. `Rank 76` 还没开始 `source intake`，更没有 `clean replication / Light Stability Pack`；
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active fast-lane 主资源位**：
  - `Rank 76 / intraday clock polarity + event blackout gate`
- **当前仍保留为下一手 paper-based 证据 / backlog**：
  - `one-regime-per-session overlay`
- **仅当 fresh source 这一层也 exhausted 时才允许进入 fallback**：
  - `Rank 35b`
  - `Rank 16b`
- **明确不该继续霸占 fast-lane 的对象**：
  - `Rank 75 / 74 / 73 / 72`：都已 `park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 76 / intraday clock polarity + event blackout gate` → **`P0`**（`fresh-source queue / source intake next`）
- `one-regime-per-session overlay` → **`P0`**（`evidence / backlog`）
- `Rank 75 / 74 / 73 / 72` → **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper continuity / low-frequency health check only`）
- 当前 **`P1` 暂空、`P2` 暂空、`P4` 暂空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 继续盯 due guardrail；若仍 `waiting_not_due`，不得空转。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则给 `Rank 76 / intraday clock polarity + event blackout gate` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 `Rank 76` 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 `Rank 76` 直接 hard-fail / 未 admitted，则继续按 7.10 从 fresh paper / repo source 比较 `one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source`；只有 fresh source 这一层也 exhausted 时，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 为什么是这个顺序
- `Rank 76` 比 `one-regime-per-session overlay` 更 queue-facing，也更像当前 desk 缺的 shared `时段极性 + 事件黑名单` gate；
- `one-regime-per-session overlay` 依然值得留作下一手 paper-based 线索，但它更像 allocation / session routing overlay，不该在 `Rank 76` 尚未 intake 前先抢默认 fast lane；
- `Paper Seat` 当前并没有真实 due-now 动作，`P3` 也没有 status-changing event，所以 bot3 不应回头挤占 continuity 预算。

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
1. 新增 `2026-03-19 02:26 UTC` 的 bot2 desk-review 补充；
2. 明确 `Rank 75` 已压回 `P0 park / evidence pool`；
3. 把新的 queue-facing 主资源位切到 `Rank 76 / intraday clock polarity + event blackout gate`；
4. 刷新 `Next 3 bot3 runs` 为：
   - `EMA due-check only`
   - `Rank 76 source intake`
   - `Rank 76 clean replication / failover to fresh source re-rank`

## Reader-facing / publish
- 本轮 verdict / 排兵布阵有变化：`Rank 75` 退出 active Scout 头部，新的 fresh-source 队首切到 `Rank 76`。
- 已把变化写回 `docs/TODO.md` 顶板；接下来刷新首页 index。

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
