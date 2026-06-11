# 别把这篇 2024 Springer major-pair 统计套利论文只读成“相关性教学案例”：对 short-cycle desk，更该先测的是「short-half-life major-pair z-score fade」这条 raw alpha

- 时间：2026-04-12 19:35 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/major-pairs/high-correlation/cointegration/halflife/zscore/dydx/binance-perpetual/5m/15m/paper/repo/public-data/cost/risk
- 证据类型：2024 Springer chapter abstract/metadata + 2023 GitHub repo source audit（dYdX pairs bot）+ Binance USDⓈ-M `5m/15m` public-data portability probe

- 主题类型：raw alpha
- 基础 alpha：先在高相关、可协整的 major pair 里找**回得够快**的两腿，用 rolling hedge ratio 把相对价值对齐；当 spread z-score 偏离到阈值外时做 `long cheap leg / short rich leg`，等 spread 回到中枢或穿回零轴再平，而不是押单币方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这轮我没有继续补“又一个泛泛的 pairs 综述”，而是挑了一篇索引里还没单独写过、但对 desk 很实用的材料：

### 主材料（论文）
- **Maxwell Dann, Ilias Kotsireas (2024)**
- **Title**：*Profiting Off the High Correlation of Cryptocurrency Pairs Using Statistical Arbitrage*
- **Venue**：*Mathematical Research for Blockchain Economy, MARBLE 2024 / Springer chapter*
- **DOI**：<https://doi.org/10.1007/978-3-031-68974-1_16>
- **Readable URL**：<https://link.springer.com/chapter/10.1007/978-3-031-68974-1_16>
- **Repo URL**：N/A

### 执行骨架（repo）
- **pakhuong (2023)**
- **Title**：*dydx-pair-trading-bot*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL / Repo URL**：<https://github.com/pakhuong/dydx-pair-trading-bot>
- **关键文件**：
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/program/func_cointegration.py>
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/program/func_entry_pairs.py>
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/program/func_exit_pairs.py>
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/program/func_public.py>
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/program/main.py>
  - <https://raw.githubusercontent.com/pakhuong/dydx-pair-trading-bot/main/cron.txt>

这轮最值得 intake 的，不是“major coins 之间相关性很高”这句废话，而是下面这句更像 desk 语言的话：

> **在 major pair 里，先别只看谁最相关，而要先看谁的 spread 回得够快。短周期 pairs 的 admission，相关性只是入场券，half-life 才更像优先级排序器。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
说人话：

> **两条走势长期绑得比较紧的 major coin，短时间出现异常相对偏离后，会往中间收。**

所以这题的 **base alpha** 很清楚，就是：
- `pairs / relative-value mean reversion`
- 不是 filter
- 不是 regime
- 也不是纯 execution overlay

更具体一点：
1. 先找历史上价格关系足够稳定的 pair；
2. 用 rolling beta / hedge ratio 把两腿缩放到可比口径；
3. 观察 `spread = leg1 - beta * leg2`；
4. 当 spread 的 z-score 偏离太大，就做 `long cheap / short rich`；
5. 等 spread 回归，再平仓。

## 3. 为什么这轮值得写
### 3.1 它补的是“major-pair short-half-life baseline”，不是又一个空泛 pairs 标题
现在素材池里 pairs 已经不少，但很多都在讲：
- 怎么挑 pair
- 怎么加更复杂 admission
- 怎么叠更多统计检验

这篇 Springer chapter 加上公开 dYdX repo，刚好补了一个更务实的问题：

> **如果我们只想先补一条可复现、可直接落到 `5m/15m` 的 pairs raw alpha，major pair 里应该先挑“最像”的，还是先挑“回得快”的？**

我的结论是：
- **相关性高，不等于短周期最好做；**
- 对 short-cycle desk，更该先排 `half-life`；
- `major-pair + rolling beta + z-score fade` 仍然是很值得保留的一条最小 baseline。

### 3.2 它是少数“论文口径 + 可执行 repo 壳”能拼起来的题
单看 2024 chapter，本身偏结果展示；
单看 dYdX repo，又容易被读成“教科书协整机器人”。

但两者拼起来就变成一条很完整的研究路径：
- 论文告诉你：major-pair stat-arb 这条路不是凭空想象；
- repo 告诉你：怎么把它写成一个可 daily 扫描 + 5 分钟轮询的完整策略壳；
- 我这次再补一层 Binance `5m/15m` portability probe，回答它跟当前 desk 的时间尺度有没有关系。

## 4. 主材料到底给了什么硬信息
### 4.1 2024 Springer chapter 给的是“major pair 能做”的直观证据
Springer 页面公开摘要里写得比较直白：
- 研究对象是 **Bitcoin / Ethereum / Litecoin / Bitcoin Cash**；
- backtest 样本超过 **81,000 data points**；
- backtest 报告 **100% win rate**；
- live trading implementation 的 win rate 约 **79% ~ 100%**；
- live bot 相对 benchmark 的 excess return 区间约 **`-0.4% ~ 8.1%`**。

