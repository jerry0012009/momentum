# Rank 168 / venue-tier-duration-gated funding carry — fresh intake 首判（keep_P1）

- 时间：2026-03-25 21:01 UTC
- 对象：`research/quant_digests/2026-03-25_1918_venue-tier-duration-gated-funding-carry.md`
- 轮次角色：bot3 executor
- 执行动作：fresh intake 最小首判，只回答 `park` 还是 `keep_P1`
- 结论：**keep_P1，分配正式 Rank 168**

## 为什么不是直接 park
这条线没有被当前快检证伪成“完全不可做”。被证伪的只是更宽泛、也更偷懒的读法：**BTC/ETH/SOL × Binance/Bybit/Hyperliquid 这类主流大 venue 组合上的 funding spread 太薄、持续时间太短，不能把它当成公共票息。**

但这份 digest 的核心价值并不在“大 venue 都能跑”，而在于把 raw alpha 收窄成一个更诚实、可继续检验的 deployable skeleton：

> 只保留 `venue tier + duration gate` 之后仍显著高于成本线的 cross-venue funding carry 机会；
> 若 spread 只出现在主流 venue 的单个 8h bucket 幻觉里，就应直接 veto。

## 首判依据
1. 论文结构证据仍支持“厚 spread 更可能来自 venue fragmentation / tier mismatch，而不是所有 venue 同质可做”。
2. 本地 21 天快检对主流三币给出的是否定筛查，不是全面反证：
   - BTC/ETH 各主流 pair 的 `share_episode_net_pos_after_4bps = 0`；
   - SOL 对 Hyperliquid 相关 pair 仅约 `8.3%` 的 `>=1bps` episode 在 4bps round-trip 下勉强为正；
   - episode 中位持续时长几乎都只有 8 小时，说明 **duration gate** 是生死线，不是修饰项。
3. 因此系统认知应从“funding carry 可能是普适票息”收缩为“它也许只在长尾 symbol / tiered venue 组合里成立，值得保留为一条窄版 P1 线索，再做一次唯一的 decisive follow-up”。

## 改变系统认知的一句话
**Rank 168 / venue-tier-duration-gated funding carry 保持 P1：可保留的不是‘大 venue funding carry’，而是仅限 `venue tier + duration gate` 的窄版 cross-venue carry skeleton。**

## 下一步（留给后续唯一 follow-up）
只回答一个问题：厚 spread 是否主要只存在于长尾/分层 venue，且在最小成本与持有时长假设下仍保留值得进 `P2` 的净边；如果答案是否定的，就应在下一步诚实结束，不再升 `P2`。
