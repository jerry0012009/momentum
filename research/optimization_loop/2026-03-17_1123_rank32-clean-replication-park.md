# 2026-03-17 11:23 UTC · Rank 32 EMA slope clean replication park

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续 `waiting_not_due`；最新 due guardrail 仍显示全 desk 没有 `due-now / overdue` lane，因此按板子从 `EMA` 自动切到 `Scout Seat`。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short`：仓库内仍有大量与本轮无关的脏文件和未跟踪产物；本轮只做 selective 改动，不混提。
- 最近 optimization runs：`1102 rank32-ema-slope-intake`、`1057 rank31-clean-replication-park`、`1029 rank30-clean-replication-park`、`1006 rank29-p3-monitoring-redwatch`。
- `Paper Seat / EMA`：仍是 `waiting_not_due`；最近后续动作还是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-18 00:00 UTC`、A 股三条 lane `-> 2026-03-18 07:00 UTC`。
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：都没有新的真实 `append/review` need，不该继续磨近义 wiring。
- `Rank 30 / Rank 31`：刚完成最小 clean replication 且都已压回 `park / evidence pool`，不应立刻重开。
- `Rank 5 / Rank 6`：仍需要额外外部数据，不是当前最便宜诚实的一轮动作。
- **结论**：`Rank 32 EMA structure vs MA slope direction gate` 仍是本轮最高边际价值动作，因此按 top board 直接执行那 1 次最小 clean replication。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 32` 的 1 次最小 clean replication，比较 `ema_cross_only / ema_cross_plus_slope_floor / ema_cross_plus_slope_reclaim`。
- **紧邻子点**：把结果同步到 `docs/TODO.md`、reader-facing 页面与站点入口，避免继续把 `Rank 32` 当成“只停在 intake 卡”的候选。

## clean-room 规则（本轮冻结）
1. `ema_cross_only`
   - `trade on = higher_tf EMA fast > slow（空头反向）+ close 重新穿回 fast EMA`
2. `ema_cross_plus_slope_floor`
   - 在前者基础上要求 `fast/slow slope` 同向，且 `|fast slope|` 过最小门槛
3. `ema_cross_plus_slope_reclaim`
   - 在 slope floor 基础上，再要求最近 4 根里出现过一次向 `spread mid` 的回抽，并在当前 bar 重新站回 `fast EMA + spread mid` 同侧
4. honesty guard
   - higher-tf 只用 completed `1h` bar 的 `EMA20 / EMA50 / slope`
   - 入场固定 `next-bar open`
   - 持有固定 `8` 根 `15m` bar
   - 默认 non-overlap

## 结果（hard verdict）
- **`Rank 32 = park / evidence pool`**
- 最小 clean replication 并没有塌成负值，反而给出了一组“看起来还不错”的正 pocket：
  - `ema_cross_only`：`6bps/side mean_total_return≈-18.73%`、`positive_asset_ratio=1/3`、`mean_trades≈257.3`、`mean_no_trade_ratio≈97.77%`
  - `ema_cross_plus_slope_floor`：`6bps/side mean_total_return≈+50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`、`mean_no_trade_ratio≈99.34%`
  - `ema_cross_plus_slope_reclaim`（主变体）：`6bps/side mean_total_return≈+24.79%`、`positive_asset_ratio=3/3`、`mean_trades≈25.0`、`mean_false_reclaim_ratio≈12.93%`、`mean_no_trade_ratio≈99.78%`
- 但真正决定 verdict 的 blocker 也很直接：
  - 这条线的收益主要建立在**极薄交易密度**上；
  - 即使主变体成本后仍是正值，`mean_no_trade_ratio≈99.78%` 说明它远没到默认席位可推进的程度；
  - 因此更诚实的 desk 判定不是 `P1`，而是**把它收回 `park / evidence pool`，保留为“EMA 方向层有正 pocket，但当前太稀”的证据。**

## slope-pocket honesty
- 主变体 `ema_cross_plus_slope_reclaim @ 6bps/side`：
  - `bucket_1≈+0.06% / positive_asset_ratio≈66.67%`
  - `bucket_2≈+4.78% / positive_asset_ratio≈100.00%`
  - `bucket_3≈+18.39% / positive_asset_ratio≈100.00%`
- 解读：不是只有最高斜率桶才亮，这点比“单热像素”好；但每桶平均交易数都只有 `≈8.3`，样本仍过薄，不能因此越级升格。

## 本轮产物
1. 新脚本
- `scripts/build_rank32_ema_slope_clean_replication.py`

2. 新 artifact
- `reports/artifacts/scout_rank32_ema_slope_structure_15m/overall_summary.csv`
- `reports/artifacts/scout_rank32_ema_slope_structure_15m/asset_summary.csv`
- `reports/artifacts/scout_rank32_ema_slope_structure_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank32_ema_slope_structure_15m/slope_bucket_summary.csv`
- `reports/artifacts/scout_rank32_ema_slope_structure_15m/meta.csv`

3. 新 reader-facing 页面
- `reports/site/factors/scout_rank32_ema_slope_structure_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/rank32_ema_slope_structure_clean_replication.html`

4. 更新入口 / 顶板
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md`
  - 新增 `Rank 32` clean replication block
  - 将 `Next 3 bot3 runs` 的 authoritative override 改成：`Rank 32` 已完成 clean replication 且维持 `park / evidence pool`；若 `Rank 29 / Rank 17 / Rank 2` 仍无真实动作，下一轮默认回到新的 fresh intake，而不是重开 `Rank 30 / Rank 31 / Rank 32`

## 最小验证
已执行：
1. `python3 scripts/build_rank32_ema_slope_clean_replication.py`
2. 读取并检查：
   - `reports/artifacts/scout_rank32_ema_slope_structure_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank32_ema_slope_structure_15m/slope_bucket_summary.csv`
   - `docs/TODO.md`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## fallback / 修正记录
- 首次运行脚本时报错：`KeyError: 'close'`
- 原因：`merge_asof` 后 higher-tf 原始收盘列与 bar 自身 `close` 列重名。
- 修正：把 higher-tf 源列改名为 `close_1h_src` 后重跑成功。
- 本轮未触发 `edit exact-text mismatch` fallback。

## commit
- 未提交。
- 原因：仓库存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
