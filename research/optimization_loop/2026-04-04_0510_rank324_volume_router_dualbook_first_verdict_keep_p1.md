# bot3 optimization log — Rank 324 volume-router dual-book first verdict keep P1

- Time: 2026-04-04 05:10 UTC
- Cycle item: `research/quant_digests/2026-04-04_0347_volume-router-tsmom-xsreversal-dualbook-alpha.md`
- Target: `Rank 324 / vol-z router × TSMOM / XS reversal dual-book`
- Decision: `keep_P1`

## Why this passes fresh-intake first verdict
这条对象通过 first verdict，不是因为 README 讲了一个“volume 很重要”的熟故事，而是因为 digest 已经把它拆成了 **两本可独立交易的 raw alpha 书 + 一个明确的路由层**：

1. **Book A = TSMOM continuation**
   - 主语清楚：单币 own-past continuation，而不是泛化的 breakout confirmation。
   - 可直接写成最小 desk 壳：`entry / exit / holding window / sizing / cost ladder` 都有明确落点。

2. **Book B = XS reversal**
   - 主语清楚：横截面 loser-vs-winner 的短窗回归，而不是模糊的“均值回归感觉”。
   - 同样已经能形成最小可测壳：排序、换仓、持有窗、成本口径都可独立定义。

3. **Router = volume z-score**
   - 关键不是把 volume 当 confirmation，而是把它升级成 `continuation` 与 `reversal` 之间的路由器。
   - 这使对象不再是“再给已有 alpha 加一个 filter”，而是一个能服务 short-cycle desk 的完整 dual-book raw alpha shell。

4. **对象具备 short-cycle 可迁移性，而不只是一份 4H 作业**
   - digest 已明确给出 `15m / 5m / 3m / 1m` 的最小实验压缩方式；
   - 所需输入仅为公开价格与成交量，不依赖私有订单流、低延迟特权或难以获得的外部数据；
   - 因此它至少具备进入 survivor follow-up 的资格，去回答 short-cycle 成本后 pocket 是否真实存在。

## Why it does not jump straight to P2
本轮还不能直接升 `P2`，因为最关键的不确定性还没被收口：

- README 叙事与源码实现并不完全等价；
- `vol_z` 作为连续 `tanh` 缩放还是分桶路由，哪一种才是诚实可迁移的 desk 版本，尚未经过最小 decisive follow-up；
- short-cycle 口径下的核心 blocker 也还没过：`15m` 上 router dual-book 在 `4 / 8 / 12 bps` 成本阶梯下是否仍能留下至少一条干净 lane。

所以它当前最合规的位置是：**`keep_P1` 并进入唯一一次 survivor follow-up**，而不是越级写成 `P2`。

## Result sentence
`Rank 324` 的 fresh intake first verdict 已完成：`vol-z router × TSMOM / XS reversal dual-book` 被确认不是把 volume confirmation 重新包装成主语，而是一条把 `TSMOM continuation`、`XS reversal` 与 `volume regime router` 三层拆开的完整 dual-book raw alpha 壳；因此本轮正式记为 `keep_P1`，并进入 `Surviving candidate slot` 等待那唯一一次 decisive follow-up。

## Runtime consequence
- 分配正式 `Rank 324`
- `Fresh intake slot` 本轮完成后释放
- `Surviving candidate slot` 切换为 `Rank 324 / vol-z router × TSMOM / XS reversal dual-book`
- `followup_budget_remaining = 1`
- `Active P2 slot` 继续保持 `Rank 322`，不受本轮影响

## Next decisive question for survivor follow-up
唯一值得做的 survivor follow-up 应直接回答：

> 在 `15m` 优先、`4 / 8 / 12 bps` 成本阶梯下，是否存在至少一条诚实的 `vol-z` 路由 short-cycle lane，使 `TSMOM` 与 `XS reversal` 不只是 README 双书故事，而是真能留下最小 post-cost pocket？
