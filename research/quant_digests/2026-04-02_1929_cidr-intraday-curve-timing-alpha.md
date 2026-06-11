# 别把这篇 2021 IRFA 论文只读成 functional time series：对 short-cycle desk，更该先测的是「predict-next-day intraday curve × buy forecasted low / sell post-low high」这条 BTC directional raw alpha

- 主题类型：raw alpha
- 基础 alpha：**Bitcoin 的“次日整条日内收益曲线”并不完全随机；如果能提前大致预测次日 CIDR（cumulative intraday return）曲线形状，就可以在预测的日内低点附近做多，并在其后的预测高点前后平仓，吃一段日内 drift**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-02 19:29 UTC
- 类型：2021 *International Review of Financial Analysis* 接收稿全文 PDF + Binance USDⓈ-M `15m` public-data portability probe
- 主题标签：raw-alpha/single-asset/btc/intraday/time-of-day/cidr/functional-forecast/curve-shape/long-only/timing/15m/5m/3m/1m/paper/public-data/cost
- 证据类型：paper-based（accepted PDF fulltext 可读）+ public-data desk translation

## 1. 这次看了什么
这轮主看的是一篇 **公开可读接收稿 PDF**：

- **Authors / Year**: Elie Bouri, Chi Keung Marco Lau, Tareq Saeed, Shengyang Wang, Yuqian Zhao (2021)
- **Title**: *On the intraday return curves of Bitcoin: predictability and trading opportunities*
- **Venue**: *International Review of Financial Analysis*, Volume 76, Article 101784
- **DOI**: `10.1016/j.irfa.2021.101784`
- **Readable URL**: <https://centaur.reading.ac.uk/97607/1/Bitcoin_Functional_Accepted.pdf>
- **Publisher URL**: <https://doi.org/10.1016/j.irfa.2021.101784>
- **Repo URL**: N/A

它不是在讲“某个 5 分钟形态会不会涨”这种单点信号，而是在问更底层的一件事：

> **次日整条 BTC 日内收益曲线，是不是有可预测的 shape？如果有，能不能把它直接翻译成一个“日内什么时候买、什么时候卖”的交易计划？**

这件事对 short-cycle desk 值钱，因为它提供的不是某个单独 candle pattern，而是一个 **“日内路径预测 → 时间窗交易”** 的主壳。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 很清楚：**

> **Bitcoin 的次日日内收益路径存在可预测的曲线形状；因此，可以根据前一段时间估出来的次日 intraday curve，提前决定“预测低点买、预测后续高点卖”。**

翻成人话：
不是赌“下一根 5m 红还是绿”，而是赌 **“明天这一天大概率先走弱再走强，或者先慢慢抬升再在后段见高点”**，然后把交易压缩成一笔日内 long-only 定时交易。

所以这轮它属于 **raw alpha**，不是 filter / overlay。

## 3. 论文里到底怎么做这条 alpha

## 3.1 数据口径
论文用的是：

- **交易所**：Bitstamp
- **频率**：`5m`
- **样本期**：`2014-11-01` 到 `2019-08-10`
- **有效天数**：**1367 天**
- **异常处理**：剔除了 `2015-01-05` 到 `2015-01-10` 的 hacked exchange event 区间

作者把每一天都表示成一条 **CIDR 曲线**：

`CIDR_t(u) = 100 × (log P_t(u) - log P_t(0))`

也就是：
- 当天开盘价作为 0；
- 后面每个 `5m` 点，都看“相对当日开盘已累计涨跌多少”。

这一步很重要，因为它把“很多根 5m bar”变成了“一条完整的日内路径”。

## 3.2 预测层：不是直接预测 return，而是预测整条 curve
论文先对历史日内曲线做 FPCA（functional PCA）：

- **前两个主成分就解释了 90.23% 的总变异**；
- 作者解释为：
  - **第一主成分**更像是对整体上行均值曲线的强弱偏离；
  - **第二主成分**更像是 **日内均值回归 / 路径弯折** 机制。

然后作者滚动训练，用两种方法预测“次日主成分分数”：

1. **FPES**：对 score 做 exponential smoothing；
2. **FPAR**：只有当 score 序列存在 serial correlation 时，才对它做 AR(1) 预测；否则直接回到均值曲线。

