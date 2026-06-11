# 别把这份 2026 大而全引擎只读成“策略超市”：对 short-cycle desk，更该先测的是「BB/z-score overshoot × RSI confirm × trend-veto」这条单币完整 mean reversion raw alpha
- 时间：2026-04-02 23:56 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `src/strategies/mean_reversion.py` + GitHub API metadata）+ 2025 intraday BTC mean reversion thesis 作 sanity anchor
- 主题类型：raw alpha
- 基础 alpha：**单资产价格在短窗内对 rolling mean 的偏离达到异常 z-score 后，后续若不是顺着更大级别趋势继续扩散，就更容易向均值/中轨回吐；alpha 本体是“overshoot snapback”，不是 RSI，也不是 trend filter。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/bollinger-bands/zscore/rsi-confirmation/trend-veto/keltner-squeeze/atr-stop/zscore-bucket/5m/15m/1m/3m/repo/paper/public-data/cost
- 证据类型：2026 repo 源码证据（主）+ 2025 thesis 频率/成本 sanity anchor（辅）

## 1. 这次看了什么
### 一句话核心结论
**这轮最值得 intake 的，不是 repo 里“20+ strategies”那串清单，而是已经被源码写成完整闭环的一条单币 raw alpha：`|z-score| >= 2` 的 BB overshoot，配 `RSI` 确认、`50-bar EMA slope` 反向 veto、`ATR stop` 与 `z-score/bb-mid` 回归出场。**

### 一句话它是怎么证明的
**证明方式不是作者在 README 里吹结果，而是源码把策略四层全写死了：异常偏离定义、入场 admission、出场与止损、按 z-score 分桶统计 edge。** 这比“又一个均线/RSI 教程”更像可直接下场做最小实验的完整策略卡。

## 2. base alpha 是什么
先把这句说死：

> **base alpha = 单币短周期 overshoot snapback。**

更具体一点：
1. 先用 `z = (close - rolling_mean) / rolling_std` 衡量价格对短窗均值的偏离；
2. 当 `|z|` 足够大时，把它当成“局部过冲”，不是普通噪音；
3. 如果这次过冲没有获得更高一级趋势的继续扩散许可，那么价格更容易向均值回归；
4. 因此可以在 oversold 时做多、overbought 时做空，吃回到中轨/均值附近的那一小段回吐。

翻成人话：**不是“RSI 超卖就抄底”，而是“价格已经偏离到统计意义上的极端，再用 RSI 与更高一级趋势状态判断，这次偏离到底是该继续追，还是该赌回归”。**

## 3. 为什么这轮值得写
- 最近 intake 里 `pairs / stat-arb / carry / order-flow` 已经非常多；这轮补一张**单币 5m/15m mean reversion 完整卡**，能显著提高素材池多样性。
- 它不是纯 filter 主题。**raw alpha 本体非常清楚**，而 RSI / trend / squeeze 都只是 admission 或 veto 层。
- 它和当前 desk 节奏很对：
  - `5m / 15m` 是 repo README 明写的目标频率；
  - 源码里已经包含 `entry / exit / sizing / stop / bucket stats`；
  - 不需要外部稀缺数据，只用公开 OHLCV 就能先跑 existence test。
- 相比再补一篇新 pairs，这条线更容易在一晚之内做出**可解释的 ablation**：
  - base overshoot 是否有边；
  - RSI 是否增益；
  - trend veto 是否减少左侧抄底的灾难；
  - 哪个 `|z|` 桶费后还能活。

## 4. 来源信息
### 主工程来源
- **Repo owner：** `mefai-dev`
- **Year：** 2026
- **Title：** `mefai-autotrade`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/mefai-dev/mefai-autotrade>
- **Repo URL：** <https://github.com/mefai-dev/mefai-autotrade>
- **GitHub metadata：** created `2026-03-25T12:26:28Z`，pushed `2026-03-29T21:37:33Z`，default branch `master`，⭐ `3`
- **关键文件：**
  - `README.md`
  - `src/strategies/mean_reversion.py`

