# 别把 Fieberg et al. 的 CTREND 只读成“周频因子论文”：对 short-cycle crypto desk，更该先回答的是「多时域技术状态聚合，迁到 `5m/15m` liquid majors 后还能不能剩下横截面 raw alpha」
- 时间：2026-04-21 04:05 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：把不同期限的价量技术指标压成一个横截面总分，做多技术状态最强的一篮子、做空最弱的一篮子，赚的是 **cross-sectional trend / relative-strength spread**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / cross-sectional / relative-value / trend / momentum / technical-indicators / feature-aggregation / 5m / 15m / Binance / paper / public-data
- 证据类型：论文全文 audit（open-access PDF）+ Binance USDⓈ-M public-data portability probe（curated liquid majors, `5m/15m`）

## 1. 先回答最重要的一句：这篇东西的 base alpha 是什么？
这篇东西的 **base alpha** 不是“技术分析有用”这种空话，也不是单一 RSI / MACD 规则。

它真正的 base alpha 是：**横截面技术强弱排序**。更直白地说，**同一时点把所有币放在一起比较，把多个期限上的价格趋势、均线位置、量能状态、波动扩张压成一个总分，然后多最强、空最弱。**

所以它属于：
- `主题类型：raw alpha`
- 更细分地说是：`cross-sectional / relative-value / trend / momentum`

## 2. 这次看了什么
看的是 Fieberg, Liedtke, Poddig, Walker, Zaremba 的 **A Trend Factor for the Cross Section of Cryptocurrency Returns**。

这篇论文最值得 desk 看的，不是“又发现一个 crypto 因子”，而是它把一个很实用的问题系统化了：

> 单个技术指标都很 noisy，那能不能别赌某一个指标，而是把多个期限、多个维度的技术状态拼成一个横截面排序器？

作者的做法很像“技术分析版的特征聚合器”：
- 输入不是 1 个指标，而是 `28` 个技术信号；
- 覆盖 momentum oscillators、moving averages、volume indicators、volatility indicators；
- 再用 cross-sectional Fama-MacBeth + combined elastic net 之类的方法，把这些 noisy 特征合成一个 **CTREND** 分数；
- 每周按 CTREND 排名分组，做多最高组、做空最低组。

对 short-cycle desk 真正重要的启发不是“照搬周频回测”，而是：

**能不能把“多时域技术状态聚合”这件事，压缩成适合 `1m/3m/5m/15m` 的横截面 router / alpha scorer？**

## 3. 论文里最硬的结果，翻成人话
论文原始样本是 `2015-04 ~ 2022-05`、超过 `3,000` 个币，主结论相当硬：

1. **主 long-short 组合平均周收益约 `3.87%`**
   - 不是只对单个币有效，而是横截面 top-vs-bottom 的 spread。

2. **交易成本打折后仍然活着**
   - 论文 Table 9 里，long-short 组合在较高成本假设下，净周收益仍约 `2.35%`，`t-stat ≈ 3.16`。
   - break-even transaction cost 约 `1.41%`。

3. **不只是小币角落里的错价**
   - 就算只看最大/最活跃币，效应仍在。
   - largest 100 那组，gross long-short 约 `3.40%/week`；高成本下净收益仍约 `1.90%/week`。

4. **不是传统 crypto momentum 因子的换皮**
   - 论文里 CTREND 会把原本的 `CMOM` 逼到不太重要，说明它抓到的不只是“过去几周涨过”。

5. **横截面回归里也站得住**
   - Table 4 里 CTREND slope 大约 `2.36`，`t-stat ≈ 5`。

翻成人话：

**论文不是在说“某个技术指标神了”，而是在说“把多个技术状态拼起来做横截面排序，本身就是一个强 raw alpha”。**

## 4. 为什么它和当前项目有关
这条线和当前 desk 的关系很直接，因为它补的是一类我们必须持续积累的素材：

- 不是单资产形态，而是 **cross-sectional raw alpha**；
- 不是只看 return，而是 **价 + 量 + 波动 的多特征聚合**；
- 不是单一 entry trick，而是 **统一打分 / 排序 / router**；
- 以后无论你做 trend、breakout、funding、OI、pairs，都可能需要一个“同一时刻该做谁、不该做谁”的评分层。

