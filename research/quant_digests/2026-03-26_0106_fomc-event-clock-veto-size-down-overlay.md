# 别把 FOMC 只当宏观日历提醒：这篇 2026 working paper 更该先落地的是「14:00 ET 事件时钟 veto + size-down」共享 overlay
- 时间：2026-03-26 01:06 UTC
- 类型：2026 SSRN working paper（Crossref 摘要可得）+ Fed 官方日历/声明页 + Binance Futures 公共 `1h/15m` 最小快检
- 主题类型：overlay
- 基础 alpha：无独立 raw alpha；基础逻辑是 `scheduled FOMC release → 短时波动/成交额显著抬升`，因此对既有 `1m/3m/5m/15m` 策略施加 event-clock veto / size-down / re-arm 管理
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：overlay/regime/macro-event/fomc/event-clock/volatility/volume/liquidity/execution-veto/position-sizing/shared-gate/binance/btc/eth/crypto/1m/3m/5m/15m/paper/external-data
- 证据类型：论文摘要证据 + 官方日历证据 + 公共市场数据快检

> 先回答 base alpha：**这不是独立 raw alpha。它更诚实的定位，是一个可以独立复现、并且能同时服务 trend / mean reversion / maker-taker execution 的 scheduled-event overlay。**

## 1. 这次看了什么
这次主看：
- **Manlu Yang, Yufeng Wang (2026), _Scheduled FOMC Statements and Cryptocurrency Trading Activity: Intraday Evidence from a 24/7 Market_**
- **Federal Reserve FOMC 官方会议日历与 statement 页面**
- **Binance USDⓈ-M Futures 公共 `1h/15m` K 线**，做最小 desk 化复核

我这次不把它硬写成“FOMC 后做方向突破”这种伪 raw alpha，因为论文摘要并没有给出稳定方向，只清楚给出两件事：
1. **FOMC statement release 这个时钟本身是可预测的**；
2. **release 后第一个小时里，BTC / ETH 的波动和成交会系统性放大**。

所以对我们 desk 更值钱的，不是再造一条没有证据的方向信号，而是先把它落成一句可执行的话：

**凡是没有显式 event edge 的短周期策略，在 FOMC 14:00 ET 公布前后，都不该用平时那套仓位和成交方式去硬打。**

这轮为什么允许它插队、而不是继续补一篇 raw alpha？
- 过去两天 raw alpha intake 已经很密；
- 但这些 raw alpha 大多默认“平稳时段成本/波动结构”，而 **FOMC 是少数可以提前知道时点、又会同时冲击波动与流动性的宏观事件**；
- 它不是纯解释文，而是一个能同时服务至少三类已有 alpha（trend breakout、MR、maker/taker execution）的**共享 event gate**。

## 2. 核心结论
- 一句话核心结论：**这篇 2026 working paper 最该先落地的，不是“宏观也会影响 crypto”这种废话，而是一个公开、精确、可回测的 event-clock risk overlay。**
- 一句话它怎么证明：**论文用 2021-01 到 2026-01 的 41 次 scheduled FOMC statement，对 BTC / ETH 的 hourly 波动与成交做事件研究；我再用 2024-01 到 2026-03 的 18 次事件，在 Binance Futures 上做 `1h/15m` 的 pre/post 快检，结论方向一致。**

关键数据点（论文） ：
1. 样本覆盖 **41 次 scheduled FOMC statement**（2021-01 至 2026-01），研究的是 24/7 crypto 市场在 **14:00 New York time** statement release 之后的反应。
2. **BTC** 在事件前 1 小时的平均绝对收益约 **0.66%**，到事件后第 1 小时升到 **1.25%**；USD 成交额约放大到 **2.54 倍**。
3. **ETH** 在事件前 1 小时的平均绝对收益约 **0.85%**，到事件后第 1 小时升到 **1.50%**；USD 成交额约放大到 **2.81 倍**。
4. 论文还做了 **matched-week controls、hour-matched placebos、fixed-effects regressions**，并在 **Bitfinex** 上做 cross-venue replication，说明这不是简单的日内季节性。

