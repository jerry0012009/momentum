# Rank 188 / extreme-only sparse top-k shock reversal skeleton — P2 admission (effectiveness / cross-asset stability)

- 时间：2026-03-26 22:47 UTC
- 对象：`Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- 轮次角色：bot3 P2 admission 第一刀
- 结论：`keep_P2`

## 本轮只回答一个问题
在更完整的主流 perp universe 与统一成本口径下，`top-k=2~4 + 16-bar sparse rebalance + BTC gate` 这条 pocket 的 **effectiveness / expected return** 是否仍保留，以及它的 **cross-asset stability** 是不是已经 broad enough 到足以直接走 `P3`。

## 已有 admission 基线（沿用上一轮，不重开 dense 版本）
上一轮 survivor follow-up 已把系统认知从“dense 15m 明显判负”推进到：
- `top-k=2`、`16-bar sparse rebalance`、BTC gate：**gross `+0.053 bps/bar`，Sharpe 约 `+1.57`，turnover 约 `1.54x/day`**；
- `top-k=4`、`16-bar sparse rebalance`：**gross `+0.054 bps/bar`，Sharpe 约 `+1.73`，turnover 同样约 `1.54x/day`**；
- 以单边 `2 bps` 粗算，成本拖累约 `0.032 bps/bar`，所以净空间只剩 **约 `+0.021 ~ +0.022 bps/bar`**。

这说明：
1. `Rank 188` 已不是 dense 版本那种“高换手直接杀死”的明显负 edge；
2. 但它当前留给 admission 的**有效厚度很薄**，离“足够厚到直接进 paper queue”还有距离。

## 本轮补的新增证据：cross-asset broadness
为了避免只盯组合总收益，我用同一 `11` 个主流 perp cheap probe（`ETH/BNB/SOL/XRP/DOGE/ADA/AVAX/LINK/LTC/DOT/SUI`，`BTC` 只作 gate）补做了资产贡献拆解，观察这条 pocket 是否是 broad basket 还是少数币硬撑。

结果读法很明确：
- 正贡献主要集中在：`SOL / ETH / BNB / SUI / ADA`
- 负贡献主要集中在：`XRP / DOGE / DOT`，`AVAX / LINK / LTC` 也没有形成有力正贡献
- 也就是说，这条线**不是“多数主流币都稳定贡献一点”**，而更像是：
  - 少数趋势/弹性更好的币把组合抬正；
  - 一批主流币上同样的 shock-reversal 映射并不站得住。

换成人话：
> `Rank 188` 现在已经证明“不是完全死在 turnover 上”，但还没证明“这是一个 cross-asset 足够宽、可以放心当成 broad desk sleeve 的 pocket”。

## 对 effectiveness / cross-asset stability 的 admission verdict
### effectiveness / expected return
- **结论：保留，但不厚。**
- sparse 之后已经从明显负值翻到小幅正 gross，说明对象值得继续 admission；
- 但按当前成本口径，净 edge 仍只是薄正，不足以因为“方向翻正”就直接升 `P3`。

### cross-asset stability
- **结论：暂未通过。**
- 当前 pocket 更像被少数币种支撑，而不是在主流 perp 横截面里普遍成立；
- 所以这一步不能把它解释成“broad enough，已经 ready for paper launch”。

## 为什么这轮是 keep_P2，而不是 promote_P3 / drop_to_background
- **不是 `promote_P3`：** 因为当前 admission 第一刀已经看出两个现实限制：
  1. 净收益空间太薄；
  2. cross-asset broadness 还不够，存在“少数币 hard-carry”嫌疑。
- **也还不是 `drop_to_background`：** 因为 dense 负值与 sparse 薄正之间确实存在级别变化；这条线已经证明自己至少有一个诚实可交易 pocket，不该在还没做时间/参数/诚实性那刀前就直接判死。

## 本轮唯一改变系统认知的话
**`Rank 188` 的 `top-k=2~4 + 16-bar sparse rebalance + BTC gate` pocket 已确认不是 turnover-only 假象，effectiveness 仍保留薄正，但 cross-asset stability 还不够宽，目前更像少数币支撑的窄 pocket，因此本轮只能 `keep_P2`，且剩余唯一 blocker 已缩到“时间/参数/诚实性那刀能否证明这不是脆弱巧合”。**

## 系统影响
- `Rank 188` 继续留在 `Active P2 slot`；
- `p2_consecutive_keep_p2` 增加到 `1`；
- 下一轮若继续执行第 2 刀，必须只回答 `time stability / parameter stability / honesty-execution realism`，不能重复本轮 axis；
- 若下一刀仍不能把这条线收口成更扎实的准 `P3`，后续应更偏向直接出口，而不是继续开放式 admission。
