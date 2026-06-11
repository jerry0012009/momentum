# 2026-03-20 10:12 UTC · Rank 116 / EMA respect memory clean replication park

## 本轮结论
- 先按顶板 `Run 1` 实际执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果仍是全 desk `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-20 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-21 00:00 UTC`
  - 创业板ETF `1d -> 2026-03-23 07:00 UTC`
- 因此本轮合法主动作继续落在 `Scout Seat / Run 2`
- 本轮认领主点：**`Rank 116 / EMA respect memory score` 的 1 次最小 clean replication**
- 当前 hard verdict：**`Rank 116 = P0 / park / evidence pool`**

## 为什么这轮继续做 Rank 116
- 顶板 `09:47 UTC` 已把 `Rank 116` 冻结为 `P1 / guard-passed / clean replication next`
- 本轮不再开新候选，只做这一手最小验证，符合“1 个主点 + 1 个紧邻子点”的预算约束
- 若这轮能得到 honest uplift，再进 `Run 3`；若 hard-fail / exhausted，就必须回 fresh intake，而不是继续磨近义说明

## 本轮完成内容
### 1. 最小 clean replication（单一 archetype）
新建并运行：
- `scripts/build_rank116_ema_respect_memory_clean_replication.py`

固定口径：
- 样本：`BTC/ETH/SOL 120d 15m` 本地 cache
- base archetype：`fib_retest_long`
- 执行：`next-bar open + no-overlap + hold 8 bars`
- frozen params：`score_window=14 / touch_band=0.5% / score>=2`
- 对照组：`score + dist<=0.75 ATR + depth>=-0.8 ATR`

比较三臂：
- `baseline_direct_entry`
- `ema_respect_score_only`
- `score_plus_corridor_control`

### 2. clean replication 的硬发现
核心结果非常直接：
- **`score_only` 与 baseline 在测试段完全相同**
  - `entries` 相同
  - `retention` 相同（= `1.0`）
  - `mean_total_return` 相同
  - `false_follow_4bars` 相同（= `0.75`）
- 这说明：在这条 clean-room 里，`EMA respect memory score` 没有提供新的 honest filter；它只是把原本就会通过的 base signal 重命名了一遍

6 bps/side 的 desk 级摘要：
- `baseline`: `mean_total_return ≈ +0.00%`，`mean_retention = 100%`
- `score_only`: **与 baseline 完全相同**
- `score_plus_corridor`: `mean_total_return ≈ +0.43%`，但 `mean_retention ≈ 35%`

更诚实的解释：
- `score_plus_corridor` 的表面改善主要来自**砍样本**，不是 shared admission layer 的稳健 uplift
- 同时它继续支持 intake 阶段的判断：`ATR corridor` 不该默认升级成共享硬门

### 3. desk judgment
因此当前最诚实的收口不是 `keep_P1`，而是：
- **`Rank 116 / EMA respect memory score = P0 / park / evidence pool`**
- 保留为 repo feature note 可以
- 不再继续申请 `Light Stability Pack`
- 下一轮默认必须回 fresh intake

## 新增产物
- `scripts/build_rank116_ema_respect_memory_clean_replication.py`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/trade_log.csv`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/asset_summary.csv`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/overall_summary.csv`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/train_test_gate_summary.csv`
- `reports/artifacts/scout_rank116_ema_respect_memory_15m/summary.json`
- `reports/site/factors/scout_rank116_ema_respect_memory_15m/report.html`
- `reports/site/reading/repo_scout/rank116_ema_respect_memory_clean_replication.html`

## 顶板写回
- `docs/TODO.md` 已追加 `10:11 UTC` authoritative write-back
- active Scout 顺序收紧为：
  - `fresh intake（next）`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
  - `Rank 116 / park`
  - `Rank 115 / park`
  - `Rank 114 / park`
  - `Rank 113 / park`
- `Live Seat = 暂空`
- 最新 `Next 3`：
  - `Run 1 = EMA due-check first`
  - `Run 2 = 若 EMA 仍 waiting_not_due，则按 7.10 回 fresh intake 池再认领 1 条新 source`
  - `Run 3 = 若新 source guard-pass，则只给它 1 次 truly verdict-changing 的最小 clean replication`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 waiting/not-due 守门态，符合当前 desk 状态
- `python3 scripts/build_rank116_ema_respect_memory_clean_replication.py`
  - 成功产出 CSV / JSON / HTML
- reader-facing 页面已落地，不是只留内部日志

## git / 脏文件说明
- repo 工作区仍存在大量与本轮无关的历史脏文件与未跟踪文件
- 本轮只做 selective write-back，不做混提 commit

## 下一轮建议
- 不再继续给 `Rank 116` 额外预算
- 直接按 `7.10` 从：
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
  重新认领 1 条新的 `paper/repo-based 5m/15m crypto` source
