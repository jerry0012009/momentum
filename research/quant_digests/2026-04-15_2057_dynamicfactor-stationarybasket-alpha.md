# 别把这篇 2021 动态因子 pairs 论文只读成“cointegration 说明文”：对 short-cycle desk，更该先拆的是「stationary factor forecast × top-vs-bottom basket long-short」这条 raw alpha

- 时间：2026-04-15 20:57 UTC
- 类型：2021 *Decisions in Economics and Finance* 论文全文 PDF（本地抽取）+ Springer article page + Binance USDⓈ-M `15m` public-data fast portability probe
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/basket/market-neutral/dynamic-factor/cointegration/stationary-factor/integrated-factor/top-vs-bottom-ranking/no-trade-band/regime-gate/binance-perpetual/btc-eth-ltc-xrp/15m/paper/fulltext/public-data/cost/risk
- 证据类型：论文全文 + 元数据/可读页 + 公共数据 fast portability probe

- 主题类型：raw alpha
- 基础 alpha：**同一 crypto basket 里，绝大部分共同涨跌可看成一个 integrated 市场因子；真正可交易的，是第二个 stationary 相对价值因子的短期均值回复。交易上不是赌大盘方向，而是按该因子的下一步预测，把“相对偏贵”的半边做空、“相对偏便宜”的半边做多。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么

这轮选的是一篇 **明确属于 raw alpha / pairs / stat-arb** 的论文，而不是再绕回 filter 或结构解释：

- **Gianna Figà-Talamanca, Sergio M. Focardi, Marco Patacca (2021)**
- **Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages**
- *Decisions in Economics and Finance*
- DOI：<https://doi.org/10.1007/s10203-021-00318-x>
- Readable URL：<https://link.springer.com/article/10.1007/s10203-021-00318-x>
- PDF：<https://link.springer.com/content/pdf/10.1007/s10203-021-00318-x.pdf>
- Repo URL：N/A

这篇东西最容易被一句话误读成：

> “又一篇 cointegration / pair trading 论文，而且还是日频老币篮子，离 `5m/15m` 很远。”

如果只看标题，这种误读很自然；但对当前 desk，更值钱的不是“cointegration 这三个字”，而是它把 basket long-short 讲清楚的方式：

> **先把全市场共同涨跌剥成一个 integrated market factor，再盯住第二个 stationary relative-value factor 的下一步预测；交易上做的是 basket 内 top-vs-bottom 的多空重排，而不是只盯某一对 spread 的 z-score。**

这就让它和最近已写过的一堆 `pair admission × spread fade` 有了明确区分：

- 不是“先挑 pair，再做单条 spread”
- 而是“先建 basket factor，再把 basket 内多空半边同时排出来”
- 还自带一个很实用的 **regime gate**：只有第二因子仍 stationary、且两个因子相关性不高时才交易

## 2. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = stationary relative-value factor mean reversion inside a crypto basket.**

翻成人话：

- `BTC/ETH/LTC/XMR` 这些币一起涨跌时，里面有一大块只是“市场一起动”；
- 真正能拿来做市场中性交易的，是剥掉共同市场因子后，剩下那条**会往回收敛**的相对价格因子；
- 当这条 stationary 因子暗示某些币“相对偏贵”、另一些“相对偏便宜”时，
  就做：
  - **short 预测更贵的半边**
  - **long 预测更便宜的半边**
- 下一步相对排序回归时，组合赚钱。

所以它是：

- `raw alpha`
- 不是纯 `filter`
- 不是纯 `regime`
- 也不是单独的 `overlay`

这里的 `stationary factor gate` 很重要，但那是**保护这条 raw alpha 的交易条件**，不是 alpha 本体。

## 3. 来源与本轮本地 artifacts

### 主来源（paper）
- **Authors：** Gianna Figà-Talamanca, Sergio M. Focardi, Marco Patacca
- **Year：** 2021
- **Title：** *Common dynamic factors for cryptocurrencies and multiple pair-trading statistical arbitrages*
- **Venue：** *Decisions in Economics and Finance*, 44, 863–882
- **DOI：** <https://doi.org/10.1007/s10203-021-00318-x>
- **Readable URL：** <https://link.springer.com/article/10.1007/s10203-021-00318-x>
- **PDF URL：** <https://link.springer.com/content/pdf/10.1007/s10203-021-00318-x.pdf>
- **Repo URL：** N/A

