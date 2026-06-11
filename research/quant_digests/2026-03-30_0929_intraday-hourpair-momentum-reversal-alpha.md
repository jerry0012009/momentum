# 24/7 伪交易日里的“早段续动 + 尾段反转”：把 Wen et al. (2022) 改写成 crypto 短周期 raw alpha 池

- 时间：2026-03-30 09:29 UTC
- 类型：raw-alpha
- 主题标签：raw-alpha/time-of-day/intraday/hourly/hour-pair/momentum/reversal/pseudo-session/single-asset/btc/eth/ltc/xrp/1m/3m/5m/15m/paper/public-data/cost
- 证据类型：2022 *The North American Journal of Economics and Finance* 论文摘要页 + ScienceDirect section snippets + IDEAS/RePEc 摘要页 + Crossref/OpenAlex 元数据

- 主题类型：raw alpha
- 基础 alpha：同一“伪交易日”内，较早时段的 1h 收益能对较晚时段的 1h 收益提供可交易预测，而且在 crypto 里这种预测既可能是**同向续动**，也可能是**反向回吐**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（论文本身更像 signal-family paper，但补齐成 desk 可跑最小策略很快）

## 0. 先回答一句：这篇东西的 base alpha 是什么？
base alpha 不是“又一个泛泛的 intraday seasonality”。它更具体：**把 24 小时切成若干 hour-pair，寻找“前一段小时收益 → 后一段小时收益”的稳定映射；有些 pair 做 continuation，有些 pair 做 reversal。**

这就让它不是纯解释型材料，而是一组可以直接进入研究池的 `same-day time-series alpha family`：
- 不依赖 funding / basis / options；
- 不要求跨资产对冲；
- 也不是只能服务 breakout 的 gate；
- 更像一套可在 `1m/3m/5m/15m` 上执行的**时钟条件化 directional alpha**。

## 1. 这次看了什么
Wen, Bouri, Xu, Zhao 在 2022 年研究 BTC 的**同日内收益预测性**。他们用 BTC 的 5 分钟高频价格构造小时收益，样本覆盖 **2013-03-03 到 2020-05-31**，核心问题是：在一个 24/7、没有隔夜休市的 crypto 市场里，更早时段的收益，是否还能像股票那样，对同一天更晚时段的收益有预测力？

答案是：**有，而且不只是一边倒的 momentum。** 论文明确强调，crypto 的 intraday predictors 既可能是正号，也可能是负号——也就是同一天里同时存在“早段续动”和“尾段回吐”两类 pocket。作者还发现：
- 这种 predictability 在 **无大跳跃（no jump）**、**非 FOMC 公布窗口**、**低流动性** 子样本里更强；
- 现象不只在 BTC，上到 **ETH / LTC / XRP** 也能看到；
- 基于有效 predictor 的 timing strategy，经济价值**高于** always-long / buy-and-hold 这类基准。

对 desk 来说，最值得拿走的不是“论文证明了 crypto 也有 intraday anomaly”，而是这句更实用的话：**不要把同日内方向信号只理解成 continuation；在 24/7 crypto 里，clock-conditioned reversal 也是 raw alpha。**

## 2. 为什么这题现在值得排进研究池
这条线和我们最近已经积累的几类 raw alpha 不同：
- 它不是 pairs / stat-arb；
- 不是 funding / carry；
- 不是 order-book microstructure 里的秒级压力；
- 也不是固定结构形态（breakout / retest / trendline）。

它提供的是一条更“轻数据、轻工程”的 raw alpha 路径：
1. 只要有连续分钟级 K 线，就能先做最小实验；
2. 先在 BTC / ETH 单币跑，后面再扩到 majors；
3. 可以同时支持 `5m / 15m` 主实验，也能下钻到 `1m / 3m` 做 execution refinement；
4. 将来还能自然叠加 jump / FOMC / liquidity 这些 regime 条件，而不需要先上复杂模型。

换句话说，这篇材料给的是**raw alpha 主体**，不是只给一个 veto 层。

## 3. 论文里真正值得 desk 抓住的 4 个点
### 3.1 24/7 市场里，intraday alpha 不是只有正号
股票里的经典 intraday momentum 往往更像“开盘信息慢扩散 → 收盘前继续走”。

但这篇论文明确说，crypto 因为：
- 24/7 连续交易；
- 没有传统隔夜空窗；
- 散户占比高、噪音交易多；
- 基本面锚弱、情绪和过度反应更强；

所以同日内预测关系的**符号本身**就是研究对象：
- 有些 hour-pair 是 continuation；
- 有些 hour-pair 是 reversal。

