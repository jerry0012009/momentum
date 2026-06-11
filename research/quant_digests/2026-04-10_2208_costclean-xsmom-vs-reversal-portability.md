# 别把这份 2026 cross-sectional stat-arb repo 直接压到 `5m/15m`：对 short-cycle desk，更该先先测的是「slow strength rank × turnover veto」，否则 majors futures 上更像反向信号
- 时间：2026-04-10 22:08 UTC
- 类型：GitHub / notebook
- 主题类型：raw alpha
- 基础 alpha：横截面 winner-minus-loser 排名（过去一段收益高的做多、低的做空），外加 z-score reversal 作为对照腿
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：cross-sectional / momentum / mean-reversion / relative-value / turnover / cost / market-neutral / Binance / 5m / 15m
- 证据类型：工程经验 + 最小公开数据 portability probe

## 1. 这次看了什么
看的是 GitHub repo **`rong9494/crypto-statistical-arbitrage`**（2026-04-08），核心 notebook 用 Binance 日线数据做 10 个大市值币的横截面动量与反转对照，并把 turnover、执行成本、组合优化都写进去了。

## 2. 核心结论
- 这份 repo 的 **base alpha 很清楚**：不是花哨 ML，也不是黑盒配对，而是最朴素的 **cross-sectional momentum**。做法就是按过去 `N` 天收益给币排序，做多 winner、做空 loser，权重做成 dollar-neutral。
- repo 自带结果里，**20d momentum 明显优于 15d reversal**：gross Sharpe 约 **1.01**，年化收益约 **20.1%**，最大回撤约 **-17.9%**；而 reversal gross Sharpe 只有 **0.34**。
- 真正值钱的不是 headline return，而是它把 **turnover 写清楚了**：momentum 平均日换手约 **0.33**，对应年化成本拖累约 **8.34%**；reversal 平均日换手约 **1.30**，成本拖累约 **33.21%**，所以 net Sharpe 直接掉到 **-1.43**。
- 我额外做了一个 **Binance USDⓈ-M majors `15m/5m` portability probe**（BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/LTC/AVAX）：如果把这个横截面 ranking 思路 **逐根搬到短周期 perpetuals**，结果并不好。`15m` 上 momentum 在 `4h~8d` lookback 都是 **负 gross Sharpe**；reversal 虽然 gross 是正的，但每根换手大约 **1.22~1.33**，在 `5 bps` 成本假设下会被彻底吃掉。`5m` 上也是同样结构：**momentum 反着来，reversal 有毛刺但没法留住净值**。
- 所以，对当前 desk 来说，这份 repo **最可复用的不是“直接 port 一个 5m/15m 主 alpha”**，而是三件事：
  1. 用它的 **横截面 rank 骨架** 做 slow book / slow router；
  2. 把 **turnover veto** 当一等公民，而不是事后补一句“注意成本”；
  3. 把 reversal 限定在 **高 dispersion / post-shock / hard time-stop** 口袋里，而不是 always-on。

## 3. 为什么和当前项目有关
这条线和我们现在补 raw alpha 素材池是直接相关的，因为它回答了一个很实际的问题：**横截面 momentum / reversal 这类最基础的 market-neutral alpha，哪些部分能复用，哪些部分不能直接下放到短周期？**

这份 repo 给了一个很干净的答案：
- **可复用**：ranking、市场中性权重、turnover accounting、cost-aware comparison；
- **不可直接照搬**：把日线 alpha 逐根压到 `5m/15m` 的重平衡节奏；
- **更适合当前 desk 的读法**：把它当成“slow strength / slow weakness 的资产侧 admission layer”，而不是一条 always-on 的 intraday 主信号。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：过去一段收益排序后的 winner-minus-loser continuation
- regime：更适合有持续强弱分层、而不是全市场一起抽风的阶段
- filter / veto：turnover cap、dispersion gate、post-shock bucket、refresh 频率降速
- risk / sizing / execution overlay：market-neutral 权重、只在 rank 变化足够大时换仓、成本阈值先过再交易

## 4. 可复刻的最小实验
**研究假设 A**：`15m` 上横截面强弱不是不能做，而是不能每根都按最新 rank 重排；要改成 **slow signal + sparse rebalance**。

最小做法：
1. 数据：Binance USDⓈ-M 10 个 liquid majors，`15m`，最近 `180d`。
2. 信号：用 `1d / 2d / 4d` 等效 lookback 生成横截面强弱分数，但只允许 **每 `1h` 或 `4h` 刷新一次仓位**。
3. 组合：top2 long / bottom2 short，等权或波动率缩放。
4. veto：若本次调仓隐含 turnover 超过阈值（如 `0.35`），则不换；或只有 rank gap 超过阈值才换。
5. 成本：至少跑 `2 / 4 / 6 bps` friction ladder。

**研究假设 B**：`5m/15m` 上真正可能留下来的不是 always-on reversal，而是 **高 dispersion + 单次冲击后的 loser-bounce**。

## 5. 风险与备注
- 这份 repo 原始证据主要是 **日线**，所以它证明的是“这条 alpha 在慢频上可讲通”，不是“可直接做 intraday”。
- 我这次 portability probe 只覆盖 **majors perpetuals**；若换到更分化的小币 universe，符号和成本结构可能会变。
- 高频 annualization 数字会很夸张，所以这里更该盯的是 **sign、turnover、cost sensitivity**，不是把年化收益机械地当成可实现收益。

## 6. 来源
- GitHub handle / Year: `rong9494` (2026)
- Title: *crypto-statistical-arbitrage*
- Venue: GitHub repository
- Repo URL: <https://github.com/rong9494/crypto-statistical-arbitrage>
- Readable README: <https://raw.githubusercontent.com/rong9494/crypto-statistical-arbitrage/master/README.md>
- Notebook: <https://raw.githubusercontent.com/rong9494/crypto-statistical-arbitrage/master/Statistical_Arbitrage_in_Cryptocurrencies.ipynb>

## 7. 一句话结论
这份 repo 值得 intake，但 **不是因为它能直接给我们一条 `5m/15m` 主 alpha**；它更像是在提醒：**cross-sectional momentum/reversal 要先过 turnover 这一关，过不了，就别把 gross edge 当真 edge。**