对 desk 来说，这里的关键不是函数分析术语，而是：

> **先预测“明天一天会怎么走”，再从预测曲线上直接读 entry time 和 exit time。**

## 3.3 交易层：完整的 buy-low / sell-later-high 壳子已经给了
论文的 long-only 日内交易规则很直接：

1. 用滚动窗口数据预测次日整条 CIDR 曲线；
2. 找到预测曲线的 **全局最低点时间** `u_min`；
3. 在 `u_min` 之后，再找 **后续最高点时间** `u_max`；
4. 次日到点后：
   - 在 `u_min` 买入 BTC；
   - 在 `u_max` 平仓；
5. **不隔夜**，所有仓位午夜前清掉。

这点很重要：
它不是“解释性论文”，而是已经把 **entry / exit / no-overnight** 这套基本交易骨架写出来了。

## 3.4 论文里为什么专门强调 serial-correlation gate
作者发现：
- 不是什么时候都存在可预测性；
- 真正值得交易的时段，往往是 **FPC score 自身存在 serial correlation** 的那些日子。

这其实就是一个非常 desk-friendly 的结论：

> **别每天机械做；只在“路径可预测性明显没死”的 regime 里做。**

所以这篇 paper 真正最像 desk 组件的，不是纯粹的 functional forecasting，而是：

- **预测次日 curve shape**
- **把交易压缩成一笔日内 timing trade**
- **再用 serial-dependence 作为 admission gate**

## 4. 论文给了哪些硬信息

## 4.1 forecasting 层面：不是每次都比均值强，但 gated 时更像样
全文里 Table 3 的核心信息是：

- 在 **entire sample** 上，FPAR 相对 Fmean 的预测误差改善很有限；
- 但在 **first and second scores 都 serially correlated** 的样本里，FPAR 才明显更好。

也就是说：
**这条 alpha 不是“永远预测得很好”，而是“可预测性本身有 regime”。**

## 4.2 交易层面：FPAR 是论文里最强那条
论文 Table 4 给出的最关键一组结果：

### 交易全部样本（每天都做）
在 **FPAR + `S=182`** 下：

- **Annualised Return：64.70%**
- **Annualised Volatility：58.15%**
- **Sharpe：1.11**
- **Maximum Drawdown：-99.25%**

同表里：
- `S=365` 的 FPAR 仍优于另外两种方法；
- 说明“用 AR(1) 预测 score、并在无 serial correlation 时退回均值”这条思路，比机械均值曲线更强。

但也别被 headline 迷惑：
**它的 gross Sharpe 不差，但路径极粗糙，回撤非常深。**

## 4.3 只在 serial-correlation 样本做，风险显著下降
如果只在“第一或第二 score 存在 serial correlation”的样本里做，`S=365` 的 FPAR 表现为：

- **Annualised Return：42.10%**
- **Annualised Volatility：40.03%**
- **Sharpe：1.05**
- **Maximum Drawdown：-53.95%**

这里真正重要的不是 return 更高，而是：

> **把策略限制在“可预测性活着”的日子里，drawdown 明显变浅。**

这比“无脑每天做”更像 desk 能接受的策略壳。

## 4.4 成本不是没影响，但不是一句话就把 edge 判死
作者还做了交易费敏感性：

- 假设 **Bitstamp fee rate = 0.03%**；
- 在 **entire sample + `S=182`** 下，FPAR 的 **Sharpe 仍有 0.74**；
- 且作者明确指出：**如果只在 serial-correlation 样本做，交易频率更低，费率冲击更小。**

所以论文的直觉很清楚：

- **全样本硬做**：有 alpha，但成本和回撤都重；
- **加 dependence gate**：更像实际能交易的版本。

## 5. 对 short-cycle desk 真正有用的，不是“functional”三个字，而是这条主壳
如果把它翻译成 desk 语言，这篇论文最值钱的是：

1. **信号对象不是单 bar，而是日内整条路径**；
2. **交易动作极简单：一天只做一笔 long-only timing trade**；
3. **天然适合 `15m -> 5m -> 3m/1m` 三层拆解**：
   - `15m` 负责发现大致的日内低点-高点时间窗；
   - `5m` 负责细化到更窄 entry/exit window；
   - `3m/1m` 只做 execution improvement，而不是重新发现 alpha。

