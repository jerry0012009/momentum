# bot3 optimization loop — low-volume upmove fade first verdict -> background/P0

- 时间：2026-04-25 09:30 UTC
- 对象：`research/quant_digests/2026-04-24_2250_lowvolume-upmove-fade-alpha.md`
- 执行槽位：`cycle_plan` 第 3 项（fresh intake）
- 本轮动作：对 `低成交量上冲 × 次段回吐` 做 first verdict；只围绕唯一最小 decisive blocker 判断它在 short-cycle crypto perp 上是否留下可独立交易的 after-cost `15m` pocket

## 结论
`低成交量上冲 × 次段回吐` 本轮诚实收口为 `background/P0`：当前 portability 证据只显示 `15m` 上存在极薄、且高度单币/小样本化的毛边，统一 `8bps` 成本后 pooled `15m hold1/hold3` 分别为 `-4.06 / -4.39 bps`，最好的 `DOGE 15m hold1` 也仅 `+0.90 bps/笔 (26 笔)`、`BTC 15m hold3` 虽有 `+9.40 bps/笔` 但样本仅 `13` 笔，不能证明存在可独立交易的 after-cost XS fade pocket。

## 本轮证据
来源：`reports/artifacts/quant_digests/low_volume_fade_probe_summary_2026-04-24.csv`

关键数：
- `POOLED 15m hold1`: `104` 笔，`avg_net_bps = -4.0617`
- `POOLED 15m hold3`: `104` 笔，`avg_net_bps = -4.3916`
- `POOLED 5m hold1/3`: `-7.7634 / -7.5237 bps`，说明 child 层也没有成本后可留 pocket
- `DOGE 15m hold1`: `26` 笔，`avg_net_bps = +0.8955`
- `BTC 15m hold3`: `13` 笔，`avg_net_bps = +9.3962`
- 其余 `ETH/SOL/ADA/XRP` 的 `15m` 口径多数仍为负，说明这不是跨币一致成立的可迁移 edge

## 为什么直接判 P0
本轮 success criterion 要求：只有当至少一个统一成本口径下的 `1h parent -> 15m/5m child` XS reversal pocket 明显成立、且不只是“少亏一点”的 liquidity filter 语义，才保留到 `P1`。

但当前 digest 实际拿到的证据仍停留在更粗的 `15m/5m` next-open 反手空 probe：
1. pooled `15m` 仍是稳定负净值；
2. 正 pocket 只出现在 `DOGE` 与极少数 `BTC hold3` 事件上，明显受单币与样本稀疏主导；
3. `5m` 没有救回成本，无法支持“15m parent -> 5m child` 能把 alpha 变成可交易口袋”的乐观解释；
4. 因此目前更像“假突破语义存在，但无法穿透 taker friction”的研究线索，而不是能保留到前排的 raw alpha。

## 对 runtime 的影响
- 不分配新 Rank
- 不进入 `Surviving candidate`
- 不升级 `P1/P2/P3`
- 作为 fresh intake first verdict 直接收口到 `background/P0`

## 一句话写回 state
`低成交量上冲 × 次段回吐` 已诚实收口 `background/P0`：统一 `8bps` 成本下 pooled `15m hold1/hold3` 仍为 `-4.06 / -4.39 bps`，仅剩 `DOGE hold1` 与 `BTC hold3` 的单币稀疏 pocket，不足以证明可独立交易的 after-cost XS fade alpha。
