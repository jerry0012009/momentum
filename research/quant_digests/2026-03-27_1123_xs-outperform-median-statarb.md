# 别把这篇 2019 stat-arb 论文只当老派 ML demo：它真正值得 desk 先测的是「outperform-median 横截面多空」完整 raw alpha
- 时间：2026-03-27 11:23 UTC
- 类型：论文 + GitHub + Binance Futures 公共 `5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：横截面相对强弱延续——做多“未来 120 分钟最可能跑赢截面中位数”的币，做空最可能跑输的币
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/relative-value/stat-arb/market-neutral/random-forest/lagged-returns/minute-data/top-vs-bottom/binance/perpetual/5m/15m/paper/repo/external-data/cost
- 证据类型：论文证据 + repo 代码 + 公共数据快检

## 1. 这次看了什么
这次看的是 **Fischer, Krauss, Deinert (2019), _Statistical Arbitrage in Cryptocurrency Markets_**，外加作者公开的 GitHub 代码仓。它不是在讲某个单币 breakout，而是在做一条更像 desk 素材池缺口的东西：**minute 级横截面 market-neutral raw alpha**。

## 2. 核心结论
- **一句话核心结论：** 这篇东西的 base alpha 很清楚——不是“预测 BTC 涨跌”，而是**用全市场 lagged returns 去排出未来 120 分钟的相对赢家和相对输家，再做多 top、做空 flop**。
- **一句话它怎么证明：** 论文在 `40` 个币的 minute 数据上训练随机森林，目标是预测“某币未来 `120` 分钟是否跑赢截面中位数”，然后做 `top-3 / flop-3` 多空，给出独立样本回测结果。
- 论文摘要给的 headline 数字很硬：样本外区间 `2018-06-18 ~ 2018-09-17`，在 **超过 `100,000` 笔交易** 后，策略仍有 **`7.1 bps/day`** 的成本后收益；论文口径交易成本是 **`15 bps per half-turn`**。
- GitHub 仓库把“怎么复现”讲得比摘要更值钱：`crypto_forest_example.py` 明确用了 **`1~20` 分钟收益 + `120*x` 分钟收益（直到 `24h`）** 做特征；`feature_generator.py` 明确 target 是**未来窗口收益离散成 2 档**，本质就是“是否跑赢截面中位数”；`kpi_backtest.py` 还给了 **top/flop 组合、staleness filter、交易成本入口**。
- 我这里用 **Binance USDT 永续 top10、`5m` bar、120 分钟持有、top3/bottom3、轻摩擦占位成本** 做了最小 transfer check，`2026-03-12 ~ 2026-03-26` 的结果大约是 **`-20.8 bps/day`**，说明这条 alpha 不是拿来就能上，**近期迁移先不过线**。

## 3. 为什么和当前项目有关
这轮虽然不是近 5 年新文，但我还是把它插进来，原因很直接：**它是少数把 raw alpha、entry/exit、组合构造、成本接口、代码骨架一次性给全的 crypto 短周期 market-neutral 主题**。

对当前 desk，它的价值不在“再学一次随机森林”，而在于把一条可复刻主线说清楚：
- alpha 本体不是 breakout，也不是 pairs spread，而是 **cross-sectional winner-vs-loser ranking**；
- 组合层天然是 **market-neutral**，适合和当前单币 directional 素材池形成互补；
- 特征层极简，几乎全是 **lagged returns**，对 `1m / 3m / 5m / 15m` 都能快速落地；
- 即使 ML 版 transfer 暂时不活，也很容易拆出更便宜的 baseline：**plain return-rank / horizon-stacked momentum / top-bottom spread**。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / market-neutral
- 基础 alpha：未来 `120m` 截面相对强弱可由过去多窗口收益排序近似预测
- regime：更适合有足够横截面分化、币种间相关性未完全塌缩的时段
- filter / veto：staleness / 最低成交量 / 最低可交易币数 / 重大事件时段停机
- risk / sizing / execution overlay：等权 top-bottom、单币权重上限、sector cap、taker cost ladder、可改成 maker-first

## 4. 可复刻的最小实验
**研究假设：** 在 Binance/OKX 永续的 liquid universe 上，存在一条可被极简 lagged-return 排名近似复原的 `120m` 横截面 market-neutral alpha；若 paper 里的 RF 太重，简单线性/排序版也应先保留同方向雏形。

**最小实验：**
1. 取最近 `60~120d` 的 top `20~40` USDT perp，周期先做 `5m`，再平移到 `15m`。
2. 每个 bar 计算 `1~12 bar`、`24 bar`、`48 bar`、`96 bar` 收益；先不上复杂因子。
3. 目标定义成：未来 `24` 个 `5m` bar（或未来 `8` 个 `15m` bar）是否跑赢当期截面中位数。
4. 先跑三档模型：`plain return rank` / `logit` / `RF`；组合统一成 `long top3, short bottom3, hold 120m`。
5. friction ladder 至少跑 `4 / 8 / 12 bps round-trip`，再看净值、换手、正收益日占比。

## 5. 我对这条线的当前判断
这条线**值得进研究池，但暂时不该直接进 admission**。原因不是 paper 不清楚，而是我这次 public `5m` quick check 已经先给了一个冷水：**近期 Binance perp 迁移为负**。所以它更像：
1. 一条很好的 **横截面 market-neutral 原型母体**；
2. 一个适合拿来做 **plain-vs-ML / 5m-vs-15m / spot-vs-perp / top3-vs-top5** 的标准化对照组；
3. 如果后续继续失败，就该把结论写死成：**minute 级 XS stat-arb 在 2026 更可能需要更强的 universe/成本/执行约束，不能把 2018 的 edge 当常量。**

## 6. 来源与可复用材料
1. **Fischer, T., Krauss, C., & Deinert, A. (2019). _Statistical Arbitrage in Cryptocurrency Markets_. Journal of Risk and Financial Management, 12(1), 31.**  
   DOI：<https://doi.org/10.3390/jrfm12010031>  
   Readable URL：<https://cris.fau.de/publications/216708387/>
2. **作者公开代码仓：Statistical-arbitrage-in-cryptocurrency-markets**  
   Repo URL：<https://github.com/Exceluser/Statistical-arbitrage-in-cryptocurrency-markets>
3. **本地最小快检笔记**  
   Artifact：`reports/artifacts/tmp_stat_arb_rf_5m_summary.txt`
