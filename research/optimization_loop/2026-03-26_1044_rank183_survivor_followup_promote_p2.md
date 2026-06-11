# Rank 183 / cbeth-eth-rolling-fair-basis-mr — survivor follow-up honesty gate
- 时间：2026-03-26 10:44 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 本轮角色：bot3 对 survivor 做唯一一次 decisive follow-up，只回答 `CBETH spot + ETH perp` 在真实 `cost / funding / depth honesty` 下是否还值得留在前排

## 结论
**单一收口 verdict：`promote_P2`。**

更具体地说，值得升入 `Active P2` 的不是泛 `liquid staking basis` 叙事，而是已经被现实约束收窄后的这条对象：

> **`CBETH spot + ETH perp` 的 `15m rolling fair-basis MR` 仍保有 admission-level 诚实净边；但 `5m` 档在真实成本/深度下过薄，不应继续当作同一对象的 production 主体。**

## 本轮补的 honesty 证据
### 1) 成本梯度：15m 还能穿，5m 不再漂亮
沿用 intake 产物中的最小回放结果：
- `15m / z=1.5`：`mean_trade ≈ +20.36 bps`（在 **pair RT = 20 bps** 后仍为正）
- `15m / z=2.0`：`mean_trade ≈ +29.86 bps`
- `5m / z=1.5`：`mean_trade ≈ +9.57 bps`
- `5m / z=1.25`：`mean_trade ≈ +7.53 bps`

这意味着：
- 若把真实执行再往上加几 bps，**15m 的 1.5σ / 2.0σ pocket 仍有余量**；
- **5m 基本只剩 close-to-close 幻觉空间**，一旦把真实 spot 冲击、ETH perp taker、funding 和安全余量都加进去，几乎没有理由继续把它当前排主对象。

### 2) 当前可见深度：CBETH 这条腿对小中号仓位不是直接 fatal flaw
2026-03-26 10:43 UTC 抓取 Coinbase `CBETH-USD` level-2 盘口：
- top-of-book spread 约 **4.1 bps**
- 买入 `CBETH`：
  - `2k USD` 冲击约 **2.6 bps**
  - `5k USD` 冲击约 **3.6 bps**
  - `10k USD` 冲击约 **4.8 bps**
  - `25k USD` 冲击约 **7.7 bps**
- 卖出 `CBETH`：
  - `2k USD` 冲击约 **2.9 bps**
  - `5k USD` 冲击约 **3.0 bps**
  - `10k USD` 冲击约 **3.0 bps**
  - `25k USD` 冲击约 **5.0 bps**

翻成人话：**CBETH 并不深，但也没有薄到小中号（约 `2k~10k USD`）名义一碰就死。** 这条线的 honest 版本显然应默认从小仓位起步，而不是预设成大容量 stat-arb。

### 3) funding：存在，但不是当前最主要 kill switch
抓取 Binance `ETHUSDT` 最近 200 条 funding：
- `|funding|` 平均约 **0.48 bps / 8h**
- 折算约 **0.72 bps / 12h**、**1.45 bps / 24h**

而 intake 结果里当前 pocket 的中位持有时长基本只有 **1 根 bar**：
- `15m` 的 median hold = **1 bar**
- `5m` 的 median hold = **1 bar**

所以对这条短持有 basis MR 来说，**funding 是要记账的现实摩擦，但还不是决定生死的主矛盾；真正决定对象还能不能留前排的，是 `15m` 是否能在更保守执行口径下继续保有净边，以及 `5m` 是否应该被剔除。**

## 为什么这轮是 promote_P2，不是继续 keep_P1 或直接 park
- 不是继续 `keep_P1`：policy 明确 survivor 只允许这唯一一次 decisive follow-up；现在已经拿到会改变层级的答案，不能再拖。
- 不是 `park_to_background`：因为 `15m` pocket 在 `20 bps pair RT` 下本来就已有正余量，而当前可见 CBETH 深度 + ETH funding 也**没有**构成“这条线根本不可交易”的致命否决。
- 是 `promote_P2`：因为现在最诚实的前排对象已经收窄清楚——**保留 `15m`，基本放弃把 `5m` 也当 production 候选的幻想**。这足够进入下一层 admission，去补更正式的 `execution sizing / venue realism / slow-anchor spec lock`。

## 本轮改变系统认知的一句话
`Rank 183` 不是“泛 LSD basis 候选”；它已被诚实收窄为 **可小仓位执行的 `CBETH spot + ETH perp` 15m rolling fair-basis MR**，因此应从 survivor 升入 `Active P2`，而不是继续停留在 P1 或直接回背景池。

## 产物
- intake 复用：
  - `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/summary.csv`
  - `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_5m/summary.csv`
- 本轮新增 honesty gate：
  - `reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`
