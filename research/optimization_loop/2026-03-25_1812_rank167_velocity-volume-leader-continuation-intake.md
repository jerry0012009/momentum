# Rank 167 / velocity-volume leader continuation fresh intake 首判

- 时间：2026-03-25 18:12 UTC
- 执行轮次：bot3 auto 13m
- 对象：`research/quant_digests/2026-03-25_1730_velocity-volume-leader-continuation.md`
- 本轮动作：只做 fresh intake 最小首判（`park` vs `keep_P1`）

## 结论
**Rank 167：`dynamic threshold leader continuation + 二段式入场` 这条短周期动量 raw alpha 首判通过，记为 `keep_P1`，因为它已经把 regime-aware signal、二段式 entry、风险约束与最小实验口径写成了可直接复现的完整骨架；当前真正未决的只是不知道成本后 edge 是否足够厚、以及 edge 是否集中在少数 regime 桶里。**

## 为什么不是直接 park
- 这不是空泛“涨得快就追”的口号，而是明确限定为：**按 BTC 波动状态切换 `5m/10m/15m` lookback 与阈值，再用 `volume_ratio + RSI` 过滤后做 leader continuation**。
- digest 已经把交易闭环写完整：候选信号、`50% + 50%` 二段式入场、`-2%` 止损、`1.5*ATR` 止盈、`+3%` 后保本、总风险与板块集中度上限都已给出。
- 最小实验口径也足够清晰，能直接在 `Binance spot / perp` 的公开 K 线上先做 honest baseline，不需要先补社交数据或复杂板块 overlay。
- 这条线和当前 desk 主频匹配：alpha 本体在 `5m/15m`，执行可自然下沉到 `1m/3m maker-first / TWAP`，不是一条只能停留在周频叙事里的泛 trend 想法。

## 为什么还不能直接升 P2
- 现有材料的强项是**工程骨架完整**，不是**admission 级证据完整**；还缺成本后净收益、regime 分桶稳定性、以及参数扰动后的生存性验证。
- 最容易出错的地方是把 sparse continuation edge 做成 late-chasing；若净边只在极少数高波动桶里存在，或一上 taker cost 就变薄，就还不配直接占用 `Active P2`。
- 所以下一步唯一高杠杆 follow-up 很明确：先验证这条线在目标 `5m/15m` 口径下，扣除基础 round-trip cost 后是否仍有稳定的 post-entry drift / net bps，并确认 edge 是否主要集中在少数明确 regime。 

## 对 runtime 的直接影响
- 该对象获得正式身份 `Rank 167`。
- 本轮只完成 fresh intake 首判，结论为 `keep_P1`；不顺手执行 survivor follow-up，也不提前占用 `Active P2 slot`。
- 下一轮若继续推进，合法动作应是把 `Rank 167 / velocity-volume leader continuation` 写入 `Surviving candidate slot`，并只做一次最小 decisive follow-up：先回答“扣除基础交易成本后，这条 leader continuation 在明确 regime 分桶里是否仍保留足够厚的 net edge，值得进 `P2 admission`”。
