# 2026-03-17 10:29 UTC · Rank 30 clean replication → park

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 先执行 `Run 1` 守门：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：当前全 desk 仍无 `due-now / overdue` lane；美股约 `9.6h`、Crypto 约 `13.6h`、A 股约 `20.6h` 后到点，因此按板子规则切到 `Scout Seat`。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short --branch`：工作区仍有大量与本轮无关的已修改/未跟踪文件；本轮不混提。
- 最近 runs：`1007 rank30-trendln-channel-intake`、`1006 rank29-p3-monitoring-redwatch`、`0941 rank29-time-stability-p3`、`0925 rank29-no-overlap-honesty-check`、`0921 rank29-clean-replication`。
- `Paper Seat / EMA`：真实 `waiting_not_due`；本轮 `run_ema_paper_trading_guarded_refresh.py --require-due` 只输出守门说明，并以 exit code `2` 结束，语义是“当前不该伪 refresh”，不是失败。
- `Live Seat`：仍无 bot2 新 promoted candidate；继续暂空。
- `Scout Seat`：
  - `Rank 17 / Rank 2 / Rank 29` 都没有新的真实 `append/review` need；
  - `Rank 26 / 27 / 28` 已 park；
  - 因此当前边际价值最高的动作是按上一轮 intake 计划，给 `Rank 30` 做那 1 次最小 clean replication，直接回答“该不该继续给预算”。

## active Scout 边际价值比较（本轮前）
- `Rank 29`：已经是 `P3 narrow paper pilot`，且刚补完 `monitoring / weekly-review` 最小接线；当前没有新的真实 append/review 行，再继续磨近义 wiring 边际价值低。
- `Rank 17`：`P3 narrow paper pilot approved（ETH+SOL-only）`，最近已补过 weekly-review writeback，没有新的真实 append need。
- `Rank 2`：当前也没有新的真实 append/review 行；继续围着 closeout / receipt / wiring 近义卡打磨不符合板子要求。
- `Rank 30`：刚好处在 `admit_to_clean_replication_queue`，而且最便宜的四个问题已经预先冻结好：`trade_count / false_break_ratio / post_cost_return / width-stability`。
- 结论：本轮主资源给 `Rank 30`，不并行打开第二条 fresh intake。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 30 trendln paired-channel breach / corridor breakout gate` 的 **最小 clean replication**。
- 紧邻子点：把 hard verdict 同步回 `TODO` 顶部指挥板与 reader-facing 页面，避免下一轮继续把它误读成待复现 fresh intake。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_rank30_trendln_channel_clean_replication.py`
2. 新增 artifact：
   - `reports/artifacts/scout_rank30_trendln_channel_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank30_trendln_channel_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank30_trendln_channel_15m/width_stability_summary.csv`
   - `reports/artifacts/scout_rank30_trendln_channel_15m/trades_primary_6bps.csv`
   - 以及三条资产的 `*_channel_frame.csv` / `trades_primary_6bps_*.csv`
3. 新增 reader-facing 页面：
   - `reports/site/factors/scout_rank30_trendln_channel_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/rank30_trendln_channel_clean_replication.html`
4. 更新 reader-facing 入口：
   - `reports/site/reading/trendline_alpha_scout/report.html`
   - 给 Rank 30 卡补上 `clean replication` 链接。
5. 更新 desk board：
   - `docs/TODO.md`
   - 把 `Rank 30` 从 `admit_to_clean_replication_queue` 改成 `park / evidence pool`；
   - 同步把 `Next 3 bot3 runs` 顶部 override 改成 `10:27 UTC` 版本；
   - 顺手清掉了 `Rank 30` 条目后面误串上的一段旧 `Rank 29` 文本，避免下一轮继续被脏板子误导。

## clean-room 规则（冻结后）
- 通道成立：过去 `96` 根里，support / resistance 两条拟合线都至少有 `3` 个因果确认 pivot，斜率方向一致，且最近 `12` 根的 corridor width 变异系数 `<= 0.35`。
- `raw_corridor_breach`：上一根还在外轨内侧，本根收盘真正穿出 outer line，且平均斜率同向。
- `breach_plus_reclaim_hold`：先出现 raw breach，再要求下一根收盘仍留在 corridor 外侧，避免只靠单根动作入场。
- 执行口径：`next-bar open` 入场，持有 `8` 根 15m bar。
- 假突破定义：触发后 `4` 根内收盘重新回到同一方向边界内，或通道状态直接失效。

## 关键证据 / hard verdict
### 跨资产总表（核心结论）
- `raw_corridor_breach @ 6bps/side`：
  - `mean_total_return≈-10.73%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈93.0`
  - `mean_false_break_ratio≈86.11%`
- `breach_plus_reclaim_hold @ 6bps/side`（主变体）：
  - `mean_total_return≈-7.33%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈57.3`
  - `mean_false_break_ratio≈82.39%`
  - `mean_width_cv≈0.137`

### 分资产读法（主变体 @ 6bps/side）
- `BTC`：`total_return≈-13.92%`，`false_break_ratio≈78.12%`
- `ETH`：`total_return≈-6.31%`，`false_break_ratio≈88.00%`
- `SOL`：`total_return≈-1.78%`，`false_break_ratio≈81.03%`

### 最诚实的结论
- `breach_plus_reclaim_hold` 确实比 `raw_corridor_breach` 少亏一些，也把交易数从约 `93` 降到约 `57`；
- 但它**没有**把这条线拉回最小 admission 门槛：
  - 成本后跨资产仍然 `0/3` 为正；
  - 假突破率仍高达约 `82%`；
  - 宽度稳定性虽然不算爆炸，但远不足以弥补收益与假突破问题。
- 因此本轮 hard verdict 只能是：**`park / evidence pool`**。

## 最小验证
已执行：
1. `python3 -m py_compile scripts/build_rank30_trendln_channel_clean_replication.py`
2. `python3 scripts/build_rank30_trendln_channel_clean_replication.py`
3. 抽查输出：
   - `reports/artifacts/scout_rank30_trendln_channel_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank30_trendln_channel_15m/asset_summary.csv`
   - `reports/site/factors/scout_rank30_trendln_channel_15m/report.html`
   - `docs/TODO.md` 顶部 override 与 `Rank 30` 条目

## 风险 / 边界
- 这轮只做了 **1 次最小 clean replication**，不是完整 `Light Stability Pack`；但按板子规则，这已经足够回答“还值不值得继续给默认预算”。
- 当前实现是 `trendln` 语义的 clean-room channel derivative，不是直接调用上游 repo 算法；它的用途是做 fast verdict，不是给 `trendln` 盖章。
- 当前 repo 仍有大量与本轮无关的脏文件；本轮不安全 mixed commit。

## 下一步建议
1. 若下一轮 `Rank 29 / Rank 17 / Rank 2` 仍无新的真实 `append/review` row，就不要重开已 park 的 `Rank 30`；直接比较下一条新的 `paper / repo based 5m / 15m crypto` fresh intake。
2. 若 bot2 后续明确要求对 `Rank 30` 重开，也只能把它当 `park / evidence pool` 里的反例线来处理，而不是继续假装它仍在 admission 队列。
3. 一旦 `EMA` 到点，立即切回 `Paper Seat`，不要因为 Rank 30 的 park 结果打断 due-now refresh。

## 实现小插曲
- 首版脚本在 `update_reading_report()` 里有一个字符串字面量手误，`py_compile` 当场报 `SyntaxError`。
- 已立即修正并重跑，不影响本轮最终 artifact；这类错误属于可恢复实现错误，不改变本轮硬结论。

## Commit hash
- 未提交。
- 原因：当前 repo 存在大量与本轮无关的脏文件与未跟踪文件，避免混提。
