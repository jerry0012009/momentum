# Rank 200 / BTC weekday-hour sparse short schedule — P2 admission promote P3

- 时间：2026-03-27 20:02 UTC
- 对象：`Rank 200 / BTC weekday-hour sparse short schedule`
- 本轮角色：bot3 对当前唯一 `Active P2` 做 admission 主检查，并按 policy 直接收口成 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 三选一

## 结论
**单一正式 verdict：`promote_P3`。**

更准确地说，进入 `Paper launch queue` 的不是泛泛的 weekday 异象，而是这条已经收窄清楚、足够 paper 化的对象：

> **BTC-only 稀疏时钟 short scheduler：每月滚动重算过去 365 天的 `weekday-hour` 弱桶，选 bottom-5，在桶结束后做 `4h short`；`2h/8h` 仅作邻近参数与退出对照。**

## 为什么这轮必须直接升 P3，而不是继续留在 P2
policy 明确要求：当 `P2 exit decision` 已达到“足够值得进入 paper trade / paper launch”的门槛时，bot3 必须直接升级，不能把升级动作留给下一轮 review。

`Rank 200` 现在已经满足这个门槛：

1. **effectiveness / expected return：够厚，不是勉强擦线。**
   - 已有 survivor 产物显示，`monthly refresh + hold=4h + 8bps`：
     - spot：约 `+26.36 bps/trade`，`127` 笔
     - perp：约 `+29.05 bps/trade`，`127` 笔
   - 即使把 round-trip 提到 `12bps`，仍分别约 `+22.36 / +25.05 bps/trade`。
   - 这已经不是“只能在极低摩擦下勉强为正”的口袋。

2. **cross-asset stability：诚实答案是 BTC-only，不构成 admission blocker。**
   - 这条线的 raw alpha 本来就是 BTC weekday-hour event clock；当前没有证据支持把它硬扩成 ETH/SOL 多资产家族。
   - 但 admission 需要的是回答“它应不应该严格限定在 BTC-only”，而不是强行要求跨资产复制。当前答案已经清楚：**应保留 BTC-only。**

3. **time stability：不是只靠单个静态训练窗口。**
   - `monthly refresh` 版本并未因为滚动重算而塌掉，反而比 static 更厚；重复入选的弱桶集中在 `Thu 19:00`、`Fri 00:00`、`Thu 13:00` 等少数时段，说明这更像可持续更新的稀疏 schedule family，而不是后验捡到的一次性最佳桶。

4. **parameter stability：邻近参数同向，不是单针尖。**
   - `2h`、`4h`、`8h` 在 rolling 口径下都为正；其中 `4h` 是默认主轴，`8h` 更厚但暴露更长，`2h` 更轻更薄。
   - 这足以回答 admission 需要的“是不是只有一个针尖参数能活”。答案是：**不是。**

5. **honesty / execution realism：已经足够 paper trade，不必再用研究口径拖延。**
   - 入口定义清楚：小时桶结束后入场。
   - 刷新频率清楚：每月重算一次 bottom-5 弱桶。
   - 执行场地清楚：spot 与 perp 同向，paper 更适合先走 perp 版本，便于做 short 与后续记账。
   - 频率清楚：稀疏事件触发，不是连续高换手系统。
   - 仍未补的 funding / 更细滑点，只影响后续 runner wiring 细节，不再构成是否进入 paper queue 的 decisive blocker。

## 为什么不是 one-time P2->P1 re-scope
不是因为“还可以再补一点 admission 证据”就回 P1。policy 只允许在存在唯一明确 re-scope 时才这么做。

这里不存在新的 re-scope 需求：对象已经很清楚，就是 **BTC-only / bottom-5 weekday-hour / monthly refresh / 4h short**。继续回 P1 只会变成开放式拖延，不合法。

## 为什么不是 drop_to_background
也不是因为这条线没有 fatal flaw：
- 没出现成本后翻负；
- 没出现 rolling refresh 直接失效；
- 没出现 spot/perp 方向相反；
- 没出现轻微参数扰动就坍塌；
- 没出现明显 lookahead / repaint / impossible execution 设定。

所以它不符合 `drop_to_background` 的条件。

## 对 Paper launch queue 的最小 handoff truth
本轮应把 queue truth 直接写成：
- `Paper launch queue.current_target = Rank 200 / BTC weekday-hour sparse short schedule`
- 该对象当前状态不是“研究中”，而是 **已完成 P2 admission，等待 dedicated runner + scheduler + 首跑验证的 paper launch wiring**

## 本轮改变系统认知的一句话
`Rank 200 / BTC weekday-hour sparse short schedule` 的 admission 已经完成：它不是需要继续开放式补证据的 BTC 稀疏时间袋，而是足够值得进入 paper trade 的 `BTC-only monthly-refresh bottom-5 weekday-hour -> 4h short` scheduler，因此本轮应直接从 `Active P2` 升入 `P3 / Paper launch queue`。
