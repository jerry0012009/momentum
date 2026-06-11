# 2026-03-23 21:45 UTC · Rank 145 interrupt-reserve sync

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；本轮未见 `Paper / 正在自动运行` 的真实 interrupt，因此本轮路径 = `Scout`
- 认领动作：执行 `Next 3 bot3 runs / Run 1 = interrupt reserve / Rank 145 reserve`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
复核 `Rank 145` 当前 routing 口径，确认它是否仍被 desk 误写成默认 Scout 主位。

### 紧邻子点
把顶板里与 `Run 1 = interrupt reserve / Rank 145 reserve` 冲突的字样收口成同一 authoritative 表述，避免后续 bot2 / bot3 再按旧话术误认领。

## 本轮核实的可验证事实
1. `docs/TODO.md` 顶部 `Next 3 bot3 runs` 已明确：`Run 1 = interrupt reserve / Rank 145 reserve`
2. `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`
   - `recommended_action = keep_P1`
   - `why_now` 明确写的是：本地最便宜 A/B 已回答 routing 问题，当前不值得继续占默认 primary
3. `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
   - `Rank 145` 行的 authoritative routing read = `budget used / no promote / reserve only`
4. `reports/artifacts/ema_psar_raw_alpha/ema_paper_autopilot_status.json`
   - `updated_at_utc = 2026-03-23T21:45:01Z`
   - `mode = waiting_not_due`
   - 未见 paper runner interrupt 证据

## 本轮实际交付
已同步 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 两处表述：

1. `Active Scout 排序 / Rank 145` 行
   - 从：`无 interrupt 时的默认 Scout 主位`
   - 改为：`interrupt reserve fallback / ... / 不回默认 Scout 主位`

2. `Next 3 bot3 runs / Run 1` 目标说明
   - 去掉“给默认 Scout 主位”的旧说法
   - 改为明确的 `reserve fallback` 口径

## 为什么这一步最有杠杆
这轮不该重跑 Rank 145。
问题不在证据不足，而在顶板内部还有一句旧表述会把它重新写回默认主位。把这句收口掉，价值在于：
- 后续 bot3 不会再把 `Rank 145` 误当成重新争取默认 primary 的对象；
- `interrupt reserve -> Rank 145 reserve fallback -> Rank 111 anchor -> Rank 140 on-demand compare` 的路由终于前后一致；
- 这是最小、可验证、会直接改变下一轮认领动作的一步。

## 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 3/3`
- `cross_asset_stability = 2/3`
- `cost_trade_stability = 3/3`
- `deployability = 3/3`
- `recommended_action = keep_Rank145_as_interrupt_reserve_fallback`
- `why_now = Rank 145 的实验结论早已固定，当前最有杠杆的是消掉顶板里残留的 routing 自相矛盾`
- `main_weakness = 这是 authoritative writeback，不是新增研究证据`

## 本轮结论
本轮完成的是一个小但真正会影响自动执行的收口动作：
- `Rank 145` 继续保留 `keep_P1`；
- 但角色固定为 `interrupt reserve fallback / reserve only`；
- 顶板不再同时出现“reserve”与“默认 Scout 主位”这两种互相打架的口径。
