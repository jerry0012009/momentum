# 别把这份 2026 repo 只读成“momentum 失效”：对 short-cycle desk，更该保留的是「OOS-valid 但 cost-dead 的 XS 1-day loser-bounce」这条 raw alpha

- 时间：2026-04-15 07:18 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `02_signals.ipynb` + `03_backtest.ipynb`）
- 主题类型：raw alpha
- 基础 alpha：**对 liquid-crypto 横截面做最近 `1d` 相对收益排序，买最近相对落后者、卖最近相对领先者，赌的是 next-day cross-sectional mean reversion；repo 最有价值的新信息不是“它最终没法直接赚钱”，而是它在 2025-2026 OOS 里仍然表现出显著 alpha，只是被换手与成本打死。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / relative-value / mean-reversion / loser-winner / oos-validation / turnover / transaction-cost / market-neutral / dispersion / binance / daily / 15m / 5m / repo / public-data / cost / risk
- 证据类型：repo README + notebook source / embedded outputs + GitHub metadata

## 1. 这次看了什么
主材料是 2026 GitHub repo：
- **Author：** Pramesh
- **Year：** 2026
- **Title：** *Cryptocurrency Cross-Sectional Momentum: A Rigorous Out-of-Sample Analysis*
- **Venue：** GitHub
- **DOI：** N/A
- **Readable URL：** <https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/README.md>
- **Notebook URL：** <https://github.com/prams2104/crypto-momentum-backtest/blob/main/03_backtest.ipynb>
- **Repo URL：** <https://github.com/prams2104/crypto-momentum-backtest>

先把 base alpha 说清楚：

> **这份 repo 对 desk 最值得保留的，不是“20-day momentum 曾经有效”这句老结论，而是：在更近的 2025-2026 样本里，横截面 `1-day loser → next-day bounce / winner → next-day fade` 这条 raw alpha 仍然有显著统计证据，只是原始实现的换手太高，净值被成本直接打穿。**

所以这不是 filter、不是 overlay、也不是解释型摘要。alpha 本体非常清楚：**cross-sectional loser-bounce / winner-fade mean reversion**。

repo 用的是：
- **资产池：** 25 个 liquid cryptos（BTC / ETH / BNB / XRP / ADA / SOL / DOGE / AVAX / DOT / MATIC / LINK / UNI / LTC / ATOM / ETC / XLM / TRX / NEAR / APT / ALGO / VET / ICP / FIL / AAVE / SHIB）
- **数据源：** Binance historical OHLCV
- **样本：** `2020-01-01 ~ 2026-02-05`（2,229 天）
- **频率：** 日频 rebalance
- **测试对象：**
  1. `20d` cross-sectional momentum
  2. `1d` cross-sectional reversal
  3. `low-vol filtered reversal`

## 2. 核心结论
### 2.1 先回答 base alpha
一句话版：

> **对一篮子 liquid cryptos，昨天相对跌得最狠的那一组，明天更容易相对反弹；昨天相对涨得最猛的那一组，明天更容易相对回吐。**

repo 里的实现写得很直接：
- reversal 信号 = `-1 × 最近 1 天收益`
- 再做横截面 percentile rank
- 再做去均值（保持 market-neutral）
- 再做 `sum(|w|)=1` 归一化
- 执行时再 `shift(1)`，避免 lookahead

翻成人话就是：**这不是方向预测，而是 relative-value mean reversion。**

### 2.2 这份 repo 最值钱的，不是“reversal 很猛”，而是“它在 OOS 真的显著，但仍不可直接上线”
repo 最大的优点是：它没有只给 full-sample 漂亮图，而是把样本切成：
- **Training：** `2020-2022`
- **Validation：** `2023-2024`
- **OOS：** `2025-2026`

对 desk 最值钱的是 reversal 这组数：
- **Training alpha：** `-5.5%`，`t = -0.31`（没意义）
- **Validation alpha：** `+17.1%`，`t = 1.37`（还不够硬）
- **OOS alpha：** **`+73.0% annual`，`t = 4.64`**（高度显著）
- **OOS gross Sharpe：** **`4.41`**
- **但日均 turnover：** **`139%`**
- **20 bps 成本后 OOS net Sharpe：** **`-1.73`**
- **gross return `72.8%` → net return `-28.5%`**

这组数的意思非常明确：

> **alpha 不是不存在；问题是“按 repo 这版日频全量轮动去做”，你会先死于换手。**

这和很多“gross 都站不住”的失败案例不一样。这里更接近：
- **预测关系是真的**；
- **但执行形态错了**。

