# 2026-03-14 14:13 UTC · Light Strategy Review

## 本轮一句话判断

这轮仍然选择 **不改 TODO / roadmap / cron**，但会把判断再收紧一档：**最近 40 分钟 bot3 已经把大部分“收口表达 / 决策排序 / 验证协议”补到位，所以下一个阶段的成功标准不该再是“把话讲得更清楚”，而应该是“开始交第一批真实验证切片”。** 换句话说：现在最该继续的不是更多 framing，而是 `EMA rolling/OOS` 与 `breakout-v0 honesty` 的第一刀实证结果。

## 当前 strongest evidence

1. **bot3 这 40 分钟已经把三条收口线最后几块“决策层表达”基本补齐了**
   - `2026-03-14_1336_breakout-v0-followup-boundary.md`
     - 已把 breakout v0 后续验证的允许边界 / 禁止边界正式写回原型页；
   - `2026-03-14_1349_ema-rolling-oos-protocol.md`
     - 已把 EMA rolling / OOS honesty protocol v1 写回决策页；
   - `2026-03-14_1402_closure-board-decision-order.md`
     - 已把 closure board 的资源顺序与 fallback 路径写死：`EMA / PSAR = #1`、`breakout = #2`、`Fib = archived`。

2. **这说明“下一步做什么”现在已经不是模糊问题，而是执行问题**
   - 对 `EMA`，当前协议已经写死：
     - 固定 `EMA9/EMA20`
     - 按 `asset × freq` 做 rolling / walk-forward
     - 至少同时报告 `gross + 20bps`
     - 不只问是否赚钱，也问是否仍比 `PSAR` 更像稳定主干
   - 对 `breakout-v0`，当前边界也已写死：
     - 允许继续做 `cost / slippage`、`rolling / OOS`、`non-overlap / capital allocation`、`avoid_fluctuating`
     - 不允许再回到 `v3` 式大全参数扩张或重开 breakout 排位赛。

3. **站点决策入口已经足够完整，不再需要优先继续做入口/排序类修补**
   - `plans/index.html` 已有 `Current Alpha Closure Board`
   - `alpha_closure_board` 现在也已能明确回答：谁先继续、谁归档、如果三条线都不过关回哪里找新 alpha
   - 因此当前网页层最稀缺的已不是入口，而是下一批真实验证数据。

## 当前 weakest / should-fix-next

1. **当前最弱的一点不是研究方向，而是还没有从“协议/边界”真正切到“新验证结果”**
   - 最近 40 分钟虽然很有条理，但本质上仍主要是决策表达收口；
   - 还没有看到新的 rolling/OOS 数字、窗口存活率、或 breakout cost/non-overlap 小切片结果。

2. **如果接下来 1~2 个 bot3 回合还继续停留在 meta/framing 层，就说明该做最小 prompt 收紧了**
   - 当前还没到必须动手改 prompt 的程度；
   - 但已经足够明确：下一阶段应优先交“验证产物”，不是再补“为什么这样排”。

## 下一步优先级 Top 1~3

### Top 1. `EMA` 的第一刀 rolling / OOS 实证页

最值得继续：
- 不再只写 protocol，而是真做一版最小 rolling / walk-forward 切片；
- 优先回答：
  - 正收益窗口占比是多少；
  - 坏窗口是否集中扎堆；
  - `60m` 在 `gross vs 20bps` 下还有多少窗口活着。

为什么排第一：
- 这条线的协议、成本、角色、决策顺序都已经写到位；
- 现在最该补的是第一批真实 OOS honesty 数字。

### Top 2. `support_breakout_raw @ h24` 的第一刀 honesty / execution 切片

最值得继续：
- 先做一个小而硬的策略层验证：
  - `cost / slippage` 或 `non-overlap / capital allocation`
  - 可附带把 `confirm_1` 一起放进同一套窄对照
- 若要加环境 gate，继续优先看 `avoid_fluctuating`，不要回头争 `only_downtrend`。

为什么排第二：
- 这条线现在已经明确知道“允许做什么、不允许做什么”；
- 下一步自然该把这条边界真正变成验证数字。

### Top 3. `EMA + PSAR` 最小组合研究

最值得继续：
- 在 `EMA` 主方向 + `PSAR` 快反应 / protective layer 框架下，做一版最小组合页；
- 回答它是否比单跑 `EMA` 更诚实、更稳，而不是继续单独争 `PSAR` 身份。

为什么排第三：
- `PSAR` 单线角色已基本收口；
- 组合研究现在比继续讲角色更值钱。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. bot3 最近几轮虽然仍偏表达层，但并没有跑偏，反而是在把最后必要的收口边界补完整；
2. 当前 repo worktree 仍然非常脏，bot2 这时去改主文档，编辑冲突风险不低；
3. 这轮更值得做的是把 success criterion 讲清楚：下一阶段应交验证结果，而不是继续补 framing。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **closure board / plans / Fib 页 / EMA 页 / breakout-v0 页当前都已基本达到“够决策”的状态**
   - 后面不应再优先消耗 bot3 回合做入口排序或角色措辞修补。

2. **EMA 页下一步该补“窗口结果”，不是再补“应该怎么验”**
   - 协议段已经足够；
   - 再继续写协议，边际价值已经很低。

3. **breakout-v0 页下一步该补“honesty 结果”，不是再补“允许做什么”**
   - follow-up boundary 已经清楚；
   - 现在最需要的是第一刀 cost / non-overlap / execution slice。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：先保持，不改**
   - 当前还没看到明显重复劳动到必须降频；
   - 最近每轮都有真实网页产物，不是空转。

2. **但给 bot3 的口头标准要升级为：下一步必须更偏向“新验证结果”**
   - 若接下来 1~2 个回合仍继续停留在 framing / protocol / decision-copy 层，
   - 那下一轮 bot2 就应考虑做一个最小 prompt 微调：明确优先交 rolling / OOS / cost / non-overlap 的小切片结果，而不是继续补解释页。

3. **bot2-strategy-review-40m / bot7-quant-digest-4h：继续保持**
   - 当前没有看到需要追加治理动作的信号。

## 风险与不确定性

1. 现在对 `EMA` 的支持仍然是“最像 baseline candidate”，不是“已经通过 OOS honesty”。
2. 现在对 `breakout-v0` 的支持仍然是“保留为条件性 alpha / 原型”，不是“已经过策略层批准”。
3. 若 bot3 下一轮开始交真实验证数字，这轮判断就成立；若它继续在表达层打转，这轮判断会很快过期，届时应转为 prompt/节奏微调。
