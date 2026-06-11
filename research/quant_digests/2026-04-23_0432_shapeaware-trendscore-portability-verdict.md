# 别把 Jiang–Kelly–Xiu (2023) 只读成“价格图喂给机器学习”的长周期选股论文：对 short-cycle crypto desk，更该先回答的是「path smoothness × trend continuation」这条 raw alpha 到底比裸 momentum 多了什么
- 时间：2026-04-23 04:32 UTC
- 类型：2023 *Journal of Finance* 论文 metadata / abstract audit（Crossref + OpenAlex）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m` parent，近约 `23d`）
- 主题类型：raw alpha
- 基础 alpha：不是所有“过去涨了”的走势都一样；**更平滑、更单调、更像“有结构的趋势路径”** 的那类过去走势，对未来延续更有信息量
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / trend / momentum / shape-aware / path-smoothness / cross-sectional / 15m / 5m / paper / public-data / cost / risk
- 证据类型：论文摘要证据 + public-data portability probe

## 1. 这次看了什么
看的是 **Jiang, Kelly, Xiu (2023), *(Re-)Imag(in)ing Price Trends***。这篇文的学术主轴是：别只拿固定的 momentum / reversal 规则测价格可预测性，而是直接把**价格路径本身**当输入，让更灵活的方法去找“哪种走势形状”最能预测未来收益。对我们 desk 来说，最值得先拆的不是“图像模型”本身，而是它背后的朴素想法：**趋势不只是过去收益大小，还包括这段路是怎么走出来的。**

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**同样是上涨 1%，如果一条路径是平滑、单调、少回撤地爬上去，另一条是来回乱甩后勉强涨到 1%，前者更像真趋势，后者更像噪音。**
- 对 short-cycle crypto desk，最自然的可移植版本不是 CNN 识图，而是先做一个 **shape-aware trend score**：把最近 `L` 根 K 线的总收益，与“这条路径有多直、有多顺”结合起来，而不是只看裸 return。
- 我做了一个最小 portability probe：在 Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/AVAX` 上，用 `15m` bars 构造 `shape score = sign(ret) × |ret| × R²`（`R²` 来自最近路径对时间的线性拟合，表示“走得有多像一条直线”），然后跟 plain momentum 做并排对照。
- 结果并不亮眼，但信息很有用：在近约 `23d` 样本里，**shape-aware 版本大多只比 plain momentum 略好一点点，远谈不上成本后可交易。** 例如 `lookback=8 bars, hold=1 bar, top1 long` 时，shape 约 `-0.10 bps/次`，plain momentum 约 `-0.13 bps/次`；`lookback=8, hold=2` 时 shape 约 `-0.38 bps/次`，plain 约 `-0.43 bps/次`；`top1-bottom1 long-short` 也只是 `-0.63 vs -0.68 bps/次`。
- 一句话核心结论：**“路径形状”这个想法有信息，但在我们当前 `15m` liquid majors 直推口径里，它最多只是让裸 momentum 少亏一点，还没有独立长成可交易 raw alpha。**
- 一句话证明方式：**论文给了“走势形状可能比固定指标更有预测力”的母想法，我再把它压成一个不用图像模型也能快速复现的 path-smoothness 代理，与 plain momentum 在公开 Binance 数据上做正面对照。**

## 3. 为什么和当前 desk 有关
它直接回答了一个很现实的问题：为什么很多 intraday momentum 看起来“方向对”，做出来却没 edge？原因可能不是方向逻辑完全错，而是**我们把“有趋势的涨”与“噪音里的涨”混在一起了**。这篇 paper 提醒我们：趋势信号不该只回答“涨了多少”，还该回答“这段涨法像不像趋势”。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / cross-sectional relative-strength
- 基础 alpha：平滑、单调的近期路径比锯齿噪音路径更可能延续
- regime：更适合趋势展开期；若路径顺滑度低、振荡高，则应降权或 veto
- filter / veto：`R²`、回撤深度、路径单调性、波动压缩/扩张状态
- risk / sizing / execution overlay：`15m` 产方向分数，`5m` 做 child execution；可配合成本阈值、maker-first、持有期上限与同向拥挤度约束

## 4. 可复刻的最小实验
- 研究假设：在同样的过去收益下，**shape 更“顺”的路径** 比裸收益本身更能预测下一段延续。
- 一个可计算定义：最近 `L=8` 根 `15m` K 线，计算总收益 `ret`；再对 `log(price)` 与时间做线性拟合，取 `R²` 代表“路径顺滑度”；构造 `shape_score = sign(ret) × |ret| × R²`。
- 最小回测切口：8 个 liquid majors 上，每根 `15m` bar 对 `shape_score` 排名，先做 `top1 long`、`bottom1 short`、`top1-bottom1 long-short` 三种最小壳；child execution 以后再下沉到 `5m`。
- 最该先看哪 1~2 个指标：**shape 相对 plain momentum 的增量 bps**、**增量是否能覆盖最基本 round-trip friction**。如果连增量都接近 0，就别急着上更复杂模型。

## 5. 当前 verdict 与下一步怎么测
### 当前 verdict
- 这条线 **不是无效**，因为 shape proxy 在多个配置里都比 plain momentum 略好一点；
- 但它 **也远没到可直接交易**，因为当前增量只有零点几 bps 量级，根本不够吃成本。

### 下一步怎么测
1. **别先上 CNN**，先把代理做厚：在 `R²` 之外，加上 `max drawdown in lookback`、`signed autocorr`、`monotonic up-bar ratio`、`path efficiency`，看“多维 shape score”能不能明显拉开与 plain momentum 的差距。  
2. 从 cross-sectional 排名改成 **single-asset router**：只在 `shape_score` 进入最强分位时交易，避免把弱趋势样本硬塞进组合。  
3. 把 parent `15m` 信号下沉到 `5m` 执行，单独测试 **maker-first / next-open / VWAP child** 三种执行口径；这类薄 edge 很可能死在执行，不死在方向。  
4. 如果 shape 只在趋势市场里略有增量，就明确把它降级成 **trend-quality filter**，服务于已有 momentum / breakout，而不是强行把它当独立 alpha。

## 6. 风险与保留意见
- 我这轮只有论文 metadata / abstract，没拿到全文细节；因此当前更像是**基于论文主张做的 desk-oriented proxy replication**，不是 paper 原方法复刻。
- `R²` 只是“形状信息”的一个很粗代理，不等于 paper 里的 image-based learning；当前 negative verdict 只能说明**这个粗代理不够厚**，不能反证 paper 主结论本身。
- 样本只覆盖近约 `23d` 的 liquid majors，属于 first verdict，不是最终结论。

## 7. 来源
- Jiang, G. J., Kelly, B., & Xiu, D. (2023). *(Re-)Imag(in)ing Price Trends*. *Journal of Finance*.
- DOI: `10.1111/jofi.13268`
- Readable URL: `https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268`
- Crossref: `https://api.crossref.org/works/10.1111/jofi.13268`
- OpenAlex: `https://api.openalex.org/works/https://doi.org/10.1111/jofi.13268`
- 本地 probe artifact:
  - `reports/artifacts/quant_digests/2026-04-23_shapeaware-trendscore_vs_plainmom_probe.csv`
  - `reports/artifacts/quant_digests/2026-04-23_shapeaware-trend_proxy_grid.csv`