换句话说，它不是“直接拿去实盘就完事”，但非常适合作为：

> **BTC 单币 directional intraday timing alpha 的研究母体。**

## 5.5 策略拆解（必填）
- 方向属性：single-asset / directional / intraday timing / long-only
- 基础 alpha：次日日内收益曲线 shape 有弱可预测性，可据此做“预测低点买、后续高点卖”
- regime：只在历史日内曲线主成分 score 显示 serial dependence 时更值得开
- filter / veto：serial-correlation gate；若预测曲线的高点出现在低点之前，则不做或改为别的壳
- risk / sizing / execution overlay：单日单笔、午夜前清仓、成本先行；`1m/3m` 只做入场精修与滑点控制

## 6. 我做的最小 portability probe：Binance BTCUSDT perp `15m`
我没有在这轮硬复刻论文的所有 functional 细节到 `5m`，而是先做一个 **desk translation**：

- 数据：Binance USDⓈ-M `BTCUSDT` perpetual 公共 `15m` K 线
- 样本：**2025-02-07 到 2026-04-01，共 419 个完整 UTC 日**
- 训练窗：**182 天**
- 日内曲线：每个 UTC 日 96 根 `15m` bar，构造日内 CIDR 曲线
- 预测：
  - 每天滚动做 PCA；
  - 取解释 **≥90%** 变异的主成分；
  - 对存在 Ljung-Box serial dependence 的 score 做简化 **AR(1)** 预测；
  - 否则 score 预测为 0（回到均值曲线）；
- 交易：
  - 从预测次日曲线里找 `u_min`；
  - 再找 `u_min` 之后的 `u_max`；
  - 次日 `u_min` 买、`u_max` 卖；
  - 只做多，不隔夜。

这不是 paper-perfect replication，但足够回答一个问题：

> **这条“日内曲线预测 → 一笔日内 timing trade”的骨架，放到 2025-2026 的 Binance perp `15m` 上，还有没有最小生命迹象？**

## 6.1 probe 结果：gross 还有点东西，但成本非常关键
### 全部可交易日（236 天）
- **平均单日收益：+3.90 bps**
- **胜率：52.97%**
- **年化收益：15.31%**
- **Sharpe：0.65**
- **最大回撤：-13.35%**

### 只在“前两主成分至少一个 serially correlated”时做（22 天）
- **平均单日收益：+8.30 bps**
- **胜率：54.55%**
- **年化收益：35.36%**
- **Sharpe：1.21**
- **最大回撤：-4.04%**

这组数很说明问题：

1. **alpha 没死，但比论文年代薄很多**；
2. **不 gating 地每天做，gross edge 很薄；**
3. **一旦用 serial-dependence gate，单位交易质量明显上升。**

## 6.2 成本敏感性：这条线绝不能假装自己不怕费
我又对同一组 `15m` probe 做了 round-trip 固定成本敏感性：

### 全样本版本
- **0 bps**：Sharpe **0.65**
- **4 bps**：Sharpe **-0.02**（基本被打平）
- **6 bps**：Sharpe **-0.35**
- **8 bps**：Sharpe **-0.69**

### gated 版本
- **0 bps**：Sharpe **1.21**
- **4 bps**：Sharpe **0.63**
- **6 bps**：Sharpe **0.33**
- **8 bps**：Sharpe **0.04**（几乎归零）

结论非常直白：

> **这条 alpha 在今天更像“低成本、低频 gated timing 壳”，而不是高成本环境里随便硬打的主策略。**

也就是说，如果 desk 做它：
- 必须争取 maker / passive fill；
- 或者把它当成 **日内方向时间窗 gate**，再让更快的 microstructure 组件决定精确 entry。

## 6.3 最近一年这条曲线偏向什么时间窗
在这组 Binance `15m` probe 里：

- **全样本版本的中位买点**大约在 **20:00 UTC**；
- **中位卖点**大约在 **22:45 UTC**；
- **gated 版本的中位买点**更早，约在 **10:00 UTC**；
- **gated 版本的中位卖点**接近 **23:45 UTC**。

这说明两件事：

