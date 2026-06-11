# Rank 314 — ORCA tradability-aware cluster pairs P2 exit decision: background/P0

- 时间：2026-04-03 19:40 UTC
- 对象：`Rank 314 / ORCA tradability-aware cluster pairs`
- 执行动作：作为当前 `Active P2` 的出口决策轮，收口 `更懒 refresh cadence + maker/taker 成本梯度 + pair remap latency` 后，这条 `tradability-aware admission-layer alpha` 是否已经足够值得进入 `P3 / paper launch queue`
- 结论：`drop_to_background / P0`

## 这一步回答的问题
上一轮已经知道：`top tradability-score pairs` 相比 classic `top-corr pairs`，在统一 `5m/15m` 固定成本 walk-forward 壳下能跑出更高累计净后收益；但优势主要来自更高 turnover 与更激进的 pair replacement。本轮要回答的是：

> 一旦把这层优势放进更诚实的执行口径——更懒 refresh、pair remap latency、以及 refresh/remap 时更容易落到 taker / crossed spread 的成本梯度——它是否已经硬到值得直接进 `P3 / paper launch`？

本轮结论：**还不够，且当前最诚实的收口不是继续 `keep_P2`，而是直接退回 `background/P0`。**

## 本轮依据（沿用已落地 artifact，做出口口径收口）
直接复核：
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/summary.csv`
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/5m_pair_selection_windows.csv`
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/15m_pair_selection_windows.csv`

核心数字：

### 5m
- `top_corr`: net `0.186484`，`14` trades，`133.203 bps/turn`
- `top_tradability`: net `0.277151`，`28` trades，`98.982 bps/turn`
- tradability 相对优势：`+0.090667`
- 多出来的交易：`+14`
- 等价优势容忍度：每笔新增交易只能再承受约 **`64.76 bps`** 的额外 refresh/remap 摩擦，优势就被吃光
- 但它自己的单笔效率已经比 classic `top_corr` **低 `34.221 bps/turn`**

### 15m
- `top_corr`: net `0.244820`，`24` trades，`102.008 bps/turn`
- `top_tradability`: net `0.294181`，`37` trades，`79.508 bps/turn`
- tradability 相对优势：`+0.049361`
- 多出来的交易：`+13`
- 等价优势容忍度：每笔新增交易只能再承受约 **`37.97 bps`** 的额外 refresh/remap 摩擦，优势就被吃光
- 但它自己的单笔效率已经比 classic `top_corr` **低 `22.5 bps/turn`**

## 为什么这轮不该 promote_P3
### 1) 这条 edge 目前本质上仍是“更高 churn 换来的 book-level 优势”
当前最关键的认知不是“tradability 没用”，而是：

> 它的优势主要体现在 **换得更快、换得更多**，而不是每一笔 spread / 每一次 signal 的兑现质量更高。

这点在两个频率上都一致：
- `top_tradability` 的 `pnl_per_turn_bps` 均低于 `top_corr`
- 更高累计净后回报，主要来自 **更高交易数 + 更短持有期**

这就意味着：一旦 refresh 不再被当成零摩擦白送，这层优势马上会变得很脆。

### 2) 一旦把 refresh/remap 放回真实执行壳，容错带其实并不厚
在 desk 口径里，pair remap 不只是“换个名单”这么便宜。它至少会带来：
- 信号 mapping 延迟
- 新 pair 切换期更容易跨 spread / 落 taker
- 老 pair 退出与新 pair 进入之间的过渡磨损
- alt-heavy pair book 在更懒 refresh 下可能直接错过最肥的快回归段

而当前 artifact 已经把可承受的额外摩擦上限说得很直白：
- `5m`：新增交易只要再多吃约 `64.76bps`，优势就归零
- `15m`：新增交易只要再多吃约 `37.97bps`，优势就归零

对一个 **alt-heavy、频繁 remap、且单笔效率本来就更低** 的 admission layer 来说，这并不是一个让人舒服的纸面缓冲。

### 3) 当前缺的不是“再补一轮同轴 admission”，而是一个全新的 execution-level 证据层
若要继续留在前排，下一步本该拿出的是：
- 懒 refresh cadence 下的真实净后存活情况
- refresh/remap 事件上的 maker/taker 成本归因
- pair 切换延迟对实际抓到的 spread 的侵蚀程度

但这些已经不再是“再做一轮 admission-layer 快检”能诚实回答的问题，而是 **新的 execution-layer 实证任务**。在当前 policy 下，bot3 不能把同一条 `P2` 用开放式同轴检查继续拖着。

## 为什么这轮也不该再 keep_P2
policy 明确要求：
- 当前轮是 `P2 exit decision`
- 结论必须在 `promote_P3 / one-time P2->P1 re-scope / drop_to_background / blocked:missing-single-decisive-blocker` 之间收口
- 不得继续写开放式同轴 `keep_P2`

本对象当前也不存在一个足够单一、足够具体、能自然写成 `P2->P1 re-scope` 的新 scope：
- 问题不是“只做 BTC/ETH 会不会更好”这种已明确成型的单一重定义
- 问题是整个优势本体仍依赖高 churn admission，而 execution realism 还没被穿透

所以最诚实的出口，不是勉强再挂着 `P2`，也不是伪装成 `P2->P1 re-scope`，而是：

> **把它作为一条“值得保留证据、但尚未穿过 paper-ready honesty 门槛”的 admission-layer 研究线，退回 `background/P0`。**

## 这条线还有没有价值
有。

本轮不是说 `tradability-aware cluster pairs` 是错的，而是把它的定位收得更准：
- 它已经证明：`top corr` 不是 pair admission 的唯一合理主语
- 它也证明：更快半衰期 / 更高 crossing density / 更活跃的 alt-heavy pair book，确实能改写累计净后结构
- 但它尚未证明：这种改写在更真实 refresh/remap/maker-taker 摩擦下，仍能成为一个值得直接接到 paper runner 的对象

所以它更像：
- 一个 **background research asset**
- 一个以后若有人明确要做 `execution-aware pair remap engine` 时可 reopen 的证据包
- 而不是当前队列里应该继续霸占前排的 `P2`

## 对 runtime 的影响
- `Rank 314` 从 `Active P2 slot` 退出
- 当前 `Active P2 slot` 清空为 `none`
- `Rank 314` 记入 `Background pool`
- 当前系统认知改写为：
  - `tradability-aware` admission layer 确有结构性增益
  - 但这层增益目前主要依赖更高 churn，而不是更强单笔效率
  - 在缺少懒 refresh / remap latency / maker-taker realism 的 execution-level 证据前，不足以诚实进入 `P3 / paper launch`

## 一句话 result
`Rank 314` 的 `tradability-aware cluster pairs` 已经证明“按可交易性而非纯相关性做 pair admission”能改写 book-level 净后表现，但当前优势主要靠更高 churn 而非更强单笔效率；在 `5m/15m` 下，这层优势对额外 refresh/remap 摩擦的容忍度仅约每新增交易 `64.76bps / 37.97bps`，不足以诚实支撑 paper-ready，所以本轮直接从 `P2` 收口到 `background/P0`，不再继续开放式 `keep_P2`。