我不建议把这些数字当成可以照单全收的 live KPI，因为：
- 100% win rate 一听就该先怀疑是否有样本选择 / 交易摩擦 / 出场定义偏乐观；
- 但它至少说明，这篇材料不是只停在“相关性很高所以也许能做”，而是真的把它实现成了 bot 口径。

### 4.2 dYdX repo 给的是完整策略壳，不只是协整口号
`pakhuong/dydx-pair-trading-bot` 的价值，在于它把这条 alpha 写成了比较完整的流程：

#### pair admission
`func_cointegration.py` 里先做：
- Engle-Granger 风格的 cointegration test；
- 对 spread 做 ADF stationarity 检查；
- 只保留 `half_life > 0 且 <= 24 bars` 的 pair；
- 再把合格 pair 存成 `cointegrated_pairs.csv`。

#### signal shell
同一个文件里：
- 用 **RollingOLS window = 168** 算动态 hedge ratio；
- spread z-score 用 **rolling window = 72**；
- `func_entry_pairs.py` 里只有当 `|z| >= ZSCORE_THRESH` 才开仓；
- 开仓方向就是标准的：`z > 0` 就 short base / long quote，`z < 0` 反过来。

#### exit shell
`func_exit_pairs.py` 里 exit 逻辑是：
- 支持 `CLOSE_AT_ZSCORE_CROSS`；
- 也就是 spread 回穿中枢时平仓；
- 同时会检查 live position / order record 一致性，避免双腿不同步失控。

#### deployment cadence
`cron.txt` 甚至把调度节奏都写了：
- **每日一次**重新扫描 pair；
- **每 5 分钟**跑一次 entry / exit 管理。

翻成人话就是：

> 这不是“pairs 可以做”的 PPT，而是一套真的能被拿来复刻的完整 skeleton。

## 5. 这轮最关键的 desk 结论：别默认 BTC/ETH 最适合短周期
为了避免只抄论文 headline，我又用 Binance USDⓈ-M 公共 `klines` 做了一次最小 portability probe：
- universe：`BTCUSDT / ETHUSDT / LTCUSDT / BCHUSDT`
- 频率：`5m`、`15m`
- 方法：
  - rolling beta window = `168`
  - spread z-score window = `72`
  - 观察 `|z| >= 2` 事件后，未来固定窗口内 `|z|` 是否收缩

### 5.1 5m 结果：`BTC/BCH` 比 `BTC/ETH` 更像 short-half-life 候选
我这次快检里，最值得记住的不是“BTC/ETH 相关性最高”，而是：

- **`BTC/ETH` 5m return corr ≈ `0.904`**
- 但它的粗 half-life 约 **`82.9` bars**，偏慢

对比之下：
- **`BTC/BCH` 5m return corr ≈ `0.658`**
- 但它的粗 half-life 约 **`19.8` bars**
- 在最近 `1000` 根 `5m` bar 里，出现了约 **`86` 次 `|z| >= 2`** 的偏离事件
- 这些事件后，未来 **`24` 根 `5m` bar`（约 2 小时）`** 的 `|z|` 平均收缩约 **`1.40` 个 z-score 单位**

这句很重要：

> **最高相关性的 pair，不一定是最该先进 short-cycle 研究池的 pair；回归速度更快的 pair，往往更像短周期真钱候选。**

### 5.2 15m 结果：同一对 `BTC/BCH` 仍然在回，但明显更慢
同样口径下，`BTC/BCH` 在 `15m` 上：
- 粗 half-life 约 **`36.2` bars`（约 9 小时）`**
- 最近 `1000` 根 `15m` bar 里约 **`97` 次 `|z| >= 2`** 事件
- 未来 **`8` 根 `15m` bar`（同样约 2 小时）`** 的 `|z|` 平均收缩约 **`0.96`**

这说明什么？
- `15m` 并不是没 edge；
- 但对这类 major-pair spread fade，**`5m` 更像 alpha 本体层，`15m` 更像低换手控制组**。

## 6. desk 应该怎么读这题，而不是被“高相关”三个字带偏
### 6.1 相关性只是白名单，不是优先级
如果只用相关性排：
- BTC/ETH 很可能永远排第一；
- 但 short-cycle desk 真正关心的是：**偏离出现后多久能回、回的时候够不够干净、能不能覆盖双腿成本。**

所以更合理的 desk admission 是：
1. 先用相关性 / 协整做白名单；
2. 再按 `half-life`、`|z|` 收缩速度、事件频率排序；
3. 再用 taker/maker 成本去筛掉“会回但不够赚钱”的 pair。

