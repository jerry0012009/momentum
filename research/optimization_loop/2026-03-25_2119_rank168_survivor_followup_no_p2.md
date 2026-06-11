# Rank 168 / venue-tier-duration-gated funding carry — survivor 唯一 follow-up 结论（不升 P2）

- 时间：2026-03-25 21:19 UTC
- 对象：`Rank 168 / venue-tier-duration-gated funding carry`
- 轮次角色：bot3 executor
- 执行动作：对 survivor 槽位执行唯一一次 decisive follow-up，只回答“厚 spread 是否主要只存在于长尾/分层 venue，且在最小成本与持有时长假设下仍保留值得进 P2 的净边”
- 结论：**不升 P2；结束前排，占用预算归零，回到 background pool 作为已收口的窄版 P1 skeleton**

## 本轮回答的唯一问题
答案是否定的，至少在当前 desk 已有证据口径下是否定的：

> 我们能支持的，只是“厚 spread 更可能出现在长尾 / 分层 venue”这个方向判断；
> 但我们**还不能诚实支持**“这些机会已经形成足够可扩展、可复制、净边明确的 deployable 组合”，因此这一步不能把 Rank 168 推进到 `P2`。

## 为什么这一步要收口，而不是继续拖
根据 policy，survivor 只允许这一次 follow-up；这一步之后如果仍未升级到 `P2`，默认就应退出前排。当前证据更像“限制条件越来越窄”，而不是“可部署性越来越清楚”。

## 依据
1. **本地快检对主流可复制组合几乎是负面结论。**
   - BTC/ETH 在 `Binance/Bybit/Hyperliquid` 各 pair 上，`share_episode_net_pos_after_4bps = 0`；
   - SOL 也只有 Hyperliquid 相关 pair 约 `8.3%` 的 episode 在 `4bps round-trip` 下勉强为正；
   - `>=1bps` episode 的中位持续时长几乎都只是 `8h`，说明很多 spread 只活一个 funding bucket，离“稳健 carry”很远。
2. **论文并没有把“长尾 / 分层 venue”直接证明成可部署 admission。**
   - 论文 headline 证据支持市场是 two-tiered、厚 spread 更多出现在更碎片化截面；
   - 但作者自己的 top opportunities 在扣成本和 reversal 之后，也只有 **40%** 仍为正收益；
   - 且 **95%** 的机会最终靠 forced exit 结束，这说明它更像“偶发而脆弱的 spread harvesting”，不是已经接近 paper-launch 的稳定 carry admission。
3. **当前缺的不是再补同维度一句话，而是缺可扩展 universe 的正面证据。**
   若没有 30~100 perp × 分组 venue（尤其 `CEX-CEX / CEX-DEX / DEX-DEX`）层面的 ex-ante persistence + post-cost 结果，我们无法把 edge 归因成“可扩展 venue-symbol family”，只能归因成“少数偶发点”。

## 改变系统认知的一句话
**Rank 168 / venue-tier-duration-gated funding carry 用完 survivor 唯一 follow-up 后仍不足以证明存在可扩展、成本后为正的 venue-symbol family；它只能作为已收口的窄版 P1 skeleton 退回 background，不升 P2。**

## 对 runtime 的直接影响
- `Surviving candidate slot`：本轮执行完毕后清空；
- `Rank 168`：不进入 `Active P2`；
- `Background pool`：新增一条已收口对象，保留的仅是“若未来明确 reopen，应直接按 long-tail / tiered-venue universe 扩展验证”的窄版方向，而不是继续把它当成当前前排主线。
