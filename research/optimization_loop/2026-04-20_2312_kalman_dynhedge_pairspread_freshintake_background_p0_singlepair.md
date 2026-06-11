# Kalman dynamic hedge ratio × rolling z-score spread fade：fresh intake first verdict -> background/P0

- 时间：2026-04-20 23:12 UTC
- 对象：`research/quant_digests/2026-04-20_1216_kalman-dynhedge-pair-spreadfade-alpha.md`
- 执行动作：按 cycle_plan 对这条 fresh intake 做 first verdict；只检查一个最小 decisive blocker——在统一双腿 `8bps`、hedge-ratio 漂移允许、并要求不是单 pair 集中后，是否仍保留可复制 after-cost pocket。

## 本轮读取的最小证据
直接使用 digest 已落地的 artifact：
- `reports/artifacts/quant_digests/2026-04-20_kalman_pair_spreadfade_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-20_kalman_pair_spreadfade_probe_event_horizon.csv`

代表性结果：
- `XRPUSDT/DOGEUSDT`：`187` 笔，`gross≈+11.04bps/trade`，`net_8bps≈+3.04bps/trade`
- `BTCUSDT/ETHUSDT`：`325` 笔，`gross≈+2.11bps/trade`，`net_8bps≈-5.89bps/trade`
- `SOLUSDT/AVAXUSDT`：`317` 笔，`gross≈+2.83bps/trade`，`net_8bps≈-5.17bps/trade`
- `LINKUSDT/LTCUSDT`：`295` 笔，`gross≈+3.20bps/trade`，`net_8bps≈-4.80bps/trade`
- `XRPUSDT/ADAUSDT`：`178` 笔，`gross≈+4.22bps/trade`，`net_8bps≈-3.78bps/trade`

## 结论
这条 raw alpha 没有通过本轮要求的“非单 pair、费后仍成立”的 fresh intake 首判。

原因不是 repo 没有思路，而是：
1. 统一双腿 `8bps` 后，代表性 pair 里只有 `XRP/DOGE` 保住明确正 net；
2. `BTC/ETH` 这类更稳、更像 benchmark 的 pair 费后明显为负，说明 edge 不足以跨到更可承接的主流 pair；
3. 其他 alt pair 虽有 gross pocket，但整体仍被成本吃掉，不能证明存在“不是单 pair lucky run”的可复制 after-cost basket；
4. 因而当前最小 blocker 已经被直接回答：它不是一个可先保留为 survivor 的广义 pair-admission alpha，而更像单一 `XRP/DOGE` 阶段性 pocket。

## 本轮 verdict
- `background/P0`

## 会改变系统认知的一句话
`Kalman dynamic hedge ratio × rolling z-score spread fade` 在统一双腿 `8bps` 与非单 pair 约束下没有保住可复制 after-cost pocket；正边际基本只剩 `XRP/DOGE` 单 pair，故本轮 fresh intake 直接收口 `background/P0`。

## 对 runtime 的影响
- 不分配新 Rank
- 不进入 `Surviving candidate slot`
- `Fresh intake slot` 的最新结果更新为该对象已直接收口 `background/P0`
- `cycle_plan` 第 2 项标记为 `done`
