# Rank 319 — directional-change × VWAP/EMA asymmetric trend shell first verdict: keep P1

- Time: 2026-04-04 00:30 UTC
- Target: `research/quant_digests/2026-04-03_2251_dc-vwap-ema-asymmetric-trend-shell.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `319`

## Why this changes runtime truth
这条对象已经具备清楚的 `VWAP-EMA directional-change continuation × ~1% reversal exit` 主语，不是空泛的“趋势确认 filter”。repo 还把 entry / exit / cost / deploy fraction 落成了完整策略壳，因此它满足进入 `P1` 的最低要求。

但当前证据同样明确说明：
- `5m/15m` 的 majors / 常见 alts 直搬参数并不成立；
- edge 更像是“可迁移机制 + 必须先做 asset admission”，而不是 universal trend alpha；
- 因而本轮不能直接升 `P2`，下一步只值得做一次 survivor one-shot：验证它是否至少存在诚实的 `5m/15m` asset-admission 路径，或者更适合作为 exit shell 而非独立 raw alpha。

## First-verdict decision
结论不是 `background/P0`，因为这条线已经满足：
1. 有明确 raw alpha 主语；
2. 有完整 entry/exit/cost 壳；
3. 有可执行的最小 follow-up 问题：到底能否在 desk 关心的 `5m/15m` 形成诚实的 asset-admission 路径。

因此本轮正式写成：

> `Rank 319：directional-change × VWAP/EMA asymmetric trend shell first verdict 完成，保留为 P1 survivor；当前更像需要 asset-ranking admission 的单资产趋势母板，而不是可直接通用部署的 universal strategy。`

## Runtime effect
- fresh intake 已获得正式 Rank：`319`
- 层级：`fresh intake -> P1 / Surviving candidate`
- survivor one-shot follow-up budget: `1`
- reader-facing implication: 后续只应再做一次最小 decisive follow-up，验证 `5m/15m` 下是否存在诚实的 asset-admission 路径；若没有，就应直接收口到 background，而不是继续把它当通用参数故事拖长。
