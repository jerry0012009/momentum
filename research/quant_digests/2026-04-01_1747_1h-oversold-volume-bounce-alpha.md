# 别把这份 2025 新 repo 只读成“stat-arb 简历项目”：对 short-cycle desk，更该先测的是「1h 跌幅冲击 × 放量确认 × 24h bounce capture」这条单币 mean reversion raw alpha
- 时间：2026-04-01 17:47 UTC
- 类型：2025 GitHub 新仓库 source audit（`README.md` + `src/strategy.py` + `src/backtester.py` + `results/performance_metrics.json` + `results/backtest_results.csv` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：单币在 `1h` 内出现大幅下跌且伴随异常放量时，短期更容易出现 oversold bounce；alpha 本体是“冲击后的反弹捕捉”，不是 funding、不是 filter。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/mean-reversion/shock-reversal/volume-confirmation/oversold-bounce/hourly/15m/5m/3m/1m/kraken/binance/bybit/okx/repo/public-data/cost
- 证据类型：2025 GitHub repo source audit（工程主证据，样本很短）

## 1. 这次看了什么
### 一句话核心结论
**这轮更值得 intake 的，不是 repo 给自己贴的“stat-arb”标签，而是它已经写成完整骨架的一条单币 raw alpha：`1h 跌超 2% + 成交量超过近 24h 均量 1.5x` 后，做接下来 `24h` 的 bounce。**

### 一句话它是怎么证明的
**证明方式不是论文，而是源码 + 回测产物直接把信号、持有期、成本和交易明细都摆出来了；更关键的是，`4h/8h/12h` 全部 after-cost 不行，只有 `24h` 留下了明显正边，这让我们能很快判断“alpha 在哪段 horizon 才活”。**

## 2. base alpha 是什么
这次的 **base alpha 很清楚**：

1. 先找 **短时极端下跌**：`1h return <= -2%`；
2. 再要求这根下跌 bar **不是普通噪音**，而是有 **放量确认**：`volume / rolling_24h_avg >= 1.5`；
3. 一旦同时满足，就把它视为 **oversold shock**；
4. 交易逻辑不是继续追空，而是做 **未来若干小时到 24h 的反弹回补**。

翻成人话：**这不是“均值回归概念课”，而是一条可以直接写成规则的 shock-to-bounce raw alpha。**

## 3. 为什么这轮值得写
- 最近 intake 已经积累了不少 `pairs / XS / carry / microstructure`；这份 repo 补的是一条**更朴素、可独立复现的单币事件型 MR skeleton**。
- 它很适合当前阶段：**信号简单、数据公开、first verdict 很快**，不需要外部数据，不需要复杂特征工程。
- 它也很诚实：repo 自己把 **不同持有期的成败** 摆出来了，不需要我们先替它美化结论。

## 4. 来源信息
### 主工程来源
- **Author / Repo owner：** Skylar Shi（GitHub: `skylarshi123`）
- **Year：** 2025
- **Title：** `crypto-stat-arb`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/skylarshi123/crypto-stat-arb>
- **Repo URL：** <https://github.com/skylarshi123/crypto-stat-arb>
- **GitHub metadata：** created `2025-12-31T08:54:06Z`，pushed `2025-12-31T09:22:42Z`，default branch `main`
- **关键文件：**
  - `README.md`
  - `src/strategy.py`
  - `src/backtester.py`
  - `results/performance_metrics.json`
  - `results/backtest_results.csv`
  - `results/detailed_trades.csv`

## 5. repo 具体是怎么把这条 alpha 写出来的
### 5.1 数据与 universe
- 数据源：Kraken API 公共 OHLCV
- 频率：`1h`
- 样本：README 写的是 `30 days from Kraken`，结果文件实际约 `20` 个 trading days、`2,884` 个小时级观测
- 标的：`BTC/USD`、`ETH/USD`、`SOL/USD`、`AVAX/USD`

也就是说，它不是跨市场复杂 stat-arb，更像一个 **4 个 major coin 的单币 shock-reversal 实验台**。

### 5.2 Entry：跌幅冲击 + 放量确认
`src/strategy.py` 把入场写得非常直白：
- `price_drop_threshold = -0.02`
- `volume_ratio_threshold = 1.5`
- `volume_lookback_hours = 24`

也就是：
- 当前 `1h return <= -2%`
- 且当前成交量至少是近 `24h` 平均的 `1.5x`

两个条件同时满足，`signal = 1`。

### 5.3 Exit：不猜底部结构，只测固定持有期
`src/backtester.py` 没搞花哨退出，而是直接测 `4 / 8 / 12 / 24h` 四档 holding period：
- 同一币种若已有仓位，新的信号先跳过，避免重叠；
- 到期后按最近可用 bar 平仓；
- 只做 long-only bounce capture。

这点对 desk 很有价值：**alpha 本体先和 exit 解耦，再判断哪段持有期真的值得留下。**

### 5.4 Cost：repo 没装作“零摩擦”
repo 明确写了：
- 单边成本 `20 bps`
- round-trip `40 bps`

虽然这个成本口径很粗，但至少不是“毛收益好看就算赢”。

## 6. 3 个最值得记住的硬数据点
1. **只有 `24h` holding period after-cost 明显存活**：`total_net_return = 34.33%`，`win_rate = 72.7%`，`num_trades = 22`，`max_drawdown = 8.2%`。
2. **短持有期全部不行**：`4h = -12.60%`，`8h = -17.60%`，`12h = -0.38%`；也就是说，repo 这条 alpha 不是 1~2 个 bar 就反弹的 ultra-fast scalp。
3. README 还给了一个很有用的执行线索：**42% 的信号出现在 `15:00 UTC`**，说明它可能和欧美时段的风险释放 / rebound pocket 有关。

