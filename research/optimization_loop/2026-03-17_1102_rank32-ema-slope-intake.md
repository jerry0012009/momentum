# 2026-03-17 11:02 UTC · Rank 32 EMA structure vs MA slope fresh intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Run 1 / EMA` 仍为 `waiting_not_due`；`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 继续显示全 desk 没有 `due-now / overdue` lane，因此按板子自动切到 Scout，不允许 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short`：当前仓库存在大量与本轮无关的脏文件与未跟踪产物；本轮只做 selective 改动，不混提。
- 最近 optimization runs：`1057 rank31-clean-replication-park`、`1036 rank31-intake`、`1029 rank30-clean-replication-park`、`1006 rank29-p3-monitoring-redwatch`。
- `Paper Seat / EMA`：继续 `waiting_not_due`；最近到点仍是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-18 00:00 UTC`、A 股三条 lane `-> 2026-03-18 07:00 UTC`。
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：都已在 `P3`，当前没有新的真实 `append/review` row；继续补近义 wiring 边际价值低。
- `Rank 30 / Rank 31`：刚完成最小 clean replication，并已如实压回 `park / evidence pool`；不应立刻重开。
- `Rank 5 / Rank 6`：仍需要 prediction-market / equity-proxy 这类额外外部数据，不是当前最便宜诚实的一轮动作。
- `Rank 7`：唯一允许的 cheap honesty recheck 已做完，当前也不该继续占默认主资源。
- **结论**：当前边际价值最高的动作，不是再磨旧 P3，也不是重开刚 park 的 `Rank 30 / Rank 31`，而是挑一条更贴近现有 EMA / pullback 家族、且不需要新外部数据的 fresh repo-based intake。

## 本轮主点 + 紧邻子点
- **主点**：把 `Rank 32 EMA structure vs MA slope direction gate` 落成新的 fresh-intake artifact。
- **紧邻子点**：把这个 intake 同步进 `TODO` 顶板与 reader-facing 页面，避免下一轮再次误回已 park 的旧线。

## 为什么选 Rank 32，而不是别的 fresh 线
- 这条线直接来自当前 repo 已在用的 `EMA` 方向层拆解：不是凭空发明新框架，而是把“快慢线位置关系”与“趋势斜率同向”拆成一个可验证问题。
- 它比 `Rank 5 / Rank 6` 更便宜诚实：不需要新的外部市场或预测市场数据。
- 它比继续围绕 `Rank 17 / Rank 29 / Rank 2` 做近义接线更贴近当前 desk 主线：如果 slope honesty gate 根本不成立，就可以很快 `park`；如果有一点增益，也可能自然衔接回当前存活的 EMA / pullback 家族。

## 两条轻量诚实守门（进入 intake 前）
1. **trade on / trade off 能写清楚**
   - `trade on = EMA fast > EMA slow（空头反向），且 fast/slow slope 同向并超过最小斜率门；若做 reclaim 版，则 close 还要重新站回 fast EMA / spread 中枢同侧`
   - `trade off = EMA 结构反向、任一 slope 走平/反拐、或 reclaim 失败后重新跌回结构错误一侧`
2. **没有偷塞 lookahead / repaint**
   - 全部只允许使用已完成 bar 的 EMA level / spread / slope；
   - 不允许先看未来 pocket 再挑 slope 阈值，也不允许把回看最优窗口写回 source intake。

## 本轮具体产物
1. 新增 artifact
- `reports/artifacts/literature/scout_rank32_ema_slope_structure_source_intake_card.csv`

2. 新增 reader-facing 页面
- `reports/site/reading/trendline_alpha_scout/rank32_ema_slope_structure_source_intake.html`

3. 更新 reader-facing 总入口
- `reports/site/reading/trendline_alpha_scout/report.html`
  - 新增 `Rank 32 · EMA structure vs MA slope` 卡。

4. 更新顶板
- `docs/TODO.md`
  - `Next 3 bot3 runs` 的 authoritative override 已切到：若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 `append/review row`，下一轮默认先给 `Rank 32` 做那 1 次最小 clean replication。
  - 同时补入 `Rank 32` 的简短候选说明，防止未来 run 再把它当“没落卡的随想法”。

## 当前 hard verdict
- **`Rank 32 = fresh intake only / admit_to_clean_replication_queue`**
- 更直白地说：
  - 这轮只回答“下一条最值得花 1 轮预算验证的 repo-based 15m crypto 候选是谁”；
  - 当前最诚实答案是：**把 `EMA` 方向层拆成 `位置关系 vs slope honesty gate`，比重开刚 park 的 `Rank 30 / Rank 31` 更值。**

## 下一轮只允许做什么
- 固定复用 `BTC/ETH/SOL 120d 15m` cache；
- 只做 **1 次最小 clean replication**：`ema_cross_only / ema_cross_plus_slope_floor / ema_cross_plus_slope_reclaim`；
- 先回答四个便宜问题：
  - `post_cost_return`
  - `trade_count`
  - `no_trade_ratio`
  - `slope-pocket honesty`
- 做完后应快速给出 `park / P1`，而不是继续停在 intake 文案态。

## 最小验证
已执行：
1. `grep -n "Rank 32" docs/TODO.md`
2. `grep -n "Rank 32 · EMA structure" reports/site/reading/trendline_alpha_scout/report.html`
3. 文件存在性检查：
   - `reports/artifacts/literature/scout_rank32_ema_slope_structure_source_intake_card.csv`
   - `reports/site/reading/trendline_alpha_scout/rank32_ema_slope_structure_source_intake.html`

## fallback 记录（按 8.1）
- 本轮未使用 `edit`，因此也未触发 exact-text mismatch fallback。

## commit
- 未提交。
- 原因：仓库仍有大量与本轮无关的脏文件与未跟踪文件，避免混提。
