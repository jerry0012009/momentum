# Rank pending / BTC intraday session momentum fresh intake -> background/P0

- 时间：2026-04-23 20:20 UTC
- 对象：`research/quant_digests/2026-04-23_0901_btc-intraday-session-momentum-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮最小 decisive blocker
用 Binance USDⓈ-M `BTCUSDT` perp `5m` 公共 K 线，对 digest 里最贴近论文叙事的伪 session continuation 壳做最便宜 honesty probe：

- 样本：`2025-12` ~ `2026-04-23`，按 `1h` parent 切 `5m` bars
- 口径 sweep：
  - 前段 `15m / 20m / 30m`
  - 后段对称持有到同一 `1h` 尾端
  - `|first-leg return|` 阈值 `0 / 5 / 10 / 15 bps`
  - admission bucket：`all / top30% first-leg volume / top30% realized-vol / top30% both`
- 交易口径：前段结束后按同方向进入，持有到本小时尾端；先看 gross continuation，再问它是否可能穿过常见 perp round-trip 成本

## 结果
### 1) 最直接的论文相邻口径（前 15m -> 后 15m）没有 pocket
`2026-01` ~ `2026-04-23` 的 1h/5m 快检里：

- 全样本：`+0.23 gross bps/trade`，按 `8 bps` round-trip 后约 `-7.77 net bps/trade`
- `top30% first-leg volume`：`-0.68 gross bps/trade`
- `top30% realized vol`：`+0.67 gross bps/trade`，按成本后仍明显转负
- `top30% volume & realized vol`：`-1.45 gross bps/trade`

也就是说，连最贴近论文叙事的伪 session continuation 壳，在当前 desk 可用的 perp 成本口径下都没有接近可交易的厚度。

### 2) 放宽到 20m 前段 / 20m 后段的 sweep，仍只剩“毛边启发”，不是可独立排队 pocket
本轮 sweep 里最好的组合是：

- `20m` 前段、`|first-leg| >= 15bps`、`top30% realized vol`
- `gross mean ~= +1.86 bps/trade`
- 只在 `5` 个月中的 `3` 个月毛值为正
- `median gross` 仍为负（约 `-0.92 bps`）

这个结果说明：
- 叙事上确实还能看到一点“高 realized-vol 下的短时延续痕迹”；
- 但它离穿过 `8~12 bps` perp round-trip 成本还差很远；
- 且不是一个多月份、稳定正中位数、足以直接排进 desk 队列的 pocket。

## 改变系统认知的话
`BTC intraday session momentum` 已完成 fresh intake first verdict 并收口 `background/P0`：最小 public perp probe 里，论文相邻的 `15m->15m` continuation 壳连 gross 都几乎贴地，放宽到 `20m` sweep 后最优组合也只有约 `+1.86 gross bps/trade`、正月数仅 `3/5` 且中位数仍为负，说明它目前只保留为 `pseudo-session structure / high-RV admission` 的 research hint，而不是可独立排队的 after-cost continuation pocket。

## 备注
- 本轮已按 policy 收口为 first verdict，不继续扩展成第二个 pending 小点。
- 因结论为 `background/P0`，无需分配 Rank。
