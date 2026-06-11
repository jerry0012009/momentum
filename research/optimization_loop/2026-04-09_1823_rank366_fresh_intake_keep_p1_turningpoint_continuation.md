# Rank 366 fresh intake first verdict — turning-point-confirmed trend leg × short-horizon continuation

- 时间：2026-04-09 18:23 UTC
- 对象：`research/quant_digests/2026-04-08_2041_dynamic-turningpoint-tsmom-alpha.md`
- 动作：fresh intake first verdict
- 结论：`keep_P1`，并分配正式 `Rank 366`

## 这轮实际回答的问题
这条线能不能从“又一个趋势/动量说法”压成一个足够具体、能进入前排继续做 1 次 survivor follow-up 的 crypto pocket？

我的判断：**能，但当前只够 `keep_P1`，还不够直接升 `P2`。**

## 为什么不是直接打回 background
这条线已经有一个比 generic trend/momentum 更窄的、queue-facing 的因果骨架：

1. **事件定义是具体的，不是泛泛追涨。**
   它的核心不是“过去 N 根涨就继续追”，而是：
   - 先出现一段正/负 momentum cycle 的 formation；
   - 再等价格**超过前一个 turning point 的价位**；
   - 把这个 exceed 视作新一轮 momentum cycle 的确认；
   - 只交易后面很短的一段 continuation。

2. **持有窗足够短，能落到 short-cycle desk 语言里。**
   现有 digest 的 portability probe 已经把这条线压到 `5m/15m` 的 `1/3/6 bars` continuation，尤其 `15m` 上更像先能活的第一站；这比日频/小时级“大趋势会持续”更接近当前项目的可交易表达。

3. **它和现有 breakout / pullback family 仍有可区分性。**
   这条线的触发不是 rolling high breakout，也不是回踩恢复，而是“局部转折结构已经站上/跌破前一 turning-point level 后的确认续行”。如果后续能把 turning-point 定义做成 causal check，它可以成为一条独立 pocket，而不是现有趋势家族的纯改写。

## 为什么现在还不能直接升 P2
当前最大的未收口点不是“有没有一点毛 edge”，而是 **honesty / execution realism 还没真正关掉**：

- 论文里的 turning point 来自 smoothing filter algorithm；
- 文中明确有 sensitivity parameter `kappa=5`；
- 当前 digest 自己也承认现在只是 `EMA slope sign flip + threshold + 1-bar confirm` 的**薄近似**，不是 faithful replication；
- 若 turning point 的识别在实时里存在明显 endpoint lag / ex-post extremum dependence，这条线就会从“可交易 continuation”退化成“事后标注的漂亮结构”。

所以，这里**不是 fatal flaw**，但确实是 survivor follow-up 该优先回答的唯一高杠杆问题：
> 把 `turning point` 改写成一个严格因果、非事后重绘的 `confirmed extremum / prior-level exceed` 事件后，`15m` after-cost continuation 还剩多少？

## first verdict
- 正式 Rank：`Rank 366`
- 层级：`fresh intake -> keep_P1 -> Surviving candidate`
- 一句话结果：**`Rank 366` 已经把 turning-point-confirmed continuation 压成一个足够具体的 `15m-first` 趋势续行 pocket，但核心 edge 仍依赖 turning-point causalization 是否成立，因此先保留到 `P1 survivor`，不直接升 `P2`。**

## 对 runtime 的直接影响
1. `Fresh intake slot` 本轮已完成首判。
2. `Surviving candidate slot` 现切换为 `Rank 366`。
3. survivor 的唯一 follow-up 应优先做：
   - 把事件定义从 `EMA slope flip` 薄近似推进到**严格非重绘**的 `confirmed turning point / prior-level exceed`；
   - 聚焦 `15m`、top-liquid majors、after-cost expectancy；
   - 明确回答它到底是独立 pocket，还是会被现有 breakout/confirmed-extremum family 吸收。