所以这篇论文最值得拿来拆的，不是周频多空组合本身，而是：

**“多时域技术状态聚合分数”能不能成为 short-cycle desk 的 shared raw-alpha scorer。**

## 5. 我做了什么最小 portability probe
我没有装作已经把论文的全部 28 个指标和 machine-learning 管线一比一复刻到分钟级；那样会假精确。

我做的是一个诚实的 **CTREND-lite portability probe**：
- 市场：Binance USDⓈ-M perpetual
- 币池：手工挑的 `16` 个 liquid majors
  - `BTC, ETH, SOL, XRP, DOGE, BNB, ADA, LINK, AVAX, LTC, BCH, DOT, TRX, SUI, HBAR, AAVE`
- 周期：`15m` 与 `5m`
- 特征：
  - 多期限收益：`ret6 / ret24 / ret96`
  - 价格相对均线：`close / SMA(8,24,96) - 1`
  - 量能：`volume / vol_SMA24 - 1`
  - 波动扩张：`range / ATR24`
  - `RSI14`
- 聚合方式：每根 bar 做横截面 percentile rank，再把这些 rank 平均成 `cttrend_lite`
- 组合：每根 bar 做多 top3、做空 bottom3，观察 next `1` bar / next `3` bars spread

## 6. probe 结果：**周频论文很强，但 minute-level naive transfer 直接不过线**
### `15m` curated majors
- next `1` bar long-short：约 **`-0.49 bps`**，`t ≈ -1.23`
- next `3` bars long-short：约 **`-0.26 bps`**，`t ≈ -0.39`

### `5m` curated majors
- next `1` bar long-short：约 **`-0.68 bps`**，`t ≈ -2.92`
- next `3` bars long-short：约 **`-1.34 bps`**，`t ≈ -3.34`

## 7. 这说明什么
这轮结果很有价值，因为它帮我们排除了一个很容易自欺的方向：

**不能因为周频 cross-sectional CTREND 很强，就默认它缩到 `5m/15m` 后还会自动有效。**

更具体地说，当前结果说明：

1. **naive feature aggregation 不等于 short-cycle alpha**
   - 把一堆趋势/均线/量能特征直接做分钟横截面排序，在 liquid majors 上不但没赚到，甚至偏反向。

2. **分钟级可能存在更强的微观均值回归 / 过度拥挤修正**
   - 也就是说，“此刻看起来技术最强”的币，在 `5m/15m` 上未必继续跑，反而可能先被回吐。

3. **论文的主要 edge 很可能依赖更慢的持有期、更宽的币池、更多小币分散化，以及更接近周频的信息更新节奏**
   - 这不代表论文没用；代表它的 alpha 载体和我们桌面当前想打的频率不同。

4. **对 short-cycle desk，CTREND 更像一个待改造的 scorer，不是现成主信号**
   - 也就是说，先别把它当裸 `5m/15m` 主 alpha；更像一个上层 ranking / router 候选。

## 8. 对 desk 真正有用的改造方向
如果继续沿这条线往前做，我认为不要再做“更像论文”的机械复刻，而要做 **更像 short-cycle 交易的条件化改造**：

### 方向 A：把 CTREND 从主信号改成 router
服务对象：
- breakout alpha
- trend continuation alpha
- funding / OI shock alpha

做法：
- 只有当原始 alpha 本身触发时，才看 `cttrend_lite` 是否支持该方向；
- 不做裸 top-vs-bottom，而是做 **alpha × CTREND-confirmation**；
- 先测它有没有提升 hit-rate / adverse excursion。

### 方向 B：把它改成“慢状态 × 快触发”二层结构
- 慢层：`15m` 或 `1h` 聚合技术状态，定义 cross-sectional bias
- 快层：`1m/3m/5m` 只等 pullback、break、reclaim、liq shock 之类触发

这样更符合论文的精神：**CTREND 负责告诉你谁正处在更强技术状态里，不负责替你决定精确入场。**

### 方向 C：测试反向解释
既然当前 naive 排名在分钟级偏负，反而可以检查：

