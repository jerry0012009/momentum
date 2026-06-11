# 别把 BTC 领涨只读成“市场 beta”：这篇 2026 *Asia-Pacific Financial Markets* 更该先测的是「BTC lead × low-liquidity alt lag」这条 raw alpha

- 时间：2026-04-06 05:58 UTC
- 类型：2026 *Asia-Pacific Financial Markets* 开放获取论文全文（Springer article page + full-size tables）+ Binance public `1m` spot data 本地 portability probe
- 主题类型：raw alpha
- 基础 alpha：**BTC 先动、低流动性小市值 ALT 后动；做的是 `leader-laggard` 信息传导迟滞，而不是泛化“跟着 BTC 看大盘”。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-market/leader-laggard/liquidity-lag/small-cap/altcoins/binance/spot/high-frequency/1m/3m/5m/15m/paper/open-access/public-data/cost/risk
- 证据类型：开放获取论文全文 + full-size tables + 公共 `1m` K 线/成交笔数 + 本地 horizon portability probe

## 1. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = `BTC 上一分钟收益 -> 低交易频次 ALT 下一分钟跟涨/跟跌`。**

翻成人话：
- 不是“BTC 强所以 alt 也会强”这种空话；
- 而是 **BTC 的信息先被价格发现，低流动性 ALT 吸收这段信息更慢**；
- 所以可交易对象不是 BTC 本身，而是 **那些还没来得及 fully catch up 的小币**。

这条东西天然属于 **cross-market / leader-laggard raw alpha**，不是 filter，也不是 overlay。

## 2. 为什么这轮值得进研究池

当前 digest 池最近几轮已经连续补了不少：
- funding / basis carry，
- pairs / stat-arb，
- microstructure directional，
- event-driven。

这篇 paper 值得补的地方在于：

1. **它是独立 raw alpha，不依赖先有 breakout / trend shell。**  
   这点很关键：不是拿 BTC 当 regime gate，而是直接拿 BTC 当 **leading leg**。

2. **它是公开数据就能做的最小实验。**  
   只要有：
   - Binance `1m` close
   - Binance `1m` trade count
   就能先验证延迟是否真的存在。

3. **它直接补 desk 当前更该持续 intake 的 cross-market / relative-value 素材。**  
   不是继续在单一形态里打转，而是扩 `leader-laggard` 这条可复现 alpha 家族。

## 3. 来源与材料

### 主论文
- **Authors**：Tomoki Kurihara, Takuji Matsumoto
- **Year**：2026
- **Title**：*Price Transmission from Bitcoin to Altcoins: High-Frequency Evidence and Implications for Trading Strategy*
- **Venue**：*Asia-Pacific Financial Markets*
- **DOI**：`10.1007/s10690-026-09589-z`
- **Readable URL**：<https://link.springer.com/article/10.1007/s10690-026-09589-z>
- **PDF URL**：<https://link.springer.com/content/pdf/10.1007/s10690-026-09589-z.pdf>
- **Repo URL**：未见作者公开 companion repo（paper-only）

### 本地复现实验所用公开数据
- **数据源**：Binance spot monthly `1m` klines（data.binance.vision）
- **公开性**：公开可直连下载，无 key
- **最小实验字段**：`close`, `trade_count`
- **本地产物**：
  - `reports/artifacts/quant_digests/2026-04-06_btc-alt-liquidity-lag-alpha/leadlag_by_horizon.csv`
  - `reports/artifacts/quant_digests/2026-04-06_btc-alt-liquidity-lag-alpha/leadlag_horizon_summary.csv`

## 4. 论文里最该拿走的硬信息

这篇 paper 不是只讲“BTC 会影响 alt”。它把 **怎么影响、影响多久、哪些币更慢、策略怎么落地** 讲得很具体。

### 4.1 样本与方法
- 数据来自 **Binance API 的 `1m` close + trade count**；
- Bull regime 用到 **369** 个币，Bear regime 用到 **381** 个币；
- 重点细看：`BTC / ETH / LTC + 5 个低交易频次小币（BIFI / CITY / PIVX / GNO / QKC）`；
- 论文定义了一个 **Immediate Sensitivity Indicator (ISI)**，专门衡量某个 ALT 是“立刻跟”还是“慢半拍再跟”；
- 还做了：
  - cross-correlation，
  - Granger causality，
  - VAR，
  - impulse response，
  - 最后再做策略回测。

### 4.2 论文最关键的 4 个结论

1. **低交易频次 ALT 更慢反应 BTC。**  
   - Bull regime：`log(trade count)` 与 `ISI` 的相关系数是 **0.561**；
   - Bear regime：对应相关系数是 **0.483**。  
   含义：越不活跃，越容易慢半拍。

2. **BTC -> ALT 的单向 lead 基本成立。**  
   论文的 Granger test 显示：
   - `BTC(t-1)` 对 ALT 预测显著；
   - 反过来 `ALT(t-1) -> BTC` 大多不显著。  
   也就是说，这不是“大家互相带”，而更像 **BTC 先发现，ALT 后补价**。

