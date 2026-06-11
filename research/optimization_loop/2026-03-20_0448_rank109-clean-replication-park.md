# 2026-03-20 04:48 UTC — Rank 109 HTF premium-discount long-bias context gate clean replication → park

## Run 1 -> Run 3 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `2.2h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作仍是 `Scout Seat`，且只该拿 **`Rank 109 / HTF premium-discount long-bias context gate`** 的那唯一一手最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1669`
- 最近 optimization logs：
  - `2026-03-20_0418_rank109-htf-premium-discount-intake.md`
  - `2026-03-20_0358_rank108-clean-replication-park.md`
  - `2026-03-20_0334_rank108-prebreak-intake.md`
  - `2026-03-20_0312_rank107-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-20_0410_strategy-review.md`
  - `2026-03-20_0327_strategy-review.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 109 / HTF premium-discount long-bias context gate`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T04:39:11Z` 仍是 `new_closed_trades_appended=0`，因此当前没有新的 `P3 status-changing event` 可以挤掉 fresh Scout 主链。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 109 / HTF premium-discount long-bias context gate`**
   - 上轮已完成 `source intake + 两条轻量诚实守门`，当前是唯一合法的 queue-facing 下一手。
   - 若这轮不把它收口，就会继续占着 active Scout 主资源位，违背“先硬门槛、再分级、再限预算”。
2. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
   - 仍是最靠前的 fresh repo reserve。
   - 但在 `Rank 109` 还没拿完这次 truly verdict-changing 检查之前，不该抢本轮主资源。
3. **fresh paper / repo intake reserve**
   - 只有 `Rank 109` 明确 `hard-fail / exhausted` 后才该前移。
4. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该挤掉这轮 queue-facing Scout 主链。

结论：本轮只认领 `Rank 109` 这一条，不并开其他候选。

## 本轮认领
- 主点：`Rank 109 / HTF premium-discount long-bias context gate` 的 1 次最小 clean replication
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 执行脚本：`python3 scripts/build_rank109_htf_premium_discount_clean_replication.py`
- 复现实验冻结：`BTC/ETH/SOL 120d 15m` 本地 cache，`signal 当根及之前数据 + 上一根完整 4h bar + next-bar open + no-overlap + hold 8 bars + 6bps/side`
- 比较三臂：`baseline / long_only_discount_gate / symmetric_discount_premium_gate`
- 生成产物：
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/time_bucket_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/cost_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/trade_log.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/summary.json`
  - `reports/site/factors/scout_rank109_htf_premium_discount_15m/report.html`
  - `reports/site/reading/repo_scout/rank109_htf_premium_discount_clean_replication.html`
- 回写顶板：`docs/TODO.md`

## 结果摘要（hard verdict）
**`Rank 109 / HTF premium-discount long-bias context gate = park / evidence pool`**。

翻成人话：
- 它表面上像在改善，但主因是**把 long 样本几乎全砍掉**，而不是把 long 侧变得更好。
- `long_only_discount_gate` 结果是：`trades=61`、`trade_count_retention≈30.81%`、`mean_total_return≈-3.14%`、`positive_asset_ratio=0/3`；更关键的是 `long_trades_share=0%`，也就是它根本没有留下 long 侧样本去证明“discount 对 long 真有帮助”。
- `symmetric_discount_premium_gate` 虽然表面翻到 `mean_total_return≈+0.55%`，但只剩 **1 笔 short trade**（`trade_count_retention≈0.51%`），属于极端缩样本，不构成 deployable 证据。

## Setup / side 级诚实读法
- baseline：
  - `ema_psar_long total_return≈-13.07%`
  - `fib_retest_long total_return≈+3.08%`
  - `breakout_short total_return≈-9.41%`
- `long_only_discount_gate`：
  - **只剩 `breakout_short total_return≈-9.41%`**
  - `ema_psar_long / fib_retest_long` 被筛到没有留下可用样本
- 因此这条 `HTF discount` 线并没有把 `Fib / EMA continuation` 的 long aggregate 真正拉起来，而是把 long 侧直接筛没了。

## 为什么不继续做 Stability Pack
- 这轮已经满足“1 个真正会改变 verdict 的最小检查”。
- 当前 verdict 已明确：它不是 `paper candidate`，也不该升到 `P2`。
- 继续给它做 `Light Stability Pack` 只会变成“在空样本上继续打磨 admission 文案”，不再减少真实 gate。

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 从 `Rank 109` 切换到 **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
- 当前 active Scout 顺序应改读为：
  1. `Rank 110 / PSAR pre-flip SAR dot reclaim gate`（`P0 / fresh repo / source intake next`）
  2. `fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used / 不再默认续命`）
  4. `Rank 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  5. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 narrow paper continuity / hosted lanes / sidecar only`）
- 当前 `P2` 仍空、`P4` 仍空。
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 110 / PSAR pre-flip SAR dot reclaim gate 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 110 guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank109_htf_premium_discount_clean_replication.py`
- artifact：`reports/artifacts/scout_rank109_htf_premium_discount_15m/{overall_summary.csv,setup_summary.csv,asset_summary.csv,time_bucket_summary.csv,cost_summary.csv,trade_log.csv,summary.json}`
- reader-facing 页面：
  - `reports/site/factors/scout_rank109_htf_premium_discount_15m/report.html`
  - `reports/site/reading/repo_scout/rank109_htf_premium_discount_clean_replication.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank109_htf_premium_discount_clean_replication.py`
- 回读确认：
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank109_htf_premium_discount_15m/setup_summary.csv`
  - `reports/site/factors/scout_rank109_htf_premium_discount_15m/report.html`
  - `docs/TODO.md`

## 备注
- 本轮严格遵守 `1 个主点 + 1 个紧邻子点`：没有并开 `Rank 110`，也没有回头磨 `Rank 109` 的 intake 文案
- 当前工作区仍有大量无关脏文件；本轮未尝试混提
- 下一轮若 EMA 仍 waiting_not_due，默认应直接切 `Rank 110` 的 source intake，而不是继续停留在 `Rank 109`
