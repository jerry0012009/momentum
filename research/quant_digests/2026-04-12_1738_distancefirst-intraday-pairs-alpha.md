# 别把这篇 2024 *Investment Analysts Journal* intraday pairs 论文只读成“又一篇 cointegration 比较”：对 short-cycle desk，更该先补的是「distance-first pair admission × spread z-score fade」这条 raw alpha

- 时间：2026-04-12 17:38 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/distance-method/pair-selection/method-benchmark/cointegration/hurst/binance/1m/3m/5m/15m/paper/abstract-metadata/cost/risk
- 证据类型：2024 *Investment Analysts Journal* 论文摘要/元数据（OpenAlex + Crossref）+ 2020 *IEEE Access* intraday grounding（OpenAlex + Crossref）

- 主题类型：raw alpha
- 基础 alpha：先用 **distance method** 在高流动性币对里挑出“走势最像”的 pair，再在交易窗里做 **spread / relative-price deviation 的均值回归**；也就是 `long cheap leg / short rich leg`，吃价差收敛，而不是押单币方向
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这轮不是再补一个花哨的 pairs admission 模块，而是回到一个更朴素、但对 desk 更重要的问题：

**在 crypto intraday pairs 里，是否真的需要先上更复杂的统计筛选，还是简单的 `distance-first` 就已经是最该先测的 base alpha？**

我最终选的是一篇目前索引里还没正面写过的论文：
- **Po-Chang Ko, Ping-Chen Lin, Hoang-Thu Do, Yuan-Heng Kuo, Linh My Mai, You-Fu Huang (2024)**
- *Pairs trading in cryptocurrency markets: A comparative study of statistical methods*
- *Investment Analysts Journal*
- DOI：`10.1080/10293523.2023.2268386`

它最值钱的地方，不是再说一遍“pairs 可能有效”，而是直接比较了 **六种 pair selection 方法** 在 Binance intraday crypto 里的表现：
- Cointegration
- Correlation
- Distance
- Fluctuation Behaviour
- Hurst Exponent
- Stochastic Differential Residual

对 short-cycle desk 来说，这类材料的价值非常直接：**它回答的是“先拿哪种最小 raw alpha 骨架做 baseline”**，而不是“能不能再往 admission 上加一层复杂度”。

## 2. 先回答一句：这篇东西的 base alpha 是什么？
先把这个问题说死：

这篇东西的 **base alpha** 不是：
- cointegration 检验本身
- Hurst / fluctuation behaviour 这类筛选指标本身
- pair ranking 模块本身

真正的 alpha 本体是：

> **找出历史走势足够相似的两条币价路径；当它们在交易窗里出现异常偏离时，做 long cheap / short rich，等 spread 回归再平。**

也就是最标准、最可落地的 **pairs / relative-value mean reversion raw alpha**。

所以这轮主题应被归类为：
- `raw alpha`
- 不是 `filter`
- 不是 `regime`
- 也不是 `overlay`

## 3. 为什么这轮值得写，而不是继续找别的 headline alpha
### 3.1 它补的是“pairs 家族里的最小可复现 baseline”
当前 digest 池里已经有很多：
- cointegration pairs
- stacked z-score pairs
- RL sizing shell
- IC-ranked basket
- pair admission / threshold governance

但仍然缺一条很关键的底层判断：

> **在 crypto 短周期里，pairs 的最小 baseline，到底该默认从 `cointegration-first` 还是 `distance-first` 开始？**

这篇 2024 论文给的，就是这个层面的证据。

### 3.2 它和我们 desk 的时间尺度直接对齐
OpenAlex 摘要里写得非常清楚：论文用的是 **Binance 30 个币的 intraday 数据**，频率直接做到：
- `1m`
- `5m`
- `60m`

这比很多只停在日线或 4h 的 pairs 文献更贴 short-cycle desk。

