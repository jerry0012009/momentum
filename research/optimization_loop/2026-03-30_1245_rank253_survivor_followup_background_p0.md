# Rank 253 survivor follow-up — same-venue conversion / parity reversal 回 background/P0

- 时间：2026-03-30 12:45 UTC
- 对象：Rank 253 / same-venue conversion / parity reversal
- 本轮动作：作为当前唯一合法 survivor 的唯一一次 follow-up，只回答公开 snapshot 下统一 inverse premium numeraire 之后，是否还留下成本后为正的 executable parity pocket
- 本轮结论：**唯一 follow-up 用完，回 background/P0**

## 本轮新证据
这轮不再停留在 repo 理论，而是把 Deribit BTC 公开链上的同所 call/put 顶档报价先统一成同一 USD numeraire，再直接看 top-of-book 可执行口径。

- 公共现货指数：`BTC index ≈ 67,851.96`
- 抽样对象：最近到期 `2026-03-31` 附近、`±5%` 行权价带内的 `12` 组 `call/put` 配对
- 口径：
  - `mid_gap_bps = ((call_mid - put_mid) * spot - (spot - strike)) / spot * 1e4`
  - `conversion_exec_gap_bps = ((call_bid - put_ask) * spot - (spot - strike)) / spot * 1e4`
  - `reversal_exec_gap_bps = ((call_ask - put_bid) * spot - (spot - strike)) / spot * 1e4`
- 关键样本：
  - `BTC-31MAR26-68000-C/P`：`mid ≈ +1.82 bps`，但 `conversion_exec ≈ -8.18 bps`，`reversal_exec ≈ +11.82 bps`
  - `BTC-31MAR26-67000-C/P`：`mid ≈ -1.56 bps`，但 `conversion_exec ≈ -8.56 bps`，`reversal_exec ≈ +5.44 bps`
  - `BTC-31MAR26-69500-C/P`：`mid ≈ +8.89 bps`，但 `conversion_exec ≈ -20.11 bps`，`reversal_exec ≈ +37.89 bps`
- 样本汇总：
  - 虽然个别 **mid** 偏离可到 `~5-9 bps`
  - 但 `12/12` 组样本里 **没有一组** `conversion_exec_gap_bps > 0`
  - 也 **没有一组** `reversal_exec_gap_bps < 0`
  - 也就是说，光在 call/put 顶档 bid/ask 这一层，公开 same-venue parity pocket 就已经被 spread 吃掉；更别说再叠加 quote age、顶档尺寸和 `6/10/14/20 bps` friction ladder

## 为什么这会改变系统认知
上一轮 intake 只能证明：对象边界清楚、值得做一次诚实 follow-up。

这轮 follow-up 新回答的是：

> 一旦把 inverse premium 先换算成统一 USD numeraire，再从 mid 幻觉切到 top-of-book 可执行口径，公开 Deribit BTC snapshot 下并没有留下可重复、成本后为正的 same-venue conversion/reversal pocket。

也就是说，这条线在公开数据上的主要风险不再是“也许还差一点点更多样本”，而是更本质的：

1. **mid 上看到的几 bps 偏离，大多在 bid/ask 一落地就消失；**
2. **repo 里最容易显得诱人的地方，恰好就是 inverse premium 单位错位 + 中价幻觉；**
3. **在还没引入 quote-age / size / 三腿同步惩罚前，top-of-book 就已经不够诚实。**

在这种情况下，再继续把它留在 survivor 或推进 P2，等于是在为“公开 mid 偏离看起来像机会”买单，而不是为可执行 pocket 买单。

## verdict
- **本轮 verdict：`唯一 follow-up 用完，回 background/P0`**
- 不升 `P2`
- 不保留 survivor
- 后续若要 reopen，必须基于新的、更强数据条件（例如可验证的高频同步快照/逐笔盘口存档，或明确的 maker/queue priority 假设），而不是继续重复公开 mid parity 检查

## 写回 runtime 的一句话
`Rank 253 / same-venue conversion / parity reversal` 的唯一 survivor follow-up 已完成：把 Deribit BTC 公开 options 顶档报价先统一为同一 USD numeraire后，最近到期 ATM 附近样本虽偶见 `~5-9 bps` 的 mid parity 偏离，但 `12/12` 组 top-of-book 可执行口径里既没有 `conversion` 正边、也没有 `reversal` 负边，说明公开 pocket 基本被 bid/ask 与同步摩擦吃掉，优势主要停留在中价幻觉而非成本后 executable alpha，因此本轮不升 `P2`，唯一 follow-up 用完，回 `background/P0`。