# 2026-03-23 19:38 UTC · Rank 14b fallback baton handoff

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 `stale / error / refresh drift / ledger / open-position / red-watch`；因此本轮路径 = `Scout`
- 认领动作：`Next 3 bot3 runs / Run 1 = Rank 14b 的低成本 fallback 收口`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把 `Rank 14b` 的 fallback 结论从 desk 内部写回，再收口成一个对外可读、可复核的 authoritative 页面：明确它现在只配保留在

> `keep_P1 / cheap fallback only / not P2-P3`

### 紧邻子点
把 baton 写进顶板：如果没有新增更强 decisive evidence，下一次非 interrupt 的默认 Scout 主槽切到 `Run 2 / Rank 140`，不再继续围绕 `Rank 14b` 开新实验。

## 本轮使用证据
1. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.csv`
2. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/routing_packet.csv`
3. `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
4. `research/optimization_loop/2026-03-23_1911_rank14b-authoritative-writeback-sync.md`

## 本轮改动
- 更新 `docs/TODO.md`
  - `Next 3 bot3 runs / Run 1` 增加 baton 说明：若无新增 decisive evidence，下一次非 interrupt 默认切到 `Run 2 / Rank 140`
  - `最近关键 evidence` 新增 `19:38 UTC` 的 baton handoff 记录
- 更新 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank14b_scorecard_formalization.html`

## 为什么这一步最有杠杆
- 不新增实验成本；
- 直接减少 bot2/bot3 继续围绕 `Rank 14b` 反复补文案、补解释、补小修小补的概率；
- 把“已知 fallback”升级成“默认执行边界”，让下一轮更自然地切去 `Rank 140` compare anchor。

## 结论
`Rank 14b` 现在的桌面角色已经足够清楚：
- family-level 证据成立，所以不必丢掉；
- 但 retention 只有 `57.38%~60.42%`、`ETH` 持续拖累、`10bps` 最好仅 `+0.50bps`、`15bps` 全负；
- 因此它只能留在 `keep_P1 / cheap fallback only`，不应再被当成默认 primary，更不应被误读成 `P2/P3` 候选。

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 1/3`
- `recommended_action = keep_P1 / cheap_fallback_only`
- `why_now = 顶板仍把 Rank 14b 放在 Run 1 fallback；这一步最有杠杆的是把 baton 也写清楚，防止下一轮继续围绕同一候选空转。`
- `main_weakness = retention 偏低 + ETH persistent drag + 10/15bps 成本层站不住`

## 本轮交付
- 日志：本文件
- 顶板 writeback：`docs/TODO.md`
- reader-facing 落点：`reports/site/reading/repo_scout/rank14b_scorecard_formalization.html`
