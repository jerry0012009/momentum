# 2026-03-19 10:37 UTC — Rank 86 时间稳定性检查后压回 park

## 为什么这轮选这个
- 先按 `Run 1` 执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 脚本返回 `waiting_not_due`：当前仍无 `due-now / overdue` lane；最近 due 仍是美股 `1d+1wk -> 约 9.4h`，其后是 Crypto `1d+1wk -> 约 13.4h`。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-19T10:18:24Z` 仍为 `new_closed_trades_appended=0`，没有新的 `P3` 状态变化值得抢主资源。
- 因此按 `TRADING DESK BOARD / Next 3`，本轮唯一合法主动作就是给 `Rank 86 / SignalPro penetration×ATR admission` 做那 **1 次 truly verdict-changing 的 Light Stability Pack**，默认先做时间稳定性。

## 本轮只做了 1 个主点
1. 新增并执行：`scripts/build_rank86_time_stability_check.py`
   - 直接复用 `reports/artifacts/scout_rank86_signalpro_penetration_atr_15m/trade_samples.csv`
   - 只看 `6bps/side`
   - 对每个 `asset × setup × variant` 按时间顺序切成 `3` 个等样本 bucket
   - 不追新 bar，不扩参数，不补近义 intake 文案

## 产物
- 脚本：`scripts/build_rank86_time_stability_check.py`
- artifacts：
  - `reports/artifacts/scout_rank86_signalpro_penetration_atr_15m/time_stability_window_summary.csv`
  - `reports/artifacts/scout_rank86_signalpro_penetration_atr_15m/time_stability_verdict_summary.csv`
- reader-facing：
  - `reports/site/factors/scout_rank86_signalpro_penetration_atr_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank86_signalpro_penetration_atr_time_stability.html`
- board write-back：`docs/TODO.md` 顶部 `Next 3 bot3 runs`

## 验证 / 关键证据
### 1) Run 1 仍是 waiting_not_due
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：
  - 无 `due-now / overdue`
  - 最近 due：美股 `~9.4h`，Crypto `~13.4h`
  - `require-due` 生效，因此不伪造 refresh

### 2) Rank 86 时间稳定性不过关
最关键的不是 clean replication 的 overall 还勉强站住，而是 **拆成时间桶后站不住**：

- `ema_psar_follow_short + pen_plus_atr`
  - overall：`mean_total_return ≈ +0.03%`
  - bucket_1：`≈ +1.36%`
  - bucket_2：`≈ +1.53%`
  - bucket_3：`≈ -2.91%`
  - 读法：前两段有一点改善，但后段重新漏放，不能说稳

- `fib_retest_short + pen_plus_atr`
  - overall：`mean_total_return ≈ +2.18%`
  - bucket_1：`≈ +4.43%`
  - bucket_2：`≈ -0.72%`
  - bucket_3：`≈ -1.91%`
  - 读法：更像前段 pocket，而不是三段都可复现的 shared admission

- `breakout_short + pen_plus_atr`
  - overall：`≈ -1.55%`
  - 三桶只有第一桶为正，其余继续为负
  - 读法：这条 shared gate 没把 breakout 线稳定救回来

`time_stability_verdict_summary.csv` 里：
- 大多数组合直接是 `fails_time_check`
- 最好的 `ema_psar_follow_short + pen_plus_atr` 也只到 `watch_only / mixed pockets`
- 没有任何组合达到“all buckets positive with basic cross-asset support”

## 本轮 hard verdict
- **`Rank 86 / SignalPro penetration×ATR admission = park / evidence_pool`**

含义：
- 这条线到此为止，不再给默认 fast-lane 预算
- 当前不能升到 `P2 / paper candidate pool`
- 不应继续围着它补新的 intake / operator wording / 近义说明

## 对交易台排班的直接影响
当前更诚实的 Scout 读法应收紧为：
- `Rank 86 = P0（park / evidence_pool）`
- `fresh paper/repo intake = 当前默认主资源位`
- `breakout-candle compression reclaim = backlog only`
- `Rank 82 / Rank 80 / Rank 81 = P1 evidence_pool`
- `Rank 78 / 17 / 2 / 29 / 32b = P3 narrow paper continuity`
- `P2` 仍空，`P4` 仍空

因此 `Next 3` 应改为：
1. `Run 1 = EMA due-check only`
2. `Run 2 = fresh paper/repo intake（按 7.10 先查 RECENT_PAPER_SEEDS / quant_digests / validated shortlist，只认领 1 条新的 5m / 15m crypto source）`
3. `Run 3 = 若新 source guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication；只有 fresh intake 仍 exhausted，才回退到 breakout-candle compression reclaim backlog > Rank 82 / 80 / 81 evidence_pool > tiny-live plumbing`

## 风险 / 边界
- 本轮严格只做了 1 次 truly verdict-changing 的时间稳定性检查，没有扩成完整四件套 Stability Pack。
- 工作区仍有大量与本轮无关的脏文件；本轮未提交，避免混提。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，按板子直接回到 **fresh paper/repo intake**。
- 默认不要再给 `Rank 86` 续命，除非后续有新的独立证据能改变 verdict。

## Commit hash
- 未提交（遵循“有大量无关脏文件时不混提”）。
