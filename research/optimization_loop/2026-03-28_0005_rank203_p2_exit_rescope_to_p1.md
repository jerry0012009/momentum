# Rank 203 / graph-matching pairbook mean-reversion P2 exit → one-time P2->P1 re-scope

- 时间：2026-03-28 00:05 UTC
- 轮次来源：bot3 13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 执行动作：执行 `cycle_plan` 最前项 `Rank 203 / graph-matching pairbook mean-reversion` 的 `Active P2` admission 出口决策
- 正式结论：`one-time P2->P1 re-scope`

## 本轮只回答的唯一问题
> 在已确认 `max-degree<=2` hybrid 优于 full non-overlap 的前提下，这条线是否已经能在统一成本/执行口径下通过 `effectiveness + honesty` 主门槛，足够值得直接进入 `paper trade / paper launch`？

## 本轮新增的 evidence axis（避免重复上一轮）
上一轮 `Rank 203` 的 axis 是：
- stronger pair admission 下，`full non-overlap` vs `degree2` vs overlap baseline 的**结构比较**；
- 结论是 `degree2` 在五个滚动窗口里是当前最像 production 候选的 pair-book 形态，因此升 `P2`。

本轮不重复那个 axis，而是专门补 **`execution realism / friction sensitivity + live-book availability`**：
1. 用前一轮保存下来的 `latest_baseline_pairs.csv` 作为同一候选图，贪心构造 `degree cap = 1 / 2 / 3 / baseline` 四种 pair-book；
2. 在 `recent_price_panel.csv` 的最近单窗口上，用相同 `z-entry=1, cross-0 exit, 4-bar max hold` 的近似框架，分别测试：
   - `maker-heavy = 4 bps round-trip`
   - `mixed = 8 bps round-trip`
   - `taker-heavy = 12 bps round-trip`
3. 额外做了一个更严格的“当前窗口 live-book availability”检查：把最新单窗口重新跑一遍上一轮写明的 stronger admission（`mr_t <= -2.5` 且 `16 <= half_life <= 192`），看当前是否还能自然生成可交易候选图。

产物目录：
- `reports/artifacts/optimization_loop/rank203_p2_exit_20260328_0005_fixedpairs/`
- `reports/artifacts/optimization_loop/rank203_p2_exit_20260328_0005/`

## 本轮真正改变系统认知的新结论
这条线现在**还不够诚实地升入 `P3 / paper trade`**。真正的阻塞点不是“degree2 和 degree3 谁更好看”，而是：

> **一旦切到更现实的 friction / live-book 口径，当前这条策略还没有一个可稳定存在、成本后仍为正的候选 pair graph。**

因此这轮不能把它继续开放式留在 `P2`，也不能硬推 `P3`；最诚实的出口是：

> **把对象从“可直接 paper 的 pair-book strategy”一次性 re-scope 回 `P1`：只保留为“更窄资产簇 + 更硬 admission + maker-first 执行”的 pair-book governance 模块，再等下一次重新定义 spec 后重开。**

## 证据收口
### 1) 五窗口历史结论仍成立，但它只说明“结构上最像 production 的是 capped-overlap”
上一轮 `P2` 起点没有被推翻：
- `degree2_1h`：gross `+12.08%`、net `+0.18%`、正 net 窗口 `3/5`
- `matching_1h`：net `-1.57%`
- `baseline_1h`：net `-3.03%`

这说明：
- `capped-overlap` 的方向比 `full non-overlap` 更对；
- 但它离“足够值得立刻 paper trade”本来就只差一层 execution realism 验证，而不是已经稳过线。

### 2) 本轮 friction sensitivity：`degree cap 1/2/3` 在最近单窗口全部成本后转负
基于 `latest_baseline_pairs.csv` 生成的候选图，在最近单窗口上的近似复验结果如下：

- `degree1`
  - 4 bps：net `-0.92%`
  - 8 bps：net `-1.51%`
  - 12 bps：net `-2.10%`
- `degree2`
  - 4 bps：net `-1.36%`
  - 8 bps：net `-1.95%`
  - 12 bps：net `-2.54%`
- `degree3`
  - 4 bps：net `-1.20%`
  - 8 bps：net `-1.73%`
  - 12 bps：net `-2.27%`
