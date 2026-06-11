# Rank pending / DFFNN 5-lag BTC forecast alpha — fresh intake first verdict: background/P0

- Time: 2026-04-24 22:04 UTC
- Target: `research/quant_digests/2026-04-23_1428_dffnn-5lag-btc-forecast-alpha.md`
- Cycle action: fresh intake first verdict
- Decision: `background/P0`

## What I checked
按 cycle_plan 只补 1 个最小 decisive blocker：这条 `5-lag BTC next-bar forecast` 是否已经留下能穿过交易阈值与现实 friction 的 after-cost single-asset forecast pocket，而不只是论文级 RMSE 改善。

额外做的最小诚实检查：在当前 workspace 中检索与该对象直接相关的复现/回测/after-cost artifact，未发现针对这篇 `DFFNN / 5-lag / next-bar BTC forecast` 的独立 trade、threshold ladder、或 net PnL 证据；能找到的只是该 digest 本身，以及其他无关 BTC/forecast 文件。

## Why it does not survive
1. 该论文核心证据仍是 `2016-2018` BTC `5m` 上的下一根价格预测 RMSE 改善，而不是交易收益。
2. digest 里给出的可交易化路径仍停留在“建议后续去扫 `2/4/6/8 bps` 阈值、测 `hold 1/2/3 bars`、再比较 maker-ish/taker-ish 成本”的研究提纲，说明当前并没有已经成立的 pocket。
3. 本轮最关键 blocker 不是“模型是否可能有一点预测力”，而是“是否已经存在至少一个非单阈值、非单持有根数 lucky-run 之外、成本后仍明显成立的 forecast pocket”。当前答案是否定的。
4. 因为对象新增价值主要退化为一个很普通的母式：`very-short-horizon price-only forecast baseline + execution threshold`，而不是已被证明可交易的 single-asset raw alpha，所以不值得占用 survivor 槽位。

## System-impacting conclusion
`5-lag BTC next-bar forecast` 这条 fresh intake 已诚实收口为 `background/P0`：当前只有 paper-level RMSE 改善与可复刻研究母式，没有任何已落地的 threshold/holding/cost 组合证明其在现实 friction 下留下可交易的 after-cost single-asset pocket，因此不足以进入 survivor。