关键数据点（本地最小快检：Fed 官方日历 + Binance USDⓈ-M Futures 公共 K 线；2024-01-31 至 2026-03-18 共 18 次 scheduled statement）：
1. **BTCUSDT 1h 口径**：事件前 1 小时平均绝对收益约 **0.43%**，事件后 1 小时升到 **0.93%**；平均 quote volume 约从 **9.81 亿 USDT** 升到 **27.34 亿 USDT**；`post > pre` 的事件占比，波动约 **72%**、成交额约 **89%**。
2. **ETHUSDT 1h 口径**：事件前 1 小时平均绝对收益约 **0.69%**，事件后 1 小时升到 **1.15%**；平均 quote volume 约从 **6.72 亿 USDT** 升到 **17.52 亿 USDT**；`post > pre` 的事件占比，波动约 **56%**、成交额约 **94%**。
3. **同样做前一周同一时刻 placebo** 时，BTC / ETH 的 `1h` **平均成交额放大量只有约 `1.09x / 1.21x`**，明显低于 FOMC 事件窗的 **`3.34x / 3.14x`**。
4. **更贴近 desk 的 15m 口径**：
   - BTCUSDT：事件前 15m 平均绝对收益约 **0.18%**，事件后第一个 15m 升到 **0.44%**；平均 quote volume 约从 **2.66 亿** 升到 **9.55 亿 USDT**。
   - ETHUSDT：事件前 15m 平均绝对收益约 **0.39%**，事件后第一个 15m 升到 **0.56%**；平均 quote volume 约从 **1.97 亿** 升到 **6.63 亿 USDT**。
   - 15m 的 **median volume ratio** 约为：BTC **3.09x**、ETH **3.29x**。

## 3. 为什么和当前项目直接相关
这篇东西不是 raw alpha，但它和当前 short-cycle desk 的关系非常直接：

1. **它服务现有 raw alpha 池，而不是替代它们。**
   - breakout / momentum：最容易在事件后放大 slippage 与追单过冲；
   - mean reversion：最容易在事件后一脚反向扩张里被提前打止损；
   - maker / passive：最容易在 spread 放宽与 adverse selection 中被动接刀。

2. **它是少数“时点可提前知道”的宏观冲击。**
   大部分风险事件只能事后识别；FOMC statement 不一样，日历是公开的，时点是固定的，天然适合做 binary overlay。

3. **它非常适合 `1m / 3m / 5m / 15m`。**
   不是因为它能给逐根方向，而是因为这些短周期正好可以精细管理：
   - `T-30m ~ T` 是否停新仓；
   - `T ~ T+15m` 是否禁 taker / 加宽 maker quote；
   - `T+15m ~ T+60m` 是否半仓恢复；
   - `T+60m` 之后是否按 realized spread / realized vol 恢复常态。

## 3.5 策略拆解（必填）
- 方向属性：shared overlay / event-risk gate / execution veto
- 基础 alpha：无独立方向 alpha；基础逻辑是 **scheduled macro-event clock → volatility/liquidity shock**
- 服务对象：
  - trend / breakout raw alpha
  - mean reversion raw alpha
  - maker / taker execution stack
- 建议的 overlay 规则（第一版）：
  - **soft gate**：`T-30m ~ T`，无明确 event edge 的新信号降到 **0.5x** 或直接不加仓；
  - **hard gate**：`T ~ T+15m`，默认**禁止 taker 追价新仓**；maker 策略则上调 quote width、下调 size；
  - **cooldown**：`T+15m ~ T+60m`，仅允许低冲击/低频信号，仓位上限 **0.25x ~ 0.5x**；
  - **re-arm**：若 `realized_vol_15m`、`spread_state`、`slippage_state` 回到滚动分位正常区间，再恢复常态。
- sizing：
  - 事件后第一个 15m 和第一个 1h 分层控制；
  - 对 taker alpha 先按 `min(0.5, baseline_size * vol_target_adj)`；
  - 对 maker alpha 先按 `baseline_inventory_cap * 0.5`。
- risk：
  - 加一条**日历型 kill-switch**，避免只靠价格路径事后止损；
  - 若策略本身没有宏观事件豁免标签，默认进 gate；
  - 事件后若出现 spread 放宽 / volume 爆发但成交质量恶化，优先保护执行质量而不是硬保信号频率。
- cost：
  - 事件时段最先坏掉的，通常不是 signal 本身，而是 **fill quality**；
  - 所以 overlay 的评估指标不能只看信号收益，还要看 `slippage / adverse selection / quote fade rate`。

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- **FOMC meeting calendars**：Federal Reserve 官方公开页面，全年可提前获取。
- **FOMC statement release pages**：Federal Reserve 官方公开页面，可确认具体 release 时间（2:00 p.m. ET）。
- **Binance USDⓈ-M Futures klines**：公开 REST，可直接取 `1m / 3m / 5m / 15m / 1h`。
- 若要扩展 cross-venue，可再接 Bitfinex / Coinbase / OKX 公共行情。

