# Kim, Na, Song（ICAIF 2025）+ ORCA repo：别把 pairs 选对继续写成“谁和谁最像”，对 short-cycle desk 更该先测的是「tradability-aware clustering × OU spread raw alpha」
- 时间：2026-04-03 16:25 UTC
- 类型：论文 + GitHub 仓库 + Binance Futures 公共 `15m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**不是“深度学习聚类”本身**，而是 `pair spread mean reversion`；ORCA 真正值得 desk 先抄的，是把配对生成逻辑从“高相关/高相似”改成“更像 OU 均值回复过程的 tradable cluster”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / clustering / OU / tradability / admission-layer / Binance-perpetual / 1m / 3m / 5m / 15m / paper / repo / public-data
- 证据类型：ICAIF 2025 论文摘要 + 开源实现 + 本地 Binance 公共数据 sanity check

**先回答 base alpha：这篇东西的 base alpha 不是“PINN 很酷”，而是非常老实的 `spread 回归均值`。真正的新意在于：别再用“相关性高 / 距离近”去挑 pairs，而是直接用“这组资产未来更可能形成稳定 OU spread”去挑。对我们 desk，这比继续在 entry band 上卷花活更值钱。**

## 1) 这次看了什么
这次主看两份材料，再加一个本地最小快检：

1. **Kim, Namhyoung; Na, Yosep; Song, Jae Wook (2025)**, *Deep Mean-Reversion: A Physics-Informed Contrastive Approach to Pairs Trading*, **Proceedings of the 6th ACM International Conference on AI in Finance (ICAIF'25)**。
   - 论文核心不是直接发明一个新 exit，而是把 **pair formation / clustering** 改写成“是否更接近可交易的均值回复动力学”。
2. **GitHub: `x7jeon8gi/ORCA`（2025）**。
   - 开源实现显示，作者把 **OU 过程约束** 直接放进 loss 里，默认配置有：`cluster_num=30`、`price_window=12`、`epochs=200`、**月度滚动重训**。
   - 比较脚本里 downstream trading 其实很朴素：**静态 threshold + outlier filter + stoploss**，这反而说明 alpha 主体仍然是 pairs mean reversion，不是执行层魔法。
3. **我做的本地 Binance Futures `15m` sanity check**（`12` 个主流 USDT perp，约 `30d`，共 `66` 个 pair，结果存于 `reports/artifacts/quant_digests/2026-04-03_orca_pairs_sanity.csv`）。
   - 目的不是“复现 ORCA 论文收益”，而是快速验证：**仅靠高相关筛 pair，是否会把一堆根本不回归的慢 spread 当成好 pair。**

## 2) 论文/仓库里真正值得 desk 拿走的，不是模型名，而是 pair formation 目标函数
OpenAlex 还原出的摘要里，这篇论文的关键信息很直接：
- 传统 pairs 方法经常找不到**稳定均值回复**关系；
- ORCA 把 **contrastive clustering** 和 **physics-informed regularization** 绑在一起；
- 约束目标不是“看起来像”，而是“更符合稳定 **Ornstein-Uhlenbeck (OU)** 过程”；
- 作者在 NYSE 数据上报告：**即使 downstream 只用简单静态 threshold mean-reversion strategy**，ORCA 生成的 clusters 也优于 benchmark clustering 方法。

翻成人话：

> 你不该先问“哪两个币最近一起涨跌”，而该先问“哪两个币配出来的 spread 更像会回来的东西”。

这对 crypto short-cycle desk 的意义非常大，因为很多我们现在会做的 pair mining 其实默认是：
- 先按相关性、行业、同 beta、同叙事、同市值去凑；
- 再跑 cointegration / z-score；
- 最后在 threshold 上反复调。

ORCA 提醒的是：**pair formation 本身就应该是 alpha 的一部分。**
不是先把 pair 选烂，再指望 entry/exit 把烂 pair 救回来。

## 3) 为什么这条线现在值得写，而不是继续补一个普通 z-score pairs
因为我们最近 pairs 素材已经不少了，但很多还是停留在：
- 动态 beta
- band action
- percentile entry
- matching / portfolio construction
- ML entry filter

这些都重要，但它们默认你已经有一批**够像“会回归”的 pair**。
而 ORCA 的价值正好卡在更上游：

### 3.1 它服务的不是一个 filter，而是 raw alpha 的“候选生成层”
这不是单纯 overlay。
因为对于 pairs 来说，**pair admission / pair formation 本身就决定了 raw alpha 是否存在**。
如果挑出来的 spread 半衰期太长、漂移太慢、结构不稳定，后面所有 z-score 触发都是假勤奋。

### 3.2 它对 crypto 特别有意义
crypto 里高相关非常廉价：
- 都跟 BTC beta 走；
- 都受同一 risk-on/off 影响；
- 同叙事币经常一起涨跌；
- 同一波资金流能把很多 alt 同时抬起来。

但“高相关”不等于“spread 可交易”。
**可交易的 mean reversion** 需要更具体的东西：
- spread 不只是同步，还要有相对稳定的 equilibrium；
- 偏离后要在可忍受的 bar 数里回来；
- OOS 里要持续出现可重复的 excursion / reversion；
- 不能一半时间都在单边漂移。

ORCA 这篇最值钱的地方，就是把这些原本要靠人工后筛的性质，前移到 pair formation 目标里。

## 3.5) 策略拆解（必填）
- 方向属性：market-neutral / relative-value / pairs stat-arb
- 基础 alpha：**spread 偏离均衡后的均值回复**
- raw alpha 主体：`zscore(spread)` 或 `s-score` 异常偏离 → 回归均值
- ORCA/本篇贡献点：把 **pair 生成层** 从“相似性”改成“均值回复可交易性”
- regime：
  - 只在高流动性 perp 宇宙内启用
  - 只保留最近训练窗内 half-life、残差波动、crossing 频次达标的 pair
- filter / veto：
  - funding 极端单边时 veto
  - 重大事件币（上币/下架/解锁）临近时 veto
  - pair 两腿 rolling beta / residual vol 突变时 veto
- sizing / risk：
  - 单 pair 等风险配重
  - 组合内按 residual vol 或 expected half-life 缩放
  - 同叙事/同 sector pair 数量上限
  - gross / net / beta-to-BTC 三层约束
- exit：
  - `entry`: `|z| >= 1.5~2.5`
  - `take-profit`: `z -> 0` 或回到 `|z| <= 0.3~0.5`
  - `stop`: `|z|` 继续扩到 `3~4` 或超出 `2x` 预估 half-life 未回归
  - `time stop`: 超过最大持有 bars 强平
- cost：
  - 必测 taker-only
  - 再测 maker-entry / taker-exit
  - 显式打 fee + slippage + funding drag

## 4) 一个很有用的 desk 结论：别先问“哪两个币最像”，先问“哪两个币的 spread 最像会回来的东西”
这篇 digest 真正想推进的，不是“上 PINN”。
而是把我们 desk 的 pairs 研究顺序换掉：

### 旧顺序
1. 找高相关/同叙事币
2. 跑 cointegration
3. 调 z-score
4. 抱怨 cost 太高 / pair 不稳定

### 更好的顺序
1. 先定义 **tradability score**：
   - half-life
   - residual stability
   - OOS crossing frequency
   - residual vol / jump profile
2. 再用模型或规则，优先生成 tradable clusters / tradable pairs
3. 最后才在 entry/exit/sizing 上细化

也就是说，**ORCA 对我们最值得抄的不是“深度学习”，而是“pair admission objective 要改”。**
如果先用更土的规则版也能跑，就已经够值钱。

## 5) Binance `15m` 最小快检：高相关 pair 里，很多根本不是好 spread
我做了一个很粗但很实用的 sanity check：
- 数据：Binance Futures 公共 `15m` K 线
- 宇宙：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/SUI/LTC/BCH` 共 `12` 个 USDT perp
- 样本：约 `30d`，`66` 个 pair
- 训练/测试：约 `67% / 33%`
- 指标：
  - train return corr
  - train spread OU half-life（粗估）
  - OOS zero-cross 次数

