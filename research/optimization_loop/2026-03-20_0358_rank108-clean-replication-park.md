# 2026-03-20 03:58 UTC — Rank 108 prebreak higher-low pressure ladder clean replication（park）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前无 `due-now / overdue` lane
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`（约 `3.0h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD`，这轮主资源必须继续留在 `Scout Seat`，且只允许认领 `Rank 108` 的那 1 次最小 clean replication。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1659`
- 最近 optimization logs：
  - `2026-03-20_0334_rank108-prebreak-intake.md`
  - `2026-03-20_0312_rank107-clean-replication-park.md`
  - `2026-03-20_0254_rank107-mtf-chop-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T03:38:45Z` 仍是 `new_closed_trades_appended=0`
  - 因此当前没有新的 `P3 status-changing event` 可以挤掉 fresh Scout 主链

## Active Scout 候选边际比较（先比较后认领）
1. **Rank 108 / prebreak higher-low pressure ladder context gate**
   - 上轮刚完成 intake + 两条轻量诚实守门；按顶板顺序，这轮只剩 1 次 truly verdict-changing 的最小 clean replication。
2. **HTF premium/discount long-bias context gate**
   - 仍是紧邻 fresh repo reserve；只有当 Rank 108 clean replication 收口为 `hard-fail / exhausted` 时，才该前移到主资源位。
3. **fresh paper / repo intake reserve（7.10）**
   - 只在当前 fresh repo reserve 也 exhausted 时才切过去。
4. **旧 evidence_pool / Rank 17 low-frequency health-check fallback / tiny-live plumbing**
   - 当前都不该抢主资源位。

结论：本轮只认领 `Rank 108` 这一条，不并开其他候选。

## 本轮认领
- 主点：`Rank 108 / prebreak higher-low pressure ladder context gate` 最小 clean replication
- 紧邻子点：同步 hard verdict、reader-facing 落点、顶板顺序刷新

## 本轮动作
- 执行脚本：`python3 scripts/build_rank108_prebreak_higherlow_clean_replication.py`
- 固定复用：`BTC/ETH/SOL 120d 15m` 本地 cache
- 冻结执行口径：
  - `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars + 6bps/side`
  - 比较三臂：`baseline / ladder_hard_gate / ladder_plus_smallbody_context`
- 最小规则冻结：
  - `ladder_hard_gate`：对 long 侧要求最近 `16` 根内已有确认后的 `>=2` 级 higher-low ladder；对 short 侧只把它当 adverse long-context veto
  - `ladder_plus_smallbody_context`：再额外要求 `body_ratio<=0.30 且 close>=level_ref`
  - base setup 仍沿用现有 `ema_psar_long / fib_retest_long / breakout_short`

## 当前硬结论
**`Rank 108 = park / evidence pool`**。

翻成人话：
- 它在 `ema_psar_long` 上确实有一点 long-side context 的减亏味道：
  - `baseline total_return≈-13.07%`
  - `ladder_hard_gate≈-0.22%`
  - 但 retention 只剩 `≈28.99%`
- 可一旦放回整个 desk 看，就不够诚实：
  - `fib_retest_long` 没被一起带起来：`≈+3.08% -> ≈-0.74%`
  - `breakout_short` 反而更差：`≈-9.41% -> ≈-11.38%`
  - 更严格的 `ladder_plus_smallbody_context` 基本只剩缩样本：`trade_count_retention≈30.81%`
  - 跨资产也没有翻正：`positive_asset_ratio = 0/3`
- 因此最诚实的 desk 读法是：把它留成 **long-side context / evidence note** 就够了，不值得继续占默认 Scout 主资源位，更不值得往 `P2 / paper candidate` 推。

## 关键结果摘录（6bps/side）
- overall：
  - `baseline`: `mean_total_return≈-6.47%`，`positive_asset_ratio=1/3`，`false_follow_through_4bars≈53.03%`
  - `ladder_hard_gate`: `mean_total_return≈-4.11%`，`positive_asset_ratio=0/3`，`trade_count_retention≈46.97%`
  - `ladder_plus_smallbody_context`: `mean_total_return≈-3.14%`，`positive_asset_ratio=0/3`，`trade_count_retention≈30.81%`
- setup 维度：
  - `ema_psar_long`：`baseline≈-13.07% -> ladder_hard_gate≈-0.22%`
  - `fib_retest_long`：`baseline≈+3.08% -> ladder_hard_gate≈-0.74%`
  - `breakout_short`：`baseline≈-9.41% -> ladder_hard_gate≈-11.38%`
- time buckets：
  - `ladder_hard_gate` 只有 `bucket_1` 勉强转正（`≈+2.65%`）
  - `bucket_2 / bucket_3` 仍明显为负，因此不足以写成稳定 shared gate

## 本轮交付（deployable artifact）
- script：`scripts/build_rank108_prebreak_higherlow_clean_replication.py`
- artifact：
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/time_bucket_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/cost_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/trade_log.csv`
- reader-facing 页面：
  - `reports/site/factors/scout_rank108_prebreak_higherlow_pressure_ladder_15m/report.html`
  - `reports/site/reading/repo_scout/rank108_prebreak_higherlow_pressure_ladder_clean_replication.html`

## 对顶板的直接影响
- `Paper Seat = EMA / waiting_not_due`
- `Live Seat = 暂空`
- `Rank 108` 从 active Scout 主资源位退出，压回 `park / evidence pool`
- `Scout Seat` 默认切到：`HTF premium/discount long-bias context gate`
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 HTF premium/discount long-bias context gate 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 HTF premium/discount guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank108_prebreak_higherlow_clean_replication.py`
- 回读确认：
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank108_prebreak_higherlow_pressure_ladder_15m/setup_summary.csv`
  - `reports/site/factors/scout_rank108_prebreak_higherlow_pressure_ladder_15m/report.html`
  - `docs/TODO.md`

## 备注
- 这轮没有并开 `HTF premium/discount` intake（遵守 1 主点 + 1 紧邻子点约束）
- `Rank 108` 的可保留价值仅剩 `long-side context evidence`，不再默认继续给 Light Stability Pack
- 工作区仍有大量无关脏文件；本轮未尝试混提
