# Rank 295 — survivor follow-up blocked — public ETH exchange inflow proxy unavailable

- 时间：2026-04-02 18:23 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`Rank 295 / ETH exchange inflow shock × 1~6h bearish drift`
- 本轮动作：survivor 唯一一次 follow-up
- 结论：`blocked:missing-single-decisive-blocker`

## 本轮只回答的问题
按 `BOT2_BOT3_STATE.md` 的当前 front-slot 指令，本轮本来要直接回答：在**公开可近似**的交易所净流入事件定义下，这条 `ETH inflow shock short` 在 `15m` 执行壳的 `4/8/12/24` bar 窗口里，是否仍保留 reader-facing 的 bearish drift、覆盖度、MAE/MFE 与 `4+2 bps` 成本后 expectancy，从而决定它是 `升 P2` 还是 `survivor 预算用尽后回 background/P0`。

## 本轮实际检查到的唯一决定性 blocker
本机当前 workspace 里**没有**可直接复核的公开 `ETH -> exchange` 聚合事件流，也没有已经整理好的交易所标签地址集 / 事件样本表 / inflow proxy 构建脚本，因而无法在本轮内诚实地产出 state 要求的那组 reader-facing 指标。

本轮核对到的事实只有两类：
1. **论文证据在本地齐全**：`tmp/onchain_flows_2411.06327.txt` 明确保留了 paper-level 方向结论——`ETH net inflows negatively predict ETH returns`，且覆盖 `1/2/3/4/6h` 全部 intraday horizon；
2. **可执行的公开 proxy 仍停留在叙事层**：
   - `research/quant_digests/2026-03-25_0805_eth-exchange-netflow-intraday-short-alpha.md`
   - `research/quant_digests/2026-04-01_0452_eth-usdt-exchange-flow-pressure-alpha.md`
   - `research/quant_digests/2026-04-02_1707_eth-exchange-inflow-event-short-alpha.md`
   都写了“可用公开标签近似复现”，但 workspace 中没有对应的已落库 proxy 数据、标签资产或可直接跑出的事件研究脚本。

换句话说：**当前缺的不是又一轮论文阅读，也不是继续改写 digest，而是唯一一块决定 admission 的 runtime 证据——可复核的 public-proxy event series。** 在这块东西不存在的前提下，硬写 `升 P2` 或 `回 P0` 都会变成拿论文 headline 冒充 clean-room follow-up。

## 为什么本轮不能硬判 P2 / P0
- 升 `P2` 不诚实：因为还没回答最关键的 desk 问题——公开 proxy 下的事件数量、后续 `15m` 路径、MAE/MFE、以及 `4+2 bps` 成本后 expectancy。
- 直接回 `background/P0` 也不诚实：因为否决理由目前不是“公开 proxy 已证伪”，而是“公开 proxy 在当前 runtime 里还不存在”。
- policy 允许这种情况写成 `blocked`：当前小点目标明确，但其前置的唯一决定性输入（public inflow proxy / label dataset）不成立，因此本轮应收口为 `blocked:missing-single-decisive-blocker`，而不是伪造出口结论。

## 本轮改变系统认知的一句话
`Rank 295` 的 survivor follow-up 目前**不是被新增价格证据否掉**，而是被唯一决定性 blocker 卡住：当前 runtime 里没有可复核的公开 `ETH exchange inflow` 事件流/标签资产，所以还不能诚实回答它在 `15m` 的 `4/8/12/24` bar 成本后是否足以升 `P2`。
