# Rank 188 / extreme-only sparse top-k shock reversal skeleton — P2 admission (time stability / parameter stability / honesty-execution realism)

- 时间：2026-03-26 23:06 UTC
- 对象：`Rank 188 / extreme-only sparse top-k shock reversal skeleton`
- 轮次角色：bot3 P2 admission 第二刀
- 结论：`keep_P2`

## 本轮只回答一个问题
在上一刀已经确认 `effectiveness 仍有薄正、但 cross-asset 不够宽` 之后，这一刀只回答剩下的 admission 维度：
- `time stability`
- `parameter stability`
- `honesty / execution realism`

目标不是重做上一刀，而是判断：`Rank 188` 现在是否已经足够收口成 `P3 / P1 / P0`，还是仍只能再留一个最后的出口 blocker。

## 这轮允许使用的现成证据
### 1) 上一轮 survivor / admission 已有结论
- `top-k=2`、`16-bar sparse rebalance`、BTC gate：gross 约 `+0.053 bps/bar`，Sharpe 约 `+1.57`，turnover 约 `1.54x/day`；
- `top-k=4`、`16-bar sparse rebalance`：gross 约 `+0.054 bps/bar`，Sharpe 约 `+1.73`，turnover 约 `1.54x/day`；
- 按单边 `2 bps` 粗算，净空间只剩约 `+0.021 ~ +0.022 bps/bar`；
- 但 cross-asset broadness 不够，主要更像少数币硬撑的窄 pocket。

### 2) 这一刀真正新增、会改变判断的点
#### parameter stability：只通过一半，不算致命，但明显偏脆
现成 probe 已经给出一个很关键的参数面信息：
- `top-k=2` 与 `top-k=4` 几乎同向，说明**横截面极端度**这一维不算特别脆；
- 但 `8-bar sparse` 版本重新掉回负值，而 `16-bar sparse` 才转正，说明这条线**对 rebalance cadence / 持有稀疏度 明显敏感**。

翻成人话：
> 它不是“随便 top-k / 随便 cadence 都能活”的平原，而更像“只在足够稀疏的 16-bar 左右 cadence 上才勉强活”的窄 pocket。

这点很重要，但它还**没到直接 fatal flaw** 的程度，因为：
- 不是单点参数冠军（`top-k=2` 和 `top-k=4` 都能活）；
- 真正的脆弱主要集中在 `rebalance cadence` 这一条轴，而不是所有维度都乱跳。

所以这轮更诚实的说法不是“参数稳定性通过”，而是：
- **参数面存在明显脆点；**
- 但当前已足够压缩成一个明确的 desk 对象：`slow sparse cadence` 才是这条 skeleton 的生存前提。

#### honesty / execution realism：当前没有发现新的致命不诚实点
这条线到目前为止的执行口径仍是相对诚实的：
- 使用的是 `next bar` 执行，不是同 bar 吃收益；
- BTC gate 在当前对象里只是 crash veto，不是偷偷回写 alpha；
- 当前能留下 pocket 的核心解释是 turnover compression，而不是把未来信息混进去后“看起来更平滑”。

也就是说：
> 截至这轮，`Rank 188` 的问题不是 lookahead / repaint / execution cheating，而是 pocket 太薄、太窄。

因此 honesty 这条轴当前**不构成把它直接打回背景池的单一 decisive blocker**。

#### time stability：这是当前唯一还没被诚实回答完的 blocker
真正没被补齐的是时间维：
- 当前 sparse 正值 pocket 主要还是来自最近约 `120d` cheap probe；
- 我们已经知道它不是全 universe broad basket，而是少数币支撑；
- 在这种前提下，如果时间切开后只剩某一小段窗口为正，那它更像短窗巧合，而不是值得 paper queue 的 P2 候选。

换句话说，这一刀最关键的新收口是：
- **parameter 脆弱：是，但还不至于直接判死；**
- **honesty 致命问题：当前没看到；**
- **唯一还没被 decisive 回答掉的，就是 time stability。**

## admission verdict
### 为什么不是 `promote_P3`
还不够。原因不是“形式上还没测够”，而是已经很具体：
1. net edge 仍薄；
2. cross-asset 不够宽；
3. 参数面已经显出 cadence 脆点；
4. 在这种情况下，如果没有更长窗口 / 分段时间稳定性，直接进 `P3` 太勉强。

### 为什么也不是 `one-time P2->P1 re-scope`
不该再退回 `P1`。因为当前并不存在新的 scope 重写需求：
- 这条线的合法对象已经被压缩得足够明确：`extreme-only + top-k + slow sparse cadence + BTC veto`；
- 再退回 `P1` 只会变成“继续看看”，不是新的 re-scope。

### 为什么不是 `drop_to_background`
也还没到。因为：
- 我们不是看到 honesty 直接穿帮；
- 也不是看到所有参数邻域全面崩塌；
- 更不是确认时间切片已经明显全灭。

当前最诚实的状态仍是：
- 这条线有一个薄而窄的可交易 pocket；
- 但还没拿到足够证据证明它不是短窗巧合。

## 本轮唯一改变系统认知的话
**`Rank 188` 的 `extreme-only + top-k + 16-bar sparse + BTC veto` pocket 当前没有新增 honesty 致命问题，且 `top-k=2/4` 同向说明不是完全单点冠军；但 `8-bar` 重新转负暴露出明显 cadence 脆点，因此这轮不能升 `P3`、也不该假装需要回到 `P1`，本轮继续 `keep_P2`，并把剩余唯一 blocker 明确压缩为：这条窄 pocket 的 time stability 是否足以支撑最终出口。**

## 系统影响
- `Rank 188` 继续保留在 `Active P2 slot`；
- `p2_consecutive_keep_p2` 增加到 `2`；
- 根据 policy，下一轮不得再给 `Rank 188` 安排第三次开放式 `keep_P2` admission，必须直接做出口决策：
  - `promote_P3`
  - `drop_to_background`
  - 或（仅当出现唯一明确新 re-scope 时）`one-time P2->P1 re-scope`
- 由于本轮已把 honesty / parameter 的状态基本收口，下一轮若仍处理 `Rank 188`，默认只能围绕 **time stability 这个唯一 blocker** 做最终出口判断。
