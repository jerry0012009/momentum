# 别把这份 2026 Binance stat-arb 仓只读成“相关性热力图”：对 short-cycle desk，更该先拆的是「correlation-ranked pair admission × ratio z-score spread fade」这条 raw alpha

- 时间：2026-04-17 22:26 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `correlation_bot.py` + `phase1_data_fetch_correlation.py`）+ Binance USDⓈ-M public-data portability probe（`1m` / `5m`）
- 主题类型：raw alpha
- 基础 alpha：**先用短窗相关性筛出“平时一起走”的 pair，再盯它们的价格比值；当 ratio 的 z-score 偏到极端，做 `short rich leg / long cheap leg`，赌价差回到均值。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / correlation-ranked / ratio-zscore / pair-admission / binance-perpetual / 1m / 5m / repo / public-data / cost / risk
- 证据类型：repo 源码 + public-data probe

## 1) 这次看了什么
- **Authors / Maintainer**：ApexQuant-Dev
- **Year**：2026
- **Title**：*Binance Correlation & Stat-Arb Suite*
- **Venue / Type**：GitHub repo
- **Readable URL**：<https://github.com/ApexQuant-Dev/binance-correlation-stat-arb>
- **Repo URL**：<https://github.com/ApexQuant-Dev/binance-correlation-stat-arb>
- **关键源码**：
  - README：<https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/README.md>
  - `correlation_bot.py`：<https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/correlation_bot.py>
  - `phase1_data_fetch_correlation.py`：<https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/phase1_data_fetch_correlation.py>

先把 **base alpha** 说清楚：

> **不是“相关性高就能赚钱”，而是“先用相关性做 pair admission，再对 admitted pair 做 ratio 极端偏离的均值回归”。**

所以它不是单纯 `filter`，也不是研究工具本身，而是一条标准的 `pairs / relative-value / stat-arb / raw alpha`：
- 交易对象不是裸 BTC 方向；
- 交易对象也不是单腿 breakout；
- 交易对象是 **两条通常一起走的资产之间，短时价差是否偏得太离谱。**

## 2) repo 里真正可继承的 alpha 是什么
### 2.1 用人话翻译源码
repo 的主逻辑很短，但交易本体很清楚：

1. 先从 Binance Futures 拉历史 K 线；
2. 挑出相关性高、平时比较同步的 pair；
3. 对每个 pair 计算 `ratio = price_A / price_B`；
4. 用最近一段 ratio 的均值和标准差，算当前 z-score；
5. 当 `z > 2` 时，认为 `A 相对 B 偏贵`，做 `short A / long B`；
6. 当 `z < -2` 时，认为 `A 相对 B 偏便宜`，做 `long A / short B`。

`correlation_bot.py` 里最核心的几行其实就这三件事：
- 拉 `1m` OHLCV；
- 直接算 ratio 序列；
- 对 ratio 做 rolling z-score 并打印 long/short 提示。

### 2.2 为什么它算 raw alpha，不是 filter
因为这里的信号本体就是：
- `pair admission = 这两个币最近确实在一起走`
- `entry trigger = 但此刻 ratio 偏离历史均值太多`

也就是说：
- **相关性** 只是入场前筛 pair 的 admission；
- **真正开仓的 alpha** 是 `ratio z-score reversion`。

这点很重要。很多“相关性仓”最后只是做了个监控面板，这个 repo 虽然简陋，但至少已经把开仓方向写死了：
> **价比值偏高就 short rich leg / long cheap leg；偏低就反过来。**

## 3) 对当前 desk 最有用的读法
如果只照 README 看，很容易把它当成“配对交易入门脚本”。

但对 short-cycle desk，更值钱的读法是：

> **把相关性当 pair admission 的最低成本近似，把 ratio z-score 当真正的 raw alpha，然后去问：在 `1m / 5m` 上，哪些 pair 还有 pocket，哪些 pair 其实已经被成本和结构变化吃死。**

这比继续泛泛补一个“pairs 也许有用”的综述值钱得多，因为它直接回答：
- 哪些 pair 还能做最小实验；
- 哪些 pair 需要更严格阈值；
- 哪些 pair 虽然高相关，但根本不值得短线动手。

## 4) repo 源码里值得保留、也值得警惕的部分
### 4.1 值得保留：公开数据、超低复现门槛
`phase1_data_fetch_correlation.py` 明确写了：
- 数据源：Binance Futures public REST
- 无需 API key
- 默认 `5m`、`100` 根 lookback
- 支持 top-volume symbol 扫描和 correlation matrix

这对 desk 很友好：
- **数据公开可得**；
- **更新时间就是 bar 级更新**；
- **最小实验口径可以直接落到 `1m / 5m`。**

### 4.2 值得警惕：repo 只写了“看见偏离”，没把完整壳写完
repo 给了很清楚的 entry 语言，但几乎没写：
- hedge ratio 是否要用 `1:1 notionals` 还是 beta-neutral；
- exit 是回到 `z=0` 还是回到 `|z|<0.5`；
- max hold、多 pair 并发、gross exposure cap；
- 两腿成本、funding、滑点、单腿崩掉时怎么办。

