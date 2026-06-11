# 2026-03-20 05:40 UTC — Rank 110 / PSAR pre-flip SAR dot reclaim gate clean replication（keep_P1 / mixed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `1.3h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作只能切到 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1683`
- 最近 optimization logs：
  - `2026-03-20_0513_rank110-psar-preflip-intake.md`
  - `2026-03-20_0448_rank109-clean-replication-park.md`
  - `2026-03-20_0418_rank109-htf-premium-discount-intake.md`
  - `2026-03-20_0358_rank108-clean-replication-park.md`
- 最近 strategy review：`2026-03-20_0511_strategy-review.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- `manual_narrow_paper_last_run_summary.json` 仍是 `new_closed_trades_appended=0`，因此当前没有新的 `P3 status-changing event` 可以挤掉 fresh Scout 主链。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，这轮只差那 1 次最小 clean replication。
   - 直接服务 `EMA / PSAR raw alpha focus`，而且比重新开新 intake 更便宜。
2. **fresh paper / repo intake reserve**（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
   - 只有 `Rank 110` clean replication 明确失真/预算用尽后才该前移。
3. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该挤掉这轮 queue-facing Scout 主链。

结论：本轮只认领 `Rank 110` 的最小 clean replication，不并开其他候选。

## 本轮认领
- 主点：`Rank 110 / PSAR pre-flip SAR dot reclaim gate` 的 **1 次最小 clean replication**
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 新增脚本：`scripts/build_rank110_psar_preflip_clean_replication.py`
- 执行：`python3 scripts/build_rank110_psar_preflip_clean_replication.py`
- 统一冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars + 6bps/side`
- 固定 cache：`BTCUSDT / ETHUSDT / SOLUSDT 120d 15m`
- 比较三臂：
  - `baseline`
  - `preflip_reclaim_long_only`
  - `preflip_reclaim_symmetric`
- reclaim 定义收紧为：
  - `pre_flip_dot` 只能取最近一次 flip 前最后一个已确认 `SAR dot`
  - 只允许在 flip 后 `1~4` 根内、当前 bar 满足 `open/close` 穿回该 dot 时放行
  - 不允许 future bar 延长窗口，不允许同 bar 成交，不允许事后重配 `N`

## 当前硬结论
**`Rank 110 = keep_P1 / mixed but honest`**。

翻成人话：
- `preflip_reclaim_long_only` 确实把 desk 级 `mean_total_return` 从 `baseline≈-6.47%` 收窄到 `≈-1.36%`，`positive_asset_ratio` 从 `1/3` 提到 `2/3`；
- 但它是靠把总交易数压到 `≈43.43%`、并把这层 gate 收窄成 **long-side optional filter** 才拿到的；
- `preflip_reclaim_symmetric` 虽表面翻正到 `≈+2.52%`，却只剩 `30` 笔交易（retention `≈15.15%`），其中 `breakout_short` 只剩 `5` 笔，明显更像极端缩样本，而不是可部署 shared gate；
- 因此这条线当前只够留在 **`P1 weak candidate / asymmetric long filter note`**，不足以升到 `P2 / paper candidate`。

## 关键结果
### desk 级（6bps/side）
- `baseline`
  - `mean_total_return≈-6.47%`
  - `positive_asset_ratio=1/3`
  - `trade_count_retention=100.00%`
  - `false_follow_through_4bars≈53.03%`
- `preflip_reclaim_long_only`
  - `mean_total_return≈-1.36%`
  - `positive_asset_ratio=2/3`
  - `trade_count_retention≈43.43%`
  - `false_follow_through_4bars≈52.33%`
  - `long_mean_net_return≈+0.21%`
- `preflip_reclaim_symmetric`
  - `mean_total_return≈+2.52%`
  - `positive_asset_ratio=2/3`
  - `trade_count_retention≈15.15%`
  - `false_follow_through_4bars≈50.00%`
  - 但这是明显缩样本：`30` 笔总交易，不能诚实包装成 shared gate

### setup 级（6bps/side）
- `ema_psar_long`：`baseline≈-13.07% -> preflip_reclaim_long_only≈+2.29%`
- `fib_retest_long`：`baseline≈+3.08% -> preflip_reclaim_long_only≈+3.02%`
- `breakout_short`：
  - `baseline≈-9.41%`
  - `preflip_reclaim_long_only≈-9.41%`（完全没改善）
  - `preflip_reclaim_symmetric≈+2.24%`，但 retention 只剩 `≈10.98%`，不够诚实

### asset 级（6bps/side, long_only）
- `BTC≈+0.60%`
- `ETH≈-9.58%`
- `SOL≈+4.89%`
- 说明它不是跨资产稳定 shared gate，更像偏 long-side / asset-dependent 的可选过滤层

### time bucket（6bps/side, long_only）
- `bucket_1≈+1.57%`
- `bucket_2≈+4.02%`
- `bucket_3≈-9.68%`
- 因此下一手若还给预算，最值钱的是 **1 次便宜时间稳定性检查**，而不是继续 admission 文案

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- 当前更诚实的 active Scout 顺序：
  1. `Rank 110 / PSAR pre-flip SAR dot reclaim gate`（`P1 / cheap time-stability next`）
  2. `fresh paper / repo intake reserve`
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
  4. `Rank 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  5. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 continuity / hosted lanes / sidecar only`）
- 当前 `P2` 仍空、`P4` 仍空。
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 110 / PSAR pre-flip SAR dot reclaim gate 1 次便宜时间稳定性检查`
  3. `Run 3 = 若 Rank 110 仍不能升到下一层，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank110_psar_preflip_clean_replication.py`
- artifacts：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/time_bucket_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/cost_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/trade_log.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/summary.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank110_psar_preflip_reclaim_15m/report.html`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_reclaim_clean_replication.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank110_psar_preflip_clean_replication.py`
- 回读确认：
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank110_psar_preflip_reclaim_15m/setup_summary.csv`
  - `reports/site/factors/scout_rank110_psar_preflip_reclaim_15m/report.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只完成了最小 clean replication，**没有**把它升格成 shared gate 或 paper candidate。
- 当前最诚实的读法仍是：它更像 `EMA / Fib long-side continuation` 的可选过滤层，而不是多空对称默认 admission。
- 当前工作区有大量与本轮无关的脏文件，因此不安全混提。

## Commit hash
- 未提交。
- 原因：工作区存在大量无关脏文件（`1683` 项），本轮只做局部产物与顶板回写，不适合混提。
