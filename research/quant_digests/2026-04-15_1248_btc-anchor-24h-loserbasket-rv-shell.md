# 别把这份 HKU 比赛仓只读成 pairs/cointegration 拼盘：对 short-cycle desk，更该先拆的是「BTC anchor × 24h loser basket short」这条 raw alpha

- 时间：2026-04-15 12:48 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `backtester/backtest/strategies/v1_ls.py` + `backtester/backtest/position_managers/v1_ls_pm.py` + `backtester/src/oms_simulation.py` + `backtester/backtest/v1_ls_bt.py`）+ Binance USDⓈ-M `1h` public-data portability probe
- 主题标签：raw-alpha/cross-sectional/relative-value/market-neutral/btc-anchor/loser-basket/24h-return/variance-scaling/alt-short/perpetual/binance/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：repo 源码规则 + 公共历史 K 线 portability probe

- 主题类型：raw alpha
- 基础 alpha：**把 BTC 当成 beta 锚，只做多 BTC、做空过去 24h 表现最差的一篮子 alt；赚的是“弱 alt 相对 BTC 继续落后/修复更慢”这条 cross-sectional relative-value spread，而不是单币方向判断。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么

### 主来源（repo）
- **Authors / Owner：** `LevRoz630`（HKU x Avenir Quantitative Trading Challenge Round 2 参赛仓）
- **Year：** repo created `2025-09-29`，last updated `2026-03-19`
- **Title：** *HKU-Avenir Quantitative Trading Challenge -- Round 2*
- **Venue：** GitHub repo / 竞赛实盘与回测代码仓
- **DOI：** N/A
- **Readable URL：** <https://github.com/LevRoz630/hku-avenir-2nd-round>
- **Repo URL：** <https://github.com/LevRoz630/hku-avenir-2nd-round>

### 本轮自建 probe 产物
- 汇总：`reports/artifacts/quant_digests/2026-04-15_btc_anchor_loser_basket_probe_summary.json`
- 日频换仓版事件流：`reports/artifacts/quant_digests/2026-04-15_btc_anchor_loser_basket_probe_daily.csv`
- 小时换仓版事件流：`reports/artifacts/quant_digests/2026-04-15_btc_anchor_loser_basket_probe_hourly.csv`

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = BTC-anchor cross-sectional loser basket short：做多 BTC，当过去 24h 跑输的 alt 出现负收益时，按 `|24h return| / variance` 加权去做空那篮子 loser，赚的是弱 alt 相对 BTC 的继续落后。**

翻成人话：
- 这不是常规 `pairs spread z-score fade`；
- 也不是“市场跌了就空山寨”的宏观判断；
- 它本体是一条 **cross-sectional / relative-value raw alpha**：
  1. 先用 BTC 当锚；
  2. 每个观察时点只找过去 `24h` 为负的 alt；
  3. 跌得更深、但历史 `24h` 波动方差更低的 alt，给更大空头权重；
  4. 多头只放 `BTC`，把组合写成 `long BTC / short loser alts`。

所以这轮不是 filter，不是 overlay，而是一个可以直接落到多空、仓位、风控、成本的 **完整 raw alpha 壳**。

## 3. 为什么这轮值得写，而不是继续在 funding / 常规 pairs 上内循环

这轮值得进池，原因很直接：

1. **它补的是“BTC 锚定的横截面 relative-value”素材，不是又一篇 funding / basis / spread zscore。**  
   最近 desk 已经堆了不少 funding、basis、pairs、lead-lag；但 `BTC anchor × loser basket short` 这种写法，把市场 beta 锚和横截面弱者筛选揉在一起，增量是明确的。

2. **它是 repo 原生带完整策略壳的 raw alpha。**  
   不是只有一句 README 想法，而是有：
   - entry / exit；
   - 权重规则；
   - 风控；
   - 回测器；
   - 成本口径（虽然偏乐观）；
   - 竞赛级实盘背景。

3. **它天然适合 short-cycle desk 做“慢信号 + 快执行”拆分。**  
   信号本身是 `24h` 横截面状态，执行完全可以拆成 `1h / 15m`。这对 desk 很重要：
   > 信号慢，不代表不能服务短周期；只要 entry / rebalance / veto / execution schedule 能拆到 `15m`，它就是可用的 slow-alpha book 原料。

## 4. repo 里到底写了什么

## 4.1 策略壳非常明确：长 BTC，空 24h 为负的 alt basket
`backtester/backtest/strategies/v1_ls.py` 给出的规则很清楚：

- universe 默认是：`BTC, ETH, SOL, ADA, XRP, DOGE`；
- BTC 是唯一多头锚；
- alt 端只保留 **过去 24h log return < 0** 的币；
- 原始权重是：
  - `raw_weight_i = abs(log_return_24h_i) / variance_i`
- 然后：
  - alt 侧先归一化；
  - 再过滤掉 **权重不超过 10%** 的小仓位；
  - 过滤后重新归一化；
- 总体配置默认：
  - `BTC long = 10%`
  - `Alt short basket = 90%`