### 5.1 先看一个很刺眼的数字
在这 `66` 个 pair 里：
- `corr > 0.88` 的 pair 有 **`12`** 个；
- 其中 **只有 `2` 个** 同时满足 `half-life < 48 bars`；
- 还有 **`3` 个** 在测试窗里 **`0` 次** 零轴穿越。

这句话已经够说明问题：
**高相关 pair 远多于可交易 pair。**

### 5.2 几个例子特别说明问题
高相关但很慢、甚至不怎么回：
- `ETHUSDT-LINKUSDT`: `corr=0.928`，但 `half-life≈153 bars`
- `BTCUSDT-ETHUSDT`: `corr=0.908`，但 `half-life≈121 bars`，OOS `0` 次零轴穿越
- `BNBUSDT-LINKUSDT`: `corr=0.897`，但 `half-life≈160 bars`，OOS `0` 次零轴穿越

相关性没那么夸张，但更像“能交易”的：
- `BNBUSDT-SUIUSDT`: `corr=0.830`，`half-life≈36 bars`，OOS `38` 次零轴穿越
- `BTCUSDT-LINKUSDT`: `corr=0.887`，`half-life≈38 bars`，OOS `6` 次零轴穿越
- `SOLUSDT-LTCUSDT`: `corr=0.827`，`half-life≈31 bars`，OOS `10` 次零轴穿越

