# Funding / basis 别硬扮 15m 主信号：它更适合给 breakout-short 做 crowded-long unwind gate
- 时间：2026-03-18 00:56 UTC
- 类型：论文
- 主题标签：breakout-short/funding/basis/regime/filter/perpetual/crypto/15m
- 证据类型：论文证据 + 公开数据可复现实验

## 1. 这次看了什么
这次看的是 Songrun He、Asaf Manela、Omri Ross、Victor von Wachter 的 working paper《Fundamentals of Perpetual Futures》，重点不是把它误读成“又一个 15m 主信号”，而是把里面的 **perp-spot 偏离 / funding / basis** 理解成一个更适合当前 desk 的 **regime gate / veto / sizing overlay**。

**一句话核心结论：** funding 和 basis 更像“市场拥挤方向温度计”，适合给 `V3 breakout-short follow-up` 做 continuation / failure 过滤，而不是伪装成逐根 15m 裸 alpha。

**一句话说明它怎么证明：** 论文先给 perpetual futures 建了 no-arbitrage benchmark，再用多币种实证去看 futures-spot 偏离的幅度、共振、衰减和套利收益，因此证据强度来自“理论锚 + 跨资产数据检验”，不是单次故事图。

## 2. 核心结论
- perpetual 不是小边角市场：文中给出的 2022 年中位数日成交额约 **101.9bn 美元**，大约是 spot 的 **2x~3.5x**，所以 funding / basis 值得当状态变量看，不只是噪音。
- perp 相对理论基准的 **mean absolute deviation 约 60%~90% annualized**，而且不同币种之间有明显共振；这更像“全市场拥挤/流动性条件”，不是单币独立小误差。
- 这种偏离并没有立刻消失，而是大致 **每年收窄约 11%**；意思不是“没用了”，而是“它是会演化的 crowding/liquidity 状态”。
- 论文里的随机到期套利策略在 BTC perpetual 上，**高交易成本下 Sharpe 约 1.8，低费率/做市层可到 3.5**；这说明 futures-spot 偏离在现实里足够大，值得拿来做过滤层。
- 更关键的一句是：**past return momentum 对 futures-spot gap 的时间序列解释度超过 50%**。直白说，就是行情刚涨过、追涨资金拥挤时，perp 往往更贵、funding 往往更偏正。
- 对我们最有用的翻译不是“去做 cash-and-carry”，而是：**当 downside break 发生时，如果 break 之前市场仍处在 crowded-long 状态，short continuation 可能比“funding 已深负”的环境更可信。**

## 3. 为什么和当前项目有关
这条更像对 `V3 final-verdict / breakout-short follow-up` 的直接补刀，而不是偏题新线：当前 breakout-short 的 blocker 不是“再造一个 entry”，而是 **avoid-chop / continuation-confirmation / 何时别追空**。

这篇 paper 给的可迁移点是：
- `funding`：可当 **拥挤多头是否仍在付钱** 的代理；
- `basis / premium`：可当 **perp 是否还明显贵于 spot/index** 的代理；
- `cross-coin comovement`：提醒我们别只看单币，可先把它当 desk-level risk-on/risk-off 热度计。

所以它在当前项目里更像：
- **过滤器候选**：只在 crowding 仍偏多时允许 breakout-short；
- **仓位管理候选**：crowded-long unwind 时给 full size，already-crowded-short 时降到 half / veto；
- **失败确认候选**：若破位后 funding/premium 已经很冷，很多 short 可能只是追末端。

## 4. 可复刻的最小实验
- **研究假设**：同一套 `breakout-short` 或 `EMA-short` 规则，在“lagged funding 正、premium/basis 正”的状态里，后续 4~16 根 15m bar 的下行延续率更高；而在 funding 已深负的状态里，假突破/追空尾端更多。
- **数据源**：Binance USDT-M public API；`Get Funding Rate History`（公开、8h 更新）+ `Premium Index Kline Data`（公开、可做高频切片）+ 现有 15m price bars。它天然是公开可得，不需要付费数据库。
- **最小可计算定义**：
  - `funding_z` = 最近 30 次 funding 的 z-score（只用入场时点之前最后一个已公布值）；
  - `premium_z` = premium index 最近 96 根 15m bar 的 z-score；
  - `crowded_long` = `funding_z > 0.5` 且 `premium_z > 0.5`；
  - `already_crowded_short` = `funding_z < -0.5` 或 `premium_z < 0`。
- **最小回测切口**：BTC/ETH/SOL perpetual，先跑 120d~180d 的 15m，不改原始 entry，只在 entry 外面包 3 桶：`no gate / crowded_long only / already_crowded_short veto`。
- **最该先看的 3 个指标**：
  1. `4/8/16 bar follow-through`；
  2. `false-break ratio`（4 根内收回破位位之上）；
  3. `net return @ 6bps/side`。

如果第一轮有信息，再做第二步：把它从 veto 升成 **sizing overlay**，例如 `crowded_long=1.0x`、`neutral=0.5x`、`already_crowded_short=0x`。

## 5. 风险与保留意见
- 这篇 paper 研究的是 **perp-spot 偏离与套利锚**，不是直接证明“15m 裸 short 信号有效”。迁移的是状态变量，不是原文策略本体。
- funding 大多是 **8h** 更新，天生偏低频；所以更适合作 gate / sizing，不适合装成逐根 15m 主信号。
- `already negative funding` 不一定等于不能再跌；极端踩踏里，负 funding 还能继续恶化。所以第一轮应先做 bucket comparison，不要一上来写成绝对 veto。
- venue 差异很大。最小实验先固定 Binance，避免把跨所 basis 差异和信号本身混在一起。

## 6. 来源
- He, S., Manela, A., Ross, O., & von Wachter, V. (2024 draft; first draft 2022). *Fundamentals of Perpetual Futures*. Working paper / arXiv.
- DOI：N/A（working paper，当前可读版本见 arXiv / SSRN）
- Readable URL：`https://arxiv.org/abs/2212.06888`
- HTML：`https://arxiv.org/html/2212.06888v6`
- PDF：`https://arxiv.org/pdf/2212.06888`
- SSRN mirror：`https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4301150`
- Public data doc 1：Binance `Get Funding Rate History` — `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`
- Public data doc 2：Binance `Premium Index Kline Data` — `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Premium-Index-Kline-Data`
