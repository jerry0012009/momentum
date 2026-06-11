# 别把 BTC/ETH pairs 继续写成“信号对了就行”：这份 2026 GitHub 仓库更该先测的是「cointegration spread × beta-consistent sizing」完整 raw alpha
- 时间：2026-03-29 20:58 UTC
- 类型：2026 GitHub 新仓库 + README/source pipeline 审阅 + Binance USDⓈ-M Perpetual 公共 `1h/15m` sizing transfer check
- 主题类型：raw alpha
- 基础 alpha：**BTC/ETH cointegration spread mean reversion**——当 `log(BTC) - β·log(ETH)` 偏离其滚动均值太远时，做多被低估腿、做空被高估腿，吃的是相对定价向长期线性关系回摆的收益。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/beta-neutral/sizing/hedge-ratio/btc/eth/binance/perpetual/1h/15m/5m/1m/3m/repo/public-data/cost/funding
- 证据类型：GitHub README/source 规则级证据 + Binance 公共 OHLCV 本地 transfer check + 15m 参数网格稳定性复核

## 1. 这次看了什么
先把 **base alpha** 说清楚：

> **这次不是 filter，不是 overlay，也不是“又一份 pairs 教程”。alpha 本体就是 BTC/ETH 的 cointegration spread mean reversion。**

翻成人话：
- BTC 和 ETH 长期会一起动，但短时间不会完全同步；
- 如果两者的相对价格关系偏得太开，理论上会有“回到更正常关系”的动力；
- 所以当 spread 的 z-score 很极端时，做多便宜腿、做空贵腿，赌的是 **相对价差回摆**，不是单边看涨看跌。

这份 2026 新 repo 最值得 intake 的点，不是“BTC/ETH 能不能做 pairs”——这个市场早就知道了；真正更适合我们 desk 的，是它把一个常被当成细枝末节的东西单独做成了 **受控实验**：

> **同一条 spread alpha，只改 position sizing：从 dollar-neutral 改成 beta-neutral，整条策略的最终 PnL 可以直接翻正。**

对短周期 desk 来说，这个分支很值钱，因为它回答的是一个更底层的问题：

> **如果你的 alpha 定义里用的是 `β`，但仓位还在按 1:1 美元对冲，那你到底是在交易原始 alpha，还是在交易一条被自己 sizing 改坏了的假 spread？**

一句话结论先放前面：

> **这条 raw alpha 值得继续留在素材池，但最先该搬的不是“再证明一次 pair 会回归”，而是把“hedge-ratio-consistent sizing”升级成 pairs / stat-arb 的默认必测组件。**

## 2. 核心结论
### 2.1 这份 repo 真正新增了什么
repo 作者是 **Howard (Cheng-Hao) Hsu**，项目标题是 **Statistical Arbitrage: BTC/ETH Cointegration Pairs Trading Strategy**。它不是只给一个 notebook 图，而是把完整管线拆成了：
- 数据抓取
- Rolling OLS hedge ratio
- ADF stationarity gate
- OU half-life
- 状态机式入场/出场
- 全成本回测
- `Dollar-Neutral` vs `Beta-Neutral` 对照实验

也就是说，这不是“有信号、没 execution”的半成品，而是一份可以直接拆 entry / exit / sizing / risk / cost 的完整 skeleton。

### 2.2 repo 里最该记住的数字
作者用的是 **Binance USD-M perpetual 的 BTC/USDT 与 ETH/USDT 1 小时数据**：
- 样本：**2021-01-01 → 2025-12-31**
- bar 数：**43,824 根 hourly bars**
- 滚动窗口：**720 小时（30 天）**
- 成本：**单腿 `0.06%` = taker fee `0.04%` + slippage `0.02%`**
- 另外还显式计入了 **8 小时 funding settlement**

统计层面：
- `β` 均值 / 标准差：**`0.629 / 0.301`**
- `β` 区间：**`-0.161 ~ 1.571`**
- ADF `p < 0.05` 的时间占比：**`9.8%`**
- median half-life：**`468 小时`**

