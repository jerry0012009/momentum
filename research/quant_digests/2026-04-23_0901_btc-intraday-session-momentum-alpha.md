# 别把 *Bitcoin intraday time series momentum* 只读成“BTC 特例”：对 short-cycle crypto desk，更该先拆的是「伪 session 前段收益 × 后段延续」这条 raw alpha
- 时间：2026-04-23 09:01 UTC
- 类型：论文（metadata + abstract audit）
- 主题类型：raw alpha
- 基础 alpha：同一伪交易时段里，前段收益率对后段收益率有正向预测；高成交量 / 高波动时段更强
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / single-asset / intraday / momentum / time-series-momentum / volume / volatility / session-structure / BTC / 1m / 3m / 5m / 15m
- 证据类型：论文证据（当前可见范围：Crossref abstract + OpenAlex metadata；非全文精读）

## 1. 这次看了什么
Shen、Urquhart、Wang 的 2022 年论文 *Bitcoin intraday time series momentum*。这篇东西最值得先抓住的，不是“Bitcoin 也有日内动量”这句大话，而是一个很适合我们 desk 立刻做最小实验的可计算骨架：**把 24/7 市场按成交量切成伪 session，再看 session 前段回报是否能预测后段延续。**

## 2. 核心结论
- 论文摘要给出的主结论很直接：**首半小时收益率对末半小时收益率有正向预测**，也就是典型的 intraday time-series momentum，而不是反转。
- 作者特别指出：**首个交易时段里“成交量最高”或“波动率最高”的那些窗口，预测性最强**。这点对我们更值钱，因为它天然像一个 admission gate，而不是逼你全天候开机。
- 摘要还说：**基于这条动量的 market timing / asset allocation 有显著经济收益，且在 BTC 下跌阶段更明显**。翻成人话：这不是只在单边牛市才看起来好看的顺风车信号。
- 机制解释上，作者把这条效应更偏向于**liquidity provision（流动性提供/短时库存消化）**，而不是“晚到信息继续扩散”。这意味着它可能更像短时 order-flow / liquidity imbalance 的价格延续，而不是宏观级别的慢变量。

## 3. 为什么和当前项目有关
这篇和 `momentum` 当前主线的关系很直接：它补的是一个**比“普通 15m 动量”更结构化的 raw alpha**。我们最近已经扫了很多 breakout、pairs、cross-sectional、carry；这篇则提供一个单资产、超短日内、规则极简的 continuation 骨架。

更重要的是，它天然能拆成我们熟悉的层次：
- base alpha 是“前段涨跌 → 后段继续”；
- volume / volatility 负责 admission；
- regime 可以再叠“仅在下跌市或高 realized vol 时启用”；
- child execution 则可落到 `1m/3m/5m`。

所以它不是泛解释型材料，而是一条**可独立复现、且可继续嫁接到 execution / filter / sizing 的 raw alpha 母体**。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：伪 session 前段 return 对同一 session 后段 return 的正向预测
- regime：优先高成交量 / 高波动窗口；可再测 BTC 下跌期是否更强
- filter / veto：低成交量静默窗口、极端跳价后回吐窗口可作为 veto 候选
- risk / sizing / execution overlay：固定持有到 session 尾段；用 ATR / realized vol 缩仓；`1m/3m` maker-first 分批入场

## 4. 可复刻的最小实验
- 研究假设：在 Binance BTCUSDT perp 上，**某个 1h 伪 session 的前 15m 或前 20m 收益**，能否预测后 15m/20m 的同向延续。
- 一个可计算定义：以 `1h` 为 parent，切成 `4 x 15m` 或 `3 x 20m`；若前段 return > `z_th` 且该 parent 的前段成交量 / realized vol 处于过去 `20d` 同时段分位前 30%，则按同方向持有到 parent 尾段；反向对空头同理。
- 最小回测切口：先只测 `BTCUSDT`，周期优先 `5m`（再下钻 `1m/3m` 做执行）；样本先取近 `180d ~ 365d`。
- 最该先看 2 个指标：**成本后 avg bps/trade** 与 **按 volume/vol bucket 分层后的 hit-rate / expectancy**。如果不做 bucket 分层，这条信号大概率会被“普通时段”稀释。

## 5. 风险与保留意见
- 当前我拿到的是 **metadata + abstract**，不是全文，所以不能把样本切法、统计检验和交易口径说得过满。
- 论文对象是 Bitcoin，本身就比大部分 alt 更深、更连续；迁移到 alt 时，可能会从“纯 continuation”变成“高流动性时 continuation、低流动性时反转”。
- 这类信号很容易受手续费、滑点和 funding 挤压；若只看方向命中率，不看 net expectancy，会被误导。
- 24/7 crypto 没有天然开收盘，所谓 session 切法本身就是模型选择；我们最好把 `30m/20m/15m` 切法并排测，而不是只信论文原口径。

## 6. 来源
- Dehua Shen, Andrew Urquhart, Pengfei Wang. (2022). *Bitcoin intraday time series momentum*. *The Financial Review*, 57(2), 319-344.
- DOI: `10.1111/fire.12290`
- Readable URL: `https://doi.org/10.1111/fire.12290`
- Metadata URL: `https://api.openalex.org/works/https://doi.org/10.1111/fire.12290`
- Abstract metadata URL: `https://api.crossref.org/works?query.title=Bitcoin%20intraday%20time%20series%20momentum`