### 2.3 low-vol filter 没救活它，说明问题不只是“挑错币”
repo 还专门试了一个 desk 很自然会想到的修补法：
- 只在 **20d realized vol 较低** 的那半边币上做 reversal

结果并不好：
- filtered reversal 平均活跃币数只有 **`9.4`** 个左右
- 但 **有仓日占比仍高达 `98.7%`**
- **日均 turnover** 反而从 reversal 的 **`1.33`** 升到 **`1.38`**
- 年化换手大约 **`503%`**，比 base reversal 更差
- repo 总结也很直白：**filtered reversal 持续跑输 base strategies**

这说明：
- 问题不只是“币太杂”或“高波币太吵”；
- **只靠 low-vol mask 并不能自然把换手压下来。**

对 short-cycle desk 来说，这个结论很有用，因为它直接排除了一个最便宜、最直觉的修补方向。

### 2.4 momentum 失效，不代表 short-cycle desk 应该放弃 XS relative-value
repo 的另一条 headline 是 20-day momentum：
- Training alpha `+36.2%`，`t=2.02`
- Validation alpha `+13.5%`，`t=1.08`
- OOS alpha `-12.5%`，`t=-0.81`

而作者给出的 regime break 证据也很清楚：
- **pre-2023 cross-sectional dispersion：`3.20%`**
- **post-2023 dispersion：`1.98%`**
- **收缩约 `38%`**

这更像在说：
- 旧的慢速 XS momentum 在近样本里塌了；
- 但 **XS relative-value 本身没死，只是当前更偏向短回吐，而不是慢追涨。**

对我们 desk，这比“动量失效”这句 headline 有用得多。

## 3. 为什么这东西和当前项目直接相关
这轮值得 intake 它，不是因为它能直接上线，而是因为它补了我们当前素材池里一个很关键的空位：

1. **它是 raw alpha，而且 base alpha 很干净。**  
   不是借某个大模型分类器、不是借宏观状态标签，核心就是 `loser vs winner` 的横截面均值回复。

2. **它给的是近样本 OOS 证据。**  
   很多 XS reversal 题材要么是老论文，要么只给 full-sample；这份 repo 至少明确告诉你：**到 2025-2026，这条关系还不是完全死掉。**

3. **它很适合做 short-cycle rescue，而不是 full-clone。**  
   repo 原版是日频轮动；我们 desk 更自然的动作，是把它改成：
   - 慢一些的信号刷新
   - 更稀疏的调仓阈值
   - 更强的 cost veto
   - 更短的 child execution

4. **它能服务不止一条 raw alpha。**  
   这类 `relative loser-bounce` 的排序骨架，后续可以嫁接到：
   - residual momentum / residual reversal
   - sector / theme 内相对强弱回吐
   - pairs / basket stat-arb 的 admission ranking

## 3.5 策略拆解（必填）
- **方向属性：** cross-sectional / relative-value / market-neutral
- **基础 alpha：** 最近一段时间相对跌得更狠的币，更容易在下一段时间对相对赢家做回吐
- **regime：** repo 没把 reversal 明确绑到单独 regime；相反，是 momentum 被 dispersion 变化打垮，reversal 在近样本更有生命力
- **filter / veto：** repo 试过 low-vol 过滤，但没救活；真正缺的更像是 **turnover veto / rebalance threshold / sparse admission**
- **risk / sizing / execution overlay：** market-neutral 去均值、权重归一化、shift(1) 执行、显式 transaction-cost 建模；真正主风险不是 beta，而是 **过度轮动**

## 4. 对 short-cycle desk 的正确读法
### 4.1 不要把它误读成“明天开盘就能日频做 25 币 loser/winner reversal”
repo 自己已经把答案写得很清楚：
- alpha 在 OOS 里存在；
- 但 **139%/day turnover** 让它在 realistic cost 下无法直接交易。

所以 desk 化的正确读法不是“照抄这套 daily rebalance”，而是：

> **保留 raw alpha 本体，但彻底重写它的 rotation / admission / execution 形态。**

### 4.2 更适合 desk 的旁支，不是 low-vol filter，而是 slow-rotation rescue
如果只允许从 repo 往前再走半步，我更倾向于先测这三个修补方向：

1. **rebalance threshold**  
   只有当 rank edge / z-score 超过阈值时才换仓，而不是每天全量对称重排。

2. **staggered rebalance**  
   信号每 `15m` 更新，但组合只在每 `1h` 或 `4h` 的固定时点改一次，强行压换手。

3. **sparse extreme-only admission**  
   不是全市场 loser/winner 全部参与，而是只做最极端尾部那一小撮，换取更高单笔 expectancy。

