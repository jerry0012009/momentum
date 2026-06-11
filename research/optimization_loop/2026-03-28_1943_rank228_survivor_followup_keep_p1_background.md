# Rank 228 / directional-change overshoot + abnormal-regime veto — survivor follow-up 收口：keep_P1 后转 background

- 时间：2026-03-28 19:43 UTC
- 对象：`Rank 228 / directional-change overshoot + abnormal-regime veto`
- 本轮动作：作为当前唯一合法 survivor，做唯一一次 `BTCUSDT / ETHUSDT` public `1m` bar-proxy DC event-flow follow-up
- 结论：**keep_P1 后转 background**（不升 `P2`）

## 这轮到底做了什么

为避免继续停留在 FX / long-only / 无成本叙事，这轮直接用 Binance public futures `1m` klines 在 `BTCUSDT`、`ETHUSDT` 上做了最小、诚实的 bar-proxy 检查：

1. 用 close-only 近似重建 DC 事件流；
2. 当价格自最近 trough 上行超过 `θ`（测试 `10 / 15 / 20 / 30 / 40 bps`）时，视为上行 DC 确认，下一根开盘入场；
3. 用 `α·θ` 反向确认出场（测试 `α = 0.4 / 0.6 / 0.8`）；
4. 再加一层最小 `abnormal regime veto` 代理：过去 `60m` realized vol z-score 或单根 `1m` absolute return z-score 过高时，阻止入场 / 提前退出；
5. 统一核对 `4 / 6 bps per side` 成本后是否仍存在可交易 pocket。

产物：
- 脚本：`scripts/build_rank228_dc_overshoot_survivor_followup.py`
- 结果目录：`reports/artifacts/scout_rank228_dc_overshoot_survivor_followup/`
- 关键文件：
  - `decision.json`
  - `summary.csv`
  - `best_variant_comparison.csv`
  - `trades.csv`

## 核心结果

### 1) 没有留下任何 `6 bps/side` 后仍为正的 pocket

`decision.json` 直接结果：

- `positive_net6_variants = 0`
- 总结句：`BTC/ETH 的 1m bar-proxy DC overshoot continuation 在 4~6 bps/side 后没有留下足够稳定的正 pocket；abnormal veto 虽偶尔改善左尾，但不足以把对象送进 P2。`

也就是说，这轮最重要的问题已经被直接回答：

> **在 crypto public 1m bar-proxy 口径下，这条 DC-confirmed overshoot continuation 没能留下成本后还能站住的 pocket。**

### 2) 最好的 gross 结果也只有接近 0，成本后一律转负

按 `best_variant_comparison.csv`：

#### BTC 最好组合
- base 最好：`theta=10bps, alpha=0.4`
  - `gross_mean_bps = -0.389`
  - `net4_mean_bps = -8.389`
  - `net6_mean_bps = -12.389`
- veto 最好：`theta=40bps, alpha=0.4`
  - `gross_mean_bps = +0.085`
  - `net4_mean_bps = -7.915`
  - `net6_mean_bps = -11.915`

#### ETH 最好组合
- base 最好：`theta=30bps, alpha=0.6`
  - `gross_mean_bps = -0.002`
  - `net4_mean_bps = -8.002`
  - `net6_mean_bps = -12.002`
- veto 最好：`theta=30bps, alpha=0.6`
  - `gross_mean_bps = +0.210`
  - `net4_mean_bps = -7.790`
  - `net6_mean_bps = -11.790`

翻成人话：

- **gross 层连 1bp 都摸不到**；
- 一旦扣掉最基本的 round-trip 成本，这条线就系统性转负；
- 所以这不是“再微调一下参数就能上板”的状态，而是当前 public 1m 近似下，alpha 本体本来就太薄。

### 3) abnormal veto 不是完全没用，但只够“稍微减伤”，不够“把负 edge 翻正”

这轮也直接回答了另一半问题：`abnormal regime veto` 是否真能压 tail loss？

- **BTC：** veto 虽把 mean 从 `-12.389` 拉到 `-11.915 net6 bps`，但 `net6 p05` 反而从 `-29.001` 变成 `-39.480`，左尾更差。
- **ETH：** veto 的确略微改善左尾，`net6 p05` 从 `-46.849` 提到 `-45.062`，mean 也从 `-12.002` 改到 `-11.790`；但改善幅度只有 `~1.79 bps`，仍远远不足以翻过成本线。

所以更诚实的读法是：

> **abnormal veto 在 ETH 上有一点点“压尾”迹象，但力度太小，救不了 alpha 本体；在 BTC 上甚至没有稳定改善。**

## 为什么这轮不能升 P2

按 survivor follow-up 的唯一目标，这轮需要回答的是：

1. 有没有至少一个 `4~6 bps` 后仍成立的 pocket；
2. `abnormal regime veto` 是否真能压住 tail loss。

现在答案是：

- **问题 1：没有。**
- **问题 2：只有局部、很弱、不可迁移的改善。**

因此这条线不满足升 `P2` 的最小门槛。

## 最终 runtime 结论

- `Rank 228 / directional-change overshoot + abnormal-regime veto`：**keep_P1 后转 background**
- 理由：public `BTC/ETH 1m` bar-proxy 口径下，`DC-confirmed overshoot continuation` 没有留下成本后 pocket；`abnormal regime veto` 只表现出很弱、且不跨资产稳定的减伤，不能把对象送进 `P2`
- survivor 预算：**已用完**
- 前排影响：`Surviving candidate slot` 清空，后续 front-chain 可以合法轮到下一条 conditional fresh intake

## 一句话结果

`Rank 228` 的唯一 survivor follow-up 已诚实收口：在 `BTCUSDT / ETHUSDT` 的 public `1m` bar-proxy DC 事件流上，这条 `overshoot continuation + abnormal-regime veto` 线 gross 端已非常薄、扣掉 `4~6 bps/side` 后没有任何稳定正 pocket，且 veto 只带来局部微弱减伤，因此本轮不升 `P2`，按预算写成 `keep_P1 后转 background`。
