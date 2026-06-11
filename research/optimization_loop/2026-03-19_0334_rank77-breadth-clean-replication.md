# 2026-03-19 03:34 UTC｜Rank 77 / alt-vs-BTC RS breadth shared gate minimal clean replication

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 77 minimal clean replication`
- 紧邻子点：根据 hard verdict 回写 `docs/TODO.md` 顶板，把下一默认动作退回 `fresh paper / repo source re-rank`

## 开始前检查
- `Run 1 / EMA due-check`：最新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 继续是 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T03:26:43Z` 继续是 `new_closed_trades_appended=0`，本轮没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- 最近 run：`2026-03-19 03:15 UTC` 已把 `Rank 77` 推进到 `guard-passed / admit_to_clean_replication_queue`，因此按板子本轮只允许给它 **1 次最小 clean replication**。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 77` clean-replication 脚本、artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 这轮为什么还是它
按 `docs/TODO.md` 顶板当前权威顺序：
1. `Run 1 = EMA due-check only`
2. `Run 2 = 若 Rank 77 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication（优先比较 24h vs 8h breadth 变体）`
3. `Run 3 = 若 Rank 77 clean replication 没有 decisive fail，再给 1 个真正会改变 verdict 的 Light Stability Pack；若直接 park，则退回 fresh source re-rank`

当前 `EMA` 真实仍是 `waiting_not_due`，所以本轮合法主动作就是把 `Rank 77` 那手最小诚实检查用掉，而不是又切回别的 fresh source，或回头挤占 `P3 continuity`。

## 本轮具体执行
### 1. 新增最小 clean replication 脚本
- 新增：`scripts/build_rank77_alt_btc_rs_breadth_clean_replication.py`
- 口径冻结：
  - base setups：`ema_psar_long / fib_retest_long / breakout_short`
  - 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
  - 成本：`6 / 10 / 15 bps per side`
  - breadth universe：`ETH / SOL / XRP / BNB / DOGE / ADA / LINK` 相对 `BTC`
  - 变体：`baseline / breadth_24h_gate / breadth_8h_gate / breadth_dual_gate`
  - gate 规则：
    - long setups 需要 `breadth_pos >= 0.55`
    - short setup 需要 `breadth_neg >= 0.55`
    - `breadth_dual_gate` 额外要求短窗口同向不弱于 `0.50`

### 2. 数据与样本
- base sample 复用：`reports/artifacts/scout_tau_band_breakout_15m/cache/{BTC,ETH,SOL}USDT__120d__15m.csv`
- breadth sample 额外最小补抓：Binance public `15m` OHLCV（缓存到 `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/universe_cache/`）
- 没有改主 trigger，也没有偷渡成独立 alpha；只测试 breadth 当 shared allow/deny gate 是否有资格升格。

## 结果
### Overall summary（均值口径，跨 9 个 asset-setup case）
- `baseline @ 6bps`：`mean_total_return ≈ -5.94%`，`positive_asset_ratio ≈ 44.44%`，`mean_trades ≈ 89.0`，`mean_early_fail_rate ≈ 53.04%`
- `breadth_24h_gate @ 6bps`：`mean_total_return ≈ -3.55%`，`positive_asset_ratio ≈ 55.56%`，`mean_trades ≈ 54.22`，`mean_early_fail_rate ≈ 55.12%`
- `breadth_8h_gate @ 6bps`：`mean_total_return ≈ +0.24%`，`positive_asset_ratio ≈ 55.56%`，`mean_trades ≈ 61.67`，`mean_early_fail_rate ≈ 55.20%`
- `breadth_dual_gate @ 6bps`：`mean_total_return ≈ -4.08%`，`positive_asset_ratio ≈ 33.33%`，`mean_trades ≈ 41.33`，`mean_early_fail_rate ≈ 55.55%`

### Setup-level read @ 6bps
- `breakout_short`
  - `baseline ≈ -14.05%`
  - `breadth_8h_gate ≈ -0.94%`（局部改善最明显）
  - 但 `breadth_dual_gate ≈ -12.90%`，说明一旦要求长短窗口同向，改善不稳，更多像局部 pocket 而不是可迁移 shared gate。
- `ema_psar_long`
  - `baseline ≈ -4.78%`
  - `breadth_24h_gate ≈ -0.02%`
  - `breadth_8h_gate ≈ +1.44%`
  - 但正收益分布不够广，且早失败率没有被压下来。
- `fib_retest_long`
  - `baseline ≈ +1.03%`
  - `breadth_24h_gate ≈ +1.96%`
  - `breadth_8h_gate ≈ +0.22%`
  - 这说明 breadth 对长侧 retest 有信息，但还不足以证明它是值得升格的 shared gate。

## Hard verdict
**`Rank 77 / alt-vs-BTC RS breadth shared gate = park / evidence pool`**

## 为什么给这个 verdict
1. `breadth_8h_gate` 的确出现局部改善，但它主要集中在 `breakout_short` 与部分 long pocket，跨三条 archetype 后不够稳；
2. 最保守主读法 `breadth_dual_gate` 仍显著为负，`positive_asset_ratio` 只有 `33.33%`；
3. 几个 breadth 变体都没有把 `mean_early_fail_rate` 压到比 baseline 更诚实的水平，说明改善更像“筛掉一部分单子”而不是找到更干净的 regime；
4. 这条线值得保留在 evidence pool，但当前还不该升到 `P2`，更不该抢 fresh queue 的默认主资源位。

## 产物
- 脚本：`scripts/build_rank77_alt_btc_rs_breadth_clean_replication.py`
- artifact：
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/setup_compare.csv`
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/time_pocket_summary.csv`
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/trades.csv`
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/meta.json`
- reader-facing 页面：
  - `reports/site/factors/scout_rank77_alt_btc_rs_breadth_15m/report.html`
  - `reports/site/reading/repo_scout/rank77_alt_btc_rs_breadth_clean_replication.html`

## 对交易台顺序的影响
- 当前 active Scout 顺序应改写为：
  1. `adaptive no-trade band / EMA cost survival`
  2. `one-regime-per-session overlay`
  3. `RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source`
  4. `Rank 35b`
  5. `Rank 16b`
  6. `tiny-live plumbing`
- 当前 seat 分级应收紧为：
  - `adaptive no-trade band / EMA cost survival = P0 fresh-paper queue / not admitted`
  - `one-regime-per-session overlay = P0 evidence / backlog`
  - `Rank 77 / 76 / 75 / 74 / 73 / 72 = P0 park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b = P3 narrow paper continuity`
  - `P1 / P2 / P4` 继续为空
- 因此写回后的 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则先回到 fresh paper / repo source re-rank（默认 adaptive no-trade band > one-regime-per-session overlay > 其他 fresh source）`
  3. `Run 3 = 只有 fresh source 这一层也 exhausted 时，才允许回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已成功执行：`python3 scripts/build_rank77_alt_btc_rs_breadth_clean_replication.py`
- 已确认文件存在：
  - `reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank77_alt_btc_rs_breadth_15m/report.html`
  - `reports/site/reading/repo_scout/rank77_alt_btc_rs_breadth_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
