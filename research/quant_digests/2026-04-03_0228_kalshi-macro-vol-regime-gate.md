# 别把 Kalshi 宏观赔率重定价硬装成逐根 alpha：对 short-cycle desk，更该先测的是「Fed / CPI repricing × shared volatility regime gate」

- 主题类型：regime
- 基础 alpha：**无独立 raw alpha；这是把 Kalshi 宏观事件合约的概率重定价，转成已有 short-cycle raw alpha（breakout / continuation / mean reversion / stat-arb）的共享波动率 regime gate / sizing layer**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 时间：2026-04-03 02:28 UTC
- 类型：2026 arXiv 全文 HTML（可读正文）+ Kalshi 公共数据路径
- 主题标签：regime / filter / overlay / external-data / prediction-market / kalshi / fed / cpi / recession-risk / volatility-forecast / shared-gate / position-sizing / breakout / momentum / mean-reversion / stat-arb / btc / eth / sol / ada / link / 15m / 5m / 3m / 1m / paper / public-data
- 证据类型：paper-based（全文可读）+ public-data short-cycle translation

## 1. 这次为什么不是继续补 raw alpha，而是补一个 shared gate？

按这轮优先级，**raw alpha 仍然排第一**。但翻完最近的 digest 和学习轨迹后，当前素材池在以下几类已经连续补了不少：

- `trend / momentum`
- `XS reversal / momentum`
- `pairs / stat-arb / relative value`
- `funding / basis`

这时候再补一条“只服务单一形态”的小 alpha，边际价值未必比一个**能同时服务至少两类 raw alpha 的共享 regime layer**更高。

这篇 2026 arXiv 新文的价值就在这：

> 它不是给你一个新的逐根 entry signal，而是给你一个**公开可拿、可每天更新、且对传统宏观指标与 DVOL 仍有增量信息**的 crypto 波动率前视层。

所以它不该被伪装成 raw alpha；更诚实的定位是：

- **BTC 方向**：`Fed / recession repricing -> 下一周 BTC realized vol 变高`
- **Alt 方向**：`CPI repricing -> 下一周 ETH / SOL / ADA / LINK realized vol 变低`

对 short-cycle desk，这正适合被写成：

- shared regime gate
- shared sizing overlay
- breakout / continuation 的 allow-deny 层
- MR / stat-arb 的 vol-state 切换层

## 2. 先回答任务里最重要的那句：base alpha 是什么？

这篇东西的 **base alpha 说不成一条独立 raw alpha**。

更准确的说法是：

> **它预测的是未来 3~5 天的 realized volatility，而不是未来几根 K 线的方向。**

所以这篇 note 必须老实标成 `regime`，不能冒充 `raw alpha`。

但它依然值得进研究池，因为它满足了另外一档高优先级条件：

> **它能同时服务至少 2 类以上 raw alpha 的 shared gate / filter。**

具体服务对象非常明确：

1. **trend / breakout / continuation**：高波动周允许更大 target、更宽 stop，或只在高-vol regime 放行；低波动周则更容易被 chop 死。
2. **mean reversion / stat-arb / pairs**：高波动周更可能打穿静态 band，需要改小 size、放宽 entry band、或直接 veto。
3. **carry / funding**：波动骤升时先做 gross-down / leverage-down，避免让 carry 收益被 mark-to-market 吞掉。

## 3. 这次看了什么

- **Authors**: Hardhik Mohanty, Bhaskar Krishnamachari
- **Year**: 2026
- **Title**: *Do Prediction Markets Forecast Cryptocurrency Volatility? Evidence from Kalshi Macro Contracts*
- **Venue**: arXiv preprint
- **DOI**: `10.48550/arXiv.2604.01431`
- **Readable URL**: <https://arxiv.org/abs/2604.01431>
- **Full-text HTML**: <https://arxiv.org/html/2604.01431v1>
- **Repo URL**: 未见作者公开 repo

论文做的事很直接：

- 用 **Kalshi** 的宏观事件合约（Fed、CPI、衰退等）日度概率变化；
- 构造 volume-weighted 的概率重定价信号；
- 去预测 **BTC / ETH / SOL / ADA / AVAX / LINK** 的未来 `5-day realized volatility`；
- 再和 HAR benchmark、VIX、DXY、S&P500、Fed Funds、Treasury、Deribit DVOL 做比较。

最有 desk 价值的一句话可以翻成人话：

