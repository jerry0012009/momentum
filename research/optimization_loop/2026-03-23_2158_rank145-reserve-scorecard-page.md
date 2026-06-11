# 2026-03-23 21:58 UTC · Rank 145 reserve scorecard page

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；未见 `Paper / 正在自动运行` 的真实 interrupt，因此本轮路径 = `Scout`
- 认领动作：执行 `Next 3 bot3 runs / Run 1 = interrupt reserve / Rank 145 reserve`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把 `Rank 145` 已经完成、但还不够 reader-facing 的 reserve 结论做成一个站点可见页，避免后续 desk 继续把它当成“还需要再跑一轮实验”的对象。

### 紧邻子点
用已有 artifact 把“为什么是 reserve only”翻成人话，给后续 bot2 / bot3 / Jerry 一个无需回看 CSV 也能读懂的简短 scorecard。

## 本轮核实的可验证事实
1. `docs/TODO.md` 顶部 `Next 3 bot3 runs` 仍明确：`Run 1 = interrupt reserve / Rank 145 reserve`
2. 当前没有真实 interrupt 证据；顶板口径仍是：paper autonomous runners 健康时不抢占本轮
3. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`
   - `recommended_action = keep_P1`
   - `why_now` 明确写的是：desk 可用共享代理上，最便宜 A/B 已回答 routing 问题，不值得继续占默认 primary
4. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_summary.csv`
   - 在 `8/10/12% DD × 0.25/0.5 size × 95/98% recover` 全组合下，`time_in_reduced_mode_bars = 0`
   - `mdd_improve_pct = 0`，`return_damage_pct = 0`
5. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`
   - baseline shared proxy = `Rank32b 15m 6bps BTC/ETH/SOL equal-weight merged trade stream`
   - portfolio baseline `post_cost_return = 0.4788691205`
   - portfolio baseline `max_drawdown = 0.0185128793`
   - portfolio baseline `calmar = 125.8941004`

## 本轮实际交付
### 新增 reader-facing 页面
- `reports/site/reading/repo_scout/rank145_interrupt_reserve_scorecard.html`

页面内容把现有结论收口为：
- `keep_P1 / interrupt reserve fallback / reserve only`
- 当前不是“overlay 没意义”，而是“在 desk 当前共享代理上还没被真正触发过”
- 因此不应回到默认 Scout 主位，也不该重复同一类 frozen-threshold A/B

## 为什么这一步最有杠杆
这轮最浪费的做法，是再跑一次 Rank 145。因为问题已经不是“缺证据”，而是“现有结论还缺一个足够显眼、可被直接引用的 reader-facing 落点”。

把它做成页面的价值是：
- 后续 desk 在需要解释 `Rank 145` 为何只保留 reserve 时，有一个可直接引用的站点入口；
- bot2 / bot3 不用再翻 CSV 才能确认它为什么不回默认主位；
- 这是 0 新实验预算、但能减少后续重复劳动的一步。

## 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 3/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 3/3`
- `deployability = 3/3`
- `recommended_action = keep_Rank145_as_interrupt_reserve_fallback`
- `why_now = 当前最缺的不是更多 A/B，而是一个可直接交付、可直接引用的读者页，把 reserve 口径固定下来`
- `main_weakness = 这是 reader-facing 收口，不是新增方法证据；若未来真实资金曲线出现更深回撤，仍需新的触发样本来重估`

## 本轮结论
本轮完成了一个小但真的可交付的步子：
- 没有误把 routine 巡检当 interrupt；
- 没有重复烧 Rank 145 的 frozen-threshold 预算；
- 给 `Rank 145 = keep_P1 / interrupt reserve fallback / reserve only` 新增了一个站点可见、可交接、可复用的 scorecard 页面。
