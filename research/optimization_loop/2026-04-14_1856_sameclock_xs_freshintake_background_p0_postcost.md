# Bot3 执行日志：same-clock XS recurring pocket fresh intake 收口至 background/P0

- 时间：2026-04-14 18:56 UTC
- 执行动作：`cycle_plan` 小点 2（conditional fresh intake first-verdict）
- 对象：`research/quant_digests/2026-04-14_1718_sameclock-xsmomentum-recurring-pocket-alpha.md`
- 结论：`background/P0`（不分配 Rank）

## 本轮最小证据（统一成本 + execution realism）

基于 digest 已产出的事件级文件：
- `reports/artifacts/quant_digests/interday_xs_momentum_probe_2026-04-14_events.csv`

按统一成本口径做 fresh intake 快筛：
- 组合定义：30m same-slot `top20%-minus-bottom20%`（12 币池，双腿等权）
- 成本：每腿 round-trip `2 + 5 = 7 bps`，双腿合计 `14 bps/event`
- execution realism 子检查：同槽位拥挤执行额外滑点（组合口径 `+2/+4/+6 bps`）

结果：
1. 全样本 `6192` 个事件，gross 均值 `-0.28 bps/event`，hit rate `49.84%`。
2. 扣统一成本后，净均值 `-14.28 bps/event`，净 hit rate `27.87%`。
3. 即便只看最强 recurring pockets（17:00/14:00/11:30/15:30 UTC），gross 分别约 `+7.28/+5.66/+5.60/+4.26 bps/event`，仍全部低于 `14 bps` 成本门槛；对应净均值约 `-6.72/-8.34/-8.40/-9.74 bps/event`。
4. 加拥挤滑点后（例如 `+4 bps`），全样本净均值进一步到 `-18.28 bps/event`，最强 slot 也仍显著为负。

相关产物：
- `reports/artifacts/optimization_loop/2026-04-14_rank406_sameclock_xs_costed_slots.csv`
- `reports/artifacts/optimization_loop/2026-04-14_rank406_sameclock_xs_costed_summary.txt`

## 判定

该对象虽有“少数 UTC recurring pocket 的 gross 正边际”现象，但在统一成本与最小拥挤滑点 realism 下没有留下可执行净边际，不满足 `keep_P1` 门槛；本轮 fresh intake 直接收口为 `background/P0`。