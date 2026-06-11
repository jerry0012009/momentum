# Rank pending / same-slot cross-sectional market-neutral — intake首判：park

- 时间：2026-03-26 15:03 UTC
- 对象：`research/quant_digests/2026-03-26_1318_same-slot-marketneutral-weekday-mom-reversal.md`
- 执行动作：最小首判（只回答这条 raw alpha 当前是否值得进入 survivor）
- 结论：`park`

## 本轮只回答一个问题
`same-slot cross-sectional market-neutral` 这条 raw alpha 在当前 `15m` transfer 下，是否仍值得进入 survivor？

本轮答案：**暂不值得进入 survivor，直接 park。**

## 为什么不是 keep_P1
这份 digest 已经把最可能存活的 exact pocket 缩到很具体：
- `weekday after-hours same-slot reversal`
- `1~2d` same-slot reversal
- `15m` Binance perp proxy

但即使在这个已经缩窄后的 pocket 上，当前结论仍是：
- `gross ≈ +0.172 bps/bar`
- `turnover ≈ 55.2x/day`
- 单边 `2 bps` 成本后 `net ≈ -0.978 bps/bar`

也就是说，**现在不是“框架有趣，留到 survivor 再慢慢收口”的状态，而是最核心的可交易口袋已经先撞上了明确的 turnover / 成本悬崖。**

同一 digest 里，另一个候选分支 `weekday regular-hours same-slot momentum` 在当前 `15m` perp transfer 上更是 gross 已经转负（`gross ≈ -0.101 bps/bar`）。把两支硬拼成 combo 后，gross 只剩很薄正值，成本后同样不活。

## 系统认知变化
本轮改变的不是“这 repo 值不值得读”，而是：

**`same-slot cross-sectional market-neutral` 作为当前 desk 的 fresh intake，不应以 survivor 身份继续占前排。**

原因不是缺少某个便宜补测，而是 digest 自己已经给出足够 decisive 的 desk 级否决信息：
1. 最像样的分支只剩 `after-hours reversal`
2. 该分支当前 edge 主要停留在 gross
3. 成本后直接翻负，且 turnover 过高不是小修小补能忽略的问题
4. `regular-hours momentum` 当前迁移也未成立

因此这一步更诚实的首判是：**先 park 到 background pool，后续只有在用户明确要求 reopen、或出现新的低换手/稀疏化/更低 fee pocket 证据时再重开。**

## 本轮 verdict
- verdict: `park`
- survivor: `no`
- rank: `none`（未达到 `keep_P1`，不分配正式 Rank）

## 一句话结果（回写 state 用）
`s ame-slot cross-sectional market-neutral` 当前 `15m` transfer 下只剩 after-hours reversal 的 gross edge，但 `~55x/day` turnover 使其在保守成本后显著转负；regular-hours momentum 也未迁移成立，因此本轮首判直接 `park`，不进入 survivor。
