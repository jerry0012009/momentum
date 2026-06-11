# Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread — fresh intake keep_P1

- 时间：2026-03-27 00:58 UTC
- 对象：`research/quant_digests/2026-03-26_2233_btc-ada-57s-tick-lag-alpha.md`
- 轮次角色：bot3 fresh intake 最小首判
- 结论：`keep_P1`
- Assigned Rank: `190`

## 本轮只回答一个问题
`BTC -> ADA` 的 `57s` tick-lag 现象，在当前 desk 可交易口径下，是否已经值得保留成一个单轴对象进入 survivor。

## 这轮保留的不是泛化叙事，而是唯一可执行对象
本轮保留的不是“BTC 会带着山寨走”这种宽泛废话，而是下面这条压缩后的 executable hypothesis：

`BTC-shock ADA-underreaction 1m beta-hedged catch-up spread`

翻成人话：当 BTC 先出现显著短时冲击，而 ADA 在同窗内同步反应不足时，做 **long ADA / short β·BTC** 的 catch-up spread；研究主窗口先钉在 `1m`，允许同时检查 `3m` 作为 bar 化后的上限近邻，但不把对象扩写成整个跨币 lead-lag family。

## 为什么它通过 fresh intake
1. **论文给的是“明确时长”，不是空泛方向。**
   - 这篇 2023 开放获取论文真正值钱的地方，是把 `BTC -> ADA` 的 lead time 压缩到 **`16~118s`，均值约 `56.5s`**；
   - 这会直接改变 desk 的研究姿势：它更像 `1m/3m` 的超短 catch-up spread pocket，而不是 `15m` 级别的慢速方向因子。
2. **对象已经可以被压成单一假设。**
   - digest 里已经把策略骨架说清楚：
     - 只在 **BTC 冲击显著**、**ADA 同步欠反应** 时开仓；
     - 优先用 **ADA vs β·BTC** spread 版本，而不是裸做 ADA 方向；
     - 成本与滑点必须显式入账；
   - 这说明它不是只能停留在“论文有意思”的题材层，而是已经形成一个值得做一次 cheap decisive follow-up 的具体对象。
3. **当前最大的未知是“现代市场结构还剩多少”，这正适合 survivor 的唯一预算。**
   - 论文主样本来自 `2019~2021`、HitBTC tick 数据；
   - 文中还明确指出 lag 随时间显著缩短；
   - 所以下一轮最值钱、也最便宜的诚实问题不是继续讲故事，而是直接问：在今天的 Binance 风格公开数据上，这个 edge 到 `1m/3m` bar 化后是否还留得住，且是否不是单纯 BTC beta 暴露。

## 为什么这轮不直接升 P2
它通过 fresh intake，但还没到直接进 `P2` 的程度，原因也很明确：

1. **现有证据还是老市场结构下的一篇单资产对论文。**
   - 样本是 `BTC/ADA` 单对；
   - 主分析交易所是 HitBTC；
   - 还没有回答 2025~2026 主流 CEX / perp 结构下 edge 是否已被更快价格发现和成本压扁。
2. **目前还没完成最关键的 modern transfer / honesty check。**
   - 还没用公开 `1s/1m` 数据做一次最小复核；
   - 还没证明收益来自 ADA 欠反应补动，而不是“BTC 涨、ADA 也涨”的方向 beta 暴露；
   - 还没把 `2/4/6 bps` 一类的实际 round-trip friction 明确带入。
3. **这正好匹配 survivor 的职责边界。**
   - 给它一次唯一 follow-up，去回答“现代公开数据 + 成本后”是否还有残差；
   - 若留不住，就应诚实 park，而不是继续把 broad lead-lag family 拉回前排。

## 单一句子结果
`Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread` 的 fresh intake 已收口为 `keep_P1`：当前值得保留的不是泛化“BTC 领先山寨”的叙事，而是一个秒级到 `1m/3m` 的单轴 catch-up spread 假设；它值得用唯一一次廉价 follow-up 去回答今天的公开市场结构里是否还留得住成本后残差。

## 运行态回写
- `Fresh intake slot`：更新为 `Rank 190 / BTC-shock ADA-underreaction 1m beta-hedged catch-up spread`，结论 `keep_P1`
- `Surviving candidate slot`：载入 `Rank 190`，`followup_budget_remaining = 1`
- `cycle_plan[3]`：写入上述单句结果并标记 `done`
- 其余前排槽位保持不变
