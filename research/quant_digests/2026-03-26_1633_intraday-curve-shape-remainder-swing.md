# 别把 intraday curve 只当图形化展示：这篇 2021 IRFA 更该先测的是「partial-day path shape → remainder-of-day swing」15m raw alpha
- 时间：2026-03-26 16:33 UTC
- 类型：2021 International Review of Financial Analysis 开放获取论文（全文 PDF 可读）+ Binance Futures 公共 `15m` 最小 transfer check
- 主题类型：raw alpha
- 基础 alpha：**当天已经走出来的 intraday 累计收益曲线形状（path shape），对当天剩余时段的 swing 方向与极值时点有预测力。** 对 desk 更值钱的第一版，不是照搬论文做“明天整天的路径预测”，而是做 `partial-day curve shape -> 剩余时段 long-only swing`。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/btc/intraday/path-shape/functional-time-series/cidr/remainder-of-day/swing/kNN/15m/5m/1m/3m/binance/bitstamp/paper
- 证据类型：全文论文证据 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，也不是“市场结构解释层”。base alpha 就是“当前日内路径长什么样，会影响接下来这一天剩余时段怎么走”，可以直接写成可交易的 intraday raw alpha。**

## 1. 这次看了什么
主来源：
- **Elie Bouri, Chi Keung Marco Lau, Tareq Saeed, Shixuan Wang, Yuqian Zhao (2021), _On the intraday return curves of Bitcoin: Predictability and trading opportunities_, International Review of Financial Analysis, DOI: `10.1016/j.irfa.2021.101784`**

这篇东西最值钱的地方，不是“Bitcoin 日内路径可以被 FPCA 描一下”，而是它已经把故事推进到交易层：
- 先把 **CIDR（cumulative intraday return）曲线** 当作预测对象；
- 再用 **projection scores** 的可预测性去 forecast 下一天整条 intraday path；
- 最后直接把 forecasted path 的 **min / max timing** 翻译成 `buy at predicted min -> sell at predicted later max` 的交易计划。

对当前 desk 来说，最值得先测的不是论文 headline 里的“next-day full-curve forecast”，而是更快的 desk 读法：
- **今天前半段/前 1/3 的路径形状，能不能告诉我们今天后半段更像 continuation、反弹，还是先低后高的 swing？**
- 这条线可以天然映射到 `1m / 3m / 5m / 15m`，尤其适合 `15m signal bar + 余下时段退出` 的最小实验。

## 2. 核心结论
### 一句话核心结论
**Bitcoin 的 intraday path 不是完全“今天长什么样、后面都没信息”；path shape 本身就是信号。对短周期 desk，更值得先测的是“partial-day path shape -> remainder-of-day swing”。**

### 一句话它怎么证明
论文做法是：
1. 用 **5 分钟 BTC/USD（Bitstamp）** 构造每日 CIDR 曲线；
2. 用 **functional PCA** 压缩成 projection scores；
3. 只在 scores 出现序列相关的时段，用 **指数平滑 / AR(1)** forecast 下一天 CIDR 曲线；
4. 依据 forecast curve 的 **预测最低点和之后的预测最高点** 制定日内交易计划；
5. 结果显示：**gross 有利润，含 3bps fee 后仍有正 Sharpe，但非常依赖 regime，且 drawdown 不小。**

### 这轮最该记住的 5 个数字
1. **论文原始样本**：Bitstamp `5m` BTC/USD，**2014-11-01 ~ 2019-08-10**，共 **1367 天**；`2015-01-05 ~ 2015-01-10` 因 hacked exchange event 被剔除。  
2. **论文主策略（FPAR, rolling window `S=182`，每天都交易，不允许裸空，未计费）**：**annualized return 64.70% / vol 58.15% / Sharpe 1.11 / max drawdown -99.25%**。  
3. **加 0.03% fee 后（Appendix A3，同样 `FPAR, S=182`）**：**annualized return 42.78% / vol 58.13% / Sharpe 0.74**。说明它不是一碰成本就全死，但也绝不是“稳赚小机器”。  
4. **论文自己也承认 edge 不是全天候**：只有在 **第一或第二个 projection score 出现 serial correlation** 的样本里，FPES / FPAR 的 forecast 才明显优于 mean benchmark。  
5. **本地 `15m` desk 化快检（2025-11-17 ~ 2026-03-15，BTCUSDT full-day bars）**：
   - `观察前 8h path shape + 60d lookback + 3-NN + exit at predicted max`：**18 笔、avg trade +0.463% 、hit 50.0%、gross Sharpe 3.25、max DD -6.97%**；
   - 同一变体按 **6bps round-trip** 扣费后仍有 **avg trade +0.403%、Sharpe 2.83**；
   - 但 **观察前 4h** 的更早版本明显弱得多：`3-NN` 只有 **16 笔、avg trade +0.177%、gross Sharpe 0.86、6bps 后 Sharpe 0.57**。  