这三个方向都比“再多加一个 volatility filter”更贴 repo 给出的失败画像。

## 5. 可复刻的最小实验
### 5.1 desk 化映射
这条线迁到我们当前 `15m/5m` 框架时，建议不要机械把“1 天 lookback”翻成“1 根短 bar lookback”，而要保留它的**经济时间含义**。

第一版可以这么映射：
- **主时钟：** `15m`
- **信号 lookback：** `16 / 32 / 96` 根 `15m`（对应 `4h / 8h / 24h`）
- **资产池：** 先从 `12~20` 个 liquid perpetuals 开始，不急着上满 25 个
- **信号：**
  - `ret_L = close_t / close_{t-L} - 1`
  - 横截面排序 → 去均值 → long losers / short winners
- **调仓频率：** 先不要每根 `15m` 都调；先试 `1h` 或 `4h` rebalance
- **子执行：** 若最终下单，用 `5m` 做分批成交/限价挂单/queue 优化

### 5.2 第一版必须跑的 4 个对照组
1. **plain XS reversal**  
   完全不加 filter，只改到 `15m`/`1h` 节奏。

2. **thresholded XS reversal**  
   只有 rank edge 超过阈值才换仓。

3. **extreme-tail only**  
   只做 top/bottom `10%~20%` 的极端 rank，而不是全量配平。

4. **slow-rotation version**  
   lookback 仍然是 `24h` 量级，但 rebalance 只在 `4h` 一次。

### 5.3 这条线最该先看哪些指标
别先被 Sharpe 带着跑，先看：
- `net bps per rebalance`
- `turnover / gross`
- `cost as % of gross pnl`
- `holding horizon`
- `winner leg` 与 `loser leg` 的分腿贡献
- `reversal expectancy` 在不同 rank tail 的斜率
- `dispersion` 与 `reversal alpha` 的关系

因为这轮最重要的问题不是“有没有预测关系”，而是：

> **怎样把“显著但 cost-dead”的 alpha，改写成“可能还活得过成本线”的 alpha。**

### 5.4 下一步怎么测
- **第一步：** 在 Binance USDⓈ-M `15m` 上复刻 `24h` 经济时间窗的 XS loser/winner reversal，先把 plain baseline 跑出来。
- **第二步：** 只加一个变量：`rebalance every 1h / 4h`，观察 turnover 与 expectancy 的弹性。
- **第三步：** 再只加一个最便宜的 admission：`top/bottom tail only`，不要一上来加复杂 regime 分类器。
- **第四步：** 同时跑 `2 / 4 / 6 / 8 bps` roundtrip cost ladder；如果过不了 `4~6 bps`，这条线就先不要升格成 production 候选。
- **第五步：** 若 slow-rotation 后仍死，再把它降级为 **negative-control baseline**，以后所有 XS reversal / lagger-catch-up / residual-fade 新题都必须先对比它。

## 6. 风险与保留意见
- **这条 alpha 目前不能被归类为“可直接落地完整策略”。**  repo 证据反而是在提醒你：原始实现不该直接上线。
- **daily OOS 显著，不代表 `15m/5m` 一定更强。**  高频化常常只会让换手更糟。
- **low-vol filter 已经被 repo 初步证伪。**  不要默认“过滤掉高波币”就能解决问题。
- **近样本有效也可能是阶段性 pocket。**  所以第一轮要严看分段稳定性，而不是只看合并回测。
- **market-neutral 不等于可交易。**  这份 repo 最有价值的教训之一，就是 beta 中性和统计显著并不能替代可实现性。

## 7. 来源
- Pramesh. (2026). *Cryptocurrency Cross-Sectional Momentum: A Rigorous Out-of-Sample Analysis*. GitHub.  
  Repo URL: <https://github.com/prams2104/crypto-momentum-backtest>
- Pramesh. (2026). *README.md*. GitHub.  
  Readable URL: <https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/README.md>
- Pramesh. (2026). *02_signals.ipynb*. GitHub Notebook.  
  Readable URL: <https://github.com/prams2104/crypto-momentum-backtest/blob/main/02_signals.ipynb>
- Pramesh. (2026). *03_backtest.ipynb*. GitHub Notebook.  
  Readable URL: <https://github.com/prams2104/crypto-momentum-backtest/blob/main/03_backtest.ipynb>
- GitHub API metadata: repository created `2026-02-04`, description `Cross-sectional momentum strategy on cryptocurrencies with regime analysis`.

## 8. 本地产物
- Digest：`research/quant_digests/2026-04-15_0718_oos-xsreversal-costdead-alpha.md`