3. **作者不是停在统计结论，而是直接做了交易壳。**  
   他们的交易输入只用了：
   - `BTC(t-1) return`
   - `ALT(t-1) return`

4. **最优阈值不是激进追价，而是“易进、慢出”。**  
   Paper Table 4 给出的最优阈值：
   - Bull：`entry = 0.0000`, `hold = -0.0001`
   - Crash：`entry = 0.0000`, `hold = -0.0001`
   - Sideways：`entry = 0.0001`, `hold = -0.0001`

翻成人话：
- **入场门槛很低**，只要 lag 线索出现就愿意上；
- **出场门槛更宽**，宁可多拿一会，少被手续费来回磨死。

## 5. 论文里最能打的结果

论文最有用的不是“准确率”，而是它给出了很直白的 OOS 累计收益对比。

### 5.1 Appendix Bull sub-sample（Table 7）
- `QKC`：Buy-and-Hold **7%** vs Lag Strategy **59%**
- `PIVX`：Buy-and-Hold **7%** vs Lag Strategy **81%**
- `BIFI`：Buy-and-Hold **1%** vs Lag Strategy **49%**
- `CITY`：Buy-and-Hold **0%** vs Lag Strategy **7%**
- `GNO`：Buy-and-Hold **6%** vs Lag Strategy **6%**

### 5.2 Appendix Bear sub-sample（Table 6）
- `QKC`：Buy-and-Hold **-9%** vs Lag Strategy **116%**
- `PIVX`：Buy-and-Hold **-12%** vs Lag Strategy **69%**
- `BIFI`：Buy-and-Hold **-6%** vs Lag Strategy **96%**
- `GNO`：Buy-and-Hold **-6%** vs Lag Strategy **41%**
- `CITY`：Buy-and-Hold **-10%** vs Lag Strategy **23%**

当然，这些数字不能直接照搬到我们 desk：
- 样本是 spot；
- 标的是低流动性小币；
- paper 的 implementation 更接近 event/regime 内的单边持仓，不是我们永续盘面的统一执行框架。

但它已经足够说明一句话：

> **这不是“统计上有点延迟”而已，而是有可能长成完整策略的 raw alpha。**

## 6. 对 short-cycle desk，最诚实的读法是什么？

### 6.1 诚实版
把它读成：

**`BTC leader` + `low-liquidity alt lagger` + `短持有 catch-up`**

而不是：
- 看到 BTC 涨就无脑追所有 alt；
- 拿它当 generic market beta；
- 或者误读成又一个“趋势确认 filter”。

### 6.2 它服务的不是哪个旧 parked 形态，而是一个新鲜、可独立站立的 alpha 家族
这条线本质上属于：
- `cross-market`
- `leader-laggard`
- `relative-value / lag-arb`

所以这轮值得单独 intake，不需要挂靠旧的 breakout / retest / park 叙事。

## 7. desk 版可落地策略骨架

## 7.1 Universe
先不要贪大：
- `BTCUSDT` 做 leader；
- 只选 **低交易频次、但仍可成交** 的 ALT 子集做 lagger；
- 第一轮优先 spot 做 honest replication；
- 第二轮再映射到 **有 perp、但仍明显慢于 BTC 的 alt-perp**。

最重要的不是小币越小越好，而是：
- **trade count 足够低到有 lag**；
- **又没低到根本没法成交**。

## 7.2 Signal
最小版先照 paper 主体：
- `x1 = BTC(t-1) return`
- `x2 = ALT(t-1) return`

直觉上：
- 如果 BTC 刚刚大幅动了，
- 而 ALT 自己上一分钟还没 fully move，
- 就有 catch-up 空间。

可以先做两个版本：

### 版本 A：最朴素同向 lag trade
- 若 `BTC(t-1)` 上涨超阈值，且 `ALT(t-1)` 同向但幅度偏小，做多 ALT 1 bar
- 若 `BTC(t-1)` 下跌超阈值，且 `ALT(t-1)` 跟跌不足，做空 ALT 1 bar

### 版本 B：paper-style classifier
- 特征：`[BTC(t-1), ALT(t-1)]`
- 输出：`next-bar return > entry_threshold ?`
- 维持单独 hold classifier

## 7.3 Entry / Exit
先照论文精神，不要一上来加花活：

### Entry
- `entry threshold` 从 `0bp / +1bp` 开始扫；
- 只在 `BTC(t-1)` move 达到 rolling quantile（例如 p70/p80）时触发；
- ALT 必须仍处于“未完全 catch up”状态：
  - 同向但幅度更小，或
  - 当根 trade count 仍低于其自身 rolling median。

### Exit
- 主出场：**固定持有 1 bar**（先诚实）
- 再测：`2~3 bars` hold
- 若 ALT 已经一口气补完、超过 BTC impulse 的投影，就立刻平
- 不要第一轮就上 trailing stop，把因果关系弄脏

