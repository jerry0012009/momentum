# 别把 pairs admission 继续写成“相关性 + ADF”二件套：这份 2026 研究仓更该先测的是「round-trip density × regime-stable pair screening」这层 raw-alpha admission filter
- 时间：2026-04-15 08:44 UTC
- 类型：GitHub / repo source audit
- 主题类型：filter
- 基础 alpha：cointegration spread mean reversion（pairs / stat-arb / relative value）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / admission / regime-stability / round-trip / beta-smoothness / repo
- 证据类型：工程证据（repo 源码 + 筛选输出表）

## 1. 这次看了什么
先回答 base alpha：**这不是一个“新的 pair alpha 本体”，而是服务于 pairs raw alpha 的 admission 层——先用可计算的 round-trip 质量、beta 稳定度和跨 regime 一致性，把“看起来像协整、实际上不好做”的 pair 先筛掉。**

这轮主看的是 2026 GitHub repo `Epsilon-Fund/Epsilon-Quant-Research` 里 statistical-arbitrage 模块，而不是昨天已经写过的 momentum / breakout 部分：
- `topics/statistical-arbitrage/strategies/testing/Pairs_Screening.py`
- `topics/statistical-arbitrage/strategies/testing/pairs_screen_v5_top50.csv`
- `topics/statistical-arbitrage/strategies/testing/portfolio.py`

repo 元数据也还算新：
- 创建时间：`2026-02-18`
- 最近更新：`2026-04-14`
- 当前 statistical-arbitrage 目录是一个**pair 预筛 + pair 级 walk-forward 组合**的研究壳，不是只给相关性热图。

最有用的不是某个具体 pair，而是它把 pair admission 明确拆成 5 个可复用指标：
1. **Round-trip frequency + completion**：这对 pair 在历史上是否真的经常“开得出、收得回”
2. **Relative beta smoothness**：对冲比率是不是老在乱跳
3. **Window reversion speed**：不同滚动窗里 spread 半衰期是否够快
4. **Regime stability**：把样本切成 4 段后，是否大多数阶段都还能完成足够 round-trip
5. **ADF on best-reference spread**：不是不用 ADF，而是把 ADF 降成尾部加分，不再当 admission 的唯一核心

## 2. 核心结论
- **一句话核心结论：** 对 short-cycle desk 来说，这份 repo 最值得 intake 的不是“再做一次 cointegration 教程”，而是把 pairs admission 从“相关性/ADF 静态筛选”升级成“能不能稳定来回收敛”的交易质量筛选。
- **一句话证明方式：** 我直接读了 repo 的 `Pairs_Screening.py` 评分逻辑和 top50 输出表，发现它真正抬高优先级的不是相关性本身，而是 `RT frequency × RT completion × beta smoothness × fast half-life × regime stability` 的组合分数。

### 2.1 repo 实际怎么打分
`Pairs_Screening.py` 里写得很直白：
- 时间框架：`1d`
- 历史长度：`1500` bars
- 参考 lookback 扫描：`[100, 130, 155, 180, 210]`
- 开仓阈值：`|z| >= 1.5`
- 平仓阈值：`|z| <= 1.0`
- 最长持有：`10` bars
- regime 切成 `4` 段

但真正值钱的是它的**评分结构**，不是这些 daily 参数本身：
- `RT frequency + completion`：30 分
- `beta smoothness`：10 分
- `window reversion speed`：20 分
- `regime stability`：25 分
- `ADF`：5 分
- `data bonus`：5 分
- `kurtosis penalty`：最多扣 5 分

换句话说，这个 repo 在表达一件很 desk-friendly 的事：
**如果一个 pair 只是统计上“像协整”，但 trade quality 很差、beta 老漂、不同阶段不稳定，那它就不该进下一轮 walk-forward。**

### 2.2 这和已有 pairs digest 的差别在哪
我们索引里已经有很多 pairs / stat-arb 主线：
- percentile-entry
- dynamic hedge ratio
- pair breakdown veto
- ORF rebalance governor
- graph matching pair book
- OU / Hurst / GHE admission

这轮不重复的点在于：
**它不是再发明一条新 spread alpha，也不是继续卷 hedge ratio / stop / portfolio construction，而是把“pair 候选到底值不值得进回测”做成一套更交易导向的 admission score。**

尤其是下面这三个维度，当前索引里还没有被单独讲透：
1. **round-trip completion**：不是信号多就好，必须“开得出来也收得回去”
2. **relative beta smoothness**：beta 抖得太厉害，意味着 hedge 不稳，真实成交更容易漂成方向暴露
3. **regime stability**：哪怕全样本均值看着行，只要某 1~2 段完全不工作，live 很容易踩中坏阶段

### 2.3 top50 输出表已经给了几个直观提醒
`pairs_screen_v5_top50.csv` 的前几名不是传统“大币对大币”的直觉组合，而是一些更“能反复完成回归”的对：
- `SNXUSDT / FILUSDT`：总分 `66.8`，年化 round-trip 频率 `9.5`，completion `0.603`
- `APTUSDT / FILUSDT`：总分 `66.4`，年化 round-trip 频率 `6.9`，completion `0.568`
- `DOTUSDT / APTUSDT`：总分 `65.3`，年化 round-trip 频率 `10.1`，completion `0.66`

这些数字未必能直接照抄到 short-cycle，但它们已经说明 repo 的筛选逻辑不是“找最像的两条线”，而是“找最像**经常来回走完一趟**的 pair”。

## 3. 为什么和当前项目有关
这轮虽然不是新的 raw alpha 本体，但和当前 desk 非常直接相关：