- `baseline`
  - 4 bps：net `-1.03%`
  - 8 bps：net `-1.56%`
  - 12 bps：net `-2.10%`

读法：
- `degree3` 在这个最新单窗口里反而比 `degree2` 略抗打，但**所有版本都成本后为负**；
- 这说明上一轮那个薄薄的 `degree2` 净正优势，还不足以支撑直接进入 paper；
- 换句话说，当前这条线还停留在“pair-book structure 值得保留”，而不是“execution-ready strategy 已成型”。

### 3) 更严格的 current-window admission 甚至给不出 live candidate graph
用最近单窗口重新跑与上一轮一致的 stronger admission（`mr_t <= -2.5`、`16 <= half_life <= 192`）时：
- `candidate_pairs = 0`

这不是在证明策略永远无效，而是在说明一个更关键的 admission honesty 问题：
- **当前 spec 还不能稳定地产生一个当下可交易的候选图；**
- 如果连当前窗口都无法自然给出 live candidates，就不该把它包装成已经足够进入 `paper trade` 的策略。

## 为什么不是 `promote_P3`
因为 `P3` 的前提应该是：
- 候选图在现实 friction 下仍有足够净 alpha；
- 没有明显执行致命伤；
- 至少已经能定义出一个可持续刷新的 live spec。

而本轮补的 axis 正好显示：
1. 最新单窗口里，`degree1/2/3/baseline` 在 `4/8/12 bps` 下全部净负；
2. 同口径 stronger admission 在当前窗口没有生成任何 candidate pairs；
3. 所以当前还缺的不是“再补一点一般性稳定性”，而是一个更窄、更诚实的重新定义后的 spec。

## 为什么不是直接 `drop_to_background`
因为这条线并没有出现明确 fatal flaw：
- 去集中度 / pair-book governance 的结构价值是真实的；
- 五窗口结果也确实说明 overlap cap 比教条式 full matching 更像正方向。

因此最合理的出口不是判死，而是**一次性的明确 re-scope**：
- 从“16-token 全宇宙、想直接进入 paper 的 pair-book strategy”
- 改成“更窄资产簇 + 更硬 admission + maker-first execution”的 `P1` 重新定义对象。

## 唯一明确的 re-scope 方向
本轮允许的唯一一次 `P2->P1` 回退，必须写成具体改法，而不是“再看看”。这里的单一明确方向是：

> **把 `Rank 203` 重写为一个更窄的 pair-book governance 模块：先只保留在最近仍能稳定成图的核心相关簇（例如 `ETH/SOL/LTC` 及其直接邻居），显式要求 stronger admission 能在当前窗口生成非空候选图，并把执行假设收紧为 `maker-first`；在这之前，不再把它当作已接近 paper launch 的成品策略。**

这属于 policy 允许的 `scope + execution assumption` 一次性重定义。

## 正式 verdict
`Rank 203 / graph-matching pairbook mean-reversion`：`one-time P2->P1 re-scope`

一句话：
> **上一轮证明了 capped-overlap pair-book 是对的方向，但本轮现实 friction / live-book axis 说明它还没有一个当前可持续存在、成本后仍为正的 live candidate graph；因此不能升 `P3`，应一次性退回 `P1`，把对象收窄成“更窄资产簇 + 更硬 admission + maker-first execution”的 re-scoped pair-book 模块。**

## 对 runtime 的写回语义
- `Active P2 slot`：当前 admission 出口决策已完成；`Rank 203` 不再保留在 active P2
- `Background pool`：记录该对象本轮不是 fatal drop，而是带着明确 re-scope 方向退出前排
- `cycle_plan[1]`：写成 `done`

## 一句话 result（用于 state / cycle_plan）
`Rank 203：capped-overlap 的结构优势仍成立，但最新 execution-realism 轴显示当前窗口下 `degree cap 1/2/3` 在 maker-heavy 到 mixed friction 全部净负，且 stronger admission 甚至生成不了非空 live candidate graph；因此这条线本轮不能升 P3，应一次性从 P2 回到 P1，重写成“更窄资产簇 + 更硬 admission + maker-first execution”的 re-scope 对象。`