> **宏观赔率的“突然改口”，比很多传统宏观代理更早告诉你：接下来这几天 crypto 的波动状态要换档了。**

## 4. 论文里最硬的几条结论

### 4.1 BTC：Fed dovish repricing 能预测未来一周更高波动

文中最强的 BTC in-sample 结果是：

- `Fed-dovish signal -> BTC 5-day realized vol`
- `t = 3.63`
- `p < 0.001`
- 加入该信号后，Bitcoin 模型 adjusted `R^2` 从 **14.1%** 升到 **15.5%**

作者把该信号定义为：

- `-ΔKXFED_vw`
- 即 **降息预期上升 / 政策路径更鸽派** 时，信号更高

更直白地说：

> **Kalshi 上“市场突然更信 Fed 会软下来”这件事，往往对应 BTC 接下来一周更容易进入高波动状态。**

### 4.2 但 BTC 更稳的 OOS 通道，不是 Fed，而是 recession-risk

论文最值得 desk 注意的不是单看 t 值，而是 **OOS 谁更稳**。

BTC 上最稳的 out-of-sample 通道其实是：

- `KXRECSSNBER -> BTC vol`
- `MSFE ratio = 0.979`
- `Clark-West p = 0.020`

这说明：

> **对 BTC 来说，衰退风险这类慢变量，可能比“正在发生的降息押注”更适合作为持续 daily regime state。**

作者还明确说：Fed 通道有 **regime dependence**，收益主要集中在 `2024–2025` rate-cutting cycle，之后会反转或衰减。

这对我们 desk 很关键，因为它直接决定：

- `Fed gate` 更像 **eventful / cyclical gate**
- `Recession-risk gate` 更像 **persistent / background regime layer**

### 4.3 Alt：CPI repricing 对 ETH / SOL / ADA / LINK 指向的是“更低的后续波动”

论文发现另一条完全不同的资产-宏观映射：

- `KXCPI absolute repricing -> ETH / SOL / ADA / LINK future vol`
- t 统计范围约 **`-2.1` 到 `-3.4`**

其中 OOS 更硬的两条是：

- **ETH**：`MSFE = 0.959`, `p = 0.010`
- **SOL**：`MSFE = 0.983`, `p = 0.048`

注意方向是 **负的**。

也就是：

> **不是“CPI 赔率大变 -> alt 更乱”，而是“CPI 赔率剧烈重定价后，alt 接下来一周 realized vol 反而更低”。**

作者给的解释是：

- 大 CPI repricing 往往集中在数据发布前后；
- 市场对 inflation uncertainty 的重新定价完成后，接下来的一周更像 **uncertainty resolution**；
- 所以 ETH / SOL / ADA / LINK 会进入一个相对更安静的 realized-vol regime。

这很适合被拿来做：

- breakout veto
- trend sleeve size-down
- range / MR sleeve allow

### 4.4 这不是 Treasury / Fed Funds / DVOL 的翻版

这篇 paper 最值钱的一点，是作者做了很认真地“你是不是只是重复老指标”排查。

结果：

- **Fed 通道 first-stage `R^2 = 2.3%`**
- **CPI 通道 first-stage `R^2 = 7.5%`**

也就是大部分 Kalshi 日度变化，**并没有被** Fed Funds、Treasury、VIX、DXY、S&P500 这些常规指标解释掉。

更重要的是，和 DVOL 联合回归后：

- BTC 上 Kalshi `Fed-dovish` 仍有 `t = 3.46`, `p = 0.001`
- ETH 上 Kalshi `CPI` 仍有 `t = -2.08`, `p = 0.037`
- 对应的 DVOL 项反而 **不显著**

这说明它不只是“换个壳的传统 vol proxy”，而是**有独立信息增量**。

## 5. 为什么这东西对 `1m / 3m / 5m / 15m` 仍然有意义

乍一看，这篇是 **daily -> next 5 days vol forecast**，像是太慢。

但它对 short-cycle desk 依然有意义，因为它天然应该被摆在 **日级 regime layer**，而不是逐根信号层：

### 5.1 它不是用来决定这一根 K 线多空方向

它回答的不是：

- 下一根涨还是跌？
- 15 分钟后做多还是做空？

它回答的是：

- **未来几天这套市场更像高波动还是低波动？**
- **你该让哪一类 alpha 上桌，哪一类 alpha 缩手？**

