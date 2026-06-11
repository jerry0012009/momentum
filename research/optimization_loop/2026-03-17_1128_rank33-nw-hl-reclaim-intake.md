# 2026-03-17 11:28 UTC · Rank 33 endpoint NW + confirmed HL reclaim fresh intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Run 1 / EMA` 继续处于 `waiting_not_due`；最新 due guardrail 仍显示全 desk 没有 `due-now / overdue` lane，因此按板子自动切到 Scout，不允许在 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short --branch`：工作区存在大量与本轮无关的已修改 / 未跟踪文件；本轮只做 selective 改动，不混提。
- 最近 optimization runs：`1102 rank32-ema-slope-intake`、`1054 rank31-clean-replication-park`、`1027 rank30-clean-replication-park`、`1007 rank30-intake`、`0847 rank29-intake`。
- `Paper Seat / EMA`：继续 `waiting_not_due`；最近到点仍是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-18 00:00 UTC`、A 股三条 lane `-> 2026-03-18 07:00 UTC`。
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：都已在 `P3`，当前没有新的真实 `append/review` row；继续补近义 wiring 边际价值低。
- `Rank 30 / Rank 31 / Rank 32`：已完成当前允许动作并压回 `park / evidence pool`；不应立刻重开。
- `Rank 5 / Rank 6`：仍需要 prediction-market / equity-proxy 之类额外外部数据，不是当前最便宜诚实的一轮动作。
- 备选的新 repo-based 方向里，`chip_distribution` 虽然贴近 support / trapped-holder 语义，但分钟级 crypto 下还要先引入 shares 假设；相较之下，`endpoint_nadaraya_watson + confirmed_extrema` 直接复用现有因果因子栈，边界更干净，也更贴近 pullback / structure 家族。
- **结论**：本轮边际价值最高的动作，不是再磨旧 P3，也不是重开刚 park 的线，而是把 `Rank 33 endpoint NW + confirmed HL reclaim` 落成 fresh-intake artifact。

## 本轮主点 + 紧邻子点
- **主点**：把 `Rank 33 endpoint NW + confirmed HL reclaim / causal swing persistence gate` 落成新的 fresh-intake artifact。
- **紧邻子点**：把这个 intake 同步进 `TODO` 顶板与 reader-facing 页面，避免下一轮再次误回已 park 的旧线。

## 为什么选 Rank 33，而不是别的 fresh 线
- 这条线直接来自当前 repo 已存在的因果因子栈：`endpoint_nadaraya_watson.py` + `confirmed_extrema.py`；不是凭空发明新大框架。
- 它比 `Rank 5 / Rank 6` 更便宜诚实：不需要新的外部市场 / prediction-market 数据。
- 它比继续围绕 `Rank 17 / Rank 29 / Rank 2` 做近义接线更贴近当前仍存活的 pullback / structure 家族：如果 `NW+HL reclaim` 根本不成立，就应很快 `park`；如果有一点 edge，也更自然地回挂到当前 desk 真正在意的 causal structure 入场问题。
- 它比 `chip_distribution` 这种仍需先处理 shares 假设的方向更适合当前一轮预算：先用完全因果、完全现有 cache 可复用的路径拿一个 first verdict。

## 两条轻量诚实守门（进入 intake 前）
1. **trade on / trade off 能写清楚**
   - `trade on = endpoint NW slope 与 higher-tf bias 同向，最近一个确认低点保持 HL，且当前 close 重新站回 NW smooth 之上并突破最近确认高点（做空反向）`
   - `trade off = NW slope 走平/反向、最近确认低点转成 LL、当前 bar 无法 reclaim NW smooth / 最近确认高点，或突破后很快跌回结构错误一侧`
2. **没有偷塞 lookahead / repaint**
   - `endpoint NW` 明确只允许 causal / endpoint 版本；
   - `confirmed extrema` 只在确认 bar 后才可用，禁止把中心点尚未确认时的 swing 提前拿来交易；
   - 不允许先看未来 pocket 再挑 `neighbor_bars / bandwidth` 的最优组合写回 source intake。

## 本轮具体产物
1. 新增 artifact
- `reports/artifacts/literature/scout_rank33_nw_hl_reclaim_source_intake_card.csv`

2. 新增 reader-facing 页面
- `reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`

3. 更新 reader-facing 总入口
- `reports/site/reading/trendline_alpha_scout/report.html`
  - 新增 `Rank 33 · endpoint NW + confirmed HL reclaim` 卡。

4. 更新顶板
- `docs/TODO.md`
  - `Next 3 bot3 runs` 的 authoritative override 已切到：若 `Rank 29 / Rank 17 / Rank 2` 仍无真实 `append/review row`，下一轮默认先给 `Rank 33` 做那 1 次最小 clean replication。
  - 同时补入 `Rank 33` 的简短候选说明，防止未来 run 再把它当成“还没落卡的 repo 想法”。

## 当前 hard verdict
- **`Rank 33 = fresh intake only / admit_to_clean_replication_queue`**
- 更直白地说：
  - 这轮只回答“下一条最值得花 1 轮预算验证的 repo-based 15m crypto 结构候选是谁”；
  - 当前最诚实答案是：**先用因果 NW + confirmed HL reclaim 拿一个最小 clean replication verdict**，而不是继续磨旧 P3 或重开刚 park 的 `Rank 30 / Rank 31 / Rank 32`。

## 下一轮只允许做什么
- 固定复用 `BTC/ETH/SOL 120d 15m` cache；
- 只做 **1 次最小 clean replication**：`raw_extrema_reclaim / nw_hl_reclaim / nw_hl_plus_highbreak`；
- 先回答四个便宜问题：
  - `post_cost_return`
  - `trade_count`
  - `false_reclaim_ratio`
  - `time-pocket honesty`
- 做完后应快速给出 `park / P1`，而不是继续停在 intake 文案态。

## 最小验证
已执行：
1. `grep -n "Rank 33" docs/TODO.md`
2. `grep -n "Rank 33 · endpoint NW" reports/site/reading/trendline_alpha_scout/report.html`
3. 文件存在性检查：
   - `reports/artifacts/literature/scout_rank33_nw_hl_reclaim_source_intake_card.csv`
   - `reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_source_intake.html`

## fallback 记录（按 8.1）
- 本轮未使用 `edit`，因此也未触发 exact-text mismatch fallback。

## commit
- 未提交。
- 原因：仓库仍有大量与本轮无关的脏文件与未跟踪文件，避免混提。
