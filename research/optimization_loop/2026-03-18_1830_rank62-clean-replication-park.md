# 2026-03-18 18:30 UTC · Rank 62 minimal clean replication

## 本轮结论
- `Paper Seat / EMA`：继续 `running paper / waiting_not_due`
- `Live Seat`：继续 `暂空`
- `Scout Seat`：按 desk board 的 `Run 2`，执行 **`Rank 62 / continuation fail-fast overlay` 的 1 次最小 clean replication**
- 本轮 hard verdict：**`Rank 62 / continuation fail-fast overlay = park / evidence pool`**

## 先检查了什么
- `git status --short`：工作区存在大量与本轮无关的脏文件（docs / reports / scripts / workspace 根目录都有历史改动与新产物），因此本轮只做 selective write，不混提其他改动。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：最早到点仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`；crypto `-> 2026-03-19 00:00 UTC`；A 股 `-> 2026-03-19 07:00 UTC`。当前没有新的 `due-now / overdue` lane。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最新 `run_at_utc=2026-03-18T18:18:17Z`，`new_closed_trades_appended=0`，不构成抢回 `P3 continuity` 的理由。
- `docs/TODO.md` 顶板：当前合法顺序仍是 `Run 1 = EMA due-check only`、`Run 2 = Rank 62 minimal clean replication`、`Run 3 = Rank 63 / CQI / Rank35b / Rank16b` 的比较层。由于 `EMA = waiting_not_due`，本轮主资源继续留在 `Scout Seat`。

## 为什么本轮继续做 Rank 62，而不是切别的
- 当前活跃 Scout 里，上一轮已把 **`Rank 62 / continuation fail-fast overlay`** 放进 `admit_to_clean_replication_queue`，因此它仍是最该先结清的一条。
- 相比直接切去 `Rank 63 / Fib 0.618 hold / 0.5 fail gate` 或 `pullback-quality / CQI`：
  - `Rank 62` 已过两条轻量诚实守门，边际价值更高；
  - 它的承诺很明确：不是再发明 entry，而是测试能不能给三条 archetype 补一个 shared failure protocol；
  - 这次 replication 只需复用本地 `BTC/ETH/SOL 120d 15m` cache，预算最小。

## 本轮执行口径（最小 clean replication）
- 复用三条最小 archetype：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 统一口径：
  - `signal bar -> next-bar open` 入场
  - `no-overlap`
  - base 持有上限 = `8` 根 `15m` bar
  - fail-fast 触发后也统一按 `fail close 确认 -> next-bar open exit`
- 比较三臂：
  1. `base_exit`
  2. `ema_atr_fail_fast`
  3. `ema_vwap_atr_fail_fast`
- 核心检查指标：
  - `post-cost return @ 6bps`
  - `median_loser_size`
  - `false_follow_through_4bars / 8bars`
  - `winner_truncation_rate`
  - `early_exit_rate / realized hold bars`

## 结果冻结
### setup-level（6bps/side）
- `ema_psar_long`
  - `base ≈ -5.55%`
  - `ema+atr ≈ -4.27%`
  - `ema+vwap+atr ≈ -3.92%`
  - loser size 从 `0.649%` 缩到 `0.507%`
  - 但 `winner_truncation_rate ≈ 37.5%`，`early_exit_rate ≈ 76.2%`
- `fib_retest_long`
  - `base ≈ +0.88%`
  - `ema+atr ≈ -0.35%`
  - `ema+vwap+atr ≈ -1.88%`
  - `winner_truncation_rate ≈ 61.7%`
  - 说明这层 fail-fast 把原本能走出来的 Fib retest 也大量砍掉了
- `breakout_short`
  - `base ≈ -2.58%`
  - `ema+atr ≈ -3.25%`
  - `ema+vwap+atr ≈ -3.12%`
  - loser size 虽有一点缩小，但总回报更差

### 更诚实的读法
- 这层 overlay 在 `ema_psar_long` 上**确实像 shared failure protocol**：它能更快认错、缩小 loser size。
- 但问题是它**没有跨 archetype 保持一致**：
  - 对 `fib_retest_long`，它明显在做过度早砍；
  - 对 `breakout_short`，它没有把负 pocket 修回来；
  - `false_follow_through_4bars / 8bars` 在当前定义下基本没改善，说明它更多是在重塑尾部，而不是实质减少“假延续”事件频率。
- 因此这条线的增量还不够支撑继续占默认 fast lane；更像是一种 **局部 EMA continuation 保护层**，不是当前 desk 可直接共享部署的三线共用 overlay。

## 本轮 hard verdict
**`Rank 62 / continuation fail-fast overlay = park / evidence pool`**

原因：
1. 主读法 `ema_psar_long` 虽改善，但幅度还不足以抵消跨 setup 不一致；
2. `fib_retest_long` 被明显过早截断，`winner_truncation_rate` 太高；
3. `breakout_short` 没有被修复；
4. `session VWAP` 在 24/7 crypto 上仍带 session 任意性保留意见，不值得继续优先占用 scout 主资源。

## 本轮产物
- script：`scripts/build_rank62_continuation_fail_fast_clean_replication.py`
- artifact：`reports/artifacts/scout_rank62_continuation_fail_fast_15m/`
  - `overall_summary.csv`
  - `asset_summary.csv`
  - `setup_compare.csv`
  - `trade_log.csv`
  - `time_pockets.csv`
- reader-facing：
  - `reports/site/factors/scout_rank62_continuation_fail_fast_15m/report.html`
  - `reports/site/reading/repo_scout/rank62_continuation_fail_fast_clean_replication.html`
- desk board refresh：`docs/TODO.md`

## 对排班的影响
- `Rank 62` 已完成最小 clean replication，并被压回 `park / evidence pool`。
- 因此当前更诚实的 active Scout 顺序应收紧为：
  - `Rank 63 / Fib 0.618 hold / 0.5 fail gate`
  - `pullback-quality / CQI`
  - `Rank 35b`
  - `Rank 16b`
  - `tiny-live plumbing`
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认应先执行 `Rank 63`，而不是继续给 `Rank 62` 续命。

## 验证 / 风险控制
- 只复用本地 `120d 15m` cache；未触发新的重型下载。
- 这次只做最小 clean replication，不扩成完整稳定性包，不额外偷开新候选。
- 由于工作区存在大量无关脏文件，本轮不做 commit，避免混提。
