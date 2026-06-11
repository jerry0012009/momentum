# 2026-03-19 23:38 UTC — Rank 102 impulse re-break time stability -> park

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最靠前 lane：`Crypto 1d+1wk -> due_soon / 约 23 分钟后到点`
- 因此按 `TRADING DESK BOARD` 当前 authoritative `Next 3`，本轮合法主动作只能落在：
  - `Scout Seat / Rank 102 / retest 后重破 impulse extreme continuation gate`
  - 剩下那 `1` 次 **truly verdict-changing** 的便宜诚实检查（默认时间稳定性）

## 开轮检查
- branch：`master`
- repo 工作区仍有大量与本轮无关的既有脏文件；本轮不混提、不清理。
- 最近 optimization logs：
  - `2026-03-19_2315_rank102-clean-replication.md`
  - `2026-03-19_2258_rank102-impulse-rebreak-intake.md`
  - `2026-03-19_2233_rank101-volume-drydown-clean-replication.md`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-19T23:03:00Z` 虽出现 `new_closed_trades_appended=2`，但仍只构成 `P3 continuity sidecar` 观察权，不足以抢走当前 Scout 主资源位。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 102 / retest 后重破 impulse extreme continuation gate`**
   - 顶板已明确要求：若 `EMA` 仍 `waiting_not_due`，本轮就先给它那 `1` 次 truly verdict-changing 的便宜诚实检查。
   - 当前它仍高于 `Rank 103`，因为 clean replication 已完成，只差最后一次 cheap honesty check 就能直接收口。
2. **`Rank 103 / confirmed extremum honest fib anchor`**
   - 继续保留为 `P0 / fresh repo reserve`；只有当 `Rank 102` 本轮完成 cheap check 后被诚实压回 `park`，才释放为下一条默认主线。
3. **`post-break sign-flip density` / `prebreak higher-low pressure ladder context gate` / `tiny-live plumbing`**
   - 当前都不该抢本轮主资源。

结论：本轮只认领 `Rank 102` 的时间稳定性检查，不并开第二条候选。

## 本轮认领
- 主点：`Rank 102 / retest 后重破 impulse extreme continuation gate`
- 紧邻子点：把 hard verdict、reader-facing 页面、`TODO` 顶板一次写齐

