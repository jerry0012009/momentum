# 2026-03-19 18:25 UTC — Rank 96 retest-count 最小 clean replication 后压回 park

## 为什么这轮是它
- 先实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本继续返回 **`waiting_not_due`**：当前没有 `due-now / overdue` 的 EMA lane；最近 due 约为 `美股 1.6h`、`Crypto 5.6h`、`A股 12.6h`。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新仍是 `new_closed_trades_appended=0`，没有新的 `P3 status-changing event` 可以挤掉 Scout。
- 按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的当前 `Next 3 bot3 runs`，本轮合法主动作就是 **`Rank 96 / AdvancedMA retest-count admission layer`** 的那 1 次最小 clean replication。

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 96` 的最小 clean replication，并直接回答 `promote_to_P2 / keep_P1 / park`
- **紧邻子点**：把 hard verdict、active Scout 顺序、下一轮 `Next 3` 最小写回到 `TRADING DESK BOARD`

## 本轮实现口径
- 新增脚本：`scripts/build_rank96_advancedma_retest_count_clean_replication.py`
- 固定复用：`BTC/ETH/SOL | 120d | 15m` 本地 cache
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- breakout / retest 代理口径：
  - `baseline`：20-bar breakout 后直接 next-bar open，不等 retest
  - `first_touch_only`：第一次有效 retest 就放行
  - `second_touch_only`：至少第二次有效 retest 才放行
  - `second_touch_plus_candle_quality`：第二次 retest 且实体/收盘位置/量能不过分差
- 成本统一看：`6 / 10 / 15 bps per side`

## 结果摘要（主读法：6bps/side）
### short 侧
- `baseline`：`post_cost_expectancy≈-4.90bps` / `mean_total_return≈-13.28%` / `positive_asset_ratio=0/3` / `hold8_rate≈46.10%` / `fail_close_ratio≈53.90%`
- `first_touch_only`：`≈-3.55bps` / `≈-8.50%` / `0/3` / `≈48.14%` / `≈51.86%`
- `second_touch_only`：`≈-7.68bps` / `≈-16.57%` / `0/3` / `≈44.60%` / `≈55.40%`
- **`second_touch_plus_candle_quality`（主变体）**：`post_cost_expectancy≈-0.46bps` / `mean_total_return≈-1.12%` / `positive_asset_ratio=1/3` / `hold8_rate≈42.02%` / `fail_close_ratio≈57.98%` / `trade_count_retention≈20.17%`
- 读法：short 侧确实从“明显负”改善到“几乎打平”，但没有真正转正，而且改善主要伴随**样本大幅缩薄**，失败率也没有一起改善。

### long 侧
- `baseline`：`post_cost_expectancy≈-18.29bps` / `mean_total_return≈-48.96%` / `positive_asset_ratio=0/3`
- `first_touch_only`：`≈-10.46bps` / `≈-24.99%` / `0/3`
- `second_touch_only`：`≈-18.41bps` / `≈-39.99%` / `0/3`
- **`second_touch_plus_candle_quality`（主变体）**：`post_cost_expectancy≈-34.05bps` / `mean_total_return≈-18.11%` / `positive_asset_ratio=0/3` / `trade_count_retention≈21.08%`
- 读法：long 侧没有出现“second-touch 更诚实”的证据，反而说明如果把它提前写成共享 gate，会把 long admission 读法越写越差。

### 分资产补充（主变体 / short / 6bps）
- `BTC`：`mean_net_bps≈-6.20` / `total_return≈-3.72%`
- `ETH`：`mean_net_bps≈+27.52` / `total_return≈+12.38%`
- `SOL`：`mean_net_bps≈-22.69` / `total_return≈-12.03%`
- 读法：当前只剩 `ETH short` 一条腿为正，跨资产一致性不够，不支持继续占默认 fast lane。

## hard verdict
**`Rank 96 = park / evidence pool`**

更直白地说：
- 这条线不是完全没信息；它留下的唯一像样线索，是 **short 侧 second-touch + candle-quality** 可能比 raw breakout 更少自欺；
- 但它没有把 **成本后收益、跨资产一致性、失败率** 一起改善到值得继续占主资源：
  - short 主变体仍未真正转正；
  - `positive_asset_ratio` 只有 `1/3`；
  - `trade_count_retention` 只剩约 `20%`；
  - long 侧还明显恶化；
- 因此当前最诚实的 desk 读法不是“值得继续升格”，而是：**最多保留成 setup-specific short admission / veto 弱线索，先压回 park。**

## 本轮产物
### reader-facing 落点
- `reports/site/factors/scout_rank96_advancedma_retest_count_15m/report.html`
- `reports/site/reading/repo_scout/rank96_advancedma_retest_count_clean_replication.html`

### artifacts
- `reports/artifacts/scout_rank96_advancedma_retest_count_15m/trade_log.csv`
- `reports/artifacts/scout_rank96_advancedma_retest_count_15m/asset_summary_primary_6bps.csv`
- `reports/artifacts/scout_rank96_advancedma_retest_count_15m/overall_summary.csv`
- `reports/artifacts/scout_rank96_advancedma_retest_count_15m/cost_summary.csv`
- `reports/artifacts/scout_rank96_advancedma_retest_count_15m/summary.json`

## desk board 写回
已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 最小刷新为：
- `Rank 96 = park / evidence pool`
- active Scout 顺序：`fresh 5m / 15m paper-repo source intake > Rank 93 / Rank 90 / Rank 91 / Rank 82 / Rank 80 / Rank 81 evidence_pool > Rank 96 / Rank 95 / Rank 92 / Rank 94 park > P3 continuity > tiny-live plumbing`
- `Next 3 bot3 runs`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则按 7.10 重新认领 1 条新的 5m / 15m paper-repo source intake`
  3. `Run 3 = 若 fresh source guard-pass，则只给它 1 次最小 clean replication；若 fresh source 也 exhausted，才允许回退到旧 evidence_pool > P3 continuity > tiny-live plumbing`