## 3. 为什么和当前 desk 直接相关
这条线和当前 short-cycle desk 的关系很直接：
- 它是 **raw alpha**，不是 overlay。
- 它补的是当前池子里相对少见的一类：**path-shape / trajectory-based directional alpha**，不是单看上一根收益、单个阈值、或横截面排序。
- 它天然能服务于多个时钟：
  - `15m`：先做最便宜的版本；
  - `5m`：后续把 path 细化，增强样本量；
  - `1m/3m`：如果以后只交易特定 session pocket，可以再下钻。

更重要的是，这篇 paper 给了一个很诚实的提醒：
- **边不是全天候存在**；
- 真正有信息的是 **某些 path regime**；
- 所以对 desk 来说，这条线的价值，不在于“照搬一套 FPCA 预测器”，而在于把 **path-state** 变成一条新的信号轴：
  - 已经走出 `U-shape` 的日子，后半段是否更容易收在更高？
  - 已经走出单边下坠的日子，后半段是否更容易继续创新低、还是回补？
  - 哪些 partial-day shape 应该只做 long swing，哪些应直接 veto？

## 3.5. 策略拆解（必填）
- 方向属性：single-asset / intraday / path-shape directional raw alpha
- 基础 alpha：当前日内累计收益曲线的**形状**，对剩余时段的 swing 极值位置和方向有预测力
- regime：只在 path-shape 与历史模板足够相似、且预测剩余路径有足够正空间时开机
- filter / veto：
  - 只做流动性最好的 BTC 主合约 / 主 spot
  - 避开重大事件分钟（CPI/FOMC 等）和异常缺口日
  - 只保留 `predicted max - current level` 高于成本阈值的 setup
- risk / sizing / execution overlay：
  - 第一版只做 long-only，避免把问题一次性扩成双边路径策略
  - 单笔风险固定；若当天 path 已非常极端，size-down
  - 默认用 maker / passive limit，减少把小 edge 全打掉
- entry（desk 第一版）：
  1. 以 `15m` bars 构造当日累计 intraday log-return 曲线；
  2. 到观测时点（先测 `4h / 6h / 8h`）时，取当前 partial path；
  3. 在过去 `60d` 的同频 full days 里找 shape 最近邻（首轮 `k=3/5`）；
  4. 若邻居的 average remainder path 预示后续仍有正向 swing，开 long；
- exit：
  - 第一版按 **predicted future max timing** 平仓；
  - 对照组：`hold to EOD`、`固定 4/8/12 bars`。

## 4. 论文里最值钱的细节，不该漏掉什么
### 4.1 样本与方法
- 数据：Bitstamp BTC/USD `5m`
- 区间：`2014-11-01 ~ 2019-08-10`
- 核心对象：每日 **CIDR** 曲线，定义为 `100 * (log P(u) - log P(0))`
- 方法：
  - 用 FPCA 提取 curve modes；
  - 取能解释 **90% total variation** 的主成分数；
  - 对 score 做 forecast：`Fmean`（均值基线）、`FPES`（指数平滑）、`FPAR`（AR(1)）

### 4.2 论文自己的交易翻译
论文不是只做 forecast error，而是直接写成交易：
1. 用前 `w` 天数据估模型；
2. 生成 **下一天** forecasted CIDR；
3. 找 forecast curve 的 **预测最低点** 作为开多时刻；
4. 再在它之后找 **预测最高点** 作为平仓时刻；
5. 次日按这个时间表执行。

这点很关键：
- 它说明这篇 paper 并不是“可预测，但没法交易”的纯学术展示；
- 它已经包含了最小的 `entry / exit` 翻译。

### 4.3 论文真正诚实的地方：不是 always-on edge
论文里最该保留的 caveat：
- 整体看，`FPES / FPAR` **并不总是优于** `Fmean`；
- 只有在 **projection scores 存在 serial correlation** 的时段，forecast 才明显改善；
- 作者还明确写到：策略在 **2017 年 2 月前更稳定赚钱**，之后一度失效，到 **2018 年 12 月** 左右达到最大回撤后才恢复。

所以这条线绝不能被误写成“全样本都稳”。更诚实的 desk 读法应该是：
- **path alpha 先天就是 regime-dependent**；
- 关键不是“有没有一条万能 path 策略”，而是“何时 path 变得有预测力”。

## 5. 可复刻的最小实验
### 数据源与公开性
- 论文数据：Bitstamp BTC/USD `5m`
- 本地快检数据：`reports/artifacts/scout_rank76_intraday_clock_polarity_15m/btcusdt_feature_frame.csv`
  - 来源：Binance Futures 公共 K 线缓存
  - 公开性：公开可得
  - 更新频率：`15m`
  - 本轮使用：只保留 **119 个 full-day** (`96 x 15m`) 交易日，区间 `2025-11-17 ~ 2026-03-15 UTC`

