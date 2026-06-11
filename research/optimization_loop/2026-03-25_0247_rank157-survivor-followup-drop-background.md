# 2026-03-25 02:47 UTC — Rank 157 survivor follow-up（pair-selection × cost × timeout）

## 本轮执行小点
- target: Surviving candidate slot
- action: 对 `Rank 157 / H<0.5 spread-band fast mean-reversion` 执行唯一一次 survivor 级 `pair-selection × cost × timeout` 诚实检查，直接回答是否存在值得进入 `P2` 的 post-cost 正期望 pocket

## 执行依据
- policy 规定：survivor 只能做这 1 次 decisive follow-up，之后必须收口为 `promote_P2` 或 `drop_to_background`，不能继续开放式补研究。
- 当前 state 已把唯一 blocker 收口为：`top-pair pocket` 在现实可接受的 `round-trip cost × timeout` 治理后，是否仍保留稳定正的 post-cost expectancy。

## 本轮实际检查内容
我直接复核 intake 产物 `reports/artifacts/quant_digests/hurst_pairs_antipersistence_probe_20260325_0150/strategy_signals.csv`，按 pair 聚合，并用最小成本生存线做 survivor 级 honesty check：
- pair selection：先看是否存在明显优于全体的 top-pair pocket；
- cost：对每个 pair 施加 `8 / 12 / 16 / 20 bps` round-trip 成本生存线；
- timeout：用 `hours_held` 分布检查收益是否只来自过长持仓，或是否主要集中在 `<=24h / <=48h` 的可接受 holding pocket。

## 关键发现
### 1) 确实存在“更快回归”的 pair pocket，但还不是可信的可交易 pocket
几条 pair 在当前 probe 里表面上很亮：
- `BNBUSDT-SOLUSDT`：37 笔，median hold `22.5h`，`<=48h` 占比 `91.9%`
- `SOLUSDT-LINKUSDT`：64 笔，median hold `12.4h`
- `ADAUSDT-LINKUSDT`：27 笔，median hold `4.25h`
- `ETHUSDT-XRPUSDT`：387 笔，median hold `7.75h`

翻成人话：`H<0.5` 这层 admission 的“快回归”特征确实还在，而且能把一部分 pair 压进相对短的 holding pocket。

### 2) 但当前盈利口径不是可直接宣称“成本后正期望”的可执行口径
当前 CSV 里的收益列是 `gross_spread_pnl`，本质上仍是 spread-unit proxy，不是已经冻结好腿权重、交易成本、滑点/资金费率和 timeout exit 重算后的真实可执行 net return。这个口径下甚至出现了多条 pair 的平均单笔 `gross_spread_pnl` 高达数个百分点到十几个百分点的结果；对短周期 crypto pairs 来说，这更像 proxy 度量，不像可以直接拿去宣称 paper-worthy 的真实成交口径。

也就是说：
- 它足够说明“哪类 pair 回得更快”；
- 但还不够诚实地说明“哪类 pair 在真实 round-trip cost 后仍稳定赚钱”。

### 3) timeout 维度没有形成单一可交易口袋，反而暴露出当前证据还停留在 proxy 层
- `BNBUSDT-SOLUSDT` 的收益并不依赖超长持仓，但样本只有 37 笔；
- `ADAUSDT-LINKUSDT` 与 `BNBUSDT-LINKUSDT` 看起来更快，但样本更薄（27 / 8 笔）；
- `ETHUSDT-XRPUSDT` 样本足够，但 proxy 盈利边际明显变薄，而且一旦把 `>48h` 的尾部长持仓单独看，收益结构并没有形成“唯一明确、可冻结”的 timeout pocket 结论；
- `BTCUSDT-XRPUSDT` 在极低成本（8 bps）下仅仅接近打平，成本一抬就转负。

翻成人话：现在还看不见一个同时满足“样本不薄 + 持仓不拖沓 + proxy 收益不只是口径幻觉”的唯一 decisive pair pocket。

## survivor 级结论
**结论：`Rank 157` 本轮应直接 `drop_to_background`，不升 `P2`。**

原因不是这条线完全没东西，而是它在本轮 survivor follow-up 里没有跨过 policy 要求的那条线：
- 我们确认了 `H<0.5` 确实像论文说的那样更偏向 fast-reversion admission；
- 但没有确认出一个足够诚实、可冻结、能直接说“成本后仍保留稳定正期望”的 top-pair pocket；
- 当前最亮的结果仍高度依赖 proxy spread PnL 口径或薄样本 pair，达不到升级 `P2` 的 admission 起点。

所以最诚实的动作不是继续开放式补研究，也不是硬升 `P2`，而是把它收口成：
> `Rank 157 / H<0.5 spread-band fast mean-reversion` 已证明自己更像一个“pairs 快回归 admission idea”，但在唯一一次 survivor 级 `pair-selection × cost × timeout` 诚实检查后，仍未产出足够可信的 post-cost 可交易 pocket，因此本轮直接回落 `Background pool`。

## 对 runtime 的唯一必要影响
- `Surviving candidate slot`：清空，结论写成 `drop_to_background`
- `Fresh intake slot`：从 `keep_P1_assigned_waiting_survivor_decision` 收口为已完成 survivor 决策的 drop 结果
- `Background pool`：更新 latest parked 为 `Rank 157`
- `cycle_plan #1`：标记为 `done`

## 一句话结果（用于 state 回写）
`Rank 157 / H<0.5 spread-band fast mean-reversion` 虽然再次确认了 `H<0.5` 对 crypto pairs 的快回归筛选价值，但唯一一次 survivor 级 `pair-selection × cost × timeout` 诚实检查仍未给出足够可信的 post-cost 可交易 pocket；当前亮点主要停留在 spread-unit proxy 或薄样本 pair，因此本轮直接 `drop_to_background`，不升 `P2`。
