# 2026-03-16 11:35 UTC｜Scout Rank 3 continuity refresh：completed 15m bar 推进到 11:00 后做一刀诚实续跑

## 为什么这次选这个
按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- **Run 1 / Paper Seat**：`EMA` 仍是 `running paper / waiting_not_due`，当前没有新的 `due-now / overdue` lane。
- **Run 2 / Scout Seat**：上一轮写明若出现新的 completed `15m` bar，优先继续 `Rank 3 third_touch_plus_ema_macd` 的 honest continuity。
- 本轮先核对共享 Binance `15m` cache，确认在当前时间点只能新增 `11:00 UTC` completed bar（`11:15 UTC` 仍是 open bar，不纳入）。因此本轮合规继续 `Run 2`，不回退到 `Run 3`。

## 本轮只认领的事项
- **主点**：把共享 Binance `15m` cache 做最小增量续写到 `11:00 UTC` completed bar，并执行 `Rank 3` 一刀 honest continuity refresh。
- **紧邻子点**：把本轮结论同步到 `docs/TODO.md` 顶部 `Scout Seat / Next 3 bot3 runs`，并刷新 reader-facing 页面。

## 本轮做了什么
### 1）最小增量续写共享 15m cache（不混入 open bar）
目标缓存：`reports/artifacts/scout_tau_band_breakout_15m/cache/*.csv`

- `BTCUSDT__120d__15m.csv`：`10:45 -> 11:00 UTC`（仅新增 1 根 completed bar）
- `ETHUSDT__120d__15m.csv`：`10:45 -> 11:00 UTC`
- `SOLUSDT__120d__15m.csv`：`10:45 -> 11:00 UTC`

执行中出现一个格式摩擦：首次追加时把新时间写成了 `T` 分隔格式，导致 `build_third_touch_ema_macd_first_verdict.py` 在 `pd.to_datetime` 上报错。随后立即把三份 cache 的 `timestamp` 统一回脚本可读的同一格式（`%Y-%m-%d %H:%M:%S%z`），并重跑通过。

### 2）重跑 Rank 3 continuity
执行：

- `python3 scripts/build_third_touch_ema_macd_first_verdict.py`
- `python3 scripts/build_trendline_alpha_scout_report.py`

刷新产物：

- `reports/artifacts/scout_third_touch_ema_macd_15m/variant_aggregate.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/asset_summary.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`
- `reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv`

同步页面：

- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

### 3）同步指挥板并更新计划页
更新：

- `docs/TODO.md`（新增 `11:26 UTC` 的 `Scout Seat` 与 `Next 3 bot3 runs` 回执）
- `python3 scripts/build_plans_site.py`

## 验证 / 证据
最小验证：

1. 核对共享 cache 末端：三个币种均为 `2026-03-16 11:00:00+0000` ✅
2. `python3 scripts/build_third_touch_ema_macd_first_verdict.py` ✅
3. `python3 scripts/build_trendline_alpha_scout_report.py` ✅
4. `python3 scripts/build_plans_site.py` ✅

更新后的核心读法（来自 `variant_aggregate.csv`）：

- 最佳变体仍是 `third_touch_plus_ema_macd`
- `mean_total_return ≈ +0.7797%`
- `mean_false_break_ratio = 0.00%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 0.33`

成本梯度读法仍守住：

- `10bps`：约 `+0.70%`
- `15bps`：约 `+0.60%`
- `20bps`：约 `+0.50%`

## 本轮 hard verdict
一句话：

**Rank 3 在 `11:00 UTC` 新 completed bar 下继续通过 continuity，但席位含义没有升级，仍只是 keep-narrower structure-confirmation challenger，不是 replace-ready / tiny-live ready。**

证据支持：

- 相比 `raw_breakout`，Rank 3 仍显著更“没那么差”，且本轮新增 completed bar 后没有反转；
- 但交易数仍稀，正收益资产仍仅 `1/3`，不足以升格为可替换 Live Seat 的主候选。

## 风险 / 边界
- 本轮不是新 alpha 主线，也不是 breakout recheck。
- 未重开 EMA 发散研究；未做 breakout heavy rerun。
- 仅在有 genuinely new completed `15m` bar 的条件下做了一刀 continuity。

## 下一步建议
1. 若下一轮前共享 cache 仍停在 `11:00 UTC` completed bar，默认不要重跑同样本 Rank 3 continuity；按 desk 规则回退 `Run 3 / tiny-live plumbing`。
2. 若出现新的 completed `15m` bar，再优先回到 `Run 2` 做 honest continuity。
3. breakout 继续按 `bench / recheck-only` 处理，除非出现 genuinely new blocker reduction。

## 网页可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `reports/site/plans/momentum_todo.html`

## Commit hash
- HEAD：`5e1d263`
- 本轮未提交。

## 如果未提交，原因
当前 worktree 含大量与本轮无关的既有脏文件与未跟踪文件；本轮坚持 selective 更新（cache + scout continuity + TODO/plans + index），避免混提。