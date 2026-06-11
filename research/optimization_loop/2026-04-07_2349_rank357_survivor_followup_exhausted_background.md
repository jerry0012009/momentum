# Rank 357 — survivor 唯一 follow-up 收口：不升 P2，keep_P1 exhausted -> background

- 时间：2026-04-07 23:49 UTC
- 对象：`Rank 357 / pattern-shortlist × next-hour drift`
- 轮次角色：bot3 surviving candidate 唯一一次 decisive follow-up
- 结论：`keep_P1 exhausted -> background`

## 本轮判定
`Rank 357` 作为 fresh intake 已经成立：它确实把 `Harami / Hikkake / Three White Soldiers / Three Black Crows` 压成了一个独立于 breakout / trend-shell / event overlay 的单资产 raw-alpha 主语。但把它从 `P1 survivor` 升到 `P2` 还差关键一截：当前材料只清楚说明了 **paper shortlist + 持有壳 + 大致成本假设**，还没有把 **pattern 识别规则的 clean-room 口径** 与 **相对简单 return/trend baseline 的最小增量信息** 压到足以进入 admission 的程度。

因此，这次 survivor 唯一 follow-up 的诚实出口不是 `promote_P2`，而是：**对象保留为一个成立过的 P1 线索，但本轮预算已用尽，正式移回 background pool。**

## 为什么这一步不能升 P2
1. **pattern parser 口径仍不稳**
   - 当前 digest 明确说可以用 `TA-Lib 或自写规则` 识别 pattern；这恰好说明 parser 本身还没有被固定。
   - 对于 `Harami / Hikkake / Three White Soldiers / Three Black Crows` 这类多 bar 结构，实体/影线阈值、inside/outside bar 边界、是否允许极小实体等，都会直接改变触发频率和样本构成。
   - 在 parser 尚未压成单一 clean-room 口径前，把它推进到 `P2 admission` 会把 admission 轮浪费在定义漂移上。

2. **还没压出相对简单 baseline 的最小独立增量**
   - 目前能确认的是：论文说这些 pattern 对 next-hour drift 有统计信息，且高量/高波时更强。
   - 但对 desk 而言，升级到 `P2` 至少要先知道它是不是明显优于更简单的壳：例如 `上一小时 return sign / ROC / EMA slope / breakout continuation` 这类轻量 baseline。
   - 现有材料没有把“pattern 本身”与“只是趋势延续或波动放大”清楚剥离。

3. **执行壳有了，但 admission 主问题还没被压成最小 decisive blocker**
   - `15m 持有 4 bar`、`5m 持有 12 bar`、下一根开盘入场、先按 `4 bps fee + 1 bp slippage` 每边，这些已经足够支持 first verdict。
   - 但它们本身不构成 `P2`。`P2` 需要的是：对象已经值得花 admission 预算去做 effect / cross-asset / time / parameter / honesty 五维判断。
   - 当前最像 blocker 的恰恰是“pattern 定义是否可稳定复刻、且是否相对简单 baseline 仍有增量”。这不是 admission 后半段问题，而是 admission 前的主语完整性问题。

## 为什么也不是直接 P0
- 它不是空泛蜡烛图概念；已经有明确 shortlist、固定预测窗口、清楚的 desk 迁移壳。
- 所以它保留为 `background pool` 中的有效线索是合理的；只是**这一次 survivor 预算不足以把它诚实抬进 P2**。

## runtime 影响
- `Surviving candidate slot`：`Rank 357` 的唯一 follow-up 已消费完，当前槽位清空。
- `Background pool`：新增停放 `Rank 357`，理由为“独立 intake 成立，但 parser 口径与 baseline 增量尚未压清，不足以升 P2”。
- `cycle_plan[1]`：本轮写成 `done`，结果为 `Rank 357：survivor follow-up 收口，未压清 parser/baseline 增量，keep_P1 exhausted -> background`。

## 一句话 result
`Rank 357：survivor 唯一 follow-up 已收口；对象虽是成立的独立 intake，但 parser 口径与相对简单 baseline 的增量仍未压清，因此不升 P2，改为 keep_P1 exhausted -> background。`