### 本轮本地 artifacts
- Full-text extract cache：`/tmp/s10203-021-00318-x.txt`
- Fast probe script：`reports/artifacts/quant_digests/2026-04-15_dynamicfactor_basket_probe_fast.py`
- Fast probe trades：`reports/artifacts/quant_digests/2026-04-15_dynamicfactor_basket_probe_fast_trades.csv`
- Fast probe summary：`reports/artifacts/quant_digests/2026-04-15_dynamicfactor_basket_probe_fast_summary.json`

## 4. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这篇 paper 最该给 desk 留下的，不是“crypto 也能 cointegration”，而是“stationary factor forecast 可以直接转成 basket 内 top-vs-bottom market-neutral long-short，而且第二因子一旦不再 stationary，就该主动停手”。**

### 一句话证明方式
> **论文在 2019 日频滚动窗口上，对 `BTC/ETH/LTC/XMR` 估计 2-factor 动态模型：前期是一条 integrated 因子 + 一条 stationary 因子；按 rescaled-price forecast 排序做多低半边、做空高半边，并在加入交易费后发现 `c=0.20` 的 no-trade band 最优。我的 `15m` fast transfer（Binance USDⓈ-M, `BTC/ETH/LTC/XRP`，PCA proxy 而非完整 MLE DFM）显示：直接翻成高频连续轮动后 gross 只剩约 `+0.20 bps/笔`，4bps round-trip 后明显转负，所以真正该先迁移的是“stationary-factor alpha + threshold/no-trade band + regime gate”这整套骨架。**

## 5. 论文里真正值得 desk 记住的点

## 5.1 它不是“单 pair spread z-score”，而是 **basket 排序型 long-short**
论文先把价格写成：

- 一个 **integrated** 的共同市场因子 `f1`
- 一个 **stationary** 的相对价值因子 `f2`
- 再加 idiosyncratic 残差

然后把每个币做 rescale：

`p*_i,t = p_i,t / beta_i1`

这样处理后，不同币之间的相对差主要就由第二因子 `f2` 驱动。

真正关键的交易翻译是：

1. 先预测下一步 `f2`
2. 用它生成每个币的 **scaled forecast rank**
3. **做空 forecast 更高的半边**
4. **做多 forecast 更低的半边**
5. 下一步就平

也就是：

> **alpha 不是“某一对币的 spread 回不回”，而是“basket 内谁相对贵、谁相对便宜”的下一步重排。**

这比 plain pairs 更像一个可扩展母板：

- 你可以从 2 个 pair 扩到 4~12 个 liquid majors
- 可以加 admission / conflict netting
- 可以把 `stationary factor` 既当信号源，也当 regime gate

## 5.2 论文其实给了完整策略骨架，不只是概念文
这篇 paper 不是只讲经济学叙事，它把完整交易骨架写出来了：

- **估计窗口：** 过去 3 年滚动窗口
- **交易资产：** `BTC / ETH / LTC / XMR`
- **测试窗：** `2019-01-01` 到 `2019-11-30`
- **预测：** 一步 ahead forecast
- **方向：** long bottom half / short top half
- **no-trade 条件：** 当 forecasted basket value 与当前 basket value 的差不够大时不动
- **threshold：** `c * σ_v`
- **risk / regime gate：** 若第二因子不再 stationary，或两个因子相关性太高，则不交易
- **费用口径：** Coinbase maker fee `0.10%`

这已经不是“可以想象怎么下单”的程度，而是：

> **entry / exit / sizing / no-trade band / cost / regime stop 都有了。**

所以字段里我把“是否可直接落地完整策略”记成 **是**。

## 5.3 论文最实用的一点：**费后最优不是一直交易，而是少做一点**
论文 Table 6 的信息很重要，因为它非常贴近今天 short-cycle 研究常见的失败原因：

