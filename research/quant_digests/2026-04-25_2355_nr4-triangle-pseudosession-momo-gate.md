# 别把 SPY intraday momentum 只读成“开盘越界就追”：对 short-cycle crypto desk，更该先测的是「NR4 / NR7 / Triangle 压缩日 admission gate」

- 时间：2026-04-25 23:55 UTC
- 主题类型：**filter**
- 基础 alpha：**伪 session open 之后，若价格突破“按时段自适应噪声带”，则顺着异常买卖失衡方向做 intraday continuation；这轮真正值得拆给 crypto 的旁支，不是再重复 headline alpha，而是“前一 pseudo-day 若属于压缩/三角整理，下一 pseudo-session 的动量突破更值得放行”。**
- 是否可独立复现：**是**
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：**否**
- 主题标签：filter/regime/intraday-momentum/pseudo-session/compression/nr4/nr7/triangle/trend-day/admission-gate/noise-area/vwap/crypto/15m/5m/1m/paper/fulltext

## 1. 这次看了什么
这轮主材料是：

**Carlo Zarattini, Andrew Aziz, Andrea Barbon (2025 version; first version 2024)**  
**Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY)**  
- Venue：working paper / full-text PDF  
- DOI：**未见正式期刊 DOI；可读版本来自作者公开页与 St. Gallen 机构库 PDF**  
- Readable URL：<https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/>  
- Full-text PDF：<https://www.alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content>  
- Repo URL：**未见官方策略 repo**

这篇材料在 digest 里之前已经作为 **raw alpha 主线** 做过；所以这次**不重复写 headline 的 noise-area continuation 本体**，而是专门抽它对当前 desk 更值钱、且还没单独整理过的一条旁支：

> **不是所有 pseudo-session 动量突破都该一视同仁；上一 pseudo-day 如果本来就很压缩（NR4 / NR7）或三角收敛，那么下一段 intraday continuation 更值得放行；如果上一天已经是 trend day，再去追同类 intraday 动量，反而更弱。**

## 2. 一句话核心结论
**对 crypto 短周期 desk，这篇 paper 更值得迁移的不是“看到越界就追”本身，而是一个很便宜的前置 gate：`compression yesterday -> today intraday momentum more credible`；`already-trended yesterday -> today follow-through weaker`。**

## 3. 它在原文里怎么体现
作者先做完整 intraday momentum 策略：
- 用过去 `14` 天“同一时刻距开盘的平均绝对位移”定义 **Noise Area**；
- 当价格上穿/下破该噪声带时，顺着方向做 intraday momentum；
- 只在 `HH:00 / HH:30` 这类半小时节点交易；
- 用 `current band + VWAP` 做 trailing stop；
- 全部仓位在收盘前平掉。

然后他们把**前一日的日线形态**拿来给这条 intraday momentum 做条件分组，结果很干净：

- **Unconditional**：`12 bps/day`，t-stat `5.34`，Sharpe `1.7`
- **NR4**：`22 bps/day`，t-stat `5.14`，Sharpe `3.2`
- **NR7**：`16 bps/day`，t-stat `3.07`，Sharpe `2.5`
- **Triangle**：`14 bps/day`，t-stat `3.19`，Sharpe `2.0`
- **Trend day**：`-2 bps/day`，t-stat `-0.24`，Sharpe `-0.3`

原文自己的解释也很直接：**压缩后更容易出可交易趋势；而在已经“走完一大段”的日子后，再追同样的 intraday 趋势并不占优。**

## 4. desk 化后，真正该拿走的东西是什么
### 4.1 先说人话
对我们来说，这不是“又一个美股日内动量故事”。

更值钱的翻译是：

> **同样一个 5m/15m breakout 或 pseudo-session continuation，前一 pseudo-day 是“压缩整理后待释放”，还是“已经单边走过一大段”，两者不是一回事。**

这能直接服务现有的：
- breakout / trend-following
- pullback continuation
- BTC lead -> alt catch-up continuation
- session-window momentum

### 4.2 最小 gate 定义
把 paper 的日线条件，翻成 crypto `24/7` 的 pseudo-day 版本：

1. **NR4 / NR7 compression gate**  
   - 以 UTC `00:00` 或 `08:00` 切 pseudo-day；
   - 记昨日 high-low range；
   - 若昨日 range 是过去 `4` / `7` 个 pseudo-day 最窄，则标记 `NR4 / NR7=1`。

2. **Triangle gate**  
   - 昨日高点下降、低点抬升；
   - 且昨日 range 小于过去 `14` 天均值；
   - 可用“rolling slope(highs) < 0 且 slope(lows) > 0”做最小实现。

