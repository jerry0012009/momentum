# Rank 365 / benchmark-beta return differential × thresholded pair fade — survivor follow-up exhausted -> background

- Time: 2026-04-08 07:05 UTC
- Target: `Rank 365 / benchmark-beta return differential × thresholded pair fade`
- Action type: surviving-candidate decisive follow-up
- Verdict: `keep_P1 exhausted -> background`

## Why this changes runtime truth
`Rank 365` 的主语本身是清楚的：`benchmark-beta adjusted residual -> thresholded pair fade` 确实比泛 pairs 教科书写法更窄。但这次 survivor follow-up 要回答的三个 admission 级问题——`benchmark` 定义敏感度、相对简单 raw-spread z-score 基线的 post-cost 增益、以及净边是否真的来自 beta-adjusted residual——在现有证据里都没有被压成决定性答案，因此对象不够诚实地升到 `P2`，应当按 survivor 预算用尽后收回 `background`。

## Evidence used
1. fresh-intake 记录已经把对象压成了明确 raw alpha，但也明确列出尚缺的三条 admission 级证据：
   - benchmark 定义敏感度；
   - 相对 raw-spread z-score 基线的 after-cost 增益；
   - alpha 是否真的来自 beta-adjusted residual。
2. 当前 digest 的 benchmark 口径只有单一路径：初版建议 `cap-weighted majors`，拿不到时再退到 `liquidity-weighted proxy`；这说明 benchmark 口径本身仍是主要自由度，而不是已经被锁死的稳定定义。
3. digest 虽然给出了论文里的累计利润与 cointegration 显著性，但没有把 `beta-adjusted residual shell` 与更简单的 `raw spread / raw ratio z-score` 在同一宿主、同一成本口径下做 head-to-head 对比；因此无法证明额外复杂度真的换来了更稳的 after-cost edge。
4. 现有材料也没有把净边拆解成“market beta 被剥掉后 residual 回归”与“传统 pairs MR 在特定样本里本来就会赚钱”这两部分的归因对照；也就是还没证明这条 edge 的独特性。

## Honest conclusion
这不是说对象主语错误，而是说它还停在“值得继续记住的 P1 线索”，没到 admission 级别。当前唯一一次 survivor follow-up 用完后，最诚实的结论不是继续开放式 `keep_P1`，更不是硬升 `P2`，而是 `keep_P1 exhausted -> background`。

## Result sentence
`Rank 365` 虽已把 `benchmark-beta adjusted residual -> thresholded pair fade` 压成独立 raw alpha，但 benchmark 定义敏感度、相对 raw-spread 基线的 after-cost 增益、以及 residual 独特归因三条 admission 级证据仍未建立，因此 survivor follow-up 收口为 `keep_P1 exhausted -> background`。
