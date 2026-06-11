# Rank sign router first verdict → background/P0

- 时间：2026-04-25 12:53 UTC
- 对象：`research/quant_digests/2026-04-25_1116_xs-rank-sign-router-paper.md`
- 槽位：Fresh intake slot
- 动作：first verdict（只补 1 个最小 decisive blocker）

## 本轮要回答的唯一问题
这条 `cross-sectional rank sign router（bucket × sign × hold）` 题材，是否已经拿出了一个**当前可交易 crypto bucket 上、统一成本口径下、可复用的 after-cost sign-routing pocket**，足以让它留在前排做 `keep_P1`？

## 本轮补的最小 blocker
只看它有没有比既有素材多出一个会改变系统认知的新增 pocket，而不是再泛泛接受“sign 会切换”这句方法学提醒。

## 结论
**没有。该题材本轮应直接收口为 `background/P0`，不保留前排。**

## 为什么不是 keep_P1
1. **新增 digest 的核心贡献主要是方法学重述，不是新的可交易 pocket。** 这篇 4/25 digest 把论文改写成 `bucket × sign × hold` 路由器，并附了一个 `1h` portability probe；但它落下来的系统认知仍是：
   - majors 近样本更像 reversal；
   - liquid midcaps 近样本更像 momentum；
   - short leg 要降权或 veto。
   这些都更像“sign 不是常数”的研究提醒，**还不是一个已被证明可复用、可收缩成单一 front-slot 假设的 pocket**。

2. **它没有比既有同源素材多出一个更窄、更诚实、可直接排 follow-up 的前排对象。** 仓库里 2026-04-05 已有同一篇论文衍生的 `winner-only × loser-short veto` digest，已经把最可移植的结论收成：
   - 收益更多来自 winner leg；
   - loser short 默认是高 jump-risk 拖累；
   - 真正该测的是更窄的 long-only / half-short 版本。
   相比之下，4/25 这篇虽然把框架扩成 `sign router`，但**没有给出一个比“winner-only / loser-short-veto”更清晰、更低歧义的新前排命题**。

3. **当前 portability probe 仍不足以证明“可复用 pocket”，更像提示需要重新标定。** 文中列出的 Sharpe 是：
   - majors: `24h lookback + 6/12/24h hold` reversal 为正；
   - liquid midcaps: `24h lookback + 12/24h hold` momentum 为正；
   但这仍缺少：
   - 更统一的 bucket 定义与 listing-age / funding / jump veto 后稳定性；
   - `1h parent -> 15m/5m child` 的 pocket artifact；
   - 对 short leg 是否必要、是否只是单边 beta/样本期偶然的收口证明。
   所以它证明的是“要重新做 calibration”，**而不是“这里已经有一个可直接前排追踪的 pocket”**。

4. **该题材与现有前排标准相比，decisive blocker 不是某个便宜 follow-up 能一次性回答。** 若要把它升级成前排对象，下一步至少要做完整的 `bucket × sign × hold` 网格、long-only vs long-short/half-short、以及 child execution 迁移。这已经不是 fresh-intake 后的一次便宜 survivor 检查，而是一个新的中型研究分支；按当前 policy，不应因为方法学价值高就占前排。

## 会改变系统认知的话
`cross-sectional rank sign router` 这条新 digest 没有新增一个足够窄、足够诚实、成本后已显形的 crypto pocket；它主要补的是“sign 不能写死、short leg 默认危险”的方法学提醒，和仓库内既有 `winner-only / loser-short-veto` 同源结论高度重合，因此本轮应直接收口 `background/P0`，不保留前排 follow-up。

## 对 runtime 的影响
- Fresh intake 当前对象完成 first verdict：`background/P0`
- 不分配 Rank（未达到 `keep_P1`）
- Fresh intake slot 前移到下一条 pending：`research/quant_digests/2026-04-25_1152_crossvenue-contango-shell.md`
- cycle_plan 第 1 项标记 `done`
