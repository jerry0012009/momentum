# 2026-03-23 18:36 UTC · Rank 14b fallback scorecard freeze

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 `stale / error / refresh drift / ledger / open-position / red-watch`；因此本轮路径 = `Scout`
- 认领动作：`Next 3 bot3 runs / Run 1 = Rank 14b 的低成本 fallback 收口`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
不给 `Rank 14b` 再开新 cut，而是把它已经完成的 family-level evidence 固化成**标准 promotion scorecard**，把 fallback 的边界说死：
- 可以继续保留为 `keep_P1`
- 不能被误读成新的 default primary
- 也不构成 `P2/P3` 升级理由

### 紧邻子点
把 scorecard 落到 artifact 层，供后续 bot2/bot3/读者直接复核，不再只散落在旧日志与页面文案里。

## 本轮核实并固化的证据
来源：
1. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/summary.csv`
2. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/asset_summary_6bps.csv`
3. `reports/site/reading/repo_scout/rank14b_family_level_breadth_cut.html`

本轮新增 artifact：
- `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.csv`
- `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.json`

## 核心结论
### 1) fallback 仍然成立，但只成立在 `keep_P1` 层
`low breadth veto` 在 `EMA/PSAR long` family 的相邻变体里都保持了同向改善：
- `raw_trigger @ 6bps`: `-16.36 -> +3.80 bps`（`delta = +20.16 bps`）
- `close_confirmed_n1 @ 6bps`: `-22.70 -> +4.44 bps`（`delta = +27.14 bps`）
- `close_confirmed_n2 @ 6bps`: `-30.62 -> +7.31 bps`（`delta = +37.94 bps`）
- `close_confirmed_n3 @ 6bps`: `-30.56 -> +8.51 bps`（`delta = +39.07 bps`）

因此它不是单一 pocket 的幻觉，保留 `keep_P1` 合理。

### 2) 但它依然不具备更硬的 routing 升级条件
- `trade_retention` 仍只有 `57.38% ~ 60.42%`
- `ETH` 在所有相邻变体里持续为负，是明显 structural drag
- `10bps` 最好也只是 `close_confirmed_n3 = +0.50 bps`
- `15bps` 全部为负

因此更诚实的 routing 不是“继续往上推”，而是：
> **`Rank 14b = keep_P1 / family-level evidence strengthened / default fallback only`**

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板当前把 Rank 14b 放在 Run 1 fallback；本轮最有杠杆的小步就是把它固化成标准 scorecard，防止后续 bot3 再把 fallback 误读成值得续磨的 primary。`
- `main_weakness = ETH persistent drag + retention only 57~60% + 10/15bps 站不稳`

## 为什么这是本轮最有杠杆的小步
- 不新增实验成本
- 直接把已有结论沉淀成可复核 artifact
- 让后续 desk 在 `Rank 14b` 上更容易保持同一口径：保留、但不再抬级

## 本轮交付
- 日志：本文件
- artifact：`reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.{csv,json}`
- reader-facing 落点：刷新 homepage index 后可见本轮日志入口
