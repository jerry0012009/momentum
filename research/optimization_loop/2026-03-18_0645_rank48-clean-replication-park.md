# 2026-03-18 06:45 UTC — Rank 48 / session-range active-hours gate clean replication -> park

## 本轮为什么做这个
- 先按 `docs/TODO.md -> TRADING DESK BOARD -> Next 3 bot3 runs` 检查当前 desk：
  - `Run 1 / EMA` 仍处于 **`running paper / waiting_not_due`**；A 股下一次 close 仍是 `2026-03-18 07:00 UTC`，当前轮次还没有新的 due-now / overdue bar。
  - `Rank 46 / OI participation gate` 与 `Rank 47 / EMA-ADX-VOL skeleton` 都已在允许预算内完成最小 clean replication，并已给出 **`park / evidence pool`** hard verdict。
  - 当前 active Scout 候选里，`Rank 48 / session-range active-hours gate` 是唯一更高边际价值的 fresh `repo + paper based` 候选；`Rank 35b` 仍只是 queue-only fallback。
- 因此本轮按指挥板只认领 **1 个主点**：`Run 2 / Rank 48 minimal clean replication`。

## 开始前检查
### repo / seat / dirty state
- repo：`/root/clawd/jerry/momentum`
- 交易台状态：`Paper Seat = EMA waiting_not_due`，`Live Seat = 空席`，本轮默认走 `Scout Seat`
- 当前工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；因此本轮不做混提、不做风险 commit。
- 最近 optimization loop 已存在：
  - `2026-03-18_0622_rank48-session-range-intake.md`
  - 更早若干 `Rank 46 / Rank 47` clean replication / intake 记录

## 这轮实际做了什么
### 主点：对 Rank 48 做最小 clean replication
新写脚本：
- `scripts/build_rank48_session_range_active_hours_clean_replication.py`

新产物：
- `reports/artifacts/scout_rank48_session_range_active_hours_15m/overall_summary.csv`
- `reports/artifacts/scout_rank48_session_range_active_hours_15m/setup_scorecard.csv`
- `reports/artifacts/scout_rank48_session_range_active_hours_15m/session_bucket_summary.csv`
- `reports/artifacts/scout_rank48_session_range_active_hours_15m/all_trades.csv`
- `reports/site/factors/scout_rank48_session_range_active_hours_15m/report.html`

### 固定口径
- 样本：`BTC / ETH / SOL | 120d | 15m`
- 执行：`next-bar open + no-overlap + hold 8 bars`
- Rank 48 只被当作 **共用 overlay**，不被误写成新 raw alpha
- 三条 base setup：
  - `ema_psar`
  - `fib_retest`
  - `breakout_reclaim`
- 五档对照：
  - `raw_all_day`
  - `active_hours_only`
  - `session_structure_gate`
  - `session_structure_plus_volume`
  - `session_structure_plus_volume_trend`

### 紧邻子点：修正一次统计口径错误
- 首次跑完后，发现我把 `trade_count_retention` 误算成了接近恒为 `1.0` 的 `signal_to_trade_ratio`，这会把“样本是否被过度砍掉”写得不诚实。
- 立刻修脚本并重跑：
  - 改成相对 `raw_all_day` 的 `mean_trades` 保留率；
  - 因此 verdict 从初跑的误判 `P1 weak candidate` 修正为更诚实的 **`park / evidence pool`**。
- 这轮没有让错误口径留在最终写回里。

## 核心结果
### 6bps/side 下的最关键对照
1. `ema_psar`
- `raw_all_day`: `mean_total_return≈-27.84%`，`positive_asset_ratio=0/3`，`mean_trades≈455.3`，`early_fail_4bars≈50.70%`
- `session_structure_plus_volume_trend`: `≈+3.82%`，`positive_asset_ratio≈66.67%`，`mean_trades≈66.7`
- 但问题是：`trade_count_retention≈14.64%`，而 `early_fail_4bars` 还从 `≈50.70%` **小幅升到** `≈51.12%`
- 结论：改善主要来自极强 sample compression，不够诚实

2. `fib_retest`
- `raw_all_day`: `mean_total_return≈-1.58%`，`positive_asset_ratio≈33.33%`，`mean_trades≈73.0`，`early_fail_4bars≈48.06%`
- `session_structure_plus_volume_trend`: `≈-1.15%`，`positive_asset_ratio≈66.67%`，`mean_trades≈17.0`
- `trade_count_retention≈23.29%`，`early_fail_4bars≈47.18%`
- 结论：只算轻微修剪，不足以升级 seat judgement

3. `breakout_reclaim`
- `raw_all_day`: `mean_total_return≈-9.54%`，`positive_asset_ratio=0/3`，`mean_trades≈104.7`，`early_fail_4bars≈52.50%`
- `session_structure_plus_volume_trend`: `≈-0.45%`，`positive_asset_ratio≈33.33%`，`mean_trades≈40.7`
- `trade_count_retention≈38.85%`，`early_fail_4bars≈45.09%`
- 结论：是三条里最像“有点价值”的执行 veto，但还没强到足够把 Rank 48 升格

## 本轮硬结论
- **`Rank 48 / session-range active-hours gate = park / evidence pool`**
- 更诚实的解释：
  - 它确实显示出“dead hours / session context 有信息量”；
  - 但当前最小 replication 更像证明它是 **execution / veto template**，不是已经足够改变交易台判断的共用 overlay；
  - 改善并没有在足够多 base setup 上同时满足：
    - 成本后表现改善
    - 4-bar early-fail 明显下降
    - 且不是靠过度砍样本得到

## 指挥板 / 网页外显更新
已写回：
- `docs/TODO.md`
  - 补入 `2026-03-18 06:45 UTC` 的 Rank 48 hard verdict
  - 更新 `Next 3 bot3 runs`
- reader-facing 页面：
  - `reports/site/factors/scout_rank48_session_range_active_hours_15m/report.html`

## 下一步更诚实的顺序
- 若接下来一轮（约 `06:48 UTC`）`EMA` 仍 `waiting_not_due`：
  - 先按 `7.10` 回到 **fresh source intake**：`docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
  - 只认领 1 条新的 `paper / repo based 5m / 15m crypto` 候选
  - 若同轮仍拿不到合格 source，再退到 `Rank 35b / tiny-live plumbing`
- 接近 `07:01 UTC` 的下一轮：
  - 默认优先回 **`EMA due-now follow-up`**

## 验证
- 脚本执行成功：`python3 scripts/build_rank48_session_range_active_hours_clean_replication.py`
- 关键落点存在：
  - `ok_html = reports/site/factors/scout_rank48_session_range_active_hours_15m/report.html`
  - `ok_overall = reports/artifacts/scout_rank48_session_range_active_hours_15m/overall_summary.csv`
  - `ok_scorecard = reports/artifacts/scout_rank48_session_range_active_hours_15m/setup_scorecard.csv`
  - `ok_todo = docs/TODO.md`

## commit
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不安全混提。
