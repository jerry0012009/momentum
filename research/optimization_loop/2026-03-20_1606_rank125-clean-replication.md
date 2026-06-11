# 2026-03-20 16:06 UTC · Rank 125 / range location veto gate / clean replication

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 **`Rank 125 / range location veto gate` 的 1 次最小 clean replication**。当前 hard verdict：**`keep_P1 / weak candidate`**。

## 先检查了什么
- `git branch --show-current` -> `master`
- `git status --short | wc -l` -> 工作区继续极脏，不混提
- 最近 optimization logs：
  - `2026-03-20_1535_rank125-range-location-intake.md`
  - `2026-03-20_1515_rank124-stop-clean-replication.md`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 4.0h`、`Crypto 1d+1wk -> 8.0h`、`创业板ETF 1d -> 63.0h`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T15:41:06Z`
  - `new_closed_trades_appended=1`
  - 但这仍是 `Rank 29` 的 hosted `P3 continuity / sidecar only`，不改本轮主资源位
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - authoritative `Next 3`：`Run 1 = EMA due-check first -> Run 2 = Rank 125 minimal clean replication -> Run 3 = 按 Rank 125 verdict 决定 promote/keep/park`

## 为什么这轮认领 Rank 125
这轮不是 fresh intake，也不是回头续磨 `Rank 112 / 111` 这类已 `budget used` 的旧 `P1`。按顶板，`Rank 125` 刚完成 source intake 与两条轻量诚实守门，当前正处在最值得给那 **1 次最小 clean replication** 的时点。

它值得这 1 次预算，不是因为它像新 alpha，而是因为它直接回答 desk 里一个反复出现的执行问题：
**“这笔已经贴着近期区间边缘了，还该不该继续追，还是应该先 veto / 等确认？”**

## 本轮主点
### Rank 125 minimal clean replication
- 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache
- 统一执行口径：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - `hold 8 bars`
- 三条 baseline 一起做最小 clean-room：
  - `breakout_short`：只测试 `no-chase veto`
  - `fib_retest_long`：只测试 `reclaim confirm`
  - `ema_psar_long`：只测试轻量确认 / veto
- 训练段只冻结一组共享参数，再去测试段验证：
  - `n = 8`
  - `short_veto = RL <= 0.10`
  - `long_confirm = RL >= 0.45`

其中 `RL_n = (close - rolling_low_n) / (rolling_high_n - rolling_low_n + 1e-9)`；
下一步若还要继续，只允许围绕“这组 gate 在成本 / 交易数稳定性上是否还站得住”做 1 个最小稳定性检查，不允许再扩成新大框架。

## 结果 / 硬结论
## authoritative verdict
**`Rank 125 / range location veto gate = keep_P1 / weak candidate`**。

翻成人话：
- `range location` 这层确实有一点 honest uplift；
- 但 uplift 还不够硬，暂时只能保留在 `P1`；
- 它还不到 `P2 / paper candidate`，更不配抢 `Live Seat`。

### 测试段主读法（6 bps / side）
1. `fib_retest_long`
   - `baseline ≈ +0.154%`
   - `RL gate ≈ +0.154%`
   - `failure_before_target = 28.57% -> 28.57%`
   - `retention = 100%`
   - 读法：几乎完全等价，没有提供真正新的 gate 信息。

2. `ema_psar_long`
   - `baseline ≈ +0.221%`
   - `RL gate ≈ +0.288%`
   - `failure_before_target = 53.85% -> 52.63%`
   - `retention ≈ 97.44%`
   - 读法：有一小点 honest uplift，但幅度还不够大。

3. `breakout_short`
   - `baseline ≈ -0.110%`
   - `RL gate ≈ -0.015%`
   - `failure_before_target = 51.77% -> 49.36%`
   - `retention ≈ 55.32%`
   - 读法：`no-chase veto` 的方向没错，但改善里明显掺着“砍掉很多 trade”的成分。

### 分资产读法
- `BTC-USD`
  - `baseline ≈ -0.198%`
  - `RL gate ≈ -0.134%`
  - `delta ≈ +0.064%`
  - `retention ≈ 59.46%`
- `ETH-USD`
  - `baseline ≈ -0.037%`
  - `RL gate ≈ +0.047%`
  - `delta ≈ +0.084%`
  - `retention ≈ 70.19%`
- `SOL-USD`
  - `baseline ≈ +0.039%`
  - `RL gate ≈ +0.244%`
  - `delta ≈ +0.205%`
  - `retention ≈ 54.87%`

最诚实的读法是：
**它不是没东西，但现在更像“有一点料的 shared veto/confirm 候选”，而不是“已经证明完毕的 shared overlay”。**

## 做了什么改动
### 新增脚本
- `scripts/build_rank125_range_location_clean_replication.py`

### 生成 artifacts
- `reports/artifacts/scout_rank125_range_location_veto_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/trade_log.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/parameter_grid_scores.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/train_setup_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/test_setup_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/asset_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/metrics_by_setup_cost_split.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/summary.json`

### reader-facing 落点
- `reports/site/factors/scout_rank125_range_location_veto_15m/report.html`
- `reports/site/reading/repo_scout/rank125_range_location_veto_clean_replication.html`

### board write-back
- 已最小更新 `docs/TODO.md` 顶部 board：
  - 把 `Rank 125` 从 `guard-passed / clean replication next` 写成 `keep_P1 / 仅余 1 个真正会改变 verdict 的最小稳定性检查`
  - 更新 active Scout 顺序
  - 把 `Next 3` 改写为：
    - `Run 1 = EMA due-check first`
    - `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 125 1 个最小 Light Stability Pack（默认优先 成本 / 交易数稳定性）`
    - `Run 3 = 再按这 1 个稳定性检查决定 promote_P2 / keep_P1 / park；若失败则回 fresh intake`

## 验证 / 证据
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`
- `python3 scripts/build_rank125_range_location_clean_replication.py`
  - 成功生成 artifacts 与 reader-facing 页面
  - 输出冻结参数：`n=8 / short=0.10 / long=0.45`
  - 输出 hard verdict：`keep_P1 / weak candidate`

关键证据文件：
- `reports/artifacts/scout_rank125_range_location_veto_15m/test_setup_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/asset_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/parameter_grid_scores.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/summary.json`

## 风险 / 边界
- 当前 uplift 还不够硬，尤其 `breakout_short` 的改善伴随明显 retention 下滑；
- `fib_retest_long` 在这轮几乎没贡献额外信息，说明这条 overlay 暂时并不是真正三线通吃；
- 论文主证据来自股票日频，当前只是借 `range location` 这个可解释旁支做 15m clean-room；
- 按 desk 预算，`Rank 125` 不能无限续命；下一轮若再给预算，也只能是 **1 个真正会改变 verdict 的最小稳定性检查**。

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 125 1 个最小 Light Stability Pack，优先 成本 / 交易数稳定性`
  - 目标问题：这点 uplift 在 `10/15 bps` 下是否还成立，trade count retention 是否会进一步塌掉
- `Run 3 = 按这 1 个稳定性检查直接做 promote_P2 / keep_P1 / park`
  - 若 uplift 被证明主要只是样本筛选，就直接 `park` 并回 fresh intake

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 125` 直接相关文件与 board 局部更新，不适合混提。
