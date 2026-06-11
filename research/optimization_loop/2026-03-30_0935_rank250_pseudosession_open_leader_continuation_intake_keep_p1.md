# Rank 250 / pseudosession open leader continuation fresh intake 首判

- 时间：2026-03-30 09:35 UTC
- 对象：`Rank 250 / pseudosession open leader continuation`
- 本轮动作：作为当前 `cycle_plan` 最前 pending 小点的 fresh intake 首判，只回答这条最新 alpha 是否形成独立前排对象；主语锁定为 `pseudo-session open shock → leader continuation / follower participation`，不回退成泛 intraday open momentum / generic event-clock 家族。
- 来源：`research/quant_digests/2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md`

## 结论（result）

**Rank 250：`pseudosession open leader continuation` 形成了独立前排对象边界，首判给 `keep_P1`。它不是旧 `clock/open continuation` 或 `cross-market shared gate` 的泛改写，而是把 alpha 本体钉死在 `00/08/16 UTC` pseudo-session 开头 `30m` 里 `dominant leader 自身继续领跑`；`spread-to-runner` 只是一道 admission gate。虽然无 gate 的 broad 同向版本成本后转负，但 `leader>=50bps + spread_to_runner>=40bps` 的稀疏 pocket 在 Binance perp `15m` quick check 里仍留下 `12/24/30 bars` 约 `+2.34/+8.96/+16.16 bps/trade` 的 after-cost 空间，因此值得进入唯一 survivor follow-up。**

## 为什么这不是旧对象的泛重述

1. **交易主语变了。**
   这里交易的不是“大家同向所以跟一腿”，而是 **pseudo-session 前 30m 已明显甩开 runner-up 的最强 leader 自己**。
2. **cross-market 信息被降级为上下文/准入，不再是 alpha 本体。**
   `至少 2/3 同向` 只能说明 session 有共振；真正决定是否出手的是 `leader` 与 `runner-up` 的拉开幅度。
3. **持有窗口、执行对象、成本口径都已经具体。**
   `BTC/ETH/SOL` perpetual，`15m`，第 2 根 bar 收盘确认后下一根入场，持有 `12/24/30 bars` 或 session close，round-trip 成本先按 `8 bps`。这已经是可复现的最小完整骨架，不是抽象叙述。

## 首判证据摘录

- broad 同向版本：持有到 session close，`n=1091`，毛收益约 `-6.64 bps/trade`，按 `8 bps` 后约 `-14.64 bps`。
- 只加 `leader>=50bps` 仍不够：`n=394`，毛收益约 `+3.33 bps/trade`，成本后约 `-4.67 bps`。
- 关键 pocket：`leader>=50bps` 且 `leader-runner_up>=40bps` 时，`n=112`，毛收益在 `12/24/30 bars` 约 `+10.34/+16.96/+24.16 bps/trade`，成本后约 `+2.34/+8.96/+16.16 bps/trade`。

## 这一步之后的合法未决点

- 它还不是 `promote_P2`，因为当前 pocket 明显是 **稀疏条件 pocket**，而且 quick check 只覆盖 `BTC/ETH/SOL` 三资产代理。
- 合法的唯一 survivor follow-up 应继续只回答一个收口问题：
  - 这条 `dominant leader continuation` 在固定 pseudo-session 规则下，是否在 `spread_to_runner` 阈值与 `12/24/30 bars` 持有窗的 rolling / OOS 口径里仍保有稳定的 after-cost 边；
  - 若稳定，则可 `promote_P2`；若只剩零散 pocket 或 rolling 后塌掉，则应诚实收口回 `background/P0`。

## 本轮 runtime 写回

- 分配新正式 `Rank 250`
- `Fresh intake slot` 改写为 `Rank 250 / pseudosession open leader continuation`
- `Surviving candidate slot` 改写为 `Rank 250 / pseudosession open leader continuation`
- `followup_budget_remaining = 1`
- `cycle_plan` 第 2 项写回 `done`