### 4.2 最小可复现实验口径
第一轮不用做复杂 event-study econometrics，直接做 desk 版最小实验：
1. 用 Fed 日历生成事件时间戳 `event_ts`；
2. 对 `BTC/ETH/SOL` 取 `1h` 与 `15m` K 线；
3. 比较：
   - `abs_ret(T-1h,T)` vs `abs_ret(T,T+1h)`
   - `quote_vol(T-1h,T)` vs `quote_vol(T,T+1h)`
   - `abs_ret(T-15m,T)` vs `abs_ret(T,T+15m)`
4. 再做一个**前一周同一时刻 placebo**，防止把普通时段季节性误认成事件效应；
5. 最后把这个 binary event feature 接到现有 raw alpha 回测里，比较 `with gate` vs `without gate`。

## 5. 下一步怎么测（必须）
1. **先做 overlay A/B test，而不是继续争论方向。**
   在现有 3 类策略上回放：
   - 无 overlay
   - `[-30m, +15m]` hard veto
   - `[-15m, +60m]` size-down
   看净值、回撤、成交质量谁更好。

2. **把“禁做”拆成“禁什么”。**
   不要只测一个总开关，至少拆 3 条：
   - 禁新开 taker 仓
   - maker 加宽报价 / 降 inventory cap
   - 平旧仓允许、不加新仓

3. **补一个 re-arm 条件，而不是固定熬满 60 分钟。**
   可先测：
   - `realized_vol_15m` 回到滚动 `p70` 以下
   - `spread` 回到滚动 `p70` 以下
   - `volume shock` 回落到滚动 `p80` 以下
   三者满足两条才解除 hard gate。

4. **扩展到同类 scheduled macro events。**
   下一批最值得平移的是：
   - CPI
   - NFP
   - PCE
   - Powell 记者会 / Jackson Hole 级别讲话
   先验证它们是不是和 FOMC statement 一样，属于“公开、精确、可治理”的事件窗。

5. **按策略家族拆效果，而不是求全局平均。**
   我更怀疑：
   - breakout / momentum 会从 overlay 中受益最多；
   - MR 可能在 `T+15m ~ T+60m` 才开始真正受益；
   - maker 最需要的是 quote widening，而不是简单停机。

## 6. 风险与保留意见
- 这条线**不是方向 alpha**；若硬把它包装成“FOMC 后做多/做空 BTC”，那是在超出证据说话。
- 事件数并不多，天然属于**低频但高影响**的 overlay，不是每天都会触发的模块。
- 本地快检用的是 **Binance Futures**，而论文摘要描述的是 **BTC/ETH 现货跨 venue 事件研究**；两者方向一致，但不是同一数据口径。
- 它更可能改善的是 **回撤、尾部损失与成交质量**，不一定会提高 gross alpha 命中率。
- 如果 desk 将来专门做“事件后 breakout sleeve”，那应单独建模，不该和这里的 veto / size-down overlay 混为一谈。

## 7. 来源
1. **Yang, M., & Wang, Y. (2026). _Scheduled FOMC Statements and Cryptocurrency Trading Activity: Intraday Evidence from a 24/7 Market_. SSRN Working Paper.**
   - DOI: `10.2139/ssrn.6299551`
   - Readable URL: `https://doi.org/10.2139/ssrn.6299551`
   - Repo URL: N/A
2. **Federal Reserve. _Meeting calendars and information_.**
   - Readable URL: `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`
3. **Federal Reserve. _Federal Reserve issues FOMC statement_（示例页）.**
   - 2025-01-29：`https://www.federalreserve.gov/newsevents/pressreleases/monetary20250129a.htm`
   - 2026-03-18：`https://www.federalreserve.gov/newsevents/pressreleases/monetary20260318a.htm`
4. **Binance Developers. _USDⓈ-M Futures API: Kline/Candlestick Data_.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 8. 本地复现产物
- `reports/artifacts/quant_digests/2026-03-26_fomc_event_gate_probe/event_windows.csv`
- `reports/artifacts/quant_digests/2026-03-26_fomc_event_gate_probe/summary.csv`
- `reports/artifacts/quant_digests/2026-03-26_fomc_event_gate_probe/summary_15m.csv`
- `reports/artifacts/quant_digests/2026-03-26_fomc_event_gate_probe/meta.json`
