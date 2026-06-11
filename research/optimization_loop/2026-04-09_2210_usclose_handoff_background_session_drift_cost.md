# 2026-04-09 22:10 UTC — US close pocket handoff fresh intake first verdict

## 执行对象
- `research/quant_digests/2026-04-08_2356_usclose-pocket-crossmarket-overnight-alpha.md`
- 角色：`Fresh intake slot` 的当前唯一 pending 小点

## 本轮要回答的问题
`US close pocket impulse × next-session handoff continuation` 在当前 crypto `15m` top-liquid follower universe 里，是否已经足够像一个**可独立兑现的 cross-market handoff pocket**，而不是只在单一 `BTC 19:30-20:00 UTC` proxy 下偶然成立、且一上最小 taker 成本就被压平的薄时段效应。

## 本轮最小 honesty 子检查
直接用本地 `Binance USDⓈ-M 15m perp cache`（`BTC/ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`，各 `120d`）做一个最便宜但足以改变结论的 drift/cost 检查：

1. 对 `BTC` 固定候选 leader slot：`18:30 / 18:45 / 19:00 / 19:15 / 19:30 / 19:45 / 20:00 UTC`
2. 每个 slot 都用该 `30m` pocket return 当 leader signal
3. 只保留 `|signal|` 位于样本前 `1/3` 的强事件
4. follower 为 `ETH/SOL/XRP/ADA/DOGE/LINK/AVAX`
5. 统计 next `1 / 2 / 4` 根 `15m` 的同向 signed mean return，并看 `2-bar` 在 `4/6/8 bps` round-turn 下是否仍为正

## 结果
| leader slot | 事件数 | next 1 bar | next 2 bars | next 4 bars | 2-bar 正资产比 | 2-bar 净值（4bps） | 2-bar 净值（6bps） | 2-bar 净值（8bps） |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 19:30 | 40 | -3.76 bps | **+7.37 bps** | -2.36 bps | 0.475 | +3.37 bps | +1.37 bps | **-0.63 bps** |
| 19:00 | 40 | -1.07 bps | +3.90 bps | +9.29 bps | 0.536 | -0.10 bps | -2.10 bps | -4.10 bps |
| 18:45 | 40 | -4.40 bps | +2.41 bps | -2.83 bps | 0.500 | -1.59 bps | -3.59 bps | -5.59 bps |
| 20:00 | 40 | -7.50 bps | +1.43 bps | -24.16 bps | 0.468 | -2.57 bps | -4.57 bps | -6.57 bps |
| 19:15 | 40 | -1.63 bps | -3.30 bps | +0.88 bps | 0.421 | -7.30 bps | -9.30 bps | -11.30 bps |
| 18:30 | 40 | -8.91 bps | -7.17 bps | -10.66 bps | 0.418 | -11.17 bps | -13.17 bps | -15.16 bps |
| 19:45 | 40 | -0.80 bps | -13.58 bps | -6.61 bps | 0.386 | -17.58 bps | -19.58 bps | -21.57 bps |

## first-verdict 口径
这条 intake 当前**不保留为 P1**，直接收口到 `Background / P0`。决定性的原因有三条：

1. **edge 过度依赖单一时钟定义**
   - 只有 `19:30` 这个 proxy slot 的 `2 x 15m` continuation 明显为正；前后相邻 slot 大多迅速塌掉，甚至转负。
   - 这说明现在看到的不是一个稳固的“US close handoff continuation pocket”，而更像单一时钟切法下的窄窗口偶然项。

2. **2-bar pocket 虽是最强窗口，但强度不够覆盖现实 taker 成本**
   - `19:30` 的 `2-bar` 毛值只有 `+7.37 bps`；若按最小 round-turn `8 bps`，已经转成 `-0.63 bps`。
   - 换句话说，`2 x 15m` 确实是唯一还像样的 pocket，但它本身已经太薄，不足以支撑 desk 直接当 raw alpha pocket 保留前排。

3. **截面一致性也不够强**
   - 即便在最优 `19:30` slot，`2-bar` 的平均正资产比也只有 `0.475`，并不是那种 follower 普遍同向扩散的干净 cross-market 传播。

## 结论
- first verdict：`background / P0`
- 不分配 Rank
- 不进入 `Surviving candidate slot`

## 会改变系统认知的一句话
`US close pocket impulse × next-session handoff continuation` 在当前 crypto `15m` top-liquid followers 上只在单一 `BTC 19:30-20:00 UTC` proxy 的 `2 x 15m` pocket 里勉强显正，前后相邻 slot 很快塌掉且最小 `8 bps` round-turn 后转负，因此它更像脆弱的时钟切片效应，不是可独立兑现的 cross-market handoff alpha，fresh intake first verdict 收口为 `background / P0`。
