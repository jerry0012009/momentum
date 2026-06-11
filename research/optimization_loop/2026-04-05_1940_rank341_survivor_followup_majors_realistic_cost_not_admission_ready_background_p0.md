# Rank 341 / two-tier funding-rate cross-venue arb — survivor follow-up 收口 = drop_to_background / P0

- Time: 2026-04-05 19:40 UTC
- Source digest: `research/quant_digests/2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md`
- Prior state: `Surviving candidate slot`
- Verdict: `drop_to_background / P0`
- Layer change: `Surviving candidate -> Background pool`

## 本轮只回答一个问题

> 把对象压成 `BTC/ETH/SOL/BNB/XRP × 20/30/40bps × persistence / sign-flip / CEX-lead` 的最小 admission clean-room 后，它是否已经足够诚实地证明：在 liquid majors 与 realistic fee / slippage / transfer friction 下，`CEX-DEX funding spread × duration` 仍留下独立 alpha 壳？

本轮答案：**还没有。**

## 为什么这一步不能升 P2

source digest 的价值主要在于它把对象讲成了一个**像样的 cross-venue carry 壳**：

- 有清楚的 state：`8h-equivalent funding spread`
- 有清楚的 hierarchy：`CEX lead -> DEX lag`
- 有清楚的 admission 直觉：不能只看 spread，还要看 `duration / sign-flip / reversal`
- 有清楚的诚实提醒：round-trip cost 和 reversal risk 会吞掉大量纸面机会

但 survivor follow-up 这一轮要看的不是“壳像不像”，而是**它是否已经够资格进入更重的 admission/P2**。

在这点上，当前证据不够，甚至偏向否定：

1. **source 自己已经承认 after-cost 可活下来的机会占比不高。**
   - portfolio simulation 里 only `8/20` after-cost 为正；
   - 全部 20 个机会平均净 PnL 只有约 `$22`；
   - 平均 Sharpe 为负；
   - `19/20` 出现 reversal pattern。
   这更像“结构解释 + 强过滤需求”，还不是 admission-ready alpha。

2. **对象没有拿出 majors-first 的正面证据。**
   survivor 轮要求回答 liquid majors 是否也成立，而不是只靠长尾/illiquid 极端机会撑故事。
   当前 digest 虽然提出 `BTC/ETH/SOL/BNB/XRP` 作为下一步实验 universe，但那是**待测计划**，不是已完成证据。

3. **realistic friction 仍停留在概念提醒，不是 desk-ready break-even map。**
   当前 source 提到了 fee / slippage / transfer friction / holding duration，但没有给出对 `20/30/40bps × 12h/24h × majors venue pair` 的明确 after-cost 生死线。
   也就是说，`spread × duration` 是正确问题，但还没有被压成可准入的答案。

4. **`CEX lead` 目前更像市场结构解释器，不是已被验证能抬高净胜率的 gate。**
   source 证明了 `CEX -> DEX` 的信息流方向，但没有把它转成“在 majors 上 after-cost 更好”的 clean-room 结果。

## 为什么也不该继续 keep_P1

policy 对 survivor 很明确：

- survivor 只能是上一条 fresh intake；
- 最多只允许 **1 次** 最小 decisive follow-up；
- 这 1 次之后若仍未升级到 `P2`，默认移入 `Background pool`。

本轮已经用了这唯一一次 follow-up。

而且本轮没有得到会改变层级上限的新证据，只得到一个更清楚的收口：

> `Rank 341` 目前更像值得保留的 **cross-venue carry / regime-gated hypothesis shell**，但还不是已经通过 admission 的候选。

因此合法动作不是继续拖在 survivor，也不是硬升 P2，而是：**drop_to_background / P0**。

## 系统认知变化

`Rank 341` 的新增结论不是“funding cross-venue 不存在”，而是：

- 它确实不是旧 funding carry 的简单换壳；
- 但以当前证据强度，它更像**需要 future explicit reopen 才值得继续的 hypothesis shell**；
- 尚不足以占用当前前排资源进入 `P2 admission`。

## Result sentence for runtime

`Rank 341 / two-tier funding-rate cross-venue arb` 的 survivor 唯一一次 follow-up 已收口：现有证据只把对象压成了 `CEX lead -> DEX lag`、`spread × duration`、`CEX-DEX pairing` 的 distinct cross-venue carry hypothesis shell，但并未证明它在 `BTC/ETH/SOL/BNB/XRP` 等 liquid majors 与 realistic fee/slippage/transfer friction 下已留下 admission-ready 的 after-cost alpha，因此本轮按 policy 直接 `drop_to_background / P0`。