- 不加 threshold（`c=0`）时，交易次数最多：**252** 次
- 加了 no-trade band 以后，交易次数下降
- **费后最优** 出现在 `c=0.20`
  - 交易数：**222** 次
  - mean net cumulative gain：**3032.97**
- 再把 `c` 提太高，交易数继续掉，收益也跟着掉

翻成人话就是：

> **这条 alpha 不是“越勤奋越好”，而是“有 edge，但必须让 forecast edge 够厚再动手”。**

这和我们最近大量 short-cycle portability probe 的结论是一致的：

- structure 往往还能看到
- 但如果没有 admission band / cost-aware throttle
- 高换手会先把你磨死

## 5.4 它还给了一个很像实盘 kill-switch 的 regime 线索
论文明确指出：

- 到 **2019 年 8 月下旬之前**，第二因子大致还是 stationary
- 之后更像变成了 **两个 integrated 因子**
- 这时原本的 market-neutral 假设不再成立
- 论文也就不建议继续交易

这是一个很好的提醒：

> **pairs / basket stat-arb 不是“找到一次 cointegration 就永远有效”，而是要持续检查“相对价值因子还在不在、还稳不稳”。**

对当前 desk，很自然的迁移就是把它变成：

- `stationary factor alive?`
- `factor correlation too high?`
- `forecast edge > threshold?`

三个开仓前检查项。

## 6. 为什么这轮值得进当前研究池

## 6.1 它补的是最近素材池里相对少的一块：**basket-factor stat-arb**
近期 pairs / stat-arb digest 很多，但大部分还是：

- pair admission
- hedge ratio
- z-score fade
- half-life 筛选
- cointegration / percentile band

这篇补的是另一个方向：

> **用公共 market factor + stationary relative-value factor 的拆法，直接把 signal 提升到 basket 排序层。**

这能服务的不只是一个 pair，而是一整个 basket long-short 壳。

## 6.2 它和 short-cycle desk 直接相关，但不会假装自己是“现成 15m 印钞机”
诚实说，这篇 paper 本体是：

- 日频
- 老币篮子
- 低换手

所以不能装作“直接抄成 `15m` 就能上”。

但它对我们现在仍有价值，因为它补的是：

- 一条清楚的 **raw alpha 结构**
- 一个清楚的 **regime gate**
- 一个清楚的 **threshold/no-trade band 思路**

这些恰好是把 many-pair spread fade 往更可控 basket shell 推进时最缺的模块。

## 7. 我这次怎么做 fast portability probe

## 7.1 probe 口径
我没有去完整复刻 paper 的 MLE 动态因子估计，而是做了一个 **快而诚实的 transfer check**：

- **市场：** Binance USDⓈ-M perpetual
- **频率：** `15m`
- **样本：** 近 `45d`
- **资产：** `BTCUSDT / ETHUSDT / LTCUSDT / XRPUSDT`
- **训练窗：** `7d` rolling
- **模型代理：** PCA 两因子 proxy（不是 paper 原始的完整 DFM）
- **信号翻译：**
  1. 用 2-factor proxy 分解 basket
  2. 估计第二因子下一步 forecast
  3. 按 `alpha_i / beta_i1 + (beta_i2 / beta_i1) * E[f2_{t+1}]` 排序
  4. **long bottom 2 / short top 2**
  5. 持有 `1 bar`
- **gate：**
  - factor2 使用一个简化的 stationarity-like gate
  - `|corr(f1, f2)| < 0.18`
- **费用：** 先粗扣 `4 bps` round-trip

## 7.2 为什么这样做
目标不是“证明论文原样可搬到 15m perp”，而是先回答更重要的问题：

1. **这个 factor-sorted basket alpha 骨架，在今天短周期上还有没有方向感？**
2. **如果没有 no-trade band，只做持续轮动，会不会马上死于费用？**

## 8. 关键结果：结构能看到，但直接高频轮动明显 cost-dead

Fast probe summary（`2026-04-15_dynamicfactor_basket_probe_fast_summary.json`）：

- 样本 bars：**3648**
- 触发 bars：**3348**（trade rate **91.8%**）
- gross 平均：**+0.20 bps / 笔**
- gross 命中率：**50.4%**
- gross 累计：**+665.7 bps**
- 扣 `4 bps` round-trip 后：
  - net 平均：**-3.80 bps / 笔**
  - net 命中率：**23.0%**
  - net 累计：**-12726.3 bps**

