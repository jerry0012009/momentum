# 2026-03-19 01:46 UTC strategy review

## 轮次定位
- 时间：2026-03-19 01:46 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，明确当前 `Paper / Live / Scout` 三席与接下来 `Next 3 bot3 runs`

## 开始前检查
### 1) repo 状态
- `git status --short` 当前约 **1202** 条脏文件/未跟踪项，且绝大多数与本轮无关。
- 本轮只做最小必要更新：`docs/TODO.md` 顶部作战板、本轮 strategy review 记录、邮件摘要、首页 index 刷新。
- 不做混提，不做清理。

### 2) 最近 optimization logs
- `2026-03-19_0103_rank73-clean-replication.md`
  - `Rank 73 / PSAR close-confirmed follow-up gate` 已在唯一那手 minimal clean replication 后给出 **`park / evidence pool`**。
- `2026-03-19_0112_rank74-source-intake.md`
  - `Rank 74 / ADX+ER price-only trend-readiness gate` 已完成 `source intake + 两条轻量诚实守门`，一度进入 `guard-passed / admit_to_clean_replication_queue`。
- `2026-03-19_0140_rank74-clean-replication.md`
  - `Rank 74` 已在 minimal clean replication 后压回 **`park / evidence pool`**；局部改善主要来自砍单或只在单一 archetype 勉强成立。

### 3) 最近 strategy review
- 最近两轮 bot2 review：
  - `2026-03-19_0046_strategy-review.md`
  - `2026-03-19_0006_strategy-review.md`
- 上轮核心判断：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat` 在 `Rank 73 -> fresh source re-rank -> Rank 74` 之间切换。
- 本轮新增判断：`Rank 74` 也已 hard-park，当前更诚实的 fast-lane 头部应切到新的 fresh paper / repo source，而不是继续围着已 park 的 `Rank 72~74` 或回头挤占 `P3 continuity`。

### 4) 当前 cron 列表
- `bot2-strategy-review-40m`：启用，当前运行中，上一轮 `ok`
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，上一轮 `ok`
- 其余 quota / 旧 bot4 cron 不影响当前 seat judgment

## 当前关键证据
### Paper Seat / market clock
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 无 `due-now / overdue`
  - 最近 due 点：`A股三条 lane -> 2026-03-19 07:00 UTC`
  - 其后：`美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`

### P3 continuity
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - 最新仍是 `new_closed_trades_appended = 0`
  - 说明当前没有新的 `P3 status-changing event`
  - 现有 narrow-paper lanes 已由专属 cron 托管，不应再误写成 bot3 的默认主资源位

### Fresh source pool 重新比较
这轮重新比较当前 active Scout 候选的边际价值：
1. **`Rank 75 / GCR extreme-sentiment exhaustion veto`**（repo-based、5m/15m 兼容、直接服务三条主线的 shared failure veto、实现最便宜）
2. **`Rank 76 / intraday clock polarity + event blackout gate`**（paper-based、直接服务 continuation vs retest 时段极性，但首轮实现更重）
3. **`one-regime-per-session overlay`**（paper-based，但更像 desk-level allocation overlay，且与 `Rank 7b` 单轴 reframe 高度相邻）
4. `Rank 35b`
5. `Rank 16b`
6. `tiny-live plumbing`

## 本轮 desk verdict
### 1. 谁坐 `Paper Seat`？
- **`EMA` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 口径：最新 due guardrail 仍显示最近 due 点是 `A股 07:00 UTC`，所以这是 market-clock waiting，不是 desk 空闲。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 72 / 73 / 74` 都已在允许预算内给出 **`park / evidence pool`**；
  2. 新的 `Rank 75 / 76` 还没走到 `source intake` 之后，更没有 `clean replication / Light Stability Pack`；
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active fast-lane 主资源位**：
  - `Rank 75 / GCR extreme-sentiment exhaustion veto`
  - `Rank 76 / intraday clock polarity + event blackout gate`
- **当前只保留为 evidence / backlog，不抢默认 fast-lane**：
  - `one-regime-per-session overlay`
- **仅当 fresh source 本轮也 exhausted 时才允许进入 fallback**：
  - `Rank 35b`
  - `Rank 16b`
- **明确不该继续霸占 fast-lane 的对象**：
  - `Rank 72 / 73 / 74`：都已 `park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 75 / GCR extreme-sentiment exhaustion veto` → **`P0`**（`fresh-source queue / source intake next`）
- `Rank 76 / intraday clock polarity + event blackout gate` → **`P0`**（`fresh-source queue / source intake next`）
- `one-regime-per-session overlay` → **`P0 evidence/backlog`**（`暂不进入默认 fast-lane`）
- `Rank 72 / 73 / 74` → **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper continuity / low-frequency health check only`）
- 当前 **`P1` 暂空、`P2` 暂空、`P4` 暂空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 继续盯 due guardrail；若仍 `waiting_not_due`，不得空转。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则给 `Rank 75 / GCR extreme-sentiment exhaustion veto` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 `Rank 75` 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 `Rank 75` 直接 hard-fail / 未 admitted，则立刻切到 `Rank 76 / intraday clock polarity + event blackout gate` 做 fresh source intake；只有 fresh source 这一层也 exhausted 时，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 为什么是这个顺序
- `Rank 75` 比 `Rank 76` 更 queue-facing、更便宜，也更直接服务当前 desk 缺的 shared failure veto；
- `Rank 76` 值得保留为下一手，因为它直接回答“当前时段更像 continuation 还是 retest”，但实现上比 `Rank 75` 更重；
- `one-regime-per-session overlay` 与 `Rank 7b` 高度相邻，当前更适合作为 backlog/evidence，而不是在 fresh source 仍有更便宜对象时抢 fast lane；
- 当前没有任何真实 `due-now / overdue` 的 `Paper Seat` refresh，也没有新的 `P3 status-changing event`，因此 bot3 不应回头挤占 continuity 预算。

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
1. 新增 `2026-03-19 01:46 UTC` 的 bot2 desk-review 块；
2. 明确 `Rank 74` 已 `park / evidence pool`，不再写成 active Scout 头部；
3. 正式冻结新的 queue-facing 顺序 Rank：
   - `Rank 75 / GCR extreme-sentiment exhaustion veto`
   - `Rank 76 / intraday clock polarity + event blackout gate`
4. 收紧 `Next 3 bot3 runs` 为：
   - `EMA due-check only`
   - `Rank 75 source intake`
   - `Rank 75 clean replication / failover to Rank 76 source intake`

## Reader-facing / publish
- 本轮 verdict / 排兵布阵有变化：`Rank 74` 退出 active Scout 头部，新的 fresh-source 队首切到了 `Rank 75 / 76`。
- 已把变化写回 `docs/TODO.md` 顶板；接下来刷新首页 index。

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