### 频率/成本 sanity anchor（不是主证据）
- **Author：** Marja Ekström
- **Year：** 2025
- **Title：** *Bitcoin trading performance evaluation: A comparative study of momentum and mean reversion strategies from 2020 to 2025*
- **Venue：** Haaga-Helia University of Applied Sciences, Master’s thesis
- **DOI：** 无 DOI
- **Readable URL：** <https://www.theseus.fi/handle/10024/902903>
- **PDF URL：** <https://www.theseus.fi/bitstream/handle/10024/902903/Ekstrom%20Marja.pdf?sequence=2>
- **这篇在本文中的角色：** 不是拿来证明 repo 必然有效，而是给一个更朴素的先验：**BTC 的 intraday mean reversion 在更慢一级（1h）确实曾有存在证据，repo 则把它 desk 化成 5m/15m 更完整的多层 admission 版本。**

## 5. repo 具体是怎么把这条 alpha 写出来的
## 5.1 目标频率就是我们关心的 5m / 15m
README 的策略表明确把这个模块标成：
- **Strategy：** Mean Reversion
- **Description：** Bollinger Band + z-score statistical mean reversion
- **Timeframes：** `5m, 15m`

这点很关键，因为它不是“日频论文硬下沉”，而是工程作者一开始就把它摆在 short-cycle 档位里。

## 5.2 base signal：不是单看 BB 触边，而是先看 z-score 极端
源码默认参数：
- `bb_period = 20`
- `bb_std = 2.0`
- `zscore_lookback = 20`
- `zscore_entry = 2.0`
- `zscore_exit = 0.5`
- `zscore_stop = 3.5`

也就是：
- **入场门槛：** `|z| >= 2.0`
- **均值回复出场：** long 回到 `z >= -0.5`，short 回到 `z <= 0.5`
- **统计止损：** long 若继续恶化到 `z < -3.5`，short 若继续恶化到 `z > 3.5`，直接认错

所以最准确的 desk 读法是：
**BB 只是把“均值”可视化，真正的 alpha admission 核心是“异常偏离已经达到统计极端”。**

## 5.3 入场不是裸左侧，而是三层 admission
源码的 long/short 入场逻辑不是只看 z-score，还叠了 3 层 admission：

### A. RSI 确认
- 默认 `rsi_period = 14`
- 默认要求：
  - `z > 0` 做空时，`RSI >= 70`
  - `z < 0` 做多时，`RSI <= 30`

翻成人话：**统计偏离要和传统“过热/过冷”方向一致，才允许开仓。**

### B. 高一级趋势 veto
- 默认 `trend_ema_period = 50`
- 用 `EMA(50)` 最近 `5` 根 bar 的 slope 判断趋势方向
- 若：
  - 当前 overbought，但更高一级仍是明显上行斜率，则**不做空**；
  - 当前 oversold，但更高一级仍是明显下行斜率，则**不做多**。

这层非常值钱，因为它直接回答了均值回复最常见的死法：
> **不是 every overshoot 都该 fade；在强趋势里，很多所谓 oversold 只是趋势中的正常扩散。**

### C. 可选 squeeze gate
- `require_squeeze = False` 默认关闭
- 若打开，就要求 Bollinger Band 处于 Keltner Channel 内（BB inside KC）

这说明工程作者也承认：
- squeeze 更像**可选的 range admission**；
- 它不该和 base alpha 本体混为一谈。

## 5.4 出场写得很实用：均值回归 + ATR 价格止损双轨制
源码里同时存在两套退出逻辑：

### 统计出场
- long：`z >= -0.5` 即认定“回归到差不多了”
- short：`z <= 0.5` 即平仓

### 价格出场
- take profit：直接挂在 **Bollinger middle band**
- stop loss：
  - long：`entry - 2.5 * ATR(14)`
  - short：`entry + 2.5 * ATR(14)`

也就是：
**它不是纯 z-score 策略，也不是纯 BB 策略，而是“统计极端入场 + BB 中轨止盈 + ATR 价格防守”的混合壳。**

这很 desk：
- 统计层负责发现错位；
- BB 中轨负责提供朴素、透明的回归目标；
- ATR 负责对付“这次不是回归，是 regime shift”的尾部风险。

