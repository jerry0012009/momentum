# 2026-03-18 15:24 UTC — Rank 58 / event-anchored VWAP 最小 clean replication

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 因此 `Paper Seat / EMA` 仍是 **`running paper / waiting_not_due`**，这轮不能把整桌误判成等待态。
- 顶板 `Next 3` 的权威顺序要求这轮执行 **`Run 2 / Rank 58 minimal clean replication`**：它刚完成 source intake + 两条轻量诚实守门，本轮只允许给它一次最小复现预算，回答 event-anchored VWAP 能不能比 session VWAP 更诚实地充当 shared hold-reclaim spine。

## 做了什么
### 主点：完成 Rank 58 的最小 clean replication
- 新增脚本：
  - `scripts/build_rank58_event_anchored_vwap_clean_replication.py`
- 新增 artifact：
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/signal_snapshot.csv`
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/asset_setup_summary.csv`
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/time_pockets.csv`
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/anchor_mix_summary.csv`
  - `reports/artifacts/scout_rank58_event_anchored_vwap_15m/trades.csv`
- 新增 reader-facing 页面：
  - `reports/site/factors/scout_rank58_event_anchored_vwap_15m/report.html`
  - `reports/site/reading/repo_scout/rank58_event_anchored_vwap_clean_replication.html`

### 紧邻子点：最小 authoritative writeback
- 在 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 下追加 `2026-03-18 15:24 UTC` 补充：
  - 把本轮结果冻结为 **`Rank 58 = park / evidence pool`**；
  - 写回最小 clean replication 的核心指标；
  - 将下一轮默认顺序改回：`Run 1 = EMA due-check only -> Run 2 = fresh paper/repo intake（优先 continuation fail-fast overlay > pullback-quality / CQI > 其他 fresh pool source） -> Run 3 = 只有 fresh pool 也 exhausted 时才回退到 Rank 35b > Rank 16b > tiny-live plumbing`。

## 本轮冻结口径
- 只复用 `BTC/ETH/SOL 120d 15m` 本地 cache；不追新 bar。
- 只比较三条最小 archetype：
  - `ema_psar_long`
  - `fib_retest_long`
  - `breakout_short`
- 四臂固定为：
  - `base`
  - `session_vwap_gate`
  - `event_avwap_gate`
  - `event_avwap_gate + 0.5ATR proximity`
- 所有执行统一冻结到：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - `hold 8 bars`
- event anchor 类型提前冻结，避免事后挑 anchor：
  - `ema15 reclaim trigger`
  - `fib0.618 reclaim trigger`
  - `rolling-low breakdown trigger`

## 验证 / 证据
### 1）总体结果（6bps/side）
- `base`
  - `mean_total_return ≈ -2.02%`
  - `positive_asset_ratio ≈ 33.33%`
  - `mean_trades ≈ 22.11`
  - `false_follow_4bars ≈ 81.14%`
- `session_vwap_gate`
  - `mean_total_return ≈ -2.51%`
  - `positive_asset_ratio ≈ 22.22%`
  - `mean_trades ≈ 20.89`
  - `trade_count_retention ≈ 91.37%`
  - `false_follow_4bars ≈ 24.48%`
- `event_avwap_gate`（主读法）
  - `mean_total_return ≈ -1.35%`
  - `positive_asset_ratio ≈ 44.44%`
  - `mean_trades ≈ 20.78`
  - `trade_count_retention ≈ 93.68%`
  - `false_follow_4bars ≈ 61.45%`
- `event_avwap_gate + 0.5ATR proximity`
  - `mean_total_return ≈ -0.37%`
  - `positive_asset_ratio ≈ 33.33%`
  - `mean_trades ≈ 11.44`
  - `trade_count_retention ≈ 53.53%`
  - `false_follow_4bars ≈ 69.88%`

### 2）time-pocket
- `event_avwap_gate`
  - `bucket_1 ≈ -1.05% / positive_asset_ratio ≈ 55.56%`
  - `bucket_2 ≈ -0.71% / positive_asset_ratio ≈ 33.33%`
  - `bucket_3 ≈ +0.54% / positive_asset_ratio ≈ 33.33%`
- 读法：只在最后一段出现轻微正 pocket，不足以支撑升格；更像 pocket-level 收敛，而不是跨时间稳定成立。

### 3）anchor mix
- `ema_psar_long / ema15 reclaim trigger`
  - `signals = 110`
  - `event_gate_pass_rate ≈ 97.27%`
  - `event_plus_proximity_pass_rate ≈ 41.82%`
- `fib_retest_long / fib0.618 reclaim trigger`
  - `signals = 34`
  - `event_gate_pass_rate = 100%`
  - `event_plus_proximity_pass_rate ≈ 50.00%`
- `breakout_short / rolling-low breakdown trigger`
  - `signals = 63`
  - `event_gate_pass_rate ≈ 80.95%`
  - `event_plus_proximity_pass_rate ≈ 63.49%`
- 读法：event gate 本身并没有极端砍样本，说明它不是纯粹“几乎不给交易”；但 false follow-through 仍偏高，没把 shared hold spine 做成足够干净的 admission 证据。

## 当前硬结论
- **`Rank 58 / event-anchored VWAP hold-reclaim spine = park / evidence pool`**。
- 更直白地说：
  - 它比 `session_vwap_gate` 少亏，且 trade retention 没明显塌掉；
  - 但主读法仍是成本后负收益，且 `false_follow_4bars` 仍高；
  - `+0.5ATR proximity` 虽进一步收敛亏损，但已经明显更像通过额外切样本获得的表面改善；
  - 因此这条线当前更像 execution-layer evidence，不够诚实升到 `P1/P2` active fast lane。

## 风险 / 边界
- 这轮只回答“event anchor 能不能比 session 锚点更诚实”，没有把它扩成独立 alpha，也没有重写任何现有主线策略规则。
- 当前 `manual_narrow_paper_last_run_summary.json` 在 `2026-03-18T15:19:15Z` 已出现 `new_closed_trades_appended=2`，但本轮仍优先遵守顶板 `Run 1 -> Run 2` 权威顺序，先消化 Rank 58 的最小 replication。若 bot2 认为这些 append 属于真实 status-changing continuity 事件，可在后续独立轮次低频处理，不应反过来覆盖本轮已被权威指定的 Scout 主动作。
- git 工作区有大量与本轮无关的既有脏文件 / 未跟踪产物；本轮未做 commit，避免混提。

## 下一步建议
1. 下一轮若 `EMA` 仍 `waiting_not_due`，按 `7.10` 回到 **fresh paper/repo intake**。
2. 当前优先回到：`continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source`，只认领 1 条新的 `5m / 15m crypto` paper/repo 候选。
3. 除非出现新的 `due-now / overdue` paper refresh，或 bot2 明确点名 status-changing continuity 事件，否则不要回头继续磨 `Rank 58` 的近义 admission / wording。

## Reader-facing 落点
- `reports/site/factors/scout_rank58_event_anchored_vwap_15m/report.html`
- `reports/site/reading/repo_scout/rank58_event_anchored_vwap_clean_replication.html`

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关的既有脏文件与未跟踪产物；本轮只做最小必要写回，不安全混提。
