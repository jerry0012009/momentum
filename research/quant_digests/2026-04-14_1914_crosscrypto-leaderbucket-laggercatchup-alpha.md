# 别把这篇 2024 *JEDC* 只读成“crypto 也有 lead-lag”：对 short-cycle desk，更该先拆的是「leader-basket shock × lagger catch-up ranking」这条 cross-sectional raw alpha

- 时间：2026-04-14 19:14 UTC
- 类型：2024 *Journal of Economic Dynamics and Control* 论文正文可读页（ScienceDirect article page）+ Binance USDⓈ-M `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**高注意力 leader 币会更快吸收共同冲击；当 leader-basket 先动后，反应较慢的 lagger 币在下一小段时间里更容易补涨/补跌。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/relative-value/lead-lag/information-spillover/leader-lagger/catch-up/ranking/binance-perpetual/5m/15m/paper/public-data/cost/risk
- 证据类型：paper article-page full text snippet + public-data first verdict

## 1. 这次看了什么
主来源是这篇 paper：
- **Authors：** Li Guo, Bo Sang, Jun Tu, Yu Wang
- **Year：** 2024
- **Title：** *Cross-cryptocurrency return predictability*
- **Venue：** *Journal of Economic Dynamics and Control*, Volume 163, 104863
- **DOI：** <https://doi.org/10.1016/j.jedc.2024.104863>
- **Readable URL：** <https://www.sciencedirect.com/science/article/pii/S0165188924000551>
- **Repo URL：** N/A

这篇 paper 最容易被读成一句很抽象的话：

> “不同 crypto 之间存在 return predictability。”

但对 short-cycle desk，真正该拿走的不是这个 headline，而是一条更可执行的 raw alpha：

> **当共同冲击先被 BTC / BNB / TRX 这类高注意力 leader 吸收后，其他 lagger 币往往不会同一拍完全反应，下一拍更容易走 catch-up。**

翻成人话：
- 不是赌“某个币自己会反转还是延续”；
- 而是赌“市场里反应快的那一批已经先动了，反应慢的那一批会补动作”；
- 更像 **cross-sectional / relative-value lead-lag**，不是单腿裸方向。

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = common-shock information spillover。**

也就是：
- 市场出现共同信息冲击时，leader coins 先反应；
- lagger coins 因为注意力/信息处理更慢，下一拍才跟上；
- 于是可以做一个 **leader→lagger 的短周期 catch-up 排名策略**。

所以它是：
- `raw alpha`
- 不是 `filter`
- 不是 `regime overlay`
- 也不是单纯的 `risk veto`

## 3. paper 里最值得 desk 记住的，不是“LASSO 很厉害”，而是这 5 个硬点

### 3.1 样本就是高频 Binance，不是慢频概念文
paper 用的是 **Binance top 30 coins 的 minute-level 数据**，样本期 `2019-03-25 ~ 2021-04-30`；作者说这 30 个币在项目启动时覆盖了 **超过 86% 的总市场成交额**。所以它不是拿周频 / 日频硬讲短周期。

### 3.2 “别人上一分钟的收益”真的能预测“你这一分钟的收益”
author 在文中直接写到：
- 所有 30 个币的收益，都显著受其他币的 lagged returns 影响；
- pooled 口径下，**其他币 lagged return 每增加 1 个标准差，个体币当前分钟收益会增加 `0.40 ~ 4.82 bps`**。

翻成人话：
> **共同冲击不是所有币同一拍吃完。市场里真有“先动的币”和“后动的币”。**

### 3.3 真正的 top predictors 不是平均市场，而是 `BTC / BNB / TRX`
paper 的 adaptive LASSO 结果里：
- **BTC** 被选为几乎所有非稳定币的正向预测变量；
- **BNB、TRX** 也是高频出现的正向预测变量。

这点对 desk 很有用，因为它直接把“要盯谁”从泛泛的全市场相关性，缩成了一个可执行的 **leader set**。

### 3.4 论文不是只讲显著性，它真的做了 long-short 排名组合
作者按 forecast 做 quintile sorting，构建 zero-investment long-short portfolios：
- adaptive LASSO：**`3.34 bps / 分钟`** spread
- PCA：**`1.85 bps / 分钟`** spread
- BTC-only regression：**`1.54 bps / 分钟`** spread

而且文章明确说：
- returns 从 lowest quintile 到 highest quintile **单调上升**；
- 在 futures market、计入成本后，组合仍有统计显著收益；
- 文中举例：**半天训练窗、10 分钟换仓、regular taker `4 bps` 成本下，long-short 仍有 `0.34 bps`**，约等于 **每周 3%** 左右。

### 3.5 strongest version 发生在“共同冲击大”的时候
paper 还专门看了九类 broad market events，结论是：
- **event days 的 alpha 明显大于 normal days**；
- 解释是：共同事件带来更大的 common shocks，于是 cross-crypto predictability 更强。

这点非常重要，因为它告诉我们：
> **别把这条 alpha 读成“每根 bar 都机械轮转”，更像“冲击越大，lag diffusion 越明显”。**

## 4. desk 化之后，我觉得最该先测的不是全文 LASSO，而是这条更轻的 branch
我这轮没有去硬复刻 paper 的 30 币 minute-level adaptive LASSO；对当前 desk，更划算的是先抽出一个更轻、更能马上跑 `5m/15m` 的 branch：

> **`leader-basket shock × lagger catch-up ranking`**

### 4.1 我这轮的最小实验口径
- **市场：** Binance USDⓈ-M perpetual
- **数据源：** public `fapi/v1/klines`
- **公开性：** 公开可得
- **更新频率：** `5m / 15m`
- **样本：** 最近约 `30d`
- **universe：** `BTC, ETH, BNB, SOL, XRP, ADA, DOGE, LINK, LTC, TRX`
- **leader set：** `BTC + BNB + TRX`（直接来自 paper 的 top predictors）
- **tradable laggers：** `ETH, SOL, XRP, ADA, DOGE, LINK, LTC`
- **训练窗：** rolling `7d`
- **两种轻量 forecast：**
  1. `leader_trio`：用 leader-basket 的 lagged return 预测 laggers
  2. `pooled_others`：用“其他币平均 lagged return”预测个体币
- **交易方式：**
  - 每根 bar 对 laggers 做 forecast ranking
  - **long top 2 / short bottom 2**
  - 持有 `1` 根 bar
- **common-shock gate：** 额外测试 `|leader basket return| >= trailing 70% quantile` 的 admission 版本
- **成本阶梯：** 组合级粗口径 `2 / 4 / 8 bps` round-trip

### 4.2 本轮产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_crosscrypto_leadlag_probe.py`
- 汇总：`reports/artifacts/quant_digests/crosscrypto_leadlag_probe_summary_2026-04-14.csv`
- 明细：`reports/artifacts/quant_digests/crosscrypto_leadlag_probe_detail_2026-04-14.csv`
- beta snapshot：`reports/artifacts/quant_digests/crosscrypto_leadlag_probe_beta_snapshot_2026-04-14.csv`

