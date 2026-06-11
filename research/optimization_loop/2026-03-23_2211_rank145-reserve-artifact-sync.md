# 2026-03-23 22:11 UTC · Rank 145 reserve artifact sync

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 interrupt，因此本轮路径 = `Scout`
- 认领动作：执行 `Next 3 bot3 runs / Run 1 = interrupt reserve / Rank 145 reserve`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
为 `Rank 145` 已完成的 reserve 结论补一个机读 artifact，避免它只停留在 reader-facing 页面，后续 bot2 / bot3 还得重新翻旧 CSV/JSON 才能引用。

### 紧邻子点
把关键 baseline 与 frozen-threshold A/B 结果收口成单行 CSV，便于后续 desk、日志或脚本直接引用同一份 authoritative 摘要。

## 本轮核实的可验证事实
1. `docs/TODO.md` 顶部 `Next 3 bot3 runs` 仍是：`interrupt / Rank 145 reserve / Rank 111 anchor / Rank 140 on-demand compare`
2. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`
   - `recommended_action = keep_P1`
   - `why_now` 已明确：最便宜本地 A/B 已回答 routing 问题，不值得继续占默认 primary
3. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`
   - baseline shared proxy = `Rank32b 15m 6bps BTC/ETH/SOL equal-weight merged trade stream`
   - baseline `post_cost_return = 0.4788691205`
   - baseline `max_drawdown = 0.0185128793`
   - baseline `calmar = 125.8941004`
4. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.csv`
   - `8/10/12%` DD × `0.25/0.5` 缩仓 × `95/98%` recover 全组合都未触发
   - `time_in_reduced_mode_bars = 0`
   - `mdd_improve_pct = 0`
   - `return_damage_pct = 0`

## 本轮实际交付
### 新增 artifacts
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/interrupt_reserve_scorecard_20260323.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/interrupt_reserve_scorecard_20260323.csv`

### 已有 reader-facing 页面继续作为落点
- `reports/site/reading/repo_scout/rank145_interrupt_reserve_scorecard.html`

## 为什么这一步最有杠杆
上一轮已经把 `Rank 145 = keep_P1 / interrupt reserve fallback / reserve only` 做成读者页，但 desk 自动化真正会复用的往往不是 HTML，而是一个短小、稳定、可机读的摘要产物。

这一步的价值在于：
- 后续 bot2 / bot3 / 顶板更新可以直接引用统一 JSON/CSV，不必再次人工翻旧表；
- `Rank 145` 的 reserve 口径从“页面可读”升级成“页面可读 + artifact 可复用”；
- 仍然没有重复烧 frozen-threshold 实验预算，符合当前 `reserve only` 的 desk 纪律。

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 2/3`
- `deployability = 2/3`
- `recommended_action = keep_P1 / interrupt reserve fallback / reserve only`
- `why_now = 当前缺的不是更多 A/B，而是一个让 desk 能直接复用、不会再误认领 Rank 145 的 authoritative 摘要 artifact`
- `main_weakness = 这是 artifact 收口，不是新增方法证据；若未来出现更深真实回撤，仍需新的触发样本重估`

## 本轮结论
本轮完成了一个最小但可验证的小步：
- 没有误把 routine 健康状态当 interrupt；
- 没有重复重跑 Rank 145；
- 把 `Rank 145` 的 reserve 口径补成了可机读、可交接、可被后续自动化直接引用的 artifact。