### 3.3 它天然适合做“5m 先验 + 15m 控制组”
对 desk 而言，pairs raw alpha 最怕两件事：
- 过度依赖慢频 formation 逻辑，落不到 intraday execution
- 一上短周期就被 turnover / taker cost 吃掉

这篇材料刚好允许我们做一套最小而诚实的拆分：
- `5m`：看 alpha 本体是否最强
- `15m`：看 downsample 后能不能用更低 churn 保住净值
- `1m/3m`：只在 execution 足够好时再往下压

## 4. 来源信息
### 4.1 主论文
- **Authors**：Po-Chang Ko, Ping-Chen Lin, Hoang-Thu Do, Yuan-Heng Kuo, Linh My Mai, You-Fu Huang
- **Year**：2024（Crossref print date `2024-04-02`）
- **Title**：*Pairs trading in cryptocurrency markets: A comparative study of statistical methods*
- **Venue**：*Investment Analysts Journal*
- **DOI**：<https://doi.org/10.1080/10293523.2023.2268386>
- **Readable URL**：<https://www.tandfonline.com/doi/full/10.1080/10293523.2023.2268386>
- **Repo URL**：N/A

### 4.2 辅助 grounding 论文
- **Authors**：Miroslav Fil, Ladislav Kristoufek
- **Year**：2020
- **Title**：*Pairs Trading in Cryptocurrency Markets*
- **Venue**：*IEEE Access*
- **DOI**：<https://doi.org/10.1109/ACCESS.2020.3024619>
- **Readable URL**：<https://doi.org/10.1109/ACCESS.2020.3024619>
- **Open-access PDF URL（OpenAlex 记录）**：<https://ieeexplore.ieee.org/ielx7/6287639/8948470/09200323.pdf>
- **Repo URL**：N/A

## 5. 两篇论文到底给了什么硬证据
### 5.1 2024 IAJ：六种方法直接打擂台，distance 在 1m / 5m / 60m 都没掉队，反而最好
根据 OpenAlex 摘要，这篇 2024 论文：
- 使用 **2022-01-01 到 2022-03-31** 的三个月 Binance intraday 数据
- 样本为 **30 个 cryptocurrencies**
- 直接比较六种 statistical pair selection 方法
- 用 **11 个指标** 评价交易结果（不只看收益，也看风险和交易特征）

摘要里最关键的一句是：

> **Distance performs well at all three frequencies of 1 minute, 5 minutes, and 60 minutes, with a total return of 208.12%, 236.31%, and 210.36%, respectively.**

也就是说，这篇 paper 给出的主结论不是“cointegration 永远最强”，反而更接近：

- **最简单的 distance method，在 intraday crypto pairs 里已经很强**；
- 而且不仅 `5m`，连 `1m` 和 `60m` 也都表现不错；
- 这说明对 crypto 这类高噪声市场，**先验上不必默认“更复杂的统计方法一定更优”**。

### 5.2 2020 IEEE Access：crypto 的 pairs edge 更像 intraday，而不是 daily
2020 那篇 open-access grounding paper 的 OpenAlex 摘要同样很关键。它研究的是：
- **26 个 liquid cryptocurrencies**
- Binance
- 三个频率：`5m`、`1h`、`daily`
- 对比 distance 和 cointegration 方法

它给出的几条信息，和 2024 那篇拼起来非常完整：
1. **高频明显优于日频**
   - 摘要直接写到：最常见的 daily distance method 月收益只有 **`-0.07%`**
   - 但同样框架到了 `5m`，月收益可以到 **`11.61%`**
2. **结果对参数、成本和 execution windows 很敏感**
   - 也就是说：alpha 不是“白给的”，而是高度依赖执行壳
3. **daily 数据里看不到的均值回复，在 intraday 里更明显**
   - 这点对我们特别重要，因为 desk 的落点本来就不是日线

翻成人话：

