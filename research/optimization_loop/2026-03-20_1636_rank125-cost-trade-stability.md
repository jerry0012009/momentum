# 2026-03-20 16:36 UTC · Rank 125 / range location veto gate / 成本-交易数稳定性检查

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 **`Rank 125 / range location veto gate` 的 1 个最小 Light Stability Pack：成本 / 交易数稳定性检查**。当前 hard verdict：**`keep_P1 / budget used`**。

## 先检查了什么
- `git branch --show-current` -> `master`
- `git status --short | wc -l` -> 工作区继续极脏（约 `1913` 条），不混提
- 最近 optimization logs：
  - `2026-03-20_1606_rank125-clean-replication.md`
  - `2026-03-20_1535_rank125-range-location-intake.md`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 3.4h`、`Crypto 1d+1wk -> 7.4h`、`创业板ETF 1d -> 62.4h`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T16:11:14Z`
  - `new_closed_trades_appended=3`
  - 但这仍是 hosted `P3 continuity / sidecar only`，不改本轮主资源位
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - authoritative `Next 3`（本轮前）是：`Run 1 = EMA due-check first -> Run 2 = Rank 125 成本/交易数稳定性检查 -> Run 3 = 按这 1 个最小检查决定 promote_P2 / keep_P1 / park`

## 为什么这轮继续认领 Rank 125
上一轮 `Rank 125` 已完成 clean replication，但结论还停在 **`keep_P1 / weak candidate`**：
- 不是没料；
- 也不是已经硬到能升 `P2 / paper candidate`；
- 真正没回答清楚的，只剩一个问题：
  **这点 uplift 在更高 friction 下还能不能站住，还是只是靠砍 trade 换出来的样本筛选假象？**

按当前 desk 预算，这正好就是它最后还配拿的那 **1 个 truly verdict-changing 最小检查**。

## 本轮主点
### Rank 125 · 成本 / 交易数稳定性检查
- 直接复用上一轮 clean-room 的同一份 `trade_log`
- 不再改 setup 定义，也不再扩参数空间
- 继续固定上一轮已经冻结的参数：
  - `n = 8`
  - `short_veto = RL <= 0.10`
  - `long_confirm = RL >= 0.45`
- 只看三档 friction：
  - `6 bps / side`
  - `10 bps / side`
  - `15 bps / side`
- 只回答三个问题：
  1. `return delta` 还在不在；
  2. `failure delta` 有没有恶化；
  3. `trade retention` 有没有塌到失真。

执行脚本：
- `python3 scripts/build_rank125_cost_trade_stability_check.py`

## 结果 / 硬结论
## authoritative verdict
**`Rank 125 / range location veto gate = keep_P1 / budget used`**。

翻成人话：
- 这条线不是一加成本就直接穿帮；
- 但它也还不够硬，达不到 `P2 / paper candidate`；
- 当前更诚实的位置是：**保留为值得留样的 shared veto/confirm 线索，但默认预算用尽，不再继续占 fast lane 主资源。**

### 总体稳定性快照
- `mean_return_delta ≈ +0.054%`
- `mean_failure_delta ≈ -1.21 pct`
- `mean_trade_retention ≈ 84.25%`
- 三档成本下都保持：
  - `positive_setup_count = 2 / 3`
  - `non_worsening_failure_count = 3 / 3`

### 分 setup 读法
1. `breakout_short`
   - `6bps`: `-0.110% -> -0.015%`，`delta ≈ +0.095%`
   - `failure_before_target: 51.77% -> 49.36%`
   - `trade_retention ≈ 55.32%`
   - 读法：`no-chase veto` 方向没错，但改善仍明显伴随 trade 被砍掉。

2. `ema_psar_long`
   - `6bps`: `+0.221% -> +0.288%`，`delta ≈ +0.067%`
   - `failure_before_target: 53.85% -> 52.63%`
   - `trade_retention ≈ 97.44%`
   - 读法：有小幅、相对干净的增益，但量级还不够把它推成 shared 默认层。

3. `fib_retest_long`
   - 三档成本下两臂几乎完全等价
   - `trade_retention = 100%`
   - 读法：这条 setup 上几乎没有新增 gate 信息，说明它还谈不上真正三线通吃。

### 为什么不是 `promote_P2`
因为当前最硬的事实不是“它没用”，而是：
- uplift 主要集中在 `breakout_short` 与 `ema_psar_long`；
- `fib_retest_long` 基本没有贡献；
- `breakout_short` 的改善继续伴随明显 retention 下滑；
- 还不够像一条 **足够稳定、可直接进入 paper candidate pool 的 shared overlay**。

### 为什么也不是直接 `park`
因为它又确实没被 friction 直接打回零：
- 三档成本下都有 `2/3` setup 保留正增量；
- `failure rate` 也没有恶化；
- 所以更诚实的动作不是“宣布死亡”，而是 **留样，但停止继续烧默认预算**。

## 做了什么改动
### 执行脚本
- `scripts/build_rank125_cost_trade_stability_check.py`

### 生成 / 刷新 artifacts
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_overall.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/asset_cost_stability_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.json`

### reader-facing 落点
- `reports/site/factors/scout_rank125_range_location_veto_15m/cost_trade_stability_check.html`
- `reports/site/reading/repo_scout/rank125_range_location_veto_cost_trade_stability.html`

### board write-back
已最小更新 `docs/TODO.md` 顶部 board：
- 把 `Rank 125` 从“还剩 1 个最小稳定性检查”写成 **`keep_P1 / budget used`**；
- 保留其 reader-facing 证据位置，但不再把它当默认主资源位；
- 把 `Next 3` 改写为：
  - `Run 1 = EMA due-check first`
  - `Run 2 = 若 EMA 仍 waiting_not_due，则优先 fresh intake`
  - `Run 3 = 若新的 fresh intake guard-pass，则只给它 1 次最小 clean replication；否则才允许 tiny-live plumbing fallback`

## 验证 / 证据
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`
- `python3 scripts/build_rank125_cost_trade_stability_check.py`
  - 成功输出最新 summary
  - `generated_at_utc = 2026-03-20 16:35:57 UTC`
  - `verdict = keep_P1_budget_used`

关键证据文件：
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_overall.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/asset_cost_stability_summary.csv`
- `reports/artifacts/scout_rank125_range_location_veto_15m/cost_trade_stability_summary.json`

## 风险 / 边界
- `Rank 125` 还没有硬到能升 `P2`；
- 当前 uplift 仍带有一定筛样本成分，尤其在 `breakout_short` 上更明显；
- `fib_retest_long` 基本不贡献增益，说明 shared 性还不够；
- 按 desk 预算，当前不应继续围着 `Rank 125` 打转，更不该继续补近义说明页。

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条新的 fresh intake`
  - `Run 3 = 若新的 fresh intake guard-pass，则只给它 1 次最小 clean replication`
- hosted `P3` continuity（`Rank 122 / 2 / 17 / 29 / 32b`）继续只按 sidecar 看待；除非出现真正 `due-now / status-changing event`，否则不抢 bot3 主资源。

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 125` 直接相关文件、reader-facing 页面与 board 局部更新，不适合混提。