这对我们特别重要，因为它意味着不能把“时钟类 alpha”自动翻译成 trend filter；它本身就可能是一套独立的 directional signal family。

### 3.2 强度并不是在“最热闹”时段最高
论文摘要直接点名：predictability 在 **no jump / no FOMC / low liquidity** 情况下更强。

这有两个直接启发：
- **启发 A：** 这条 alpha 更像慢扩散 + 过度反应混合体，而不是纯信息公告驱动；
- **启发 B：** 做 live 时不能只挑最活跃时段，反而要专门测试“相对安静但仍可成交”的 pocket。

当然，论文里的“低流动性更强”不等于 live 一定更赚钱，因为 crypto 实盘会多出 spread / impact / queue risk。对 desk 来说，这不是立即上线的 gate，而是**必须拿成本后结果来判**的条件分层。

### 3.3 它不是 BTC 独有现象
论文还把结论扩展到 **ETH / LTC / XRP**。这点的意义不是“所有币都能照抄”，而是说明这不是某一条 BTC 历史偶然路径。

更好的 desk 读法是：
- 先在 BTC 做 hour-pair mining；
- 再看 ETH 是否保留同符号、同方向 pocket；
- 若 majors 间共享某些时钟 pocket，再考虑做 basket 化或 cross-asset confirmation。

### 3.4 论文已经给了“做 timing strategy”这个许可
作者并不只停在统计显著性，而是明确说基于有效 predictor 的 timing strategy，经济价值高于 always-long / buy-and-hold。

这很关键。因为它说明这篇东西默认就不是“解释市场现象的综述”，而是**允许你往交易规则推进**。虽然论文页我们当前拿到的是摘要和 section snippets，不是完整表格全文，但 raw alpha 定义已经足够清晰，可以先做最小复现。

## 4. 对 desk 的正确翻译：不要抄论文 headline，要抄它的 alpha family
最合理的 desk 改写不是“找出论文里最强的某一对小时，然后机械照搬”。更好的做法是把它翻成一套 hour-pair mining framework：

1. **定义伪交易日锚点**
   - 默认先用 `UTC 00:00` 切日；
   - 备选再测 `UTC 08:00`（更贴近亚洲早盘）和 `UTC 13:00/14:00`（更贴近欧盘/美盘切换）；
   - 不同锚点本质上是在问：哪种 session framing 最适合 24/7 crypto。

2. **把分钟线压成小时 predictor，但执行仍在短周期**
   - 信号层：用过去某个小时的 return 作为 predictor；
   - 执行层：在目标小时内部用 `15m / 5m / 3m / 1m` 分批进出。

3. **允许 continuation 与 reversal 共存**
   - 若某个 hour-pair 估出来是正 beta，就做 continuation；
   - 若估出来是负 beta，就做 reversal；
   - 不要先验规定“同日内一定追涨”或“一定反转”。

4. **把 jump / FOMC / liquidity 当条件切片，不是先验真理**
   - 论文给的是方向：`no jump / no FOMC / low liquidity` 更强；
   - desk 要做的是：这些条件在扣成本后是否仍保留净边际。

## 5. 可落地的最小实验（直接给 next step）
### 5.1 数据口径
- 标的：先做 `BTCUSDT perpetual`，再复制到 `ETHUSDT perpetual`
- 频率：下载 Binance 公共 `1m` K 线；向上聚合得到 `5m / 15m / 1h`
- 区间：先取最近 12 个月，滚动训练 + 前瞻测试
- 日切：默认 `UTC 00:00`
- 额外标签：
  - `jump_flag`：过去 1h 绝对收益是否超过滚动 60d 同 hour 分位数（如 p95）
  - `fomc_flag`：是否落在 FOMC 公布日前后窗口（先用公开日历）
  - `liq_bucket`：目标小时起始前过去 1h 的 dollar volume 分位桶

### 5.2 信号挖掘
对每个伪交易日内的 `(predictor_hour i, target_hour j)` 组合做滚动检验：
- 训练窗：60 天
- 测试窗：14 天
- 条件：`j > i`，同一伪交易日内
- 回归：`r_j = alpha + beta * r_i`
- 保留条件：
  - IS `t-stat(beta) > 2`
  - OOS `R^2 > 0`
  - beta 符号在最近 3 个滚动窗一致
  - 目标小时平均绝对波动 > 预估 round-trip cost 的 `1.5x`

这一步的目的不是生成一条固定信号，而是先找出**稳定的正向 pocket**和**稳定的反向 pocket**。