## 7. desk 最该偷走的，不是“stat-arb”这个词
如果按 repo 名字去读，很容易以为这是“统计套利”。但源码其实更像：
- **单币 shock admission**
- **volume confirmation**
- **固定持有期 bounce capture**

对我们更值钱的，不是“它是不是严格 stat-arb”，而是这条 skeleton 很适合拆成：
- **raw alpha 本体：** oversold shock → bounce
- **确认层：** volume spike
- **执行层：** 15m / 5m 入场切分、maker/taker 选择、cost ladder
- **风险层：** 单边 news/liquidation veto、max hold、再冲击止损

## 8. 和当前 1m / 3m / 5m / 15m 的关系
这条线**可以服务短周期 desk**，但要诚实转译：

### 8.1 不要把 `1h` trigger 硬说成 `1m alpha`
repo 的原始 trigger 是 **小时级冲击**，所以它更适合：
- 用 `15m` 先做 first verdict；
- 用 `5m` 做执行精修；
- `1m / 3m` 只在确认存在 alpha 后再拿来抠 entry/exit。

### 8.2 正确 desk 化方式
更合理的迁移不是“直接把 -2% 套到 5m”，而是：
- 用 `4 x 15m` 或 `12 x 5m` 拼成一个 `1h shock window`；
- 把原 repo 的 `24h hold` 拆成 `8h / 12h / 16h / 24h` 梯子；
- 再看是否存在更适合 perp 的 `partial take-profit + max_hold` 变体。

### 8.3 它属于哪类 raw alpha
它不是 breakout，不是 trend，不是 carry。
它更接近：
- **single-asset mean reversion**
- **event-driven shock reversal**
- **volume-confirmed oversold bounce**

## 9. 可复刻的最小实验
### 实验 A：15m transfer check（最优先）
- **标的：** BTC / ETH / SOL / AVAX 永续，必要时加 LINK / DOGE 作为扩展
- **bar：** `15m`
- **shock 定义：** 最近 `4` 根 `15m` 的累计收益 `<= -2%`
- **volume 定义：** 最近 `4` 根 `15m` 成交量 / 过去 `96` 根 `15m` 平均量 `>= 1.5`
- **entry：** 下一根 `15m` 开盘做多
- **exit：** `8 / 12 / 16 / 24h` 四档 max hold，对照 `mid-bounce take-profit`
- **成本：** round-trip `6 / 10 / 14 / 20 / 30 / 40 bps`

### 实验 B：5m execution refinement
在实验 A 成立后，再下钻：
- 同一个 `1h shock flag` 触发后，比较 `immediate 5m entry` vs `等首个止跌 5m bar 再进`；
- 比较 `一次性进场` vs `2 段进场`；
- 检查更细粒度执行能否提升盈亏比，而不是单纯增加噪音。

### 实验 C：失效环境识别
加三个 veto：
1. shock 后下一小时继续放量新低；
2. 同期 BTC 出现更大级别单边崩跌；
3. funding / basis / liquidation 异常放大。

它们不改变 alpha 本体，只是帮我们识别 **“不是 oversold bounce，而是趋势继续踩踏”** 的场景。

## 10. 下一步怎么测
1. **先忠实复刻原 skeleton**：不要第一刀就把 -2% / 1.5x / 24h 全改烂，先确认原始 shock-bounce 是否能在 liquid perp transfer 成立。
2. **优先跑 holding-period ladder**：因为 repo 已经明确提示，alpha 的关键不在 signal 有无，而在 **得给它足够时间反弹**。
3. **先用 `15m` 做 existence test**，别急着上 `1m/3m`；如果 `15m` after-cost 都不活，细频率大概率只是更快死。
4. **把成本分档做厚**：这条线是典型会被摩擦吃掉的 MR，必须一开始就看 `10~40bps` 梯子。
5. **若 15m 成立，再决定是否加 shared gate**：比如大盘 regime veto、liquidation veto、session gate；不要反过来让 overlay 冒充 alpha。

## 11. 这条线最容易错在哪
- **把 repo 的“34.33% 总收益”直接当成强证据。** 样本只有约 `20` 天、`22` 笔交易，证据强度其实很一般。
- **忽视短持有期全部失败。** 这说明反弹不是立刻发生；如果 desk 硬要把它压成超短频，可能正好把 edge 切没。
- **忽视 single-name crash risk。** 均值回归最怕真正的 regime break / liquidation cascade。
- **把它误标为纯 stat-arb。** 实际更像单币 shock-reversal，而不是 market-neutral relative-value。

## 12. 对当前项目的直接意义
这条主题值得进研究池，因为它满足当前优先级较高的几条：
- **主题类型：raw alpha**
- **基础 alpha 清楚**
- **数据公开可得**
- **可直接拆成 entry / exit / sizing / risk / cost**
- **可以很快做 15m / 5m 的 first verdict**

如果要一句话概括：**这不是“又一个教学 repo”，而是一张很干净的 alpha existence card——先看 `1h 跌幅冲击 × 放量确认` 在 liquid perp 上能不能稳定换来 `8~24h` 的 bounce。**

## 13. 来源链接
- Repo：<https://github.com/skylarshi123/crypto-stat-arb>
- README：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md>
- Strategy：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/strategy.py>
- Backtester：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/backtester.py>
- Metrics JSON：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/performance_metrics.json>
- Backtest summary CSV：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/backtest_results.csv>
- Detailed trades CSV：<https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/detailed_trades.csv>
- GitHub API metadata：<https://api.github.com/repos/skylarshi123/crypto-stat-arb>
