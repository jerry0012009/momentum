# 2026-03-20 20:47 UTC — Rank 128 / MAX(5m) impulse confirmation tier / minimal clean replication

## 本轮先核对的东西
- repo：`master`；`git status --short` 仍显示大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：最新已留痕是 `2026-03-20 20:28 UTC / Rank 128 source intake + 两条轻量诚实守门`。
- `Paper Seat`：这轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果仍是 **`EMA = waiting_not_due`**；当前无 `due-now / overdue` lane，最近 due 仍是 `Crypto 1d+1wk -> 约 3.3 小时后到点`。
- hosted paper lanes：`manual_narrow_paper_last_run_summary.json` 这轮没有新的 `P3 status-changing event` 插队，因此仍不回头占用 continuity 预算。

## 为什么这轮合法主动作仍是 Rank 128
按 `docs/TODO.md` 顶板 `2026-03-20 20:28 UTC` 最新排班：
1. `Run 1 = EMA due-check first`
2. 若 EMA 仍 `waiting_not_due`，`Run 2 = Rank 128 / MAX(5m) impulse confirmation tier 1 次最小 clean replication`
3. 若 `Rank 128 clean replication hard-fail / exhausted`，`Run 3 = 回 fresh intake reserve`

本轮满足第 2 条，因此只认领 **`Rank 128`** 这 1 个主点，不并开其他候选。

## 本轮实际执行
### 1. 真实先做 EMA due-check
实际运行：

`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果继续如实返回：当前仍无 `due-now / overdue` lane，`Crypto 1d+1wk` 只是 `due_soon`，所以这轮不能伪 refresh，也不能空转。

### 2. 新增 clean-room 脚本
- `scripts/build_rank128_max5m_impulse_confirmation_tier_clean_replication.py`

### 3. 冻结实验口径
统一只跑这 1 次最小实验：
- 资产：`BTC / ETH / SOL`
- 周期：`120d 5m+15m`
- base archetype：`ema_reclaim_long` + `fib_retest_long`
- 执行口径：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三臂对照：
  - `baseline`
  - `max_high_only`
  - `exclude_max_high`
- 训练段冻结：`max5m_1h` 的 `top30%` 作为 high tier，阈值约 `0.002258`

## 测试段硬结果（6 bps / side）
### overall
#### baseline
- `trades = 87`
- `mean_total_return ≈ -0.092%`
- `failure_before_target ≈ 47.13%`

#### max_high_only
- `variant_trades = 42`
- `trade_count_retention ≈ 48.28%`
- `variant_return ≈ -0.109%`
- `return_delta ≈ -0.017%`
- `variant_failure ≈ 50.00%`
- `failure_delta ≈ +2.87 pct`

#### exclude_max_high
- `variant_trades = 46`
- `trade_count_retention ≈ 52.87%`
- `variant_return ≈ -0.115%`
- `return_delta ≈ -0.023%`
- `variant_failure ≈ 45.65%`
- `failure_delta ≈ -1.47 pct`

## 最诚实的读法
- **高 MAX 没有形成更好的成本后收益。** 如果它真是 continuation-confirmation tier，`max_high_only` 至少该比 baseline 更好；但这轮反而更差。
- **低 MAX 也没有被压成明显更差。** `exclude_max_high` 的 failure 略好一点，但收益同样更差，说明不是“砍掉低质量样本后留下更强边”。
- **当前更像 setup 间互相打架。** `EMA reclaim` 和 `Fib retest` 没有在这条规则下给出一致 uplift，因此它不够格升到 `P2`，也不值得继续占 fast lane。

## 硬结论
**`Rank 128 / MAX(5m) impulse confirmation tier = park / evidence pool`**。

翻成人话：
- “小时内极端上冲”这个想法在论文和代理快检里有启发；
- 但放进这次 desk clean-room 后，**没有留下可用的 long-side confirmation uplift**；
- 因此当前更诚实的处理不是继续磨说明页，也不是硬保留它当 active Scout，
- 而是直接把它压回 `P0 / park / evidence pool`，下一轮回到 **fresh intake**。

## 本轮产物
### artifacts
- `scripts/build_rank128_max5m_impulse_confirmation_tier_clean_replication.py`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/thresholds.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/trade_log.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/overall_summary.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/setup_summary.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/asset_summary.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/cost_summary.csv`
- `reports/artifacts/scout_rank128_max5m_impulse_confirmation_tier_15m/summary.json`

### reader-facing
- `reports/site/factors/scout_rank128_max5m_impulse_confirmation_tier_15m/report.html`
- `reports/site/reading/repo_scout/rank128_max5m_impulse_confirmation_tier_clean_replication.html`

### desk write-back
- `docs/TODO.md`（新增 `2026-03-20 20:47 UTC` 顶板执行补充）

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：默认主资源位应切回
  - `fresh intake（优先 RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`
  - `Rank 127 = P1 weak candidate / budget used / evidence_pool`
  - `Rank 125 = P1 keep_P1 / budget used / 留样`
  - `Rank 112 / 111 = P1 evidence_pool / budget used`
  - `Rank 128 = P0 park / evidence pool`
  - `P3 continuity sidecar only`

## 下一手建议
1. 下一轮仍先做 `EMA due-check first`；
2. 若仍无新的 `due-now / overdue` lane，则按顶板回到 **fresh intake**，优先从：
   - `docs/RECENT_PAPER_SEEDS.md`
   - `research/quant_digests/INDEX.md`
   - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   认领 1 条新的 paper / repo-based 候选；
3. 不建议继续磨 `Rank 128` 的 admission wording / operator packet / closeout docs。

## Commit hash
未提交。

原因：工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit。