先看信号稀疏度：
- 在严格 `ADF p < 0.05` gate 下，**5 年只成交 9 笔**；
- 也就是说，这不是一条高 turnover pair 策略，而是一个“只在 stationarity regime 出手”的稀疏 alpha。

但真正重要的是 sizing 对照：

**Version A：Dollar-Neutral（两腿都固定 5000 美元）**
- Final Equity：**`$9,208.40`**
- Net PnL：**`-$791.60`**
- Max Drawdown：**`-14.89%`**
- Gross PnL：**`-$652.58`**
- Total Fees：**`-$108.00`**
- Funding & Carry：**`-$30.99`**

**Version B：Beta-Neutral（ETH 腿按 `5000 × β_entry` 配）**
- Net PnL：**`+$67`**
- Total Fees：**`-$96.48`**
- Funding & Carry：约 **`-$27`**

repo 自己给出的解释非常直接：
- 因为样本里的平均 `β ≈ 0.629`；
- 如果你还是按 1:1 美元做 BTC/ETH，两腿并不对应你定义 signal 时那条 `BTC - β·ETH` spread；
- 你其实把 ETH 腿配重了，等于偷偷引入了一段多余的方向暴露；
- 而 beta-neutral 不只是费率更省，本质上是 **仓位终于和 signal 的数学定义一致了。**

### 2.3 最值得 desk 记住的判断
> **这份 repo 最该 intake 的不是“BTC/ETH pairs 可以做”本身，而是“错误 sizing 会把原本还算合理的 pairs alpha 直接做坏”。**

## 3. 为什么和当前项目直接相关
先回答最关键的问题：

> **为什么这篇东西比继续补一个新的 headline alpha 还值得？**

因为我们当前库里并不缺：
- pair 怎么选
- spread 怎么定义
- z-score 怎么入场
- ADF / OU / cointegration 这些标准件

更缺的是：

> **当 alpha 真的要从 notebook 走向 live 时，signal 定义和 position sizing 有没有保持同一种“统计中性”？**

这点和当前 desk 非常直接相关：
1. **它仍然是 raw alpha，不是纯风控。**
   - alpha 本体仍然是 spread convergence。
2. **它又不仅仅是“再来一条 pair”。**
   - 它补的是 pairs / stat-arb 最容易被低估的落地层：`sizing`。
3. **它能直接扩到 `15m / 5m / 1m`。**
   - signal 生成可在 `15m`，执行切片可下沉到 `5m / 1m`；
   - 真正该检验的是：快周期下 beta-neutral 是否仍普遍优于 dollar-neutral。
4. **它对现有素材池是增量，不是重复。**
   - 我们已经有很多“entry signal”型 pairs 材料；
   - 但“hedge-ratio-consistent sizing”还没有被立成默认必测卡片。

## 3.5 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / mean reversion**
- 基础 alpha：**BTC/ETH 相对定价偏离长期线性关系后的 spread convergence**
- 原 repo 的完整策略组件：
  - `signal layer`：rolling OLS `β` + spread z-score
  - `admission layer`：ADF `p < 0.05`
  - `entry`：`|Z| > 2`
  - `exit`：`|Z| < 0.5`
  - `risk`：`|Z| > 4` stop；`3 × median half-life` time-stop
  - `cost`：每腿 `6 bps` + funding
  - `sizing`：对照 `dollar-neutral` vs `beta-neutral`
- 对 desk 的短周期翻译：
  - `raw alpha layer`：`15m` 或 `5m` 上的 spread 偏离回摆
  - `sizing layer`：按 `β_entry` 配腿，而不是机械 1:1 美元
  - `risk layer`：cointegration / corr gate、time-stop、止损、funding 结算规避
  - `execution layer`：`5m/1m` 分批成交 + maker/taker 切换 + 盘口 veto

## 4. repo 里的完整机制，翻成 desk 语言
### 4.1 spread 是怎么定义的
repo 用的是：