> 如果你想在 crypto 做 pairs，先别把它写成一个慢频协整研究题。更合理的入口，是把它当成 **intraday relative-value mean reversion**。

## 6. desk 该怎么读这两篇，而不是照抄 headline
### 6.1 这不是“distance 永远正确”，而是“distance 应该先当 baseline”
我不建议把 2024 那篇读成：
- cointegration 无用
- 复杂方法没价值
- distance 一定 live 最强

更合理的 desk 读法是：

- **distance-first** 应该是第一条 baseline；
- 只有当它在相同 universe / 相同 cost 假设下明显不够用时，才值得继续往更复杂 admission 推；
- 否则很容易出现一种典型坏习惯：
  - 先上复杂 pair selection
  - 再把所有失败都归咎于 execution
  - 却没回答过“最简单的 raw alpha 到底有没有 edge”

### 6.2 这两篇合起来，支持“5m first, 15m control, 1m execution-only extension”
如果只看 short-cycle desk 的 transfer 优先级，我会这样排：

1. **`5m` first lane**
   - 两篇论文里最一致、最可信的交集就在这里
   - 既足够快，又没有 `1m` 那么容易被撮合微结构噪声吞掉

2. **`15m` control lane**
   - 论文没有直接给 `15m`，但它是 desk 很自然的“更低 churn 控制组”
   - 如果 `5m` gross 还行但 net 不行，`15m` 往往是第一个该试的降频版本

3. **`1m/3m` only after execution passes**
   - 2024 paper 虽然给了 `1m` 的好看回报，但这种结果最容易被真实执行折损
   - 所以 `1m` 不该是“第一落点”，而该是**已确认 alpha 本体存在后，用更强执行去放大**

### 6.3 对 desk 来说，pair selection 和 execution shell 必须拆开看
这两篇 paper 一起给出的最实用提醒其实是：

- **pair selection** 决定有没有“会回”的东西
- **execution shell** 决定你能不能把“会回”变成真钱

所以本轮 intake 最合理的写法，不是“distance 方法已经可上线”，而是：

> **distance-first pairs raw alpha 值得先进入素材池；但 live 价值取决于 threshold、持有时长、成本假设、以及是不是 maker-first。**

## 7. 和当前 `1m / 3m / 5m / 15m` 的关系
### 7.1 `5m`：最自然的第一实验层
如果现在就要做最小实验，我会让 `5m` 当第一落点，因为：
- 2020 paper 明确支持 `5m > daily`
- 2024 paper 在 `5m` 也给出很强结果
- 相比 `1m`，`5m` 更适合先验证 alpha 本体，不会把全部问题都变成 execution 问题

### 7.2 `15m`：更像成本过滤后的控制组
`15m` 的角色不是替代 `5m`，而是回答一个更现实的问题：

> 如果 `5m` 的 gross edge 真实存在，但净值过不了线，降到 `15m` 后能不能用更低 turnover 换回一部分可交易性？

也就是：
- `5m` 更像 alpha discovery
- `15m` 更像 cost-control / transfer sanity check

### 7.3 `3m`：在 5m 有效后做过渡层
如果 `5m` 成立，而 `1m` 太脏，那么 `3m` 是很自然的中间层：
- 比 `5m` 更快
- 比 `1m` 更不容易完全被微结构噪声主导
- 很适合拿来做同一套 pair book 的 execution refinement

### 7.4 `1m`：除非 maker / queue / staleness 已经有壳，否则不要先把 headline 当真钱
2024 paper 的 `1m` 结果非常吸引眼球，但 desk 化时一定要先问：
- 是否有足够小的真实 spread？
- 是否允许 maker-first？
- 是否有 symbol staleness / depth / queue risk 控制？
- 是否能接受 pair book 在极端时刻两腿不同步？

在这些问题没回答前，`1m` 更像**第二阶段 execution 放大器**，不是第一阶段 baseline。

