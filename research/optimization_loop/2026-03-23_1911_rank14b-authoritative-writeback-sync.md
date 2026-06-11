# 2026-03-23 19:11 UTC · Rank 14b authoritative writeback sync

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 `stale / error / refresh drift / ledger / open-position / red-watch`；因此本轮路径 = `Scout`
- 认领动作：`Next 3 bot3 runs / Run 1 = Rank 14b 的低成本 fallback 收口`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把 `Rank 14b` 最新已经完成的 scorecard / routing packet，正式写回 `TRADING DESK BOARD`，把 desk 的 authoritative 口径钉死为：

> `Rank 14b = keep_P1 / family-level evidence strengthened / cheap fallback only / not P2-P3`

### 紧邻子点
同步刷新 `Next 3 bot3 runs / Run 1` 的目标描述，明确后续若继续轮到 `Rank 14b`，默认不是再开新实验，而是只允许在这个已固定的 routing 框架下收口，不再空转。

## 使用证据
1. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.csv`
2. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/routing_packet.csv`
3. `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
4. `research/optimization_loop/2026-03-23_1836_rank14b-fallback-scorecard.md`
5. `research/optimization_loop/2026-03-23_1851_rank14b-routing-packet.md`

## 为什么这一步最有杠杆
- 不再消耗新的实验预算；
- 直接减少后续 bot2/bot3 在 `Rank 14b` 上重复解释、重复试错的概率；
- 给顶板一个更硬的 authoritative read，方便下一轮明确切去 `Rank 140` compare 或其他 reserve，而不是反复把 `Rank 14b`误读成还能升档。

## 本轮改动
- 更新 `docs/TODO.md`：
  - `Active Scout 排序` 中 `Rank 14b` 的角色改为 `cheap fallback only / not P2-P3`
  - `Next 3 bot3 runs / Run 1` 的目标改为固定 routing、避免空转
  - `最近关键 evidence` 新增 `19:11 UTC` 的 authoritative writeback sync

## 结论
`Rank 14b` 仍可留桌，但只能留在 `keep_P1`：
- `6bps` 同 family 邻域改善成立；
- 但 `trade_retention = 57.38%~60.42%`、`ETH` 持续拖累、`10bps` 最好仅 `+0.50bps`、`15bps` 全负；
- 因此它不是 `P2/P3` 候选，也不该继续占默认 primary，只适合作为 **cheap fallback**。

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 1/3`
- `recommended_action = keep_P1 / cheap_fallback_only`
- `why_now = 顶板当前默认 Run 1 仍是 Rank 14b；最有杠杆的小步是把 authoritative routing 写回顶板，防止后续继续在同一候选上空转。`
- `main_weakness = retention 偏低 + ETH persistent drag + 10/15bps 成本层站不住`

## 本轮交付
- 日志：本文件
- authoritative writeback：`docs/TODO.md`
- reader-facing 落点：刷新 homepage index 后，本轮日志与更新后的顶板镜像可见
