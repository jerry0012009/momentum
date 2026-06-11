# Rank 320 — Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit survivor follow-up：promote_P2

- Time: 2026-04-04 01:20 UTC
- Target: `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- Action type: `P1 survivor` decisive follow-up
- Verdict: `promote_P2`

## 结论
`Rank 320` 已经不只是“单资产趋势母板待分辨”，而是可以诚实确认存在一条清楚、可复现、post-cost 仍站得住的 `asset / timeframe admission` 路径：在同一套 `Wilder RSI breakout + EMA200/ADX/volume allow + fast RSI-45 exit` 壳下，`ETH/SOL 5m` 与 `BTC/ETH/SOL 15m` 都给出正收益、受控回撤与大于 1 的 profit factor，因此本轮 survivor follow-up 应直接把对象从 `P1` 升到 `Active P2`，进入正式 admission，而不是再把它收口成“共享 fast-exit / trend-allow 组件”。

## 本轮 decisive evidence
### 1. 原版慢退出在 short-cycle 上失败，说明问题主要在 exit，不在 alpha 主语
现有 portability probe 显示：
- 原版近似 `RSI exit = 30` 在 `5m` 上三币全负：`BTC -48.0% / ETH -41.9% / SOL -43.1%`
- `15m` 也偏弱：`BTC -12.4% / ETH -12.7% / SOL -4.7%`

这一步已经把“repo 只是 4h 样本内包装、短周期根本不成立”的解释大幅削弱了；真正被证伪的是**慢退出搬运**，不是 `RSI breakout continuation` 主语本体。

### 2. 一旦把 exit 提快到 RSI-45，同一策略壳在多资产 / 多 timeframe 上出现一致可用路径
#### 5m faster-exit probe
- `BTCUSDT 5m, entry 62 / exit 45`: `+35.1%`, max DD `-7.61%`, PF `1.76`
- `ETHUSDT 5m, entry 58 / exit 45`: `+90.8%`, max DD `-4.40%`, PF `3.21`
- `SOLUSDT 5m, entry 58 / exit 45`: `+61.2%`, max DD `-8.15%`, PF `2.57`

#### 15m threshold sweep
- `BTCUSDT 15m, entry 55 / exit 45`: `+27.2%`, max DD `-3.65%`, PF `5.97`
- `ETHUSDT 15m, entry 60 / exit 45`: `+48.2%`, max DD `-3.94%`, PF `6.55`
- `SOLUSDT 15m, entry 65 / exit 45`: `+45.8%`, max DD `-4.65%`, PF `3.59`

这里最关键的不是“统一最佳参数”，而是：
- 同一个 raw alpha 主语在 `BTC/ETH/SOL` 三币都能找到诚实的正收益 admission；
- `5m` 与 `15m` 两层都成立；
- 最优差异主要体现在 `entry threshold` 微调，而 `fast exit = 45` 这一结构在各资产 / timeframe 上都保持稳定方向一致。

这已经满足 survivor follow-up 要回答的唯一问题：**它存在清楚的 asset/timeframe admission 路径，而不是只能作为局部组件残留。**

## 为什么这一步是 promote_P2，而不是继续留在 P1
`P1 survivor` 只有一次最小 decisive follow-up 预算；本轮已经拿到会改变层级的答案：
1. 不是单一币种偶然命中，而是 `BTC/ETH/SOL` 都有 post-cost 正路径；
2. 不是单一 timeframe 脆弱 lucky hit，而是 `5m/15m` 都有可承认版本；
3. 不是只剩“把 fast exit 当共享零件复用”，而是完整 `entry / allow / exit / sizing / cost` 壳仍然成立。

因此继续停留 `P1` 只会变成低杠杆重复；更合规的动作是直接升到 `P2`，让下一轮 admission 去回答更正式的 5 维问题：`effectiveness / cross-asset stability / time stability / parameter stability / honesty`。

## 为什么还不是 P3
虽然当前已经证明它值得进入 `P2 admission`，但还没到直接 `paper launch`：
- 目前证据窗口仍短，主要覆盖 `2026-01-01 ~ 2026-04-03`；
- 参数最优点在不同资产 / timeframe 间有差异，尚未完成系统性的 parameter-stability 收口；
- 还没把 friction realism 梯度、镜像 short sleeve、或更长时间稳定性正式并入 admission。

所以诚实结论是：**足以升 P2，但还不足以直接升 P3。**

## 本轮写回 runtime 的系统认知变化
- `Rank 320` 已用完唯一一次 `P1 survivor` follow-up，且结论为 `promote_P2`。
- 当前系统不再把它视为“待判断是否只剩组件价值的 survivor”；而是把它视为当前唯一 `Active P2`。
- 下一轮若继续研究它，必须按 `P2 admission` 逻辑收口，而不是再做第二次 survivor。

## Reader-facing 一句话
`Rank 320` 已经证明自己不只是一个可拆零件的 RSI 趋势母板：在 `BTC/ETH/SOL × 5m/15m` 上都存在诚实可复现的 fast-exit admission 路径，因此本轮从 `P1 survivor` 直接升到 `Active P2`。