## 5. first verdict：15m 比 5m 像样，但当前还只是 gross candidate，不是 production shell
### 先记 4 个最重要的数据点
1. **本轮最好的 pocket 是 `15m + pooled_others + common-shock gate`**：
   - `610` 次信号
   - **avg gross `+0.68 bps / rebalance`**
   - gross hit rate **`51.5%`**
   - 说明“共同冲击大时再做 lagger ranking”这件事，确实比无脑全时段轮动更对。  

2. **`15m` 明显优于 `5m`**：
   - `15m pooled_others ungated`：**`+0.53 bps`**
   - `15m leader_trio ungated`：**`+0.28 bps`**
   - `5m` 几个版本只有 **`+0.02 ~ +0.13 bps`**，基本说明在当前 Binance perp 口径下，**太快会被噪音和换手吃掉。**

3. **paper 的“event day 更强”在 desk 化版本里是能看到影子的**：
   - `15m pooled_others` 从 ungated 的 **`+0.53 bps`** 提到 gated 的 **`+0.68 bps`**；
   - 而 `5m` 上 gate 反而没明显改善，说明 **不是所有频率都适合同一 admission。**

4. **当前 still not over cost**：
   - 最好版本在粗扣 `2 bps` 后，平均也只剩 **`-1.32 bps`**；
   - 扣 `4 / 8 bps` 更是全灭；
   - 而且这还是组合级粗成本，不是 fill-aware multi-leg 成本，**真实落地只会更难。**

