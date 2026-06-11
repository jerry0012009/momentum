# 2026-03-23 22:25 UTC · Rank 145 revisit trigger matrix

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 interrupt，因此本轮路径 = `Scout`
- 认领动作：执行 `Next 3 bot3 runs / Run 1 = interrupt reserve / Rank 145 reserve`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把 `Rank 145` 从“已经是 reserve”进一步收口为一份 **何时才允许重开** 的触发矩阵，避免后续 bot2 / bot3 在 healthy 状态下继续误认领。

### 紧邻子点
把机读 artifact 和 reader-facing 页面都补齐，并从已有 reserve scorecard 页加链接过去，形成一个可直接引用的交付入口。

## 本轮核实的可验证事实
1. `docs/TODO.md` 顶板仍明确：`Run 1 = interrupt reserve / Rank 145 reserve`
2. `reports/artifacts/ema_psar_raw_alpha/ema_paper_autopilot_status.json`
   - `updated_at_utc = 2026-03-23T22:15:01Z`
   - `mode = waiting_not_due`
   - 当前不是 interrupt
3. `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_status.csv`
   - `updated_at_utc = 2026-03-23T22:15:01Z`
   - `open_position = none`
   - 当前不是 interrupt
4. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/frozen_threshold_ab_portfolio_summary.json`
   - shared proxy baseline `max_drawdown = 0.0185128793`（约 `1.85%`）
   - 明显低于 `Rank 145` 本地最小 arm 阈值 `8%`
   - 说明 overlay 仍没有在 desk 相关样本里真正 armed

## 本轮实际交付
### 新增 artifacts
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/interrupt_revisit_trigger_matrix_20260323.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/interrupt_revisit_trigger_matrix_20260323.csv`

### 新增 reader-facing 页面
- `reports/site/reading/repo_scout/rank145_interrupt_revisit_trigger_matrix.html`

### 现有页面联动更新
- `reports/site/reading/repo_scout/rank145_interrupt_reserve_scorecard.html`
  - 新增指向 trigger matrix 的链接

## 这一步改变了什么
之前 desk 已经知道：`Rank 145 = reserve only`。
但还缺一个更硬的、可直接执行的口径：**到底什么情况才允许它重新回到台前**。

这轮把这个边界写死为三类触发：
1. `real paper interrupt`
2. `shared proxy drawdown reaches arm zone (>= 8%)`
3. `new scope upgrade`

同时也明确了三类 **不算触发** 的情况：
- routine 健康刷新；
- 在同一个 shared proxy 上重复 frozen-threshold A/B；
- 仅因它是 `Run 1 reserve fallback` 就默认认领。

## 为什么这一步最有杠杆
这轮最有价值的不是再跑一次 Rank 145，而是阻止后续继续浪费轮次。

把“何时重开 / 何时不重开”写成触发矩阵之后：
- bot2 / bot3 以后更不容易把 healthy 状态误当成 interrupt；
- `Rank 145` 的 reserve 角色从“结论”升级成“带触发条件的操作规则”；
- 这是一个真实可验证、能直接影响后续自动认领的 reader-facing 小步。

## 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 2/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 3/3`
- `deployability = 3/3`
- `recommended_action = keep_P1 / interrupt reserve fallback / reserve only`
- `why_now = 当前最缺的不是新增实验，而是把 Rank 145 的“重开条件”写死，减少后续自动循环重复浪费`
- `main_weakness = 这仍然不是新的触发样本；若未来真出现 >=8% drawdown，仍需基于新样本重估`

## 本轮结论
本轮完成了一个最小但真的会改变后续路由的动作：
- `Rank 145` 继续保留 `keep_P1 / reserve only`；
- 新增了 **什么时候才允许重开** 的 trigger matrix；
- 这让 `interrupt reserve` 从模糊口号，变成了可执行、可交接、可引用的操作规则。
