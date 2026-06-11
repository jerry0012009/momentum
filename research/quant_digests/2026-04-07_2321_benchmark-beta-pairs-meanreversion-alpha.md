# 别把这篇 2021 pairs 论文只读成“老式相关性配对”：对 short-cycle desk，更该先测的是「benchmark-beta return differential × thresholded pair fade」这条完整 raw alpha
- 时间：2026-04-07 23:21 UTC
- 类型：2021 *Investment Management and Financial Innovations* 全文 PDF（Business Perspectives）
- 主题类型：raw alpha
- 基础 alpha：先把两条腿各自对 crypto 市场基准的 beta 暴露剥掉，再交易剩余 return differential / cointegration residual 的均值回复
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / benchmark-beta / return-differential / cointegration / market-neutral / 15m / 5m / 3m / 1m
- 证据类型：论文证据

## 1. 这次看了什么
看的是 Saji Thazhungal Govindan Nair (2021) 的全文论文 *Pairs trading in cryptocurrency market: A long-short story*。论文用 2018-01 到 2020-06 的 top-10 市值 crypto，比较了相关系数、beta 系数、stochastic return differential、cointegration 四种配对思路。对我们最值钱的，不是“相关性高就配对”，而是 **先对 cap-weighted crypto benchmark 做 beta 去市场化，再看 pair residual 是否回归**。

## 2. 核心结论
- 这篇东西真正适合我们 desk 的 base alpha，不是“老式价格距离”，而是 **benchmark-beta 调整后的 pair residual mean reversion**。先把市场共同 beta 去掉，再做 rich leg / cheap leg 的 relative-value 交易，明显更像可移植的短周期原型。
- 论文的 Table 5 显示：基于 return differential 的 cointegration 检验在 4 个子样本里都显著，统计量大致落在 **-12.16 到 -15.91**，说明 residual 这一层不是拍脑袋拼出来的。
- 最能说明问题的是 **熊市/逆风子样本（Panel D）**：六组 pair-trading 累计利润仍然全部为正，分别约 **359.25 / 162.34 / 16.05 / 169.47 / 16.48 / 14.13 USD**；而论文给的 long-only portfolio 同期六组结果全部为负，约 **-245.60 到 -15.75 USD**。一句话：赚钱的不是 crypto beta，而是 market-neutral 的 spread 回归。
- 在顺风样本（Panel A）里，pair-trading 在 **ETH-LTC / ETH-NEO** 上的累计利润约 **768.89 / 857.52 USD**，反而说明更值得盯的是“同市场 beta、不同 idiosyncratic drift”的组合，不一定非要死守最大市值 pair。

## 3. 为什么和当前项目有关
这篇论文对我们最有用的地方，是给 pairs / stat-arb 素材池补了一个**比纯 z-score 价差更像 institutional shell 的 spread 定义**：
- 不是直接比两条腿谁涨得多；
- 而是先问：这两条腿分别对市场大盘有多少 beta；
- 再看剩余 residual 是否偏离过头、会不会回归。

这正好补当前 desk 的 raw alpha 缺口：我们已经收了很多 `cointegration / z-score / OU` 壳，但 **“先 market-neutralize，再做 pair fade”** 这一层还没有被单独拿出来做最小实验。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / market-neutral
- 基础 alpha：beta-adjusted return differential residual 的均值回复
- regime：流动性较好的 majors / residual 仍平稳 / 没有强单边事件冲击的时段
- filter / veto：rolling ADF 或 cointegration pass、相关性下限、半衰期上限、重大上币/退市/资金费率结算/宏观事件 veto
- risk / sizing / execution overlay：每组 pair 固定 gross notional；`|z|` 入场、`z→0` 平仓、超时退出、结构性破坏止损；两腿合并计费，先按 maker-first / taker fallback 做成本梯度

## 4. 可复刻的最小实验
- **研究假设**：在 `15m`（再下探 `5m`）上，**benchmark-beta 调整后的 pair spread** 会比“原始价格比值 / 原始价差”更快、更稳地回归。
- **可计算定义**：
  1. 取 top 8~10 liquid perp（如 BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LTC/AVAX）。
  2. 用滚动 `3d` 的 `15m` 收益估计每个资产对 market benchmark 的 beta；benchmark 初版可先用 cap-weighted majors，拿不到就先用流动性加权 proxy。
  3. 对任意 pair `(i,j)` 定义 `eps_t = (r_i - β_i r_m) - (r_j - β_j r_m)`，再累积成 spread `S_t = cumsum(eps_t)`，对 `S_t` 做 rolling z-score。
  4. 仅保留 rolling ADF / cointegration pass 且半衰期在 `2~24 bars` 的 pair。
- **最小回测切口**：先跑 `15m`、最近 `6~12` 个月、top 10 majors 全组合；入场阈值先试 `|z|>1.5 / 2.0`，平仓 `z=0` 或 `8 bars` time-stop。
- **最该先看**：
  - 成本后 `PnL / pair-day`
  - `positive pair ratio`
  - 以及它相对“原始价差 z-score”是否真的更稳。
- **成本口径**：必须按“双腿合并”算 round-trip，先做 `8 / 16 / 24 bps` 三档，不要只看单腿手续费。

## 5. 风险与保留意见
- 论文样本是 2018–2020，而且币种生态偏老（XEM / NEO / EOS 这种今天已不是核心），**不能直接把样本收益当今天可复制收益**。
- 这个思路最脆的地方是 **benchmark 定义**：cap-weighted、equal-weight、OI-weighted，都会影响 beta 和 residual 稳定性。
- `1m` 上 beta 估计会非常吵，默认不要一上来就冲 `1m`；先在 `15m -> 5m` 做 portability。
- 即使 residual 看起来平稳，pair 也可能被 funding、合约事件、上架/下架、单币新闻冲断，所以必须配事件 veto 和 time-stop。

## 6. 来源
- Saji Thazhungal Govindan Nair. (2021). *Pairs trading in cryptocurrency market: A long-short story*. *Investment Management and Financial Innovations*, 18(3), 127–141.
- DOI: `10.21511/imfi.18(3).2021.12`
- Readable URL: `https://www.businessperspectives.org/index.php/journals/investment-management-and-financial-innovations/issue-393/pairs-trading-in-cryptocurrency-market-a-long-short-story`
- PDF URL: `https://www.businessperspectives.org/images/pdf/applications/publishing/templates/article/assets/15401/IMFI_2021_03_Govindan.pdf`
- Repo URL: 未见官方公开仓库
