# 2026-03-18 13:42 UTC — Rank 56 最小 clean replication（liquidation-map path overlay）

## 本轮执行定位（按 TRADING DESK BOARD）
- `Run 1` 先做 EMA due-check：`ema_paper_trading_due_guardrail_snapshot.csv` 当前 5 条 lane 全部仍是 `waiting_not_due`。
  - 美股 `2026-03-18 20:00 UTC`
  - Crypto `2026-03-19 00:00 UTC`
  - A 股三条 lane `2026-03-19 07:00 UTC`
- 因此本轮合法主动作落在 `Run 2`，认领 **`Rank 56 / liquidation-map path overlay` 最小 clean replication**。

## 本轮主点（1）
完成 `Rank 56` 的唯一那手最小 clean replication（复用历史样本，不追新 bar）：
- 脚本：`scripts/build_rank56_liquidation_map_clean_replication.py`
- 复用：`BTC/ETH/SOL 120d 15m` cache + 已有 signal 前 `aggTrades` 缓存
- 三臂对照：`base` / `binary_path_gate` / `size_tilt`
- 执行冻结：`next-bar open + no-overlap + hold 8 bars`

## 紧邻子点（1）
把 verdict 写回 authoritative board，并同步 reader-facing 可见落点：
- `docs/TODO.md` 新增 `2026-03-18 13:40 UTC` 补充（含 hard verdict + Next 3 更新）
- `reports/site/factors/scout_rank56_liquidation_map_path_overlay_15m/report.html`
- `reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_clean_replication.html`
- artifact：`reports/artifacts/scout_rank56_liquidation_map_path_overlay_15m/overall_summary.csv`

## 结果（硬结论）
- `6bps/side` setup-level：
  - `ema_psar_long`：`base≈+1.63%` / `gate≈+0.74%` / `size≈+1.69%`
  - `fib_retest_long`：`base≈+0.03%` / `gate≈-0.22%` / `size≈-0.04%`
  - `breakout_short`：`base≈-2.49%` / `gate≈-2.02%` / `size≈-2.85%`
- **hard verdict：`Rank 56 = P1 weak candidate / evidence pool`**。
  - 含义：当前不再占 clean-replication queue 主资源；若后续继续认领，只能走 `P1` 预算内的便宜诚实检查，不再反复磨 intake 文案。

## 对当前 Next 3 的影响
- 更新后顺序：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 55 / order-imbalance crash-risk overlay 的 1 次便宜时间稳定性检查（仅当 EMA 仍 waiting_not_due）`
  - `Run 3 = 若 Rank 55 也不能给出更高层 verdict，再比较 Rank 35b > Rank 16b > tiny-live plumbing；若出现 fresh intake，则仍按 fresh intake 优先`

## 最小验证
- 成功执行：`python3 scripts/build_rank56_liquidation_map_clean_replication.py`
- stdout：`verdict=P1 weak candidate / evidence pool`
- 输出文件存在：
  - `reports/artifacts/scout_rank56_liquidation_map_path_overlay_15m/{meta.csv,overall_summary.csv,setup_compare.csv}`
  - 对应 reader-facing 页面已生成

## fallback 记录（按 8.1）
- 首次自动写回 `TODO.md` 失败，原因是脚本里 `replace_once` 依赖 exact block；同时一次脚本级改写引入了字符串换行语法错误（`unterminated string literal`）。
- 本轮已执行 fallback：`read + 定位 + 稳健改写`，将 `update_todo` 改为锚点插入（`anchor + marker`），再重跑脚本，写回成功。

## Git 备注
- 工作区存在大量与本轮无关的既有脏文件；本轮未提交，避免混提。