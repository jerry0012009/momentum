# 2026-03-19 02:22 UTC｜Rank 75 / GCR extreme-sentiment exhaustion veto minimal clean replication

## 轮次定位
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 75 minimal clean replication`
- 紧邻子点：`TRADING DESK BOARD / Next 3 bot3 runs` 写回

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 继续显示全 desk 当前无 `due-now / overdue` lane；最早 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，因此 `Paper Seat / EMA` 仍是真 `running paper / waiting_not_due`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T01:50:50Z` 仍是 `new_closed_trades_appended=0`，当前没有新的 `P3 status-changing event` 值得 bot3 回头挤占 continuity。
- 上一轮 `Rank 75 source intake` 已把这条线定为 `guard-passed / admit_to_clean_replication_queue`，因此按顶板当前顺序，本轮合法主动作就是给它 **1 次最小 clean replication**。
- git 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 75` clean-replication script、artifact、reader-facing 页面、`TODO` 顶板写回与本轮日志，不做混提。

## 本轮为什么仍是 Rank 75
- `EMA = waiting_not_due`，因此不该空刷 paper refresh。
- `P3` 托管位也没有新的 status-changing event，因此不该把 budget 花在 continuity。
- 按上一轮写回的合法顺序：`Rank 75 minimal clean replication > Rank 76 source intake > one-regime-per-session overlay > Rank 35b > Rank 16b > tiny-live plumbing`。
- 这轮只认领 `Rank 75`，没有同时再开第二条 fresh intake，符合“最多 1 个主点 + 1 个紧邻子点”。

## 本轮实际做了什么
1. 新增最小 clean-replication 脚本：
   - `scripts/build_rank75_gcr_exhaustion_veto_clean_replication.py`
2. 固定复用现有 `BTC/ETH/SOL 120d 15m` cache，把 `GCR exhaustion veto` 接到三条 archetype：
   - `ema_psar_long`
   - `fib_retest_long`
   - `breakout_short`
3. 只比较五臂：
   - `baseline`
   - `extreme_only`
   - `extreme_plus_volume`
   - `extreme_plus_volume_plus_bb`
   - `full_gcr_with_divergence`
4. 执行口径统一冻结为：
   - `signal 当根及之前数据`
   - `next-bar open`
   - `no-overlap`
   - `hold 8 bars`
5. 产出 artifact / 页面：
   - `reports/artifacts/scout_rank75_gcr_exhaustion_veto_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank75_gcr_exhaustion_veto_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank75_gcr_exhaustion_veto_15m/time_pocket_summary.csv`
   - `reports/site/factors/scout_rank75_gcr_exhaustion_veto_15m/report.html`
   - `reports/site/reading/repo_scout/rank75_gcr_exhaustion_veto_clean_replication.html`
6. 把最新结果写回 `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`。

## 诚实边界
- 原计划里的最小实验写的是 `15m 主信号 + 5m veto 执行层`，但本轮为了严格复用现有历史样本、避免额外下载重缓存，实际先做的是 **同频 15m exhaustion proxy** 的便宜诚实检查。
- 也就是说：这轮只回答“这条线值不值得继续占预算”，**不能**把结果伪装成完整 `5m execution-layer` 结论。
- `divergence` 仍然是最脆的一层，因此专门保留了 `baseline -> extreme_only -> extreme+volume -> extreme+volume+bb -> full_gcr_with_divergence` 的逐层对照，避免把改善全偷渡成花哨条件。

## 关键结果（6bps / side）
### breakout_short
- `baseline`：`mean_total_return≈-2.58%`，`mean_trades≈20.3`，`false_break≈44.57%`
- `extreme_only`：`mean_total_return≈-0.54%`，但 `retention≈6.67%`，几乎是靠极度砍单换出来
- `extreme_plus_volume`：`mean_total_return≈-0.75%`，`retention≈40.29%`，但 `false_break≈53.33%`
- `full_gcr_with_divergence`：`mean_total_return≈-2.88%`，`retention≈62.02%`，`false_break≈56.12%`，比 baseline 更差

### ema_psar_long
- `baseline`：`mean_total_return≈-5.41%`，`mean_trades≈34.7`
- `extreme_only`：`mean_total_return≈+0.23%`，但 `retention≈23.08%`，仍是明显靠砍单
- `extreme_plus_volume`：`mean_total_return≈-1.79%`，`retention≈59.66%`
- `full_gcr_with_divergence`：`mean_total_return≈-1.36%`，`retention≈72.07%`，比 baseline 好一些，但只是局部改善

### fib_retest_long
- `baseline`：`mean_total_return≈+0.88%`，`mean_trades≈11.0`
- `extreme_only`：`mean_total_return≈+1.43%`，但 `retention≈39.39%`
- `extreme_plus_volume`：`mean_total_return≈+0.71%`，`retention≈81.82%`
- `full_gcr_with_divergence`：`mean_total_return≈+0.35%`，`retention≈90.91%`，比 baseline 反而退步

## Hard verdict
**`Rank 75 / GCR extreme-sentiment exhaustion veto = park / evidence pool`**

## 为什么是这个 verdict
- 这条线确实碰到了一个真实问题：`ema_psar_long` 的末端追价被修掉了一部分。
- 但更诚实地看，主要改善集中在局部 setup，且最漂亮的 `extreme_only` 读法明显靠 **大幅砍交易数**。
- 一旦把条件补到更像原始 GCR 叙事的 `full_gcr_with_divergence`，`breakout_short` 和 `fib_retest_long` 都没有被修好，`breakout_short` 甚至更差。
- 因此这轮不能把它升成 `P1/P2` 有效候选；当前更像一条可留档的局部线索，而不是当前 desk 应继续默认追的 shared veto。

## 对交易台顺序的影响
- 这轮已消耗掉 `Rank 75` 允许的那次 minimal clean replication。
- 因此当前合法的 `Next 3` 应切到：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 Rank 75 minimal clean replication 已给出 park / evidence pool hard verdict，则立刻切到 Rank 76 / intraday clock polarity + event blackout gate 做 fresh source intake`
  3. `Run 3 = 只有 fresh source 这一层也 exhausted 时，才允许回退到 one-regime-per-session overlay > Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- `python3 scripts/build_rank75_gcr_exhaustion_veto_clean_replication.py` 已成功跑完，退出码 `0`。
- 已确认下列读者可见落点存在：
  - `reports/site/factors/scout_rank75_gcr_exhaustion_veto_15m/report.html`
  - `reports/site/reading/repo_scout/rank75_gcr_exhaustion_veto_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 后续动作
- 刷新首页 index：`bash scripts/publish_homepage_index.sh`
- 发送中文邮件摘要：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...`

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