### 第一版最小实验口径
- signal bar：`15m`
- asset：`BTCUSDT`
- lookback：`60d`
- path construction：`当天开盘到当前时刻的累计 log-return path`
- similarity：对 partial path 做 shape normalization 后，找最近邻 `k=3/5`
- signal：若邻居平均 remainder path 仍指向更高 future max，则开 long
- exit：预测 future max 所在 bar
- 成本：先看 gross，再看 `4 / 6 / 10 bps round-trip`

### 这轮本地快检结果
#### 5.1 最强版本：先观察 8 小时，再做余下时段 swing
- 配置：`obs=32 bars (=8h), k=3`
- trades：**18**
- avg trade：**+0.463% gross**
- hit rate：**50.0%**
- gross Sharpe：**3.25**
- max drawdown：**-6.97%**
- `6bps` round-trip 后：**avg trade +0.403% / Sharpe 2.83**

这说明：
- 对 `15m` desk 版本，这条线现在更像 **late-session path-state alpha**；
- 不是早盘一开就能知道，而是 **路径先走出来一点，后面再做 swing**。

#### 5.2 较弱版本：想更早下手，边明显变薄
- 配置：`obs=16 bars (=4h), k=3`
- trades：**16**
- avg trade：**+0.177% gross**
- hit rate：**43.8%**
- gross Sharpe：**0.86**
- `6bps` 后 Sharpe：**0.57**

这表明更早的 path inference 还不够稳，至少在当前短样本上，**路径要多展开一点，signal 才变厚**。

#### 5.3 它不是“参数随便换都活”
- `obs=24 bars (=6h), k=5`：gross Sharpe 只有 **0.60**，`6bps` 后已转负；
- `obs=32 bars, k=5` 还能活，但明显弱于 `k=3`；
- 所以这条线当前更像 **有 pocket 的结构性想法**，不是大范围参数平原。

## 6. 下一步怎么测
1. **把 `15m` partial-shape 版本降采样到 `5m`**：保留同样的 path-state 逻辑，但把观察点改成 `2h / 4h / 6h`，提升样本量与时点分辨率。  
2. **把 kNN 升级成更接近论文的 rolling FPCA**：不是为了学术完美，而是为了分清：当前 edge 到底来自 `shape-neighbor`，还是来自 `projection score dynamics`。  
3. **显式加 regime gate**：先用 projection-score serial-correlation proxy、realized vol、event-clock 三条 gate，回答“哪类天 path 才有预测力”。  
4. **做 exit family 对照**：`predicted max exit` vs `EOD exit` vs `fixed-hold`，确认 edge 是来自“方向判断”还是来自“极值时机判断”。  
5. **把单资产扩到 ETH**：如果 ETH 也能复制出类似的 late-session path edge，这条线才值得从 BTC 单点升为 desk 组件。  
6. **做执行诚实性检查**：当前 trade count 不高，paper 也提醒 latency / venue microstructure 会影响执行；所以必须加上 maker fill 假设、盘口深度和 session 分层。  

## 7. 风险与保留意见
- 论文原始结果虽然漂亮，但 **max drawdown 非常大**，说明它不是“低波稳态现金流”。  
- 论文最强结果来自 **2014~2019 的 Bitstamp spot**；我们现在关心的是 `2025Q4~2026Q1` 的 Binance-style short-cycle 环境，中间有明显 regime 漂移。  
- 本地快检里最好的变体只有 **18 笔交易**，样本很短，annualized 指标容易被放大。  
- 当前 edge 更像 **late-session pocket**，如果 desk 需要“全天候、早盘就能部署”的 raw alpha，这条线暂时还不够。  
- 所以它现在最诚实的状态应是：**值得进研究池，但先以 path-state pocket alpha 记账，不要急着写成全天候主策略。**

## 8. 来源
1. **Bouri, E., Lau, C. K. M., Saeed, T., Wang, S., & Zhao, Y. (2021). _On the intraday return curves of Bitcoin: Predictability and trading opportunities_. International Review of Financial Analysis, 76, 101784.**  
   - DOI: `10.1016/j.irfa.2021.101784`  
   - Readable URL: `https://repository.essex.ac.uk/30487/`  
   - PDF URL: `https://repository.essex.ac.uk/30487/1/Bitcoin_Functional%20V8%20Clean.pdf`  
   - Venue URL: `https://doi.org/10.1016/j.irfa.2021.101784`  
   - Repo URL: `未见作者官方开源代码`
2. **Binance USDⓈ-M Futures Kline/Candlestick Data Docs**  
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9. 本地产物
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/variant_summary.csv`
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/cost_sensitivity.csv`
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/selected_variant_trades.csv`
- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/meta.json`

## 10. 当前 verdict
**值得进研究池，而且按 raw alpha 记账；但当前更诚实的 desk 落点不是“照搬论文做 next-day full-curve 预测”，而是先把它改写成 `partial-day path shape -> remainder-of-day swing` 的 `15m` pocket alpha，再决定是否下钻到 `5m / 1m / 3m`。**
