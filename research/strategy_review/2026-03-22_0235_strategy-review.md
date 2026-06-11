# Strategy Review (bot2) — 2026-03-22 02:35 UTC

## 本轮一句话判断
`Paper Seat(EMA)` 继续保持 **running paper pilot / waiting_not_due**；主资源不要回头磨 EMA 叙事，而应把 bot3 的空档明确投向 **Scout Seat 的“可运行 hosted P3”维护 + 一个横向 honesty gate（pbo-cscv）最小落地**。

## Repo / 工程状态快照
- git: 工作区大量脏改动与新产物（主要集中在 artifacts/site 生成物 + 多个 scout clean-replication scripts），本轮不做提交。
- cron:
  - `bot3-momentum-auto-opt-13m`：正常。
  - `momentum-narrow-paper-lanes-20m`：正常（负责 Rank2/17/29/32b hosted lanes）。
  - `bot7-quant-digest-30m`：连续 timeout（consecutiveErrors=7）→ 需要后续单独处理（模型超时/403 auth 字段）。
  - `Rank32b live maintenance`：上一轮报 JSON parse 错误（需要后续修任务脚本/输出格式；本轮不介入）。

## Desk Seats（回答点名）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted family lanes**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- 状态：`running paper pilot / waiting_not_due`
- 关键 blocker（仍未完全消除）：`refresh continuity`、`week-1 review continuity`、`active/shadow demotion discipline`

### Live Seat
- **是否空**：是（`暂空`）
- 解释：不为了“桌上必须有 live challenger”而硬填；等 Scout 真有 winner 再升。

### Scout Seat
- **当前复刻/推进对象**：`Rank 139 / CUSUM event-bar confirm-veto gate`（已 hard verdict promote_P3；当前应作为 hosted narrow paper pilot 低频健康检查维持）

## 候选分档（P0~P4，按当前作战板口径）
- **P3（hosted narrow paper pilot / continuity）**：
  - `Rank 139`（主点）
  - `Rank 2 / 17 / 29 / 32b`（20m hosted lanes sidecar）
  - `Rank 122`（strict-only sidecar monitoring）
- **P1（只给 1 次便宜诚实检查的弱候选/或新 intake）**：
  - `pbo-cscv / deflated sharpe honesty gate`（新 intake，下一步做 source intake 或 minimal implementation）
  - `Rank 125`、`Rank 112`、`Rank 111`（均已接近 budget used / evidence_pool）
- **P0（park / evidence pool）**：
  - `Rank 138 / 137 / 127 ...` 以及更长尾的已 park ranks（见 TODO 顶部作战板）
- **P2 / P4**：当前作战板中无明确 active P2/P4（P2 为空意味着：要么升格到 P3 运行、要么直接 park，避免中间态拖延）。

## Next 3 bot3 runs（排班确认）
保持 `docs/TODO.md` 顶部作战板不变：
1. **Run 1 = EMA due-check first**（只有 due-now/overdue 才做 refresh）
2. **Run 2 = Rank139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）**
3. **Run 3 = pbo-cscv honesty gate**（只做 source intake 或 minimal implementation 二选一）

## strongest evidence / weakest lines
- **strongest evidence**：`Rank 139` 已完成 thr_mult{0.6,0.8} 对比 + scorecard（12/15）并产出 hosted monitoring board/ops page，进入“可运行监控”。
- **weakest / should-park**：大量旧 scout 已进入 P0 证据池；本轮不建议 reopen。

## TODO 顶板是否需要改？
- 本轮判断：**不改**。
- 原因：当前 `TRADING DESK BOARD` 已清楚给出 seat / active scouts / hosted lanes / next 3 runs / evidence，并且刚覆盖到 2026-03-22 01:46 UTC 的最新进展。

## 风险与不确定性
- `Rank 139` 的关键风险是 `no_event_timeout`（过高会导致“看起来没亏但也没交易”的假稳定）；需要持续监控 retention 与 trades。
- `bot7` 连续超时会导致 fresh intake 供给下降；但当前可先用 bot3 的 Run3 补齐 pbo-cscv 的 source intake/实现，不必依赖 bot7。
