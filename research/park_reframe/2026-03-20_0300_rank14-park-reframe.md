# 2026-03-20 03:00 UTC — Rank 14 park reframe review

- source rank: `Rank 14 / cross-asset TSMOM confirmation gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 14 被 park，不是因为“跨资产信息”这个主题从此没价值，而是因为它当时被写成了 **本币 sign-momentum + peer basket 同步共振确认** 这一条最小 clean-room 线后，结果非常硬负：

- `2026-03-17 00:52 UTC` clean replication 的 primary variant 是 `peer_dual_gate`
- `6bps/side` 下跨资产约：
  - `mean_total_return ≈ -87.28%`
  - `positive_asset_ratio = 0/3`
  - `mean_trade_events ≈ 3600`
  - `mean_max_drawdown ≈ -87.71%`
- 甚至比 baseline `sign(momentum)`（约 `-78.35%`）还更差
- `Light Stability Pack` 四项一起 fail：
  - 时间稳定性 `0/3 positive buckets`
  - 参数稳定性 `0/5 positive configs`
  - 跨标的稳定性 `0/3 positive assets`
  - 成本稳定性 `0/4 positive cost levels`

所以原 Rank 14 被审计否掉的核心，不是“跨资产永远无用”，而是：**把三币同频 peer-basket 共振，当成 15m crypto sign-momentum 的 standalone confirmation rescue，这条写法已经被清楚审计成失败。**

## 2) 它更像 hard park 还是 soft park
我把它判成 **soft park**。

原因：
- 原始失败主要集中在 **角色与实现形状**：
  - 同频、同步、三币彼此互相确认；
  - 仍然服务于 `standalone sign-momentum`；
  - 结果变成高交易数下的负增量过滤。
- 这不等于“跨市场 / 外部先行 / breadth 主题”已经被彻底证明无用。

但它又不是一个适合现在立刻派生 `Rank 14b` 的 soft park，因为 **最自然的窄救法，已经被更诚实的邻近旁支单独消费掉了**。

## 3) 有没有“可救信号”
有，但这些信号更像在说明“该去别的 rank 身上表达”，而不是继续从 Rank 14 自己切出新旁支。

### 可救信号 A：`ETF lead-strength` 比三币同步 peer gate 更贴“谁先发现价格”
`2026-03-19 05:01 UTC` 的 digest 已把跨资产主题收敛成：
- 不是让 BTC/ETH/SOL 彼此做同频确认；
- 而是用 `IBIT/FBTC/GBTC` 一类外部代理的 **lead-strength / impulse** 做 shared regime gate。

这条线后来已经落成 queue-only 的 `Rank 6b`：
- `demote BTC->COIN/MSTR direct lag-trade entry to an ETF / US proxy lead-strength shared regime gate`

它保留了“跨资产先行信息”主题，但表达方式明显比 Rank 14 原始的三币 peer gate 更诚实。

### 可救信号 B：`alt-vs-BTC RS breadth` 比 pairwise peer confirm 更贴“市场共识宽度”
`2026-03-19 02:37 UTC` 的 digest 已把另一条跨资产读法收敛成：
- 不问“另外两币是否和我同向”；
- 改问“alt 池里有多少币正在强于 / 弱于 BTC”。

这条线后来也已落成 queue-only 的 `Rank 28b`：
- `demote cross-market intraday leader-laggard signal from direct lag-trade entry to an alt-vs-BTC RS breadth shared regime gate`

它保留了“跨市场共振 / crowd alignment”主题，但比 Rank 14 的同步 peer gate 更上层，也更适合当前 desk。

## 4) 最值得改的唯一一刀是什么？
如果只看 Rank 14 本身，最自然的一刀本来会是：

**把“同频 peer basket 同向确认”降级成 shared cross-asset regime gate。**

问题在于，这一刀现在已经没有必要再以 `Rank 14b` 的形式重写：
- “外部先行价格发现”这条角色，已经由 `Rank 6b` 占掉；
- “市场 breadth / crowd alignment”这条角色，已经由 `Rank 28b` 占掉；
- 若再为 Rank 14 单独起一个 `14b`，很容易只是把已存在的 queue 候选换个壳重写一次。

所以本轮最诚实的结论不是再起新旁支，而是：
- **承认 Rank 14 的唯一主修改轴已经被邻近派生假设消费；**
- **本轮不再重复派生。**

## 5) 是否值得形成新的 derived hypothesis
**当前不值得。**

原因：
1. 原 `park` 的审计意义已经足够清楚，没必要推翻；
2. 最自然的单轴 reframe 并不是没有，而是已经被 `Rank 6b / Rank 28b` 这两条更干净的旁支表达掉；
3. 若现在硬写 `Rank 14b`，大概率会变成“把已经存在的 cross-asset regime / breadth gate 再包一层旧 rank 壳”，不够节制，也不够新。

因此本轮不新增 queue-only draft，结论保持：**`keep_park`**。

## 6) 本轮结论
- 原 Rank 14 为什么 park：作为 `standalone sign-momentum + peer-basket 同频确认`，收益、回撤、稳定性都被审计成硬负；
- 它更像：`soft park`；
- 可救信号：有，但已经主要体现在 `ETF lead-strength` 与 `alt-vs-BTC RS breadth` 两条更诚实的邻近旁支里；
- 最值得改的唯一一刀：理论上是“降级成 shared cross-asset regime gate”，但该修改轴已被现有 `Rank 6b / Rank 28b` 基本消费；
- 是否值得形成新的 derived hypothesis：**不值得**；
- 本轮最终结论：`keep_park`。

## 7) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：工作区存在大量与本轮无关的脏文件与未跟踪文件，当前不适合安全地 selective commit。
