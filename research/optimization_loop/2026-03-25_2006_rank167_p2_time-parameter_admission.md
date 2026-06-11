# Rank 167 / velocity-volume leader continuation P2 time-parameter admission

- 时间：2026-03-25 20:06 UTC
- 执行轮次：bot3 auto 13m
- 对象：`Rank 167 / velocity-volume leader continuation`
- 本轮动作：只做 `time / parameter` admission 小闭环，回答“这条线在非单窗、非单参数点下是否仍保留方向一致的成本后生存性，还是只是某组 lookback/threshold 恰好有效”

## 结论
**Rank 167：`time / parameter` admission 只能给出 `keep_P2`，还不足以靠这一维直接升 `P3`。好消息是它并不是单一参数点幻觉——在同一套 90 天 Binance spot 极简 baseline 下，把动态阈值整体做 `±0.3pct` 轻扰动、并把 `volume_ratio` 过滤在 `1.3 / 1.5 / 1.7` 之间来回拨，9 组参数在 `8bps round-trip` 成本后全部仍为正，整体中位数约 `+28.3 bps/trade`；但坏消息是时间稳定性明显不够平，90 天切成三个 30 天窗后，样本 `net bps/trade` 约为 `-11.1 / +64.1 / +24.5`，而且最近 30 天基准参数实际上只剩 `1` 笔触发，放松阈值后也不过 `3` 笔且均值约 `-6.1 bps/trade`，更严格参数则直接变成 `0` 笔，所以当前更像**阶段性 pocket + 触发稀疏**，还不是可以放心 paper-launch 的非单窗稳定线。**

## 本轮怎么做的
- 保持和前两轮一致的极简 honest baseline，不换 alpha 本体：
  - `BTC 14d ATR%` 分桶：`high > 5`，`mid 3~5`，`low < 3`
  - 信号：`5m/10m/15m` 动态 lookback + 对应阈值（baseline 为 `3.0% / 2.0% / 1.5%`）
  - 过滤：`volume_ratio > 1.5`、`RSI < 75`
  - 入场：下一根开盘先上 `50%`，未来 `1~3` 根若突破 signal-bar high 且 RSI 未过热，再补 `50%`
  - 出场：`-2%` 固定止损、`1.5*ATR` 止盈、`+3%` 后移 breakeven、按 regime 给 `16~48` 根 time stop
- 数据：Binance 公共现货 `5m` K 线
- universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC`
- 窗口：最近约 90 天

## time stability：不是连续三窗同向
基准参数（`threshold shift = 0`，`volume_ratio > 1.5`）下：
- 全样本：`66` 笔，`net ≈ +25.9 bps/trade`，胜率约 `72.7%`
- 前 30 天窗：`33` 笔，`net ≈ -11.1 bps/trade`
- 中间 30 天窗：`32` 笔，`net ≈ +64.1 bps/trade`
- 最近 30 天窗：仅 `1` 笔，`net ≈ +24.5 bps/trade`

翻成人话：**这条线不是“全程都烂”，但也绝不是“每个时间窗都差不多能跑”。** 真正的问题不是 90 天总均值，而是最近一个月已经接近“信号旱季”；若要上线 paper trade，这种稀疏度会直接变成 deployability 问题。

## parameter stability：轻扰动后方向还在，但 trade-off 很尖
在 `8bps round-trip` 下，把动态阈值整体平移 `-0.3 / 0 / +0.3 pct`，并把 `volume_ratio` cut 设为 `1.3 / 1.5 / 1.7`：
- 共 `9/9` 组参数为正
- 参数网格中位数约 `+28.3 bps/trade`
- 较松参数（`shift=-0.3`）会把样本放大到 `119~142` 笔，但均值掉到约 `+13.6 ~ +14.7 bps/trade`
- 基准附近（`shift=0`）约 `58~72` 笔，均值约 `+25.9 ~ +28.8 bps/trade`
- 更严参数（`shift=+0.3`）只剩 `29~38` 笔，但均值抬到约 `+42.7 ~ +62.4 bps/trade`

这说明它**不是某一个 lookback / threshold 恰好踩中 lucky point**；但同样也说明它是很典型的 sparse continuation：门槛一放松，trade count 上来但单笔厚度迅速变薄；门槛一收紧，单笔变漂亮但样本掉得很快。

## recency 检查：最近 30 天并不稳
把同样的 9 组参数只看最近 30 天：
- baseline（`shift=0`）各组都只有 `1` 笔
- 较松参数（`shift=-0.3`）能扩到 `3` 笔，但 `net ≈ -6.1 bps/trade`
- 更严参数（`shift=+0.3`）直接 `0` 笔

所以当前真正阻断它直接升 `P3` 的，不是“参数一动就全死”，而是**最近可部署样本太稀薄**：想增加触发，就会把最近一窗打成略负；想保厚度，就几乎没单可跑。

## admission 含义
- **偏正面的部分：** 它通过了“不是单点参数幻觉”的检查；parameter neighborhood 没有一碰就翻负。
- **偏负面的部分：** time stability 明显不如 cross-asset 那一维，尤其最近 30 天几乎没有可用触发，说明当前证据还不支持把它描述成可稳定上线的短周期 paper-launch 候选。
- **因此本轮 verdict：** `keep_P2`，且 blocker 已被收窄成一个更明确的问题——**不是 alpha 本体完全失效，而是 recency / deployability 还不足以支撑 `P3`。**

## 对 runtime 的直接影响
- `Rank 167` 继续留在 `Active P2 slot`，但 `p2_consecutive_keep_p2` 现在应增至 `2`。
- 按 policy，下一轮不得再给它第三次开放式 `keep_P2` admission；必须进入 `honesty / execution realism` 收口并直接给出 `P3 / one-time P2->P1 re-scope / drop_to_background` 出口判断。
- 若后续要为它争取 `P3`，重点不该再回头问“参数点是不是 lucky”，而应直接回答：**在当前这种最近一窗几乎无信号的条件下，paper trade 是否仍有足够 honest 的部署意义。**
