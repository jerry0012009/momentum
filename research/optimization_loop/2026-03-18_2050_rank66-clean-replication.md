# Rank 66 / exec-TF switch alignment gate minimal clean replication

## 轮次定位
- 时间：2026-03-18 20:50 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 66 minimal clean replication`
- 紧邻子点：`queue-facing 更新（TODO 顶板）`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无 `due-now / overdue`；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- `TRADING DESK BOARD` 最新授权顺序：`Run 1 = EMA due-check only`，`Run 2 = Rank 66 minimal clean replication`，`Run 3 = 再比较 Rank 67 / regime-matrix ...`。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 66` 对应脚本、artifact、reader-facing 页面、TODO 顶板与本轮日志，不做混提。

## 本轮最小实验口径
- 数据：复用 `BTC/ETH/SOL 120d 15m` 本地 cache，并补 Binance spot `5m` cache；`1h / 4h` 从同一条 `5m` 数据 resample。
- base archetype：`ema_psar_long`、`fib_retest_long`、`breakout_short`。
- 四臂固定为：
  1. `base_15m_only`
  2. `always_5m_confirm`
  3. `alignment_switch`
  4. `alignment_switch_plus_pressure`
- 对齐定义：`4H bias` 与 `1H trend` 同向（相对各自 `EMA200`）时，允许 `5m BOS`；否则坚持 `15m BOS`。
- 轻 pressure：`bodyPct >= 0.55` 且 `volume > SMA20(volume)`。
- 执行统一冻结到：`signal 当根及之前数据 + next-bar open + no-overlap + hold 120m`。

## 本轮新增产物
1. 脚本：
   - `scripts/build_rank66_exec_tf_switch_alignment_clean_replication.py`
2. Artifact：
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/signal_windows.csv`
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/trade_log.csv`
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/time_pockets.csv`
   - `reports/artifacts/scout_rank66_exec_tf_switch_alignment_15m/setup_compare.csv`
3. Reader-facing 页面：
   - `reports/site/factors/scout_rank66_exec_tf_switch_alignment_15m/report.html`
   - `reports/site/reading/repo_scout/rank66_exec_tf_switch_alignment_clean_replication.html`
4. Queue-facing 更新：
   - `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已补 `2026-03-18 20:48 UTC` 最新块。

## 关键结果（6bps / side）
- `ema_psar_long`：
  - `base≈-8.38%`
  - `always5≈-0.31%`
  - `switch≈-5.91%`
  - `switch+pressure≈-4.79%`
- `fib_retest_long`：
  - `base≈-0.42%`
  - `always5≈0.30%`
  - `switch≈-0.42%`
  - `switch+pressure≈-0.42%`
- `breakout_short`：
  - `base≈-3.14%`
  - `always5≈1.21%`
  - `switch≈-1.24%`
  - `switch+pressure≈-1.87%`

## Hard verdict
**`Rank 66 / exec-TF switch alignment gate = P1 weak candidate / evidence pool`**

## 为什么是这个 verdict
- `alignment_switch` 的确比纯 `15m` 在 `ema_psar_long` 与 `breakout_short` 上少亏，但没有稳定赢过 `always_5m_confirm` 这条更便宜的对照臂。
- `fib_retest_long` 上 `switch` 基本没有增量，说明“HTF 对齐 -> execution TF 切换”还没有形成足够统一的 shared gate。
- `switch+pressure` 能进一步少亏一点，但它并没有把 `Rank 66` 直接推进到 `P2`；更像说明：这条线值得保留证据，但不值得继续霸占默认主资源位。
- 因此更诚实的读法是：**保留为 `P1` 证据池，不升格；主资源转去下一条 active Scout。**

## 对交易台顺序的影响
- `Rank 66` 已消耗完当前允许的 `1 次 minimal clean replication` 预算，不应继续在 fast-lane 队首反复打磨。
- 当前更诚实的 active Scout 顺序更新为：
  - `Rank 67 / regime-matrix shared-state gate`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 更新后的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = 若 Rank 66 verdict 不足以升到下一层，则比较 Rank 67 / regime-matrix shared-state gate`
  - `Run 3 = 若 Rank 67 guard-passed 且 EMA 仍 waiting_not_due，则给 Rank 67 1 次最小 clean replication；若 fresh source 仍未 admitted，则按 7.10 再从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条 5m/15m crypto source`

## 最小验证
- 成功执行：`python3 scripts/build_rank66_exec_tf_switch_alignment_clean_replication.py`
- 结果：脚本完成并输出 `verdict=P1 weak candidate / evidence pool`
- 备注：运行中仅出现 pandas `FutureWarning(observed=False)`，不影响本轮 artifact 与 verdict。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