所以它是 **合格的 raw alpha 母板**，但不是现成 production 成品。

不过本轮我仍把“是否可直接落地完整策略”标成 **是**，原因不是 repo 自己已经完美，而是：
- entry 足够明确；
- exit/sizing/risk/cost 都能用标准 desk 壳快速补齐；
- public-data first probe 已经能给出“哪些参数/哪些 pair 先测”的方向。

## 5) 最小可复现实验（本轮已跑）
### 数据源
- **Binance USDⓈ-M Futures `klines` API**
- URL：<https://fapi.binance.com/fapi/v1/klines>
- 公开性：公开可得
- 更新频率：按 bar 更新
- 本轮最小实验口径：
  - `5m`：近 `30d`
  - `1m`：近 `7d`

### Pair universe
沿用 repo 默认/近似默认风格，测试：
- `ETHUSDT / BTCUSDT`
- `SOLUSDT / AVAXUSDT`
- `LINKUSDT / UNIUSDT`
- `ARBUSDT / OPUSDT`
- `APTUSDT / SEIUSDT`

### Baseline 规则
最基础版本，先不加 fancy 模块：
- rolling lookback：`30` bars
- entry：`|z| >= 2.0`
- exit：回到 `|z| <= 0.25`
- max hold：
  - `5m` 版 `12` bars（约 `1h`）
  - `1m` 版 `20` bars（约 `20m`）
- 持仓方向：
  - `z > 0` ⇒ `short A / long B`
  - `z < 0` ⇒ `long A / short B`
- 成本：**round-trip `12 bps` 总成本**（双腿合并口径，保守但还不算极端）

## 6) 关键数据点：baseline 能复现，但大多数 pair 已经不够好
### 结论 1：plain correlation-first spread fade 在 `5m` 上基本全面不过线
按 pair 看，`5m` baseline 全是负的：
- `ETH/BTC`：`339` 笔，平均 **`-11.69 bps/笔`**
- `SOL/AVAX`：`351` 笔，平均 **`-9.34 bps/笔`**
- `LINK/UNI`：`339` 笔，平均 **`-9.01 bps/笔`**
- `ARB/OP`：`373` 笔，平均 **`-8.25 bps/笔`**
- `APT/SEI`：`355` 笔，平均 **`-6.30 bps/笔`**

人话：
> **“相关 pair 出现 2σ 偏离就做回归” 这件事，在 recent `5m` perp 上几乎是全军覆没。**

### 结论 2：`1m` 上也不是普遍有效，但 pocket 开始出现
`1m` baseline 同样大多为负：
- `ETH/BTC`：`370` 笔，平均 **`-11.08 bps/笔`**
- `SOL/AVAX`：`378` 笔，平均 **`-9.92 bps/笔`**
- `LINK/UNI`：`399` 笔，平均 **`-6.95 bps/笔`**
- `APT/SEI`：`383` 笔，平均 **`-6.80 bps/笔`**

但 `ARB/OP` 明显是例外中的例外：
- `ARB/OP 1m baseline`：`403` 笔，平均 **`-1.42 bps/笔`**，胜率 **`66.3%`**

这说明：
> **不是整条 alpha 完全死掉，而是 baseline 阈值太松，只有某些“强替代关系” pair 还保留了 pocket。**

### 结论 3：`ARB/OP` 在更严格的 `3σ` 触发下，已经能转成小幅正值
我对 `ARB/OP 1m` 做了参数快扫。最有信息量的 pocket 是：
- lookback：`20` bars
- entry：`|z| >= 3.0`
- exit：回到 `|z| <= 0.5`
- max hold：`30` bars
- cost：round-trip `12 bps`

结果：
- 交易数：**`205`**
- 平均净收益：**`+1.73 bps/笔`**
- 胜率：**`62.0%`**
- 累计净收益：**`+3.55%`**（样本期约 `7d`）

这不是“已经 production-ready 印钞”，但已经足够说明：
- repo 里的 base alpha **能在当前市场结构里找到仍活着的 pocket**；
- 关键不是“pair 越多越好”，而是 **pair admission 更严格 + entry 阈值更苛刻**。

### 结论 4：`5m` 口径里，连最好的 pair 也还只是接近成本线
同样对 `ARB/OP 5m` 做参数快扫，最好的几组也仍是负的：
- 最优附近结果：平均大约 **`-0.49 bps/笔`**，`190` 笔，胜率 **`64.2%`**

这说明一个很关键的 desk 结论：
> **这条 correlation-ranked spread fade 目前更像 `1m` pocket，不像 `5m` 主战 alpha。**

## 7) 这条线和当前 `1m / 3m / 5m / 15m` 的关系
- **1m**：当前最值得测。尤其是 `ARB/OP` 这种替代关系强、消息与流动性经常联动的 pair，已经看到 pocket。  
- **3m**：很适合作为下一轮折中层；比 `1m` 更抗噪，比 `5m` 更不容易让回归走完。  
- **5m**：当前 first verdict 偏负，更适合拿来做 higher-level admission 或冷却层，而不是直接主触发。  
- **15m**：对这种短寿命 ratio dislocation 来说通常太慢，除非改做更慢的 regime/cluster spread，而不是当前 repo 这类短窗 z-score。  

