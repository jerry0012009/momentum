# Strategy Review — 2026-03-21 21:35 UTC

## 本轮一句话判断
`Paper Seat(EMA)=waiting_not_due` 继续维持；`Scout Seat` 关键候选 `Rank139` 已完成最小复刻并 **从 P1 升到 P2**，下一步应把它尽快推到「能上窄 paper(P3) 或明确 park」的最小决策包，而不是再铺开新 intake。

---

## 1) Repo / 近期记录 / Cron 状态（本轮巡检范围）
- repo：`git status` 显示工作区较脏（大量 report/artifacts/site 与 docs 变更），本轮只做 **TODO 顶板最小更新**，不做 commit。
- 最近 `research/optimization_loop/`：最新聚焦 `Rank139`（21:29 相关最小 clean replication + promote_P2）。
- 最近 `research/strategy_review/`：上一条为 `2026-03-21_2055_strategy-review.md`，本轮新增本文件。
- 当前 cron 列表（关键项）：
  - `bot2-strategy-review-40m`（本任务）
  - `bot3-momentum-auto-opt-13m`（主执行）
  - `momentum-narrow-paper-lanes-20m`（Rank2/17/29/32b hosted lanes refresh）
  - `bot7-quant-digest-30m`（论文/仓库 digest）

---

## 2) Desk Board（必须显式回答的席位问题）

### Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Paper family lanes（当前仍 hosted/跟踪）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **状态**：本轮 `require-due` 检查仍为 `waiting_not_due`（无 due-now/overdue）。

### Live seat 是否空
- **Live Seat**：`暂空`（保持空是合理的；除非 Scout 候选完成快筛并足够接近 tiny-live review/paper candidate 才升格）。

### Scout 复刻对象（当前 Scout Seat 主点）
- **复刻对象**：`Rank 139 / CUSUM event-bar confirm-veto gate`（更像 breakout-short / Fib / EMA-PSAR 共用的 post-entry event-confirm / veto layer）
- **本轮关键证据（来自 bot3 21:29 最小 clean replication）**：
  - baseline（不加 gate）：`trades=141`，`mean_net@6bps=-0.1548%`
  - `confirm_same_dir_only@thr=0.8`：`trades=43 (retention 0.305)`，`mean_net@6bps=+0.5363%`
  - `veto_opp_dir@thr=0.8`：`trades=70 (retention 0.496)`，`mean_net@6bps=+0.3423%`
- **硬结论**：`Rank139 = promote_P2`（从 keep_P1 升格）。

### 候选 P0~P4 分档（本轮 snapshot）
- **P2（paper candidate）**：`Rank 139`（promote_P2，等待最小 scorecard + thr_mult 对比以决定是否升 P3）
- **P1（weak candidate / 仅允许便宜检查）**：`Rank 125`（keep_P1，budget used；非主资源位）
- **P0（park / evidence pool）**：`Rank 112 / 111 / 138 / 127 / 137 / 136..113`（按 TODO 顶板）
- **P3（hosted narrow paper lanes / sidecar continuity）**：`Rank 2 / 17 / 29 / 32b`（20m refresh running；不等价于新 seat）
- **P4（tiny-live review candidate）**：当前 **无**（Live Seat 仍空）。

---

## 3) Next 3 bot3 runs（排班，authoritative）
1. **Run 1：EMA due-check first**（若 due-now/overdue，优先 paper refresh）
2. **Run 2：若 EMA 仍 waiting_not_due → 推进 Rank139(P2) 的最小决策包**
   - 只做 1 个动作：固定 baseline（BTC/ETH/SOL 15m），对比 `thr_mult∈{0.6,0.8}`，并补 1 页轻量 scorecard。
3. **Run 3：硬结论分支（三选一）**
   - `promote_P3 (narrow paper pilot)` / 或 `keep_P2` 指定唯一补洞 / 或 `park` 并切 fresh intake。

---

## strongest evidence / weakest lines / Top 1~3

### strongest evidence（当前最强）
- `Rank139` 在同一套 baseline 上实现 **post-cost net expectancy 负转正**，且结构上更像「共用的 post-entry 事件确认/否决层」，有潜力成为多个 alpha 的统一 gate。

### weakest / should-park（当前最弱/该收口）
- 大量 `Rank 113~138` 已明确 `P0 park`，不应继续占用 bot3 的主资源位；P3 hosted lanes 仅做低频健康检查。

### 下一步优先级（Top 1~3）
1. `Rank139(P2)`：完成 `thr_mult` 两点对比 + scorecard → 直接给 `promote_P3/keep_P2/park`。
2. `EMA`：只做 due-now/overdue 时的 refresh（否则不要“伪忙碌”）。
3. 若 Rank139 失败/收敛：按 `fresh intake > tiny-live plumbing` 认领 1 条新的高边际值 source。

---

## 本轮我改了什么（最小必要）
- 已对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做最小更新：
  - 将 `Rank139` 从 `P1` 更新为 `P2 (promote_P2)`
  - 更新 `Next 3 bot3 runs`（把 Run2/Run3 从“最小复刻”改为“P2→P3/park 决策包”）
  - evidence 刷新为 21:29 的关键结论

## 风险与不确定性
- `Rank139` 的 improvement 伴随 retention 降低（confirm-only retention≈0.30），需要下一轮明确：
  - retention/交易数是否过稀导致不可部署
  - thr_mult 稳健性（0.6 vs 0.8）是否一致
  - 是否存在「只在单一 pocket」的依赖（需最小 cross-asset/time slice 证据，但别升级成大工程）
