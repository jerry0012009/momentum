# Rank 258 / Deribit butterfly convexity static arb intake keep_P1
- 时间：2026-03-30 18:34 UTC
- 对象：Rank 258 / Deribit butterfly convexity static arb
- 动作：fresh intake first verdict
- 结论：`Rank 258` 的主语应锁定为 **Deribit BTC same-expiry options 链上的 butterfly / convexity static-arb 事件**，即当中间 strike 的 bid 高于两翼 ask 线性插值、或 LP 口径出现正初始现金流且到期非负 payoff 的同到期静态无套利违例时，做同 expiry 凸性修复；这条线对象边界、腿结构、entry/exit、成本梯度和可复刻数据源都已独立成型，因此本轮给 `keep_P1`，但由于 live sanity check 在严格与宽松过滤下都接近 `0` 事件，暂不升 `P2`，下一步只值得做一次便宜诚实的 event logger / persistence check。

## 为什么给 keep_P1，而不是直接回 background
1. **对象边界独立**：它不是泛 options monitor，也不是旧 parity/no-arb 家族的换皮；核心是 `same-expiry butterfly / convexity violation` 这一条明确可证伪的事件型 raw alpha。
2. **执行骨架完整**：
   - `entry`：LP 正利润或三点 butterfly 正 credit，且至少连续两帧存在；
   - `exit`：edge 回到 0、任一腿流动性消失、或距到期不足 30 分钟；
   - `sizing`：不超过最弱腿深度的 25%~33%；
   - `cost`：手续费 + 半个/一个/1.5 个 spread 三档。
3. **数据与实现可公开复刻**：Deribit 公共 REST 可分钟级抓链，必要时补腿级 order book；repo 也已经给出 LP 约束与基础过滤口径。

## 为什么不直接升 P2
1. **当前 live 样本太干净**：digest 已给出公开快检——在 `vol>=10 & spread<=20%` 的 desk-friendly 过滤下，245 个合约、12 个 expiry、`0 fee` 也没有扫到正初始现金流 static-arb；即便放宽到接近不过滤脏链，结果仍是 `0`。
2. **目前更像低频尾部事件扫描器**：主问题不是 spec 不清楚，而是事件频率可能过低，不足以占用更贵的 admission 资源。
3. **唯一值得补的 cheap follow-up 很明确**：做 7~14 天 event logger，看事件频率、持续时长、最弱腿深度与成本后三档净 edge；若长期仍接近 0，再收口回 background/P0。

## 本轮写回 runtime 的影响
- 新鲜 intake 正式建档为 `Rank 258`，状态 `keep_P1`。
- 上一条 fresh intake `Rank 257` 转入当前唯一合法 `Surviving candidate slot`，保留一次最小 decisive follow-up 预算。

## 一句话 result
`Rank 258：Deribit same-expiry butterfly/convexity static-arb 不是泛 options 监控，而是独立的低频事件型 raw alpha；虽然当前 live 快检几乎 0 触发，但对象与执行骨架已成型，首判 keep_P1，不直接升 P2。`
