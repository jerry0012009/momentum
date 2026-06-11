# 别把 liquid staking 只读成慢频 carry：对 short-cycle desk，更该先测的是「rolling basis z-score × WBETHETH fade」这条 relative-value raw alpha
- 时间：2026-04-10 14:22 UTC
- 类型：论文 + 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：liquid staking derivative 相对 ETH 的 basis 偏离会向均值回归，可直接做 `WBETHETH` spread fade
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / liquid-staking / basis / mean-reversion / wbeth / eth / 5m / 15m
- 证据类型：论文证据（OpenAlex abstract + DOI metadata）+ Binance Spot 公共数据 portability probe

## 1. 这次看了什么
看的是 **The Economics of Liquid Staking Derivatives: Basis Determinants and Price Discovery**（2024, *Journal of Futures Markets*）。论文主线是解释 liquid-staking 衍生品的 basis 为何存在、谁在做 price discovery；但对我们 desk 更值钱的，不是慢频市场结构讨论，而是把 **LSD basis 本身** 抽成一条可交易的 short-cycle relative-value raw alpha：当 staking token 相对 ETH 的交易价偏离滚动常态太多时，后面更容易往回收。

## 2. 核心结论
- 这篇东西的 **base alpha** 很清楚：不是情绪、不是 overlay，而是 **staking derivative / underlying 之间的相对价值偏离回归**。
- 真正适合我们 desk 的落点，不是去复刻整篇 paper 的 price-discovery 分解，而是直接拿 Binance 现成可交易的 `WBETHETH` 做 `15m` basis fade。
- 本地用 Binance Spot `WBETHETH` 近约 `180d` 做 portability probe 后，`15m` 上 rolling `192-bar` z-score 的极端偏离有明确回归：
  - quintile 里，最低 z bucket 后续 `4/16/48` bar 约 `+0.52 / +0.98 / +2.08 bps`，最高 z bucket 约 `-0.49 / -0.68 / -0.86 bps`，对应 fade spread 约 `+1.01 / +1.66 / +2.94 bps`；
  - 若只看 `|z| >= 3` 的极端，mean-reversion 对齐后的未来 `1/4/16/48` bar 约 `+1.14 / +1.67 / +2.35 / +2.45 bps`；
  - 做成简单 shell（`entry |z|>=3`，回到 `|z|<=0.5` 或 time-stop）时，`15m max_hold=32` 近样本约 `100` 笔、gross `+5.01 bps/笔`、胜率约 `86%`，粗扣 `4 bps` round-trip 后仍约 `+1.01 bps/笔`。
- 同一思路在 `5m` 也能跑，但更弱：`|z|>=3` 的 aligned future `12-bar` 约 `+1.72 bps`，简单 shell 只有在更长 hold / 更低摩擦下才开始像样，所以当前优先级应是 **`15m > 5m`**。

## 3. 为什么和当前项目有关
这不是泛金融结构知识，而是一条能直接补进素材池的 **relative-value / stat-arb raw alpha**。它和我们当前已积累的 trend、funding、top-trader、pairs 不冲突，反而补了一块此前较少覆盖的 **staking-basis spread**：
- 可独立作为单一 spread 策略；
- 也可作为 “crypto basis / carry / RV” 方向的补充素材；
- 执行上比跨 venue / 跨腿 perp 套利简单，因为 `WBETHETH` 本身就是可直接交易的 pair。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / 均值回归
- 基础 alpha：`WBETHETH` 相对其 rolling mean 的极端 basis 偏离会回归
- regime：优先在 pair 仍有正常成交、rolling std 未塌缩的时段运行
- filter / veto：低成交量、连续单边漂移、Binance staking token 机制变化时停机
- risk / sizing / execution overlay：按 `|z|` 或 rolling std 缩放；优先 maker / 被动挂单；设 time-stop 与机制事件 veto

## 4. 可复刻的最小实验
- 研究假设：`WBETHETH` 的 rolling basis 偏离在 `15m` 上存在可交易的短周期回归。
- 一个可计算定义：
  - `z_t = (close_t - mean(close, 192)) / std(close, 192)`
  - long spread：`z <= -3`
  - short spread：`z >= 3`
  - exit：`|z| <= 0.5` 或 `32 bars` time-stop
- 最小回测切口：Binance Spot `WBETHETH`, `15m`, 近 `180d`。
- 最该先看 2 个指标：
  1. `gross / net bps per trade`（至少做 `2 / 4 / 8 bps` friction ladder）
  2. `成交笔数 + 胜率 + 平均持有 bars`（确认不是只靠少数尾部样本）
- 下一步怎么测：
  1. 先做 `15m` 参数网格：lookback `96/192/288`、entry `2/2.5/3`、exit `0/0.5/1`；
  2. 再比 `direct pair (WBETHETH)` vs `synthetic ratio (WBETHUSDT / ETHUSDT)`，确认是否是 pair 微观结构幻觉；
  3. 最后加成交量 / spread veto，确认能否把 `4 bps` 以上的净值再抬高。

## 5. 风险与保留意见
- 当前论文证据主要来自 abstract + metadata，不是全文逐表复刻；paper 是经济机制与 price discovery 研究，不是现成策略论文。
- `WBETH` 带 staking accrual 与产品机制，basis 不是纯静态 1:1；若 token 规则、赎回路径或交易所激励变化，历史回归参数可能失效。
- 这个 alpha 更像 **低波动、低周转的 RV spread**，不是高爆发单币 directional alpha；若手续费高、只能 taker、或流动性显著恶化，优势会被吃掉。

## 6. 来源
- Milunovich, G., Nguyen, H., & Zheng, X. (2024). *The Economics of Liquid Staking Derivatives: Basis Determinants and Price Discovery*. *Journal of Futures Markets*.
- DOI：`10.1002/fut.22556`
- Readable URL：`https://doi.org/10.1002/fut.22556`
- OpenAlex metadata：`https://api.openalex.org/works/https://doi.org/10.1002/fut.22556`
- Public data：Binance Spot `WBETHETH` klines (`/api/v3/klines`)
- Portability artifacts：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/liquid_staking_basis_probe_summary_2026-04-10.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/liquid_staking_basis_probe_detail_2026-04-10.csv`