1. **它服务的 base alpha 很清楚。**
   服务对象就是 pairs / stat-arb 的 `spread mean reversion`，不是泛化过滤器。

2. **它补的是当前最缺的一层：pair admission 质量控制。**
   现在 pairs 线已经不少，但很多主题还停留在“方法可做 / alpha 可讲”；真正进 live 前，最常见的问题反而是：
   - pair 入池太宽
   - 某些 pair 只在一小段样本有效
   - beta 不稳导致 hedge 漂移
   - 看起来 stationarity 很强，但 round-trip completion 很差

3. **它很适合 15m / 5m desk 化，而不要求抄 daily 参数。**
   需要迁移的是**筛选逻辑**，不是 `1d + 1500 bar + 10 day hold` 这些原始数值。

## 3.5 策略拆解（必填）
- 方向属性：pairs / relative-value / stat-arb
- 基础 alpha：cointegration spread mean reversion
- 这轮新增层：admission / candidate-ranking filter
- filter 核心：`round-trip density + completion + beta smoothness + fast half-life + regime stability`
- risk / sizing / execution overlay：这份 repo 只提供 pair 入池逻辑与部分组合可视化；short-cycle 的 sizing / stop / execution 仍需接到现有 pairs shell 上

## 4. 可复刻的最小实验
### 4.1 最值得先做哪一版
最值得先做的是：**把这套 pair screening 逻辑 desk 化到 `15m`，然后喂给我们已有的 pairs shell，当作 admission layer 对照实验。**

也就是说，不要先把它当 standalone 策略；先把它当：
- `pair 预筛器`
- `walk-forward 候选池排序器`
- `坏 pair 淘汰器`

### 4.2 15m 最小实验口径
- 市场：Binance USDⓈ-M Perpetual
- 频率：`15m`
- 宇宙：先做 15~25 个流动性最稳定的大中盘 perp
- formation window：先试 `45d / 60d / 90d`
- 参考 lookback grid：先试 `192 / 256 / 320 / 384 / 448` bars
- spread 生成：rolling OLS hedge ratio + z-score
- 开平规则（先沿用 repo 的第一版）：
  - 开仓：`|z| >= 1.5`
  - 平仓：`|z| <= 1.0`
  - 最长持有：`24` bars（6h）
- pair admission score：
  1. annualized RT frequency
  2. RT completion
  3. relative beta smoothness
  4. fast-half-life 占比
  5. 4-regime stability
  6. ADF 只做轻量加分

### 4.3 一定要做的对照组
至少跑三组：
1. **Naive pair selection**：相关性 + ADF
2. **Trade-quality selection**：本轮 `RT + beta smoothness + regime stability`
3. **Hybrid**：相关性/ADF 先粗筛，再用 trade-quality score 排名

真正想回答的问题是：
**在同一个 execution shell 下，trade-quality admission 能不能让 pair 池更稳定，而不是只让 in-sample 看起来更漂亮。**

### 4.4 先看哪些指标
先不要只看 Sharpe，优先看：
- post-cost `bps / trade`
- trade count
- median hold bars
- win rate
- pair survival rate（多少期之后还在池里）
- OOS pair turnover
- 坏阶段回撤是否明显收敛

### 4.5 下一步怎么测
- **第一步：** 用现有 15m pairs shell，先复写一版 `trade-quality admission score`。
- **第二步：** 同一套 entry/exit/cost，不换 execution，只换 pair admission，看 OOS 差异。
- **第三步：** 检查 `top-N` pair 池在滚动窗口里是否更稳定，尤其看 pair turnover 和 beta drift。
- **第四步：** 若 15m 有改善，再下钻到 `5m` 看 admission 是否仍有帮助；若 5m 只剩高 turnover 噪音，就把它停留在 15m selection layer，不硬降频。

## 5. 风险与保留意见
- **这不是完整策略。** 它是 admission 层，不是 entry/exit/sizing/risk/cost 全套。
- **repo 原始口径是 daily。** 迁到 15m 时，必须重调窗口，不能照搬 bar 数。
- **容易 overfit 在“筛选分数”上。** 如果 admission 分数本身被反复调参，也会变成另一种 data-mining。
- **top pairs 未必可交易。** CSV 里高分 pair 主要说明“历史上容易来回收敛”，不自动等于 perp 盘口深度、资金费率、借贷和滑点都能承受。

## 6. 来源
- **Authors / Year / Title / Venue / DOI / Readable URL / Repo URL**
- Epsilon Fund contributors. (2026). *Epsilon-Quant-Research* — statistical-arbitrage module. Venue: GitHub repository. DOI: N/A.  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/tree/main/topics/statistical-arbitrage`  
  Repo URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research`
- Epsilon Fund contributors. (2026). *Pairs_Screening.py*. Venue: GitHub source file. DOI: N/A.  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/statistical-arbitrage/strategies/testing/Pairs_Screening.py`  
  Repo URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research`
- Epsilon Fund contributors. (2026). *pairs_screen_v5_top50.csv*. Venue: GitHub data artifact. DOI: N/A.  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/statistical-arbitrage/strategies/testing/pairs_screen_v5_top50.csv`  
  Repo URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research`
- Epsilon Fund contributors. (2026). *portfolio.py*. Venue: GitHub source file. DOI: N/A.  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/statistical-arbitrage/strategies/testing/portfolio.py`  
  Repo URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research`

## 7. 本地产物
- Digest：`research/quant_digests/2026-04-15_0844_roundtrip-regimestable-pairs-admission.md`
