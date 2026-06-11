# Rank 369 — dynamic pair admission × half-life-bounded spread fade — first verdict keep_P1

- 时间：2026-04-10 03:40 UTC
- 对象：`research/quant_digests/2026-04-10_0127_dynamic-halflife-admission-pairs-alpha.md`
- 结论：`keep_P1`
- 新 Rank：`369`

## 本轮只回答一个问题
`dynamic pair admission × half-life-bounded spread fade` 是否提供了独立于旧 `fixed-pair pairs/stat-arb` 家族的可存活增量，还是只是把 pair 选择写得更花。

## 读到的最关键证据
1. 同一策略壳下，`dynamic admission` 与 `fixed BTC/ETH` 已经出现方向性分离：
   - `15m`、`14d formation + 2d trading`、每天重选一次 pair、`ADF p<0.05` 且 `half-life 2~96 bars`、`z>2` 反手 / `|z|<0.5` 平仓 的 portability probe 约 `25` 笔、gross `+341bps`；
   - 粗扣每笔 `8bps` round-trip 后仍约 `+141bps`；
   - 同窗固定 `BTC/ETH` 约 `16` 笔、gross `-493bps`。
2. 被 admission 选中的窗口没有表现为“每天随机换 pair”的失真噪音，而是主要集中在 `ETH/XRP`（约 `11` 次）与 `SOL/XRP`（约 `8` 次）；这更像 admission 在识别稳定可交易子簇，而不是靠高 turnover 偶然刷出来。
3. `5m` 缩短版快检（`ETH/SOL/XRP/ADA`、`7d formation + 1d trading`）近约 `18d` 仍有约 `7` 笔 / `+242bps gross`，说明这条线不只活在慢频周尺度。
4. 当前最真实的保留意见仍然是：完整双腿执行、funding/borrow、冲击与容量还没被 production 级接入；但这不是一个单独就足以把对象打回 background 的 decisive blocker，因为首判阶段已经证明真正的增量来自 `dynamic admission`，而不是旧固定 pair 壳的低杠杆复述。

## 最小 honesty 结论
- `formation-window fragility`：存在，但当前没有证据显示它把 dynamic-vs-fixed 的方向性优势抹掉；相反，固定 `BTC/ETH` 已直接转负。
- `pair turnover`：当前不是唯一 decisive blocker；被选 pair 主要集中在少数 alt-major 组合，说明 turnover 尚未失真到不可交易。
- `half-life honesty`：当前 admission 已明确把可交易窗口限制在 `2~96 bars`，不是把超长回归时间硬塞进 short-cycle 壳里。

## verdict
`Rank 369` 的 first verdict 为 `keep_P1`：这条线当前最值钱的部分不是“pairs 还能做”，而是 `dynamic pair admission` 的确把固定 pair 壳从负值翻成了成本后仍为正的候选；因此它应进入 `Surviving candidate`，做且只做一次最小 follow-up，而不是直接打回 background。

## 应写回 runtime 的一句话
`Rank 369 / dynamic pair admission × half-life-bounded spread fade` 完成 fresh-intake 首判：其有效增量来自 `dynamic admission` 而非旧 fixed-pair stat-arb 改写；在统一 formation/trading 与最小成本口径下，dynamic shell 相对固定 `BTC/ETH` 已出现方向性优势，因此对象保留为 `keep_P1` 并进入 surviving candidate。
