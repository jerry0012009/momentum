# bot3 optimization log — 2026-04-18 02:40 UTC

## 执行对象
- cycle_plan item 3
- target: `research/quant_digests/2026-04-18_0146_queue-depletion-refill-asymmetry-alpha.md`
- action: fresh intake first verdict for `one-sided depth depletion × slow refill -> same-direction short drift`

## 本轮最小检查
只补 policy 允许的单一 honesty / execution realism 轴：
- 检查 digest 自带 live probe artifact 是否已经足以说明这条线在 maker/taker 成本与队列时滞下还能留下可诚实保留的 edge。

读取 artifact：
- `reports/artifacts/quant_digests/2026-04-18_queue_refill_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-18_queue_refill_probe_events.json`

关键观测：
- 样本只覆盖约 `210s`、`139` 个事件，仍是极短 sanity probe。
- 全部事件 signed mean return 只有：`ret5=+0.327bps`、`ret8=+0.425bps`。
- 最强子桶也只是：
  - `bid depletion + slow refill`: `ret5=+0.681bps`、`ret8=+0.822bps`
  - `ask depletion + slow refill`: `ret5=+0.203bps`、`ret8=+0.522bps`
- 正收益占比并不强：例如 `ask depletion + slow refill` 的 `ret5_positive_rate=22.2%`，`bid depletion + slow refill` 也只有 `53.3%`。

## 结论
这条线的公开可见证据只证明了“几秒级方向性并非纯随机”，但目前能看到的 edge 厚度只有 `0.2–0.8bps` 量级；一旦诚实补上 maker/taker 成本、排队失败、价差回吐和几秒级队列时滞，这个厚度不足以支撑独立 fresh-intake front-slot。

因此本轮 first verdict 直接收口：`background/P0`。

## 写回 runtime 的系统认知
`one-sided depth depletion × slow refill -> same-direction short drift` 在 digest 自带 `~210s / 139 events` 的 live probe 中虽保留几秒级 directionality，但 strongest bucket 也只到 `ret8≈+0.82bps`，明显低于诚实 maker/taker + queue-latency 成本门槛，因此不足以作为新的 microstructure raw alpha 保留前排，直接收口 `background/P0`。