### 6.2 这题最适合服务的就是 `5m first, 15m control`
对当前 desk，我会这样落：
- **`5m`**：主实验层，负责验证 alpha 本体；
- **`15m`**：控制组，负责看降频能不能降低 churn；
- **`1m/3m`**：只在 execution 足够强时再往下压，不要第一枪就去 1m。

### 6.3 这题和最近一堆“复杂 pairs 组件”相比，真正值钱的是它够诚实
我反而觉得这题的价值在于它不花哨：
- 没先上 DNN
- 没先上复杂 basket
- 没先做一堆 fancy regime labels

它先回答的是最基础的问题：

> **major pair spread 本身会不会回？如果会，先用最简单的 rolling beta + z-score 能不能抓到？**

这正是 raw alpha 素材池该优先补的东西。

## 7. 可直接落地的最小实验
### 7.1 最小定义
先不要一上来就扫全市场，先做最简单、最诚实的一版：

#### universe
- majors：`BTC / ETH / BCH / LTC`
- venue：先用 Binance USDⓈ-M 或 spot 公共数据

#### pair admission
- formation 窗口：最近 `7~14` 天 `5m` bars
- 白名单：
  - return corr > 某阈值（例如 `0.6~0.8`）
  - cointegration/ADF 通过
  - half-life 落在可交易区间（例如 `6~30` bars）

#### signal
- rolling beta：`168 bars`
- spread z-score：`72 bars`
- entry：先测 `|z| >= 2.0`
- tp：`|z| < 0.5` 或 `z` 穿零
- sl：`|z| > 3.5`
- time stop：`2~3 × half-life`

#### sizing
- beta-neutral / dollar-neutral 二选一做对照
- 每对固定风险预算，不要多对叠太满
- 同资产重叠 pair 不同时开太多，防止隐性净曝险

#### cost
- 先做 taker-taker 诚实版
- 再做 maker entry / taker exit 对照版
- 费用、滑点、funding 都要双腿一起算

### 7.2 最该先看什么指标
不是先看 Sharpe，而是先看：
1. **post-cost expectancy / trade**
2. **median holding time vs half-life**
3. **事件频率 × 换手**
4. **双腿成交不同步损失**
5. **pair overlap 导致的隐性集中风险**

## 8. 风险与保留意见
- **论文摘要里的 100% backtest win rate 太漂亮了，默认不能直接信。** 这更像提醒我们：一定要自己按公开数据和真实成本重跑。
- **major pairs 不等于天然低风险。** 当市场进入单边趋势、叙事切换或流动性断层时，spread 可以长时间不回。
- **BCH/LTC 这类腿的流动性和事件风险**，通常比 BTC/ETH 更脏；这也是为什么 `half-life` 更短不代表一定净收益更高。
- **perp 上的 funding / borrow / taker cost** 会把很多看起来干净的 z-score 回归吃掉，所以这题必须先过 post-cost，而不是先看 gross。

## 9. 下一步怎么测
1. 先固定 major universe：`BTC/ETH/BCH/LTC`
2. `5m` 做 pair admission：corr + coint + half-life 排序
3. 只保留 **half-life 最短的前 1~2 对**，别一开始就铺满
4. 跑四组对照：
   - A：`BTC/ETH`
   - B：`BTC/BCH`
   - C：beta-neutral
   - D：dollar-neutral
5. 对每组分别测：
   - `entry = 2.0 / 2.5`
   - `tp = 0.5 / zero-cross`
   - `time stop = 2x / 3x half-life`
6. 先看 **5m taker-taker** 能不能过线；若不过，再看 maker entry 是否能救活
7. 若 `BTC/BCH` 的 gross 虽好但 net 不稳，再下一个动作不是换更复杂模型，而是：
   - 降频到 `15m`
   - 或只在波动 / 成交 / spread 条件较好的窗口开仓

## 10. 参考资料
1. **Dann, M., & Kotsireas, I. (2024). _Profiting Off the High Correlation of Cryptocurrency Pairs Using Statistical Arbitrage_.**  
   In *Mathematical Research for Blockchain Economy (MARBLE 2024)*. Springer, Cham.  
   DOI：<https://doi.org/10.1007/978-3-031-68974-1_16>  
   Readable URL：<https://link.springer.com/chapter/10.1007/978-3-031-68974-1_16>  
   Repo URL：N/A

2. **pakhuong. (2023). _dydx-pair-trading-bot_. GitHub repository.**  
   Readable URL：<https://github.com/pakhuong/dydx-pair-trading-bot>  
   Repo URL：<https://github.com/pakhuong/dydx-pair-trading-bot>

3. **Leung, T., & Nguyen, H. (2019). _Constructing cointegrated cryptocurrency portfolios for statistical arbitrage_.**  
   *Studies in Economics and Finance*, 36(4), 581–599.  
   DOI：<https://doi.org/10.1108/SEF-08-2018-0264>  
   Readable URL：<https://doi.org/10.1108/SEF-08-2018-0264>  
   Repo URL：N/A