## 验证 / 命令
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 已执行：`python3 scripts/build_rank96_advancedma_retest_count_clean_replication.py`
- 已确认以下文件存在并可读：
  - `reports/artifacts/scout_rank96_advancedma_retest_count_15m/overall_summary.csv`
  - `reports/site/factors/scout_rank96_advancedma_retest_count_15m/report.html`
  - `reports/site/reading/repo_scout/rank96_advancedma_retest_count_clean_replication.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮 clean replication 用的是 20-bar breakout + retest 代理口径，不是三条主线的原始信号本体；因此当前 verdict 应读成 **执行层 admission 启发被快筛否掉**，不是对所有 retest 研究永久封死。
- 如果未来真要复活，只应从 **short-side setup-specific overlay** 重新开，而不是再把它包装成共享 hard gate。
- 当前不允许因为它“几乎打平”就继续给第二轮近义检查；按 desk 预算，这轮已经足够回答 keep / park。

## git / 脏区说明
- 当前 git 工作区仍有大量与本轮无关的脏文件。
- 本轮直接相关的新增/改动主要包括：
  - `scripts/build_rank96_advancedma_retest_count_clean_replication.py`
  - `reports/artifacts/scout_rank96_advancedma_retest_count_15m/*`
  - `reports/site/factors/scout_rank96_advancedma_retest_count_15m/report.html`
  - `reports/site/reading/repo_scout/rank96_advancedma_retest_count_clean_replication.html`
  - `docs/TODO.md`
- 因脏区过大，本轮不提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认不要再给 `Rank 96` 续命；
- 直接按 `7.10` 从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 中再认领 **1 条新的 5m / 15m paper-repo source intake**；
- 若 fresh intake 也真实 exhausted，再退回旧 evidence_pool 或 tiny-live plumbing。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，混提不安全。
