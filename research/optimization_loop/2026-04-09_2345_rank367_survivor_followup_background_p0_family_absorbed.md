# Rank 367 survivor follow-up：post-cost funding+basis dislocation × delta-neutral carry admission 不升 P2，回到 background/P0

- 时间：2026-04-09 23:45 UTC
- 对象：`Rank 367 / post-cost funding+basis dislocation × delta-neutral carry admission`
- 轮次角色：bot3 当前轮 `Surviving candidate` 的唯一一次 decisive follow-up
- 结论：`background / P0`

## 本轮只回答一个问题
这条 `future_net_return_bps` carry-admission 层，在当前 runtime 可用证据下，是否已经足够证明自己相对 `always-on carry` 与简单 `funding>threshold & basis_z>threshold` baseline 有独立 admission 增量，并可诚实推进到 `P2`？

本轮答案：**还不够，且应直接收口，不再占用前排。**

## 本轮实际做的最小 decisive 检查
1. 重读 `2026-04-09_2146_postcost-funding-basis-deltaneutral-alpha.md` 与 `Rank 367` first verdict，确认这条对象的新增值确实是：
   - 把目标直接写成 `future_net_return_bps`；
   - 默认主语限定为 `short perp + long spot`；
   - 显式采用 `execution_delay_bars = 1` 与四腿 post-cost。
2. 回查同家族旧 runtime 记录：`Rank 310`、`Rank 349`、以及 `BTC 单 venue spot-perp carry × 负 funding 成本阈值 veto / re-entry` 的家族吸收结论。
3. 对照当前 cycle_plan 的成功条件，检查现有材料里是否真的出现了会改层级的新增证据：
   - `BTC/ETH/SOL` 或 liquid majors 的并列 portability 结果；
   - 相对 `always-on carry` / 简单 threshold baseline 的直接 A/B；
   - `spot-leg capacity / borrow asymmetry / delayed-confirmation realism` 中是否已有被压实后的 admission 级回答。

## 本轮新结论
`Rank 367` 不应升到 `P2`，而应在这次 survivor follow-up 用尽后直接退回 `background / P0`。

关键原因不是这条线“完全没价值”，而是：

1. **它仍没有把 cycle_plan 要求的 admission 句子压成结果，只是把 carry 家族写得更诚实。**
   当前 digest 和 first verdict 能确认的是：
   - 标签比旧 funding carry 家族更 desk-friendly；
   - 延迟执行与四腿成本是显式的；
   - borrow 风险大的反向腿没有被偷偷默认启用。
   但这些主要是在回答“这个 repo 有没有把自己写假”，不是在回答“它相对 baseline 是否已证明有独立 admission 增量”。

2. **当前没有出现会改变层级的 cross-asset / baseline A/B 证据。**
   cycle_plan 要求的关键句子是：
   - 在 `BTC/ETH/SOL` 或至少 liquid majors 上；
   - 用 `15m/1h` decision cadence；
   - 相对 `always-on carry` 与简单 threshold baseline；
   - 是否提高 `post-cost bps/trade` 与 `tradeable rate`。
   现有材料没有给出这组 reader-facing 结果；仍停在“最小实验应该这样做”的提纲。

3. **这条对象与旧的 same-venue delta-neutral carry / funding+basis 家族重叠很深，但没有给出足够强的新 family-breaking 证据。**
   - `Rank 310` 已证明 `funding carry gate` 是可独立描述的主语，但 survivor follow-up 因缺少 `BTC/ETH/SOL × 更真实 friction` 证据而回到 `background/P0`；
   - `Rank 349` 已把对象推进到 `funding+basis+persistence+sign-flip/liquidity gate`，但 survivor follow-up 仍因没有压成 `BTC/ETH/SOL × 5m/15m × after-cost` 的可迁移净增量而收口回 `background/P0`；
   - 当前 `Rank 367` 的新增值主要是把 admission layer 改写成 `future_net_return_bps` 标签。这个写法更诚实，但在没有直接 A/B 与跨资产结果前，还不足以逃离旧家族“写法更完整、证据仍未过 admission”的同一收口逻辑。

4. **不存在新的单一 decisive blocker 被清除，反而仍保留旧 blocker 形态：缺少唯一能改层级的对照结果。**
   这轮最便宜、最能改判的检查不是再争论 borrow 文档是否诚实，而是看是否已经出现 `baseline -> admission layer` 的硬对照结果。当前答案是否定的。

## 为什么这轮不能继续 keep_P1 或升 P2
按 policy，survivor 只允许 **1 次** 最小 decisive follow-up。

这次 follow-up 已经把唯一高杠杆问题问完：
- 如果出现 `majors × after-cost × baseline A/B` 的 admission 级结果，可以升 `P2`；
- 如果没有，就不该继续把“写法更诚实”当作前排理由反复拖延。

`Rank 367` 当前正落在第二种情况，因此本轮最诚实的动作就是直接收口。

## 对 runtime 的直接影响
- `Rank 367` 不升 `P2`
- `Surviving candidate slot` 用尽唯一 follow-up 后清空
- 对象退回 `Background pool / P0`
- 当前前排主动作回到后续 `fresh intake`

## 一句话结果（写回 state 用）
`Rank 367` 的唯一 survivor follow-up 已诚实收口：当前证据只证明它把 same-venue funding+basis carry 家族写成了更诚实的 `future_net_return_bps` admission layer，但仍未给出相对 `always-on carry / 简单 threshold` 在 `BTC/ETH/SOL` 或 liquid majors 上的 after-cost admission 增量，因此不升 `P2`，直接退回 `background / P0`。
