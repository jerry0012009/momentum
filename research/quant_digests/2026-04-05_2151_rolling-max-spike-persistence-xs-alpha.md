# 别把大阳线只读成“该反转了”：这篇 2021 *Financial Innovation* 更该先测的是「rolling-MAX recent-spike persistence」这条 cross-sectional raw alpha

- 时间：2026-04-05 21:51 UTC
- 类型：2021 *Financial Innovation* 开放获取全文（Springer article HTML + PDF）+ Crossref / OpenAlex 元数据
- 主题类型：raw alpha
- 基础 alpha：**横截面里，过去一个滚动窗口内打出“最大单次正收益”更极端的币，后续一段时间继续跑赢；也就是 recent-spike persistence / MAX effect，而不是默认短期 spike-reversal。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/max-effect/lottery/extreme-positive-return/recent-spike/persistence/rolling-max/top-bottom/liquidity/volatility/skewness/sentiment/binance-perpetual/15m/5m/3m/1m/paper/open-access/public-data/cost/risk
- 证据类型：开放获取全文给出样本、变量定义、分组回测、Fama-MacBeth 回归、控制变量与稳健性；足够改写成最小可复现实验

## 1. 先回答一句：这篇东西的 base alpha 是什么？

**base alpha = `recent extreme-upmove intensity` 的横截面 continuation。**

翻成人话：
- 不是看“过去 2~4 周总涨幅谁最高”；
- 而是看“谁在最近窗口里打出过最夸张的单次正收益 / spike”；
- 论文发现，在 crypto 横截面里，**高 MAX 币后面不是更容易回吐，反而更容易继续强**。

所以它不是一个 filter，也不是纯解释性行为金融故事；它本身就是一条可以独立落地的 **cross-sectional raw alpha**。

## 2. 这次看了什么

主看的是：

**Ozdamar, Melisa; Akdeniz, Levent; Sensoy, Ahmet (2021). _Lottery-like preferences and the MAX effect in the cryptocurrency market_. Financial Innovation.**

这篇最值钱的点，不是“散户爱彩票型资产”这种大词，而是它把一个可直接交易化的信号说清楚了：

> 在 crypto 里，`lagged extreme positive return` 不是坏事，反而能预测下一段相对收益。

而且它不是只做一个松散相关性展示，是真正给了：
- 样本口径
- MAX 变量定义
- 组合排序方法
- 风险调整 alpha
- 对 momentum / reversal / liquidity / volatility / skewness / sentiment 的控制

这就很适合拿来给当前 desk 补一条 **不依赖固定 breakout 形态、也不依赖 pairs/carry** 的 XS raw alpha。

## 3. 为什么这轮值得进研究池

先问一句：**它为什么比继续补一个 shared gate 更值得？**

因为这轮 desk 当前更缺的是 **可独立复现的 raw alpha 素材**，而不是再补一层“看起来有帮助”的过滤器。

这篇 paper 值得进池，原因有三条：

1. **信号本体清楚。**
   不是“市场热度高/低”，而是可计算的 `rolling MAX`。
2. **与已有 XS 动量素材不重复。**
   它抓的不是累计收益强弱，而是“极端单次正收益”的强度；更像 `spike-intensity rank`，和普通 24h/7d relative-strength 不是一回事。
3. **对 short-cycle desk 有天然改写空间。**
   日频论文里的 `past-month MAX -> next-week return`，可以很自然改写成：
   - `过去 N 根 bar 的最大单根/短窗正收益`
   - 去预测 `未来 H 根 bar` 的横截面相对表现。

换句话说，这轮不是补一个“解释为什么 winners 继续涨”的故事，而是补一条 **可以独立 A/B test 的信号骨架**。

## 4. 论文里最值得拿走的证据

## 4.1 主结论不是 reversal，而是正向 MAX effect

论文样本：
- 数据源：**CoinMarketCap**
- 时间：**2014-01 到 2020-09**
- 只保留 **市值高于 500 万美元** 的币
- 新币进入样本前先等 **6 个月**
- 样本从最早 **17** 个币扩展到最多 **523** 个币

核心定义：
- `MAX_{i,t}` = 某币在过去一个月里的**最大单日收益**
- 每周重排一次横截面
- 看下一周的组合收益

最关键结果：
- **高 MAX decile - 低 MAX decile = 3.03%/周**（value-weighted raw return spread，t=**4.10**）
- 对应 **三因子 alpha 差 = 1.99%/周**（t=**3.72**）
- equal-weight 版本也显著：raw spread **2.45%/周**

