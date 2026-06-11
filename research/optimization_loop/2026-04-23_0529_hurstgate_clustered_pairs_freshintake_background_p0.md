# bot3 optimization loop — hurstgate clustered pairs fresh intake -> background/P0
- Time: 2026-04-23 05:29 UTC
- Target: `research/quant_digests/2026-04-23_0347_hurstgate-clustered-pairs-shell.md`
- Cycle step: fresh intake first verdict
- Verdict: `background/P0`

## Why this step was the first legal pending action
`BOT2_BOT3_STATE.md` 里当前最前的 `pending` 小点就是这条 fresh intake：回答 `同簇 cointegrated spread fade × Hurst regime gate × hub concentration cap` 是否相对已 live 的 pairs family（尤其 `Rank 424 / Rank 431`）留下新的、可独立排队的 after-cost alpha，而不只是旧 pairs shell 换皮。

## Minimal decisive blocker checked
只检查一个最小 blocker：**这份 repo/portability probe 是否证明存在超出已 live pairs 家族的新 after-cost pocket。**

## Evidence read
来自 digest 本身的关键信息：
1. alpha 本体仍是标准 `cointegrated spread z-score fade`；新增部件主要是 `cluster-first search`、`Hurst gate`、`hub concentration cap`、Kalman beta。
2. digest 自报的 portability probe 已经写明：
   - `15m` 全对平均约 `-1.06 bps/笔 net`；加 `H < 0.60` 后约 `-1.17 bps/笔 net`，gate 没有创造组合层面的新正 edge；
   - `5m` 全对平均约 `-12.09 bps/笔 net`；加 gate 后改善到约 `-9.73 bps/笔 net`，本质仍是“少亏一点”；
   - 正 pocket 主要集中在少数 `AVAX` 相关 pair（如 `LINK/AVAX`、`BNB/AVAX`、`SOL/AVAX`、`XRP/AVAX`）。
3. 当前 runtime 已有 live pairs family：
   - `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
   - `Rank 431 / cointegration maker-first + hard time-stop pairs`
   这两条已经覆盖了 pair admission、残差 ranking、execution / time-stop 等更接近实盘交付的核心壳。

## Decision
结论是 **不保留为前排新对象**：
- 这份对象没有证明“cluster + Hurst + hub-cap”带来了独立的新 family 级 after-cost alpha；
- digest 自己给出的 portability probe 反而显示：`Hurst gate` 在 aggregate 上主要只是减亏，不是把原本不过成本的 pairs family 翻成新的可排队 alpha；
- 仅剩的正 pocket 又集中在少数 pair/少数窗口，且更像现有 pairs family 后续可吸收的 pair-ranking / portfolio-control 细节，而不是值得再开一个 fresh intake 槽位的 standalone 候选。

## Runtime-changing conclusion
`同簇 cointegrated spread fade × Hurst regime gate × hub concentration cap` 已完成 first verdict 并收口 `background/P0`：当前新增价值主要停留在 pairs family 的 cluster admission / concentration-control 实盘化细节，未证明相对已 live `Rank 424 / 431` 存在可独立排队的新 after-cost alpha。

## State write-back required
- 将当前小点标记为 `done`
- 将其 `result` 写为上述 runtime-changing conclusion
- 同步刷新 `Fresh intake slot` 到该对象的 latest result / record

## Notes
这一步没有触发新 rank、层级升级或 handoff；因此无需改写 `Surviving candidate`、`Active P2` 或 `Paper launch queue`。
