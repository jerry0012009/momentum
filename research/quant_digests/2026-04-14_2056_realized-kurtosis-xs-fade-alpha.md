# 别把 higher moments 只读成资产定价注脚：对 short-cycle desk，更该先测的是「realized-kurtosis cross-section fade」这条 raw alpha

- 主题类型：raw alpha
- 基础 alpha：**横截面上，最近一段时间收益分布更“尖、跳、尾部更肥”的币，后续几根 bar 更容易相对跑输；分布更平、尾部没那么肥的币，后续更容易相对跑赢，因此可做 `long low-kurtosis / short high-kurtosis` 的横截面反转**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 时间：2026-04-14 20:56 UTC
- 类型：2020 *Finance Research Letters* 论文元数据 + 2026 GitHub repo source audit（`Statistical Arbitrage Higher Moment Crpyto Strategies.ipynb`）
- 主题标签：raw-alpha / cross-sectional / relative-value / stat-arb / mean-reversion / realized-moments / kurtosis / higher-moments / tail-risk / long-short / 15m / 5m / 3m / 1m / paper / repo / public-data / cost
- 证据类型：paper-based（higher-moments crypto cross-section grounding）+ repo-based（可直接抄成最小策略壳）

## 1. 这次为什么选它

这轮默认优先补 **可独立复现的 raw alpha**，而不是再写一个纯 gate / overlay。

最近 digest 已经写过不少：
- lead-lag / catch-up
- pairs / cointegration / basis
- funding / carry
- skewness / MAX / loser-basket

但 **“更高阶分布形状 → 短线横截面 relative value”** 这一支还不厚，尤其是 **`kurtosis`（尾部肥厚 / 跳变密度）** 这条线，库里还没有单独立项。

这次我选它，不是因为 repo 里最亮眼的结果一定来自 kurtosis；恰恰相反，repo 里最强的是 plain reversal。**我选的是其中更适合我们素材池补短板的旁支 raw alpha：`realized-kurtosis fade`。**

一句话先把 base alpha 说死：

> **不是追涨跌本身，而是做“最近这币是不是进入了 jumpy / 尖峰厚尾 / 容易被尾部事件支配的状态”之后的横截面回吐。**

这条线之所以值得进池，是因为它补的是 **tail-shape / distribution-state** 家族，而不是把已有 reversal 再换个 lookback 皮肤。

## 2. 这次看的材料

### 2.1 crypto higher-moments grounding

- **Authors**: Yuecheng Jia, Yuzheng Liu, Shu Yan
- **Year**: 2020
- **Title**: *Higher moments, extreme returns, and cross–section of cryptocurrency returns*
- **Venue**: *Finance Research Letters*
- **DOI**: `10.1016/j.frl.2020.101536`
- **Readable URL**: <https://doi.org/10.1016/j.frl.2020.101536>
- **Repo URL**: 未见作者公开 repo

### 2.2 可直接抄壳的 repo / notebook

- **Author**: Evan Hetland
- **Year**: 2026（repo 创建于 2025-10-22，最后更新 2026-02-28）
- **Repo**: `EvanHetland/Signal-Research`
- **Notebook**: `Statistical Arbitrage Higher Moment Crpyto Strategies.ipynb`
- **Readable URL**: <https://github.com/EvanHetland/Signal-Research>
- **Direct Notebook URL**: <https://github.com/EvanHetland/Signal-Research/blob/main/Statistical%20Arbitrage%20Higher%20Moment%20Crpyto%20Strategies.ipynb>
- **DOI**: 无

## 3. 先把 base alpha 讲清楚：它不是 filter，它本身就是 alpha

repo 里这条支线写得很直接：

```python
avg_ret = ret.rolling(5, min_periods=1).kurt().rank()
avg_ret = avg_ret.subtract(avg_ret.mean(1), 0)
avg_ret = avg_ret.divide(avg_ret.abs().sum(1), 0)
strat = (-avg_ret.shift(5) * ret).sum(1)
```

把它翻成人话就是：

