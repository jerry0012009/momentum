# Rank 113 / alpha-beta abstain / profit-window clean replication → park

## 为什么这轮是它
- 先按交易台指挥板执行 `Run 1 / EMA due-check first`：实际再次运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果继续如实返回 **全 desk `waiting_not_due`**。
- 最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`；因此 `Paper Seat` 这轮没有新的 due-now / overdue 动作。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T07:59:18Z` 显示 `new_closed_trades_appended=1`，但没有新的 blocker 抢占 bot3 主资源位；所以本轮合法主动作仍是顶板点名的 **`Rank 113 / alpha-beta abstain / profit-window` 那 1 次最小 clean replication**。

## 本轮只认领了什么
- **主点**：`Rank 113 / alpha-beta abstain / profit-window` 的最小 clean replication。
- **紧邻子点**：把 verdict 写回 `docs/TODO.md` 顶板，并前推 `Next 3`。
- 没有并开第二条 Scout 候选；严格遵守“一轮最多 1 个主点 + 1 个紧邻子点”。

## 做了什么
1. 新增 `scripts/build_rank113_alpha_beta_abstain_clean_replication.py`
   - 固定只挂 **1 条 base archetype = `fib_retest_long`**；
   - 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；
   - 训练段先冻结：
     - `profit-window = hold 12 bars`
     - `signal_distance_atr = (close - fib_618) / ATR14`
     - 双阈值分位：`lower_q = 0.15`、`upper_q = 0.80`
   - 测试段统一比较三臂：
     - `baseline`
     - `lower_band_only`
     - `dual_band`
   - 口径固定为：`signal 当根及之前数据 + next-bar open + no-overlap`。
2. 运行脚本，落地 artifacts：
   - `reports/artifacts/scout_rank113_alpha_beta_abstain_profit_window_15m/`
   - `reports/site/factors/scout_rank113_alpha_beta_abstain_profit_window_15m/report.html`
   - `reports/site/reading/repo_scout/rank113_alpha_beta_abstain_profit_window_clean_replication.html`
3. 最小更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 新增 `2026-03-20 08:27 UTC` 顶板补充；
   - 把 `Rank 113` 明确压回 `park / evidence pool`；
   - 把 `Run 2 / Run 3` 前推到 `Rank 114`。

## 核心结果（6bps/side）
### baseline
- `mean_total_return ≈ 1.79%`
- `mean_trades ≈ 6.0`
- `mean_trade_retention ≈ 78.79%`
- `mean_false_follow_through_4bars ≈ 25.00%`

### lower_band_only
- `mean_total_return ≈ 0.80%`
- `mean_trades ≈ 2.0`
- `mean_trade_retention ≈ 66.67%`
- `mean_false_follow_through_4bars ≈ 0.00%`

### dual_band
- `mean_total_return ≈ 0.50%`
- `mean_trades ≈ 1.0`
- `mean_trade_retention ≈ 33.33%`
- `mean_false_follow_through_4bars ≈ 0.00%`

## 最诚实的结论
- 当前 hard verdict：**`Rank 113 = park / evidence pool`**。
- 翻成人话：
  - “太小不做、太远不追”这个想法本身没错；
  - 但这轮最小 clean replication 里，改善主要来自**大幅砍掉样本**，不是带来更高的成本后收益；
  - `lower_band_only` 和 `dual_band` 都能把坏单过滤得更干净一些，但代价是 trade retention 掉得太快，最终 desk 级收益反而不如 baseline。
- 所以它现在更适合留在证据池，不配升到 `P2 / paper candidate pool`，也不该继续占主资源位。

## 为什么这次算 exhausted
- 当前已完成它默认预算里的关键一步：
  - `source intake`
  - `两条轻量诚实守门`
  - `1 次最小 clean replication`
- 这次 replication 已经直接回答最关键问题：
  - 不是“这个 overlay 有没有任何过滤效果”，
  - 而是“它有没有形成对 desk 有意义的 honest uplift”。
- 答案是：**没有**。因此默认应 `park`，而不是继续给它更多参数微调预算。

## 席位 / 排班写回
- `Paper Seat = EMA / 创业板ETF 1d primary anchor / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat` 当前更诚实的顺序：
  1. `Rank 114 / pullback → two-sided breakout window verdict`（下一主点）
  2. `Rank 113 / alpha-beta abstain / profit-window`（`park / evidence pool`）
  3. `Rank 112 / basis dislocation short veto`（`P1 weak candidate / evidence_pool / budget used`）
  4. `Rank 111 / abnormal-return event clock`（`P1 evidence_pool / budget used`）

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`：
  1. 先做 `Rank 114 / pullback → two-sided breakout window verdict` 的 source intake；
  2. 若 guard-pass，再只给它 **1 次最小 clean replication**；
  3. 若 `Rank 114` 也 hard-fail / exhausted，再回 fresh intake（优先 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）；
  4. 只有 fresh intake 也 exhausted 后，才允许 tiny-live plumbing fallback。

## 验证 / 命令
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`；在 `require-due` 模式下以 code `2` 退出，属于预期等待路径。
- `python3 scripts/build_rank113_alpha_beta_abstain_clean_replication.py`
  - 成功写出 clean replication artifacts 与网页报告。

## Git / 工作区说明
- 当前 git 工作区存在大量与本轮无关的已修改/未跟踪文件。
- 为避免混提，本轮未提交；只保留本轮脚本、artifacts、顶板更新与日志。
