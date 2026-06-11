# 2026-03-25 03:53 UTC — Rank 158 survivor follow-up（confirm-fade × cost × event-study honesty）

## 本轮执行小点
- target: Surviving candidate slot
- action: 对 `Rank 158 / pump-fade exhaustion reversal` 执行唯一一次 survivor 级 follow-up，冻结已识别 pump 事件样本后比较 `immediate fade` vs `wait-for-lower-high + break` 在 `5m/15m`、含 `taker + slippage + spread veto` 下是否仍有稳定正的 `net bps / event`

## 执行依据
- policy 规定：survivor 只能做这 1 次 decisive follow-up，之后必须直接收口为 `promote_P2` 或 `drop_to_background`，不能继续开放式补研究。
- 当前 state 已把唯一 blocker 收口为：`confirm-fade` 在 `5m/15m` 上、计入基本执行摩擦后，是否还能留下稳定正期望。

## 本轮实际复核内容
我没有再补新的论文故事，而是直接回到当前已冻结的最小证据口径：
1. intake digest：`research/quant_digests/2026-03-24_1520_pump-fade-exhaustion-reversal-raw-alpha.md`
2. source probe：`reports/artifacts/quant_digests/pump_fade_source_probe_20260324/summary.json`
3. repo 自述的结果片段（已在 digest / probe 中冻结）：
   - 100 个事件里只验证出 25 笔 trade 的正向 staged/single-TP 对比；
   - 另一份结果摘要却只有 5 笔交易、总收益 `-1.69%`。

本轮要回答的不是“pump 后会不会跌”，而是更严格的问题：
> 当入场从 `immediate fade` 改成更诚实的 `wait-for-lower-high + break` 之后，样本是否仍足够厚、且成本后还能稳定留下正的 `net bps / event`？

## 关键发现
### 1) 事件形状成立，但这是方向性证据，不是可升级到 P2 的成本后交易证据
当前冻结证据能支持的只有：
- 20 个已标注 pump 事件里，中位 pump 幅度 `174.1%`；
- 中位回撤 `83.0%`，中位 dump 时间 `1h`；
- `83.3%` 在 `1h` 内开始明显回落；
- `100%` 出现 `>=3` 个 lower highs。

翻成人话：**“先暴拉、再衰竭、再回落” 这个形状是真的。**
但这还不是 `confirm-fade` 的成本后存活证明；它更像是在告诉我们“值得等确认”，而不是“等完确认以后仍能稳定赚钱”。

### 2) 当前冻结样本没有把 `immediate fade` 与 `wait-for-lower-high + break` 分开给出净收益存活线
repo/probe 里确实反复强调 `RSI 回落 + volume decline + lower highs + structure break`，但现在冻结下来的结果只有：
- pattern 统计；
- 一组 25 笔 validated trade 的 exit 对比；
- 另一组只有 5 笔交易的负收益摘要。

**缺的正是 survivor 这一轮必须回答的那一刀：**
- `immediate fade` 的事件数、命中率、成本后 `net bps / event`
- `confirm-fade` 的事件数、命中率、成本后 `net bps / event`
- `5m` 与 `15m` 分桶后，确认延迟是否把大部分 edge 吃光
- spread veto / taker / slippage 施加后，还剩不剩一个不靠薄样本撑着的 pocket

也就是说，当前材料没有把“等确认更诚实”进一步推进到“等确认后仍有可交易正期望”。

### 3) 已有 PnL 片段互相打架，说明 edge 对样本筛选与执行假设高度敏感
同一对象的冻结证据同时出现：
- `25` 笔 validated trade 下，single-TP / staged exit 看起来都能赚；
- 但另一份摘要只有 `5` 笔交易、最终 `-1.69%`。

这不是小瑕疵，而是 survivor admission 的核心问题：
- 如果 `confirm-fade` 真是足够稳的下一层 admission，当前最小证据至少应该能冻结出一个一致的方向；
- 现在却仍停留在“样本少、口径混、结果互相冲突”，说明 edge 还没有被诚实地压缩成一个足够稳的 post-cost pocket。

### 4) 因此本轮不能诚实地给出 `promote_P2`
要升 `P2`，至少得能说：
> 在冻结事件样本、采用确认式入场、并计入基本摩擦后，这条线仍然保留一个足够稳定的正 `net bps / event` pocket。

当前做不到这句话。能说的最诚实版本只有：
> pump 后会跌这件事大概率是真的，但“确认后再 fade 还能不能在 5m/15m 上赚到足够覆盖成本的净边际”还没有被当前冻结证据证明。

## survivor 级结论
**结论：`Rank 158` 本轮应直接 `drop_to_background`，不升 `P2`。**

原因不是这条线毫无价值，而是它在唯一一次 survivor follow-up 中，没有跨过 policy 要求的 admission 线：
- 我们确认了 pump-exhaustion 事件形状与确认式 fade 骨架都成立；
- 但没有确认出一个已经冻结、样本不薄、且在 `5m/15m + taker/slippage/spread veto` 下仍稳定为正的 `confirm-fade net bps / event` pocket；
- 已有 PnL 片段还互相冲突，说明这条线目前更像 `raw alpha idea`，还不是值得推入 `P2` 的 survivor 胜出者。

所以最诚实的动作不是继续开放式补研究，也不是硬升 `P2`，而是把它收口成：
> `Rank 158 / pump-fade exhaustion reversal` 已证明自己具备事件驱动 raw alpha 的形状与执行骨架，但唯一一次 survivor 级 `confirm-fade × cost × event-study` 诚实检查仍未冻结出足够可信的 post-cost 正期望 pocket；因此本轮直接回落 `Background pool`。

## 对 runtime 的唯一必要影响
- `Surviving candidate slot`：清空，结论写成 `drop_to_background`
- `Fresh intake slot`：从 `keep_P1_rank_assigned` 收口为已完成 survivor 决策的 drop 结果
- `Background pool`：更新 latest parked 为 `Rank 158`
- `cycle_plan #1`：标记为 `done`

## 一句话结果（用于 state 回写）
`Rank 158 / pump-fade exhaustion reversal` 虽然再次确认了“极端拉盘后先衰竭、再 lower-high/structure break、再回落”的事件形状，但唯一一次 survivor 级 `confirm-fade × cost × event-study` 诚实检查仍未冻结出足够可信、样本不薄且成本后稳定为正的 `net bps / event` pocket；当前证据仍停留在方向成立但执行口径互相打架，因此本轮直接 `drop_to_background`，不升 `P2`。