`Spread_t = log(BTC_t) - β_t × log(ETH_t)`

其中 `β_t` 不是常数，而是 **rolling OLS hedge ratio**，并且显式 `shift(1)`，避免把当根 bar 信息偷偷用进来。

这意味着：
- signal 不是“BTC vs ETH 谁涨得多”；
- 而是 **在当前估计的线性关系下，BTC 相对 ETH 是贵了还是便宜了。**

### 4.2 入场 / 出场规则
repo 的状态机很规整：
- 平仓状态下：
  - `|Z| > 2` 且 `ADF p < 0.05` 才入场
  - `Z > 2`：short spread
  - `Z < -2`：long spread
- 持仓状态下：
  - `|Z| < 0.5`：止盈平仓
  - `|Z| > 4`：stop-loss
  - `holding_hours > 3 × median_HL`：time-stop

换句话说，这不是“极端就赌回归”的裸奔版本，而是：
- 先确认当前窗口还有 stationarity 痕迹；
- 再赌 spread 过度偏离后的均值回归；
- 如果迟迟不回、或者越走越偏，就强制认输。

### 4.3 这份 repo 最值钱的地方：sizing 和 signal 定义一致
repo 的关键 insight 可以压成一句话：

> **你定义的是 `BTC - β·ETH` 这条 spread，就该配 `1 : β` 这组仓位；否则 signal 和仓位不是同一件东西。**

这件事看起来像理论洁癖，实际上是 PnL 大事：
- 当 `β < 1` 时，1:1 美元对冲会让 ETH 腿偏重；
- 于是策略会混入额外 ETH 方向暴露；
- 这个暴露既会放大 drawdown，也会让交易成本变高；
- beta-neutral 则同时修了两件事：
  1. 对冲结构更接近 signal 本身；
  2. ETH 腿 notional 更小，费用更低。

## 5. Binance 公共 `1h / 15m` sizing transfer check
我补了一个 **轻量本地 transfer check**，目标不是复刻 repo 全部统计检验，而是验证最核心的 desk 问题：

> **同一条 BTC/ETH spread mean reversion，只改 sizing，beta-neutral 在当前 Binance 短周期上是不是普遍更优？**

### 5.1 本地 proxy 口径
为保证这轮 intake 速度，我用的是轻量版 proxy，而不是完整 repo 复刻：
- 数据：**Binance USDⓈ-M Perpetual 公共 `BTCUSDT / ETHUSDT` klines**
- 频率：`1h` 与 `15m`
- 信号：rolling `β` + spread z-score
- gate：rolling return correlation `>= 0.75`
- 成本：每腿 **`6 bps`**
- 暂未纳入：
  - funding cashflow
  - 严格 rolling ADF p-value
  - OU half-life 精确估计

也就是说：
> **这轮 proxy 只是在测 sizing 迁移，不是在给 BTC/ETH 现成 live verdict。**

相关 artifact：
- `reports/artifacts/quant_digests/2026-03-29_btc_eth_beta_vs_dollar_proxy.json`
- `reports/artifacts/quant_digests/2026-03-29_btc_eth_beta_vs_dollar_15m_grid.json`

### 5.2 `1h` proxy 结果：beta-neutral 明显减损，但还没把 alpha 救活
样本：
- 区间：**2025-02-02 → 2026-03-29**
- bars：**10,080**
- median corr：**`0.821`**
- median beta：**`0.532`**

结果：
- **Dollar-neutral**
  - trades：**46**
  - cum net：**`-23.01%`**
  - mean trade：**`-50.0 bps`**
  - max DD：**`-25.30%`**
- **Beta-neutral**
  - trades：**46**
  - cum net：**`-15.23%`**
  - mean trade：**`-33.1 bps`**
  - max DD：**`-16.04%`**

翻成人话：
- 同样的信号、同样的交易次数；
- 只改 sizing，beta-neutral 就把累计亏损从 **`-23.0%` 收窄到 `-15.2%`**；
- drawdown 也从 **`-25.3%`** 缩到 **`-16.0%`**。

