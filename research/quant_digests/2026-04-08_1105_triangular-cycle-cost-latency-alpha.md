# 别把这份高星 multi-strategy repo 只读成“大而全交易框架”：对 short-cycle desk，更该先测的是「spot triangular cycle gap × fee/latency/staleness gate」
- 时间：2026-04-08 11:05 UTC
- 类型：GitHub repo source audit（`README.md` + `src/strategies/arbitrage.py`）
- 主题类型：raw alpha
- 基础 alpha：同 venue 三角路径定价偏离（USDT→BTC→ETH→USDT / 反向路径）回归无套利平价
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / triangular-arbitrage / same-venue / spot / btc-eth-usdt / latency / staleness / fee-hurdle / 1m / 3m / 5m
- 证据类型：工程经验

## 1. 这次看了什么
我这次看的是 `mefai-dev/mefai-autotrade` 这个近期仍活跃的仓库（GitHub Stars `108`，`2025-11-28` push）。虽然 repo 对外包装成“大而全自动交易系统”，但对我们 desk 更值钱的其实是它在 `src/strategies/arbitrage.py` 里明写的一条**旁支 raw alpha**：三角套利。源码不是泛泛说“支持 arbitrage”，而是直接写了 `USDT -> BTC -> ETH -> USDT` 与反向路径的收益公式、round-trip 成本扣减、净利门槛、延迟/陈旧报价闸门、单笔/总敞口上限。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得拿来测的，不是它的大框架，而是“同 venue 三角路径净利 > 三腿费用 + 滑点 + 最小利润门槛”这条可独立复现的 relative-value raw alpha。
- **一句话证明方式：** 证据直接来自源码：策略会扫描三角循环收益，扣掉 `taker_fee_bps`、`max_slippage_bps`、提现/跨所成本项，只有 `net_profit` 过线才生成信号。
- 参数默认值很像一个可直接进最小实验的壳：`min_spread_pct=0.10%`、`min_net_profit_usd=$5`、`taker_fee_bps=7`、`max_slippage_bps=10`、`max_exposure_usd=50,000`、`max_trade_usd=5,000`、`max_open_arbs=5`。
- 它还额外加了执行现实闸门：`max_latency_ms=200`、`max_price_age_ms=1500`。这很关键——三角套利不是“看到价差就上”，而是“只在报价够新、链路够快时才承认 edge”。
- 三角分支不是纯监控：源码会把 `spread_pct / expected_profit / transaction_cost / net_profit / buy_price / sell_price` 一起打进 signal metadata，说明它天然适合改造成我们自己的 admission + friction ladder 框架。

## 3. 为什么和当前项目有关
这条线和我们现在要补的 **raw alpha 素材池** 直接相关，而且刚好能把注意力从 breakout / trend 扩到 **relative-value / stat-arb**。更重要的是，它不是“只会告诉你市场可能有效”的解释型材料，而是已经把 `entry / exit / sizing / risk / cost` 的骨架写进去了：
- entry：三角路径净收益扣成本后过阈值才开；
- exit：三腿走完即回到 base currency，本质是即时 flat；
- sizing：单笔与总敞口双上限；
- risk：陈旧报价、延迟、最多并发机会数限制；
- cost：明确把手续费与滑点门槛写进策略。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb
- 基础 alpha：同 venue 三角循环价格不一致会向无套利平价回归
- regime：只在高流动性 majors、报价新鲜、低延迟时启用
- filter / veto：`cycle_gap > fees + slippage + min_net_profit`；`price_age < 1500ms`；`latency < 200ms`
- risk / sizing / execution overlay：`max_trade_usd`、`max_exposure_usd`、`max_open_arbs`；三腿执行失败即视为残腿风险，需要单独记账与强平兜底

## 4. 可复刻的最小实验
- **研究假设：** 在 `BTCUSDT / ETHUSDT / ETHBTC` 这类高流动性三角里，只有当三角路径毛收益明显高于三腿费用与滑点时，短周期才存在可成交的净 edge。
- **一个可计算定义：**
  - `gap_fwd = bid_ETHUSDT / (ask_BTCUSDT * ask_ETHBTC) - 1`
  - `gap_rev = (bid_BTCUSDT * bid_ETHBTC) / ask_ETHUSDT - 1`
  - `net_gap = max(gap_fwd, gap_rev) - fee_3leg - slip_3leg - fixed_hurdle`
- **最小回测切口：** 先用 Binance spot 公共 `bookTicker` 或高频 top-of-book 快照，做 `BTCUSDT / ETHUSDT / ETHBTC` 的 `1m` 主实验，再聚合成 `3m / 5m` 看机会密度是否塌陷；如果 spot 数据链路麻烦，可先用 perp proxy 做“伪三角”可行性 sanity check。
- **最该先看 2 个指标：**
  1. `post-cost net edge / opportunity`（每次机会扣完三腿成本后还剩多少）
  2. `fillable opportunity count`（真正过净利门槛、且报价不过期的机会数）

## 5. 风险与保留意见
- 这类 alpha 最容易死在**执行现实**，不是死在想法本身：public klines 几乎不够，至少要 L1/`bookTicker` 级别。
- 同 venue 三角套利通常容量有限，`$5` 净利门槛在低手续费 tier 下也可能很快被竞争者吃掉。
- 如果只能做到 bar 级回测，而做不到 quote-level freshness / leg sequencing，回测结果大概率乐观偏差。
- 这份 repo 是大框架的一条旁支，不代表作者已经证明这条支线在真实资金上稳定赚钱；我们应该把它当 **可快速复现的 raw alpha shell**，不是现成 production verdict。

## 6. 来源
- mefai-dev. (2025/2026). *Mefai Autotrade*. GitHub.
- Repo URL: `https://github.com/mefai-dev/mefai-autotrade`
- Readable URL: `https://github.com/mefai-dev/mefai-autotrade/blob/master/README.md`
- Strategy source: `https://github.com/mefai-dev/mefai-autotrade/blob/master/src/strategies/arbitrage.py`
- 这次重点审计分支：`triangular arbitrage`（同文件内与 `basis / funding / cross-exchange` 并列实现）
