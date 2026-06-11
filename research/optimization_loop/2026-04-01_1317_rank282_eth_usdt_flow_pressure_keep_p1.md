# Rank 282 / ETH-USDT exchange flow pressure alpha — first verdict = keep_P1

- Time: 2026-04-01 13:17 UTC
- Target: `research/quant_digests/2026-04-01_0452_eth-usdt-exchange-flow-pressure-alpha.md`
- Loop role: bot3 current-cycle executor
- Decision: `keep_P1`
- Assigned rank: `Rank 282`

## Why this intake survives
这条线已经不只是“链上情绪叙事”。当前 digest 至少把一个可审计的 directional raw alpha skeleton 说清了：

1. **alpha 来源清楚**
   - 主腿不是泛泛的“资金流有用”，而是 `ETH 进交易所 = 可卖出的 ETH 供给上升`；
   - 对照腿也清楚：`USDT 进交易所 = 可立即接盘的稳定币干火药增加`；
   - desk 版最自然的表达不是论文原始单变量，而是 `pressure_spread = z(ETH_exchange_net_inflow) - λ * z(USDT_exchange_net_inflow)`。

2. **执行骨架清楚**
   - 信号聚合频率、交易标的、入场、持有窗、风控和成本口径都已经给出最小版本；
   - 这意味着它已经能被干净地翻译成项目内部的实验 spec，而不是只能停留在论文 headline。

3. **诚实 transfer path 存在**
   - 虽然 paper-level 全复刻依赖的原始供应商口径不透明，但 desk 级最小复现不需要等原始 vendor；
   - 可以直接用公开链上转账 + 已标注交易所地址，自行聚合 `ETH/USDT -> CEX` 的 15m inflow proxy，再映射到 ETHUSDT perp 的 15m/5m/1m 执行层。

## Why it does NOT jump to P2 yet
当前不诚实直接升 `P2`，原因也很明确：

1. **honesty / execution realism 还没过**
   - 论文系数量级明显偏激进；当前更可信的是“方向可能对”，不是“幅度可直接照抄”；
   - 地址标签覆盖、交易所内部调拨、归集钱包搬运等噪音，可能让信号在真实 desk 口径下大幅衰减。

2. **还缺最小 clean-room replication**
   - 现在还没有完成公开标签版 `ETH inflow`、`USDT inflow`、`pressure_spread` 的事件分位测试；
   - 也还没回答最关键的 admission 前问题：这条线是单靠 `ETH inflow` 就够，还是 `ETH-USDT spread` 明显更稳。

3. **目前更像“值得做一次便宜而 decisive 的 follow-up”**
   - 合法下一步不该是开放式继续讲故事，而应直接做一次最小 replication：
     - 用公开链上标签聚合 `15m` inflow proxy；
     - 测 `top 10% / 5% / 1%` 事件后 `1h / 2h / 4h` 的 ETHUSDT perp after-cost 路径；
     - 对比 `ETH inflow` 单变量 vs `pressure_spread` 双变量。

## Runtime consequence
- 本轮将该对象正式记为 `Rank 282`；
- first verdict 为 `keep_P1`；
- 由于 policy 明确规定 survivor 只能是“上一条 fresh intake”，本轮需把 survivor 槽纠正为 `Rank 282`；
- 之前停在 survivor 槽的 `Rank 280` 并非本轮合法 survivor，应回写到 `background pool / wait-for-reopen`。

## One-line result
`ETH-USDT exchange flow pressure` 已形成可审计的 event-driven directional raw alpha skeleton，因此本轮正式记为 `Rank 282` 并首判 `keep_P1`；但在公开标签版 inflow proxy 完成最小事件分位 replication、证明 edge 不只是论文供应商/标签口径幻觉前，不诚实直升 `P2`.
