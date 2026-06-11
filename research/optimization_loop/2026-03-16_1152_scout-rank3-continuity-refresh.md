# 2026-03-16 11:52 UTC｜Scout Rank 3 continuity refresh：completed 15m bar 推进到 11:30 后继续一刀诚实续跑

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行：

- **Run 1 / Paper Seat**：`EMA` 仍是 `running paper / waiting_not_due`，本轮无新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：上一轮结论写明，若出现新的 completed `15m` bar，优先继续 `Rank 3 third_touch_plus_ema_macd` 的 honest continuity。
- 本轮先核对共享 Binance `15m` cache，确认可用 completed bar 已到 `11:30 UTC`；`11:45 UTC` 在本轮时点仍属 open bar，不纳入 continuity。

## 本轮只认领的事项
- **主点**：把共享 Binance `15m` cache 最小增量续写到 `11:30 UTC` completed bar，并执行一次 `Rank 3` continuity refresh。
- **紧邻子点**：把结论同步到 `docs/TODO.md` 顶部（`Scout Seat` + `Next 3 bot3 runs`）并更新 reader-facing 页面。

## 本轮做了什么
### 1）共享 15m cache 最小增量续写（只保留 completed bar）
目标缓存：`reports/artifacts/scout_tau_band_breakout_15m/cache/*.csv`

- `BTCUSDT__120d__15m.csv`：最新 completed bar 到 `2026-03-16 11:30 UTC`
- `ETHUSDT__120d__15m.csv`：最新 completed bar 到 `2026-03-16 11:30 UTC`
- `SOLUSDT__120d__15m.csv`：最新 completed bar 到 `2026-03-16 11:30 UTC`

执行中曾出现一次操作口径风险：初次抓取把 `11:45 UTC` open bar 一并带回。随后已立即修正为只保留 completed bar，并重跑验证链路。

### 2）重跑 Rank 3 continuity
执行：

- `python3 -u scripts/build_third_touch_ema_macd_first_verdict.py`（本机耗时约 3m30s）
- `python3 -u scripts/build_trendline_alpha_scout_report.py`
- `python3 -u scripts/build_plans_site.py`

刷新产物：

- `reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/asset_summary.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv`

同步页面：

- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`

### 3）同步指挥板
已在 `docs/TODO.md` 顶部补充 `11:52 UTC` 回执，覆盖：
- `Scout Seat` 最新补充
- `Next 3 bot3 runs` 最新补充

## 验证 / 证据
最小验证：

1. 核对 cache 尾部：三币种最新 completed bar 均为 `2026-03-16 11:30:00+0000` ✅
2. `build_third_touch_ema_macd_first_verdict.py` ✅
3. `build_trendline_alpha_scout_report.py` ✅
4. `build_plans_site.py` ✅

更新后的核心读法（`variant_aggregate.csv`）：

- 最佳变体仍是 `third_touch_plus_ema_macd`
- `mean_total_return ≈ +0.7797%`
- `mean_false_break_ratio = 0.00%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 0.33`

friction ladder（`third_touch_plus_ema_macd`）仍守住：

- `10bps`：约 `+0.70%`
- `15bps`：约 `+0.60%`
- `20bps`：约 `+0.50%`

## 本轮 hard verdict
一句话：

**Rank 3 在 `11:30 UTC` 新 completed bar 下继续通过 continuity，但席位含义没有升级，仍只是 keep-narrower structure-confirmation challenger，不是 replace-ready / tiny-live ready。**

证据支持：

- 新 completed bar 纳入后，`third_touch_plus_ema_macd` 的跨资产收益与 false-break 读法没有恶化；
- 但交易仍偏稀、正收益资产仍仅 `1/3`，不足以升格成可替换 Live Seat 的主候选。

## 风险 / 边界
- 本轮未重开 EMA 发散、未重跑 breakout heavy analysis、未新开主线 alpha。
- 本轮仅在存在 genuinely new completed `15m` bar 的条件下执行了一刀 Scout continuity。

## 下一步建议
1. 若下一轮前共享 cache 仍停在 `11:30 UTC`，默认不要再重跑同样本 Rank 3 continuity；按 desk 规则回退到 `Run 3 / tiny-live plumbing`。
2. 若出现新的 completed `15m` bar，再优先回到 `Run 2` 做 honest continuity。
3. `breakout` 继续按 `bench / recheck-only` 处理，除非出现 genuinely new blocker reduction。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`

## Commit hash
- HEAD：`5e1d263`
- 本轮未提交。

## 如果未提交，原因
当前 worktree 含大量与本轮无关的既有脏文件与未跟踪文件；本轮只做 selective 更新（cache + Rank 3 continuity + TODO/plans + 站点索引），避免混提。