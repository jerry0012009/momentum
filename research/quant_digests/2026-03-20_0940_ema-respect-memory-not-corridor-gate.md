# 别把 EMA 回踩确认继续写成“贴线越近越好”：`recent EMA respect score` 在 15m 只够做轻量 admission，`ATR corridor` 反而容易过筛
- 时间：2026-03-20 09:40 UTC
- 类型：GitHub 仓库 + Binance 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/ema-respect/memory-score/atr-corridor/admission/filter/repo/crypto/5m/15m
- 证据类型：仓库代码（工程证据）+ 公开 OHLCV 代理快检

## 1. 这次看了什么
这次主看 **noahfm / continuation-screener（2026-02 仍有更新）**。这轮不抄它的美股选股框架，而是只抽一个更适合我们 desk 的旁支：
**把“最近是否反复尊重 EMA9”量化成记分（`ema_bounce_score`），再和“离 EMA9 的 ATR 距离上限”分开评估。**

仓库里对应实现很清楚：
- `ema_bounce_score`: 最近窗口里统计 `low` 贴近 `EMA9`、且 `close>EMA9` 的“尊重次数”；
- `stacked_emas`: 额外限制 `dist_to_ema9 <= 0.75 ATR`、`depth >= -0.8 ATR` 等走廊条件。

## 2. 核心结论
- **一句话核心结论：** 对 5m/15m crypto，`EMA respect memory` 可以当轻量上下文，但把它再收紧成 `ATR corridor + depth` 的硬门，容易把信号质量和交易密度一起筛坏。  
- **一句话证明方式：** repo 给了可计算规则；我用 Binance Futures `BTC/ETH/SOL 15m` 近 `6000` 根/币做了最小代理，比较 `base`、`score>=2`、`score>=2 + dist/depth` 三档在未来 `4 bars` 的表现。

关键数据点（聚合 `ALL`）：
1. **long 侧**：`base` 平均 `-0.80 bps`（扣 12 bps 成本后 `-12.80 bps`），加 `score>=2` 后到 `+0.46 bps`（净 `-11.54 bps`），只改善约 **+1.26 bps**，属于“轻微减亏”。
2. long 再加 `dist<=0.75 + depth` 后反而恶化：均值到 `-10.21 bps`（净 `-22.21 bps`），胜率降到 **38.3%**（`base` 为 **45.8%**）。
3. **short 侧**：`base` 净值约 `-6.66 bps`；加 `score>=2` 几乎无增量（`-6.85 bps`）；加 `dist<=0.75` 后明显变差到 `-11.13 bps`。

翻成人话：
- “最近确实常在 EMA9 附近守住”有一点信息；
- 但“必须贴得很近、且最近不能刺破太深”这类硬走廊，在 15m 上更像是过拟合式严筛，不像稳健提升器。

## 3. 为什么和当前三条收口线有关
- **V3 final-verdict / breakout-short follow-up**：这轮直接提醒我们，不要把 long 语境下的 `ATR distance corridor` 生搬给 short follow-up；镜像后 short 质量并没有变好。  
- **Fibonacci confirmation / retest_hold**：`recent EMA respect score` 可以当“趋势健康度旁证”（轻量 admission），但不该升级成单一硬门。  
- **EMA / PSAR raw alpha focus**：更诚实的路线是“先加轻量记分，再看是否真改善成本后表现”，而不是继续堆越来越硬的距离阈值。

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 15m 上，`memory-score` 适合做软分层（admission/sizing），`hard corridor` 不适合做共享准入门。

### 一个可计算定义（先冻最小版）
1. `score14`：过去 14 根里，满足 `low ∈ EMA9±0.5%` 且 `close>EMA9` 且 `close>open` 的次数；
2. 分档：
   - `score<2`：不加分（或半仓）
   - `score>=2`：允许正常 admission
3. 暂不默认加 `dist<=0.75` 与 `depth>=-0.8` 硬门（只保留为对照组）。

### 最小回测切口
- 资产：`BTC/ETH/SOL` perpetual
- 周期：`15m`（可补 `5m` 做执行细化）
- 样本：先近 `180d`
- 执行：`next-bar open`、`no-overlap`
- 成本：`6 / 10 / 15 bps per side`

### 先看哪 2 个指标
- `post-cost expectancy`
- `trade_count retention`（防止“只靠砍单变好看”）

## 5. 风险与保留意见
- 主证据来自仓库代码 + 代理快检，不是论文级因果识别；
- continuation-screener 原场景是美股筛选，不是 crypto perp；我们只借“特征定义”，不借其收益结论；
- 当前快检是固定 `4-bar` 观察窗，仍需在 `8/12-bar` 与完整出场规则下复核。

## 6. 来源
1. **noahfm. (2026). _continuation-screener_. GitHub repository.**
   - Authors: GitHub user `noahfm`
   - Year: 2026（仓库最新提交 2026-02）
   - Title: Russell 3000 Trend Continuation Screener
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/noahfm/continuation-screener/blob/main/README.md`
   - Repo URL: `https://github.com/noahfm/continuation-screener`
2. **关键实现：`trend_screener.py`（`ema_bounce_score` / `stacked_emas`）**
   - Readable URL: `https://github.com/noahfm/continuation-screener/blob/main/src/continuation_screener/trend_screener.py`
3. **关键实现：`entry_exit.py`（reclaim 逻辑）**
   - Readable URL: `https://github.com/noahfm/continuation-screener/blob/main/src/continuation_screener/simulator/entry_exit.py`
4. **Binance. USDⓈ-M Futures Kline API（公开数据）**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - 公开性：公开可得
   - 更新频率：逐根 K 线更新（5m/15m）

---
快检文件：
- `reports/artifacts/literature/ema_respect_memory_distance_quickcheck_2026-03-20.csv`
- `reports/artifacts/literature/ema_respect_memory_distance_events_2026-03-20.csv`
- `reports/artifacts/literature/ema_respect_memory_distance_meta_2026-03-20.json`
