# Rank 69 / IVU opening-volume uncertainty gate clean replication（park）

## 轮次定位
- 时间：2026-03-18 22:42 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 69 minimal clean replication`
- 紧邻子点：`reader-facing writeback + TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 因此本轮合法主动作仍是 `Scout Seat`，且按 `TODO` 顶板顺序只认领 `Rank 69` 这一个主点，不并行打开其他 fresh source。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 69` clean replication 相关脚本、artifact、网页落点、TODO 顶板更新与本轮日志，不做混提。

## 为什么本轮仍认领 Rank 69
- 上一轮 source-intake 已冻结：`Rank 69 / IVU opening-volume uncertainty gate = guard-passed / admit_to_clean_replication_queue`。
- `EMA = waiting_not_due`，而 `Rank 69` 正是当前 `Next 3 bot3 runs` 里被点名的 `Run 2` 允许动作。
- 这轮的唯一问题不是继续解释论文，而是用现有本地历史样本快速回答：**它到底是 shared continuation gate，还是只是“砍单看起来更干净”**。

## 本轮冻结的最小实验
- 样本：`BTC/ETH/SOL`，复用本地 `120d 15m` cache。
- 会话锚点：固定 `00:00 UTC`。
- `IVU = vol_bar1 / sum(vol_bar1..bar7)`；只有 anchor 后前 `7` 根 `15m` bar 全部完成后，gate 才允许生效。
- base archetype：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 四臂对比：
  - `base`
  - `ivu_allow_q476`
  - `ivu_allow_q40`
  - `ivu_size_haircut_q40`
- 统一执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 首轮只回答 5 个便宜指标：
  - `post-cost return`
  - `trade count retention`
  - `failure_before_target`
  - `target_hit_12bars`
  - `positive_window_ratio`

## 实现与验证
### 新增脚本
- `scripts/build_rank69_ivu_clean_replication.py`

### 首次执行失败与 fallback
- 首次运行因 session merge 写法导致 `KeyError: 'session_ivu'`。
- 按要求没有把整轮判失败，立刻回退做稳健改写：
  - 将 session 级参考列改成 `session_bar1_volume_ref / session_ivu_ref`
  - merge 时只带回 `open_vol_median_60 / ivu_q40_60`
- 第二次运行又因超小样本 `qcut` 分桶报错：`Bin labels must be one fewer than the number of bin edges`。
- 再次 fallback，把 `positive_window_ratio` 的时间桶逻辑改成：
  - `len >= 3` 时用等宽三桶
  - 否则退化为逐笔 bucket
- 修补后重跑成功。

## 本轮新增产物
### Artifact
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/signal_windows.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/trade_log.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/asset_summary.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/overall_summary.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/time_stability.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/parameter_stability.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/cost_trade_stability.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/setup_compare.csv`
- `reports/artifacts/scout_rank69_ivu_opening_volume_uncertainty_15m/meta.csv`

### Reader-facing 页面
- `reports/site/factors/scout_rank69_ivu_opening_volume_uncertainty_15m/report.html`
- `reports/site/reading/repo_scout/rank69_ivu_opening_volume_uncertainty_clean_replication.html`

### Queue-facing 更新
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs` 已写回本轮 verdict 与新的顺序。

## 关键结果（6bps/side）
### setup compare
- `ema_psar_long`：`base=-3.68%`，`q476=+4.22%`，`q40=+0.32%`，`size=-2.10%`
- `fib_retest_long`：`base=+1.17%`，`q476=+1.11%`，`q40=-0.62%`，`size=+0.34%`
- `breakout_short`：`base=-3.55%`，`q476=-6.04%`，`q40=-2.14%`，`size=-2.89%`

### 主变体（`ivu_allow_q40`）的 Light Stability Pack 摘要
- `mean_total_return = -0.84%`
- `positive_asset_ratio = 11.11%`
- `mean_trades = 1.78`
- `mean_trade_count_retention = 8.02%`
- `mean_failure_before_target_rate = 86.46%`
- `mean_target_hit_12bars_rate = 16.67%`
- `mean_positive_window_ratio = 8.33%`
- `10bps/side` 与 `15bps/side` 下 aggregate 继续变差：`-0.99%`、`-1.19%`

### 参数稳定性补充
- `allow_q476` 整体比 `q40` 好一些：`mean_total_return = -0.24%`、`positive_asset_ratio = 55.56%`、`mean_trade_count_retention = 38.13%`
- 但它仍没有给出足够统一、足够便宜的 shared gate 证据；更像个偶然 pocket，而不是当前桌面应升格的 paper candidate。
- `size_haircut_q40` 虽然保住了 `92.45%` 的 trade count retention，但 aggregate 仍是 `-1.55%`，说明它也不是“放行太严，改半仓就好”的简单问题。

## Hard verdict
**`Rank 69 / IVU opening-volume uncertainty gate = park / evidence pool`**

## 为什么是这个 verdict
1. `q40` 主变体在三条 archetype 上没有形成统一改善：只有 `ema_psar_long` 勉强转正，其余两条仍没有过关。
2. 过滤后的 trade retention 过低（约 `8%`），更像“砍到几乎没交易”而不是形成可用 shared gate。
3. `failure_before_target` 仍高，`target_hit_12bars` 也弱，不像 continuation gate 该有的形状。
4. `q476` 虽有局部 pocket，但跨 setup / 成本 / 参数邻域不够硬，达不到升到 `P1/P2` 的诚实门槛。

## 对交易台顺序的影响
- 本轮已消耗掉 `Rank 69` 被允许的那次最小 clean replication。
- 因为 verdict 已是 `park / evidence pool`，下一轮不该继续围着 Rank 69 做 admission 文案或 operator copy。
- 当前更诚实的 active Scout 顺序应回到：
  - `fresh source intake（优先 5m / 15m crypto）`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 新的 `Next 3` 也已按这个顺序写回 `docs/TODO.md`。

## 最小验证
- `python3 scripts/build_rank69_ivu_clean_replication.py`
  - 成功输出 `generated_at=2026-03-18 22:42 UTC`
  - 成功输出 `verdict=park / evidence pool`
- 已读取 `meta.csv / setup_compare.csv / cost_trade_stability.csv / parameter_stability.csv` 复核结论。
- 已确认 reader-facing 页面成功写出。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
