# Rank 131 / fib violation-cluster 最小 clean replication 后压回 park

## 为什么这次选这个
- 先按 desk board 执行 `Run 1`：再次运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 返回仍是 `waiting_not_due`；当前最靠前的仍是 `Crypto 1d+1wk`，约 `1.6h` 后才到下一次 close，因此这轮不能伪造 EMA refresh。
- 按 `Run 2`，本轮只给 `Rank 131 / fib violation-cluster + 1-bar memory gate` 一次最小 clean replication。
- 这条线本轮的目标不是把 Fib 重新吹成 shared gate，而是诚实回答：**最近 1~2 根破位记忆，能不能在 15m crypto 上减少 fib retest 的假 hold，同时又不把交易数砍穿。**

## 做了什么改动
1. 新增最小 clean replication 脚本：
   - `scripts/build_rank131_fib_violation_cluster_clean_replication.py`
2. 生成本轮 artifact：
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/signals.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/trade_log.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/cost_summary.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/promotion_scorecard.csv`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/promotion_scorecard.json`
   - `reports/artifacts/scout_rank131_fib_violation_cluster_memory_15m/summary.json`
3. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank131_fib_violation_cluster_memory_15m/report.html`
   - `reports/site/reading/repo_scout/rank131_fib_violation_cluster_memory_clean_replication.html`
4. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 把 `Rank 131` 从 active scout 主点挪回 `P0 / park / evidence pool`
   - 把 `Scout Seat` 当前主点切回 `fresh intake reserve`
   - 把 `Next 3 bot3 runs` 改成：`EMA due-check -> fresh intake reserve -> intake/或 tiny-live fallback`

## 复现实验口径
- 资产：`BTC / ETH / SOL perpetual 15m`
- 执行：`next-bar open + no-overlap`
- 持有：`8 bars`
- 成本：`6 / 10 / 15 bps per side`
- 三臂：
  1. `baseline`
  2. `t-1 veto`（若前一根已发生同向 fib violation，则否决当前 hold）
  3. `t-1,t-2 cluster veto`（只有前两根连续 violation 才否决）
- 主要指标：`post_cost_mean_return`、`false_hold_ratio@4bars`、`trade_count_retention`、`timeout_share`

## 验证 / 关键证据
### 1) EMA 仍是 waiting_not_due
命令：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果要点：
- 当前没有 `due-now / overdue lane`
- 最靠前的仍是 `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 1.6 小时后到点`
- 因而本轮合法动作只能落在 `Scout Seat`

### 2) Rank 131 clean replication 总结（test 段，6bps）
- `baseline`：
  - trades = `11`
  - mean net return = `+8.77 bps`
  - false_hold_ratio@4bars = `27.27%`
  - trade_count_retention = `100%`
- `t-1 veto`：
  - trades = `3`
  - mean net return = `-11.26 bps`
  - false_hold_ratio@4bars = `0%`
  - trade_count_retention = `27.27%`
- `t-1,t-2 cluster veto`：
  - trades = `9`
  - mean net return = `+23.77 bps`
  - false_hold_ratio@4bars = `33.33%`
  - trade_count_retention = `81.82%`

### 3) 这组结果怎么解读
- `t-1 veto` 的确把 test 段的假 hold 直接压成了 `0%`，但代价是样本只剩 `27.27%`，且 `post-cost` 反而掉到负值：
  - return delta vs baseline = `-20.02 bps`
- `cluster veto` 没有解决核心问题：
  - 样本保留得更多（`81.82%`），但 test 段假 hold ratio 反而从 `27.27%` 升到 `33.33%`
- 训练段里两条 veto 也没有形成足够诚实的一致 uplift：
  - `t-1 veto` train 段同样为负值
  - `cluster veto` train 段也为负值

## 当前硬结论
**`Rank 131 / fib violation-cluster + 1-bar memory gate = P0 / park / evidence pool`**。

翻成人话：
- “最近一根破位就 veto 当前 fib hold” 这件事，**更像是在砍样本，不像在稳定提纯 alpha**。
- `t-1 veto` 有一点“少踩雷”的味道，但它把交易数砍得太狠，经济结果也变差；
- `cluster veto` 则连“少踩雷”都没保住。
- 所以这轮最诚实的结论不是 `keep_P1`，更不是 `promote_P2`，而是直接压回 `park`。

## Scout Promotion Scorecard（本轮）
- `chosen_variant = t1_veto`
- `usefulness = 0/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 0/3`
- `deployability = 1/3`
- hard-fail flags：
  - `rule_unclear = false`
  - `leakage_risk = false`
  - `post_cost_collapse = true`
  - `too_sparse = true`
  - `single_pocket_dependency = true`
- `recommended_action = park`
- `main_weakness = trade_count retention 太低，confirmation 价值更像缩样本，不像可部署 admission gate`

## 风险 / 边界
- 这轮只做了最小 clean replication，还没有做 stability pack；但因为 clean replication 已经不诚实，没必要继续给它预算。
- 当前实现仍是我们自己的 fib retest proxy，不是论文原作者代码；不过 desk 当前要回答的是“是否值得继续占资源”，这轮证据已经足够回答“不值得”。
- `cluster veto` 在 BTC/ETH 测试段有少量 return uplift，但它没有降低假 hold，说明它更像 pocket coincidence，不够 shared。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，默认不要再认领 `Rank 131`；直接回 `fresh intake reserve`，从：
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
  里认领下一条新的 paper / repo based `5m / 15m crypto` 候选，并先拿下下一个顺序 `Rank`。
- 只有 fresh intake 也 exhausted，才允许落到 `tiny-live plumbing fallback`。

## Commit hash
- 未提交。
- 原因：repo 工作区存在大量与本轮无关的脏文件；这轮不适合做安全 selective commit。
