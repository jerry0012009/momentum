# 别把这份 2026 Polymarket repo 只读成预测市场 bot：对 short-cycle desk，更该先测的是「BTC/ETH 5m divergence-pair discount × hard-expiry reprice」这条完整 raw alpha

- 时间：2026-04-08 12:25 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `strategy.py` + `risk_manager.py` + `config.py` + `data_fetcher.py`）
- 主题类型：raw alpha
- 基础 alpha：在 Polymarket 的 BTC/ETH 5 分钟 recurring binary markets 里，若 `BTC_UP+ETH_DOWN` 或 `BTC_DOWN+ETH_UP` 这类 divergence pair 的组合价跌到折价区，就同时买入两腿，等 5 分钟硬结算/官方 resolution 兑现
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / prediction-market / relative-value / stat-arb / polymarket / btc / eth / 5m / hard-expiry / pair-trading / divergence / repo / public-data / cost / risk
- 证据类型：工程经验（开源代码 + 策略参数 + 风控实现）

## 1. 这次看了什么
这次主看 Andrew Cao 2026 的 GitHub 仓库 `andrew-cao-zc/polymarket-pair-trading`。别把它当成“预测市场自动下单脚本”；它真正值得 desk intake 的，是一条相当完整的 relative-value raw alpha：**BTC 和 ETH 的 5 分钟方向 pair 在短时分歧里会出现组合价折价，而这种折价会在硬到期前后被重新定价。**

- 一句话核心结论：这份 repo 真正值钱的不是 bot 外壳，而是 **“跨资产 5m 分歧 pair 折价”** 这条可独立下单的 raw alpha。
- 一句话证明方式：作者把 entry、持有到官方 resolution、次数限制、连亏停机和回撤停机都写成了硬规则，直接围绕 Polymarket 订单簿与结算逻辑执行。
- 最值得复用/复现的点：**单腿价带 + 组合价带 + 官方结算** 这个最小实验口径非常清楚，几乎拿来就能做 first verdict。

## 2. 核心结论
- repo 不是做单腿方向，而是做两腿组合价：只交易 `BTC_UP+ETH_DOWN` / `BTC_DOWN+ETH_UP` 两个 divergence pair。
- entry 写得很硬：两腿单价都要在 `0.38~0.44`，组合价在 `0.70~0.82`。这本质上是在等“便宜的分歧票”，不是追热门单腿。
- signal 还要看当期 leader：若当前 5m 内 `btc_price > eth_price` 就偏 `BTC_UP+ETH_DOWN`，反之做 `BTC_DOWN+ETH_UP`；也就是说它不是无脑买 pair，而是把相对强弱塞进 pair 方向。
- 它天然带完整退出：持有到 5m 市场 official resolution；风控再加 `3` 连亏停机、日内回撤 `5%` 停机、单方向/单周期交易次数上限。

## 3. 为什么和当前项目有关
这条线跟我们最近写过的 Polymarket/Kalshi 锁定套利不一样：那些更像**跨平台或互补合约的静态错误定价**，这里更像**同一平台、同一到期、跨资产方向分歧的动态 relative-value**。它能直接补进 desk 的 raw alpha 素材池，而且周期天生就是 `5m`，几乎不用硬做 frequency transfer。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：`BTC/ETH divergence pair discount × hard-expiry reprice`
- regime：只在 Polymarket `5m` recurring 市场活跃、盘口非空、进入新结算周期后启用
- filter / veto：两腿价格带 `0.38~0.44`；组合价 `0.70~0.82`；按 BTC-vs-ETH 当前强弱决定 pair 方向；流动性不足不做
- risk / sizing / execution overlay：固定 bet size；基于订单簿的 sweep 定价；`3` 连亏停机、日内 `5%` 回撤停机、每方向/每周期次数上限、持有到官方结算

## 4. 可复刻的最小实验
- 研究假设：Polymarket BTC/ETH `5m` recurring markets 里，**分歧组合价的折价**，在 1 个结算窗内有正的 net expectancy。
- 一个可计算定义：每个 `5m` 周期开始后 `60~120s`，抓四个 token 的 mid/ask；构造 `BTC_UP+ETH_DOWN` 与 `BTC_DOWN+ETH_UP` 两个 pair。若两腿单价都在 `0.38~0.44` 且 pair 价在 `0.70~0.82`，按 BTC-vs-ETH 当期变动方向选一组，在 ask 买入，持有到官方 resolution。
- 最小回测切口（资产 / 周期 / 样本）：Polymarket Gamma/CLOB 公共 API + BTC/ETH 外部现价源；样本先抓近 `2~4` 周全部 BTC/ETH `5m` recurring 市场；先只测 `5m`，不强行迁到 `1m/3m/15m`。
- 最该先看哪 1~2 个指标：`post-cost expectancy / pair`、`fill-adjusted win rate`；其次看 `max losing streak` 和 `liquidity shortfall rate`。

## 5. 风险与保留意见
- 这是 prediction-market relative-value，不是 CEX perp；容量、排队、resolution 延迟都可能比 README 设想更差。
- 公开代码里“持有到结算”最干净，但真实收益会对买入 ask / 盘口深度极敏感；如果 sweep 成本抬高，alpha 很可能瞬间消失。
- 它天然更适合 `5m`；若硬迁到 `1m/3m/15m`，应把它当作**外部数据驱动的独立 5m alpha**，而不是伪装成逐根币价信号。

## 6. 来源
- Andrew Cao. (2026). *Polymarket Pair Trading Bot*. GitHub.
  - Repo URL: `https://github.com/andrew-cao-zc/polymarket-pair-trading`
- Public data APIs used by the repo:
  - Polymarket Gamma API: `https://gamma-api.polymarket.com/markets?slug=...`
  - Polymarket CLOB book API: `https://clob.polymarket.com/book?token_id=...`