1. 对每个币，算最近 `5` 根 bar 收益序列的 **realized kurtosis**；
2. 做横截面排序；
3. **short 最近更高 kurtosis 的币，long 最近更低 kurtosis 的币**；
4. 信号滞后 `5` 根 bar 后再吃下一期横截面收益。

这里的经济直觉不是“高 kurtosis = 一定反转”，而是：

- 高 kurtosis 往往意味着最近的收益由少数极端 bar / wick / jump 主导；
- 这种状态在 crypto 里经常和短时拥挤、消息冲击、流动性抽干、连环止损、局部 squeeze 绑在一起；
- 当这种尾部主导状态过后，**横截面 relative performance** 往往会从“最夸张的那批币”往更正常的币回摆。

所以它不是：
- 只服务于别的 alpha 的 veto；
- 只能做解释变量；
- 必须绑定趋势或 pairs 才能存在。

它本身就是一条 **cross-sectional raw alpha**：

> **`long low-kurtosis / short high-kurtosis` 的横截面 fade。**

## 4. repo 里到底给了什么硬信息

### 4.1 数据和样本口径

notebook 直接从 Binance 拉公开历史 K 线：

- **Universe**：18 个 USDT 对
  - `BTC, NEAR, ATOM, HBAR, ETH, ADA, LINK, SUI, XLM, BNB, ICP, UNI, LTC, AAVE, XRP, AVAX, ETC, DOT`
- **Bar 频率**：`4h`
- **样本区间**：`2025-03-09` 到 `2025-10-22`
- **样本长度**：`1363` 根 `4h` bar
- **train/test**：直接前后各半切分

这不等于 production evidence，但至少说明它不是纯嘴炮：**数据可公开获取、代码可读、信号和成本都写出来了。**

### 4.2 notebook 内几条 higher-moment / XS 信号

同一本 notebook 里其实混了几条横截面信号：

- plain return reversal
- rolling volatility rank
- rolling skewness rank
- rolling kurtosis rank

对我们最有价值的不是“整本 notebook 结论”，而是它把 **higher-moment cross-sectional shell** 明确写出来了。

### 4.3 和这次主题最相关的几个数字

按 notebook 自带输出：

- **kurtosis 信号单独跑**：`rolling(5).kurt()`、`shift(5)`、turnover cost `20 bps`
  - 年化 Sharpe 约 **`1.86`**
- **skewness 信号单独跑**：年化 Sharpe 约 **`0.10`**
- **volatility-rank 信号单独跑**：
  - `2-bar` vol rank 年化 Sharpe 约 **`0.63`**
  - `6-bar` vol rank 年化 Sharpe 约 **`-0.26`**
- **plain 1-bar XS reversal**：年化 Sharpe 约 **`16.52`**（明显强得离谱，后面必须防数据挖掘 / 成本低估 / 样本偶然性）
- **reversal + vol/skew/kurt 组合**：年化 Sharpe 约 **`17.15`**，最大回撤约 **`-4.60%`**

我对这些数字的解读是：

1. **plain reversal 很强，但太像“样本窗里打鸡血”**，不缺新意；
2. **kurtosis 单信号虽然不炸裂，但它是正的，而且方向清楚、结构独立、可下沉到短周期**；
3. 这更像一个该被纳入 raw-alpha 素材池、做增量检验的信号，而不是直接拿 repo 的组合 Sharpe 当真相。

## 5. 为什么这条线对我们的 desk 有意义

### 5.1 它补的是“尾部形状”家族，不是普通 loser-bounce

已知很多 XS alpha 都在看：
- lagged return
- rolling MAX
- skewness
- volatility

但 **kurtosis** 看的是另一件事：

> **最近这段路径是不是被“少数极端条”支配。**

这和：
- 单纯跌多了会不会反弹，
- 单纯涨多了会不会回吐，

不是一回事。

### 5.2 它天然适合做 short-cycle relative value，而不是单币故事会

单币上看到高 kurtosis，很容易沦为：
- “刚插针了”
- “刚暴拉了”
- “刚被爆仓链带飞/带崩了”

但横截面上它更有意思，因为你可以比较：