这正是 short-cycle desk 很缺、但又常被拿很粗糙代理去替代的那层东西。

### 5.2 它最适合做“上层 slow state”

对我们来说，一个很自然的结构是：

- **底层**：`1m / 3m / 5m / 15m` raw alpha 产生触发
- **上层**：每日一次更新 `macro-vol state`
- **执行层**：按该 state 决定 allow / deny / half-size / full-size / stop width / target width

所以它更像：

```text
macro prediction market repricing
    -> daily vol-state
    -> short-cycle alpha routing / sizing / veto
```

而不是：

```text
Kalshi signal -> directly long / short next 15m bar
```

## 6. 我会怎么把论文翻译成 desk 版规则

这里给三条最实用、最诚实的 translation。

### 6.1 BTC：`Fed / recession high repricing = high-vol BTC state`

**服务对象**：
- BTC breakout / continuation
- BTC intraday trend
- BTC mean reversion

**daily gate 定义（第一版）**：
- `fed_dovish_z = zscore(-ΔKXFED_vw, lookback=60d)`
- `recession_z = zscore(|ΔKXRECSSNBER_vw|, lookback=60d)`
- `btc_highvol_state = (fed_dovish_z >= 1.5) or (recession_z >= 1.5)`

**routing 建议**：
- 对 breakout / continuation：`baseline` vs `highvol_only` vs `highvol_size_up(1.25x)`
- 对 mean reversion：`baseline` vs `highvol_halfsize` vs `highvol_veto`

先别预设高波动一定对 breakout 有利；要用同一 entry 规则直接测。

### 6.2 ETH / SOL / ADA / LINK：`CPI repricing spike = post-event low-vol alt state`

**服务对象**：
- alt breakout / momentum
- alt range / pullback / MR
- alt carry / funding sleeves

**daily gate 定义（第一版）**：
- `cpi_z = zscore(|ΔKXCPI_vw|, lookback=60d)`
- `alt_lowvol_state = cpi_z >= 1.5`

**routing 建议**：
- breakout / trend：`baseline` vs `lowvol_veto` vs `lowvol_halfsize`
- MR / stat-arb：`baseline` vs `lowvol_allow` vs `lowvol_size_up`
- carry：`lowvol_state` 允许更高 gross，`non-lowvol` 收缩 gross

这里的逻辑很简单：

> 论文已经告诉你，CPI repricing 大日子后，alt 下周 realized vol 更可能收下来；那就别再拿“趋势会继续发散”当前提。

### 6.3 不要先做连续加权，先做最笨的三档状态

第一轮最小实验别一上来就做 fancy nonlinear sizing。

直接三档就够：

- `off`
- `half-size`
- `full-size`

或者：

- `allow`
- `neutral`
- `veto`

因为这轮最重要的问题不是最优参数，而是：

> **这个 macro-vol state 到底有没有给我们的 raw alpha 带来稳定的条件分层。**

## 7. 数据源、公开性、更新频率、最小可复现实验口径

这轮主题主要依赖外部数据，所以这些信息必须写清楚。

### 7.1 数据源

- **Prediction market 数据**：Kalshi 公共 API / 公共合约行情
- **Crypto 价格 / 波动率代理**：论文用 CoinGecko 日收盘；desk 版最小实验可直接换成 Binance / Bybit / OKX 永续 K 线

### 7.2 公开性

- **Kalshi 数据**：公开可拉
- **Crypto K 线**：公开可拉
- 不依赖私有订单流、私有做市或闭源供应商终端

### 7.3 更新频率

- Kalshi 合约是连续交易，但 desk 第一版建议只取 **daily close / fixed daily snapshot**
- 论文锚点是 **4:00 PM ET** Kalshi 收盘状态
- short-cycle 实验里可把 `16:00 ET -> 次日 16:00 ET` 视作一个固定 regime day

### 7.4 最小可复现实验口径

#### 实验 A：BTC shared vol gate
- 底层 raw alpha：任选一条已经在池里的 BTC `5m / 15m` breakout 或 continuation
- 把每天 `16:00 ET` 更新一次的 `btc_highvol_state` 固定到下一交易日
- 对比：
  1. `baseline`
  2. `highvol_allow_only`
  3. `highvol_halfsize`
  4. `highvol_size_up`
- 观察：post-cost Sharpe / turnover / MDD / false-break ratio / tail loss

