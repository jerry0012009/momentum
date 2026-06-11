# 别把这篇跨链 spillover 论文只读成“行业联动叙事”：对 short-cycle crypto desk，更该先测的是「leader-chain attention shock × rival-chain relative weakness」这条 raw alpha

- 时间：2026-04-19 16:02 UTC
- 类型：arXiv 论文全文 + Binance USDⓈ-M portability probe
- 主题类型：raw alpha
- 基础 alpha：**当某条链的原生币在短窗里放量急拉、吸走注意力时，其他链的原生币会在接下来 `1h~2h` 更容易相对走弱；对 desk 来说，更像一条“跨链相对价值 / rotation”原始信号，而不是宏观叙事。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前更像 `15m` 母信号；执行侧还需压腿数与成本）
- 主题标签：cross-sectional / relative-value / cross-chain / attention / spillover / rotation / native-token / 15m / 5m / paper / cost
- 证据类型：论文证据 + 本地 public-data portability probe

## 1. 这次看了什么

看的是 **Mengzhong Ma, Te Bao, Yonggang Wen (2026)** 的 arXiv 论文 **《One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets》**。作者用 `2022–2025` 的链上数据研究 Ethereum、Solana、BSC、Arbitrum、Avalanche 之间的联动，核心不是“大家一起涨跌”，而是：**一条链突然更吸引人时，别的链会被抽血。**

对我们 desk，最值得拿来试的不是半日频非线性因子模型本身，而是其中那句很可交易的话：**注意力和资金在链之间会轮动，不一定是同涨同跌。** 这可以直接翻成短周期 relative-value 事件实验。

## 2. 核心结论

- **一句话核心结论：** 当前更像样的不是“追 leader 链继续涨”，而是 **leader 出 attention shock 后，去做 rival-chain 的相对走弱**。
- **一句话证明方式：** 我把论文里的“attention-driven cross-chain substitution”翻成 Binance 原生币篮子代理：`ETH/SOL/BNB/AVAX/ARB` 中，若某币在 `15m` 上出现 `过去1h收益 z>=1.5` 且 `quote_volume_z>0` 的最强 shock，就观察其他链原生币接下来 `1h~2h` 的表现。
- `15m` 上，若每次只取 **最强 leader-chain shock**，再做 **long leader / short 当下最弱 rival**，next `1h` 约 **`+10.88 bps gross`**，胜率约 **`53.27%`**（`n=871`）。
- 若不做双腿，只做 **short weakest rival**，next `2h` 约 **`+10.77 bps gross`**、胜率约 **`54.99%`**；这比“追 leader 本身”更厚，也更贴近论文想表达的 substitution。
- 若做得更钝一点、直接 short 其余 4 条链的 **equal-weight rival basket**，next `2h` 也还有约 **`+8.22 bps gross`**、胜率约 **`57.29%`**；粗看已经接近单腿 `8bps` taker 成本线。
- 相反，`5m` 压缩版不稳：同思路在 `5m` 上主要是 leader 自己还在延续，rivals 没明显一起下，说明这条线当前更像 **`15m` context / mother signal**，不适合直接硬压成 `5m` 裸主信号。
- 事件异质性很强：这轮 proxy 里 **BNB / ETH 领涨 shock** 后，rival basket 的 `2h` 走弱更明显（约 **`+26.34 / +13.32 bps`** 的 short-alpha）；**ARB** 的跨链抽血效果则明显更弱。

## 3. 为什么和当前项目有关

这条线补的是我们最近相对少的一块：**不是单币 trend，也不是传统 pairs spread，而是“跨链资金轮动”驱动的 relative-value raw alpha。**

翻成人话就是：
- 某条链突然成了全市场焦点；
- 钱和注意力会往那边挪；
- 其他链的原生币短时间内更容易被卖、至少更容易相对跑输；
- 所以最值得测的不是“全市场一起 risk-on”，而是 **跨链 winner vs loser 的 rotation trade**。

这也给了一个很实用的 desk 读法：论文原本是半日频链级 spillover 研究，但对短周期开发，更值钱的是把它拆成 **event-driven relative-value router**。

## 3.5 策略拆解（必填）

- 方向属性：横截面 / 相对价值 / 事件驱动
- 基础 alpha：leader-chain attention shock → rival-chain relative weakness
- regime：更适合链间资金轮动明显、leader shock 足够强且伴随放量的时段
- filter / veto：`leader ret_1h_z >= 1.5`、`leader volume_z > 0`；优先只做最强 leader；可先 veto `ARB` 这类 spillover 较弱的 leader
- risk / sizing / execution overlay：先从 **single-leg short weakest rival** 起步，再和 `long leader / short weakest rival` 做成本对比；持有 `1h~2h`，单事件 time-stop，限制并发事件重叠

## 4. 可复刻的最小实验

- **研究假设：** 一条链的 attention shock 会在接下来 `1h~2h` 内压制 rival-chain native tokens 的相对收益。
- **可计算定义：** 在 `ETH/SOL/BNB/AVAX/ARB` 上，每个 `15m` bar 计算 `ret_1h_z` 与 `quote_volume_z`；若某币满足 `ret_1h_z>=1.5 & volume_z>0` 且为当期最强，则：
  1. 方案 A：short 当期 `ret_z` 最弱的 rival，持有 `8` 根 `15m` bar；
  2. 方案 B：long leader / short weakest rival，持有 `4` 根 `15m` bar；
  3. 对比 `5m` child execution 是否优于母信号直接持有。
- **最小回测切口：** Binance USDⓈ-M，`15m` 近 `90d`；先做 5 个链代表币，再决定是否扩到 OP / POL / SUI / APT 等“生态代理币”。
- **先看两件事：** `post-cost` 是否还能活；以及把 rival 从 `EW4` 收缩到 `top1 weakest` 后，trade count 与稳定性有没有明显变差。

## 5. 风险与保留意见

- 论文原始证据来自链级 on-chain 面板与非线性因子模型；这里用的是 Binance 原生币永续代理，不是严格 reproduction。
- 当前 pocket 主要赚的是 **rival 弱**，不是 leader 强；因此若做双腿，成本会吃掉不少 edge。
- 这条线本质上是“跨链 attention rotation”的代理，native token 不一定完美代表整条链生态流入流出。
- `ARB` 这类 leader 的 spillover 强度偏弱，说明不能假设所有链都同权。
- 若要变成 production，更像要和执行层结合：例如 `15m` 母信号、`5m` 只负责找更好的 short 进场，而不是单独用 `5m` 事件开仓。

## 6. 来源

- Mengzhong Ma, Te Bao, Yonggang Wen. (2026). *One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets*. arXiv.
- DOI: `10.48550/arXiv.2602.23762`
- Readable URL: https://arxiv.org/abs/2602.23762
- PDF URL: https://arxiv.org/pdf/2602.23762
- 本地全文抽取：`tmp_cross_chain_negative_spillovers_2026.txt`
- 本地实验产物：
  - `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_by_leader.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crosschain_spillover_summary.csv`
