# 2026-03-15 15:32 UTC · Light Strategy Review

## 本轮一句话判断

这轮项目级排序仍然不变：`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`。但 **bot3 在接住上轮 TODO 后，又多走了一步 `rolling/OOS verdict sync`，说明当前最需要的不是再同步 deployment 口径，而是把 EMA 真正推进到第一份 `refresh / week-1 delta` 前瞻记录。** 因此本轮仍只做一个最小必要干预：把 EMA 下一步明确收紧成 **沿 `first-refresh queue` 落首个真实 refresh 结果**，避免继续在近义 `queue / verdict / closure-copy` 上空转。

## 本轮先检查了什么

1. 当前 cron 状态：
   - `bot3-momentum-auto-opt-13m`：`lastRunStatus = ok`、`consecutiveErrors = 0`
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：正常
2. 最近 3 条 optimization loop：
   - `2026-03-15_1504_ema-day0-ledger-snapshot.md`
   - `2026-03-15_1520_ema-first-refresh-queue.md`
   - `2026-03-15_1526_ema-rolling-oos-verdict-sync.md`
3. `docs/TODO.md` 当前 deployment-facing EMA 剩余动作
4. EMA 主报告与 closure 页的当前阶段口径

## 当前 strongest evidence

### 1) bot3 已经实质接住了“别再写近义 spec，去开账本”这条纠偏

最近 3 条产出里，前两条是正向推进：
- `15:04`：`day-0 ledger snapshot` 已真正落表
- `15:20`：`first-refresh queue` 已落表

这说明上轮 bot2 的微调没有白做，EMA 确实从“纸面 paper-ready”走到了“首张账本 + 首刷顺序”。

### 2) 但 `15:26 rolling/OOS verdict sync` 说明 bot3 开始出现新一轮边际递减

`2026-03-15_1526_ema-rolling-oos-verdict-sync.md` 做的事，不是新增 forward 结果，而是：
- 把已经完成的 rolling / OOS honesty 任务在 `TODO / plans` 再勾一遍；
- 把项目级 deployment verdict 再同步一遍。

这本身不是错误，但它是一个很清楚的信号：
- 当前 EMA 主线已从“缺口太多”切到“执行该往哪一个真实结果推进”；
- 如果 bot2 这轮不再出手，很容易让 bot3 继续回到 `已开账本 -> 再同步一层 wording/verdict` 的模式。

### 3) EMA 仍然明显是最接近 paper trading admission 的那条线

当前相较另外两条线：
- **EMA** 已有：`candidate spec -> operating spec -> monitoring board -> runbook -> day-0 snapshot -> first-refresh queue`
- **breakout**：仍停在 `one_more_gate`，且当前样本 same-sample slicing 已冻结，等新的 `pure-test / down-tail` forward honesty
- **Fibonacci**：继续 `park / archive`

因此本轮项目级判断不需要改：**EMA 还是最值得集中火力的一条。**

## 当前 weakest / should-park lines

1. **Fibonacci**：继续 archive，不抢主资源。
2. **breakout 的 same-sample follow-up**：继续冻结；当前没新 forward 证据，不值得 reopen。
3. **EMA 的近义 verdict sync / closure-copy**：现在开始成为低杠杆动作，应主动压住。

## 本轮最小必要干预

### 只做 1 个动作：把 EMA 下一步从“同步 verdict”收紧成“首个真实 refresh / week-1 delta 记录”

已在 `docs/TODO.md` 新增：

- `EMA：沿 first-refresh queue 落下首个真实 refresh / week-1 delta 记录（不要再继续做近义 verdict sync）`

目的很明确：
- 不改项目级总排序；
- 不改 cron；
- 不改 closure board 主口径；
- 只把下一步从“已经讲清楚的事再同步一层”推进到“在同一张账本里留下第一份真实变化记录”。

## 为什么这轮需要再动一次

因为当前已经满足 40 分钟 bot2 brief 里“应更快出手”的信号：
- 同一条主线连续两轮以上开始偏向 `queue / sync / wording / closure-copy`；
- 而不是继续给出新的前瞻执行结果；
- TODO 如果不再前推一步，bot3 很可能继续围绕“EMA 已多接近 paper”反复改写，而不是产生第一份真实 refresh 变化。

所以这轮最有杠杆的小动作，不是再讨论 admission，而是把 execution 下一步写死成：
**给账本新增第一份真实 refresh delta。**

## 下一步优先级 Top 1~3

### Top 1. EMA：沿 `first-refresh queue` 落首个真实 refresh / week-1 delta 记录

最优先对象：
1. `创业板ETF 1d` primary first refresh
2. front-queue secondary（例如 `美股-1d`）
3. `沪深300ETF 1d` shadow lane

最核心要求：
- 真落 `delta / monitor_status / review_action`
- 不再只写“之后应 refresh”

### Top 2. breakout：继续冻结，等新的 forward / down-tail 命中

当前没有理由回去做 same-sample micro-slicing；这条线仍然只是 `one_more_gate`。

### Top 3. 结构层后续若再推进，必须显式回答“是否稳定优于 EMA baseline”

EMA honesty 边界已经够清楚了；下一次结构层若继续，不应假装 EMA baseline 还没讲明白。

## 本轮改动

- 已编辑 `docs/TODO.md`
  - 新增并前推：`EMA 首个真实 refresh / week-1 delta 记录`
- 本轮不改：
  - `alpha_closure_board` 主排序
  - `bot2 / bot3 / bot7` cron 频率
  - breakout / Fibonacci 项目级结论

## 网页 / 表达建议

- 这轮不需要改 closure board 主文案。
- 下一次值得改网页的条件是：
  - EMA 账本里真的出现 first-refresh 变化；
  - 那时再把 `day-0 -> first refresh -> week-1 pending` 回写到入口页。
- 在这之前，再继续补 `EMA 离 paper 有多近` 的措辞，边际价值很低。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改
- `bot7 4h`：不改

原因：
- 当前偏差不是节奏错了；
- 是 **bot3 在“已开账本”之后，下一步动作类型需要继续被收紧成真实 refresh 结果**。

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate 已从 `paper spec / monitoring spec` 进一步推进为：
  - **首个真实 refresh / week-1 delta 记录**
- **needs one more gate：support_breakout_v0**
  - 仍缺新的 `forward / pure-test / down-tail honesty`
- **park / archive：Fibonacci**

## 风险与不确定性

1. `day-0 snapshot + first-refresh queue` 仍主要属于 execution scaffolding，不等于已经有新的前瞻 alpha 证据。
2. 若 bot3 下一轮继续忽略新 TODO，仍去做近义 sync / wording，后续可能要考虑 prompt-level steering。
3. breakout 若突然出现新的 pure-test/down-tail 命中，这轮继续冻结的态度需要复核。

## 本轮一句话结论（给 Jerry）

**EMA 这条线已经从“纸面接近 paper”推进到了“账本已开 + 首刷顺序已定”，所以这轮最该做的不是再同步一层 verdict，而是逼它交出第一份真实 refresh / week-1 delta 记录；我也已经把 TODO 明确推到这一步。**
