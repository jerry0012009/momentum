# 别把这篇 *Cross-Market Intraday Time-Series Momentum* 只读成“跨市场联动综述”：对 short-cycle crypto desk，更该先测的是「BTC downside shock × alt catch-up continuation」这条 raw alpha

- 时间：2026-04-24 21:52 UTC
- 类型：2023/2024 SSRN working paper metadata audit（Crossref + OpenAlex）+ Binance USDⓈ-M public-data portability probe（`BTC -> alt basket`，`15m`）
- 主题类型：raw alpha
- 基础 alpha：**一个领先市场/资产刚走出的 intraday 方向，会在下一小段里向跟随市场继续传导；对 crypto desk，可先翻成 `BTC 先跌/先涨 -> alt 下一段同向 catch-up`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-market/lead-lag/intraday/momentum/continuation/btc/alt-basket/15m/5m/paper/public-data/cost/risk
- 证据类型：metadata-only paper signal + public-data portability probe

## 1. 这次看了什么
主线材料是 Xu, Li, Singh, Li 的 SSRN working paper **Cross-Market Intraday Time-Series Momentum**。当前能稳定拿到的是 Crossref / OpenAlex / SSRN metadata：
- **Authors：** dezhong Xu, Bin Li, Tarlok Singh, Jinze Li
- **Year：** 2023 首版，2024 有更新版本
- **Title：** *Cross-Market Intraday Time-Series Momentum*
- **Venue：** SSRN Electronic Journal / working paper
- **DOI：** `10.2139/ssrn.4651331`（另有 2024 版本 `10.2139/ssrn.4765613`、`10.2139/ssrn.4978089`）
- **Readable URL：** <https://doi.org/10.2139/ssrn.4651331>
- **SSRN URL：** <https://www.ssrn.com/abstract=4651331>

先把限制说清楚：**这轮没拿到全文正文**，因为 SSRN 页面对当前抓取路径有 Cloudflare challenge；所以我不复述作者未核实的具体统计结论，只把它当成一个高相关 raw-alpha 题目线索，再用 Binance 公共数据做 first verdict。

## 2. 一句话结论
- **一句话核心结论：** 这条题目最值得 desk 先试的，不是“大而全跨市场动量”，而是更窄、更像执行入口的 `BTC 15m 先动 -> alt 下一段同向 catch-up`；当前在 Binance `15m` 上，**常态很薄，但 BTC 下跌尾部冲击后，alt basket 短窗跟跌有 pocket edge 迹象**。
- **一句话证明方式：** 论文侧目前只有 metadata 级线索；我这轮真正可核的证据来自 public-data 快检：直接把题目翻成 `BTC lead / alt follow`，在 Binance USDⓈ-M `15m` 上看下一段同向收益还剩多少。

## 3. 为什么和当前项目有关
这题和当前 desk 相关，不是因为“又一篇 momentum”，而是它天然能拆成：
1. **raw alpha 本体：** 跨资产 intraday lead-lag continuation；
2. **更 desk 化的旁支：** 不做所有市场互相传导，先抓最有现实意义的 `BTC -> alt` 单向冲击传播；
3. **执行映射：** `15m` 父层给方向，`5m` 子层再做 pullback / maker-friendly 入场。

这正好服务于当前 bot7 的 alpha 素材池：它不是解释型综述，而是一条能直接落到 `1m/3m/5m/15m` 最小实验的 cross-market raw alpha 候选。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / cross-market lead-lag
- 基础 alpha：BTC 先动后，alt 下一小段同向 catch-up continuation
- regime：更像集中在 **BTC downside tail shock** 之后，而不是所有普通 bar
- filter / veto：只在 `|BTC 15m return|` 进入高分位时开；若只是普通波动，默认不交易
- risk / sizing / execution overlay：alt basket 等权或 inverse-vol；父层 `15m` 触发，子层 `5m` 做 pullback 入场与 time-stop；先看 `2/4/6/8 bps` friction ladder