### 5.3 交易规则
对保留下来的 hour-pair：
- 若 `beta > 0`：
  - predictor 小时收盘后，若 `r_i > 0`，则在 target hour 开头做多；若 `r_i < 0`，则做空
- 若 `beta < 0`：
  - predictor 小时收盘后，若 `r_i > 0`，则在 target hour 开头做空；若 `r_i < 0`，则做多

执行细节：
- `15m` 版：target hour 前 15 分钟进场，持有到该小时结束
- `5m` 版：target hour 前 5 分钟进场，持有 2~4 根 5m K
- `1m/3m` 版：只对最稳定的 1~2 个 pocket 做 execution refinement，不要一开始全覆盖

### 5.4 sizing / risk / cost
- 单笔目标波动风险：账户权益的 `25bp`
- 同时持仓上限：`2` 个 pocket
- 同币单日最大方向暴露：`50%` notional
- 止损：目标小时内若反向走出 `0.75 x` 过去 20 个同类 trade 的中位绝对收益，提前止损
- 成本：
  - taker 回转先按 `4bp~6bp` 压测
  - maker/taker 混合版再做第二轮
- 跳过条件：若 predictor 小时结束时 funding / 大事件 / 极端波动使 spread 明显恶化，则记为 veto 版本单独统计，不要和主实验混算

## 6. 我更建议先测的，不是“全 24 小时扫一遍”，而是这 3 个版本
### 版本 A：最朴素的 BTC 单币版
- BTCUSDT perp
- `UTC 00:00` 切日
- predictor/target 都按 `1h`
- 执行在 `15m`

目的：先确认同日内 hour-pair predictability 在近一年是否仍存在。

### 版本 B：同信号、短执行版
- 信号仍是 `1h -> 1h`
- 执行改成 `5m`
- 比较 `target hour 开头 5m`、`开头 15m`、`均匀 TWAP 一小时` 三种进入方式

目的：看 alpha 在短周期执行里是“越快越好”，还是“要给几分钟扩散时间”。

### 版本 C：条件切片版
把版本 A/B 按：
- no-jump vs jump
- no-FOMC vs FOMC window
- low-liq vs mid/high-liq

分层。

目的：检验论文里的条件结论，在 crypto perp 成本后是否仍成立。

## 7. 这条 alpha 最可能怎么死
1. **hour-pair 不稳定**：不同年份、不同 regime 下，最强 pocket 会漂移。
2. **低流动性 pocket 扣成本后变空**：论文说更强，不代表可成交后更好。
3. **伪交易日锚点选错**：24/7 市场里，切日方式本身就是模型参数。
4. **过拟合 hour-pair 网格**：24×24 组合很多，若不做滚动 OOS，很容易把噪音当 alpha。
5. **事件污染**：宏观公告、ETF 流、链上突发消息可能把“慢扩散/过度反应” pocket 瞬间改写成 news regime。

## 8. 结论
这篇 2022 论文最值得带回 desk 的，不是“crypto 也有 intraday anomaly”这句废话，而是这句更能交易的话：

**在 24/7 crypto 里，同日内可交易关系既有 continuation，也有 reversal；正确单位不是单一时钟效应，而是稳定的 hour-pair pocket。**

因此，这个主题值得进入 raw alpha 素材池，而且优先级不低：
- 它可独立复现；
- 只要分钟线就能开测；
- 与现有 funding / pairs / microstructure 线条相关但不重复；
- 最自然的下一步，就是做 `hour-pair mining + short-cycle execution transfer`。

如果这轮只做一个最小实验，我建议直接做：

**`BTCUSDT perp × UTC 伪交易日 × 1h predictor → 15m execution`，先找 60d rolling 下最稳定的 continuation pocket 与 reversal pocket 各 1 个。**

## 9. 来源
1. Wen, Zhuzhu; Bouri, Elie; Xu, Yahua; Zhao, Yang (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both*. **The North American Journal of Economics and Finance**, Vol. 62, Article 101733. DOI: `10.1016/j.najef.2022.101733`
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S1062940822000833
   - Abstract / metadata mirror: https://ideas.repec.org/a/eee/ecofin/v62y2022ics1062940822000833.html
   - Repo URL: 未找到公开官方仓库（截至 2026-03-30）

2. IDEAS / RePEc abstract page（用于交叉核对摘要、作者、期刊、DOI）
   - https://ideas.repec.org/a/eee/ecofin/v62y2022ics1062940822000833.html

3. ScienceDirect article page section snippets（用于核对方法、section 结构、timing strategy 描述）
   - https://www.sciencedirect.com/science/article/pii/S1062940822000833