> “分钟级技术最强/最弱横截面”是不是更适合拿来做短窗 fade，而不是 continuation？

这条支线很值得测，因为它可能把论文提供的“状态压缩器”变成一个 **intraday overextension detector**。

## 9. 可复刻的最小实验
### 最小实验 1：CTREND-lite 作为 router，而不是裸 alpha
- Universe：top `20` liquid majors
- 主 alpha：任选一条已有可下单 raw alpha（例如 breakout / panic-bounce / OI shock）
- admission：仅保留与 `15m cttrend_lite` 同向且位于 top/bottom `30%` 的信号
- 看：
  - `net bps/trade`
  - `hit rate`
  - `MAE/MFE`
  - `signal count`

### 最小实验 2：慢分数 + 快执行
- 慢层：`15m` 计算 CTREND-lite
- 快层：`5m` 做 pullback entry 或 break-retest entry
- Exit：固定 `3/6/12` bars + ATR stop
- 看：到底是 **continuation** 还是 **fade** 更配这个分数

### 最小实验 3：直接检验“分钟级 strongest 是否该反着做”
- 每根 `5m` bar 排名 top3 / bottom3
- 比较：
  1. 顺势 top-vs-bottom
  2. 反转 top-fade / bottom-bounce
- horizon：next `1/3/6` bars
- 成本：先粗扣 round-trip `4~8bps`

## 10. 下一步怎么测
这是本轮最重要的落地点：

1. **不要继续做裸 `5m/15m` CTREND top-vs-bottom**
   - 当前结果已经说明这条最直接迁移路不值得优先继续烧时间。

2. **把 CTREND-lite 先降级成 ranking layer**
   - 去给现有 raw alpha 做 confirmation / veto / symbol selection。

3. **先测“它是 continuation scorer 还是 overextension scorer”**
   - 也就是同一份分数，同时测顺势版和反转版，不要预设结论。

4. **如果要更接近论文，再增加 two-speed design**
   - `1h/15m` 算慢状态，`5m/3m` 做 child entry。

5. **如果 two-speed 仍不过线，就把这条线归档为“周频有效、短周期不直通”的 literature lesson**
   - 这同样有研究价值，能避免后面重复踩坑。

## 11. 风险与保留意见
- 我这轮做的是 **CTREND-lite**，不是论文 `28` 指标 + 完整 combined elastic-net 的一比一复刻；所以不能把 probe 负结果误读成“论文是错的”。
- 但这不影响 desk 判断：**当前这条 raw alpha 不能直接按分钟级裸迁移。**
- 论文样本覆盖大量小币与更慢频率；而我们当前 probe 故意限制在 liquid majors + short-cycle，这个差异本身就是研究结论的一部分。

## 12. 来源与材料
### 论文来源
- Authors: Christian Fieberg, Gerrit Liedtke, Thorsten Poddig, Thomas Walker, Adam Zaremba
- Year: `2024`（Cambridge online-first）
- Title: *A Trend Factor for the Cross Section of Cryptocurrency Returns*
- Venue: *Journal of Financial and Quantitative Analysis*
- DOI: `10.1017/S0022109024000747`
- Readable URL: `https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/trend-factor-for-the-cross-section-of-cryptocurrency-returns/4C1509ACBA33D5DCAF0AC24379148178`
- PDF URL: `https://www.cambridge.org/core/services/aop-cambridge-core/content/view/4C1509ACBA33D5DCAF0AC24379148178/S0022109024000747a.pdf/a-trend-factor-for-the-cross-section-of-cryptocurrency-returns.pdf`
- Repo URL: `N/A`

### 本轮产物
- `research/quant_digests/2026-04-21_0405_cttrend-xs-techstack-alpha.md`
- `reports/artifacts/quant_digests/cttrend_lite_majors_15m_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/cttrend_lite_majors_15m_detail_2026-04-21.csv`
- `reports/artifacts/quant_digests/cttrend_lite_majors_5m_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/cttrend_lite_majors_5m_detail_2026-04-21.csv`
- `reports/artifacts/quant_digests/cttrend_lite_majors_meta_2026-04-21.json`
