# 2026-04-13 00:52 UTC · post-cost tradeable label fresh intake first verdict

## 执行小点
- target: `research/quant_digests/2026-04-12_2205_postcost-tradeable-label-admission-filter.md`
- action: fresh intake first-verdict（统一 round-trip 成本快检 + 1 条 execution realism）

## 本轮最小实验（只做本小点所需）
- 资产：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`15m`
- 样本：最近约 `4000` 根 15m bar（`2026-03-02 09:00 UTC` 到 `2026-04-13 00:45 UTC`）
- raw admission：`spread_z_1d > 1` 且 `funding_rate > 0`
- 方向：`short perp + long spot`
- 持有：`8h`（`32` 根）
- 执行口径：`signal@t`，`entry@t+1 bar open`，`exit@t+33 bar open`
- 成本口径（统一）：`12bps round-trip`

## 结果
- 总信号数：`752`
- 信号加权 `gross_mean`: `+0.661 bps`
- 信号加权 `net_mean`（扣 12bps）：`-11.339 bps`
- `net > 0` 命中率：`0%`
- `net > 5bps` 命中率：`0%`

分资产：
- BTC：signals `286`，gross `+0.501bps`，net `-11.499bps`，`net>0=0%`
- ETH：signals `268`，gross `+0.506bps`，net `-11.494bps`，`net>0=0%`
- SOL：signals `198`，gross `+1.101bps`，net `-10.899bps`，`net>0=0%`

## honesty / execution realism 子检查（本小点允许的一条最小检查）
- 检查项：可交易时段与实际成交时点一致（strict next-bar open fill）
- 结果：对齐率 `100%`
- 解读：不存在“靠同 bar 或未来信息偷来的 fill 假象”；execution timing 不构成正向豁免。

## first verdict（收口）
- verdict：`background/P0`
- 会改变系统认知的一句话：
  - `post-cost tradeable-label admission filter` 作为**独立可交易 alpha** 不成立；在统一 `12bps` 成本下跨 `BTC/ETH/SOL` 仍全量费后不可交易。
- 唯一 decisive blocker：`edge_after_cost` 无法跨资产跨样本转正（且 execution timing realism 已通过，不是时点错配导致）。

## 备注
- 该对象仍可作为“shared admission filter”方法论保留在证据池，但不进入前排独立策略槽位。
