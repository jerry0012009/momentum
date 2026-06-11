# Rank 200 / BTC weekday-hour sparse short schedule — survivor 唯一 follow-up promote P2
- 时间：2026-03-27 19:27 UTC
- 对象：`Rank 200 / BTC weekday-hour sparse short schedule`
- 本轮角色：bot3 对 survivor 做唯一一次 decisive follow-up，只回答这条 sparse `weekday-hour -> short BTC` 事件时钟在更诚实的 `cost / rolling refresh / spot-perp / hold perturbation` 口径下，是否仍值得升入 `P2 admission`

## 结论
**单一收口 verdict：`promote_P2`。**

更具体地说，值得进入下一层 admission 的不是泛泛的 `calendar anomaly`，而是这条已经收窄清楚的对象：

> **滚动识别 BTC `weekday-hour` 最弱 5 个桶，在桶结束后做 `2~6h short`；其中 `4h short` 仍是当前最稳的主轴，且 spot / perp 同向。**

## 本轮补的 survivor 证据
本轮新增产物目录：
- `reports/artifacts/optimization/rank200_survivor_followup_20260327_1927/`

### 1) 成本梯度没有把主轴打掉
按 `2024-03-27 ~ 2025-09-28` 训练、`2025-09-28 ~ 2026-03-27` 测试，固定选 bottom-5 弱桶：

- **Spot / static / hold=4h**
  - `4 bps`：`+15.00 bps/trade`
  - `8 bps`：`+11.00 bps/trade`
  - `12 bps`：`+7.00 bps/trade`
- **Perp / static / hold=4h**
  - `4 bps`：`+15.12 bps/trade`
  - `8 bps`：`+11.12 bps/trade`
  - `12 bps`：`+7.12 bps/trade`

翻成人话：这条线不是只在极低摩擦下才勉强为正；就算把 round-trip 提到 `12 bps`，`4h short` 主轴在 spot / perp 上都还留有净后空间。

### 2) rolling refresh 反而让它更像真实 scheduler，而不是训练期偶然命中的静态桶
把弱桶改成**每月滚动重算过去 365 天**后，`4h short` 没有塌，反而更厚：

- **Spot / monthly refresh / hold=4h**
  - `4 bps`：`+30.36 bps/trade`
  - `8 bps`：`+26.36 bps/trade`
  - `12 bps`：`+22.36 bps/trade`
- **Perp / monthly refresh / hold=4h**
  - `4 bps`：`+33.05 bps/trade`
  - `8 bps`：`+29.05 bps/trade`
  - `12 bps`：`+25.05 bps/trade`

而且滚动窗口里反复出现的弱桶并不完全随机，`Thu 19:00`、`Fri 00:00`、`Thu 13:00` 一类桶持续反复入选，说明它更像一个**可滚动更新的稀疏 schedule family**，不是一次性挑出来的后验最佳桶。

### 3) 轻微持有窗扰动没有把方向打回去
同样看 monthly refresh：

- **Spot**
  - `hold=2h @ 8bps`：`+12.88 bps/trade`
  - `hold=4h @ 8bps`：`+26.36 bps/trade`
  - `hold=6h @ 8bps`：`+23.32 bps/trade`
- **Perp**
  - `hold=2h @ 8bps`：`+9.76 bps/trade`
  - `hold=4h @ 8bps`：`+29.05 bps/trade`
  - `hold=6h @ 8bps`：`+24.12 bps/trade`

这说明它不是“只有 4h 一个针尖参数能赚钱”；`2h` 虽然 thinner，但仍为正，`6h` 也没有反向塌掉，因此 survivor 这一步要求的最小 parameter honesty 已经够了。

### 4) spot / perp 口径同向，说明它不只是某个单 venue close-to-close 幻觉
无论用 static 还是 monthly refresh，spot 与 perp 的方向、厚度排序都大致一致：
- `4h` 明显优于 `2h`
- `4h` 与 `6h` 都能穿过 `8~12bps`
- perp 没有因为合约口径就把 edge 打没

这足够回答 survivor 轮唯一关键问题：**它更像可独立 paper 的 sparse scheduler，而不是只能给别的策略当 overlay 的时间袋。**

## 为什么这轮是 promote_P2，不是 park_to_background
- 不是 `park_to_background`：因为本轮要求验证的 4 个 honesty 方向——成本梯度、rolling refresh、spot/perp、轻微持有窗扰动——都没有出现 fatal breakdown；相反都支持同一条 `BTC sparse short schedule` 主轴。
- 不是继续 `keep_P1`：policy 明确 survivor 只允许这唯一一次 follow-up；现在已经拿到会改变层级的答案，不能继续把它留在 P1。
- 是 `promote_P2`：因为对象已经收窄到足够具体、足够可测的 desk 候选——**BTC `weekday-hour` bottom-5 弱桶结束后 `4h short`，monthly refresh 为默认版本，`2h/6h` 为参数邻近对照。** 下一层该补的是正式 admission 的 `time stability / exact execution realism / scheduler wiring potential`，而不是再讨论它是不是只是“有点意思”。

## 下一层 P2 admission 应围绕的五项
1. `effectiveness / expected return`：补更完整的 OOS path、回撤与 active-time 占用，而不只看 avg bps/trade
2. `cross-asset stability`：回答它是否应严格保留为 BTC-only，而不是硬扩到 ETH/SOL
3. `time stability`：拉更长历史并拆年度/季度，确认不是 2025-2026 单段现象
4. `parameter stability`：继续检查 `k=3/5`、refresh 频率、entry delay 是否仍保留主轴
5. `honesty / execution realism`：若要进 paper，需锁定真实入口（spot 还是 perp）、成交时点与 funding/slippage 记账口径

## 本轮改变系统认知的一句话
`Rank 200 / BTC weekday-hour sparse short schedule` 用完 survivor 唯一 follow-up 后，已经不只是“值得再看一下”的稀疏时间袋；在 `spot+perp / 4-12bps / 2-6h / monthly refresh` 下它仍保持同向净后空间，因此应从 P1 升入 `P2 admission`。
