# 2026-03-17 11:50 UTC · Rank 33 NW+HL reclaim clean replication park

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续处于 `waiting_not_due`；最新 `due guardrail` 仍显示全 desk 没有 `due-now / overdue` lane，因此按顶板从 `Run 1` 自动切到 `Run 2`，不允许在 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short`：仓库内仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只做 selective 改动，不混提。
- 最近 optimization runs：`1128 rank33-nw-hl-reclaim-intake`、`1123 rank32-clean-replication-park`、`1057 rank31-clean-replication-park`、`1029 rank30-clean-replication-park`。
- `Paper Seat / EMA`：继续 `waiting_not_due`；最近后续动作仍是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-18 00:00 UTC`、A 股三条 lane `-> 2026-03-18 07:00 UTC`。
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：都已在 `P3`，当前没有新的真实 `append/review` need；继续补近义 wiring 边际价值低。
- `Rank 30 / Rank 31 / Rank 32`：都已完成当前允许动作并压回 `park / evidence pool`，不应立刻重开。
- `Rank 5 / Rank 6`：仍需要额外外部数据，不是这轮最便宜诚实的动作。
- **结论**：顶板已把 `Rank 33 endpoint NW + confirmed HL reclaim` 指定为当前 fresh intake 主线；本轮最该做的是把它从 `admit_to_clean_replication_queue` 推进到最小 clean replication verdict，而不是继续磨旧 P3 或重开已 park 线。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 33` 的 1 次最小 clean replication，比较 `raw_extrema_reclaim / nw_hl_reclaim / nw_hl_plus_highbreak`。
- **紧邻子点**：把结果同步到 `docs/TODO.md` 与 reader-facing 页面，避免下一轮再把它误读成“还只停在 intake 卡”。

## clean-room 规则（本轮冻结）
1. `raw_extrema_reclaim`
   - `trade on = higher-tf bias 同向 + 最近确认 swing 保持 HL/LH，并重新站回最近 swing 的中位 reclaim level`
2. `nw_hl_reclaim`
   - 在前者思路上，改用 `endpoint NW` 平滑与 `NW-confirmed HL/LH`，要求价格重新站回 `NW smooth` 同侧
3. `nw_hl_plus_highbreak`
   - 在 `nw_hl_reclaim` 基础上，再要求当前 close 同时突破最近确认高/低点
4. honesty guard
   - `endpoint NW` 只允许 causal / endpoint 版本
   - `confirmed extrema` 只在确认 bar 后才可用
   - higher-tf bias 只用 completed `1h` endpoint NW slope
   - 入场固定 `next-bar open`
   - 持有固定 `8` 根 `15m` bar
   - 默认 non-overlap

## 结果（hard verdict）
- **`Rank 33 = park / evidence pool`**
- 最小 clean replication 没把它推成合格候选：
  - `raw_extrema_reclaim`：`6bps/side mean_total_return≈-1.72%`、`positive_asset_ratio=1/3`、`mean_trades≈355.3`、`mean_false_reclaim_ratio≈49.13%`
  - `nw_hl_reclaim`：`6bps/side mean_total_return≈-1.39%`、`positive_asset_ratio=1/3`、`mean_trades≈324.7`、`mean_false_reclaim_ratio≈47.20%`
  - `nw_hl_plus_highbreak`（主变体）：`6bps/side mean_total_return≈-8.51%`、`positive_asset_ratio=1/3`、`mean_trades≈121.7`、`mean_false_reclaim_ratio≈20.07%`、`mean_no_trade_ratio≈98.71%`
- 直白解释：
  - `NW` 平滑确实把假 reclaim 比例压低了一些；
  - 但它没有把收益结构一起救活，反而在加上 `highbreak` 后变成 `bucket_2 单段为正、前后两段都负` 的中段口袋；
  - 所以当前更诚实的 desk 判定不是 `P1`，而是**直接压回 `park / evidence pool`**，保留为“结构过滤更干净，但还不够形成可推进 edge”的反例证据。

## time-pocket honesty（主变体 `nw_hl_plus_highbreak @ 6bps`）
- `bucket_1≈-9.24% / positive_asset_ratio=0/3`
- `bucket_2≈+5.03% / positive_asset_ratio=2/3`
- `bucket_3≈-3.95% / positive_asset_ratio=1/3`
- 解读：这不是稳定的三段存活，而是典型的 `中段亮、前后两端不站住`；因此不配继续占默认 Scout 主资源。

## 本轮产物
1. 新脚本
- `scripts/build_rank33_nw_hl_reclaim_clean_replication.py`

2. 新 artifact
- `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/overall_summary.csv`
- `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/asset_summary.csv`
- `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/meta.csv`

3. 新 reader-facing 页面
- `reports/site/factors/scout_rank33_nw_hl_reclaim_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/rank33_nw_hl_reclaim_clean_replication.html`

4. 更新入口 / 顶板
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md`
  - `Rank 33` 已从 `admit_to_clean_replication_queue` 更新为 `park / evidence pool`
  - `Next 3 bot3 runs` 的 authoritative override 已同步改成：若 `Rank 29 / Rank 17 / Rank 2` 仍无真实动作，下一轮默认回到新的 fresh intake，而不是重开 `Rank 30 / Rank 31 / Rank 32 / Rank 33`

## 最小验证
已执行：
1. `python3 scripts/build_rank33_nw_hl_reclaim_clean_replication.py`
2. 读取并检查：
   - `reports/artifacts/scout_rank33_nw_hl_reclaim_15m/overall_summary.csv`
   - `docs/TODO.md`
   - `reports/site/reading/trendline_alpha_scout/report.html`
3. 关键结果复核：
   - `nw_hl_plus_highbreak @ 6bps` 仍为负，且 `time-pocket honesty` 呈 `负 / 正 / 负`

## 风险 / 边界
- 这轮仍只是最小 clean replication，不是假装已经完成完整 `Light Stability Pack`。
- 规则里 `raw_extrema_reclaim` 的 reclaim level 采用了最近 swing 区间的中位线，这是一个刻意收缩后的最小可检验定义；当前结论只说明“按这套最小诚实定义，Rank 33 不值得继续拿默认主资源”。
- 若未来 bot2 明确要求重开，应该基于新的 genuinely verdict-changing 证据，而不是继续重复同一套 clean replication。

## 下一步建议
- 默认不要再给 `Rank 33` 额外预算；它已用完这条 fresh intake 当前允许的第一轮预算。
- 若下一轮 `EMA` 仍是 `waiting_not_due`，且 `Rank 17 / Rank 2 / Rank 29` 依旧没有真实 `append/review need`，应回到新的 `paper / repo based 5m / 15m crypto` fresh intake，而不是重开 `Rank 30 / Rank 31 / Rank 32 / Rank 33`。

## fallback / 修正记录
- 本轮未触发 `edit exact-text mismatch`；`TODO.md` 与 reader-facing 入口更新由脚本内稳健替换完成。

## commit
- 未提交。
- 原因：仓库仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
