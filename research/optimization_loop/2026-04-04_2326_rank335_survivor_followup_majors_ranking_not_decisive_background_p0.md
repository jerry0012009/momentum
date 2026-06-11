# Rank 335 — survivor follow-up：majors / ranking 仍不足以把 dual momentum breakout expansion 升到 P2

- 时间：2026-04-04 23:26 UTC
- 对象：`Rank 335 / dual momentum breakout expansion`
- 轮次角色：bot3 auto execution
- 对应 cycle_plan：第 1 项（survivor 唯一一次 follow-up）
- 最终结论：`drop_to_background / P0`

## 本轮要回答的唯一问题
不是再证明它“看起来像个趋势想法”，而是要直接回答：

> 在固定 `1h regime -> 15m execution` 架构，并把 universe 收窄到 `BTC/ETH` 或最小 top-N ranking discipline 后，`Rank 335` 是否已经足够像一条可 admission 的 raw alpha，可以升到 `P2`？

答案：**还不够。**

## 为什么这一步不该升 P2
前一轮 first verdict 已经说明，这条对象的主语是清楚的：
- `20-bar breakout`
- `20/60-bar dual momentum`
- `ATR expansion`
- `bull regime gate`

所以它不是空壳，也不是纯叙事。但 survivor 这一步要求更高：要证明它在一个诚实、可搬到 desk 的最小壳里，已经有足够稳定的“可继续 admission”价值。

这一步没有做到，原因有三个。

### 1) 现有 majors 证据是“分裂 pocket”，不是同一壳下的稳定主体
digest 里现成的最小 portability probe 给出的最好结果是：
- `1h ETH`：`26` 笔，累计约 `+6.63%`，PF `1.22`
- `15m BTC`：`8` 笔，累计约 `+1.88%`，PF `1.63`

但同一批结果同时也显示：
- `1h BTC` 为负
- `15m ETH` 为负
- `SOL/BNB` 更差

也就是说，当前留下的是两个**分裂在不同 timeframe 的 pocket**：
- 一个像 `1h ETH` 的 trend pocket
- 一个像 `15m BTC` 的 short-horizon pocket

这还不能构成同一条 `1h regime -> 15m execution` desk 迁移壳已经成立的证据。更直白地说：
**它还没有证明“同一套 majors-first 规格”能稳定产出 edge，只证明了某些切片不难看。**

### 2) ranking / correlation gate 目前更像“可能的补救器”，不是已经被证成的 admission 主体
上一轮的 first verdict 已把 ranking / correlation gate 定位成“更像放大器，不是定义性前提”。

这句话在 fresh intake 阶段成立，因为它说明 raw alpha 主语不是假的；
但到了 survivor follow-up，要求变成：

> 你得证明在最小 ranking discipline 下，它已经足够值得进入 P2，而不是继续把希望寄托在更完整的 portfolio wrapper 上。

本轮没有新的 reader-facing 证据表明：
- top-N ranking 一上以后，亏损币被系统性剔除；
- 或 `BTC/ETH` 双币在同一套壳下已经呈现一致正向；
- 或 correlation gate 只是锦上添花，而不是决定成败的关键。

因此现在若把它升到 `P2`，实际上是在把一个尚未被证明的“组合层补救假说”带进 admission，而不是把一个已站住的 raw alpha 带进 admission。

### 3) survivor 的唯一一次 follow-up 不该被用来继续拖成“再试一次 ranking”
policy 很清楚：survivor 只有一次便宜诚实检查。

这次检查后，我们能诚实说的是：
- 这条对象**有清楚主语**；
- 但还没有证明它在 desk 关心的 `majors-first / ranking-aware` 最小执行壳下，已经足够稳定到值得进入 `P2 admission`。

如果下一步还写成“再补一个 top-N ranking backtest 看看”，那本质上是在把 survivor 阶段拖长，而不是收口。

## 本轮改变的系统认知
`Rank 335` 不再应被表述为“等待 majors-first follow-up、很可能升 P2 的 survivor”。
更准确的 runtime truth 是：

> `Rank 335` 的 breakout + dual-momentum + ATR expansion 主语成立，但目前只显示出零散的 majors/timeframe pocket；尚未证明在统一的 `1h regime -> 15m execution` 或最小 ranking discipline 下已经形成可 admission 的 raw alpha 主体，因此 survivor 唯一一次 follow-up 用尽后应直接退回 `Background pool / P0`。

## runtime 回写
- `Surviving candidate slot`：清空为 `none`
- `followup_budget_remaining`：视为已用尽
- `Background pool.latest_parked`：更新为 `Rank 335` 本轮 follow-up 收口失败，退回 `P0`
- `cycle_plan[1]`：写为 `done`

## 为什么这仍算真实推进
这轮不是无效重读，因为系统状态被明确收口了：
- `Rank 335` 不再占用 survivor 前排槽位；
- 后续轮次可以诚实切到新的 fresh intake，而不是继续围着同一条趋势 sleeve 做低杠杆补测。
