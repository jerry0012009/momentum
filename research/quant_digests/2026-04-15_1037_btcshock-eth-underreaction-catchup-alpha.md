# 别把这份 BTC/ETH pairs repo 又读成一篇 spread fade：对 short-cycle desk，更该先测的是「BTC shock × ETH same-minute underreaction → next 1~2 bar catch-up」这条 relative-value raw alpha

- 时间：2026-04-15 10:37 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `analytics/features.py` + `analytics/mean_reversion_backtest.py` + `ingestion/binance_websocket.py` + `config.py` + `app.py`）+ Binance USDⓈ-M `1m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 `BTC` 出现 `1m` 冲击、而 `ETH` 在同一分钟明显“没跟上”时，做 `long ETH / short BTC`（若是下跌冲击则反向理解为继续做相对 catch-up），持有接下来的 `1~2` 根 bar，赌 lagger 补动；repo 里的 `cross-correlation at lags` 更适合服务这条 event-driven relative-value alpha，而不该只留在 dashboard 里。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，但需要补事件阈值、beta/vol scaling、next-bar 执行与成本约束
- 主题标签：raw-alpha/relative-value/lead-lag/event-driven/btc-shock/eth-underreaction/catch-up/binance-perpetual/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit + public-data portability probe

## 1. 这次看了什么
这轮主看的是一个 2025-12 创建、2026-02 仍有更新的新 repo：

- **Author / Repo owner：** `HerambPatilcoder`
- **Year：** 2025/2026
- **Title：** *Crypto_Pairs_trading*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/HerambPatilcoder/Crypto_Pairs_trading>
- **Repo URL：** <https://github.com/HerambPatilcoder/Crypto_Pairs_trading>
- **GitHub API metadata（已复核）：** repo 创建于 `2025-12-16`，最近更新时间 `2026-02-28`

repo 表面 headline 还是很像那类熟悉的 `BTC/ETH spread + z-score + mean reversion` dashboard，但这轮如果继续把它写成“又一篇 BTC/ETH spread fade”，和近几天素材池会太近。

它真正还值得 intake 的旁支，是 `analytics/features.py` 里那条经常被忽略的函数：
- `cross_corr(x, y, max_lag=20)`

再加上 repo 已经给好的 live plumbing：
- `ingestion/binance_websocket.py`：实时 trade stream
- `duckdb_storage.py`：本地 tick 存储
- `resampler_filter.py`：`1s / 1m / 5m` 重采样
- `app.py`：把 lag / corr / z-score / ADF 全都挂上 dashboard

所以这轮更值钱的读法不是：
> “BTC/ETH spread 又能做均值回复。”

而是：
> **“既然 repo 已经显式给了 lag-scan，这份材料更适合拿来测 `BTC impulse -> ETH delayed catch-up` 这条 event-driven relative-value raw alpha，到底有没有短周期 pocket。”**

## 2. base alpha 先说清楚
这轮的 **base alpha** 不是 correlation monitor，也不是 dashboard alert。

它是：
> **`BTC` 先剧烈动、`ETH` 同一分钟却明显没跟上时，后面 `1~2` 根 `1m` bar 存在一段短暂的 relative-value catch-up pocket。**

翻成人话：
- 这不是方向单；
- 也不是 broad 的“BTC 永远领先 ETH”；
- 更不是把 lag correlation 当解释型小图；
- 它是一条 **条件触发型 / event-driven / relative-value raw alpha**。

具体可写成：
1. 先识别 `BTC 1m shock`；
2. 再要求 `ETH same-minute underreaction`；
3. 然后做 `ETH catch-up vs BTC` 的短持有期交易；
4. 超时没补动就走。

所以它仍然属于当前 bot7 优先级里更高的那一类：
- **可独立复现的 raw alpha 候选**；
- 而不只是给现有 alpha 当 shared filter。

## 3. 为什么这条旁支比“再写一篇 spread MR”更值得
因为 repo 的主壳当然还是 spread mean reversion：
- `huber_hedge_ratio(y, x)`
- `kalman_hedge_ratio(y, x)`
- `spread_and_zscore(y, x, hr, window)`
- `mean_reversion_backtest(z, entry_z=2.0, exit_z=0.1)`

但这一类主题这几天已经补得很密：
- BTC/ETH spread fade
- dynamic hedge ratio spread fade
- pair admission / half-life / validation ranking
- vol-gated spread fade

继续顺着 headline 写，边际增量不高。

反而 repo 里 **明确留着但没被写成主策略** 的那条 `cross-correlation at lags`，更能补当前池子里一个没那么拥挤的 pocket：
> **不是 always-on lead-lag，而是“冲击 + 同步失败 + 1~2 bar catch-up”这条更短、更诚实的 event pocket。**

## 4. repo 里哪些实现支撑这条读法
### 4.1 `features.py`
关键函数：
- `cross_corr(x, y, max_lag=20)`
- `rolling_corr(x, y, window)`
- `huber_hedge_ratio(y, x)`
- `kalman_hedge_ratio(y, x, delta=1e-4, R=0.01)`
- `adf_test(series)`

这意味着 repo 不是只能看 contemporaneous spread，它已经允许：
- 看 `lag 0` 之外的相关性；
- 看 relationship 是否从“同步”偏到“谁先谁后”；
- 再决定该做 spread fade，还是改做 catch-up / veto。

### 4.2 `config.py`
repo 的默认实验口径本身就很 desk-friendly：
- `SYMBOLS = ["btcusdt", "ethusdt"]`
- `TIMEFRAMES = {"1s": "1s", "1m": "1min", "5m": "5min"}`
- `DEFAULT_WINDOW = 50`
- `DEFAULT_Z_THRESHOLD = 2.0`

这说明作者虽然 README 主要讲 pairs analytics，但实际 scaffold 已经把 `1s/1m/5m` 快节奏入口给出来了。

### 4.3 `ingestion/binance_websocket.py`
repo 用的是：
- `wss://stream.binance.com:9443/ws/{symbol}@trade`