## 便宜诚实检查口径（time stability）
- 新脚本：`scripts/build_rank102_time_stability_check.py`
- 复用 artifact：
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/trade_log.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/overall_summary.csv`
- 只检查上一轮唯一存活的主读法：
  - `breakout_short_signal + impulse_rebreak_gate`
- 口径固定不变：`BTC / ETH / SOL | 120d | 15m | next-bar open | no-overlap | 6bps/side`
- 检查方式：
  - 不追新 bar、不改规则
  - 把样本按时间顺序拆成 **`older_half / recent_half`** 两半窗
  - 直接检查：
    - 跨资产平均总收益是否两半都能站住
    - `positive_asset_ratio` 是否两半都够硬
    - `false_follow_4bars` 是否只在后半窗偶然改善

## 结果
### 1) half summary
- `older_half`
  - `mean_total_return ≈ -0.14%`
  - `positive_asset_ratio = 1/3`
  - `mean_trade_count ≈ 39.7`
  - `mean_avg_net_ret ≈ +1.81bps`
  - `mean_false_follow_4bars ≈ 55.65%`
- `recent_half`
  - `mean_total_return ≈ +5.28%`
  - `positive_asset_ratio = 2/3`
  - `mean_trade_count ≈ 39.3`
  - `mean_avg_net_ret ≈ +15.49bps`
  - `mean_false_follow_4bars ≈ 43.82%`

### 2) per-asset 最诚实拆分
- `older_half`
  - `BTC`: `total_return ≈ -7.78%`，`avg_net_ret ≈ -19.51bps`，`false_follow_4bars ≈ 58.54%`
  - `ETH`: `total_return ≈ +10.56%`，`avg_net_ret ≈ +31.12bps`，`false_follow_4bars ≈ 47.06%`
  - `SOL`: `total_return ≈ -3.19%`，`avg_net_ret ≈ -6.20bps`，`false_follow_4bars ≈ 61.36%`
- `recent_half`
  - `BTC`: `total_return ≈ +5.49%`，`avg_net_ret ≈ +14.18bps`，`false_follow_4bars ≈ 47.50%`
  - `ETH`: `total_return ≈ +13.12%`，`avg_net_ret ≈ +36.94bps`，`false_follow_4bars ≈ 29.41%`
  - `SOL`: `total_return ≈ -2.78%`，`avg_net_ret ≈ -4.64bps`，`false_follow_4bars ≈ 54.55%`

### 3) 这轮最诚实的解释
- `impulse re-break` 并不是完全没料；它在 `recent_half` 确实表现出 shared continuation 改善的味道。
- 但真正决定 verdict 的问题是：**它没有穿过 older half**。
  - older half 仍只有 `ETH` 为正，`BTC / SOL` 都没转过来
  - `positive_asset_ratio` 只到 `1/3`
  - `false_follow_4bars` 还停在 `≈55.65%`
- 换成人话：这条 gate 更像**后半窗 pocket**，不是两半都够硬的稳定 shared gate。

## 本轮 hard verdict
- **`Rank 102 = park / evidence pool`**

### 为什么不是 `promote_to_P2`
1. 两半窗并没有都转正；`older_half` 仍没穿过时间稳定性。
2. `positive_asset_ratio` 只在 recent half 到 `2/3`，older half 仍只有 `1/3`。
3. `false_follow_4bars` 的改善也主要集中在后半窗，尚不足以证明稳定 shared gate。

### 为什么也不再保留 `keep_P1`
1. 顶板已明确：这次 cheap check 做完后，应直接在 `promote_to_P2 / park` 之间收口，不再给第三轮近义检查。
2. 当前真正过门的只有 `recent_half`；这不足以继续占 active Scout 主资源位。
3. 因此最诚实的 desk 动作是：**把 Rank 102 正式压回 park，并把下一手切到 Rank 103 fresh intake**。

## 本轮交付（deployable artifact）
- script:
  - `scripts/build_rank102_time_stability_check.py`
- artifacts:
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/time_stability_window_summary.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/time_stability_asset_window_summary.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/time_stability_verdict_summary.csv`
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/time_stability_summary.json`
- reader-facing:
  - `reports/site/factors/scout_rank102_impulse_rebreak_continuation_15m/time_stability_check.html`
  - `reports/site/reading/repo_scout/rank102_impulse_rebreak_continuation_time_stability.html`

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due（Crypto due_soon）`
- `Live Seat = 暂空`
- `Rank 102 = P0 / park / evidence pool`
- `Rank 103 = P0 / fresh repo reserve / source intake next`
- 当前最新 `Next 3`：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 若 EMA 仍 waiting_not_due 且 Crypto 尚未切到 due-now / overdue，则切 Rank 103 / confirmed extremum honest fib anchor 的 source intake + 两条轻量诚实守门`
  3. `Run 3 = 若 Crypto 已 due-now / overdue，则先执行 EMA guarded refresh；若到时仍 waiting_not_due 且 Rank 103 已 guard-pass，则只给 Rank 103 1 次最小 clean replication`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 如实确认当前还是 `waiting_not_due / Crypto due_soon`
- `python3 scripts/build_rank102_time_stability_check.py`
  - 已成功写出 artifact 与 reader-facing 页面
- 回读：
  - `reports/artifacts/scout_rank102_impulse_rebreak_continuation_15m/time_stability_verdict_summary.csv`
  - `docs/TODO.md`
  - 已确认 hard verdict 与更新后的 `Next 3` 写入成功

## 备注
- 本轮没有并开 `Rank 103`
- 本轮没有触发 `P3 continuity` 或 `tiny-live plumbing`
- 工作区仍有大量历史脏文件；本轮未尝试整理、提交或覆盖这些无关改动