也就是说，repo 的核心不是“看谁跌就全空谁”，而是：
> **只空最近 24h 的 loser，而且优先空“跌得够狠、但不是纯高噪声”的 loser。**

这条线更接近 **BTC-anchored relative-value continuation / underreaction**，而不是简单趋势跟随。

## 4.2 它不是高频刷仓，默认是 daily rebalance + ratio drift 触发
源码里两个触发条件：

1. **按天 rebalance**；
2. 若 BTC/Alt 名义比例偏离目标超过阈值，再额外 rebalance。

参数默认值：
- `current_btc_ratio = 0.10`
- `drift_threshold = 0.05`

翻成人话：
- 这条线的 alpha 核心不是“每根 K 线都重算”；
- 真正该优化的是 **低换手持有 + 定时重估 loser basket**。

这点很关键，因为它刚好解释了为什么它适合 short-cycle desk 的方式，不是去把信号硬压成 `1m`，而是：
> **保留慢信号，用 `15m / 1h` 执行层去降低 drift、补风控、控制换手。**

## 4.3 position manager 给了 3 个很实用的生产部件
`backtester/backtest/position_managers/v1_ls_pm.py` 里有三块值得直接吸收：

### (a) 60 天 ramp-up
- 起始 alloc multiplier：`200`
- 最大 alloc multiplier：`2000`
- 线性 ramp-up：`60d`

这不是 alpha 本体，但非常适合 desk：
> 新 book 不一定先满仓，把它当成“上线初期逐步放量”的标准模板很合理。

### (b) 15% red button
- 任何单腿若浮亏超过 `15%`，直接强平。

这对 `BTC long / alt short` 书尤其重要，因为 alt squeeze 经常是组合真正的尾部风险来源。

### (c) CLOSE 优先级高于开仓
position manager 会优先执行 close，避免同一 symbol 同时出现互相打架的指令。

这是个小实现细节，但对 live shell 很关键：
- 先平旧腿；
- 再开新腿；
- 不要让 rebalance 变成方向翻转时的脏成交。

## 4.4 repo 的成本口径是“有，但偏乐观”
`backtester/src/oms_simulation.py` 里，平仓 PnL 会扣：
- `0.00023 * notional`，也就是大约 **`2.3 bps`** 的 close 成本；

但要注意：
- 这里没有完整建模双边 taker 成本；
- 没有明显的 funding、冲击和滑点壳；
- 对 alt basket 的真实交易成本来说，这个口径偏乐观。

所以这份 repo 可贵的地方在于它给了完整策略骨架，
但真正能不能搬到 desk，还是要自己补更硬的成本假设。

## 5. 我做的 Binance USDⓈ-M 最小 portability probe：repo 原版节奏活，过度提频会被换手打穿

## 5.1 数据与口径
- **数据源：** Binance USDⓈ-M public `/fapi/v1/klines`
- **公开性：** 完全公开 REST
- **更新频率：** `1h` K 线（本轮先做与 repo 更接近的快检）
- **样本：** `2025-12-16 13:00 UTC` 到 `2026-04-15 12:00 UTC`，约 `120d`
- **资产池：** `BTC/ETH/SOL/ADA/XRP/DOGE`
- **执行口径：**
  1. 信号完全按 repo 公式：`24h` 负收益 alt、`|ret|/var` 加权、`BTC 10% / alt basket 90%`；
  2. 先测 **repo-faithful 的 daily rebalance**；
  3. 再测 **desk 常见冲动改写版：hourly rebalance**；
  4. 成本统一先用 **`4 bps * turnover`** 的较硬口径快检；
  5. 目标不是声称已 production-ready，而是判断这条 alpha 的换手承受力。

## 5.2 先记最重要的 6 个数

### repo-faithful：daily rebalance
- gross total return：约 **`+32.48%`**
- gross Sharpe：约 **`2.18`**
- net total return（`4 bps * turnover`）：约 **`+27.36%`**
- net Sharpe：约 **`1.91`**
- max drawdown：约 **`-19.97%`**
- 平均每小时 turnover：约 **`0.036`**

### desk 冲动缩频版：hourly rebalance
- gross total return：约 **`+29.00%`**
- gross Sharpe：约 **`2.02`**
- net total return（`4 bps * turnover`）：只剩 **`+1.49%`**
- net Sharpe：只剩 **`0.33`**
- max drawdown：约 **`-20.38%`**
- 平均每小时 turnover：约 **`0.219`**

一句话结论：
> **alpha 本体没有被成本直接打死；真正的问题是你不能因为 desk 喜欢快，就把它重写成每小时都折腾一次。**

## 5.3 这组数告诉了我们什么

### 结论 1：repo 的核心 edge 更像“低换手的弱 alt 相对落后”
如果只是把 repo 原节奏搬到公开 Binance perp 快检里：
- gross 不是假阳性；
- 加了较硬的 turnover 成本以后，净值仍然站得住；
- 说明这条线不是纯 README 幻觉。

