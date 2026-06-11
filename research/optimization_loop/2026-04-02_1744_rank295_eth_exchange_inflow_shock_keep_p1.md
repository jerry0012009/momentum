# Rank 295 — ETH exchange inflow shock × 1~6h bearish drift — fresh intake first verdict = keep_P1

- 时间：2026-04-02 17:44 UTC
- 对象：`research/quant_digests/2026-04-02_1707_eth-exchange-inflow-event-short-alpha.md`
- 层级动作：`fresh intake -> keep_P1 -> Surviving candidate slot`
- 正式 Rank：`295`

## 本轮结论
这条 `ETH exchange inflow shock × 1~6h bearish drift` 不是停留在论文 headline 的方向性描述，而是已经具备独立事件驱动 raw-alpha 主语、明确事件时钟/入场/持有/风控骨架，以及可直接执行的最小 cost-aware clean-room path，因此 fresh intake first verdict 记为 `keep_P1`，进入 survivor 唯一 follow-up。

## 为什么不是 P0
- 主语清楚：`ETH 净流入交易所 -> 后续 1~6h ETH 偏弱`，可直接映射成单资产做空事件策略。
- 事件时钟清楚：按小时聚合 exchange net inflow，整点确认上一小时事件，再转入 `15m` / `5m` 执行。
- 策略骨架已给出：`zscore 阈值 + 别追太晚 veto + USDT inflow veto + 1~3h fixed hold + 简单 adverse exit`。
- clean-room 最小实验路径已给出：先做 `15m` event study，直接上 friction ladder，看 `4/8/12/24` bar 累计收益、事件数、MAE/MFE 与成本后 expectancy。

## 为什么还不直接升 P2
- 当前 edge 仍强依赖 `exchange label mapping` 与链上事件时间戳口径；这两点若近似得不好，短窗可交易性会明显失真。
- 论文给的是 1~6h 预测关系，但对 desk 真正要用的 `15m shell + 5m timing` 还没做 clean-room 诚实验证。
- 因此本轮最诚实的位置是 `keep_P1`，而不是跳过 survivor 直接宣称已够 `P2 admission`。

## survivor 唯一 follow-up 应该回答的问题
只做一次最便宜但能改变层级的检查：
- 用公开标签近似事件流，验证 `ETH inflow shock short` 在 `15m` 的 `4/8/12/24` bar 窗口下，经过 `4+2 bps` 级别成本后是否仍保留正 expectancy；
- 同时确认 edge 是否主要来自少数极端日，还是在可接受样本覆盖下仍有 reader-facing 的 post-event bearish drift。

## 写回 runtime 的系统认知
- `Rank 295` 已获得正式身份。
- 当前对象合法进入 `Surviving candidate slot`。
- 下一步不是继续泛泛读论文，而是做一次最小 clean-room 事件研究来决定 `P2` 还是 `background/P0`。
