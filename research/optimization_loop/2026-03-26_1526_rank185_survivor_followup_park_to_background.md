# Rank 185 / BTC 4h 3σ shock-reversal sleeve — survivor follow-up park_to_background

- 时间：2026-03-26 15:26 UTC
- Executor：bot3 auto 13m loop
- Source digest：`research/quant_digests/2026-03-26_1428_btc-jump-reversal-tail-fade.md`
- Prior state：`Surviving candidate slot`
- Verdict：`park_to_background`

## 本轮只回答一个问题
`Rank 185 / BTC 4h 3σ shock-reversal sleeve` 在更真实的事件分层、成交口径与时间稳定性下，是否仍足以诚实保留前排？

回答：**不够。当前最诚实的出口是 `park_to_background`，不升 `P2`。**

## 本轮补的最小诚实证据
直接用 Binance Futures 公共 `BTCUSDT perpetual 4h` 数据，按 digest 同口径重算 `2024-01-01 ~ 2026-03-26`：
- rolling sigma：`30d`（`180` 根 `4h` bar）
- 事件定义：上一根 `|ret| >= 3σ`
- 动作：下一根反向开仓，持有 1 根 `4h` bar
- 成交口径：同时看 `close->close` 与更诚实的 `next-open -> next-close`
- 成本口径：先看 `4 bps` round-trip

### 1) 成交口径没有把它救活，也没有显著恶化
整体 `89` 笔样本下：
- `close->close` 毛收益约 `10.08 bps/trade`，`4 bps` 后约 `+6.08 bps/trade`
- `next-open -> next-close` 毛收益约 `10.13 bps/trade`，`4 bps` 后约 `+6.13 bps/trade`

这说明问题**不是**“一换成更诚实的 next-open 口径，edge 就瞬间蒸发”；entry 假设本身并不是唯一 decisive blocker。

### 2) 真正的问题是时间稳定性明显不够
按年份拆开后，edge 基本被 `2024` 一年包办：
- `2024`: `34` 笔，`next-open -> next-close` 约 `+36.41 bps/trade net of 4bps`
- `2025`: `44` 笔，约 **`-11.15 bps/trade`**
- `2026 YTD`: `11` 笔，约 **`-18.38 bps/trade`**

翻成人话：**不是“现在还有点 noisy 但大体稳定”，而是最近一年多已经转成负值。** 当前 overall 正值主要来自更早的 `2024` 样本，不能据此诚实地把它留在前排继续 admission。

### 3) 方向分层不构成单一可救的 re-scope
按事件方向拆分：
- `fade downshock`: `50` 笔，`+7.31 bps/trade net of 4bps`
- `fade upshock`: `39` 笔，`+4.61 bps/trade net of 4bps`

方向上两边都不是灾难，所以这不是一个“只保留做多或只保留做空那一边就能自然修好”的明确单一 re-scope。真正拖累它的，仍是**时间稳定性崩塌**，而不是可一刀切修复的 side split。

## 为什么本轮不升 P2
P2 admission 默认至少要覆盖 `effectiveness / cross-asset stability / time stability / parameter stability / honesty` 五项。对 Rank 185 来说，这一轮 survivor follow-up 的任务不是把 admission 提前做完，而是先回答：它是否还值得占据前排、进入 P2？

当前答案是否定的：
1. **time stability 已出现决定性反证**：`2025` 与 `2026 YTD` 都为负；
2. **没有出现唯一明确的 P2->P1 re-scope 方向**：不是简单保留某个方向或换个更诚实 entry 就能解决；
3. 因此它不符合“继续占据前排、等待 admission”的条件。

## 本轮改变的系统认知
**Rank 185：`BTC 4h 3σ shock-reversal sleeve` 的整体正值几乎被 `2024` 早样本包办；在更诚实的 `next-open -> next-close` 口径下并未因成交假设失真而消失，但 `2025` 与 `2026 YTD` 已明显转负，因此 survivor 唯一 follow-up 收口应为 `park_to_background`，不升 `P2`。**

## Reader-facing conclusion
`Rank 185 / BTC 4h 3σ shock-reversal sleeve` 已用尽 survivor 的唯一 follow-up。当前最诚实的结论不是“再补一点 admission 证据”，也不是勉强升 `P2`，而是承认它的正值主要来自旧时段、近一年多时间稳定性不成立，因此本轮直接 `park_to_background`。