1. **intraday curve alpha 的“低点/高点时段”本身也会迁移**；
2. 所以 desk 不该把论文读成固定时段季节性，而该读成：
   - **每天滚动预测路径**；
   - 再从路径里读时间窗。

## 7. 这条线和当前素材池的关系
最近素材池里已经有：
- microstructure continuation / reversal
- pairs / residual mean reversion
- funding / basis / carry
- ETF / Polymarket / on-chain cross-market lead-lag

但 **“把次日日内路径本身作为交易对象”** 这条主线还比较少。

这篇 paper 补上的，正是一个不同于 breakout / OFI / pairs 的视角：

> **不是预测方向点，而是预测“方向在一天里的展开顺序”。**

这能直接服务：
- BTC directional intraday timing；
- breakout 策略的 **time-of-day admission gate**；
- execution shell（什么时候更值得等、什么时候该提前平）。

## 8. 先测什么，不先测什么
**先测：**
1. 在 `BTCUSDT` 上把 discovery 固定在 `15m`，执行下钻到 `5m/3m`；
2. 只保留 **serial-dependence gate = on** 的日子；
3. 加一层最简单的 execution rule：
   - 入场不追单，等 `u_min` 附近 `1~2` 根小回拉；
   - 出场不一定卡死 `u_max`，可加 `post-entry trailing high`；
4. 成本先跑 **2 / 4 / 6 / 8 bps** 四档，不要只看 gross。

**不先测：**
- 不先卷更复杂的 functional 学术细节；
- 不先把它扩成多币篮子；
- 不先加入太多宏观 / 链上 / funding overlay 把来源搞混。

## 9. 下一步怎么测（最重要）
### 最小实验 A：`15m` discovery + `5m` execution refine
- 用最近 18 个月 Binance perp `BTCUSDT` 数据；
- 每天 UTC 00:00 之前滚动预测次日日内 curve；
- 得到 `u_min` / `u_max` 之后，不直接用 `15m close` 成交；
- 改成在对应 `15m` 窗内用 `5m`：
  - 入场等第一根停止创新低 / micro pullback；
  - 出场用窗口内最高 close 或 trailing-stop。

要验证的是：
**在不改变 alpha 本体的前提下，execution 是否能把 4~8 bps 的成本问题救回来。**

### 最小实验 B：slot-return 版本替代 full-curve 版本
如果嫌 FPCA 太学术，可以先做更工程化的替身：
- 直接预测次日 96 个 `15m` slot return 的符号 / 强弱；
- 把“低点后高点”问题改成“连续净多窗口最大化”；
- 和论文版 `curve-min / curve-max` 做 A/B。

要验证的是：
**真正值钱的是“路径预测”本身，还是只是一个 time-of-day mean pattern。**

### 最小实验 C：把它变成 gate，而不是独立主策略
把这条信号拿去给现有 BTC directional 线做 gate：
- 只有当预测曲线显示“未来 4~8 小时整体上行”时，才允许 breakout / OFI continuation 开多；
- 若预测曲线显示“先弱后强”，则更适合先等回踩再接。

要验证的是：
**这条线独立做可能太薄，但当 timing gate 也许更值钱。**

## 10. 主要风险
- **成本风险**：今天这条线最脆弱的就是 round-trip 成本；
- **路径漂移**：低点/高点时段会迁移，不能把历史固定时段当铁律；
- **结构失效**：论文里 2017 后就出现显著衰减，说明 alpha 可能与市场成熟度有关；
- **单币风险**：这篇主看 BTC，不能自动外推到 ETH/SOL；
- **过度学术化风险**：functional 术语很多，但 desk 真正需要的是可交易路径壳，不是更复杂的统计仪式。

## 11. 一句话带走
如果把这篇 2021 论文翻成 desk 语言，我会把它定义成：

> **“预测次日日内路径，再做一笔 buy-forecasted-low / sell-later-high 的 BTC timing trade。”**

它今天在 Binance perp 上 **还有微弱 raw alpha 痕迹**，但更像一个 **低成本、serial-dependence gated 的 directional timing 壳**；下一步最值得做的不是继续卷 functional 术语，而是把它下钻成 `15m discovery + 5m/3m execution` 的成本后版本。