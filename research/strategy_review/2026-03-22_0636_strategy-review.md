# Strategy Review (bot2) — 2026-03-22 06:36 UTC

## 本轮一句话判断
`Paper Seat(EMA)` 继续保持 `running paper pilot / waiting_not_due`；`Live Seat` 继续暂空；bot3 资源按既定顺序走：先做 EMA due-check，其次做 Rank139(P3) 的 hosted narrow paper pilot 健康检查（只做 1 件事），最后只对 `pbo-cscv/deflated sharpe` 做 1 个小交付（source intake 或最小实现）。

## 1) 本轮检查清单（硬性）
- **repo 状态**：git 有大量 untracked 产物（多为 reports/artifacts、reports/site 生成物、tmp、memory 日志等）；HEAD= `fce2dd7 Avoid immediate flatten when exchange stop attach fails`。
- **最近 optimization_loop**（Top 5）：
  - `2026-03-22_0344_rank139-health_pbo-cscv-source-intake.md`
  - `2026-03-22_0253_bot3-rank139-health_pbo-source-intake.md`
  - `2026-03-22_0240_rank139-health_pbo-cscv-intake.md`
  - `2026-03-22_0227_rank139-p3-healthcheck.md`
  - `2026-03-22_0146_bot3-fresh-intake-pbo-cscv.md`
- **最近 strategy_review**：最新到 `2026-03-22_0356_strategy-review.md`。
- **当前 cron 列表**：
  - 使用 OpenClaw tool `cron list` 可正常读取（CLI `openclaw cron list` 本轮报 gateway closed）；关键 job 状态：
    - `bot2-strategy-review-40m`：lastRunStatus=error（delivery JSON parse），本轮正在运行。
    - `bot3-momentum-auto-opt-13m`：上一轮 timeout（需关注是否频繁超时）。
    - `momentum-narrow-paper-lanes-20m`：最近 ok（持续跑）。

## 2) TRADING DESK BOARD 校准（只做最小必要更新）
- 已核对 `docs/TODO.md` 顶部 TRADING DESK BOARD：**本轮无需改动**（席位/Active Scout/Next 3 bot3 runs 与最近 evidence 一致）。

## 3) Seat / Lane 明确结论（回答题目要求）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted / family lanes**：
  - 美股 `1d+1wk（SPY/QQQ/AAPL）`
  - Crypto `1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d`（shadow_watch）

### Live Seat
- **是否空**：`暂空`（keep empty；等待 scout 升格胜者再填）

### Scout Seat
- **当前复刻/主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`（当前定位=P3 hosted narrow paper pilot）
- **目标**：低频健康检查维持可见性（ledger/monitoring/refresh 口径），避免继续同义研究磨损。

### Scout 候选分档（P0~P4）
- **P3（narrow paper pilot / hosted lanes）**：
  - 主点：`Rank 139`
  - sidecar hosted：`Rank 2 / 17 / 29 / 32b`（20m refresh running）
  - sidecar（非 20m lane）：`Rank 122`（low-frequency monitoring only）
- **P2（paper candidate）**：本轮无新增（当前板面 P2=空）。
- **P1（weak candidate / 仅 1 次便宜诚实检查预算）**：
  - `pbo-cscv / deflated sharpe honesty gate`（new intake；不与 rank 线抢 seat）
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0（park / evidence pool）**：
  - `Rank 138`、`Rank 127`、`Rank 137` 以及其他已 park 的号段（见 TODO 顶板）。
- **P4（tiny-live review candidate）**：当前无。

## 4) Next 3 bot3 runs（排班确认）
1. **Run 1**：EMA due-check first（若 due-now/overdue → 先 paper refresh；若 waiting_not_due → 立刻切 Run2，不得空转）
2. **Run 2**：`Rank 139 (P3)` hosted narrow paper pilot **低频健康检查（只做 1 件事）**：确认 ops page/CSV 持续更新；重点盯 `no_event_timeout`、retention、mean_net@6bps 是否出现爆雷。
3. **Run 3**：只选 1 个小交付（当前：`pbo-cscv honesty gate`）——二选一：
   - `source intake`：锁定 1 篇权威参考 + 人话摘要；或
   - `minimal implementation`：给 scout scorecard 加 `deflated_sharpe / pbo_risk_flag` 1 列。

## 5) strongest evidence / weakest line
- **strongest evidence**：Rank139 已完成最小对比与 scorecard，并已落地 monitoring board + ops page（已进入“可运行监控”阶段）。
- **weakest / should-park pressure**：P1 候选里（Rank125/112/111）多条已标注 budget used；若后续没有能改变级别的新证据，应继续向 P0 收口，避免占 seat。

## 6) 风险与不确定性
- `openclaw cron list` CLI 本轮 gateway closed，但 tool `cron list` 可用；建议后续单独排查 gateway CLI 连接稳定性（不在本轮扩大）。
- bot3 13m loop 最近一次 timeout：若连续发生，可能需要缩小单轮任务体量（更严格 1 主点 + 1 子点）。
