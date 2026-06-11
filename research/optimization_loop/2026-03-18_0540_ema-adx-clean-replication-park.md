# 2026-03-18 05:40 UTC — EMA-ADX-VOL skeleton 最小 clean replication（hard verdict: park）

## 为什么这次选这个
- 先按 `TRADING DESK BOARD -> Next 3 bot3 runs` 检查：
  - `Run 1 / EMA` 仍是 `running paper / waiting_not_due`（A 股下次 close 仍是 07:00 UTC，非 due-now）。
  - `Run 2` 当时明确是 `EMA-ADX-VOL skeleton minimal clean replication`。
  - `Run 3` 才是 `Rank 35b / tiny-live plumbing` fallback。
- 因此本轮只认领 1 个主点：把 `Rank 47 / EMA-ADX-VOL skeleton` 在固定历史样本上做完唯一那手最小 clean replication，并给出硬结论。

## 做了什么改动
### 主点（Scout Seat）
1. 新增脚本：
   - `scripts/build_repo_ema_adx_vol_skeleton_clean_replication.py`
2. 运行最小复现（复用本地 cache，不做重型下载）：
   - `python3 scripts/build_repo_ema_adx_vol_skeleton_clean_replication.py`
3. 产出 artifact：
   - `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/asset_summary.csv`
   - `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/overall_summary.csv`
   - `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/time_stability_summary.csv`
   - `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/trade_log.csv`
   - `reports/artifacts/scout_repo_ema_adx_vol_skeleton_15m/summary.csv`

### 紧邻子点（authoritative 写回）
4. 最小更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`：
   - 新增 `2026-03-18 05:38 UTC` 补充，写回本轮 hard verdict 与下一轮排班含义。

## 验证 / 证据
- 固定口径：`BTC/ETH/SOL 120d 15m`、`next-bar open + no-overlap + hold 8 bars`、`6/10/15/20bps per side`。
- 对照五臂：`EMA_stack_only / +ADX_DI / +volume_gate / +range_filter / full_stack`。
- 6bps/side 跨资产结果（来自 `overall_summary.csv`）：
  - `EMA_stack_only`：`mean_total_return≈-72.52%`，`positive_asset_ratio=0/3`，`mean_trades≈1170.3`，`mean_false_start_4bars≈67.76%`
  - `+ADX_DI`：`≈-54.10%`，`0/3`，`≈621.3`，`≈68.61%`
  - `+volume_gate`：`≈-43.16%`，`0/3`，`≈455.3`，`≈76.71%`
  - `+range_filter`：`≈-52.14%`，`0/3`，`≈807.3`，`≈70.83%`
  - `full_stack`：`≈-18.93%`，`0/3`，`≈210.3`，`≈74.92%`
- Time stability（主臂 `full_stack @6bps`）：
  - `bucket_1≈-2.59% / 33.33%`
  - `bucket_2≈-7.49% / 33.33%`
  - `bucket_3≈-9.95% / 0.00%`

## 当前硬结论
- **`EMA-ADX-VOL skeleton = park / evidence pool`**。
- 原因：亏损收敛主要来自交易数大幅压缩（`trade_count_retention≈17.97%`），不是跨资产 pocket 转正；目前更像 execution veto 模板，不应直接升格为新的 raw-alpha 候选。

## reader-facing 落点
- 新页面：
  - `reports/site/factors/scout_repo_ema_adx_vol_skeleton_15m/report.html`

## 风险 / 边界
- 本轮是最小 clean replication，不是完整 deployment 评估。
- 未继续扩展到新样本窗口或额外参数网格，避免在同一候选上过度 micro-slicing。

## 下一步建议
1. 若下一轮 `EMA` 仍 `waiting_not_due`，优先回到 **fresh paper/repo intake**（先按 7.10 从 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 认领）。
2. 若这轮 fresh intake 仍无合格 source，再回退 `Rank 35b / Run 3 tiny-live plumbing`。

## Commit hash
- 未提交。
- 原因：当前工作区存在大量与本轮无关脏文件，不能安全混提。