## 5.5 Sizing 也不是空白
源码默认：
- `risk_pct = 1.0`
- 用 `calculate_position_size(account_balance, entry, stop, risk_pct)` 按止损距离算仓位
- README 的全局风险模块还写了：
  - 风险型 sizing
  - ATR-based stop
  - correlation filter
  - daily/weekly loss limits

也就是说，**这条线不是只有 signal，没有仓位骨架。**

对我们来说，最值钱的不是 repo 的大一统风控平台，而是这条单策略最小闭环已经完整：
- entry
- exit
- stop
- size
- risk check

## 5.6 这份 repo 最独特的一点：它把 edge 按 z-score 桶追踪
源码显式维护 4 个桶：
- `1.5-2.0`
- `2.0-2.5`
- `2.5-3.0`
- `3.0+`

每个桶都记录：
- `trades`
- `win_rate`
- `avg_pnl`
- `total_pnl`

这点对 desk 特别有用，因为它让我们能直接回答：
> **费后真正有边的是“轻微过冲”还是“深度过冲”？**

很多均值回复策略死在这里：
- `|z|` 太小：噪音太多，吃不掉成本；
- `|z|` 太大：经常不是回归，而是 regime break / liquidation cascade。

repo 把这件事从一开始就工程化成了**bucket governance**，这比“手动试几个阈值”更适合 desk 素材池。

## 6. 5 个最值得记住的硬数据点
1. **目标频率不是模糊的。** README 明写 mean reversion 模块主要跑 `5m / 15m`。  
2. **默认入场阈值清楚。** `|z| >= 2.0` 才进，不是任何 BB 触边都做。  
3. **默认回归出场清楚。** `zscore_exit = 0.5`，也就是回到“离均值不远”就收。  
4. **默认止损有两道。** 统计止损 `|z| > 3.5` + 价格止损 `2.5 × ATR(14)`。  
5. **bucket 治理已经内建。** repo 不是只给你一个整体 Sharpe，而是支持按 `1.5-2.0 / 2.0-2.5 / 2.5-3.0 / 3.0+` 分桶追 edge。  

## 7. 这条线最该怎么 desk 化理解
最容易犯的错，是把这条策略读成“BB + RSI + trend filter 的指标拼盘”。

更好的拆法是：
- **raw alpha：** 单币 overshoot snapback
- **stat trigger：** `|z| >= threshold`
- **traditional confirmation：** RSI overbought / oversold
- **regime veto：** 50-bar EMA slope 不和你对着干
- **execution/risk：** BB 中轨出、ATR 止、仓位按止损距离算
- **post-trade governance：** 统计边际按 `|z|` 桶来更新

换句话说：
**alpha 本体很老，但 repo 的价值在于把“怎么让它别死在强趋势和成本里”写成了清晰的 admission + governance 结构。**

## 8. 和当前 1m / 3m / 5m / 15m 的关系
### 8.1 首选 15m 做 existence，不要先冲 1m
因为：
- repo 本身就支持 `5m / 15m`；
- `1m / 3m` 上 BB/z-score 容易被 microstructure 噪音、手续费和滑点吃掉；
- 这类 MR 最容易在更细级别上出现“看着经常回归，净值却被摩擦磨平”。

所以更合理的次序是：
- **先 `15m` 验 existence；**
- 再去 `5m` 看是否能提高 trade count 但仍保留费后边；
- 最后才决定要不要把 `1m / 3m` 只当 execution refinement，而不是主信号级别。

### 8.2 这条线适合单币，不适合伪装成 shared gate
因为它的 base alpha 非常明确：
- 就是单资产局部过冲后的回归；
- 不是给别的 alpha 做 overlay；
- 不是单独的 regime classifier。

如果后面要服务其他 alpha，也应当是作为**可迁移的 bucket/trend-veto 方法论**，而不是硬把它改写成 shared filter 主题。

## 9. 最小可复现实验
### 实验 A：15m 单币 baseline（最优先）
- **标的：** `BTC / ETH / SOL / BNB` 永续，先从 BTC+ETH 起步
- **bar：** `15m`
- **base signal：**
  - `z = (close - SMA20) / rolling_std20`
  - long 当 `z <= -2.0`
  - short 当 `z >= 2.0`
