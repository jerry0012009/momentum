# 别把 Meek (2026) 只读成“股票 cash-flow certainty 论文”：对 short-cycle crypto desk，更该先测的是「EMA fair-value dislocation × non-panicked TSV flow」这条 raw alpha

- 时间：2026-04-19 01:46 UTC
- 类型：2026 SSRN preprint abstract metadata（Crossref）+ Binance USDⓈ-M `5m/15m` portability probe（10 liquid majors）
- 主题类型：raw alpha
- 基础 alpha：**短周期价格显著偏离 EMA fair-value anchor 后，若时间分段成交量流（TSV proxy）没有继续确认单边踩踏，接下来更像发生短窗回归，而不是继续追单边**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（paper 当前只稳定拿到摘要级证据；alpha 壳可复现，但完整落地细节仍需 desk 自己补）
- 主题标签：raw-alpha / single-asset / mean-reversion / fair-value-anchor / ema / tsv / signed-volume-flow / volume-regime / dislocation-fade / binance-perpetual / 5m / 15m / paper / abstract-only / public-data / cost / risk
- 证据类型：摘要级论文线索 + 公共数据最小移植快检

先回答 base alpha：**能答清。**
这次不把 Meek (2026) 的 headline 读成“哪些股票更适合做日内均值回归”，而是把里面**最容易直接移植**的交易骨架单独拎出来：

> **`EMA fair-value anchor` 给出“偏离太远”的价差，`TSV / signed volume flow` 负责判断这次偏离是不是还在被成交量继续推着走；若没有，就优先做 fade。**

这条线本身就是 raw alpha，不是附属 filter。paper 里的 “cash-flow certainty” 更像解释层；对我们 desk 更值钱的是可落地的 **`dislocation × flow non-confirmation -> fade`** 这条主策略壳。

---

## 1. 这次看了什么
主来源：
- **Chris Meek (2026). _Cash Flow Certainty And Intraday Mean-Reversion Reliability_. SSRN preprint.**
- DOI：<https://doi.org/10.2139/ssrn.6422199>
- Readable URL：<https://www.ssrn.com/abstract=6422199>
- 当前可稳定获取：Crossref 元数据与摘要；SSRN 正文页当前反爬，**本文不引用未直接读到的表格/回测细节**。

Crossref 摘要里最关键的 3 个信息：
1. 作者明确用的是 **`TSV regime filter + EMA fair-value anchor`**；
2. 22 只美股、150 个交易日、单一未优化参数集；
3. “高 cash-flow certainty” 组 Sharpe 约 **`3.2~10.6`**，而“低 certainty” 组约 **`-3.6~0.7`**。

对 crypto 来说，最该复用的不是“行业现金流确定性分类”，而是：**先问 volume flow 有没有继续确认这次偏离。**

---

## 2. 为什么和当前项目有关
这条线对 `1m/3m/5m/15m` 有直接价值，因为它天然就是一套完整短窗 mean-reversion 壳：
- **方向属性**：逆势 / 单资产
- **基础 alpha**：价格偏离 fair-value anchor 后的短窗回归
- **regime**：TSV / 成交量流不再继续确认原方向
- **filter / veto**：避免在“还在被大单继续推”的 bar 上硬接飞刀
- **risk / sizing / execution overlay**：可再接 ATR stop、分层回补、maker 优先执行

用人话说：
> **不是“跌多了就抄”，而是“跌离均值了，而且成交量流并没有继续把它往下踩，那才更像值得接”。**

---

## 3. 最小实验与 first verdict
我先用 Binance USDⓈ-M 10 个 liquid majors 做 portability probe：`BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC`，其中 `5m` 近 `30d`、`15m` 近 `60d`。

当前最小口径：
- `fair-value anchor`：EMA（`5m span=48`，`15m span=32`）
- `dislocation`：`dev_z = zscore(close / ema - 1)`，要求 `|dev_z| >= 1.5`
- `TSV proxy`：`sign(ret1) * quote_volume` 的滚动和，再做 z-score
- 只在 **flow 没继续确认单边** 时做 fade：
  - long fade：`dev_z < -1.5 & tsv_z > -0.25`
  - short fade：`dev_z > 1.5 & tsv_z < 0.25`
- 固定持有：`5m` 持 `6` bars，`15m` 持 `4` bars

结果不算“通用裸 alpha”，但有一个值得留的 pocket：
- **`15m strongest-only / alt-proxy`**：`n=174`，next `4` bars gross 约 **`+2.05bps`**；
- 进一步看 **`15m alt-proxy long fade 且 tsv_z >= 0`**：`n=64`，next `4` bars gross 约 **`+13.50bps`**，win rate 约 **`57.8%`**，median 约 **`+13.71bps`**；
- 相反，`5m` 全样本基本不行：`n=638`，gross 约 **`-2.27bps`**；`15m` 裸全样本也偏负：`n=481`，gross 约 **`-6.92bps`**。

这说明：
> **Meek 这条线迁到 crypto 后，不该理解成“所有大偏离都能均值回归”；更像是 `15m alt pocket` 上的 `down-dislocation × non-panicked/positive flow` 反抽 alpha。**

---

## 4. 风险与保留意见
- 当前源头仍是 **摘要级证据**；没有正文，就不能假装已经完整复刻 paper 的原始设置。
- 我这里的 TSV 是 **public-data proxy**，不是作者原公式逐字还原。
- 结果对 bucket 很敏感：这轮不是“BTC/ETH 越大越稳”，反而更像 **alt-proxy long fade** 有 pocket，说明 crypto 的“cash-flow certainty” 解释不能直接照搬。
- 粗扣 taker 成本后，`+13.5bps gross` 仍只是 **可继续 admission-check 的 pocket**，不是直接宣布可实盘。

---

## 5. 下一步怎么测
先别继续炼阈值，下一轮只做 3 件事：
1. **把 pocket 固定成单边版本**：只测 `15m long fade`，不再把 long/short 混一起；
2. **把 TSV gate 改成更明确的“non-panic” 分层**：`tsv_z >= 0`、`qv_z > 0`、`taker_buy_ratio`/CVD proxy 是否同步改善；
3. **补成本与出场**：固定持有 `2/4/6` 个 `15m` bars，对比 `EMA 回归一半即止盈` 与 `ATR stop`，看 pocket 是否还能活。

如果这三步后 pocket 还站得住，它就值得进入 `15m raw alpha -> 5m child execution` 的下一轮研究池。

---

## 6. 产物路径
- Markdown：`research/quant_digests/2026-04-19_0146_tsv-fv-dislocation-fade-alpha.md`
- Artifacts：
  - `reports/artifacts/quant_digests/2026-04-19_tsv_ema_fv_fade_5m_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_tsv_ema_fv_fade_15m_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_tsv_ema_fv_fade_summary.csv`

## 7. 来源
1. **Meek, C. (2026). _Cash Flow Certainty And Intraday Mean-Reversion Reliability_. SSRN preprint.**
   - DOI: <https://doi.org/10.2139/ssrn.6422199>
   - Readable URL: <https://www.ssrn.com/abstract=6422199>
   - Metadata URL: <https://api.crossref.org/works/10.2139/ssrn.6422199>
2. **Binance USDⓈ-M Futures API**
   - Klines: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