再配 DuckDB 存 tick，意味着它天然更适合：
- 先积 tick / 1s；
- 再聚到 `1m`；
- 然后测 `shock -> underreaction -> catch-up`。

这和“只用日级/小时级 pair cointegration”不是一回事。

## 5. 我这轮怎么做最小 portability probe
我没有继续复刻 repo 的 z-score MR，而是专门测它这条 lag 旁支。

### 5.1 数据
- 数据源：Binance USDⓈ-M public klines（公开可得）
- 频率：`1m`
- 标的：`BTCUSDT / ETHUSDT`
- 样本：最近 `30d`
- 实验脚本：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-15_btceth_lagscan_probe.py`
- 输出文件：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/btceth_laglead_corr30d_2026-04-15.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/btceth_laglead_roll30d_2026-04-15.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/btceth_laglead_events_q095_2026-04-15.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/btceth_laglead_q095_directional_2026-04-15.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/btceth_laglead_summary30d_2026-04-15.json`

### 5.2 事件定义
这轮故意不用“泛泛 lag correlation”，而是更贴 desk：

1. `BTC 1m return` 达到近 `30d` 的高分位 shock（我扫了 `95% / 97.5% / 99%` 三档）；
2. 同一分钟里，`ETH` 的同向反应不到 `BTC` 幅度的 `40%`，或直接没同向跟上；
3. 把这类时刻视作 `ETH same-minute underreaction`；
4. 然后看后面 `1~2` 根 bar 的：
   - `ETH` 自身是否继续朝 BTC shock 方向补动；
   - `long ETH / short BTC` 的 relative-value PnL proxy 是否为正。

## 6. first verdict：broad lead-lag 不成立，但 event pocket 还在
### 先给最关键的 4 个数据点
1. **无条件 lag-corr 基本不支持“BTC 稳定领先 ETH 1~5 分钟”这件事。**
   - `lag 0` 相关性约 **0.873**；
   - 非零 lag 相关都很小，最高也只是：
     - `lag -1` 约 **0.054**
     - `lag +1` 约 **0.020**
   - rolling `6h` window、每小时取一次 peak lag，**`714/714` 次都是 `lag 0`**。

   这句很重要：
   > **别把 repo 里的 lag-scan 误读成“存在稳态 1m 级 BTC->ETH lead-lag”。至少 recent 30d 的 Binance perp proxy 不支持。**

2. **但一旦只看“BTC 先冲、ETH 同分钟没跟上”的事件 pocket，relative-value edge 会出来。**
   - 用 `95%` shock 阈值时，近 `30d` 一共识别到 **67** 次事件；
   - 事件后 `1m` 的 `long ETH / short BTC` signed RV proxy 平均 **+2.07 bps**；
   - 事件后 `2m` 的 signed RV proxy 平均 **+3.95 bps**；
   - 两者 hit rate 都约 **64.2%**。

3. **这个 pocket 在 downside shock 里更稳定。**
   - `BTC down-shock` 子样本：`33` 次
   - `1m RV` 平均 **+3.35 bps**，hit rate **69.7%**
   - `2m RV` 平均 **+3.42 bps**，hit rate **72.7%**

