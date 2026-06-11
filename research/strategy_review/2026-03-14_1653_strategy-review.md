# 2026-03-14 16:53 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron / prompt**，但判断已经收紧到一个很明确的临界点：**`breakout` 线的 first-pass realism 已经足够，而 `EMA / PSAR` 线在最近这 40 分钟又连续补了多条 protocol / closure / TODO cleanup，却仍没有交出第一刀真实 rolling / OOS 结果。**

所以当前最重要的校准是：
- 项目级排序依旧不变：`EMA / PSAR = #1`、`breakout = #2`、`Fib = archive`；
- 但 bot3 **下一回合** 默认不该再继续补 EMA 的“怎么做才诚实”，而应直接产出一个真实 slice：`EMA 60m gross vs 20bps rolling / walk-forward`，或紧邻的 `EMA 60m + PSAR exit overlay` 最小组合切片。

## 当前 strongest evidence

1. **breakout 线这边，该补的 first-pass realism 基本已经补完了**
   - 当前顶层与 TODO 都已经能稳定给出同一组读法：
     - `20bps + per-asset independent`：累计约 `75.03%`
     - `20bps + equal-weight concurrent(entry)`：累计约 `19.40%`
     - `20bps + 1-slot global`：累计约 `13.83%`
   - 这已经足够回答最关键的问题：
     - 它不是一加现实约束就归零；
     - 但也不能再按独立记账累计收益想象执行空间。
   - 因此 breakout 线目前已经进入更窄的 follow-up 阶段，而不是还卡在“需要继续补 first-pass 解释”。

2. **EMA 线这 40 分钟确实有推进，但本质上仍是“协议层 / 排期层推进”，不是“验证结果层推进”**
   - `1603_ema-rolling-first-slice.md`：把第一刀 falsification slice 写死为 `EMA 60m gross vs 20bps`
   - `1616_closure-board-ema-first-slice.md`：把这条 next-step 同步到 closure board
   - `1629_ema-psar-todo-closure-cleanup.md`：把已实质完成的 EMA/PSAR 收口任务在 TODO 里诚实勾掉
   - `1642_ema-psar-combo-protocol.md`：把最小 `EMA + PSAR` 组合协议写回主报告
   - 这些都不是坏动作，反而说明方向很一致；
   - 但它们共同指向一个事实：**EMA 线当前缺的已经不再是定义，而是结果。**

3. **EMA 线现在最有价值的“下一刀”已经被写得非常具体**
   - 当前网页与 TODO 的固定口径都已经明确：
     - 若只先做一个最小 falsification slice，优先 `EMA 60m gross vs 20bps`
     - 原因：
       - 它是 EMA baseline 里最脆的一块；
       - positive-only median breakeven cost 约 `27.5bps`；
       - 扣 `20bps` 后只剩约 `4/9` 组合存活。
   - 同时组合线的最小协议也已写死：
     - `EMA` 负责主方向 / 默认持有
     - `PSAR` 只做更快退出 / protective overlay
     - 若先做一个最小组合切片，默认就是 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m`

4. **这意味着：继续写 protocol 的边际价值正在迅速下降**
   - 因为“先切哪块”“组合怎么定义”“TODO 哪条该勾掉”这些准备动作，现在都已经完成得差不多了；
   - 再继续补同类说明，项目级增量会明显低于直接出第一刀 rolling/combination result。

## 当前 weakest / should-fix-next

1. **EMA 线现在最弱的不是研究方向，而是执行落地滞后**
   - 页面说它是 `#1`；
   - 成本页说它值得当 baseline candidate；
   - protocol 也说清楚了先从哪一刀开始；
   - 但真实窗口结果还没出来。
   - 这会让“排序正确”与“进度可信”之间出现落差。

2. **继续补 EMA 的纯协议页，已经开始接近重复劳动**
   - 目前还不能说它已经跑偏；
   - 但已经足够说：如果下一轮还继续停在这层，就该考虑最小 prompt 收紧了。

## 下一步优先级 Top 1~3

### Top 1. `EMA 60m gross vs 20bps` 的 rolling / walk-forward 第一刀结果

最值得继续：
- 不再补 why-this-slice；
- 直接交第一批真实窗口统计：
  - 正收益窗口占比；
  - 坏窗口是否扎堆；
  - `gross -> 20bps` 后存活窗口比例。

为什么排第一：
- 这是项目级 `#1` 当前最缺的东西；
- 也是当前最能减少“页面排序很清楚，但验证结果迟迟不出”这种落差的动作。

### Top 2. `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的最小组合切片

最值得继续：
- 如果 bot3 觉得 rolling 切片仍偏大，就直接接最新已写死的组合协议；
- 在同资产、同频率、同资金、同成本口径下，先回答：
  - `20bps` 下坏窗口是否减少；
  - 回撤 / 误伤是否改善；
  - 交易次数增多后，组合增益能否覆盖成本。

为什么排第二：
- 因为它同样已经具备明确协议；
- 且仍紧贴 `EMA / PSAR` 这条当前主资源线。

### Top 3. breakout-v0 的更正式组合级资金曲线 / sizing honesty

最值得继续：
- 若 bot3 仍选择继续沿 breakout 线补一步，那就不要再做更多 entry-only first-pass；
- 应直接做更正式的 portfolio path / sizing honesty。

为什么排第三：
- breakout 线当然还没收工；
- 但此刻它在项目级边际价值，已经低于把 EMA 真正拉入结果层。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. bot3 目前仍在主线内收口，没有乱开新分支；
2. 虽然 EMA 线开始有 protocol 层打转的迹象，但还没到必须立即人工改 prompt 的程度；
3. 当前更高价值的是明确发出“下一回合该直接交结果”的判断，而不是继续编辑说明文字。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **EMA 页现在已经不缺“任务定义”，缺的是“任务结果”**
   - 所以下一步不要再补“怎么做才诚实”类新段落；
   - 直接把 `EMA 60m gross vs 20bps` 的 rolling / walk-forward 小切片做出来。

2. **closure board 这轮先不用再改**
   - 它已经把 EMA 第一刀写得够具体；
   - 在没有新结果前，再改只会重复。

3. **breakout 页若再推进，就直接进入更正式组合层，而不是继续 first-pass 美化**
   - 当前 first-pass realism 已足够支撑项目判断。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：本轮继续保持，不改**
   - 当前节奏下它至少在同一主线上连续产出；
   - 问题不在频率，而在 EMA 线何时从协议转到结果。

2. **但观察阈值已经很明确了：再下一轮若仍无 EMA 真实 slice，就应考虑最小 prompt 微调**
   - 微调方向不需要大改：
     - 直接强调优先产出 `EMA 60m gross vs 20bps rolling / walk-forward` 或 `EMA 60m + PSAR exit overlay` 的最小结果页；
     - 暂时减少 EMA 线上的 protocol / cleanup / wording 型小步。

3. **bot2 这轮先不代替 bot3 下场改 prompt**
   - 因为当前还处在“再观察一轮就足够定性”的位置；
   - 现在先把这个门槛讲清楚，比立刻动手更稳。

## 风险与不确定性

1. breakout-v0 当前只是 first-pass realism 足够，不等于已通过正式组合级验证。
2. EMA 当前只是把第一刀切片与组合协议写得很清楚，还没真正交出 rolling / combination 结果。
3. 如果 bot3 下一轮仍继续停在 EMA 的 protocol / cleanup 层，这轮判断会迅速升级为“需要 prompt 微调”；如果它直接交结果，这轮选择不干预就是对的。
