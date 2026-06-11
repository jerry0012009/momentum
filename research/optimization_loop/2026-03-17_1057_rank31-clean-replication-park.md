# 2026-03-17 10:57 UTC · Rank 31 clean replication verdict sync (park)

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Run 1 / EMA` 仍为 `waiting_not_due`（require-due 守门返回无 `due-now / overdue`），按板子自动切到 Scout，不允许 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short`：存在大量与本轮无关脏文件（历史产物 + 站点页 + 脚本），本轮仅做 selective 改动，不混提。
- 最近 optimization runs：`1036 rank31-intake`、`1029 rank30-clean-replication-park`、`1007 rank30-intake`、`1006 rank29-p3-monitoring`。
- `Paper Seat / EMA`：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 显示无 due-now，最近到点仍为：
  - 美股 1d+1wk：约 9h 后
  - Crypto 1d+1wk：约 13h 后
  - 创业板ETF 1d：约 20h 后
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：当前都无真实 `append/review` row；继续补 wiring 边际价值低。
- `Rank 30`：上一轮已完成最小 clean replication 并 `park`，不应重开。
- `Rank 31`：上一轮仅 intake，尚缺“那 1 次允许的最小 clean replication”来给硬结论；边际价值最高。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 31 chanlun-pro second-buy` 的 1 次最小 clean replication（固定 `BTC/ETH/SOL 120d 15m` cache；不追新 bar）。
- **紧邻子点**：把 verdict 回写到 `TODO desk board + reader-facing 页面`，避免继续停在 intake 口径。

## 两条轻量诚实守门（进入 replication 前）
1. 规则可写成 `trade on / trade off`（baseline / structural reclaim / center retest reclaim 三档）。
2. 仅用因果确认 swing/center，不回填未来信息（避免 lookahead / repaint / leakage）。

## 产物与改动
1. 新增脚本
- `scripts/build_rank31_chanlun_second_buy_clean_replication.py`

2. 新增 artifact
- `reports/artifacts/scout_rank31_chanlun_second_buy_15m/overall_summary.csv`
- `reports/artifacts/scout_rank31_chanlun_second_buy_15m/asset_summary.csv`
- `reports/artifacts/scout_rank31_chanlun_second_buy_15m/trades_primary_6bps.csv`
- `reports/artifacts/scout_rank31_chanlun_second_buy_15m/meta.csv`
- 以及按资产 frame/trades 明细

3. 新增/更新 reader-facing 页面
- `reports/site/factors/scout_rank31_chanlun_second_buy_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/rank31_chanlun_second_buy_clean_replication.html`
- `reports/site/reading/trendline_alpha_scout/report.html`（Rank 31 卡更新为 clean replication 后结论）

4. 更新 command board
- `docs/TODO.md` 中 Rank 31 从 `admit_to_clean_replication_queue` 更新为 `park / evidence pool`
- `Next 3` 顶部说明同步为：Rank 31 最小 clean replication 已落地，后续应回到 fresh intake 边际价值比较

## 硬结论（hard verdict）
- **Rank 31 = `park / evidence pool`**
- 主证据（6bps/side，跨资产均值）：
  - `raw_pullback_recovery_baseline`: `mean_total_return≈-15.46%`，`positive_asset_ratio=1/3`
  - `structural_higher_low_reclaim`（主变体）: `mean_total_return≈-31.30%`，`positive_asset_ratio=0/3`，`mean_trades≈292.0`，`mean_false_reclaim_ratio≈35.04%`，`mean_no_trade_ratio≈91.62%`
  - `center_breakout_retest_reclaim`: `mean_total_return≈-41.25%`，`positive_asset_ratio=0/3`
- 结论解释：三档都未把候选拉进 `P1/P2`；按限预算规则应压回 `park`，而不是继续磨 intake 文案。

## 最小验证
已执行：
1. `python3 scripts/build_rank31_chanlun_second_buy_clean_replication.py`
2. `python3 -m py_compile scripts/build_rank31_chanlun_second_buy_clean_replication.py`
3. 抽查：
   - `docs/TODO.md` Rank 31 行已变为 `park / evidence pool`
   - `reports/site/reading/trendline_alpha_scout/report.html` Rank 31 卡已显示 `park / evidence pool`

## fallback 记录（按 8.1）
- 本轮未触发 `edit exact text mismatch`，无需 fallback。

## commit
- 未提交（当前仓库有大量本轮无关脏文件，避免混提）。