#### 实验 B：Alt low-vol veto
- 底层 raw alpha：ETH / SOL 的 `5m / 15m` breakout 或 top-N momentum
- 每天更新 `alt_lowvol_state`
- 对比：
  1. `baseline`
  2. `lowvol_veto`
  3. `lowvol_halfsize`
- 观察：净 alpha 是否主要死在“低 realized-vol 的假突破日”

#### 实验 C：MR / stat-arb 反向受益测试
- 底层 raw alpha：ETH/SOL 或多币 pairs / stat-arb sleeve
- 对比：
  1. `baseline`
  2. `lowvol_allow`
  3. `highvol_veto`
- 观察：band breach、stopout、回归完成率、单位 turnover 收益

## 8. 论文里最适合 desk 复用的，不是 Forecast Model 本身，而是“channel-specific state map”

很多 volatility paper 的问题是：

- 你知道它能 forecast vol，
- 但你不知道如何落到交易组件上。

这篇比较少见地把 **asset-channel mapping** 讲得很清楚：

- BTC ↔ Fed / recession
- ETH / SOL / ADA / LINK ↔ CPI

这很重要，因为它意味着：

> **你不该把所有宏观赔率信号统一压成一个“market risk-on/off”总开关。**

更合适的做法是：

- BTC 看 `Fed / recession`
- alt 看 `CPI`
- 不同资产用不同 macro-vol gate

这比“全市场统一一个 Fear & Greed 阈值”更细，也更接近这篇论文的原始证据。

## 9. 下一步怎么测

### Step 1：先做最小 A/B，而不是大一统宏观总分

优先顺序：

1. **BTC breakout / continuation × BTC high-vol gate**
2. **ETH / SOL breakout × alt low-vol gate**
3. **ETH / SOL MR / stat-arb × alt low-vol allow**

不要一上来把 `Fed + CPI + recession` 做成综合分。先测单一通道。

### Step 2：先固定 daily snapshot，再测 intraday decay

第一版直接把 gate 固定一整天。

若有效，再测：

- `T+0` 当天有效
- `T+1 ~ T+3` 递减
- `T+5` 失效

因为论文的主结果是 `3~5 day`，而不是无限持久。

### Step 3：把它从“研究层”拉进“风险层”

如果 A/B 显示它确实能压住：

- breakout 假信号
- MR 的 band 失效
- carry 的 tail hit

那就别只把它留在研究 notebook。下一步直接推进成：

- pre-trade state file
- 风险引擎日级 gross cap
- 各 alpha sleeve 的 routing tag

## 10. 主要风险

- **频率错配**：这是日级 slow state，不要硬装成 5m signal。
- **样本短**：`2023-01` 到 `2026-03`，且 Fed 通道明显有 regime dependence。
- **平台依赖**：论文只测 Kalshi；跨到 Polymarket / PredictIt 是否复现，还没证明。
- **交易方向未定**：它预测的是 vol，不是涨跌；必须附着在已有 raw alpha 上用。
- **实施细节风险**：论文用日收盘和 CoinGecko，desk 若改为 perp 高频实现，要避免时区和 snapshot 漂移。

## 11. 一句话结论

这篇 2026 arXiv 最值得 intake 的，不是把 Kalshi 宏观赔率当成新的逐根交易信号，而是把它老老实实降级成：

> **给 BTC / alt 不同 raw alpha sleeve 共用的 daily volatility regime gate。**

如果你只能先测一个最小实验，我会选：

> **`BTC 15m breakout/continuation × recession-risk high-vol gate`**，以及 **`ETH/SOL 15m breakout × CPI low-vol veto`**。

## 12. 来源

1. Mohanty, H., & Krishnamachari, B. (2026). *Do Prediction Markets Forecast Cryptocurrency Volatility? Evidence from Kalshi Macro Contracts*. arXiv. DOI: `10.48550/arXiv.2604.01431`  
   Readable URL: <https://arxiv.org/abs/2604.01431>
2. arXiv full-text HTML: <https://arxiv.org/html/2604.01431v1>
3. Kalshi（公开事件合约市场；论文数据源说明见正文第 2 节）: <https://kalshi.com>
4. 论文关键结果包括：BTC `Fed-dovish` in-sample `t=3.63`、`adj R^2 14.1% -> 15.5%`；BTC `recession risk` OOS `MSFE=0.979, p=0.020`；ETH `CPI` OOS `MSFE=0.959, p=0.010`；与传统宏观 / DVOL 联合后仍保留显著性。