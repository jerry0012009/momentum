# 2026-03-20 06:14 UTC — Rank 110 / PSAR pre-flip SAR dot reclaim gate time stability check → park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `48m`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作只能继续落在 `Scout Seat`，且只该给 **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`** 那 1 次 truly verdict-changing 的便宜时间稳定性检查。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1687`
- 最近 optimization logs：
  - `2026-03-20_0540_rank110-clean-replication.md`
  - `2026-03-20_0513_rank110-psar-preflip-intake.md`
  - `2026-03-20_0448_rank109-clean-replication-park.md`
  - `2026-03-20_0418_rank109-htf-premium-discount-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- `manual_narrow_paper_last_run_summary.json` 本地当前未见新 summary，可确认当前没有新的 `P3 status-changing event` 可以插队。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
   - 上轮已完成 clean replication；按顶板顺序，这轮只剩那 1 次便宜时间稳定性检查。
   - 若不在这轮把它收口，就会继续无谓占着 active Scout 主资源位，违背“先硬门槛、再分级、再限预算”。
2. **fresh paper / repo intake reserve**（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
   - 只有 `Rank 110` 做完这次 truly verdict-changing 检查后，才应该接棒成为新的主资源位。
3. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该挤掉这轮 queue-facing Scout 主链。

结论：本轮只认领 `Rank 110` 的 cheap time-stability check，不并开其他候选。

## 本轮认领
- 主点：`Rank 110 / PSAR pre-flip SAR dot reclaim gate` 的 **1 次便宜时间稳定性检查**
- 紧邻子点：同步 hard verdict、reader-facing 落点、顶板顺序刷新

## 本轮动作
- 新增脚本：`scripts/build_rank110_time_stability_check.py`
- 首次执行脚本时，因 `asset_window` 漏写 `variant` 字段而报错：`KeyError: ['variant'] not in index`
- 按要求立即 fallback 修复：补上 `assign(variant=...)` 后重跑成功
- 正式执行：`python3 scripts/build_rank110_time_stability_check.py`
- 这轮完全复用上轮 clean replication 的同一份样本：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/trade_log.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/overall_summary.csv`
- 固定口径：
  - 不追新 bar
  - 不改规则
  - 不重配参数
  - 只按 `older_half / recent_half` 两半窗检查 `preflip_reclaim_long_only / preflip_reclaim_symmetric`
- 生成产物：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_window_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_asset_window_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_verdict_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_summary.json`
  - `reports/site/factors/scout_rank110_psar_preflip_reclaim_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_reclaim_time_stability.html`
- 回写：`docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## 当前硬结论
**`Rank 110 / PSAR pre-flip SAR dot reclaim gate = park / evidence pool`**。

翻成人话：
- `preflip_reclaim_long_only` 不是完全没料，但它的改善只剩 **older-half pocket**；一到 recent half，就退化成跨资产平均总收益转负，而且 `0/3` 资产为正；
- `preflip_reclaim_symmetric` 表面总表还挂正，但 retention 只剩 `≈15.15%`，recent half 也已转负，更像极薄样本 pocket；
- 因此这条线当前只配留作 **long-side optional filter note / evidence**，不再值得继续占 active Scout 主资源位，更不足以升到 `P2 / paper candidate`。

## 关键结果摘录
### `preflip_reclaim_long_only`
- overall：
  - `mean_total_return≈-1.36%`
  - `positive_asset_ratio=2/3`
  - `trade_count_retention≈43.43%`
- time stability：
  - `older_half mean_total_return≈+1.93%`，`positive_asset_ratio=2/3`
  - `recent_half mean_total_return≈-3.29%`，`positive_asset_ratio=0/3`
  - `bucket_return_spread≈-5.22%`
- per-asset half：
  - `BTC`: `+1.48% -> -0.88%`
  - `ETH`: `-3.20% -> -6.38%`
  - `SOL`: `+7.51% -> -2.62%`

### `preflip_reclaim_symmetric`
- overall：
  - `mean_total_return≈+2.52%`
  - `positive_asset_ratio=2/3`
  - `trade_count_retention≈15.15%`
- time stability：
  - `older_half mean_total_return≈+3.00%`
  - `recent_half mean_total_return≈-0.49%`
  - retention 过薄，不足以拿来推翻 long-only 失稳的主 verdict

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 默认主资源位切回：**fresh paper / repo intake reserve**
- `Rank 110` 的更诚实层级更新为：**`P0 park / evidence pool`**
- 当前更诚实的 active Scout 顺序：
  1. `fresh paper / repo intake reserve`（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
  2. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used / 不再默认续命`）
  3. `Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  4. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 narrow paper continuity / hosted lanes / sidecar only`）
- 当前 `P2` 仍空、`P4` 仍空
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则按 7.10 回 fresh paper / repo intake reserve，并且只认领 1 条新的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若新 source guard-pass，则只给它 1 次最小 clean replication；若 fresh source 也 exhausted，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank110_time_stability_check.py`
- artifact：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_window_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_asset_window_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_verdict_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_summary.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank110_psar_preflip_reclaim_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_reclaim_time_stability.html`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank110_time_stability_check.py`
- 回读确认：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_stability_verdict_summary.csv`
  - `reports/site/factors/scout_rank110_psar_preflip_reclaim_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_reclaim_time_stability.html`
  - `docs/TODO.md`

## 备注
- 本轮未混提与本轮无关的 repo 脏文件。
- 这次脚本修复属于本轮新增脚本的局部纠错，不影响既有 artifact 口径。
