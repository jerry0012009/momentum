# momentum bot2 strategy review — 2026-03-21 19:24 UTC

## 0) 本轮硬性检查清单

### Repo 状态
- `jerry/momentum` 工作区：**非常脏**（大量未跟踪 artifacts / site build 产物 + 若干已修改脚本）。
- 结论：本轮 **不做清理/commit**；仅做 desk board 最小必要更新（时间戳/快照）。

### 最近 research/optimization_loop/
- 最新条目集中在 `2026-03-21 07:xx UTC` 附近（如 `Rank 139 source intake`、`Rank 138 clean replication`、`Rank 137 time-stability verdict` 等）。
- 结合 cron 状态：`bot3-momentum-auto-opt-13m` 最近一次运行仍是 `timeout`，因此近几个小时 **无新增优化日志** 属于一致现象。

### 最近 research/strategy_review/
- 最近存在大量 strategy review 日志；本轮新增：本文件。

### 当前 cron 列表（关键项）
- `bot2-strategy-review-40m`（本任务）：running。
- `bot3-momentum-auto-opt-13m`：最近一次 `timeout`（上次运行失败）；需要优先恢复稳定执行，否则 Run2/Run3 永远落不了地。
- `momentum-narrow-paper-lanes-20m`：最近 `2026-03-21T19:24:27Z` 刷新成功（见 artifacts）。

---

## 1) TRADING DESK BOARD（从 TODO 顶部读取，并做最小必要更新）

### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Paper family lanes（hosted）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Hosted lanes（P3 / sidecar）
- **running hosted narrow paper lanes（20m refresh）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 本轮刷新：`run_at_utc=2026-03-21T19:24:27Z`，`new_closed_trades_appended=0`
- open positions（仍只在 Rank17）：
  - `Rank17 / ETH-USD / long`（`exit_ts_marked=2026-03-21 19:00 UTC`，open inferred）
  - `Rank17 / SOL-USD / short`（`exit_ts_marked=2026-03-21 19:00 UTC`，open inferred）

### Live seat 是否空
- **Live Seat：暂空**（无候选达到可争夺 tiny-live 的“基础快筛过关 + 无硬伤”状态）。

### Scout 复刻对象（本轮唯一主点）
- **Rank 139 / CUSUM event-bar confirm-veto gate**
  - 状态：`P1 / guard-passed / admit_to_clean_replication_queue`
  - 定位：更像 breakout-short / Fib / EMA-PSAR 共用的 **post-entry event-confirm / veto layer**

---

## 2) 候选分档（P0~P4）

> 口径：以 `docs/TODO.md` 顶部 board 为 authoritative；这里只做汇总口径，便于快速排兵布阵。

### P3（Hosted / Sidecar，继续跑但不抢主资源位）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh running）
- `Rank 122`（hosted sidecar，但不在 20m lane；低频监控）

### P1（Active Scout / 仍 relevant，值得占用 bot3 主资源位）
- `Rank 139 / CUSUM event-bar confirm-veto gate`（**当前 Run2 主点**）
- `Rank 125 / range location veto gate`（keep_P1）
- `Rank 112 / basis dislocation short veto`（weak candidate / evidence_pool）
- `Rank 111 / abnormal-return event clock`（evidence_pool）

### P0（已 park / evidence pool，默认不再继续占主资源）
- `Rank 138`（hard verdict: park / single-pocket dependency）
- `Rank 127`（hard verdict: park / 2026-03 转负，不升 P2）
- `Rank 137`（park）
- `Rank 136/135/134/133/132/131/130/129/128/124/123/121/120/119/118/117/115/114/113`（park / evidence pool）

### P2 / P4
- **P2：当前无明确晋级者**（先把 Rank139 的最小 clean replication 做完，再谈升格）。
- **P4：无**（本 desk 当前不允许“纯研究型”占用席位；P4 只会是明确被否决/不再触碰的条目，但目前 park 已足够）。

---

## 3) Next 3 bot3 runs（排班）

1. **Run 1 = EMA due-check first**
   - 若有真实 `due-now / overdue` lane：先做 paper refresh。
2. **Run 2 = 若 EMA 仍 waiting_not_due：做 `Rank 139` 的 1 次最小 clean replication**
   - 复用 `BTC/ETH/SOL 15m` baseline + `1m` 数据。
   - 只回答：`same_dir_first / opp_dir_first / no_event_timeout` 是否改善 post-cost expectancy / retention / failure。
3. **Run 3 = 条件分支**
   - 若 Rank139 过关：给 `promote_P2 / promote_P3 / keep_P1` 硬结论；
   - 若 Rank139 直接 park：按 `fresh intake > tiny-live plumbing` 顺序认领下一条；
   - 只有当 Run2 + fresh intake 都 exhausted，才允许切 tiny-live / path-management fallback。

---

## 4) 本轮对 desk 的一句话结论
- Desk 配置本身合理（Paper anchor + Scout 主点明确 + P3 sidecar 续跑），**最大阻塞** 是 bot3 13m cron 的持续 timeout：需要尽快恢复其稳定执行，否则 Run2/Run3 永远无法落地。
