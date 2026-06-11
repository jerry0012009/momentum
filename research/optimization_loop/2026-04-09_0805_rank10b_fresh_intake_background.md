# Rank 10b / ATR stopDistancePct shared size-veto overlay — fresh intake first verdict = background / P0

- 时间：2026-04-09 08:05 UTC
- 对象：`research/park_reframe/2026-03-19_2242_rank10-park-reframe.md`
- 本轮角色：当前 front-slot fresh intake
- 结论：**background / P0**

## 一句话结论
`Rank 10b` 想保留的 `ATR stopDistancePct` 信息并没有形成一个新的、queue-facing 的独立 pocket；它更像已被既有 `breakout-short penetration×ATR short-admission`、`scheduled-event size-down overlay`、以及更宽泛的 tradeability / execution-risk overlay 家族吸收的共享风险层，因此本轮 fresh intake 直接收口为 `background / P0`。

## 这轮只回答一个问题
要回答的是：

> `standalone volatility-managed EMA sizing -> ATR stopDistancePct shared size-veto overlay` 这次角色降级，是否已经足够把原 Rank 10 从旧 ATR sizing park 中救成一个独立、可排进前排的 fresh intake？

回答：**没有。**

## 为什么不是 keep_P1
### 1) 它保留下来的不是独立 alpha，而是共享风险语义
`2026-03-19_2242_rank10-park-reframe.md` 自己已经把命题收得很窄：
- 不再让 ATR 决定方向；
- 不再把 ATR 写成一条独立策略；
- 只保留 `size-down / veto` 这种 shared risk overlay 职责。

这一步虽然更诚实，但也直接说明：**它的核心产出不是一个新的交易 pocket，而是一层共享风控/仓位治理语义。** 单靠“职责更诚实”还不够成为新的 front-slot 候选。

### 2) 关键旁证早就已经外流到更具体的宿主
`2026-03-19_1344_atr-stopdistance-size-veto-overlay.md` 给出的最强证据，是：
- `stopDistancePct` 在 15m 更像风险层；
- 高 ATR / 高 stop-distance 桶更适合 `size-down / veto`；
- 它在 breakout-style 事件代理里能改善高波动同仓位硬做的磨损。

但这份 digest 本身也已经把宿主写得很明确：
- `breakout-short`
- `Fib retest_hold`
- `EMA / PSAR continuation`

也就是说，这条轴的最强表达不是“独立 Rank 10b”，而是**挂接到具体 setup 上的 shared risk gate**。

### 3) 已有更窄、更 setup-specific 的前排对象吸收了这条轴
最直接的吸收者是 `Rank 222 / breakout-short penetration×ATR short-admission reframe`：
- 它已经把 `penetration / ATR` 压成 **breakout-short 专用**、可 strict A/B 的单轴假设；
- 不再停留在 generic volatility/risk overlay 说明；
- 已经因此拿到 `keep_P1`。

相比之下，`Rank 10b` 仍然是“给多种 setup 共用的 ATR size-veto 层”，对象边界更宽、宿主更模糊、可证伪口径也更松。**既然更窄、更诚实的 setup-specific 表达已经存在，就没有理由再把更宽的 shared-overlay 版本单独拉进前排。**

### 4) 它和既有 shared overlay 家族发生主题重叠，而不是产生新的 queue-facing 单体
`Rank 175 / fomc-event-clock-veto-size-down-overlay` 虽然最后没升 P2，但它已经把一个事实写得很清楚：
- “高风险事件窗存在” 与 “共享 overlay 真的能稳定带来净改善” 是两回事；
- 只证明风险窗客观存在，不足以让 shared overlay 本身进入前排。

`Rank 10b` 当前也卡在同一层：
- 能说明高 stop-distance 事件更危险；
- 还没说明独立把这层 shared overlay 抽出来，本身就值得占一个前排名额。

## 为什么不是 blocker，而是直接 background
这里不存在“只差一个唯一 decisive blocker”。

问题不是缺某个便宜补检，而是**对象身份本身不够独立**：
- 若把它继续推进，下一步自然动作一定是接到某个具体宿主上做 A/B；
- 一旦接到具体宿主，它就不再是 `Rank 10b` 这个宽泛 shared overlay，而变成某个 setup-specific admission/veto 版本；
- 也就是它的真实未来，不是独立 queue-facing 候选，而是被其它宿主吸收。

因此更诚实的做法不是给它 `keep_P1`，而是承认：**这条 residual 仍停留在 background 的证据骨架层。**

## 本轮改变的系统认知
**`Rank 10b` 的 `ATR stopDistancePct shared size-veto overlay` 没有形成新的独立 fresh intake；它只是把旧 Rank 10 的失败主题，重写成已被 `breakout-short / event-risk / tradeability overlay` 家族吸收的共享风险层，因此本轮直接收口为 `background / P0`。**

## Runtime 落点
- 本轮 fresh intake 首判：`background / P0`
- 不分配新 Rank
- 不占用 survivor 槽位
- 下一条合法 pending fresh intake 应前移到 `Rank 12b`
