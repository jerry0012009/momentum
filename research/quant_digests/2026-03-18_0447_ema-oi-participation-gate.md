# 别把 OI 当方向神谕：对 15m EMA / PSAR，更像该先测的是 `OI > OI-SMA20` 的参与度 gate
- 时间：2026-03-18 04:47 UTC
- 类型：GitHub
- 主题标签：ema/psar/raw-alpha/open-interest/participation-gate/filter/crypto/15m
- 证据类型：仓库规则 + 公开数据可复现实验

## 1. 这次看了什么
这次看的是 gelatotrade 在 2025-12 发布的 Pine 仓库 **`15m-EMA-9-15-OI-Flip-Signals`**。它的代码很简单：`EMA 9/15` 负责给方向，`OI > SMA20(OI)` 负责决定这次交叉值不值得看一眼；而且同一个 OI 条件同时套在 **buy** 和 **sell** 两边。

**一句话核心结论：** 这类 OI 条件更像 **参与度 / crowdedness gate**，适合给 `EMA / PSAR raw alpha focus` 当 15m 的 chop veto，而不是伪装成“用 OI 猜涨跌方向”的新主信号。

**一句话说明它为什么值得先测：** 和 funding / basis 那种更偏 8h 的拥挤度变量不同，公开 OI 数据本身就能直接拿到 `5m / 15m` 频率，所以它更贴近当前 desk 想收口的 **EMA 原始信号成本后还剩什么** 这个问题。

## 2. 核心结论
- 这个 repo 最有价值的地方，不是 `EMA 9/15` 本身，而是作者无意中做对的一件事：**把 OI 当成不分方向的 participation gate**。代码里 `signal_buy` 和 `signal_sell` 都要求同一个 `oi_bullish = data_src > SMA20(data_src)`，说明它真正过滤的是“这次 cross 有没有新资金 / 新仓位参与”，不是“OI 高就一定看多”。
- 这点对我们很重要，因为当前 `EMA / PSAR raw alpha` 的痛点并不是再找一个更花哨的均线，而是 **怎么少做低参与度、低延续、成本一扣就归零的 15m 假动作**。
- 如果这个 gate 有用，它最该改善的不是峰值收益，而是：
  1. `whipsaw rate`；
  2. `4~8 bar false reversal`；
  3. 扣成本后的 `median trade expectancy`。
- 另一个现实优点是：Binance 的 `openInterestHist` 公共接口直接支持 **`5m` 和 `15m`**，`limit` 默认 **30**、最大 **500**，最近 **1 个月** 可直接取；这意味着它不是“理论上可得”，而是今天就能拉下来做最小实验。
- repo 里还留了一个很值得 desk 直接修正的细节：脚本在拿不到 OI 时会 fallback 到 `volume`。这提醒我们第一轮最好不要把“没有 OI 的 volume 替代版”和“真 OI 版”混回一起，而要拆成两个 bucket 单独看，否则容易把结论搞脏。

## 3. 为什么和当前项目有关
这题比去找一条全新的远线更值得，是因为它直接贴着 `EMA / PSAR raw alpha focus` 的当前收口口径：
- **不是新 entry**：方向仍然让 EMA / PSAR / breakout 负责；
- **是低成本 filter**：OI 只负责回答“这根 15m 动作是不是太空、太挤、太容易白做”；
- **能反哺另外两条线**：
  - 对 `V3 breakout-short follow-up`，它可以变成 **break 后 continuation vs. dead-on-arrival** 的参与度过滤；
  - 对 `Fibonacci confirmation / retest_hold`，它可以变成 **retest 是否真的有人接 / 有人追** 的附加确认，而不是只看价格碰位。

换句话说，它不是偏题；它是在给三条线补一个当前还比较缺的、而且是公开可得的 **micro participation layer**。

## 4. 可复刻的最小实验
- **研究假设**：在同一套 15m `EMA` 或 `EMA+PSAR` 入场规则下，只有当 `OI` 明显高于自身短均值时，信号后的延续性更好、假翻转更少；反之，很多原始信号只是低参与度噪音。
- **数据源**：
  - Binance USDⓈ-M Futures `GET /futures/data/openInterestHist`（公开、支持 `5m/15m`、最近 1 个月、limit 最大 500）；
  - Binance `GET /fapi/v1/openInterest`（公开、当前 OI snapshot）；
  - 现有 15m OHLCV。
- **最小可计算定义**：
  - `oi_level_gate = OI_t > SMA20(OI)_t`
  - `oi_delta_gate = ΔOI_t > 0`
  - `oi_z_gate = zscore(ΔOI, 48) > 0.5`
  - `volume_fallback_gate = volume_t > SMA20(volume)_t`（只作对照，不和真 OI 混算）
- **第一轮 bucket**：
  1. `raw EMA / EMA+PSAR`
  2. `+ oi_level_gate`
  3. `+ oi_level_gate + oi_delta_gate`
  4. `+ volume_fallback_gate`
- **最该先看的 4 个指标**：
  1. `4/8/12 bar follow-through`；
  2. `2~4 bar whipsaw ratio`（信号后很快反向穿回慢线 / anchor）；
  3. `net expectancy @ 6bps/side and 10bps/side`；
  4. `trade count retention`（过滤后别把样本砍没了）。
- **更像当前 desk 的落地方式**：先不要把 OI 当 hard veto；更合理的是先试三挡：`high participation = 1.0x`、`neutral = 0.5x`、`low participation = 0x`，看看它更适合当 **veto** 还是 **sizing overlay**。

## 5. 风险与保留意见
- 这是 **repo 规则启发**，不是论文级实证。它值钱在“想法干净、实现快”，不在“作者已经替我们证明过”。
- OI 上升不是方向标签。上涨时 OI 升可能是新多进场；下跌时 OI 升也可能是新空进场。**方向仍然必须让价格规则来定**。
- Binance `openInterestHist` 公开窗口只有最近 1 个月；如果最小实验第一轮有信号，下一步就要做日常抓取，不然没法做长窗 OOS。
- repo 代码里 `request.security(sym_oi, timeframe.period, open, ...)` 这种写法依赖 TradingView 上 OI 符号的具体口径；真正落到研究管线时，最好直接固定交易所 API 字段，别把图表平台黑箱带进来。

## 6. 来源
- gelatotrade (2025). *15m-EMA-9-15-OI-Flip-Signals*. GitHub repository.
- Venue：GitHub
- DOI：N/A
- Repo URL：`https://github.com/gelatotrade/15m-EMA-9-15-OI-Flip-Signals`
- Raw script：`https://raw.githubusercontent.com/gelatotrade/15m-EMA-9-15-OI-Flip-Signals/main/ema_crossover_+_OI_flip.pine`
- Repo metadata：created `2025-12-02`, updated `2025-12-15`, public MPL-2.0
- Public data doc 1：Binance `Open Interest Statistics` — `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest-Statistics`
- Public data doc 2：Binance `Open Interest` — `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Open-Interest`

## 7. 下一步怎么测
先别扩到全世界，直接拿 `BTCUSDT / ETHUSDT / SOLUSDT` 的最近 30 天 15m，复用现有 `EMA raw alpha` 或 `EMA+PSAR` 入场定义，先跑上面 4 个 bucket。只要 `oi_level_gate` 能在 **不显著砍掉 trade count** 的前提下，稳定压低 `2~4 bar whipsaw ratio`，这条线就值得进入下一轮更长窗数据采集和 OOS 检验。