这条结论最重要的地方在于：

> 在股票里常见的是“彩票型/极端上涨资产后面回报更差”；但在这篇 crypto 样本里，结果反过来——**最近打过大阳线的币，后面更容易继续赢。**

## 4.2 不是只对单根极值敏感，前几次大阳线平均也成立

论文没有把结论押在单一 `MAX` 定义上，而是继续测了：
- `MAX(2)`
- `MAX(3)`
- `MAX(4)`
- `MAX(5)`

也就是：不只看“过去一个月最大那一天”，而是看“过去一个月里最大的前 2/3/4/5 个正收益日的平均值”。

结果仍然显著。

这对我们 desk 的启发很直接：
- 可以先测最原始的 `rolling max 1-bar return`
- 也可以测更稳一点的 `top-k positive bars mean`
- 后者往往更像“不是偶然一针，而是连续被追逐的强者”

所以它不是只能写成一个尖刺型事件信号，也能写成 **spike-cluster persistence**。

## 4.3 它不是 momentum / reversal / liquidity 的简单替身

论文明确做了双排序和横截面回归控制，控制项包括：
- `SIZE`
- `PRICE`
- `MOM`
- `REV`
- `ILLIQ`
- `VOL`
- skewness measures
- investor sentiment

比较值得记住的几个数字：
- 在低情绪期，high MAX - low MAX 仍有 **2.80%/周**
- 在高情绪期，仍有 **3.25%/周**
- 控制波动率后，high MAX - low MAX 仍有 **1.58%/周** 的 value-weighted raw spread
- Fama-MacBeth 单变量里，MAX 的平均斜率约 **8.21%**（t=**3.14**）

也就是说，这条信号不是一句“高波动币本来就更能涨”就能解释掉的。

## 5. 对当前 short-cycle desk，最诚实的读法是什么？

**最诚实的读法不是：**
- “看到 spike 就追单币 breakout”；

**而是：**
- 在一组流动性足够好的币里，
- 把“最近窗口内谁打出过更强的极端正收益”当成一个横截面排序因子，
- 去做 top-vs-bottom、winner-only、或 winner-plus-hedge 的 relative-value / XS continuation。

也就是说，这篇更适合服务：
- `cross-sectional momentum`
- `winner-only continuation`
- `beta-light relative-strength shell`

而不是把它误写成“单币见 spike 就追”。

## 6. desk 版策略骨架

## 6.1 信号定义

先给一个最小版：

- universe：`Binance USDⓈ-M perpetual` 高流动性池，先取 `top 12~20` by 24h quote volume
- bar：首选 `15m`，再下钻 `5m`
- lookback：
  - `15m`：过去 `64 / 96 / 128` 根 bar
  - `5m`：过去 `192 / 288 / 384` 根 bar
- 核心因子：
  - `MAX1` = lookback 内最大单根正收益
  - `MAX3` = lookback 内 top 3 正收益均值
  - `MAX5` = lookback 内 top 5 正收益均值
- 横截面 rank：按 `MAX1` 或 `MAX3` 排名

## 6.2 三个最小可交易版本

### 版本 A：top-bottom market-neutral
- long：top `20%`
- short：bottom `20%`
- 等权或 inverse-vol
- holding：`8 / 12 / 16` 根 bar

这是最直接复刻论文横截面的版本。

### 版本 B：winner-only + BTC 轻对冲
- 只做多 top `20%`
- 用 BTC perp 做轻 beta hedge
- 避免把 bottom bucket 硬写成必须可空

这是更 desk-friendly 的版本，因为 bottom leg 在 crypto 里经常掺杂反抽/逼空/上币噪声。

### 版本 C：MAX × standard momentum 双排序
- 先按传统 lookback return 排出 winner bucket
- 再在 winner bucket 里按 `MAX` 细分
- 只做 `high momentum & high MAX`

这个版本最适合回答一句：
**MAX 是独立 alpha，还是只是 winner strength 的一个更极端 proxy？**

## 6.3 入场 / 出场 / sizing / risk / cost

### 入场
- 只在换仓时点开仓，不在 bar 中追单
- 若某币最近 1~2 根 bar 已出现极端延伸，可改成下一根回踩限价，不强追最后一脚
- 初版先不用复杂 regime gate，避免把 raw alpha 本体看不清

### 出场
- 固定 holding `H` 根 bar 平仓
- 或 rank 掉回横截面中位数以下提前出
- 或 hit `ATR / sigma stop` 提前止损