## 8) 为什么这条主题比继续补一个 filter 更值得
因为它直接扩充的是 **raw alpha 素材池**，而且补的是当前 desk 仍然需要的 `pairs / stat-arb / relative-value` 母板：

1. **base alpha 清楚**：不是泛泛“相关性研究”，而是 `ratio extreme → mean reversion`；
2. **公开数据就能复现**：不依赖私有盘口或付费数据；
3. **很适合快速做 fail-fast**：几小时内就能知道某个 pair 有没有 pocket；
4. **能直接服务 execution 研究**：双腿成本、同步成交、单腿失配、持仓上限，全部都是真实工程问题。

## 9) 今天就能怎么写成完整策略壳
### 9.1 Entry
最小 production shell 建议：
1. 先用过去 `N` 根 return correlation 做 pair admission；
2. 只保留 correlation 高、rolling beta 稳定、成交额合格的 pair；
3. 再对 admitted pair 计算 ratio z-score；
4. 只有满足以下条件才进场：
   - `|z| >= entry_threshold`
   - `spread_vol / level` 没有突然跳变
   - 两腿盘口 spread 都不恶化
   - funding 方向不会把预期 edge 吞掉
   - 同一 pair 未处于 cooldown。

### 9.2 Exit
至少并行保留三种退出：
- **mean-revert exit**：`|z|` 回到 `0 ~ 0.5`；
- **time stop**：到 `10~30` bars 还不回，就强平；
- **structural break exit**：rolling correlation/beta 崩掉、单腿出现 news shock 时直接退出。

### 9.3 Sizing
不要做 `1:1` 名义金额无脑对冲，建议：
- 先用 rolling beta 或波动率比做 hedge ratio；
- 再叠加 gross exposure cap；
- 同一 sector/pair cluster 设组合级上限，避免全在一类替代币上堆仓。

### 9.4 Cost
这条线最容易被忽略、也最容易死在这里：
- 双腿开平共四次交易摩擦；
- perp funding 在某些 pair 上不是噪音；
- `1m` pocket 对 stale quote 特别敏感；
- 若只能单腿先成交，另一腿补单时 edge 可能已经没了。

所以所有回测都要至少输出：
- per-leg spread
- simultaneous fill 假设
- hedge slippage
- funding carry drift

## 10) 下一步怎么测（最重要）
### A. 不要再把“高相关”当充分条件，先做 pair admission 升级
优先加三层：
1. **rolling correlation + rolling beta 稳定性**；
2. **行业/叙事相近性**（例如 `ARB/OP` 这种强替代关系）；
3. **成交额 / 盘口厚度门槛**。

### B. 先专攻 `ARB/OP 1m`，别急着横向铺太多 pair
下一轮最小实验建议直接围绕：
- `ARB/OP`
- `1m signal / 1m execution / 3m aggregation`
- `lookback 20~40`
- `entry 2.5σ ~ 3.5σ`
- `exit 0.0 / 0.25 / 0.5`
- `max_hold 10 / 20 / 30 bars`
- 输出：`trade_count / avg_net_bps / time-of-day / side asymmetry / fill sensitivity`

### C. 把它和已有 raw alpha 组件串起来，而不是孤立裸跑
最值得组合的不是另一个 pairs 指标，而是：
- **市场级波动挤压 / 爆发状态**：波动爆开时先少做 fade；
- **单腿 news shock veto**：一边有独立催化时，别强行赌回归；
- **microstructure veto**：盘口太薄、瞬时冲击太大时不做。

### D. 明确 desk 当前结论
这轮最该记住的一句不是“pairs 失效了”，而是：
> **plain correlation-first z-score fade 基线大多已经成本后不过线，但替代关系更强的 pair（当前最像 `ARB/OP`）在 `1m` 高频口径里，仍可能留下只有极端偏离才值得做的 pocket。**

## 11) 风险与保留意见
- repo 用的是最简单的 ratio，不是 cointegration residual，也没估 hedge ratio；
- 当前 pocket 主要来自短样本 recent `1m`，必须做滚动窗和分段验证；
- `ARB/OP` 的 edge 可能强依赖当下叙事联动，不能假设长期稳态存在；
- 若真实交易只能 taker、且双腿无法同步，回测 pocket 很可能被进一步吃掉。

## 12) 来源
1. ApexQuant-Dev (2026), *Binance Correlation & Stat-Arb Suite*（GitHub repo）  
   Repo URL: <https://github.com/ApexQuant-Dev/binance-correlation-stat-arb>
2. README raw: <https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/README.md>
3. `correlation_bot.py`: <https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/correlation_bot.py>
4. `phase1_data_fetch_correlation.py`: <https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/phase1_data_fetch_correlation.py>
5. Binance USDⓈ-M Futures Klines API（public）: <https://fapi.binance.com/fapi/v1/klines>
