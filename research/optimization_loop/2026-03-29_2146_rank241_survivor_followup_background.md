# Rank 241 survivor follow-up：same-asset executable-spread veto 未形成策略级 A/B 净增量，预算用尽后回 Background

- 时间：2026-03-29 21:46 UTC
- 轮次动作：`cycle_plan` 第 1 项（当前最前 pending）
- 对象：`Rank 241 / same-asset executable-spread veto`
- 层级动作：`Surviving candidate -> background/P0`

## 本轮只回答一件事
`Rank 241` 作为当前唯一合法 survivor，是否已经在至少一条已落库的 same-asset / cross-venue relative-value 策略线上，留下清楚的 `naive mid-gap` vs `executable spread after fee/gas/slippage` 策略级净增量，因此足以升到 `P2`。

## 检查到的现有相关策略线
1. `research/quant_digests/2026-03-26_0922_cex-dex-eth-leadlag-spread-alpha.md`
   - 已把 `Binance impulse -> Uniswap 5m catch-up` 写成 same-asset raw alpha。
   - 证据主轴是 `Binance 5m 冲击 + DEX 少跟` 的 pocket 存在，仍停在 raw-alpha/headline 级。
   - 没有同一条策略上的 `naive mid-gap` vs `executable spread after fee/gas/slippage` A/B 结果。
2. `research/quant_digests/2026-03-26_0252_futures-lead-spot-lag-spread-alpha.md`
   - 已把 `futures lead spike -> lagging spot/perp catch-up` 写成 same-asset relative-value raw alpha。
   - 仍是 lead-lag pocket / entry-exit 级主语，没有 `with execution veto vs without` 的策略级净增量对照。
3. `research/quant_digests/2026-03-25_1705_btc-cross-exchange-spread-vol-congestion-pocket.md`
   - 已经强调“可执行买卖价差”“maker 一腿 + taker 一腿”的 honest spread 口径。
   - 但这条线本身就是把 raw alpha 直接定义成 executable spread，并不是给既有 same-asset alpha 加一层 shared veto 的 A/B 证据；它不能回答 `Rank 241` 这条 overlay 是否能在另一条已落库策略上留下独立净增量。
4. 全库 grep 结果也没有找到任何已落库 artifact / report 明确做了 `naive mid-gap` vs `executable-price veto` 的同策略双臂对照，最多只有 digest 级别的执行哲学、成本提醒，或把“可执行价差”直接写进 raw alpha 本体。

## 为什么这意味着本轮必须收口
`Rank 241` 的 survivor follow-up 被 policy 写得很死：
- 它不是要再证明“execution realism 很重要”；
- 也不是允许继续写另一篇 same-asset/cross-venue digest；
- 它唯一需要的，是至少一条已落库策略线上的 **策略级 A/B 净增量**：
  - `without veto = naive mid-gap`
  - `with veto = executable spread after fee/gas/slippage`

本轮检查后，现有证据仍然只到：
- same-asset raw alpha 主语存在；
- executable-price / fee / gas / slippage 的 filter 逻辑也成立；
- **但两者还没在同一条已落库策略线上，被做成 `with vs without` 的净增量对照。**

因此现在不能诚实地说：
- 它已经证明自己能把某条现有策略的 post-cost 结果改善；
- 或已经足够独立到应该升入 `P2` 做 admission。

## 结论
`Rank 241 / same-asset executable-spread veto` 本轮 survivor follow-up 未找到任何已落库 same-asset / cross-venue 策略线上的 `naive mid-gap` vs `executable spread after fee/gas/slippage` 策略级 A/B 净增量；现有证据只到 filter 叙事成立、尚未落成可审计 overlay uplift，因此在唯一一次 survivor 预算用尽后，不升 `P2`，回 `background/P0`。

一句会改变系统认知的话：

> `Rank 241` 没有在任何已落库 same-asset / cross-venue 策略线上留下 `with executable-spread veto vs naive mid-gap` 的策略级净增量，现有证据仍只是“execution realism 这件事很重要”的 filter 叙事，因此 survivor 唯一预算用尽后不升 `P2`，回 `background/P0`。

## 回写要求
- `BOT2_BOT3_STATE.md`
  - 清空 `Surviving candidate slot`
  - `Fresh intake slot` 保留最近 intake 结论，不再占前排
  - `Background pool.latest_parked` 改写为本轮 `Rank 241` 收口
  - `cycle_plan` 第 1 项写入本句结果并标为 `done`
- 本轮不改 policy / brief / operating card / auto loop / cron prompt
