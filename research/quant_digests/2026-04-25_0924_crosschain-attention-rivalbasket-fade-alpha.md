# 别把跨链负溢出只读成市场结构：对 short-cycle crypto desk，更该先测的是「某条链先被抢筹 → rival-chain basket 滞后走弱」这条 raw alpha
- 时间：2026-04-25 09:24 UTC
- 类型：2026 arXiv 论文全文 audit + Binance USDⓈ-M public-data portability probe（`ETH/SOL/BNB/ARB/AVAX` native-chain proxy，`1h` parent -> `15m` child）
- 主题类型：raw alpha
- 基础 alpha：某条链的原生代币/生态 proxy 出现 attention shock 后，资金会从 rival chains 抽走，导致 rival-chain basket 在随后 `1~2h` 继续走弱
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-asset / relative-value / cross-chain / attention-shock / negative-spillover / rival-basket / native-token / 1h / 15m / 5m / paper / public-data / cost / risk
- 证据类型：论文证据 + 公共数据快检

## 1. 这次看了什么
看的是 Mengzhong Ma、Te Bao、Yonggang Wen 的 2026 arXiv 论文 **One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets**。论文主线是“链与链之间不一定一起涨跌，很多时候是一条链吸走注意力和资金，别的链反而被抽血”；对我们 desk 更值钱的读法，不是把它停在 contagion 解释，而是直接把它翻成一条 **cross-chain relative-value raw alpha**：**leader chain 先冲时，short rival-chain basket。**

## 2. 核心结论
- 论文用 `Ethereum / Solana / BSC / Arbitrum / Avalanche` 五条链、`2022-2025` 的 on-chain 资产组合，发现 **一条链上涨时，其他链资产经常同步转弱**，这不是传统市场常见的“风险一起上/下一起下”。
- 作者把原因归到 **attention-driven capital reallocation**：用户和资金追着新热点链跑，买新链往往伴随卖旧链，而不只是“全市场收到同一条好消息”。
- 对 short-cycle desk，最自然的 base alpha 不是预测哪条链会火，而是：**当 leader shock 已经发生后，rival basket 的滞后走弱还能不能继续吃到。**
- 我用 Binance USDⓈ-M 公共 `15m/1h` 数据把五条链的 native-token proxy 压成最小实验后，若定义 `1h` parent shock 为：**该链 token 为当小时最强，`z >= 1.25`，且领先第二名至少 `35 bps`**，则随后：
  - rival basket 在 **下一 `2h` 平均约 `-18.56 bps`**（`44` 次事件，正收益占比仅 `25%`）；
  - 下一 `1h` 约 `-3.20 bps`，更像需要 child execution 的慢扩散，不像立刻一脚就走完；
  - 这说明它更适合做 **`1h parent -> 15m/5m child short-rivals`**，而不是把 leader continuation 当主交易。

## 3. 为什么和当前项目有关
这条线直接补的是 **cross-asset / relative-value raw alpha** 素材池，而且和我们最近 intake 的 pairs、basis、funding、lead-lag 是同一家族但不重复：
- 它不是单币趋势，而是 **跨链竞争**；
- 它不是传统 pairs cointegration，而是 **attention shock 后的 basket 弱化**；
- 数据公开、实现轻，先用 native tokens 就能做第一轮诚实 verdict，再决定是否上链上 activity / DEX flow 做增强。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / cross-asset
- 基础 alpha：leader-chain shock 后，rival-chain basket 短时走弱
- regime：链间轮动活跃、热点切换快、attention 集中时更可能成立
- filter / veto：只做 leader 强度显著、且领先第二名足够多的事件；BTC 全市场大冲/大杀时先做 market-beta 中性化
- risk / sizing / execution overlay：默认等权 short rivals；单链权重上限；`15m` 分批入场；`2h` time-stop；成本先按 taker `8 bps` 做首轮门槛

## 4. 可复刻的最小实验
- 研究假设：若链间存在 attention-driven substitution，则某条链 proxy 在 `1h` 内显著领涨后，其他链 proxy 在后续 `15m~2h` 应继续偏弱。
- 一个可计算定义：
  - universe：`ETH/SOL/BNB/ARB/AVAX` perpetual
  - event：某币 `1h` 收益为横截面第一，且 `ret / rolling_std_24h >= 1.25`，并领先第二名 `>= 35 bps`
  - trade：下一根 `15m` 开始，**short equal-weight rival basket**，持有 `8` 根 `15m`（`2h`）
- 最小回测切口：近 `1500` 根 `1h` parent bars，child 用同步 `15m` klines；先不加链上数据，只看 native-token proxy 能否站住。
- 最该先看哪 1~2 个指标：
  - post-cost 平均每事件收益（先扣 `8 bps` 单边或按你的真实执行口径）
  - 正收益事件占比 / 是否被少数大事件支撑

## 5. 风险与保留意见
- 当前 portability probe 里 **ARB 事件占比很高**，说明现阶段结果部分被 L2/alt-chain 热点驱动，未必能稳定外推到所有链。
- native-token proxy 只是“链热度”的可交易近似，不等于论文里的全链资产组合；若要更贴近原文，应补链上 activity、DEX volume、active addresses 或链级 basket。
- rival basket 在 `2h` 内走弱成立，但 **leader 自身回吐更快**；所以这轮更像“short rivals”而不是“long leader + short rivals”。
- 若全市场风险偏好突然共振，跨链替代关系会被 market beta 淹没，因此最好加 BTC / total market move veto。

## 6. 来源
- Ma, Mengzhong; Bao, Te; Wen, Yonggang. (2026). *One Rising Ship Sinks Other Ships: Cross-Chain Negative Spillovers in Crypto Markets*. arXiv working paper.
- Readable URL: `https://arxiv.org/abs/2602.23762`
- PDF URL: `https://arxiv.org/pdf/2602.23762`
- Data for portability probe: Binance USDⓈ-M public klines (`ETHUSDT`, `SOLUSDT`, `BNBUSDT`, `ARBUSDT`, `AVAXUSDT`), `1h` parent + `15m` child.
