# 2026-03-18 23:21 UTC strategy review

## 轮次定位
- 时间：2026-03-18 23:21 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，回答当前 `Paper / Live / Scout` 三席与后续 `Next 3` 排班

## 开始前检查
### 1) repo 状态
- `git status --short` 显示工作区存在大量与本轮无关的已修改 / 未跟踪文件；本轮只做最小必要更新：`docs/TODO.md`、本轮 strategy review 日志、站点镜像刷新。
- 不做混提，不做清理。

### 2) 最近 optimization logs
- `2026-03-18_2253_rank70-source-intake.md`：`Rank 70 / fast-entry slow-exit handoff spine` 已完成 `source intake + 两条轻量诚实守门`，当时 verdict 为 `guard-passed / admit_to_clean_replication_queue`。
- `2026-03-18_2312_rank70-clean-replication-park.md`：`Rank 70` 最小 clean replication 已跑完，当前 hard verdict 已冻结为 **`park / evidence pool`**。
- 较近前序：`2026-03-18_2242_rank69-clean-replication-park.md`、`2026-03-18_2207_rank68-clean-replication-park.md`，都说明 `Rank 69 / 68` 已不再占默认主资源位。

### 3) 最近 strategy review
- 最近 review：`research/strategy_review/2026-03-18_2227_strategy-review.md`
- 上轮 desk 判断核心：
  - `Paper Seat = EMA`
  - `Live Seat = 暂空`
  - `Scout Seat` 回到 fresh source，比 `realized-vol mid-band cost-survival gate` 与 `PSAR close-confirmed follow-up gate`
- 本轮新增信息：`2026-03-18 23:18 UTC` 新 quant digest 已补入更高边际价值的新 repo-based fresh source，需要重排 Scout 顺序。

### 4) 当前 cron 列表
- `bot2-strategy-review-40m`：运行中，上一轮 `ok`
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，上一轮 `ok`，本轮新增 `2026-03-18_2318_ema-vwap-atr-volume-graded-admission-score.md`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，但上一轮 `error`，原因是脚本里调用 `rg` 失败（系统无 `rg`）
- 其余 quota email / 旧 bot4、monitor cron 不影响当前 desk 席位判断

## 关键证据
### Paper Seat / P3 continuity
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前没有新的 `due-now / overdue`
  - 最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `new_closed_trades_appended=0`
  - 说明当前没有新的 `P3 status-changing event`

### 新增 Scout 证据
- `research/quant_digests/2026-03-18_2318_ema-vwap-atr-volume-graded-admission-score.md`
  - 新 source：`bptrades/0dte-momentum-continuation`
  - 核心不是再发明一条主线，而是把 `EMA spread / ATR`、`VWAP distance / ATR`、`volume`、`ATR expansion` 收成一个 **graded admission score**
  - 这比继续围绕 `realized-vol mid-band` 或 `PSAR close-confirmed` 更直接服务当前 `EMA / PSAR raw alpha focus`

## 本轮 desk verdict
### 1) Paper Seat
- **`EMA` 继续坐 `Paper Seat`**
- 当前状态：**`running paper / due_soon / waiting_not_due`**
- 口径：当前只是市场时钟未到，不是 desk 空闲；因此 bot3 仍必须优先导流到 `Scout Seat`

### 2) Live Seat
- **继续保持 `暂空`**
- 原因：当前没有任何候选已完成到足以抢占 `Live Seat` 的层级；`Rank 71` 还没过 `source intake + guard`，`realized-vol` 与 `PSAR close-confirmed` 也都还只是 fresh-source queue

### 3) Scout Seat 当前候选与分级
- **`Rank 71 / EMA-VWAP-ATR-volume graded admission score`**
  - 分级：**`P1 weak candidate`**
  - 阶段：`fresh source intake / 两条轻量诚实守门 next`
  - 理由：当前 active fresh pool 里边际价值最高，直接服务 `EMA / PSAR raw alpha focus`
- **`realized-vol mid-band cost-survival gate`**
  - 分级：**`P0 fresh-source queue / not admitted`**
  - 阶段：`source intake pending`
  - 理由：paper-based、可测，但与已 park 的 volatility/state language 更相邻，暂排第二
- **`PSAR close-confirmed follow-up gate`**
  - 分级：**`P0 fresh-source queue / not admitted`**
  - 阶段：`source intake pending`
  - 理由：repo-based、规则清楚，但当前更像单轴 follow-up gate，优先级不如新的 graded score
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`**
  - 分级：**`P3 narrow paper continuity`**
  - 阶段：仅低频 refresh / monitoring / review 托管
  - 备注：本轮没有新的 status-changing event，不应抢占 bot3 默认主资源位
- **当前 `P2` 仍空，`P4` 仍空**

## 边际价值比较（本轮显式重排）
**`Rank 71 / EMA-VWAP-ATR-volume graded admission score` > `realized-vol mid-band cost-survival gate` > `PSAR close-confirmed follow-up gate` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**

### 为什么是这个顺序
- `Rank 70` 已在 23:12 UTC clean replication 后压回 `park`，不该继续霸占 fast lane
- `Rank 71` 是新的 paper/repo-based 15m crypto 候选，且不是泛研究，而是可直接落成最小实验的 **continuation graded admission layer**
- `realized-vol mid-band` 与 `PSAR close-confirmed` 都还没开始 queue-facing source intake；当前没有理由让它们越过更新鲜、且更贴 EMA/PSAR 主线的 `Rank 71`
- `P3 continuity` 当前没有 due-now / append / weekly-review / 明显异常，不应回头挤占默认资源

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
1. 在 `Scout Seat verdict` 区新增 `2026-03-18 23:21 UTC` desk review 补充
2. 把当前 active Scout 顺序改写为：
   - `Rank 71 / EMA-VWAP-ATR-volume graded admission score`
   - `realized-vol mid-band cost-survival gate`
   - `PSAR close-confirmed follow-up gate`
   - `Rank 35b > Rank 16b > tiny-live plumbing`
3. 明确分级：`Rank 71 = P1`，`realized-vol / PSAR close-confirmed = P0`，`P2/P4` 仍空
4. 在 `Next 3 bot3 runs` 顶部新增 `2026-03-18 23:21 UTC` 最新块

## 接下来 3 个 bot3 runs
1. **Run 1 = EMA due-check only**
2. **Run 2 = 若 EMA 仍 waiting_not_due，则先给 `Rank 71 / EMA-VWAP-ATR-volume graded admission score` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 Rank 71 已 `guard-passed` 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；若 Rank 71 直接 hard-fail / 未 admitted，则回到 fresh source 比较 `realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate`；只有 fresh source 这一层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## Reader-facing / publish
- 本轮 verdict / 排兵布阵已变化，因此不能只留 markdown 记录
- 已更新 `docs/TODO.md` 顶部作战板；接下来同步刷新 `reports/site/plans/momentum_todo.html` 与首页 index

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
