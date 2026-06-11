# 2026-03-16 08:54 UTC · Scout Seat Rank 3 friction ladder 快检

## 为什么这轮做这个
- 先按 `TRADING DESK BOARD` 执行：`Paper Seat = EMA` 当前已是 `waiting_not_due`，因此本轮应走 `Run 2 = Scout Seat`，不能在 waiting-window 空转。
- `Rank 1 τ-band` 仍无 genuinely new local bar，`breakout` 仍是 `bench / recheck-only`，所以本轮选择对已 first-verdict 的 `Rank 3` 补一刀**不引入新 bar**的轻量 `friction recheck`，满足“1 个主点 + 1 个紧邻子点”。

## 本轮认领
- 主点：为 `scout_third_touch_ema_macd_15m` 增加可复用的 `friction ladder` 产物与页面外显。
- 紧邻子点：把该 friction 结论同步到 `trendline_alpha_scout` 总览卡片 + `TODO` 顶部 Desk Board 最新补充。

## 做了什么改动
1. 脚本改动（最小必要）：
   - `scripts/build_third_touch_ema_macd_first_verdict.py`
     - 增加可参数化交易成本（`cost_bps_per_side`）入口；
     - 新增 `FRICTION_COSTS=[6,10,15,20]` 与 `build_friction_ladder()`；
     - 新增 `derive_friction_verdict()`，把 friction 结论写入 `trial_meta.csv`；
     - 输出新 artifact：`reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv`；
     - 在 Rank 3 报告页新增“轻量 friction recheck”区块。
2. 总览同步：
   - `scripts/build_trendline_alpha_scout_report.py`
     - Rank 3 卡片新增 `friction recheck` 字段展示。
3. Desk Board 同步：
   - `docs/TODO.md`
     - 在 Scout Seat 最新补充追加 `2026-03-16 08:52 UTC` 条目，写清本轮 friction 快检结论与边界。

## 验证 / 证据
- 运行：
  - `python3 scripts/build_third_touch_ema_macd_first_verdict.py` ✅
  - `python3 scripts/build_trendline_alpha_scout_report.py` ✅
- 新产物：
  - `reports/artifacts/scout_third_touch_ema_macd_15m/friction_ladder.csv`
  - `reports/artifacts/scout_third_touch_ema_macd_15m/trial_meta.csv`（含 friction verdict + bullets）
- 关键数值（`third_touch_plus_ema_macd`）：
  - `6 / 10 / 15 / 20 bps per side` 下 `mean_total_return` 约：`+0.78% / +0.70% / +0.60% / +0.50%`
  - 对照：`raw_breakout @20bps ≈ -86.64%`；`third_touch_plus_ema @20bps ≈ -0.41%`

## 本轮硬结论（hard verdict）
- `Rank 3` 在当前样本下，`third_touch_plus_ema_macd` 的收益改善在更高摩擦下仍保持为正，当前可继续保留为 `keep-narrower structure-confirmation challenger`，并进入后续轻量 forward 复核队列。
- 但这仍只是 `120d / 15m / 3` 币种样本，不构成 `replace-ready / tiny-live ready`。

## 风险 / 边界
- 本轮严格未引入新 bar，不应把它表述成 forward 证据。
- 交易数极低（均值约 0.33 笔/资产）导致稳定性脆弱，后续仍需 continuity/route 偏差验证。

## 网站可见落点
- `reports/site/factors/scout_third_touch_ema_macd_15m/report.html`（新增 friction 区块）
- `reports/site/reading/trendline_alpha_scout/report.html`（Rank 3 卡片新增 friction 行）

## 提交说明
- 本轮未提交 commit。
- 原因：worktree 存在大量与本轮无关的历史脏文件，当前不适合安全 selective commit。