## 7.4 Sizing
- 单标的按 `1 / realized vol` 或 `1 / ATR` 做轻量 inverse-vol
- 再叠一层 **trade-count cap / notional cap**
- 单腿先从组合 `25bp~50bp` 风险预算起步

## 7.5 Cost
paper 直接按 **0.02% fee** 记账，这点很有参考价值。

我们 desk 第一轮也该这么老实：
- 先按 **taker 双边 4bps** 或更保守口径记账；
- 如果 spot-only replication 能活，再看 maker 或 perp 优化；
- 这条 alpha 最怕的不是方向错，而是 **edge 太短，被执行摩擦吃掉**。

## 8. 我做的最小 portability probe

为了避免只抄 paper，我用它 bull regime 的同一批公开 Binance `1m` 数据，先做了一个最小 horizon 检查。

### 8.1 实验口径
- 数据：`2024-02-25 ~ 2024-03-25 UTC`
- 标的：`BTCUSDT` + `QKCUSDT / GNOUSDT / PIVXUSDT / CITYUSDT / BIFIUSDT`
- 来源：`data.binance.vision` spot monthly `1m` klines
- 指标：
  - `corr(BTC_t, ALT_t)`
  - `corr(BTC_{t-1}, ALT_t)`
  - `lead_edge = corr(BTC_{t-1}, ALT_t) - corr(BTC_t, ALT_t)`
- 目的：看这条信息传导迟滞能不能自然映射到 `1m / 3m / 5m / 15m`

### 8.2 结果

#### 1m：还有可见 lag
- 5 个小币里有 **3 个** 仍然是 `lead_edge > 0`
- 横截面 `median lead_edge = +0.0089`

#### 3m：基本开始被同 bar catch-up 吞掉
- `median lead_edge = -0.1524`
- **0/5** 为正

#### 5m：lead 几乎完全变成 contemporaneous
- `median lead_edge = -0.2647`
- **0/5** 为正

#### 15m：已经不该再把它当 primary signal
- `median lead_edge = -0.4494`
- **0/5** 为正

### 8.3 这组 portability probe 的 desk 含义

这组结果非常重要，因为它告诉我们：

> **这条 alpha 的“物理半衰期”非常短。**

也就是说：
- **`1m` 是主战场**；
- `3m` 还能勉强做 child aggregation / batch execution；
- `5m/15m` 更像是用来做 sampling / regime summary，不该再假装是原生信号频率。

如果硬把它抬成 `15m` 主信号，本质上就不是在复现这篇 paper，而是在做另一条东西了。

## 9. 这条 alpha 的风险点

1. **最核心风险是成本和容量。**  
   这条 edge 很短，错的不是方向时常，而是来不及吃到净收益。

2. **它天然偏向低流动性币。**  
   alpha 越明显的地方，往往越难做大。

3. **spot replication 和 perp deployment 之间有断层。**  
   论文主样本是 spot，小币 perp 是否保留同样 lag，需要单独审计。

4. **一旦市场参与者都知道 BTC lead，edge 可能退化很快。**  
   这类 micro inefficiency 不是“永恒 factor”，更像 contingent pocket。

## 10. 下一步怎么测

### P0：先做 honest replication
- 直接复刻 paper 的 bull / bear / sideways / crash 四段
- 用同一批 symbol、同样 `1m` 数据、同样 fee = `2bps one-way`
- 尽量贴 paper 的 classifier / threshold 设计

### P1：做 desk portability
- 把标的换成 **当前仍可稳定成交的小币/alt-perp 子集**
- 比较 `1m` 与 `3m`：
  - hit rate
  - gross edge
  - after-cost edge
  - fill ratio

### P2：加最必要但不偷换主语的 gate
只加两层：
1. `trade_count / quote-volume floor`
2. `BTC impulse quantile gate`

注意：
- 不要一上来塞 sentiment、funding、order-book 一堆 feature；
- 先确认 base alpha 自己能不能活。

### P3：扩展到 ETH-lead companion line
论文结尾明确提到：**ETH 对某些 ALT 的解释力可能不低于 BTC。**
所以下一步很自然：
- `BTC -> alt`
- `ETH -> alt`
- `BTC/ETH 二选一 leader router`

这一步如果成立，才有机会把它从“BTC 单 leader lag trade”扩成更完整的 cross-market sleeve。

## 11. 结论

这篇 paper 值得进池，不是因为它又证明了一次“BTC 很重要”，而是因为它把一句更可交易的话讲清楚了：

> **当 BTC 先动、而低流动性 ALT 还没 fully absorb 这段信息时，市场里会出现一段很短、但可建壳的 catch-up alpha。**

对我们 desk 来说，最重要的不是把它吹成万能策略，而是接受它的真实边界：
- 它是 **raw alpha**；
- 它更偏 **`1m / 3m`**，不是天然 `15m`；
- 它最先该补的是 **honest replication + cost audit**，不是 fancy feature soup。

如果要一句最短结论：

**这是值得补进 short-cycle 素材池的 cross-market raw alpha；但必须把它当“超短半衰期的 BTC→ALT lag pocket”，而不是泛化的大盘 beta 跟随。**
