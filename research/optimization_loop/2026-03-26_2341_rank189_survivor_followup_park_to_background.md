# Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation — survivor follow-up park_to_background

- Time: 2026-03-26 23:41 UTC
- Target: `Rank 189 / current-funding richest-vs-cheapest 4h crowding continuation`
- Action: survivor 唯一一次 cheap decisive follow-up
- Verdict: `park_to_background`

## 本轮只回答的问题
把 `current funding richest-vs-cheapest 4h` 做最小去偏后，这条正 sign 还是不是一个值得升 `P2` 的独立对象？

本轮没有重开整个 funding screener，也没有继续补开放式 `keep_P1`。只做最便宜、最决定性的诚实检查：

1. **成熟/高流动性子集检查**：只看当前 artifact 里 `72h ADV >= $1m` 且价格过滤通过的可交易子集；
2. **热度/暴露代理检查**：把最“热”的币先当成伪像来源处理，观察 rich-minus-cheap sign 是否还站得住；
3. **集中度检查**：看 rich leg 是否只是少数热点单名反复撑起，而不是更广义的横截面现象。

## 新证据
### 1) 能做完整 follow-up 的成熟高流动性窗口非常窄
用现成 artifact 的 `funding_data_all_coins.csv` + `ohlcv_data_main.csv` 重建最小检查后，满足：
- `72h ADV >= $1m`
- 有足够历史去算 4h forward return / 24h-72h 热度代理 / 基本暴露代理

的窗口只剩 **25 个 hourly rebalance 点**，可交易 universe 平均约 **10 个币**。

这本身已经改变系统认知：

> 当前 intake 里的正 pocket，并不是一个在“成熟、高流动性、可长期 desk 化”的宽横截面上已经站稳的对象；它更像依赖样本边缘币池与近期热点分布的短样本现象。

### 2) 在这个更诚实的成熟子集里，sign 直接翻负
对这 25 个可诚实检查的 rebalance 点，按同样 `richest-vs-cheapest / 4h hold` 思路做最小复算：

- baseline equal-weight `top-5 rich vs bottom-5 cheap`
- 平均 **price PnL ≈ -26.79 bps / 4h**
- 平均 **funding cashflow ≈ -3.95 bps / 4h**
- 扣 8 bps round-trip 后 **net ≈ -38.74 bps / 4h**
- 胜率约 **36%**

也就是说，一旦把视角收缩到更接近 desk 真正能长期承载的成熟币子集，这条线不只是变弱，而是**直接转负**。

### 3) rich leg 明显集中在少数热点单名，不像稳健横截面 family
在这些可检查窗口里，rich leg 反复出现的主要是：
- `SUI`（24 次）
- `ZEC`（22 次）
- `NEAR`（22 次）
- `HYPE`（22 次）
- `ETH`（20 次）

cheap leg 反复出现的则是：
- `VVV`（25 次）
- `PAXG`（23 次）
- `XRP`（22 次）
- `BTC`（21 次）
- `SOL`（21 次）

翻成人话：这不是一个已经表现出“广义 funding 横截面普适有效”的对象，更像是**近期少数热点/冷门名册之间的相对强弱碰巧与 funding 极值同向**。

## 为什么这次结论是 park，而不是 promote_P2
`Rank 189` 通过 intake 时的保留理由，是“这条线值得一轮唯一 cheap follow-up 去排除高 beta / 热门币 / 上新币暴露伪像”。

这轮 follow-up 给出的答案是：

- **成熟高流动性子集不支持它；**
- **rich/cheap 两腿的成员高度集中；**
- **当前证据不足以把它诚实地解释成独立 alpha，而不是热点名册暴露。**

因此它不满足升 `P2` 的条件。

## 为什么也不做新的 re-scope
这一步是 survivor 的唯一 follow-up，不是 `P2 -> P1` re-scope 轮。

本轮虽然看到了“热点名册/近期拥挤单名暴露”这个问题，但它还没有收敛成一个唯一、足够清晰、足以立刻重写成新对象的单轴定义。现在就硬改成什么“只做热点币 funding continuation”或“只做上新币 funding crowding”都还太像顺着噪音编新故事。

所以最诚实的动作不是继续拖着 open question，而是：

> 先把 `Rank 189` 收口为 `park_to_background`。

## Result sentence
`Rank 189` 的 survivor 唯一 follow-up 已诚实收口为 `park_to_background`：当前 `current-funding richest-vs-cheapest 4h` 的正 pocket 在更成熟的高流动性子集里无法保持，rich leg 又明显集中在少数热点单名，因此它暂时更像热点暴露伪像，而不是足够独立、值得升 `P2` 的 funding 横截面 alpha。 