## 6. 为什么这轮值得进素材池
这轮值得收，不是因为它已经能直接上 production，而是因为它补的是一种**和 pairs / basis / funding 都不一样的 raw alpha 结构**：

1. **不是 spread 回归，而是信息扩散慢半拍。**  
   赚的是 leader 先动、lagger 后补，不是两个腿本来该有一个静态公平价差。

2. **天然服务 cross-sectional / relative-value book。**  
   不需要押整个市场方向，只要押“强 forecast laggers 跑赢弱 forecast laggers”。

3. **可以和现有素材池拼起来。**  
   这条 alpha 后面可以和：
   - liquidity / turnover veto
   - funding / OI crowding veto
   - session pocket
   - maker-first execution
   组合，而不是互斥。

4. **paper 给了一个很有用的 research hint：common-shock admission 比全时段硬轮动更重要。**

## 7. 策略拆解（必填）
- 方向属性：**cross-sectional / relative-value / lead-lag / market-neutral**
- 基础 alpha：**leader coins 对共同冲击反应更快，laggers 在下一拍做 catch-up**
- regime：**broad common-shock bar / event-like leader impulse 更强**
- filter / veto：**`|leader basket return|` 低于阈值不做；稳定币排除；只做 liquid majors / liquid alts**
- risk / sizing / execution overlay：**equal-weight top2-bottom2、1-bar hold、组合级 cost ladder、后续需补 multi-leg turnover / fill model**

## 8. 下一步怎么测
1. **把 `15m` 当主战场，先别继续往 `1m/3m` 硬压。**  
   当前 public first verdict 已经说明 `5m` 太容易被换手吃掉；下一轮优先测 `15m signal -> 5m execution`。

2. **把“共同冲击”从简单幅度门槛，升级成真正的 admission layer。**  
   下一轮可以把 gate 换成：
   - leader basket absolute return z-score
   - leader breadth（leaders 同向个数）
   - BTC / BNB / TRX 一致性

3. **加一个 lagger-side veto，而不是只盯 leaders。**  
   例如：
   - lagger 本币 funding/OI 已经极端时不追
   - lagger 自身近几根 bar 已经完成补动作时不再追
   这样能把“leader 真先动、lagger 真没跟上”的场景挑干净一点。

4. **把 forecast 从 rolling OLS 升级到轻量 sparse model，但别急着全量复刻论文。**  
   先试：
   - rolling LASSO
   - PCA + leader residual ranking
   - `leader_trio + pooled_others` ensemble
   不用一上来就抄 30 币全文机器学习 pipeline。

5. **补真实多腿成本。**  
   当前这条线最大的硬伤不是“完全没 gross”，而是 **gross 太薄**。下一步必须把：
   - top2/bottom2 多腿换手
   - maker/taker 混合成交
   - funding 与 basis side-effects
   真正算进去。

## 9. first verdict
我的判断是：

> **这篇 2024 *JEDC* 值得进 raw alpha 素材池，但不该被读成“再来一个抽象 lead-lag 论文”；更正确的 intake 方式是把它 desk 化成 `leader-basket shock × lagger catch-up ranking`。**

更短一点：

> **alpha 本体是信息扩散慢半拍；当前 `15m` 上还能看到一点 gross，但离完整 production shell 还差 admission、lagger veto 和真实多腿成本三道门。**

## 10. 来源
- Guo, L., Sang, B., Tu, J., & Wang, Y. (2024). *Cross-cryptocurrency return predictability*. *Journal of Economic Dynamics and Control*, 163, 104863.
  - DOI: <https://doi.org/10.1016/j.jedc.2024.104863>
  - Readable URL: <https://www.sciencedirect.com/science/article/pii/S0165188924000551>
  - Repo URL: N/A
- Local public-data probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-14_crosscrypto_leadlag_probe.py`
  - `reports/artifacts/quant_digests/crosscrypto_leadlag_probe_summary_2026-04-14.csv`
  - `reports/artifacts/quant_digests/crosscrypto_leadlag_probe_detail_2026-04-14.csv`
  - `reports/artifacts/quant_digests/crosscrypto_leadlag_probe_beta_snapshot_2026-04-14.csv`