这正好对应 ORCA 想解决的问题：
**相似性排序和 tradability 排序不是一回事。**

### 5.3 这组快检对 desk 的启发
对 `5m/15m` 短周期 pairs，pair formation 至少该多看三件事：
1. **half-life**：太慢的 pair，不适合短周期 desk；
2. **crossing density**：长期不回零的 pair，不值得占用额度；
3. **residual stability**：残差幅度太漂、太容易 regime shift，也不行。

所以这篇 digest 更该落地成：
**OU-aware admission layer**，而不是“上一个论文模型名字”。

## 6) 对 1m / 3m / 5m / 15m 的 desk 翻译
### 6.1 不直接照抄论文的数据口径
原论文和 repo 用的是 **WRDS / CRSP 月频股票特征**，repo 默认也是：
- `price_window=12`
- 月度滚动训练
- `cluster_num=30`
- 下游 static threshold strategy

这不能直接冒充成“论文已经证明 crypto `5m/15m` 有效”。
但它提供了一个非常可迁移的研究模板：

> 用更像 OU 的 pair / cluster 去喂一个简单 spread strategy，往往比用普通相似性 pair 再去拼命调 entry 更有价值。

### 6.2 short-cycle 版本怎么最小落地
先不用上神经网络，先做一个 **规则版 ORCA**：

1. **Universe**
   - 最近 `14d~30d` 名义成交额前 `20~40` 个 perp
   - 去掉明显事件币、超高 funding 币、长期限价深度不足的币

2. **Candidate generation**
   - 两两配对，先做粗筛：
     - `corr(ret) >= 0.75~0.85`
     - 两腿 median spread / depth 达标

3. **Tradability score（这一步是本篇核心）**
   - `half_life_bars`
   - `spread_zero_cross_density`
   - `residual_vol_stability`
   - `rolling beta stability`
   - `tail jump veto`

4. **只保留 top-K tradable pairs**
   - 比如每次只做 `5~10` 个 pair
   - 而不是“能过 cointegration 的都做”

5. **Execution shell**
   - `entry`: `|z| >= 1.5/2.0/2.5`
   - `exit`: `z -> 0`
   - `stop`: `|z| >= 3.5` 或超过 `2x half-life`
   - `rebalance`: `5m` 每 bar 看，`15m` 每 bar 或每 2 bars 看

### 6.3 如果规则版先有结果，再考虑上模型
只有当规则版 admission layer 已经显示：
- 比纯相关选对更稳；
- 比纯 cointegration 过筛更稳；
- 能明显降低慢 spread / 假 pair 占比；

再往前走到：
- 对 pair feature 做 representation learning；
- 把 OU loss / residual stability 正则化放进 embedding 学习；
- 做 cluster-level pair mining。

## 7) 下一步怎么测（本篇最重要的部分）
### 实验 A：先做“规则版 ORCA admission layer”
**目的**：先验证“选 pair 目标函数”是否比“调 threshold”更重要。