### 5.3 `15m` proxy 结果：短周期上 beta-neutral 也更优，但单靠 sizing 仍救不活
样本：
- 区间：**2025-11-29 → 2026-03-29**
- bars：**11,521**
- median corr：**`0.892`**
- median beta：**`0.671`**

结果：
- **Dollar-neutral**
  - trades：**98**
  - cum net：**`-11.26%`**
  - mean trade：**`-11.49 bps`**
  - hit rate：**`23.5%`**
  - median hold：**5 bars**
  - max DD：**`-11.33%`**
- **Beta-neutral**
  - trades：**98**
  - cum net：**`-8.12%`**
  - mean trade：**`-8.29 bps`**
  - hit rate：**`27.6%`**
  - median hold：**5 bars**
  - max DD：**`-9.47%`**

这里最该记的不是“依然亏钱”，而是：

> **在 15m 上，beta-neutral 仍然把同一组 trades 的净损失缩小了约 `313 bps`，同时把 hit rate 提高了约 `4.1 pct`。**

也就是说：
- sizing 改善不是 repo 那段历史样本里的偶然故事；
- 它在当前 `15m` pocket 上仍然有方向一致的正贡献；
- 但 raw alpha 本体还不够强，不能指望 sizing 一个人把整条策略救活。

### 5.4 `15m` 小网格：这不是单点调参巧合
我又扫了一个小参数网格：
- lookback：`192 / 384 / 576`
- entry z：`1.5 / 2.0 / 2.5`
- exit z：`0.25 / 0.5 / 1.0`
- max hold：`16 / 32 / 64`

总共 **81 个 cells**，结果：
- **beta-neutral 在 `61 / 81` 个 cells（`75.3%`）里优于 dollar-neutral**
- 每笔交易的中位 uplift 约 **`+0.88 bps`**
- 但最好的 beta-neutral cell 仍只有 **`-7.07 bps/trade`**，还没翻正

所以更诚实的结论是：

> **beta-neutral 更像“该做的正确实现”，不是“自动把 BTC/ETH 15m pairs 做成赚钱策略”的魔法开关。**

## 6. 这组结果该怎么读
### 6.1 正面结论：sizing 不是 garnish，是 alpha body 的一部分
如果 signal 依赖 rolling `β`，那 sizing 不该被降级成回测尾声才看的“仓位细节”。

对 pairs / stat-arb desk 来说，更正确的表述应该是：

> **`position sizing` 不是 signal 后处理，而是 spread 定义的一部分。**

### 6.2 负面结论：当前 Binance 短周期上，BTC/ETH 单 pair 还不够强
这轮 proxy 同时告诉我们另一件更重要的事：
- 即使 sizing 改对；
- 即使相关性很高；
- 即使 z-score 很极端；
- BTC/ETH 单 pair 在当前 `15m` 样本里，成本后仍然不够强。

也就是说，下一步不该是“直接上线 beta-neutral BTC/ETH pairs”，而是：
1. 先把 **sizing consistency** 变成 pairs 默认标准件；
2. 再把 alpha 强度问题交给 pair selection / regime gate / execution 来解决。

### 6.3 对我们当前素材池的直接启发
这张卡最适合服务的，不只是 BTC/ETH 本身，而是整类：
- cointegration pairs
- same-underlier quote spread
- cross-venue same-asset basis
- basket stat-arb

凡是 signal 里出现 `β` / hedge ratio / factor loading 的策略，都应该补一句：

> **回测里到底是在按 signal 定义配仓，还是在按“习惯上的 1:1 dollars”配仓？**

## 7. 下一步怎么测
### 7.1 最小可落地实验（优先级最高）
先做一张非常明确的 A/B/C 实验卡：
- 数据：Binance USDⓈ-M `BTCUSDT / ETHUSDT / BNBUSDT`
- 周期：`15m` 信号，`5m` 执行
- 信号：rolling OLS `β` + ADF p-value + spread z-score
- 仓位方案：
  1. `dollar-neutral`
  2. `beta-neutral`
  3. `beta-neutral + vol target`
