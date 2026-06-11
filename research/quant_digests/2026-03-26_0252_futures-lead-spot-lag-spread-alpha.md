# 别把 BTC spot/futures price discovery 只读成市场结构：更该先测的是「futures lead spike → lagging leg catch-up」same-asset relative-value raw alpha
- 时间：2026-03-26 02:52 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：同资产的 futures→spot / perp lead-lag；先动市场的冲击会在滞后腿上补涨补跌
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / lead-lag / price-discovery / btc / spot / futures / perpetual / intraday / 1m / 3m / 5m / 15m / event-driven
- 证据类型：论文证据（主论文当前为摘要级 + 辅助论文摘要级）

## 1. 这次看了什么
主线是 **Frino, Gaudiosi, Webb, Zhou (2025), _Price Discovery in Bitcoin Spot or Futures? The Jury Is Out_, Journal of Futures Markets**。它的 desk 化读法不是“到底谁更领先”这句机制话，而是：**当 futures 的 price-discovery share 明显上升时，能不能去做 lagging leg 的 catch-up spread**。辅助对照是 **Sharma et al. (2025), _Does Price Discovery Process Hold during Post-COVID Period in Cryptocurrency? Evidence from Bitcoin_**，用于确认 spot/futures 的因果关系并未在后疫情期消失。

## 2. 核心结论
- **一句话结论**：BTC 的短时价格发现更常先出现在 futures 端，真正能交易的不是“basis 总会回归”，而是 **futures 先动、spot/perp 还没补完时的滞后腿 catch-up**。
- **一句话它怎么证明**：主论文用 **1 秒频率** 重新估计 spot 与 futures 的 price discovery，并显式处理 spot/futures 的噪声差异；结论不是静态地“永远 futures 领先”，而是 **futures 通常领先，但领先强度每天波动**。
- 主论文摘要里最值钱的 3 个点：① 用 **1-s sampling** 才看得清；② **futures market generally leads spot markets**；③ 这种领先在 **宏观意外窗口** 与 **Tether minting tweets** 附近会明显增强。
- 这意味着对 desk 来说，最不该做的是把它写成 always-on 的 basis MR；更诚实的写法是：**只在 leader 突然变得很强的 pocket 里做短持有 lag spread**。
- 辅助论文（2017–2024、日频 spot+futures）虽然频率更粗，但也给出一致方向：**Bitcoin 市场存在持续的 price discovery 机制**，且其摘要称 **COVID 对这一机制没有显著改变**。它更像“结构仍在”的地基，不是入场规则本身。

## 3. 为什么和当前项目有关
- 它补的是 **raw alpha 素材池里的 same-asset relative-value / price-discovery**，不是继续在 breakout/retest 上打转。
- 它和我们已经写过的 **ETF→BTC lead-lag**、**BTC→ALT lead-lag** 不同：这次不是跨资产，而是**同一资产不同市场之间**的先后顺序，更容易写成可审计的 spread 规则。
- 如果这条线成立，后面既能独立做一个短持有 stat-arb，也能反过来服务其他 raw alpha：当 futures 明显主导时，单腿趋势单可以拿它做 **trade-on / trade-off**。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / lead-lag
- 基础 alpha：futures 先动后的 lagging leg catch-up
- regime：美国交易时段、BTC realized vol 抬升、重大宏观数据前后、stablecoin 供给冲击窗口
- filter / veto：leader move 必须伴随成交/持仓冲击；spread 尚未闭合；预计净边际 > 手续费+滑点；异常延迟/报价断层时 veto
- risk / sizing / execution overlay：优先 dollar-neutral；默认 1–3 bar 短持有；leader 反向即平；非美盘 size-down；延迟超阈值直接不做

## 4. 可复刻的最小实验
- **研究假设**：当 BTC perpetual / futures 在最近 `60s~5m` 明显先于现货完成方向冲击时，现货或较慢的 perp proxy 会在后续 `1~3` 根 `1m` 或 `1` 根 `5m` 内补涨补跌。
- **公开数据源**：Binance Spot `BTCUSDT` 与 Binance Futures `BTCUSDT perpetual` 公共 `aggTrades` / `bookTicker` / `1m klines`；若后续能拿到更高质量 CME 数据，再做二阶段验证。
- **最小信号定义**：
  1. 用 `1m` 或 `30s` 滚动收益定义 leader shock：`r_fut - r_spot` 或 `r_perp - r_spot`。
  2. 当 leader shock 超过过去 `N=240` 个窗口的 `z > 2`，且 spot 端尚未完成至少 `70%` 的同步跟随时触发。
  3. 入场做 **long lagging leg / short leading leg**；若只想先做单腿，先测 `leader-confirmed lagging-leg directional follow-through`。
- **出场/风控**：spread 关闭到 `80%` 目标即平；最大持有 `3 x 1m` 或 `1 x 5m`；leader 反向或 spread 继续扩到入场阈值 `1.5x` 立即止损。
- **成本口径**：先做 maker-taker 两版；净边至少要覆盖 `2 x` round-trip fee + 保守滑点；把异常延迟窗口单独剔除，不要用平均成交价自欺。
- **优先看的分组**：美盘 vs 亚洲盘、宏观事件前后 30 分钟、高 realized vol vs 低 realized vol、basis widening vs non-widening。

## 5. 先别自嗨的风险
- 主论文当前在本环境下只能稳定拿到 **摘要级证据**，不是全文逐表复核；所以这轮更像 **高质量 raw alpha intake**，还不算 clean replication。
- 论文里更偏 **regulated futures vs spot**；直接映射到 `Binance perp vs Binance spot` 时，交易者结构和延迟结构都不同，不能默认等价。
- 1 秒级领先很可能被费用和执行延迟吞掉，所以第一轮别追求 tick 级；先看 `30s/1m/5m` 的 pocket 化版本能否活下来。

## 6. 来源
1. **Frino, A., Gaudiosi, R., Webb, R. I., & Zhou, Z. I. (2025). _Price Discovery in Bitcoin Spot or Futures? The Jury Is Out_. Journal of Futures Markets.**
   - DOI: https://doi.org/10.1002/fut.22560
   - Readable URL: https://doi.org/10.1002/fut.22560
   - Open-access / PDF-direct URL（当前环境受 Cloudflare 限制，仅稳定拿到摘要元数据）：https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/fut.22560
2. **Sharma, P., Kumar, C. T. S., Singh, P., Satapathy, D. P., & Sharma, A. (2025). _Does Price Discovery Process Hold during Post-COVID Period in Cryptocurrency? Evidence from Bitcoin_. International Journal of Economics and Financial Issues.**
   - DOI: https://doi.org/10.32479/ijefi.20427
   - Readable URL: https://doi.org/10.32479/ijefi.20427
   - PDF URL: https://econjournals.com/index.php/ijefi/article/download/20427/9222
3. **OpenAlex metadata abstract** for Frino et al. (2025): confirms `1-s sampling`, `futures generally leads spot`, and stronger leadership around `macroeconomic surprises` and `Tether stablecoin minting tweets`.
