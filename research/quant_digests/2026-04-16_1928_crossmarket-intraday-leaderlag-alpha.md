# Cross-Market Intraday TSMOM：别只盯单币 own momentum，先测“leader 先动、laggard 后跟”
- 时间：2026-04-16 19:28 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：跨市场日内顺势——`leader market early return -> laggard market later same-direction return`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/cross-market/leader-laggard/intraday/time-series-momentum/funding-session/15m/5m/binance-perpetual/paper/public-data/cost/risk
- 证据类型：项目种子/shortlist 论文题录 + public-data portability probe

## 1. 这次看了什么
这次看的是 validated shortlist 里的 working paper：**Xu, Li, Singh, Li, _Cross-Market Intraday Time-Series Momentum_**。它最值得 short-cycle desk 拿来拆的，不是“单个市场自己前半段涨、后半段也涨”，而是更贴近实盘的一句人话：**大币先动后，小币会不会在同一会话里补跟。**

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：不是 filter，也不是解释层，而是 **cross-market leader→laggard 的日内顺势 spillover**。
- 把它迁到 crypto，最自然的 leader 不一定是“全球股指”，而是 **BTC/ETH 这种信息领先市场**；最自然的 laggard 则是 **SOL/XRP 这类 beta 更高、反应略慢的 alt perp**。
- 我做了一个轻量 portability probe：Binance USDⓈ-M、`15m`、近 `180d`、按 `8h funding session` 切片；leader 定义为 `BTC+ETH` 在会话前 `60m` 的等权收益，laggard 定义为 `SOL/XRP` 在随后 `60m` 的收益。只在 `|leader_ret|` 进入样本前 `20%` 时交易，**同向跟随的 gross 平均收益约 `+14.6 bps/trade`，胜率约 `60.6%`，样本 `109` 笔**。
- 单币里最亮的是 **XRP**：同样口径下，`BTC+ETH` 前 `60m` 方向去跟 `XRP` 后 `30m`，**gross 约 `+14.9 bps/trade`，样本 `109`，t-stat 约 `2.17`**；`SOL` 跟随也有正结果，但弱一些。
- 若粗略按 round-trip `6 bps` 扣成本，前面的 `SOL+XRP` basket 口径仍约 **`+8.6 bps/trade` net**。这说明它不只是“相关性好看”，而是有希望成为真正可交易的 pocket raw alpha。

## 3. 为什么和当前项目有关
这条线对当前 `1m/3m/5m/15m` 研发有价值，因为它补的是一条**不靠 funding、不靠 pair spread 回归、也不靠 OI 事件**的 raw alpha：**跨市场信息传导下的短窗延续**。它适合放进素材池，作为：
- `15m` 默认主实验：最稳，和 funding-session 切法天然兼容；
- `5m` 加强版：把“前 60m”拆成更细的 leader build-up，测试更快的 30m~60m 跟随；
- 后续还能和已有模块拼装：例如只在 `OI/成交额` 同步放大时放行，或只在 `funding 临近` 时做 admission，而不是把 funding 当 alpha 本体。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 跨市场 leader-laggard spillover
- 基础 alpha：`BTC+ETH` 先行收益可预测 `SOL/XRP` 同会话后续同向收益
- regime：高信息流/高 beta 会话更优；先用固定 `8h funding session` 作为 session 定义
- filter / veto：仅做 `|leader_ret|` 进入过去滚动分位前 `20%~30%` 的会话；若 laggard 已提前超涨/超跌或点差异常扩大则 veto
- risk / sizing / execution overlay：单笔风险预算 `25~50 bps NAV`；按 laggard 近 20-bar 实现波动反比分配；固定持有 `2~4` 根 `15m`；若 leader 在持仓后出现反向吞没则提前平仓；回测先按 round-trip `6~8 bps` 计成本

## 4. 可复刻的最小实验
- 研究假设：`BTC/ETH` 在 funding 会话前段的大幅同向移动，会在 `SOL/XRP` 上留下可交易的后续跟随窗口。
- 一个可计算定义：
  - 周期：`15m`
  - 会话：`00:00 / 08:00 / 16:00 UTC` 为起点的 `8h funding session`
  - `leader_ret = return(BTC, first 4 bars) * 0.5 + return(ETH, first 4 bars) * 0.5`
  - 若 `abs(leader_ret) >= rolling q80`，则在第 5 根开盘按 `sign(leader_ret)` 做 `SOL/XRP` 等权 basket
  - `exit = 持有 4 根 15m`；备选对照是持有 `2` 根与 `8` 根
- 最小回测切口：Binance USDⓈ-M perpetual；`BTC/ETH/SOL/XRP`；近 `180d`；先只做会话级 one-shot，不叠加复杂加仓
- 最该先看：
  1. `post_cost_bps_per_trade`
  2. `hit_rate / t-stat / turnover`

## 4.5 下一步怎么测
1. 把 `leader` 从 `BTC+ETH` 扩成 `BTC/ETH` 分开、以及 `BTC->SOL`、`ETH->XRP` 的单映射矩阵，看是不是某几条 lead-lag 边特别强。  
2. 把 `15m` 口径下沉到 `5m`：固定“前 `60m` leader build-up，后 `30m`/`60m` laggard follow”，检验更快 alpha 是否仍成立。  
3. 在现有 raw alpha 上叠加 shared gate，而不是反过来：例如只在 `leader move` 与 `OI×成交额` 同步扩张时放行，验证是否能把胜率和 net bps 再往上推。  
4. 做“延迟敏感度”测试：第 5 根开盘进、第 5 根收盘进、第 6 根开盘进，确认这是不是一条会被执行延迟迅速吃掉的 pocket。  

## 5. 风险与保留意见
- 这次没拿到 SSRN 正文，当前主要依赖项目 seed/shortlist 题录与 public-data probe，所以**论文细节口径仍需二次核实**。
- `15m` probe 说明“可迁移”，不等于已经证明“稳健可实盘”；尤其样本只是一家交易所、一个近 `180d` 区间。
- 这条 alpha 本质上吃的是**信息传导的时滞**，如果市场进入极端同步化阶段，laggard 可能不再“后跟”，而是与 leader 同时定价，边际会被压扁。
- 因为信号是 directional spillover，不是 market-neutral spread，所以遇到宏观 news spike 时，**方向没错也可能被大 wick 先打掉**；执行和止损定义必须保守。

## 6. 来源
- Xu, D., Li, B., Singh, T., & Li, J. (2024). *Cross-Market Intraday Time-Series Momentum*. SSRN Electronic Journal / working paper.
- DOI: https://doi.org/10.2139/ssrn.4765613
- Earlier SSRN record in project seeds: https://doi.org/10.2139/ssrn.4651331
- Readable URL: https://www.ssrn.com/abstract=4765613
- Legacy seed URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4651331
- Repo URL: 暂无公开实现；本笔记的 crypto 迁移口径基于 Binance USDⓈ-M public klines 自定义构造
