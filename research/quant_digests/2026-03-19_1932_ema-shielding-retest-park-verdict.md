# 别把 EMA 保护层继续写成“固定距离更安全”：15m crypto 里，fixed band 几乎没改变任何事，真正有信息的是 `retest_hold`，但它现在只够减亏，不够救活 raw alpha
- 时间：2026-03-19 19:32 UTC
- 类型：论文 + 本地 clean replication 复盘
- 主题标签：ema/psar/raw-alpha/retest-hold/no-trade-band/drawdown/confirmation/paper/crypto/15m
- 证据类型：论文全文 + 本地 clean replication artifact

## 1. 这次看了什么
最近已经把 `adaptive no-trade band`、`OI participation`、`slope floor` 等 EMA 保护层摸过一轮，所以这次更值得追一个更窄、也更贴当前收口线的问题：**同一篇论文里，固定阈值保护和 `retest_hold`，到底哪一个真能在 15m crypto 上提供有信息的保护？** 来源仍是 **Paolo De Angelis, Roberto De Marchis, Mario Marino, Antonio Luciano Martire, Immacolata Oliva (2021), *Betting on bitcoin: a profitable trading between directional and shielding strategies***，但这次不复述 headline，而是直接接本地 `scout_ema_shielding_15m` clean replication 结果。

## 2. 核心结论
- **固定阈值几乎是空动作。** 在 `BTC/ETH/SOL 120d 15m`、`EMA20/EMA50 cross`、`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side` 下，`raw_cross` 的跨资产 `mean_total_return=-15.76%`，`threshold_005` 也只是 `-15.54%`，`mean_trades` 两边都还是 `206.7`。翻成人话：**fixed band 几乎没有真正挡掉低质量 cross。**
- **真正有信息的是 `retest_hold`。** 它把 `mean_total_return` 从 `-15.76%` 收窄到 `-6.50%`，把 `mean_max_drawdown` 从 `-20.10%` 压到 `-9.36%`，同时把 `mean_trades` 从 `206.7` 降到 `54.0`，平均延后 `2.39` 根 bar 才进场。也就是：**它不是让 EMA 更会赚，而是让 EMA 少在“刚翻线就追”里亏。**
- **但它还不够把 raw alpha 救活。** `retest_hold` 在 `6bps` 下仍然是 `positive_asset_ratio=0/3`，时间稳定性检查也是 `0/3 positive buckets`，到 `20bps/side` 仍是 `-19.59%`。所以当前更诚实的 desk 读法不是“EMA 保护层成立了”，而是：**它更像 EMA-only 的减亏层 / suppression overlay，还不够升成共享 gate。**
- **对三条收口线的启发是非对称的。** 对 `EMA / PSAR raw alpha focus`，它告诉我们别再浪费时间扫固定距离阈值；对 `Fib confirmation / retest_hold` 与 `breakout-short follow-up`，它给的不是直接 alpha，而是一个更诚实的定义：**“碰到线”不算确认，`touch + close back on the right side` 才像 hold。**

## 3. 为什么和当前项目有关
一句话核心结论：**在当前 desk 语境里，EMA 保护层里真正值得继续测的不是 fixed band，而是 `retest_hold` 这种“先回踩、再证明没失守”的结构确认。**

一句话证明方式：**同一套 15m clean replication 里，fixed band 几乎不改变收益与交易数，而 `retest_hold` 明显压低亏损和回撤，但仍未把 3 个资产里的任何一个翻成稳定正收益。**

这比再开一条与三条收口线无关的新题更值得，因为它直接回答了当前 `EMA / PSAR raw alpha focus` 的一个悬而未决问题：**保护层到底该继续写成“距离阈值”，还是写成“结构 hold”**。

## 4. 可复刻的最小实验
下一步不要再扫更多 fixed threshold；直接做一轮更便宜也更有信息的四臂对照：
1. `raw_cross`
2. `adaptive_band_q1`
3. `retest_hold`
4. `adaptive_band_q1 + retest_hold`

口径继续冻结：`BTC/ETH/SOL | Binance 120d | 15m | next-bar open | no-overlap | 1 ATR stop | 2 ATR target | 8-bar time stop | 6/10/15bps`。

先只看 4 个指标：
- `mean_total_return`
- `mean_max_drawdown`
- `trade_retention`
- `3-bucket time stability`

判断规则也应更直接：如果组合版仍然 `0/3 positive assets`，或 trade retention 掉得太狠，那就把这条线正式归档成 **EMA-only suppression evidence**，不要再包装成 shared gate。

## 5. 风险与保留意见
- 源论文是 **2019 BTC 1m**，本地复盘是 **120d / BTC+ETH+SOL / 15m**；这次迁移的是“保护层读法”，不是原文参数。
- 当前 clean replication 统一冻结在同一出场框架下，所以它回答的是“entry protection 有没有边际价值”，不是“换 exit 后能不能翻正”。
- `retest_hold` 的改善很大一部分来自少做交易；因此后续必须继续盯 `trade_retention`，避免把“抑制交易”误写成“增加 alpha”。

## 6. 来源
1. De Angelis, P., De Marchis, R., Marino, M., Martire, A. L., & Oliva, I. (2021). *Betting on bitcoin: a profitable trading between directional and shielding strategies*. Decisions in Economics and Finance.
   - DOI: https://doi.org/10.1007/s10203-021-00324-z
   - Readable URL: https://link.springer.com/article/10.1007/s10203-021-00324-z
2. 本地 clean replication artifact：
   - `reports/artifacts/scout_ema_shielding_15m/overall_summary.csv`
   - `reports/artifacts/scout_ema_shielding_15m/asset_summary.csv`
   - `reports/artifacts/scout_ema_shielding_15m/time_stability_drycheck.csv`
   - `reports/site/factors/scout_ema_shielding_15m/report.html`
