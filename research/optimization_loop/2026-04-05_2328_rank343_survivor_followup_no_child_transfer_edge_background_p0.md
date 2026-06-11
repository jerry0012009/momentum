# Rank 343 — survivor follow-up: no proven 1H->15m child transfer edge, drop_to_background / P0

- Time: 2026-04-05 23:28 UTC
- Target: `Rank 343 / POC + CVD absorption`
- Slot before execution: `Surviving candidate`
- Verdict: `drop_to_background / P0`
- Layer transition: `Surviving candidate -> Background pool`

## Why this changed system belief

本轮 survivor 唯一一次 follow-up 要回答的不是 `1H POC-proximal absorption` 本身是否像一条 alpha 壳，而是：

> 它是否已经留下足够证据，证明 `1H mother signal -> 15m child execution` 这条 short-cycle transfer boundary 真实存在，值得进入 `P2` admission。

现有材料给出的答案是否定的。

一句话收口：

> `Rank 343` 只证明了 `1H` 上的 `POC-proximal price/CVD absorption fade` 是清楚、可复现、且在 repo 自己口径里可盈利的 HTF raw alpha；但没有给出任何直接证据证明把它下传到 `15m child execution` 后仍保留成本后净增益，因此本轮不能诚实升到 `P2`，应按 policy 直接 `drop_to_background / P0`。

## What the evidence does prove

### 1) `1H` 母信号本体是成立的
上一轮 first verdict 已经确认：
- `rolling POC` 提供公允锚点；
- `price vs CVD slope disagreement` 提供 absorption trigger；
- `distance-to-POC` 与 `body/ATR` 过滤让它不是松散叙事；
- `cp < poc & bullish_absorption -> long` / `cp > poc & bearish_absorption -> short` 给出了完整方向壳。

也就是说，`Rank 343` 不是假 alpha，也不是 filter 冒充 alpha。

### 2) repo 反而明确给出了一个强负迁移信号
当前 source audit 最硬的 transfer 证据其实是负面的：
- README 直接写明 **`Crypto 1H is the only profitable timeframe`**；
- `15m / 30m / 2h / 4h` 在 repo 自己的 timeframe transfer check 下都没有活下来；
- 因此，现有证据清楚支持的是：**不要直接缩频**。

这能证明 `direct 15m clone` 不成立，但不能自动推出 `1H -> 15m child execution` 就成立。

### 3) 目前没有 reader-facing 证据证明 child layer 有额外增益
这轮 follow-up 需要的关键证据本应至少覆盖：
- `1H state -> 15m entry` 的具体窗口与 half-life；
- `next-open / first pullback / failed extension` 哪类 child entry 真有优势；
- `2 / 4 / 6 bps` round-trip 成本后是否仍保留正增益；
- `direct 15m clone` 继续失效时，`15m child execution` 是否显著优于直接追 `1H` open。

但当前材料里，这些都还停留在 **“下一步怎么测”** 的假说层，而不是结果层：
- 有 child-execution 思路；
- 没有 child-execution 实证；
- 有负对照设想；
- 没有已完成的负对照结果。

因此，当前不能把“合理的桥接猜想”误写成“已经存在的可迁移 short-cycle edge”。

## Why this is not enough for `promote_P2`

`P2` admission 的前提，不是对象“看起来挺值得继续研究”，而是它已经留下了足够具体、值得花 admission 预算去检验的 **short-cycle 前排对象** 证据。

`Rank 343` 当前缺的不是细枝末节，而是最核心的问题本身还没有被正面证明：

> 这条 edge 到底能不能从 `1H standalone` 迁移成 `15m child execution`？

如果这个问题还没有任何正面结果，只是因为它的母信号壳写得漂亮，就把它推进 `P2`，那等于把 survivor follow-up 当成了“继续留在前排的理由搜集”，不符合 policy。

## Why this is not a `keep_P1`

policy 已明确：
- surviving candidate 只有 **1 次** decisive follow-up；
- 用完后若仍未升级到 `P2`，默认移入 `Background pool`；
- 不允许继续拖成开放式观察。

所以本轮没有合法的 `keep_P1` 退路。

## Final runtime sentence

`Rank 343` 的 survivor 唯一一次 follow-up 已收口：现有证据只证明 `POC-proximal price/CVD absorption fade` 在 `1H` 上是清楚可复现的 HTF raw alpha，并明确否定了 direct `15m` clone，但没有证明 `1H -> 15m child execution` 已留下成本后可迁移增益，因此本轮不升 `P2`，按 policy 直接 `drop_to_background / P0`。

## Ops note

- 本轮产生新 verdict 与层级变化，应刷新首页。
- 本轮应发送中文邮件摘要。