- 成本：maker/taker 两套
- funding：显式扣除 8h funding

核心验收条件不是“是否赚钱”，而是：
- 在**完全相同 signal** 下，`beta-neutral` 是否持续优于 `dollar-neutral`；
- 优势到底来自 **方向暴露更小**，还是 **fee/funding 更低**；
- 改成 `15m→5m` 执行后，优势会不会被 execution 噪音吃掉。

### 7.2 再往前一步：别只测 BTC/ETH
如果只盯 BTC/ETH，很容易把这件事读成“一个 pair 的特例”。

下一轮更应该扩成 liquid-major pair basket：
- `BTC-ETH`
- `ETH-BNB`
- `BTC-BNB`
- `SOL-ETH`
- `SOL-BNB`

用统一框架比较：
- rolling corr
- `β` 稳定性
- ADF hit-rate
- hold length
- funding drag
- dollar-neutral vs beta-neutral uplift

最后做一个排序：

> **哪些 pair 是“signal 一般，但 sizing 改对后能显著改善”；哪些 pair 则是“signal 本身就不够，改 sizing 也救不了”。**

### 7.3 真正适配 desk 的增强项
如果这条线继续往 `1m / 3m / 5m / 15m` 迁移，我会优先加这三层：
1. **regime gate**：
   - `ADF p < 0.10` / corr floor / realized-vol veto / funding sign veto
2. **execution gate**：
   - 盘口宽度、滑点、maker fill ratio、结算前 funding veto
3. **pair governance**：
   - 只在 `β` 稳定、half-life 合理、funding 不恶化的窗口开仓

## 8. 来源与可复现性
### 8.1 主来源（repo）
1. **Howard (Cheng-Hao) Hsu** (2026), *Statistical Arbitrage: BTC/ETH Cointegration Pairs Trading Strategy*  
   - Venue：GitHub repository  
   - Readable URL：`https://github.com/Bauch0430/crypto-pairs-trading-btc-eth`  
   - Repo URL：`https://github.com/Bauch0430/crypto-pairs-trading-btc-eth`  
   - 仓库创建 / 推送：**2026-03-13**  
   - 关键披露：5 年 `1h` Binance perpetual 数据；`β` rolling OLS；ADF gate；funding + `6 bps`/leg 成本；`Dollar-Neutral` vs `Beta-Neutral` 对照

### 8.2 理论地基
2. **Gatev, E.; Goetzmann, W. N.; Rouwenhorst, K. G.** (2006), *Pairs Trading: Performance of a Relative-Value Arbitrage Rule*, *Review of Financial Studies*  
   - DOI：`10.1093/rfs/hhj020`  
   - Readable URL：`https://doi.org/10.1093/rfs/hhj020`

3. **Ramos-Requena, J. P.; Trinidad-Segovia, J. E.; Sánchez-Granero, M. A.** (2020), *An Alternative Approach to Measure Co-Movement between Two Time Series*, *Mathematics*  
   - DOI：`10.3390/math8020261`  
   - Readable URL：`https://doi.org/10.3390/math8020261`

### 8.3 本轮本地数据口径
- 数据源：**Binance USDⓈ-M Futures 公共 klines**
- 公开性：**公开可得，无需私有权限**
- 更新频率：`15m` / `1h` bar；funding 为 `8h`
- 本轮最小实验口径：
  - 标的：`BTCUSDT`, `ETHUSDT`
  - 信号：rolling `β` + z-score
  - gate：corr floor `0.75`
  - 成本：单腿 `6 bps`
  - 输出：`dollar-neutral` vs `beta-neutral` 同信号对照

## 9. 一句话收尾
> **这轮 intake 最值得带走的，不是“BTC/ETH pairs 能做”，而是：凡是 spread 定义里用了 `β`，就别再把 beta-neutral sizing 当可有可无的小修饰。它应该是 raw alpha 骨架的一部分。**