3. **Trend-day veto**  
   - 昨日 close 靠近日内高/低端；
   - 且昨日 range 大于过去 `14` 天均值；
   - 说明前一 pseudo-day 已经明显单边扩张。

然后把 gate 接到任何一个已有动量 baseline：
- baseline A：pseudo-session open 到当前的 return 突破自适应噪声带；
- baseline B：`15m` Donchian / ORB / high-break continuation；
- baseline C：BTC 先动、alts 跟随的 lead-lag continuation。

## 5. 为什么它对 `1m/3m/5m/15m` 有用
因为这层 gate：
1. **完全不用外部数据**，只靠 OHLC；
2. **计算便宜**，适合先做全 universe 扫描；
3. **不是新 alpha 本体，而是共享 admission layer**，可以同时喂给多条趋势线；
4. **对成本友好**：它的目标不是多开交易，而是减少“本来就不该追”的入场。

对现在 desk 更现实的用法不是新造一个复杂模型，而是先问：

> **我们手上已有的 trend / breakout / lead-lag 信号，若只在 `NR4/NR7/Triangle` pseudo-day 之后才放行，净 bps、hit rate、左尾会不会更好？**

## 6. 下一步怎么测
### 实验 1：给现有 pseudo-session momentum 加 gate
- 标的：`BTC/ETH/SOL/BNB`
- bar：`15m` 主实验，`5m` 子执行
- baseline：过去 `14` 个 pseudo-day 定义 same-time noise band；突破后顺势持有 `2~6` 根 bar
- 对照：
  1. 无 gate
  2. 仅 `NR4/NR7`
  3. 仅 `Triangle`
  4. `Trend-day veto`
- 看：trade count、avg net bps、Sharpe、max DD、left-tail

### 实验 2：给 breakout 主线做 shared gate
- baseline：`15m` Donchian / opening-range breakout / 前高突破
- 只在 `NR4/NR7/Triangle` 后放行
- 看是否减少“假突破 + 追高回吐”

### 实验 3：BTC->alt continuation router
- source：BTC pseudo-session first half move
- target：ETH/SOL/ADA/AVAX 后续 `1~4` 根 `15m`
- 问题：如果 BTC 前一 pseudo-day 本身是压缩日，今天的 lead-lag transmission 是否更强？

## 7. 风险与失败方式
1. **crypto 没有天然开收盘**  
   pseudo-day 切分（`00:00 UTC`、`08:00 UTC`、`美股开盘映射`）会直接影响结论，必须多切分对照。

2. **压缩日不一定只导向 continuation**  
   对某些币，压缩后也可能先假突破再反向；所以 gate 更适合当 admission，不适合单独当 alpha。

3. **Trend-day veto 可能错杀强趋势市场**  
   在极强 bull/bear regime，下一个 pseudo-day 继续 trend 也很常见，需要再叠加 market beta / funding / OI 过滤。

4. **维度漂移**  
   论文是 SPY `1m` 日内；我们迁到 crypto 时更诚实的定位是：**共享 gate 假设**，不是“业绩数字可直接照搬”。

## 8. 我对这条线的判断
这轮最值钱的不是再抄一遍 paper headline，而是把它里面一个很容易被忽略、但对 desk 很实用的分叉单独拿出来：

> **压缩后的 intraday 动量，比“昨天已经走过趋势”的 intraday 动量更值得放行。**

它不是新的 raw alpha 本体，但它很适合做：
- `breakout` 的 shared gate
- `pseudo-session momentum` 的 admission layer
- `BTC lead -> alt continuation` 的条件放行器

如果 first probe 结果成立，这会是一个**低复杂度、低成本、跨多条趋势线复用**的过滤层。

## 9. 文件与页面
- 研究笔记：`research/quant_digests/2026-04-25_2355_nr4-triangle-pseudosession-momo-gate.md`
- 预期页面（发布后）：<https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-25_2355_nr4-triangle-pseudosession-momo-gate.html>
- 索引页：<https://jp.jerrypsy.top/momentum/reading/quant_digests/report.html>

## 10. 参考来源
1. **Zarattini, C., Aziz, A., & Barbon, A. (2025 version; first version 2024).** *Beat the Market: An Effective Intraday Momentum Strategy for S&P500 ETF (SPY).* Working paper.  
   - Readable URL: <https://concretumgroup.com/beat-the-market-an-effective-intraday-momentum-strategy-for-sp500-etf-spy/>  
   - Full-text PDF: <https://www.alexandria.unisg.ch/server/api/core/bitstreams/a99aba00-f967-49b3-aceb-f544dc386e0b/content>

2. **University of St. Gallen / Alexandria repository entry**（same paper full-text host）  
   - URL: <https://www.alexandria.unisg.ch/entities/publication/52480a9e-dc4a-4b94-a165-cf7465e4a0ae>
