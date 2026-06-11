# 2026-03-19 17:46 UTC — Rank 95 Vajra controlled-pullback 时间稳定性后压回 park

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 2.3h`、`Crypto 6.3h`、`A股 13.3h`。
- `manual_narrow_paper_last_run_summary.json` 仍没有新的 `P3 status-changing event` 可挤掉 fresh Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最新 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 95 / Vajra controlled-pullback depth-budget`** 剩下那 1 个 truly verdict-changing 的 `Light Stability Pack / 时间稳定性`。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 95` 的时间稳定性检查，并直接回答 `promote_to_P2 / keep_P1 / park`
- **紧邻子点**：把 hard verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮实现口径
- 新增脚本：`scripts/build_rank95_time_stability_check.py`
- 完全复用上一轮 `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/trade_log.csv`
- 样本：`BTC/ETH/SOL | 120d | 15m`
- 执行冻结：`6bps/side`、`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 时间稳定性口径：
  - 将每个 `asset × variant` 按时间顺序切成 `3` 个等样本 bucket
  - 重点只看两条真正影响 desk verdict 的主臂：
    - `prearmed_depth_0p75`（上一轮最佳子臂）
    - `prearmed_depth_1p0`（默认 desk 口径）
  - 其他臂（`baseline / post_trigger_depth_1p0 / prearmed_depth_1p25 / plus_filters`）只作为陪审，不争主 verdict

## 结果摘要（6bps/side）
### 主 verdict 两臂
- **`prearmed_depth_0p75`**：
  - overall：`mean_total_return≈-3.61%` / `positive_asset_ratio=0/3` / `trade_count_retention≈53.36%` / `early_fail_4bars≈77.86%`
  - 时间三桶：`bucket_1≈-0.85%` / `bucket_2≈-1.04%` / `bucket_3≈-1.78%`
  - 结论：最佳子臂也没有出现任何正桶，已经不是“混合证据”，而是直接没穿过时间维度
- **`prearmed_depth_1p0`**：
  - overall：`mean_total_return≈-3.80%` / `positive_asset_ratio=0/3` / `trade_count_retention≈66.08%` / `early_fail_4bars≈82.18%`
  - 时间三桶：`bucket_1≈-0.70%` / `bucket_2≈-1.00%` / `bucket_3≈-2.10%`
  - 结论：desk 默认口径同样 `0/3` 正桶，且后段更差，不支持继续保留 active Scout 资源位

### 陪审参考
- `post_trigger_depth_1p0` 虽有 `bucket_3≈+2.12%`，但前两桶仍为负，且 overall 仍 `mean_total_return≈-4.09%`；更像局部 pocket，不足以救回 Rank 95
- `prearmed_depth_1p0_plus_filters` 三桶全负且样本更薄，继续印证 repo 自带 green/volume/ADX 过滤只是暴力缩样本，不是稳定增益

## hard verdict
**`Rank 95 = park / evidence pool`**

更直白地说：
- 上一轮 clean replication 还能让它停在 `keep_P1`，是因为至少看到了“depth budget 前置成 pre-armed state”这个较诚实的方向；
- 但这轮真正 verdict-changing 的时间稳定性已经把那点希望打穿了：**最佳子臂 `prearmed_depth_0p75` 与默认口径 `prearmed_depth_1p0` 都是 `0/3` 正桶**；
- 既然连时间维度都过不去，就不该继续给它第三轮近义检查，也不该继续把它占在 Scout fast lane。

## 本轮产物
### reader-facing 落点
- `reports/site/factors/scout_rank95_vajra_controlled_pullback_15m/time_stability_check.html`
- `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_time_stability.html`

### artifacts
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_window_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_asset_window_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_verdict_summary.csv`
- `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_summary.json`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 95 = park / evidence pool`
- active Scout 顺序：`Rank 96 / AdvancedMA retest-count admission layer > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 95 park / evidence_pool > Rank 92 / Rank 94 park / evidence_pool > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 96 / AdvancedMA retest-count admission layer 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Rank 96 guard-pass，则只给它 1 次最小 clean replication；若 Rank 96 也直接 hard-fail / exhausted，才允许回退到旧 evidence_pool > P3 continuity > tiny-live plumbing`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已执行：`python3 scripts/build_rank95_time_stability_check.py`
- 本轮未做重下载，完全复用本地已有 `trade_log.csv`

## git / 脏区说明
- `git status --short | wc -l = 1492`
- 当前 git 工作区仍有大量与本轮无关的脏文件
- 本轮直接相关的新增/改动主要包括：
  - `scripts/build_rank95_time_stability_check.py`
  - `reports/artifacts/scout_rank95_vajra_controlled_pullback_15m/time_stability_*`
  - `reports/site/factors/scout_rank95_vajra_controlled_pullback_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank95_vajra_controlled_pullback_time_stability.html`
  - `docs/TODO.md`
- 因脏区过大，本轮不提交，避免混提

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，默认切 **`Rank 96 / AdvancedMA retest-count admission layer`** 做 `source intake + 两条轻量诚实守门`
- 不要再继续给 `Rank 95` 补第三轮近义检查；除非未来出现真正新的 status-changing 证据，否则它应停在 `park / evidence pool`

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
