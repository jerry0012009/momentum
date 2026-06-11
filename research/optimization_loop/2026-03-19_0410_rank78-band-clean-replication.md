# 2026-03-19 04:10 UTC｜Rank 78 / adaptive no-trade band 最小 clean replication

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 78 minimal clean replication`
- 紧邻子点：把 `Rank 78` 从 `P1 weak candidate` 明确升降级到更诚实的下一档，并同步写回交易台 `Next 3`

## 开始前检查
- `Run 1 / EMA due-check only`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk 无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T03:56:01Z` 显示 `new_closed_trades_appended=1`，对应 `Rank 17` 的真实 `closed-trade append + open-position refresh`；但它只构成低频 sidecar，不足以越过当前 active Scout 主资源位 `Rank 78`。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 78` clean replication 脚本、artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 这轮为什么选这个
- 顶板最新 `Next 3` 已明确：当 `EMA = waiting_not_due` 时，`Rank 78` 是当前唯一 active `P1`，默认必须先消耗它那 1 次真正会改变 verdict 的最小 clean replication。
- `Rank 17` 的新 append/open-position event 虽然是真状态变化，但仍只是 `P3 continuity` sidecar，不应抢走 `Scout Seat` 主预算。
- 因此这轮不能回头磨 continuity，也不该提前跳去新的 fresh intake；最诚实动作就是把 `Rank 78` 做完最小 replication，并直接给出 `P2 / park` 判断。

## 这轮具体做了什么
1. 新增脚本：
   - `scripts/build_rank78_adaptive_no_trade_band_clean_replication.py`
2. 固定复用本地 `BTC/ETH/SOL 120d 15m` cache，统一冻结为：
   - `signal 当根及之前数据`
   - `next-bar open`
   - `no-overlap`
   - `hold 8 bars`
3. 比较三臂：
   - `raw`
   - `fixed_band_10bp`
   - `adaptive_band_q1`
4. 套到三条当前 desk archetype：
   - `ema_psar_long`
   - `fib_retest_long`
   - `breakout_short`
5. 生成 artifact：
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/setup_compare.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/per_asset_summary.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/window_summary.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/trades.csv`
   - `reports/artifacts/scout_rank78_adaptive_no_trade_band_15m/summary.json`
6. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/report.html`
   - `reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_clean_replication.html`
7. 写回 `docs/TODO.md` 顶部交易台指挥板与 `Next 3`。

## 核心结果（6bps/side，主读法 `adaptive_band_q1`）
### 对照 `raw` 的最关键读法
- `ema_psar_long`
  - `raw total_net_return ≈ -10.98%`
  - `adaptive total_net_return ≈ -4.20%`
  - `retention ≈ 86.54%`
  - `early_fail_rate: 12.50% -> 5.56%`
- `breakout_short`
  - `raw total_net_return ≈ -10.61%`
  - `adaptive total_net_return ≈ -9.95%`
  - `retention ≈ 95.08%`
  - `early_fail_rate: 3.28% -> 1.72%`
- `fib_retest_long`
  - `raw total_net_return ≈ +3.64%`
  - `adaptive total_net_return ≈ -2.78%`
  - `retention ≈ 63.64%`
  - `early_fail_rate: 12.12% -> 9.52%`

### 这组结果最诚实的解释
- 这不是“adaptive band 已经证明自己是全 desk shared gate”。
- 但它也不该被直接打回 `park`：
  - 在 `ema_psar_long` 上改善明显，而且不是靠极端砍单；
  - 在 `breakout_short` 上改善很小，但方向仍是“少亏一点 + 更少早失败”；
  - 唯一明确掉队的是 `fib_retest_long`。
- 平均 retention 约 `81.75%`，说明这条线当前不是纯靠暴力缩样本换表面改善；它已经够资格从 `P1` 升到 `P2`，但还不够直接进 `P3`。

## Hard verdict
**`Rank 78 / adaptive no-trade band / EMA cost survival = P2 paper candidate`**

## 为什么是这个 verdict
- `P1` 阶段允许的那 1 次最小 clean replication 已经完成，且结果不是单边塌陷；
- 当前至少有两条 archetype（`ema_psar_long`、`breakout_short`）给出方向一致的便宜改善；
- 但 `fib_retest_long` 明显转弱，因此还不能把它直接包装成已过关的 `shared gate` 或直接推成 `P3 narrow paper pilot`；
- 更合规的下一步应是：只再给它 **1 个真正会改变 verdict 的最小 P2 检查**，然后直接做 `promote_to_narrow_paper_pilot / keep_P2 / park` 判断。

## 对交易台顺序的影响
- 当前更诚实的分级应改成：
  - `Rank 78 = P2 paper candidate`
  - `one-regime-per-session overlay = P0 evidence / backlog`
  - `RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source = P0 intake pool`
  - `Rank 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`
  - `Rank 17 / 2 / 29 / 32b = P3 narrow paper continuity`
- 更新后的 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则对 Rank 78 只再给 1 个真正会改变 verdict 的最小检查（默认优先时间稳定性 / 成本稳定性 二选一）`
  3. `Run 3 = 只有在 Rank 78 的 P2 检查已完成后，才回到 one-regime-per-session overlay > fresh source；Rank 17 的 sidecar 仍不得默认抢占 Scout 主资源`

## 最小验证
- 已实际运行：
  - `python3 scripts/build_rank78_adaptive_no_trade_band_clean_replication.py`
- 已确认输出文件存在：
  - `reports/site/factors/scout_rank78_adaptive_no_trade_band_15m/report.html`
  - `reports/site/reading/repo_scout/rank78_adaptive_no_trade_band_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 风险 / 边界
- 当前只用了 `BTC/ETH/SOL 120d 15m` 本地 cache，不是更长样本；
- `adaptive_band_q1` 只是最小检查口径，不代表参数已定型；
- 这轮结论针对的是 **desk 当前的 shared admission / suppression 价值**，不是说 adaptive band 已经可独立当 alpha；
- 下一轮若时间稳定性或成本稳定性一查就塌，应直接从 `P2` 压回 `park`。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
