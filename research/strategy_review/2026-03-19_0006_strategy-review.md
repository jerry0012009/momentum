# 2026-03-19 00:06 UTC strategy review

## 轮次定位
- 时间：2026-03-19 00:06 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，明确当前 `Paper / Live / Scout` 三席与接下来 `Next 3 bot3 runs`

## 开始前检查
### 1) repo 状态
- `git status --short --branch` 仍显示工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件。
- 本轮只做最小必要更新：`docs/TODO.md`、本轮 strategy review 记录、邮件摘要、站点镜像刷新。
- 不做混提，不做清理。

### 2) 最近 optimization logs
- `2026-03-18_2345_rank71-clean-replication-park.md`
  - `Rank 71 / EMA-VWAP-ATR-volume graded admission score` 已完成唯一那手 minimal clean replication。
  - hard verdict 已冻结为 **`park / evidence pool`**。
- `2026-03-19_0002_ema-crypto-refresh-append.md`
  - `Paper Seat / EMA` 已在真实 due window 完成 crypto lane refresh。
  - `Crypto 1d+1wk` 已从 `2026-03-19 00:00 UTC` 推到 `2026-03-20 00:00 UTC`。
- 因此当前 desk 读法不该再把 `Rank 71` 写成 active Scout 头部，也不该再把 crypto lane 写成 due-soon 未处理。

### 3) 最近 strategy review
- 最近两轮 bot2 review：
  - `2026-03-18_2321_strategy-review.md`
  - `2026-03-18_2227_strategy-review.md`
- 上轮核心判断：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat` 先给 `Rank 71`，其后比较 `realized-vol mid-band > PSAR close-confirmed`。
- 本轮新增信息：`Rank 71` 已在 23:45 UTC 如实 park；`00:02 UTC` 的 EMA crypto due refresh 已真实消化。

### 4) 当前 cron 列表
- `bot2-strategy-review-40m`：运行中，上一轮 `ok`
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，但上一轮 `error`（`publish_report_site.sh` 走 elevated 失败）；不过 `2026-03-18_2354_one-regime-per-session-overlay.md` 已落盘，可作为证据池线索
- quota email 类 cron 不影响当前 desk 席位判断

## 当前关键证据
### Paper Seat / market clock
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 无 `due-now / overdue`
  - 下一次最早 due 点：`A股三条 lane -> 2026-03-19 07:00 UTC`
  - 其后：`美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`

### P3 continuity
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T00:05:52Z`
  - `new_closed_trades_appended = 0`
  - 说明当前没有新的 `P3 status-changing event`

### Scout 候选边际价值
- `realized-vol mid-band cost-survival gate`
  - paper-based，共享 allow/deny gate，直接服务 `breakout-short / Fib / EMA-PSAR`
  - 当前更像先回答“哪些 vol pocket 根本不该做”
- `PSAR close-confirmed follow-up gate`
  - repo-based，规则清楚，直接服务 `EMA / breakout-short`
  - 但更偏单轴 follow-up gate，当前边际价值低于 shared realized-vol gate
- `one-regime-per-session overlay`
  - 新 digest 值得记住，但更像 desk-level allocation overlay
  - 当前不该跳过两条更窄、更便宜的 queue-facing 15m gate 直接抢 fast lane

## 本轮 desk verdict
### 1. 谁坐 `Paper Seat`？
- **`EMA` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 口径：`00:02 UTC` 的 crypto due window 已真实消化完毕；当前最早下一次 due 点已经切到 `A股 07:00 UTC`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 71` 已在 minimal clean replication 后压回 `park / evidence pool`；
  2. 当前最靠前的两条 fresh source（本轮正式冻结为 `Rank 72 / Rank 73`）都还没走到 `source intake` 之后，更谈不上 `clean replication / Light Stability Pack`；
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active fast-lane 主资源位**：
  - `Rank 72 / realized-vol mid-band cost-survival gate`
  - `Rank 73 / PSAR close-confirmed follow-up gate`
- **暂不进入默认 fast-lane 的线索**：
  - `one-regime-per-session overlay`：保留为 evidence / backlog，不直接跳进当前 queue-facing replication
- **明确不该继续霸占 fast-lane 的对象**：
  - `Rank 71`：已 `park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 72 / realized-vol mid-band cost-survival gate` → **`P0`**（`fresh-source queue / source intake next`）
- `Rank 73 / PSAR close-confirmed follow-up gate` → **`P0`**（`fresh-source queue / source intake next`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper continuity / low-frequency health check only`）
- 当前 **`P1` 暂空、`P2` 暂空、`P4` 暂空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 盯住最新 due guardrail；若仍是 `waiting_not_due`，不得空转。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则先给 `Rank 72 / realized-vol mid-band cost-survival gate` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 `Rank 72` 已 `guard-passed` 且 EMA 仍 waiting_not_due，则立刻给它 `1` 次最小 clean replication；若 `Rank 72` 直接 hard-fail / 未 admitted，则立刻切到 `Rank 73 / PSAR close-confirmed follow-up gate` 做 source intake；只有 fresh source 这一层也 exhausted，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 边际价值比较（本轮显式重排）
**`Rank 72 / realized-vol mid-band cost-survival gate` > `Rank 73 / PSAR close-confirmed follow-up gate` > `one-regime-per-session overlay（evidence only）` > `Rank 35b` > `Rank 16b` > `tiny-live plumbing`**

### 为什么是这个顺序
- `Rank 71` 已 park，不该继续霸占 fast lane
- `Rank 72` 比 `Rank 73` 更像共享生存门，覆盖三条主线更广，且当前最需要先回答的是“哪些 vol pocket 根本不该做”
- `Rank 73` 规则清楚、值得做，但仍更像单轴 follow-up gate
- `one-regime-per-session overlay` 目前更像 desk-level allocation overlay；若直接抢在两条更窄的 15m gate 前面，会把 Scout Seat 再次拉宽成泛研究入口
- `P3 continuity` 当前没有 due-now / append / review need，不应回头抢主资源

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
1. 在 `Scout Seat verdict` 区新增 `2026-03-19 00:06 UTC` desk review 补充
2. 正式把当前两条 queue-facing fresh source 冻结为：
   - `Rank 72 / realized-vol mid-band cost-survival gate`
   - `Rank 73 / PSAR close-confirmed follow-up gate`
3. 明确当前分级：`Rank 72 = P0`、`Rank 73 = P0`、`P1/P2/P4` 暂空、`Rank 2/17/29/32b = P3`
4. 在 `Next 3 bot3 runs` 顶部新增 `2026-03-19 00:06 UTC` 最新块，把当前三轮排班收紧为：
   - `EMA due-check only`
   - `Rank 72 source intake`
   - `Rank 72 clean replication / failover to Rank 73 source intake`

## Reader-facing / publish
- 本轮 verdict / 排兵布阵有变化，不能只留 markdown 记录。
- 已把变化写回 `docs/TODO.md` 顶板，并将同步刷新：
  - `reports/site/plans/momentum_todo.html`
  - `reports/site/plans/index.html`
  - 首页 index

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
