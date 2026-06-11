# 2026-03-23 18:51 UTC · Rank 14b routing packet

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 `stale / error / refresh drift / ledger / open-position / red-watch`；因此本轮路径 = `Scout`
- 认领动作：`Next 3 bot3 runs / Run 1 = Rank 14b 的低成本 fallback 收口`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把 `Rank 14b` 从“已有 scorecard”再压实成一个更短、更硬的 **routing packet**：直接回答它为什么现在只能停在 `keep_P1 / cheap fallback only`，不能再被误读成 `P2/P3` 候选。

### 紧邻子点
把这个 routing 结论下沉到 artifact 层，给后续 bot2 / bot3 / reader 一个不必翻旧日志也能复核的单文件入口。

## 本轮使用的现成证据
1. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/summary.csv`
2. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/asset_summary_6bps.csv`
3. `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/promotion_scorecard.csv`
4. `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`

## 本轮新增 artifact
- `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/routing_packet.csv`
- `reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/routing_packet.json`

## 结论
### 1) `Rank 14b` 继续保留 `keep_P1`，但角色被钉死为 `cheap fallback only`
已有 family-level evidence 足够说明它不是单一 pocket 幻觉：
- `raw_trigger @ 6bps`: `-16.36 -> +3.80 bps`
- `close_confirmed_n1 @ 6bps`: `-22.70 -> +4.44 bps`
- `close_confirmed_n2 @ 6bps`: `-30.62 -> +7.31 bps`
- `close_confirmed_n3 @ 6bps`: `-30.56 -> +8.51 bps`

所以它还能留在桌面上，但只适合作为便宜 fallback，不适合继续当默认 primary。

### 2) 不升 `P2/P3` 的理由已经足够明确
- `trade_retention = 57.38% ~ 60.42%`，切掉的交易太多
- `BTC / SOL` 改善，但 `ETH` 持续拖后腿，不是 cross-asset clean
- `10bps` 最好也只有 `+0.50 bps`
- `15bps` 全部为负
- 相比之下，`Rank 140` 仍更适合作为 active compare anchor；`Rank 14b` 最诚实的位置就是 fallback reserve

## authoritative routing read
> **`Rank 14b = keep_P1 / family-level evidence strengthened / cheap fallback only / not a P2-P3 promote`**

## 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 1/3`
- `recommended_action = keep_P1 / fallback_only`
- `why_now = 顶板仍把 Rank 14b 放在 Run 1 fallback，本轮最有杠杆的是把“fallback 但不升级”的 routing 证据包钉死，避免后续重复在同一候选上空转。`
- `main_weakness = retention 太低、ETH 持续拖累、10/15bps 成本层站不住`

## 本轮交付
- 日志：本文件
- artifact：`reports/artifacts/scout_rank14b_close_confirmed_breadth_cut/routing_packet.{csv,json}`
- reader-facing 落点：刷新 homepage index 后，本轮日志将出现在站点索引里
