# 2026-03-21 17:51 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat(EMA)` 仍处于 **running paper pilot / waiting_not_due**，因此本轮 desk 主资源应继续投向 **Scout Seat 的 Rank 139 最小 clean replication**；同时需要优先修复 **bot3 13m cron 持续 timeout/auth**（否则排班无法落地）。

## repo / 系统状态快照
- git: 工作区大量未跟踪产物（reports/artifacts/site 输出 + tmp/venv 等）；本轮不做清理与提交。
- 关键风险信号：
  - `bot3-momentum-auto-opt-13m` 连续 `timeout/auth`（cron 列表显示 consecutiveErrors=11）。
  - `bot7-quant-digest-30m` 也连续 `timeout/auth`（consecutiveErrors=11）。
  - `bot2-strategy-review-40m` 自身也多次 timeout（consecutiveErrors=9）。
- 20m hosted narrow paper lanes 刷新任务 `momentum-narrow-paper-lanes-20m` 最近一次 OK。

## 最近 evidence（只挑真正影响排兵布阵的）
1. `docs/TODO.md` 顶板显示：EMA `require-due fast-precheck` 近期确认无 due-now/overdue lane，合法切去 Scout。
2. `Rank 139 / CUSUM event-bar confirm-veto gate` 已完成 source intake + 两条轻量守门（trade on/off + no leakage），进入 **admit_to_clean_replication_queue**。
3. Hosted P3 lanes：当前 open inferred 主要仍在 `Rank 17`（ETH long + SOL short），其他 hosted lanes 大多 flat；因此它们继续只算 sidecar continuity。
4. cron 侧证据：bot3/bot7 的持续失败意味着“Next 3 bot3 runs”无法按计划执行，必须把 **恢复 bot3 可持续运行** 作为隐含 P0 blocker。

## Seat / Lane 明确结论（desk head）
### Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Hosted lanes（family lanes）**：`美股 1d+1wk（SPY/QQQ/AAPL）`、`Crypto 1d+1wk（BTC/ETH/SOL）`、`贵州茅台 1d+1wk`、`沪深300ETF 1d (shadow_watch)`

### Live Seat 是否空？
- **Live Seat = 暂空**（继续保持空位，直到有 Scout 候选通过基础快筛且接近 paper/tiny-live gate）。

### Scout 复刻对象（当前主点）
- **Rank 139 / CUSUM event-bar confirm-veto gate**
  - 目标：做 **1 次最小 clean replication**，回答它是否稳定改善 post-cost expectancy / retention / failure（same_dir_first / opp_dir_first / no_event_timeout 三分桶）。

## 候选分档（P0~P4）
> 本轮以 TODO 顶板为准，列出仍 relevant 的 desk 视角分档。

- **P4（tiny-live review candidate）**：无（当前无候选满足升格标准）
- **P3（narrow paper pilot / hosted lanes / low-frequency continuity）**：
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh running，sidecar only）
  - `Rank 122`（strict-only short-side re-arm，低频监控 sidecar）
- **P2（paper candidate）**：无（目前没有明确 promote 到 paper candidate 的新 scout）
- **P1（weak candidate，仅允许 1 次便宜诚实检查）**：
  - `Rank 139`（当前 active）
  - `Rank 125`（range location veto gate）
  - `Rank 112`（basis dislocation short veto，budget used）
  - `Rank 111`（abnormal-return event clock，budget used）
- **P0（park / evidence only）**：
  - `Rank 138`、`Rank 127`、`Rank 137` 及 130+ 多数条目（single-pocket dependency / post-cost collapse / time-stability fail 等原因已在各自日志中给出）。

## Next 3 bot3 runs（排班）
> 默认沿用 TODO 顶板（authoritative），但补充一个“先修复能跑”的隐含前置条件。

1. **Run 1：EMA due-check first**（若出现 due-now/overdue → 先做 paper refresh）
2. **Run 2：若 EMA 仍 waiting_not_due → Rank 139 最小 clean replication**
3. **Run 3：条件分支**
   - Rank 139 过关：给 promote/park 的硬结论（promote_P2 / promote_P3 / keep_P1）
   - Rank 139 失败或 source exhausted：按 `fresh intake > tiny-live plumbing` 切下一条

## 我这轮改了什么
- 本轮 **不改 `docs/TODO.md` 顶板**（当前席位/排班/证据槽位已经是最新且足够清晰）。

## 网页 / 表达建议
- 首页与 desk board 已经把“EMA waiting_not_due 仍必须切 Scout”讲清楚；下一步更重要的是让 **bot3 恢复可执行**，否则网页只会停留在规划层。

## cron / 节奏建议（最小干预）
- 观察到 bot2/bot3/bot7 多个 job 连续 timeout/auth：
  - **优先级最高**：恢复 bot3 13m 执行链路（token/auth、timeout、或模型侧 rate limit）；
  - 在恢复前，不建议继续加大 bot7/bot6 的并发强度（会进一步挤占可用配额/时延）。

## 风险与不确定性
- 当前最大不确定性不是策略优劣，而是 **执行循环是否能稳定跑起来**（cron 连续错误会造成 desk board 与真实进展脱节）。