### sizing
- 初版等权
- 第二版测 inverse-vol
- 单币 notional cap：组合资金 `10%~15%`
- 若 market-neutral 版本过于集中到小币，先加最小成交额和最小挂单深度门槛

### risk
- 单币止损：`1.5~2.0 x ATR(20)`
- 组合 kill-switch：当日回撤超过阈值暂停新开仓
- 极端公告 / 合约异常 / funding 爆点日可 veto 新仓

### cost
- 第一轮必须按 **taker 成本** 起步
- 记录 turnover / holding / gross-to-net decay
- 若 edge 只在极高换手下成立，优先减换手，不要先假设 maker 全成交能救回来

## 7. 1m / 3m / 5m / 15m 怎么映射

## 15m
最适合先做主实验：
- 噪声没 1m/3m 那么重
- 仍保留足够多的横截面换仓点
- 也最容易和日频论文保持“物理时间”相近的 transfer

## 5m
适合做第二轮：
- 看 recent-spike persistence 是否能更快体现
- 但要更严格控制 spread / depth / taker cost

## 3m / 1m
不建议第一轮就把它当主 alpha 周期。
更合理的读法是：
- `15m/5m` 负责给方向与 rank
- `3m/1m` 负责 child execution
- 例如用 pullback、spread 收敛、短时 OBI 不逆风来做更便宜的进场

## 8. 最小可复现实验

## 实验 A：MAX 本体有没有独立信息？

并排跑三条线：
1. `lookback cumulative return` 传统 winner-only
2. `rolling MAX` winner-only
3. `cumulative return × rolling MAX` 双高组合

看：
- after-cost return
- Sharpe
- turnover
- gross-to-net decay
- beta to BTC

如果 2 明显优于 1，说明这不是普通动量的马甲；
如果 3 最强，说明 MAX 更适合当 winner 书里的二级排序器。

## 实验 B：top-bottom vs winner-only

目的：验证 short leg 是否必要。

并排：
- top-bottom
- winner-only
- winner-only + BTC beta hedge

看：
- mean return
- mean log return
- MDD
- 单日极端 adverse move

如果 bottom short 对复利帮助不大，或明显放大尾部风险，就把这条线默认改写成 **winner-first**，而不是硬抄 decile spread。

## 实验 C：MAX1 vs MAX3 vs MAX5

目的：看单点 spike 还是 spike-cluster 更可交易。

- `MAX1`：最大单根正收益
- `MAX3`：top3 正收益均值
- `MAX5`：top5 正收益均值

如果 `MAX3/MAX5` 更稳，说明我们要拿走的不是“尖刺本身”，而是“最近被持续追逐过”。

## 9. 风险与保留意见

- 论文主样本是 **日频 -> 周频**，我们做的是 **短周期 transfer hypothesis**，不能把论文结论硬说成已经在 5m/15m 被验证。
- 这条信号和行为拥挤、上币故事、主题轮动天然有关系；如果 universe 不够 liquid，容易把噪声、庄股、单币事件一起混进来。
- MAX 本身可能会抬高 market beta 暴露，所以一定要和 `winner-only + BTC hedge` 对照，避免把牛市 beta 误判成 XS alpha。

## 10. 来源

1. **Ozdamar, M., Akdeniz, L., & Sensoy, A. (2021). _Lottery-like preferences and the MAX effect in the cryptocurrency market_. Financial Innovation.**
   - Authors: Melisa Ozdamar; Levent Akdeniz; Ahmet Sensoy
   - Year: 2021
   - Title: Lottery-like preferences and the MAX effect in the cryptocurrency market
   - Venue: Financial Innovation
   - DOI: <https://doi.org/10.1186/s40854-021-00291-9>
   - Readable URL: <https://link.springer.com/article/10.1186/s40854-021-00291-9>
   - PDF URL: <https://jfin-swufe.springeropen.com/track/pdf/10.1186/s40854-021-00291-9>
   - Repo URL: N/A
2. **CoinMarketCap historical cryptocurrency market data（论文主数据源）**
   - Readable URL: <https://coinmarketcap.com/>
3. **Binance USDⓈ-M Futures market data docs（短周期最小 transfer 可用公开数据）**
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api>

## 11. 下一步怎么测（一句话）

先在 `15m top-15` 永续主池上并排回测 `traditional winners`、`rolling-MAX winners`、`rolling-MAX winners + BTC hedge` 三条线，再用 `MAX1 / MAX3 / MAX5` 做二级排序；如果 high-MAX 书在 after-cost 与 mean-log-return 上都稳定更优，就把它升级为独立的 XS raw alpha 壳。