# bot3 auto：Deribit terminal probability vs Polymarket binary price fresh-intake first verdict

- 时间：2026-04-18 02:55 UTC
- 执行小点：cycle_plan item1
- 对象：`research/quant_digests/2026-04-17_2114_deribit-polymarket-terminalprob-rv-alpha.md`
- 结论：`background/P0`

## 最小 honesty / execution realism 检查

本轮只补一个会改变 front-slot 结论的廉价检查：在 repo bundled `probabilities.csv` / `orderbook.csv` 样本上，用 README/digest 口径的触发门槛观察 edge half-life 与盘口可成交性，而不是继续讨论 Deribit 曲面模型本身。

检查结果：

- bundled probability 样本下，README/digest 级别触发总共只有 `12` 个 threshold hits。
- `DOWN` 侧（digest 原本认为更像有效 pocket）只有 `4` 个 hits，且 `edge_down` 在下一次概率刷新全部跌回门槛以下：`survive_next_refresh = 0/4`，`survive_2_refresh = 0/4`。
- `UP` 侧虽有 `8` 个 hits，但集中在单一 barrier / 单日附近，下一次刷新仅 `3/8` 仍过门槛，两次刷新仅 `2/8` 仍过门槛；其中尾部极端 edge 出现在接近市场生命周期末段，不能替代可重复 desk 节奏。
- orderbook 的名义 top-book spread 常见 `1c`，但样本交易回放总交易数仅 `5` 且最终资本从 `$100` 到 `$98.83`；结合上述 half-life，当前更像 thin-book / stale-probability snapshot，而不是可诚实保留 front-slot 的跨 venue RV alpha。

## verdict

`Deribit terminal probability vs Polymarket binary price` 暂不值得作为新的 front-slot raw alpha 保留：当前可复算证据只有极少交易与极短 edge half-life，尤其原本最可疑的 `DOWN` 侧触发在下一次刷新全部失效，无法支撑 desk 级 fillability / half-life realism；本轮 fresh intake first verdict 直接收口 `background/P0`。

## runtime 更新

- Fresh intake slot：item1 已收口 `background/P0`，front-slot 按 cycle_plan 顺序切到 item2 `research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`，等待后续轮次 first verdict。
- Background pool：追加本对象的 parked 结论。
- cycle_plan item1：`status=done`，`result` 写入上述结论。

## tail

- homepage index refresh：待执行。
- email summary：待执行。