- 哪些币最近的收益分布最异常；
- 哪些币只是正常波动；
- 异常程度是否会在随后几根 bar 回吐成 relative underperformance。

这正适合我们 desk 熟悉的 **market-neutral / dollar-neutral / long-short bucket** 壳。

### 5.3 它对 `5m / 15m` 比对 `1m` 更自然

kurtosis 对噪音非常敏感。

所以我对这条线的默认优先级不是：
- 先冲 `1m`；

而是：
- **先 `15m`**，
- 再 **`5m`**，
- `3m / 1m` 只做更激进的二轮验证。

原因很简单：bar 太细时，kurtosis 很容易退化成“谁的微观结构更脏”。

## 6. desk 版最小可复现实验怎么写

### 6.1 先给完整策略壳

**Universe**
- Binance / OKX / Bybit 主流 USDT perp
- 先取 `24h quote volume` 前 `20~40` 个
- 去掉：
  - 新上架不满 `30d`
  - 最近 `N` bars 缺失率高
  - 成交额 / 深度太差的币

**Signal**
- 对每个币计算最近窗口的 realized excess kurtosis
- 做横截面 rank 或 z-score
- 方向：**long low-kurtosis bucket / short high-kurtosis bucket**

**Entry / Exit**
- 固定时点重排组合
- 第一轮先做最干净版本：
  - `rebalance every K bars`
  - `hold H bars`
  - 不加 discretionary 单币止盈止损

**Sizing**
- 先 dollar-neutral 等权
- 单币权重上限 `5%~7%`
- 第二轮再试 vol-neutral

**Risk / Cost**
- 单边成本先压 `3 / 5 / 8 bps`
- 做 BTC 急剧单边波动 veto
- 做 liquidity floor 与 funding extreme veto

### 6.2 我建议先测的参数网格

#### `15m` 主测

- **lookback W**：`16 / 32 / 48` bars（约 `4h / 8h / 12h`）
- **signal lag L**：`2 / 4 / 8` bars（约 `0.5h / 1h / 2h`）
- **holding H**：`1 / 2 / 4` bars
- **bucket**：top/bottom `10% / 20% / 30%`

#### `5m` 次测

- **lookback W**：`48 / 96 / 144` bars（约 `4h / 8h / 12h`）
- **signal lag L**：`6 / 12 / 24` bars
- **holding H**：`3 / 6 / 12` bars
- **bucket**：top/bottom `10% / 20% / 30%`

### 6.3 我更建议的实现细节

为了防 kurtosis 被脏尾部骗死：

- 先对单 bar return 做 `winsor / clip`
- 至少比较两套版本：
  - raw return kurtosis
  - clipped return kurtosis
- 若 clipped 版稳定性明显更好，优先信 clipped 版

## 7. 这条 alpha 和我们库里已有的 skewness / MAX 有什么区别

### 7.1 vs `MAX`

- `MAX`：盯最近是否出过最极端大阳 / 大阴
- `kurtosis`：盯整段分布是不是被极端条系统性支配

所以 kurtosis 比 MAX **更像“整段尾部结构”**，不只是单根极值记分牌。

### 7.2 vs realized skewness

- `skewness`：更偏“哪边尾更长”
- `kurtosis`：更偏“尾巴是不是整体更肥、更尖、更 jumpy”

skewness 更像方向性彩票偏好；
kurtosis 更像状态性尾部拥挤 / 异常波动结构。

对 short-cycle desk 来说，这意味着：
- skewness 更容易和 trend / squeeze 纠缠；
- kurtosis 可能更适合作为 **relative-value fade** 的原始打分。

## 8. 它最容易失败在哪

### 8.1 它可能只是“低流动性代理变量”

如果高 kurtosis 只是因为盘口差、成交稀、wick 多，那你并不是抓到了可交易 alpha，而是抓到了垃圾币标签。

所以一定要做：
- liquidity bucket 分层
- ADV / quote volume 缩权
- top-liquidity only 子样本

### 8.2 它可能和 plain reversal 高度重叠