- **exit：**
  - 版本 1：`z` 回到 `-0.5 / +0.5`
  - 版本 2：触 `BB middle band`
  - 版本 3：两者谁先到谁出
- **stop：** `2.5 × ATR(14)`
- **成本：** round-trip `8 / 12 / 20 / 30 bps`

这一轮只回答一句：
> **在 15m perp 上，单币 overshoot snapback 费后还有没有活口。**

### 实验 B：admission ablation
对同一套标的与成本，依次比较：
1. `z-score only`
2. `z-score + RSI`
3. `z-score + RSI + trend veto`
4. `z-score + RSI + trend veto + squeeze`

目的不是找最好看的曲线，而是问：
- edge 到底来自 raw alpha 本体，还是来自 filter？
- squeeze 是真增益，还是只会让 trade count 掉到没法覆盖成本？

### 实验 C：z-score bucket 治理
固定最佳 admission 后，比较：
- 只做 `2.0-2.5`
- 只做 `2.5-3.0`
- 只做 `3.0+`
- `2.0+` 全做

重点看：
- 哪个桶的 **gross 胜率 / avg pnl** 最好；
- 哪个桶的 **after-cost Sharpe / turnover** 最能活；
- 是否存在明显的“太浅是假信号、太深是刀口接血”的 U 型生存区间。

### 实验 D：long / short 拆开
很多 crypto MR 会出现：
- long 侧靠 oversold snapback 活着；
- short 侧因为牛市 drift、上行 squeeze、更差的 borrow/funding 结构而变弱。

所以一定要拆：
- `long-only`
- `short-only`
- `long+short`

不要默认上下对称。

## 10. 下一步怎么测
1. **先做 `15m` 的 no-frills baseline。** 不上 Keltner squeeze、不上复杂 regime，只测 `z + BB + ATR` 是否费后活着。  
2. **第二步才加 trend veto。** 因为这层最可能真能减少“抄底抄在趋势腿中段”的灾难。  
3. **把 RSI 作为可开关 admission，不要默认必需。** 很多时候 RSI 只是让交易更少，不一定让净边更强。  
4. **必须做 z-score 分桶统计。** 这是这份 repo 最值得偷走的方法，不做等于白看。  
5. **成本先打厚。** 这类短周期 MR 对手续费/滑点很敏感，first pass 不要低于 round-trip `12~20 bps`。  
6. **先看 cross-asset transfer。** BTC 有边不代表 ETH/SOL 也有；单币 MR 很可能高度依赖波动结构。  
7. **如果 `15m` 活、`5m` 死，就把 `5m` 降级成 execution layer。** 不要硬要求 alpha 必须在最细级别也成立。  

## 11. 风险与保留意见
- **repo 没给公开回测表。** 这篇 digest 的主证据是源码结构，不是作者披露的已验证绩效。必须自己跑 first verdict。  
- **趋势 veto 可能把最肥的 V-reversal 也筛掉。** 所以它是待验证 layer，不是先验真理。  
- **squeeze 可能过度稀释 trade count。** 对 5m/15m 而言，这层很可能是“看起来高级，实际上把样本数杀没”。  
- **极端 z-score 可能对应 liquidation cascade，不是均值回复。** 所以 `3.0+` 桶未必最好，甚至可能是最危险的。  
- **short 侧不能默认对称。** crypto 的 drift、上行 squeeze 与下行反弹速度常常不对称。  

## 12. 结论
如果只留一句话给后续复现：

> **别把这份 2026 repo 的 mean reversion 模块读成“BB + RSI 指标拼盘”；对 short-cycle desk，更该先复现的是“单币 overshoot snapback”这条 raw alpha，再用 `RSI confirm × trend-veto × z-score bucket governance` 去判断它在哪些口袋还能费后活下来。**

这也是为什么它值得进入当前研究池：
- **主题类型：raw alpha**
- **基础 alpha：单币 overshoot snapback**
- **可独立复现：是**
- **可直接落地完整策略：是**