- universe：Binance/Bybit/Hyperliquid 高流动 perp 前 `20~40`
- 粗筛：`corr >= 0.8`
- 对每个 pair 计算：
  - `half_life`
  - `zero_cross_per_day`
  - `residual_std`
  - `rolling_beta_std`
  - `max_adverse_z`
- 组两套组合：
  1. `Top corr pairs`
  2. `Top tradability-score pairs`
- downstream execution 完全一样

**要看的输出：**
- net pnl
- pnl per turn
- median holding bars
- stop-hit ratio
- pair replacement frequency

### 实验 B：5m vs 15m 的 half-life 适配区间
**目的**：别让慢 spread 混进短周期 book。

- `5m` 先限定 `half-life ∈ [6, 48] bars`
- `15m` 先限定 `half-life ∈ [4, 32] bars`
- 看不同 half-life 桶的：
  - OOS crossing density
  - entry fill 后回归概率
  - time-stop 占比

如果 alpha 主要集中在 `half-life > 100 bars`，那它就不是 short-cycle desk 该优先做的东西。

### 实验 C：pair score 里要不要加 funding / OI / liquidation 公开数据
**目的**：把 tradability score 往 crypto 特有结构再推一步。

给 score 加三个候选特征：
- funding spread 稳定度
- OI 共振/背离程度
- liquidation cluster proximity

看这些特征是：
- 提升 pair admission
- 还是只适合作为 entry veto

### 实验 D：从单 pair 走向 cluster-neutral book
**目的**：把 ORCA 真正的“cluster”思想 desk 化。

- 先用规则特征把币分成 `5~8` 个 cluster
- 只在 cluster 内做 pairs
- 每个 cluster 限 gross / pair 数量上限
- 观察是否能减少“全 book 同时暴露在同一 beta/regime 上”的问题

## 8) 我对这条线的判断
**值得进研究池，而且优先级偏高。**

不是因为“深度学习 + physics-informed”这串词听起来厉害，
而是因为它很准确地击中了我们 pairs 研究里一个真实痛点：

> 很多 pair 研究失败，不是输在 entry/exit，而是输在一开始就选了不该做的 pair。

如果后续规则版 admission layer 就能显著提升：
- pair 稳定性
- 回归密度
- pnl per turn
- 成本后存活率

那这条线就可以自然扩成：
1. 一个独立 raw alpha（tradability-aware pairs book）
2. 一个 shared component（给其他 pairs / stat-arb 策略共用的 pair admission 层）

## 9) 风险与保留意见
- 原论文/开源实现基于 **股票月频 + WRDS 数据**，不是现成 crypto `5m/15m` 策略包。
- 我这里的 Binance 快检只是 **sanity check**，不是收益复现；它证明的是“相关性不等于 tradability”，不是证明某几个 pair 已经能赚钱。
- OU / half-life 估计对窗口长度很敏感，必须 walk-forward，不能一次估完永久使用。
- cluster 方法可能在强单边市里退化成 beta grouping；需要额外 market beta / funding beta 约束。
- 如果 execution 不足，很多看起来“会回来”的 pair，最后可能死在成本和 time-stop 上。

## 10) 来源
### 论文
- Kim, Namhyoung; Na, Yosep; Song, Jae Wook (2025). *Deep Mean-Reversion: A Physics-Informed Contrastive Approach to Pairs Trading*. **Proceedings of the 6th ACM International Conference on AI in Finance (ICAIF '25)**.
- DOI: `10.1145/3768292.3770406`
- Readable URL: `https://doi.org/10.1145/3768292.3770406`
- ACM DOI URL: `https://dl.acm.org/doi/10.1145/3768292.3770406`
- Repo URL: `https://github.com/x7jeon8gi/ORCA`

### 开源仓库
- `x7jeon8gi/ORCA` (GitHub, 2025)
- 描述：*Pytorch Implementation of Deep Mean-Reversion: A Physics-Informed Contrastive Approach to Pairs Trading (ORCA)*
- Repo URL: `https://github.com/x7jeon8gi/ORCA`

### 本地最小快检
- 文件：`reports/artifacts/quant_digests/2026-04-03_orca_pairs_sanity.csv`
- 口径：Binance Futures 公共 `15m` K 线，`12` 个主流 USDT perp，约 `30d` 样本，`66` 个 pair，train/test 约 `67%/33%`
