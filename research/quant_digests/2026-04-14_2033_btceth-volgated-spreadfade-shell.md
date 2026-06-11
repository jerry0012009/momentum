# 别把这份 coursework repo 只读成“学生版 pairs 作业”：对 short-cycle desk，更该先拆的是「BTC-ETH spread z-score fade × middle-volatility gate」这条完整 raw alpha 壳——repo 内置 OOS 改善明显，但 Binance perp `5m/15m` taker 版仍不过线

- 时间：2026-04-14 20:33 UTC
- 类型：2025/26 GitHub repo source audit（`README.md` + `context_files/PAIRS_STRATEGY_PLAN.md` + `context_files/VOLATILITY_FILTER_PLAN.md` + `notebooks/07_pairs_strategy_vol_filter.py` + `report/tables/pairs_cointegration.csv` + `report/tables/pairs_performance.csv` + `report/tables/vol_filter_performance.csv`）+ Binance USDⓈ-M `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**做 `BTC-ETH` 协整 spread 的均值回复：`z > +threshold` 时 short spread（short BTC / long ETH），`z < -threshold` 时 long spread；vol gate 只决定“何时允许开仓”，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/btc-eth/cointegration/spread-zscore/vol-gate/time-stop/cooldown/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：repo source audit + repo embedded results + public-data portability probe

## 1. 这次看了什么
这次主看一个很新的 coursework repo：

- **Authors / Org：** `SidneyyN`（GitHub user）
- **Year：** 2025/26 coursework season
- **Title：** `COMP0051-Algorithmic-Trading-CW`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>
- **Repo URL：** <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>

repo 明面上有两条线：`breakout` 和 `pairs`。但更值得 desk 先收进素材池的，不是 breakout，而是它对第二条线的处理：
> **先用 EDA 承认“BTC lead-lag to ETH/DOGE 太薄，过不了成本”，然后把策略切到更可交易的 `BTC-ETH cointegrated spread fade`。**

这点很值钱，因为它不是盲目坚持 headline idea，而是把**能活的 raw alpha 壳**留下来。

## 2. base alpha 先说清楚
这篇东西的 **base alpha** 不是“vol filter”，也不是“课设参数搜索”。

它真正的 base alpha 是：
> **`BTC-ETH` 的 log-price spread 在协整关系没坏掉时，会围绕局部均值来回摆；当 rolling z-score 偏离太远时，做 spread 回归。**

翻成人话：
- 这是一条标准的 `pairs / stat-arb / relative-value / mean reversion` raw alpha；
- `vol gate` 只是 admission layer；
- `min hold / cooldown / max hold / cost` 是执行和风险壳；
- 所以它符合当前 bot7 要优先补的 **raw alpha 素材池**，不是纯 filter 主题。

## 3. repo 里最值得记住的，不是“会做 pairs”，而是它把完整壳写全了
`notebooks/07_pairs_strategy_vol_filter.py` 已经把一条完整策略壳写明：
- spread：`log(BTC) - 0.678 * log(ETH)`
- rolling z-score：`100` bars
- entry：`|z| > 3`
- exit：回到 `0`
- `min_hold=24` bars、`cooldown=20` bars、`max_hold=384` bars
- sizing：按 `beta` 做双腿 gross `$100k`
- cost：显式 `bps × gross notional`

更关键的是，repo 不是瞎挑 pair。内置表里 `BTC-ETH` 的 Engle-Granger `p=0.0065`、spread ADF `p=0.0015`，半衰期约 `392` 根 `15m`（约 `98h`）；另外两对 `BTC-DOGE / ETH-DOGE` 都不协整。也就是说：
> **它至少先回答了“为什么这对值得做”，不是直接把所有 pair 都丢进 z-score。**

## 4. 这条旁支为什么比直接抄 repo headline 更适合我们 desk
因为这轮最值钱的不是“再复读一次 BTC-ETH pairs”，而是 repo 给了一个很 desk-friendly 的旁支：
> **middle-volatility gate 只管开仓放行，不改 exit。**

repo 自带结果显示，这个 gate 虽然没把 full-sample 直接救成 production，但方向是对的：
- baseline pairs（`5 bps`）full-sample：`71` 笔，gross `+$5,714.89`，net `-$1,385.11`
- vol-gated 版本（`5 bps`）full-sample：`58` 笔，gross `+$4,536.81`，net `-$1,263.19`
- 更关键的是 **OOS**：baseline `-$2,000.32`，vol-gated 变成 `+$162.46`

所以这份 repo 最该记住的一句话不是“pairs trading 有效”，而是：
> **同一条 spread MR，本体没变，但 admission 放在“非极端 spread-vol regime”里，OOS 变得更像能活的 pocket。**

它主要靠什么证明？
> **靠同一 pair、同一 cost 假设下的 baseline vs vol-gated 对照回测，而不是只讲概念。**

## 5. 我这轮怎么把它 desk 化成 `5m/15m` 最小 portability probe
我补了一个 Binance USDⓈ-M public-data 快检，脚本：
- `reports/artifacts/quant_digests/2026-04-14_comp0051_btceth_volgated_probe.py`

输出：
- `reports/artifacts/quant_digests/comp0051_btceth_volgated_probe_summary_2026-04-14.csv`
- `reports/artifacts/quant_digests/comp0051_btceth_volgated_probe_pivot_2026-04-14.csv`

实验口径：
- 数据源：Binance public perpetual klines（公开可得）
- 频率：`15m`（近 `120d`）+ `5m`（近 `45d`）
- pair：`BTCUSDT / ETHUSDT`
- 信号：沿用 repo 的 `beta=0.678`、`100-bar zscore`、`|z|>3`、`min_hold/cooldown/max_hold`
- gate：`spread_vol < 1.2 * rolling_median(spread_vol)`
- 成本：`1 / 2 / 5 bps` 三档

## 6. first verdict：这条 raw alpha 壳是清楚的，但 taker 版只在低摩擦下像 pocket
### 先记 4 个关键数据点
1. **`15m` plain 在当前 Binance perp 上有 gross，但 `5 bps` 明显不过线**：
   - `55` 笔
   - gross `+$3,058.94`
   - net `-$2,441.06`

2. **`15m` 加 vol gate 后，loss 明显收敛**：
   - 允许开仓 bar 占比约 `73.6%`
   - trade entries `55 -> 46`
   - gross `+$3,800.75`
   - net `-$799.25`

3. **`5m` 也是同一个结论：gate 能救一截，但救不到 `5 bps` taker 生产线**：
   - plain：`54` 笔，gross `+$3,850.65`，net `-$1,499.35`
   - vol-gated：`37` 笔，gross `+$3,249.96`，net `-$400.04`

4. **低摩擦 pocket 仍然存在**：
   - `15m vol-gated @ 1 bps`：net `+$2,880.75`，Sharpe-like `1.32`
   - `15m vol-gated @ 2 bps`：net `+$1,960.75`
   - `5m vol-gated @ 2 bps`：net `+$1,789.96`，Sharpe-like `2.70`

所以这轮最诚实的结论是：
> **这不是 broad taker-ready shell，但它也不是“没 edge”。它更像“spread MR 本体成立，edge 主要被 friction 吃掉；vol gate 能让 edge 更集中”。**

## 7. 为什么它仍然值得进入研究池
1. **它补的是 raw alpha，不是又一个 shared gate**：base alpha 很清楚，就是 `cointegrated spread mean reversion`。
2. **它给了完整策略骨架**：entry / exit / sizing / risk / cost 都有，不是只给一个 z-score。
3. **它提供了一个可迁移的旁支**：`vol gate only on entry` 可以服务很多 spread-fade family，不只这一个 pair。

## 8. 下一步怎么测
优先别再做“同口径 taker 版加参数小修小补”，而是直接测更值钱的三件事：
1. **maker-first / passive exit 版**：保留 `15m state`，把执行切成 `5m` 挂单 close-out，看 `2~5 bps` 能否压到 `<=2 bps`；
2. **rolling beta + rolling coint admission**：不要长期抱死 `0.678`，改成过去 `14d/21d` 动态估计，只在 `ADF/coint` 继续通过时开机；
3. **pair basket 化**：把这个壳从单对 `BTC-ETH` 扩到 `BTC-ETH / ETH-SOL / BTC-BNB` 之类 liquid-major universe，检验它是单对特例，还是可扩展的 stat-arb sleeve。

## 9. 来源
1. **SidneyyN. (2025/26). _COMP0051-Algorithmic-Trading-CW_. GitHub repository.**  
   - Readable URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>  
   - Repo URL: <https://github.com/SidneyyN/COMP0051-Algorithmic-Trading-CW>
2. **Repo embedded evidence used in this digest**  
   - `report/tables/pairs_cointegration.csv`  
   - `report/tables/pairs_performance.csv`  
   - `report/tables/vol_filter_performance.csv`  
   - `notebooks/07_pairs_strategy_vol_filter.py`
3. **Public data portability probe**  
   - Binance USDⓈ-M public klines: <https://fapi.binance.com/fapi/v1/klines>