### 结论 2：不要把 slow signal 粗暴压成 fast rebalance
小时换仓版的 gross 还不错，但净后几乎被换手吃光：
- gross Sharpe 仍有 `2.02`；
- net Sharpe 掉到 `0.33`；
- 平均 turnover 从 `0.036` 直接跳到 `0.219`。

这就是这轮最重要的 portability lesson：
> **short-cycle desk 应该把它当“慢信号 + 快执行控制”，而不是“快信号 + 高频重平衡”。**

### 结论 3：这条线本质上是“BTC 作为 beta 锚，空弱 alt 的相对强弱延续”
本轮样本里，平均同时入选的空头 alt 数约 **`2.44`** 个；
被选中次数最多的是：
- `ADA`：`1388` 次
- `XRP`：`1365` 次
- `DOGE`：`1327` 次
- `SOL`：`1266` 次
- `ETH`：`1218` 次

这意味着它不是一个“永远空同一只币”的单腿策略，
而更像：
- 市场给你一组动态 loser；
- BTC 负责锚住大盘 beta；
- 组合赚的是 loser 对 BTC 的相对落后。

## 6. 这条线对 short-cycle desk 的正确定位

## 6.1 它是 raw alpha，而且是完整策略壳
原因很明确：
- 信号规则清楚；
- 多空腿清楚；
- entry / rebalance 节奏清楚；
- sizing 清楚；
- 风控和 stop 清楚；
- 成本口径至少有一版；
- 我们还做了公共数据快检。

所以这轮不是“想法备忘录”，而是可以直接进复现池的 **raw alpha / complete shell**。

## 6.2 它与 `1m / 3m / 5m / 15m` 的关系：信号慢，执行要快，但别乱快
最正确的 desk 翻译不是把 `24h` 信号降采样成 `5m` alpha，
而是：

- **signal layer：** 继续用 `24h` loser basket；
- **execution layer：** 在 `15m` 上安排开平和 drift control；
- **veto layer：** 对极端 squeeze、资金费率反转、新闻冲击做否决；
- **sizing layer：** 继续保留 inverse-vol / capped basket；
- **risk layer：** 对 alt short leg 单腿 red button 更敏感。

也就是说，它服务 short-cycle desk 的方式，更像：
> **一个慢信号的 relative-value book，交给 `15m` 执行层去做精细化。**

## 7. 风险与保留意见

1. **repo 成本假设偏乐观。**  
   真正上 perp，alt 侧双边 taker、滑点、funding、挤仓尾部都要单独补。

2. **BTC 10% / Alt 90% 默认很激进。**  
   这更像“BTC 只是锚，不是对冲满 beta”的表达。若真上实盘，可能需要更高 BTC 权重或 sector/beta neutral 化。

3. **目前 probe 用的是 6 币小 universe。**  
   扩到更多 liquid alt 后，alpha 可能更稳，也可能被尾部币的成本拖垮；这要再测。

4. **它不是逐根方向信号。**  
   若把它误用成 `5m` 连续翻仓策略，大概率会重演本轮 hourly 版本的成本塌陷。

## 8. 我给这轮主题的结论

> **这是一个合格的新 raw alpha 主题，而且比继续补一篇常规 pairs/funding 更值得。它真正可吸收的不是 repo 里的 pairs/cointegration 主线，而是这个更适合 desk 的旁支：`BTC anchor × 24h loser basket short`。**

更具体地说：
- **值得进池**，因为它是完整壳；
- **值得继续测**，因为 public-data 快检显示 daily 节奏下净后仍存活；
- **不能乱改写**，因为一旦粗暴提频，换手会先把 edge 吃掉。

## 9. 下一步怎么测

按优先级，我建议直接做这 5 步：

1. **把 signal 与 execution 拆开**  
   信号仍按 `24h` 更新，但执行改成 `15m` schedule，只允许：
   - 固定时点建仓；
   - ratio drift 超阈值时再补调；
   - 不允许每根都重算 basket。

2. **把 BTC 锚改成更真实的 hedge 壳**  
   对比三版：
   - `BTC 10%` 原版；
   - `BTC beta-matched`；
   - `BTC + ETH dual-anchor`；
   看哪版更能压住组合 beta 与 squeeze 风险。

3. **把成本模型升级成 alt-short 真实口径**  
   最少补：
   - 双边 taker 成本；
   - 不同 alt 的分层滑点；
   - funding；
   - 借由成交额或盘口深度做容量裁剪。

4. **做 `15m` execution veto**  
   给空头篮子加 3 个 veto：
   - funding 从极负快速回正；
   - `5m/15m` 级别出现 squeeze impulse；
   - 宏观新闻窗口内暂停 rebalance。

5. **把 loser basket 从“符号级”升级到“sector / residual”级**  
   下一版不要只看裸 `24h return`，而要测试：
   - 对 BTC 残差后再排 loser；
   - 对 sector/beta 中性后再排 loser；
   看 alpha 到底来自裸弱势，还是来自 idiosyncratic underperformance。