## 4. 本轮最小 portability probe
我先测最简单、也最像 desk 会真的先跑的版本：
- **leader：** `BTCUSDT` 上一根 `15m` 收益
- **followers：** `SOL/BNB/XRP/DOGE/ADA/LINK` 等权 basket
- **交易：** 若 BTC 上根为正则做多下一根 alt basket；若为负则做空下一根 alt basket
- **样本：** Binance USDⓈ-M 最近 `1500` 根 `15m` bar

先给 4 个最有用的数：
1. **BTC 正收益后的全样本 alt basket gross**：`+0.73 bps/笔`（`782` 次）
2. **BTC 负收益后的全样本 alt basket gross**：`-0.06 bps/笔`（`716` 次）
3. **BTC 下跌幅度进入 `q90` 尾部后，alt basket 下一根同向 gross**：`+2.76 bps/笔`（`65` 次）
4. **BTC 下跌进入 `q95` 尾部后，alt basket 下一根同向 gross**：`+5.71 bps/笔`（`31` 次）

再看 follower pocket：
- `BTC neg q90 -> DOGE`：`+6.08 bps/笔`
- `BTC neg q90 -> ADA`：`+3.78 bps/笔`
- `BTC neg q95 -> DOGE`：`+9.42 bps/笔`
- `BTC neg q95 -> ADA`：`+9.11 bps/笔`

翻成人话：
- **平时别硬做。** `BTC -> alt` 的常态 lead-lag 太薄，taker 成本一扣大概率没了。
- **真正值得留进研究池的是“BTC downside shock 后的 alt 跟跌 pocket”。** 它还不是完整策略，但比“所有 bar 都做跨市场动量”更像短周期 desk 的真实入口。

## 5. 风险与保留意见
1. **论文证据当前不完整。** 这轮只能确认题目、作者、版本与 working-paper 身份，不能把作者原文的样本设计和显著性结果说得过满。
2. **当前 probe 只是 first verdict。** 只测了 `15m parent -> next 15m follower`，还没做 `5m` child execution，也没扣完整滑点/手续费梯度。
3. **edge 很可能只活在 tail pocket。** 常态 gross 太薄，不适合包装成 always-on alpha。
4. **下跌传播未必长期稳定。** 这种 shock-spillover 可能受市场结构、新闻驱动和 alt beta 状态影响，必须看 rolling stability。

## 6. 下一步怎么测
1. **先做 friction ladder**：对 `BTC neg q90/q95` 口径直接扣 `2 / 4 / 6 / 8 bps`，先判断 pocket 还能剩多少。
2. **做 `15m parent / 5m child`**：父层只负责识别 BTC downside shock；子层等 alt 出现一次 `5m` 小反抽再跟空，测试能否把 `+2.76 / +5.71 bps` 的毛边保下来。
3. **做 bucket router**：不要等权全做，先只保留 `DOGE/ADA/XRP` 这类 tail-pocket 更厚的 follower，再比较 trade count 与 net bps/trade。
4. **做 regime split**：按 BTC realized vol、funding sign、US session / Asia session 分层，看这条 cross-market continuation 是不是只在高压时段成立。

## 7. 来源
- Xu, D., Li, B., Singh, T., & Li, J. (2023/2024). *Cross-Market Intraday Time-Series Momentum*. SSRN Electronic Journal / working paper.
- DOI: <https://doi.org/10.2139/ssrn.4651331>
- Updated-version DOI: <https://doi.org/10.2139/ssrn.4765613>
- Updated-version DOI: <https://doi.org/10.2139/ssrn.4978089>
- SSRN landing URL: <https://www.ssrn.com/abstract=4651331>
- Crossref metadata API: <https://api.crossref.org/works/10.2139/ssrn.4651331>
- OpenAlex metadata API: <https://api.openalex.org/works/https://doi.org/10.2139/ssrn.4651331>

## 8. 本轮 artifacts
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-24_btclead_altfollow_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-24_btclead_altfollow_asset_tail.csv`
