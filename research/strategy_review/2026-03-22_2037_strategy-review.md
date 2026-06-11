# Strategy Review (bot2)

Time: 2026-03-22 20:37 UTC

## 本轮一句话判断
Desk 主线不变：**Paper Seat(EMA)仍是 primary anchor 且处于 waiting_not_due**；`Live Seat` 继续暂空；bot3 的主资源应继续压在 **Scout Seat = Rank 140（PBO/CSCV/Deflated Sharpe honesty gate）**，并严格只做“显式三臂 returns matrix → canonical scorecard”这一类最小交付（一次只跑 1 个 family）。

## 1) 必检：Repo 状态
- 分支：`master`
- 工作区：**dirty（大量已修改 + 未跟踪产物/脚本/报告）**。
  - 结论：这会显著增加“误把产物当代码、误 commit”风险；本轮不做大清理，只记录风险。

## 2) 必检：最近 optimization_loop / strategy_review
### 最近 `research/optimization_loop/`（Top 5）
- 2026-03-22_2035_rank140-rank111-explicit-three-arm.md
- 2026-03-22_1920_rank140-rank125-explicit-three-arm.md
- 2026-03-22_1907_rank140-scorecard-arm-rename.md
- 2026-03-22_1805_rank140-rank112-aligned-scorecard.md
- 2026-03-22_1704_rank140-rank125-aligned-scorecard.md

关键证据（来自 20:35 这轮 bot3）：
- Run1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` → **waiting_not_due**（exit code 2 合规）
- Run2：manual narrow paper lanes 刷新摘要显示 `new_closed_trades_appended=0` → 无 status-changing event，按顶板跳过
- Run3（Rank 140 on Rank 111 explicit 3-arm）：
  - kept/veto 计数：`105 : 93`（显著更健康的分布）
  - canonical scorecard：`PBO=0.7143` → **verdict=guard_failed**（仍不具备 promote 资格）

### 最近 `research/strategy_review/`（Top 5）
- 2026-03-22_1950_strategy-review.md
- 2026-03-22_1910_strategy-review.md
- 2026-03-22_1831_strategy-review.md
- 2026-03-22_1733_strategy-review.md
- 2026-03-22_1653_strategy-review.md

## 3) 必检：当前 cron 列表（要点）
- `bot3-momentum-auto-opt-13m`：enabled，但最近 delivery error 显示 **使用了 `rg` 搜索** 并失败；consecutiveErrors=3（需要止血）
- `momentum-narrow-paper-lanes-20m`：最近 `ok`
- `bot2-strategy-review-40m`：本任务
- `bot7-quant-digest-30m`：最近 `ok`

本轮最小工程建议：**bot3 运行中不要假设有 `rg`**（也不要在根目录做全局搜）；若需要搜索，用 `grep -R` 或 python，且 scope 限定到 `jerry/momentum/`。

## 4) TRADING DESK BOARD 复核（authoritative）
> 本轮未改 `docs/TODO.md` 顶部作战板（它已覆盖最新座位与排班；且 20:35 bot3 loop 与之完全一致）。

### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted / family lanes**（Paper family lanes）：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat 是否空
- **Live Seat：空（暂空）**

### Scout 复刻对象
- **Scout Seat primary**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`（当前 P1）

## 5) 候选 P0~P4 分档（本轮快照）
- **P1（weak candidate / 只允许便宜诚实检查）**
  - `Rank 140`（主点；继续 keep_P1，直到显式三臂口径稳定 & scorecard 改善再谈 promote）
  - `Rank 125`、`Rank 112`、`Rank 111`（作为 Rank140 的单-family 验证输入，不应夺主资源）
- **P0（park / evidence pool）**
  - `Rank 137/138/127` 以及其余已 park ranks（按顶板）
- **P3（hosted narrow paper pilot / continuity 池）**
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（20m refresh）
  - `Rank 139`（独立 runner）
  - `Rank 122`（sidecar monitoring）
- **P2 / P4**：本轮无新增

## 6) Next 3 bot3 runs（排班）
1. **Run 1 = EMA due-check first**（only if due-now/overdue 才 refresh；否则立刻切换）
2. **Run 2 = Hosted P3 continuity（事件驱动）**（无 status-changing event 则跳过）
3. **Run 3 = Rank 140**：继续 **显式三臂 returns matrix → canonical scorecard**（一次只做 1 个 family；禁止扩展到多 family 并发）

## strongest evidence / weakest lines / Top1~3
- **Strongest evidence**：Rank140 显式三臂方法已跑通，且在 Rank111 上得到更健康的 kept/veto 分布（105:93），说明口径方向正确；但 PBO 仍高（0.714）→ 诚实结论仍是 guard_failed。
- **Weakest / should-park lines**：当前不应把 hosted P3 continuity 拉回 Scout 主点（除非出现 status-changing event）。
- **Top 1~3**：
  1) 先止血 bot3 的 `rg` 依赖导致的连续错误（改 prompt / 改搜索方式与 scope）。
  2) Rank140：坚持“一轮一条 family”的 explicit 3-arm 复跑，不要再做近义 intake/demo。
  3) Paper Seat：waiting_not_due 时不要空转，保持 due-check discipline。

## 本轮我改了什么
- 本轮尚未改代码/文档（下一步只对 bot3 cron prompt 做最小修补，避免 `rg` 依赖）。

## 风险与不确定性
- bot3 连续报错若不止血，会让 13m loop 形同虚设；需要最小 prompt/工具约束立即纠正。