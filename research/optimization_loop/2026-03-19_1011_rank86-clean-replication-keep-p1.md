# 2026-03-19 10:11 UTC — Rank 86 最小 clean replication（P1 保留）

## 为什么这轮选这个
- 先按 `Run 1` 执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`：返回 `waiting_not_due`（无 `due-now / overdue`，最近 due 仍是美股 20:00 UTC）。
- `manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 P3 状态变化需要抢主资源。
- 按 `Next 3`，本轮合法主动作应是 `Run 2 / Rank 86 minimal clean replication`，不该回头做 P3 continuity。

## 做了什么改动（1 主点）
1. 新增并执行最小复现实验脚本：
   - `scripts/build_rank86_signalpro_penetration_clean_replication.py`
2. 固定实验口径（防偷看）：
   - 数据：`BTC/ETH/SOL 120d 15m` 本地 cache
   - 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
   - setup：`breakout_short / ema_psar_follow_short / fib_retest_short`
   - 对比臂：`baseline / penetration_only / atr_only / pen_plus_atr / pen_ge_0_10_plus_atr`
3. 产出 reader-facing 页面与 artifact：
   - `reports/site/factors/scout_rank86_signalpro_penetration_atr_15m/report.html`
   - `reports/site/reading/repo_scout/rank86_signalpro_penetration_atr_clean_replication.html`
   - `reports/artifacts/scout_rank86_signalpro_penetration_atr_15m/{overall_summary.csv,setup_summary.csv,asset_setup_summary.csv,meta.csv}`
4. 局部更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：把 Rank 86 状态从 intake 阶段推进到 clean replication hard verdict，并把下一轮限制为仅 1 次 Light Stability Pack 最小检查。

## 验证 / 证据
- `overall_summary.csv`（6bps/side）关键值：
  - `baseline`：`mean_total_return=-6.65%`，`positive_asset_ratio=0/3`
  - `pen_plus_atr`：`mean_total_return=+0.22%`，`positive_asset_ratio=2/3`，`retention≈38.97%`
  - `penetration_only`：`mean_total_return=-5.95%`（说明只看 penetration 不够）
- `meta.csv` 当前 verdict：
  - **`P1 keep / worth one Light Stability Pack check`**
- setup 级别上，`fib_retest_short + pen_plus_atr`改善最明显；`breakout_short`仍偏弱，当前不支持把这条线直接升到 P2。

## 本轮 hard verdict
- **`Rank 86 / SignalPro penetration×ATR admission = P1 keep / worth one Light Stability Pack check`**
- 含义：
  - 已完成 `source intake -> clean replication` 两步；
  - 下一轮只应给它 **1 次真正会改变 verdict** 的最小 Light Stability 检查（默认先做时间稳定性）；
  - 检查不过则直接 `park`，通过才进 `P2 / paper candidate pool`。

## 风险 / 边界
- 当前结论仍是 fast-lane 口径，尚未做完整 Light Stability Pack（时间/参数/跨标的/成本交易数四项中的后续项）。
- 工作区脏文件很多（`git status --short | wc -l = 1372`），本轮未做提交，避免混提无关改动。

## 下一步建议
1. 仅做 Rank 86 的 **1 次时间稳定性检查**（同口径切片），并当轮给出 `P2/park`。
2. 若 time stability 未过，立即 park，按 7.10 回到 fresh intake（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）。
3. 若通过，则按规则升到 `P2 / paper candidate pool`，不要继续磨 intake 文案。

## Commit hash
- 未提交（本轮遵循“有大量无关脏文件时不混提”）。
