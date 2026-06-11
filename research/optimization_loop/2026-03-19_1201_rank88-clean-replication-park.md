# 2026-03-19 12:01 UTC — Rank 88 宏观事件 overlay clean replication -> park

## 本轮先做的 desk 检查（Run 1）
- 已先核对 repo 状态 / 最近 runs / 当前脏文件：
  - `git status --short` 仍显示大量与本轮无关的脏文件（未尝试混提）
  - 最近 optimization logs 最新到 `11:49 UTC / Rank 88 source intake`
- 已实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`waiting_not_due`**
  - 当前仍无 `due-now / overdue` lane
  - 最近 due 约为：`美股 8.1h`、`Crypto 12.1h`、`A股 19.1h`
- 已读取 `manual_narrow_paper_last_run_summary.json @ 2026-03-19T11:48:48Z`
  - `new_closed_trades_appended=0`
- 结论：`Paper Seat = EMA / running paper / waiting_not_due` 仍成立；本轮合法主动作确实只剩 `Run 2 / Rank 88` 这一手最小 clean replication。

## 本轮主点 + 紧邻子点
- **主点**：`Run 2 / Rank 88 / macro-event blackout + size-down risk overlay` 最小 clean replication
- **紧邻子点**：把 `TRADING DESK BOARD / Next 3` 按 hard verdict 写回到新的 breakout-centric backlog 顺序

## 先比较 active Scout 候选边际价值（3.5）
本轮进入执行前沿用顶板最新顺序：
1. `Rank 88 / macro-event blackout + size-down risk overlay`
2. 两条 breakout-centric digest backlog：
   - `outside-close -> back-inside-close failure verdict`
   - `close-range compression asymmetry`
3. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
4. `P3 continuity`
5. `tiny-live plumbing`

执行后，这个顺序应更新为：
1. 两条 breakout-centric digest backlog
2. `Rank 82 / Rank 80 / Rank 81 evidence_pool`
3. `P3 continuity`
4. `tiny-live plumbing`

原因：`Rank 88` 这手最小 replication 已经预算用尽，而且直接给出了 `park` verdict，不该继续占默认主资源位。

## 本轮最小 clean replication 口径
- Universe：`BTC / ETH / SOL 120d 15m` 本地 cache
- base setups：`ema_psar_long`、`fib_retest_long`、`breakout_short`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 成本：`6 / 10 / 15 bps per side`
- 事件时间：只使用公开、事前可得的 `FOMC / CPI` 发布时间（复用 `reports/artifacts/literature/macro_event_overlay_quickcheck_events_2026-03-19.csv`）
- 对照四臂：
  1. `baseline`
  2. `blackout[-1h,+1h]`
  3. `size_down_0.5x`
  4. `hybrid[-30m,+30m] blackout + (+30m,+120m) size_down`

## Hard verdict
- **`Rank 88 / macro-event blackout + size-down risk overlay = park / evidence_pool`**

### 为什么直接 park
- `6bps/side` 下，最好的也只是 `size_down_0.5x`，但结果仍为：
  - `mean_total_return≈-30.57%`（baseline≈`-28.85%`）
  - `positive_asset_ratio=1/3`
  - `trade_count_retention≈86.96%`
  - `pm1h_trade_share≈0.81%`
- `blackout[-1h,+1h]` 更差：`mean_total_return≈-32.29%`
- `hybrid` 也没有改善：`mean_total_return≈-30.83%`
- 这说明当前样本里真正落在事件核心窗口的交易太少，overlay 不是在“更诚实地去掉坏交易”，而更像对极少数 bar 做轻微修饰；它不足以支撑 queue-facing shared overlay 的 admission。

### setup 级读法
- `breakout_short`：`blackout_pm1h≈-15.46%`，只比 baseline `≈-15.99%` 略少亏，但幅度太小，也没改变跨资产读法。
- `ema_psar_long`：overlay 变体整体更差，未显示 shared benefit。
- `fib_retest_long`：overlay 变体整体也没有改善。
- 结论：当前并不是“至少某一条 archetype 明显被修好”，因此不配 `keep_P1`，更不配 `promote_to_P2`。

## 本轮新增产物（deployable / reader-facing）
### code
- `scripts/build_rank88_macro_event_clean_replication.py`

### artifact
- `reports/artifacts/scout_rank88_macro_event_overlay_15m/overall_summary.csv`
- `reports/artifacts/scout_rank88_macro_event_overlay_15m/setup_summary.csv`
- `reports/artifacts/scout_rank88_macro_event_overlay_15m/asset_summary.csv`
- `reports/artifacts/scout_rank88_macro_event_overlay_15m/trade_samples.csv`
- `reports/artifacts/scout_rank88_macro_event_overlay_15m/meta.csv`

### reader-facing 网页
- `reports/site/factors/scout_rank88_macro_event_overlay_15m/report.html`
- `reports/site/reading/repo_scout/rank88_macro_event_blackout_clean_replication.html`

## 对 desk board 的写回
已更新 `docs/TODO.md`：
- 新增 `12:00 UTC` 补充，冻结 `Rank 88 clean replication -> park`；
- 当前 active Scout 顺序改回：`两条 breakout-centric digest backlog > Rank 82/80/81 evidence_pool > P3 continuity > tiny-live plumbing`；
- `Next 3` 改写为：
  1. `Run 1 = EMA due-check only`
  2. `Run 2 = 两条 breakout-centric digest backlog 中只认领 1 条 fresh source（默认先做 outside-close -> back-inside-close failure verdict）`
  3. `Run 3 = 若该 fresh source guard-passed 且 EMA 仍 waiting_not_due，则给它 1 次最小 clean replication；只有这层也 exhausted，才回退到 Rank 82/80/81 evidence_pool > tiny-live plumbing`

## 最小验证
- 已确认以下文件存在并可读：
  - `reports/artifacts/scout_rank88_macro_event_overlay_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank88_macro_event_overlay_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank88_macro_event_overlay_15m/meta.csv`
  - `reports/site/reading/repo_scout/rank88_macro_event_blackout_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板写回成功。

## 脏文件与提交
- 当前 repo 仍有大量与本轮无关的脏文件。
- 本轮未提交，避免混提。

## 下一轮建议
- 若 `EMA` 仍 `waiting_not_due`，不要再给 `Rank 88` 续命；
- 直接回到两条 breakout-centric digest backlog，只认领其中 1 条 fresh source；
- 优先默认：`outside-close -> back-inside-close failure verdict`，若 source intake 当轮就不合格，再切 `close-range compression asymmetry`。