## 8. 这轮 intake 后，最小可复现实验应该怎么做
### 8.1 最小实验定义
先别急着扫太多 fancy 方法，第一轮只做一个最小但诚实的 baseline：

- **市场**：Binance USDⓈ-M perpetual
- **频率**：`5m` 为主，`15m` 为对照
- **universe**：主流 liquid majors / large alts（先 8~12 个）
- **formation window**：`10d / 20d` 两档
- **pair selection**：
  - baseline A：distance
  - control B：cointegration
- **trade rule**：
  - 选 top `K=3~5` 个最接近 pair
  - spread z-score `>|1.5| / |2.0| / |2.5|` 入场
  - `|z|<=0.25` 离场
  - `|z|>=3.5` 止损
  - `24h / 48h` timeout 强平
- **成本层**：pair round-trip `8 / 12 / 16 / 20 bps`

### 8.2 先回答哪几个问题
第一轮不是要把 pairs 做到完美，而是先回答 4 个问题：
1. **distance 是否确实比 cointegration 更适合 intraday perp baseline？**
2. **5m 的 gross edge 降到 15m 后，net 有没有更稳？**
3. **pair 数量变少（只做 top 3）能不能显著压 turnover？**
4. **真正杀掉它的是选对问题，还是 execution / cost？**

### 8.3 结果判读标准
我会用下面这套标准，而不是只看 headline return：
- gross / net Sharpe
- pair-level half-life 分布
- 平均持有时长
- 每天换手
- 单 pair PnL 集中度
- 一腿先成交 / 两腿不同步时的最差回撤代理

## 9. 我对这条线的 desk 结论
### 9.1 结论一句话
这轮值得 intake 的不是“pairs 很酷”，而是：

> **在 crypto intraday pairs 里，simple distance-first 很可能比直觉里更该被当成 baseline；复杂 selection 方法应该是第二步，不是第一步。**

### 9.2 四字段结论重述
- **主题类型**：raw alpha
- **基础 alpha**：distance-first pair selection 后的 spread mean reversion（long cheap / short rich）
- **是否可独立复现**：是
- **是否可直接落地完整策略（entry/exit/sizing/risk/cost）**：是

### 9.3 当前最诚实的状态判断
这条线当前适合被写成：
- **raw alpha baseline 候选**
- **可直接进入 pairs 素材池**
- **优先级高于继续堆更复杂 admission 模块**

但还不该被写成：
- 已完成 live transfer
- 已证明 1m taker 可做
- 已解决两腿执行不同步问题

## 10. 下一步怎么测
下一步就做一个很小、但能给出明确 yes/no 的实验：

1. 先在 Binance USDⓈ-M `5m` 跑 **distance vs cointegration** 的同 universe 对照；
2. 只做 top `3~5` 个 pair，避免把 turnover 人为做爆；
3. 成本至少扫 `12 / 16 / 20 bps pair round-trip`，不要偷乐观；
4. 如果 `5m` gross 有 edge 但 net 不行，立刻降到 `15m` 看是不是单纯 churn 问题；
5. 只有在 `5m/15m` 先过线后，才值得把执行压到 `3m/1m` 做 maker-first refinement。

## 11. 来源链接
- 2024 paper DOI：<https://doi.org/10.1080/10293523.2023.2268386>
- 2024 paper readable：<https://www.tandfonline.com/doi/full/10.1080/10293523.2023.2268386>
- 2024 paper OpenAlex：<https://openalex.org/works?search=Pairs%20trading%20in%20cryptocurrency%20markets%3A%20A%20comparative%20study%20of%20statistical%20methods>
- 2020 paper DOI：<https://doi.org/10.1109/ACCESS.2020.3024619>
- 2020 paper readable：<https://doi.org/10.1109/ACCESS.2020.3024619>
- 2020 paper OpenAlex：<https://openalex.org/works?search=Pairs%20Trading%20in%20Cryptocurrency%20Markets>