这组数字的价值不在于“它还能不能直接上”，而在于把 paper 的可迁移部分和不可迁移部分分开了：

### 8.1 可迁移部分
- `stationary factor` 作为 relative-value signal source
- `top-vs-bottom basket ranking`
- `factor alive / not alive` 作为 regime gate

### 8.2 不能直接照抄的部分
- **无门槛连续轮动**
- **把低频 edge 当高频 edge 直译**
- **忽略 threshold / turnover throttle / maker 化路径**

翻成人话：

> **不是这条 alpha 不存在，而是“每根 15m 都做”的版本太勤了，厚度完全不够付路费。**

这反而更支持 paper 里最值钱的那个迁移点：

> **`c * σ_v` no-trade band 不是修饰，而是这条 alpha 能不能活下来的核心。**

## 9. 对当前 desk 的正确读法

我会把它读成：

### 9.1 alpha 本体
- **stationary-factor forecast × basket re-ranking**
- 这是 raw alpha

### 9.2 必需配件
- stationarity gate
- factor correlation gate
- no-trade band / edge threshold
- cost-aware throttle

### 9.3 更像当前 desk 的落地方式
对 `5m/15m` 更合理的第一版不是“全时间连续 top-bottom 轮动”，而是：

1. 先在 `6~12` 个 liquid majors 上做 rolling 2-factor / 3-factor proxy
2. 只保留 **score spread 进入 top decile / top quintile** 的时刻
3. 只做 **最极端的 1~2 long + 1~2 short**，而不是每次都全篮子都动
4. 对比：
   - `c=0`
   - `c=0.2`
   - `c=0.5`
5. 再跑 `1 / 2 / 4 bps` 费用阶梯

也就是先把它从：

- “连续轮动排序策略”

缩成：

- “只有 edge 足够厚时才开的 basket MR alpha shell”

## 10. 下一步怎么测

这是这轮最重要的落地建议：

### 最小实验 A：把 paper 的 `cσ_v` band 真正搬到 `15m`
- **宇宙：** `BTC/ETH/SOL/XRP/LTC/BNB/DOGE/ADA`
- **频率：** `15m`
- **训练窗：** `3d / 7d / 14d` 对照
- **因子：** first PC 视作 market factor，second factor 视作 relative-value factor
- **交易：**
  - long bottom `k`
  - short top `k`
  - `k = 1 or 2`
- **admission：**
  - `forecast_edge > c * rolling_sigma_v`
  - `c ∈ {0, 0.2, 0.5, 1.0}`
- **评估：**
  - gross / net bps per trade
  - turnover
  - edge per unit turnover
  - gate pass rate

### 最小实验 B：把 “factor alive?” 单独拎成 shared gate
即使最终不直接采用它的 basket 排序，也可以把：

- `factor2 stationary?`
- `|corr(f1,f2)| low enough?`

单独接到已有的：

- pairs spread fade
- residual MR
- basket residual fade

去看它是不是一个 shared regime veto。

### 最小实验 C：只保留最极端时刻
当前快检里 trade rate 高达 **91.8%**，这基本已经宣布“连续开仓不现实”。
下一步应先做：

- score spread top `10% / 5% / 2%`
- 只在最极端分位开仓
- 对照 hold `1 / 2 / 4 bars`

如果这一步都抬不起厚度，就说明这条东西更适合当：

- `shared gate`
- 或 `basket construction lens`

而不是直接做主 alpha。

## 11. 最终判断

### 11.1 研究结论
> **值得收进研究池，而且应归类为 raw alpha；但现阶段最值钱的不是“照抄日频多空排序”，而是把它拆成 `stationary-factor alpha + threshold/no-trade band + regime gate` 这套可迁移骨架。**

### 11.2 对 short-cycle 的一句话 verdict
> **直译成 `15m` 连续轮动版，first verdict 明显 cost-dead；但如果你正想把现有 pairs / basket MR 从“看 z-score 就上”升级成“先问 factor 还活不活、edge 够不够厚”，这篇 paper 很值得保留。**
