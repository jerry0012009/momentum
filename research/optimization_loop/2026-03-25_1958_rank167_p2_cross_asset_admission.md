# Rank 167 / velocity-volume leader continuation P2 cross-asset admission

- 时间：2026-03-25 19:58 UTC
- 执行轮次：bot3 auto 13m
- 对象：`Rank 167 / velocity-volume leader continuation`
- 本轮动作：只做 `effectiveness / cross-asset` admission 小闭环，回答“这条 dynamic-threshold leader continuation 在目标 Binance 短周期口径下，成本后正净边是否能跨资产保留，而不是只靠少数币或单一 pocket 撑住”

## 结论
**Rank 167：`effectiveness / cross-asset` admission 给出偏正面但不算通吃的结论——在与上一轮一致的 90 天 Binance spot 极简 honest baseline 下，10 个样本币里有 7 个在 `8bps round-trip` 成本后仍为正，整体加权平均约 `+23.1 bps/trade`，说明这条线不会一扩资产就直接塌掉；但净边并不均匀，`ADA/XRP/SOL` 三币合计贡献了约 `81%` 的总净收益，而 `BTC/ETH/DOGE` 为负，因此它通过了“不是只靠单一 pocket 存活”的 admission 底线，却还没强到可以仅凭这一维直接升 `P3`。**

## 本轮怎么做的
- 保持和 survivor 轮一致的极简 baseline，不改 alpha 本体，只把结果拆到单币层：
  - `BTC 14d ATR%` 分桶：`high > 5`，`mid 3~5`，`low < 3`
  - 信号：`5m/10m/15m` 动态 lookback + 对应阈值（`3% / 2% / 1.5%`）
  - 过滤：`volume_ratio > 1.5`、`RSI < 75`
  - 入场：下一根开盘先上 `50%`，未来 `1~3` 根若突破 signal-bar high 且 RSI 未过热，再补 `50%`
  - 出场：`-2%` 固定止损、`1.5*ATR` 止盈、`+3%` 后移 breakeven、按 regime 给 `16~48` 根 time stop
- 数据：Binance 公共现货 `5m` K 线
- universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC`
- 窗口：最近约 90 天

## 单币拆解（`8bps round-trip`）
- 正值 7 币：
  - `BNBUSDT`：约 `+133.3 bps/trade`（2 笔）
  - `XRPUSDT`：约 `+64.5 bps/trade`（7 笔）
  - `LINKUSDT`：约 `+41.8 bps/trade`（7 笔）
  - `SOLUSDT`：约 `+39.5 bps/trade`（10 笔）
  - `LTCUSDT`：约 `+38.8 bps/trade`（5 笔）
  - `ADAUSDT`：约 `+34.8 bps/trade`（14 笔）
  - `AVAXUSDT`：约 `+17.7 bps/trade`（7 笔）
- 负值 3 币：
  - `DOGEUSDT`：约 `-5.7 bps/trade`（12 笔）
  - `ETHUSDT`：约 `-56.2 bps/trade`（6 笔）
  - `BTCUSDT`：约 `-165.6 bps/trade`（1 笔）

## admission 含义
- **好消息：** 这不是“离开某一个幸运币就完全失效”的假 alpha。正值资产数量是多数，且不是只剩一两个极端高波动 pocket 在硬撑；把 universe 从单币扩到 10 币后，整体净边仍为正。
- **限制：** 它也不是“核心大币普适 continuation”。当前正贡献更像集中在一组更适合短周期 leader continuation 的 alt（尤其 `ADA/XRP/SOL`），而不是 `BTC/ETH` 这种更厚、更快被套利掉的核心资产。
- **因此本轮 verdict：** 这一维 **不构成 `P2` 阻断**，但它把后续 admission 的真正问题收窄了：下一步更该验证 `time / parameter` 是否同样保留方向一致性，而不是继续重复问“是否跨资产一扩就死”。

## 对 runtime 的直接影响
- `Rank 167` 保持在 `Active P2 slot`，没有因为 cross-asset admission 失败而回退。
- `p2_consecutive_keep_p2` 应增至 `1`：本轮没有层级变化，但产出了新的 admission 结论。
- 下一轮合法主动作应切到 `time / parameter` admission；若那一维也偏正面，则后续应尽快进入 `honesty / execution realism` 收口与 `P3 / P1 / P0` 出口判断。
