# Rank 64 / pullback-quality score gate clean replication → park

## 轮次定位
- 时间：2026-03-18 19:38 UTC
- 席位：`Scout Seat`
- Desk 状态：`Paper Seat / EMA = running paper / waiting_not_due`；`Live Seat = 暂空`
- 本轮认领：`1 个主点 = Rank 64 minimal clean replication`
- 紧邻子点：无（只做最小 reader-facing 落点 + TODO 回写）

## 开始前检查
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs` 已先复核。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无 `due-now / overdue` lane；最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不做混提，只追加本轮最小产物。

## 为什么这轮还是 Rank 64
- 按上一轮权威板，`Run 1` 真实仍是 `waiting_not_due`，因此不能空转。
- 当前 active Scout 中，`Rank 64 / pullback-quality score gate` 是已经 `guard-passed` 的唯一顺序候选；先把这条线用现有历史样本做掉，比提前切去更高摩擦的 perp / execution 状态数据更符合 desk 当前预算口径。

## 本轮做了什么
1. 新增并运行脚本：`scripts/build_rank64_pullback_quality_clean_replication.py`
2. 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；不追新 bar、不做重下载。
3. 在三条 base archetype 上做最小 shared replication：
   - `ema_psar_long`
   - `fib_retest_long`
   - `breakout_short`
4. 四臂统一冻结为：
   - `base`
   - `base+zone`
   - `base+zone+vol`
   - `base+full_score`
5. 执行口径统一为：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
6. 产出 reader-facing 与 artifact：
   - `reports/site/factors/scout_rank64_pullback_quality_score_15m/report.html`
   - `reports/site/reading/repo_scout/rank64_pullback_quality_score_clean_replication.html`
   - `reports/artifacts/scout_rank64_pullback_quality_score_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank64_pullback_quality_score_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank64_pullback_quality_score_15m/trade_log.csv`
   - `reports/artifacts/scout_rank64_pullback_quality_score_15m/signal_windows.csv`
7. 回写 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把 Rank 64 结果从 active Scout 队列里移除。

## 最小 replication 结果
### 6 bps / side 总览
- `base ≈ -1.55%`，`mean_trades ≈ 22.1`
- `base+zone ≈ -0.54%`，`trade_count_retention ≈ 34.35%`
- `base+zone+vol ≈ -0.87%`，`trade_count_retention ≈ 16.52%`
- `base+full_score ≈ -0.20%`，`positive_asset_ratio ≈ 33.33%`，`mean_trades ≈ 2.9`，`trade_count_retention ≈ 12.41%`

### 直白读法
- `zone` 这层确实比裸 `base` 少亏，但还没把三资产样本拉回 admission 线。
- 一旦把 `volPts + triggerPts` 一起压到 `full_score_80`，改善主要来自**把样本切很薄**，不是形成稳定的 shared confirmation。
- `full_score_80` 下平均每资产只剩不到 `3` 笔，`trade_count_retention ≈ 12.41%`，而且 `positive_asset_ratio` 只有 `33.33%`；这不够支持继续给它 Light Stability Pack 预算。

## Hard verdict
- **`Rank 64 / pullback-quality score gate = park / evidence pool`**

## 对交易台指挥板的影响
- 当前更诚实的 active Scout 顺序更新为：
  - `perp-stress resetComplete / re-arm gate`
  - `exec-TF switch alignment gate`
  - `regime-matrix shared-state gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 因此新的 `Next 3` 应是：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh source 比较 perp-stress resetComplete / re-arm gate > exec-TF switch alignment gate > regime-matrix shared-state gate`
  - `Run 3 = 若 fresh source 也 exhausted，再回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 验证
- 成功运行：`python3 /root/clawd/jerry/momentum/scripts/build_rank64_pullback_quality_clean_replication.py`
- 已确认产物存在：
  - `reports/site/factors/scout_rank64_pullback_quality_score_15m/report.html`
  - `reports/site/reading/repo_scout/rank64_pullback_quality_score_clean_replication.html`
  - `reports/artifacts/scout_rank64_pullback_quality_score_15m/overall_summary.csv`

## 提交
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