repo 里 plain 1-bar reversal 非常强，说明这段样本里 return reversal 本身就可能吃掉了大量解释力。

因此必须问一句：

> **kurtosis 到底是独立 alpha，还是“极端路径版 reversal”的代理变量？**

如果增量解释力不够，它就应该降级成多因子里的次级特征，而不是单列 sleeve。

### 8.3 它可能在太快频率上被 microstructure 噪音淹没

`1m / 3m` 下高 kurtosis 很可能只是：
- 一堆散乱 wick
- 偶发大单扫盘
- 撮合噪音

所以我不建议第一轮直接把它当 `1m` 主信号。

## 9. 下一步怎么测（直接给实验单）

### 实验 A：先做独立性检验

在 Binance perp `15m` universe 上同时做：

- `signal_1 = -rank(kurtosis_W)`
- `signal_2 = -rank(ret_W)`
- `signal_3 = -rank(skewness_W)`

看：
- 横截面相关性
- next-bar / next-2bar rank IC
- 双变量 / 三变量横截面回归的增量 t-stat

**判定标准**：
- 若 `signal_1` 对 `signal_2` / `signal_3` 没增量，就不单列；
- 若有稳定增量，再继续推进 production shell。

### 实验 B：验证它是不是只在可交易 universe 里活

分三层跑：
- top 10 liquidity
- top 20 liquidity
- top 40 liquidity

**我当前先验**：
> 真正能下单的版本，大概率应该在 `top 10~20` 里仍然为正；如果只在尾部垃圾币里好看，这条线就不值钱。

### 实验 C：验证 lag 是否必要

repo 用了 `shift(5)`，但对我们 desk 不一定需要照抄。

先测：
- `L = 0 / 1 / 2 / 4 / 8`（15m）

看结论到底更像：
- 极短延续后的回吐，还是
- 明确需要等尾部事件冷却一段时间。

### 实验 D：验证 clipped returns 是否更稳

对同一参数网格，同时算：
- raw kurtosis
- 1%/99% clipped kurtosis
- 2.5%/97.5% clipped kurtosis

如果 clipped 版显著提高 OOS 稳定性，就说明这条线真正想抓的是 **尾部状态**，不是单根脏 wick。

## 10. 最终判断

这篇值得进研究池，而且我会把它放在 **“可独立复现、但需先做增量验证的 raw alpha”** 这一档，而不是直接判成 production-ready。

原因很简单：

1. **base alpha 清楚**：`long low-kurtosis / short high-kurtosis`；
2. **可独立复现**：只要公开 OHLC 就能做；
3. **能写成完整策略**：entry / exit / sizing / risk / cost 全都容易补齐；
4. **和现有池子有差异**：它补的是 `tail-shape / higher-moments` 家族；
5. **repo 已给出可移植代码壳**，但还远没到可以盲信 Sharpe 的程度。

所以这轮我的结论不是“这条线已经被证实很强”，而是：

> **把 `realized-kurtosis cross-section fade` 纳入 short-cycle raw-alpha 素材池，优先按 `15m → 5m → 3m/1m` 顺序验证它对 plain reversal / skewness 是否有独立增量。**

如果实验 A/B/C/D 跑出来增量成立，它就有资格成为：
- 独立 XS sleeve，或
- 多因子 XS 排序模型里的 higher-moment feature。

## 11. 来源链接

1. Jia, Y., Liu, Y., & Yan, S. (2020). *Higher moments, extreme returns, and cross–section of cryptocurrency returns*. *Finance Research Letters*, 39, 101536. DOI: `10.1016/j.frl.2020.101536`  
   URL: <https://doi.org/10.1016/j.frl.2020.101536>

2. Hetland, E. (2026). *Signal-Research* — `Statistical Arbitrage Higher Moment Crpyto Strategies.ipynb`.  
   Repo URL: <https://github.com/EvanHetland/Signal-Research>  
   Notebook URL: <https://github.com/EvanHetland/Signal-Research/blob/main/Statistical%20Arbitrage%20Higher%20Moment%20Crpyto%20Strategies.ipynb>
