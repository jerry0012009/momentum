# Rank 183 / cbeth-eth-rolling-fair-basis-mr — P2 final honesty / execution realism（promote_P3）
> 更新（2026-04-01）：该对象后续已因 `Coinbase access blocker / venue access difficult` 被记录为 **暂时搁置**，见 `2026-04-01_1230_rank183_coinbase_access_blocker_shelve.md`。本文件保留的是当时研究阶段的 promote 结论，不代表当前仍应继续推进接线。

- 时间：2026-03-26 12:38 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 本轮角色：bot3 只执行当前 `cycle_plan` 中排在最前的 pending 小点；但按 policy，若本小点已经确认对象不存在唯一剩余致命 honesty blocker，就必须立即把对象从 `Active P2` 升入 `Paper launch queue`

## 结论
**单一收口 verdict：`promote_P3`。**

更具体地说：

> `Rank 183 / CBETH spot + ETH perp 15m rolling fair-basis MR` 在当前已收窄的 paper-spec 口径下，**不存在足以阻止进入 paper trade / paper launch queue 的唯一剩余致命 honesty blocker**；因此它不应再停留在开放式 `P2`，而应立即进入 `P3 / Paper launch queue`。

## 本轮只回答的 decisive blocker 问题
上一小点已经把对象收窄成：
- pair：`CBETH spot + ETH perp`
- bar：`15m`
- slow anchor：`7~10d rolling fair basis`
- entry：`|z| >= 2.0` 为主
- exit：`0~0.5`
- execution bandwidth：小中仓位下约 `26~30 bps pair RT`

所以这轮不再重复参数面，而只看：
1. **CBETH 现货深度** 会不会让小中仓位 paper spec 变成伪命题；
2. **ETH perp funding / 执行节奏** 会不会把短持有 mean-reversion edge 吃穿；
3. **持仓节奏** 是否与这条 spec 的真实可执行性冲突到足以一票否决。

## 为什么本轮结论是“没有唯一致命 blocker”
### 1) 小中仓位的 CBETH 现货深度虽然有限，但没有薄到让 paper spec 失真
复用前轮 honesty gate 的 Coinbase `CBETH-USD` level-2：
- top-of-book spread 约 **4.1 bps**
- `2k USD`：冲击约 **2.6~2.9 bps**
- `5k USD`：冲击约 **3.0~3.6 bps**
- `10k USD`：冲击约 **3.0~4.8 bps**
- `25k USD`：冲击约 **5.0~7.7 bps**

这说明最诚实的写法不是“大容量 stat-arb”，而是：

> **把对象限定在 `2k~10k USD` 的小中仓位 paper launch 起步，是现实约束；但这个约束本身不是 fatal flaw。**

也就是说，深度会限制容量叙事，却没有把对象直接打成“连 paper 也不值得做”的伪 edge。

### 2) ETH perp funding 要记账，但对这条短持有 MR 来说不是 kill switch
复用前轮 funding 抽样：
- 最近 200 条 Binance `ETHUSDT` funding 的 `|funding|` 平均约 **0.48 bps / 8h**
- 约等于 **0.72 bps / 12h**、**1.45 bps / 24h**

而当前 paper-spec 的持有分布是：
- median hold = **1 bar（15m）**
- `p90 hold = 5 bars`
- timeout share 近似 **0%**

翻成人话：

> **这条线的主矛盾不是 funding，而是 spot leg 深度 + pair RT 能否控制在 `26~30 bps` 这一现实区间。**

对于以 `15m` 为 bar、绝大多数仓位很快回归的 MR 策略，funding 是应计摩擦，不是当前唯一 decisive blocker。

### 3) “只有 close-to-close，没有历史盘口” 是保留意见，不是当前阶段的一票否决
这条对象仍有两个诚实保留：
- 快检回放主体仍是 **OHLC / close-to-close proxy**；
- 深度证据目前还是 **单次盘口快照 + 保守成本带宽**，不是全历史盘口重放。

但按当前 policy 的门槛，这些更像 **paper launch 之后需要继续盯的 implementation realism 风险**，而不是阻止进入 `P3` 的唯一剩余 fatal flaw。原因很简单：
- 对象已经在更保守的 `30 bps` 口径下通过了 effectiveness / time stability / parameter stability；
- 当前 spec 也没有把自己伪装成大容量、低摩擦、全天候的万能策略；
- 进入的是 **paper launch queue**，不是直接真钱上线。

所以更诚实的动作不是继续把它拖在 `P2`，而是：

> **承认这是一条“可 paper、需小仓位、需继续监控执行 realism”的窄版 relative-value spec。**

## 为什么这轮必须直接 promote_P3
- policy 明确规定：bot3 是 `P2 -> P3` 的主责执行者；
- 当前 `Active P2` 已经出现 **2 次连续 `keep_P2`**，本轮不得再给第三次开放式 `keep_P2`；
- 本轮 honesty 收口并没有发现唯一剩余致命 blocker；
- 因此继续把它留在 `P2`，会违反 policy 的出口约束。

所以本轮唯一合法动作是：

> **把 `Rank 183` 从 `Active P2` 升入 `Paper launch queue`。**

## 升级后的最诚实 paper-spec 摘要
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- pair：`CBETH spot + ETH perp`
- timeframe：`15m`
- fair-basis anchor：`7~10d rolling`
- entry：`|z| >= 2.0` 为主
- exit：`0~0.5`
- timeout：`12h~24h` 防事故护栏
- execution：默认仅从 **`2k~10k USD` 小中仓位** 起步
- honesty note：不讲大容量故事；paper 阶段继续盯盘口冲击、填单节奏、funding 与慢 anchor 漂移

## 本轮改变系统认知的一句话
`Rank 183 / cbeth-eth-rolling-fair-basis-mr` 在小中仓位、CBETH 现货深度与 ETH perp 执行现实下，已不存在阻止进入 paper trade 的唯一剩余致命 honesty blocker；因此它必须结束开放式 `P2 admission`，直接升入 `P3 / Paper launch queue`。

## 产物
- 复用：`reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`
- 复用：`reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
- 复用：`research/optimization_loop/2026-03-26_1201_rank183_p2_parameter_stability_exit_framing.md`
