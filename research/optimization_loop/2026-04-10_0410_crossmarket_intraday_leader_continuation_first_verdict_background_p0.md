# Rank pending intake: crossmarket intraday leader continuation — first verdict = background / P0

- Time: 2026-04-10 04:10 UTC
- Cycle target: `research/quant_digests/2026-04-10_0248_crossmarket-intraday-leader-continuation-alpha.md`
- Policy slot: Fresh intake

## What I executed
针对该 intake 的最小诚实验证，只做一件最便宜且最能改结论的检查：
- 在其主张的强 session 过滤（`lead_bps>=50` 且 `spread_vs_runner>=40`）下，按 leader symbol 分层，检查 `12/24/30 bar` 的收益是否由单一 `SOL` 集中驱动。

数据源：
- `reports/artifacts/literature/crossmarket_intraday_tsmom_leader_probe_2026-04-10.csv`

## Minimal honesty check result
强 session cohort 共 116 笔：
- `12bar` overall gross: `+15.23bps`
- 但分层后：
  - `SOL leader`：83 笔，`+25.47bps`
  - `ETH leader`：32 笔，`-8.64bps`
  - `BTC leader`：1 笔，`-71.51bps`
- 去掉 `SOL leader` 后，`12bar` 仅剩 33 笔，mean 变成 `-10.55bps`（方向翻负）

`24bar` 去掉 SOL 仍为负（`-5.47bps`）；`30bar` 虽转正但已不符合该 alpha 主叙事的短持有 continuation 核心窗口。

## Verdict
该对象当前可见 edge 主要来自 `SOL-heavy` 单一集中暴露，尚不足以支持“leader-defined continuation 可独立迁移”的 desk 级结论；在本轮 fresh-intake 首判应收口为 `background / P0`，不进入 `keep_P1`。

## State updates required
- cycle_plan item #3: `status -> done`
- cycle_plan item #3 `result`: 写明“SOL concentration 为当前单一 decisive blocker，first verdict background/P0”
- Fresh intake slot latest_result 切换到本对象的 P0 首判
- Background pool latest_parked 刷新到本对象
