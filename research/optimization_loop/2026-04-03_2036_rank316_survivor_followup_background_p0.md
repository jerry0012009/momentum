# Rank 316 / symmetric tiered maker ladder × inventory-skew / external hedge — survivor follow-up verdict = background/P0

- Time: 2026-04-03 20:36 UTC
- Target: `Rank 316 / symmetric tiered maker ladder × inventory-skew / external hedge`
- Action: survivor one-shot follow-up / minimal maker honesty check
- Verdict: `background/P0`

## Why this changes runtime truth
`Rank 316` 的唯一 survivor follow-up 已经用掉，而且这次补的不是又一轮静态 ladder 观察，而是最小诚实口径下的 **maker fill proxy + short-horizon adverse-selection** 检查。结果说明：这条对象目前能确认的是“有明显分层挂单结构”，但还不能确认“在 majors 上存在足够厚、可复制、能穿过真实 frictions 的 maker pocket”。因此它不该继续占用前排 survivor 资源，最诚实的收口是直接回到 `background/P0`。

## What was checked
本轮直接用 Hyperliquid 公共 API 对 `BTC / ETH / SOL` 做了统一最小壳抽样：
- 采样窗口：约 `70s`
- 频率：约每 `2s`
- 数据：`l2Book` + `recentTrades`
- 口径：
  1. 记录当时 top-of-book `bid / ask / mid`
  2. 若下一采样窗口出现能打到该价位的成交，则把它记成一次最小 fill proxy
  3. 观察 fill 后约 `6s / 14s` 的 mid 位置，估算 `gross half-spread` 是否还能留存

产物：`reports/artifacts/optimization_loop/2026-04-03_2034_rank316_maker_honesty_probe.json`

## Probe readout
### BTC
- 平均 top-of-book spread：约 `0.15 bps`
- fill proxy 次数：买侧 `20`，卖侧 `19`
- 平均 gross half-spread：约 `0.075 bps`
- fill 后 `6s / 14s` 的 edge 基本只剩同量级的极薄残留

### ETH
- 平均 top-of-book spread：约 `0.49 bps`
- fill proxy 次数：买侧 `8`，卖侧 `5`
- 平均 gross half-spread：约 `0.244 bps`
- 买侧 fill 后 `6s` edge 只剩约 `0.061 bps`，到 `14s` 基本接近 `0`

### SOL
- 平均 top-of-book spread：约 `0.13 bps`
- fill proxy 次数：买侧 `4`，卖侧 `5`
- 平均 gross half-spread：约 `0.062 bps`
- 卖侧 fill 后 `6s / 14s` 已出现负 edge，说明轻微 adverse selection 就足以吃掉这层薄边

## Honest interpretation
这轮不能把结果往“maker 策略一定不行”夸大；但它已经足够回答 bot2 给的 survivor 问题：

> 在当前能公开、快速、诚实复现的最小口径下，`Rank 316` 还没有给出“gross spread capture - fee - short-horizon adverse selection - refresh/cancel friction 后仍有可存活 pocket”的正面证据。

更关键的是：
1. 这次补的是它唯一一次 survivor follow-up；
2. 新证据并没有把对象推进到 `P2`；
3. 若继续留在前排，就会变成再次重复同一条 maker honesty 证据轴。

而从这次 probe 看，当前可直接观察到的 majors top-of-book gross edge 本身就已经非常薄：
- `BTC / SOL` 大致只在 `0.06~0.08 bps`
- `ETH` 也只是 `0.24 bps` 左右，且买侧很快被 adverse selection 吃回接近 `0`

在还没计入：
- 真正 queue position / 未成交风险
- quote refresh / cancel 频率成本
- inventory skew 带来的非对称 fill
- 外部 hedge 的 taker 成本
之前，就已经看不到足够厚的 pocket 余量。对当前 desk 的最小 paper/replication admission 来说，这不够诚实。

## Runtime consequence
因此本轮把 `Rank 316` 直接从 survivor 收口到 `background/P0`，而不是再写一次 `keep_P1` 或勉强升 `P2`。如果未来要重新打开这条线，前提应是出现新的、独立于这次 evidence axis 的证据——例如真实 fill / queue-position 数据或更明确的 venue-specific rebate pocket——而不是再做一轮同口径的静态 maker probe。

## Result sentence
`Rank 316`：唯一 survivor follow-up 已完成；当前公开可复现的 `BTC/ETH/SOL` 最小 maker honesty probe 只看到极薄的 top-of-book gross edge，且在 short-horizon adverse selection 与未计入的 refresh/hedge friction 前已缺乏足够余量，因此不诚实支持 `promote_P2`，本轮直接收口到 `background/P0`。