4. **越极端不一定越好；`99%` shock 样本更少，稳定性反而下降。**
   - `99%` 只有 **10** 次事件
   - `1m RV` 平均反而 **-2.22 bps**
   - `2m RV` 才回到 **+1.28 bps**

所以这轮最诚实的结论是：
> **广义的 BTC/ETH lead-lag raw alpha 不成立；真正值得测的是“BTC shock × ETH same-minute underreaction”这种条件化 catch-up pocket。**

## 7. 这条 alpha 应该怎么 desk 化
如果把它写成最小策略骨架，建议是：

### 7.1 Entry
- 时间框架：`1m` 主状态，`3m/5m` 做背景过滤
- 触发：
  - `|BTC 1m ret| > q95` 或更稳健的 rolling EVT / realized-vol 标准化冲击
  - `ETH same-minute ret` 同向幅度 `< 0.4 * |BTC ret|`
- 入场：
  - `BTC 上冲、ETH 没跟上` -> `long ETH / short BTC`
  - `BTC 下砸、ETH 没跟上` -> 仍做 catch-up 方向的 `short ETH / long BTC`

### 7.2 Exit
优先先测最简单三种：
1. 固定持有 `1 bar`
2. 固定持有 `2 bars`
3. `ETH` 补动到某个比例（例如达到 BTC 冲击的 `60~80%`）就走

### 7.3 Sizing
- 不要裸 notional 1:1；
- 先用短窗 beta / vol ratio 做轻量中性化；
- shock 太大时可 size-down，避免把“事件有效”误做成“波动太大所以赚/亏都更大”。

### 7.4 风险 / 成本
这条线最容易死在两个地方：
1. **下一分钟继续由 BTC 主导单边趋势**，导致 short leader 腿被拖着跑；
2. **双腿 taker 成本** 很容易吞掉 `2~4 bps` 的毛边。

所以 production 前至少要补：
- next-bar open / mid-to-bidask 执行口径
- 双腿手续费 + 滑点
- 超时退出
- `BTC trend continuation` veto
- funding / basis 中性化检查（perp 版本）

## 8. 为什么这条线仍值得进研究池
1. **它补的是 raw alpha，不是又一个解释层。**
   base alpha 很明确：`underreaction catch-up`。

2. **它比“再来一篇 spread MR”更有增量。**
   因为近几天 pairs/stat-arb 已经很多，而这条是更短、更事件化的 relative-value pocket。

3. **repo 给了 live 化脚手架。**
   `trade websocket + DuckDB + 1s/1m/5m resample + lag/corr dashboard` 这套东西，天然适合下一步做 online detector。

## 9. 下一步怎么测
优先按下面 4 个 ablation 走，不要直接上线：

1. **事件阈值 sweep**
   - `q90 / q95 / q97.5 / q99`
   - underreaction 比例从 `0.2 / 0.4 / 0.6`
   - 看 edge 是不是只靠少数极端点撑着

2. **1bar vs 2bar vs adaptive exit**
   - 当前 first verdict 暗示 `2bar` 比 `1bar` 更像可留边
   - 但需要 next-bar 执行后重算

3. **down-shock / up-shock 分书**
   - 当前 proxy 显示 downside 版本更稳
   - 可以拆成两本 alpha，不要强行对称

4. **把 lag-scan 从“解释图表”改成在线 admission**
   - 平时只监控，不交易；
   - 只有 `BTC shock + ETH underreaction + lag0 high / no regime break` 同时满足时才开机。

如果这 4 步之后，`1m/2m` 版本扣完双腿 friction 还能保住正的 `post-cost bps/event`，这条就有资格进入更正式的 event-driven RV replication 池。

## 10. 来源
1. **HerambPatilcoder. (2025/2026). _Crypto_Pairs_trading_. GitHub repository.**
   - Readable URL: <https://github.com/HerambPatilcoder/Crypto_Pairs_trading>
   - Repo URL: <https://github.com/HerambPatilcoder/Crypto_Pairs_trading>
2. **Key repo files used in this digest**
   - README: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/README.md>
   - `analytics/features.py`: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/analytics/features.py>
   - `analytics/mean_reversion_backtest.py`: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/analytics/mean_reversion_backtest.py>
   - `ingestion/binance_websocket.py`: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/ingestion/binance_websocket.py>
   - `config.py`: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/config.py>
   - `app.py`: <https://raw.githubusercontent.com/HerambPatilcoder/Crypto_Pairs_trading/main/app.py>
3. **Public data portability probe**
   - Binance USDⓈ-M public klines: <https://fapi.binance.com/fapi/v1/klines>
   - Local probe script: `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-15_btceth_lagscan_probe.py`
