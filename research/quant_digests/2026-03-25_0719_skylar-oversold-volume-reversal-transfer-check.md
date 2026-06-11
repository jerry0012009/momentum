# 别把“急跌 + 放量 = 必反弹”直接照抄到 perp：这份 2025 新仓库给的是 raw alpha 骨架，但 15m transfer 先判负
- 时间：2026-03-25 07:19 UTC
- 类型：2025 GitHub 新仓库 + Binance Futures 公共 15m K 线最小快检
- 主题类型：raw alpha
- 基础 alpha：单币在 `1h` 内出现明显急跌、且成交量显著高于过去 `24h` 均值时，市场更像进入短期 oversold / panic flush，后续 `4h~24h` 有均值回归反弹
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/single-asset/oversold/panic-flush/abnormal-volume/transfer-test/binance/perpetual/15m/1h/4h/12h/24h/repo
- 证据类型：仓库规则拆解 + 本地公共数据快检

> 先回答 base alpha：**这不是 filter，也不是风险层。base alpha 就是“急跌 + 异常放量之后的短期反弹”**。它本身就是可独立交易的单资产 mean-reversion 候选，只是这轮把它搬到 Binance perp / 15m 执行口径后，默认版本先没有活下来。

## 1) 这次看了什么
主线材料是一个很新的 GitHub 仓库：
- **Skylar Shi (2025), _crypto-stat-arb_**

仓库的规则并不复杂，反而很适合做 bot7 intake：
- 不是抽象综述；
- 不是只给个 feature；
- 而是直接给了 **entry / hold / cost / no-overlap** 的最小完整骨架。

仓库原始读法：
- **Entry**：`1h return <= -2%` 且 `当前成交量 / 过去24h平均成交量 >= 1.5`
- **Hold**：测试 `4h / 8h / 12h / 24h`，作者声称 `24h` 最优
- **Cost**：`20 bps` 单边（round-trip `40 bps`）
- **Universe**：`BTC / ETH / SOL / AVAX`
- **市场**：Kraken 小时级现货

所以它很像一句人话：

**“单币在 1 小时内被砸得够狠、同时还放量，别急着追着杀；更值得先测的是后面的 oversold bounce。”**

## 2) 核心结论
- **一句话核心结论：** 这份 2025 新仓库提供的是一条很干净的单资产 raw alpha 骨架，但把它原样搬到 **Binance USDⓈ-M perp + 15m 执行** 后，默认参数在近 `180d` 快检里 **四个持有窗全部为负**，所以当前更诚实的结论不是“admit”，而是 **先判 transfer fail / 仅保留 extreme capitulation pocket 线索**。
- **一句话证明方式：** 仓库声称在 `Dec 2025` 的 `20` 个交易日里、`22` 笔交易上做到 **+34.33% total return / 72.7% win rate / 8.2% max DD**；但我把同一逻辑映射到 Binance perp 的 `180d` 公共数据后，按 `next 15m bar` 执行、`40 bps round-trip` 成本口径回测，`1h / 4h / 12h / 24h` 四档平均单笔净收益全部为负。

3 个关键数据点：
1. **仓库自报表现**（Kraken hourly spot，`Dec 2025`，`20` 交易日）：**`+34.33%` 总收益、`72.7%` 胜率、`8.2%` 最大回撤、`22` 笔交易**；作者把它解读为“高成交量暴跌后的 24h 反弹”可系统化捕捉。
2. **本地 transfer 快检**（Binance USDⓈ-M，近 `180d`，4 币，信号按 `1h` 生成、执行落到下一根 `15m`）：默认阈值 `ret_1h<=-2% & vol_ratio>=1.5` 下，**`1h / 4h / 12h / 24h` 平均单笔净收益分别约为 `-1.83% / -2.25% / -2.17% / -2.21%`**，交易数分别为 **`202 / 172 / 143 / 128`**。
3. **唯一能勉强留下的 pocket**：若把信号压到极端样本——**`1h shock <= -5%` 且 `volume ratio >= 4.0`**——在 **`12h` 持有**上，平均单笔净收益约 **`+4.07%`**，但样本只有 **`5` 笔**，目前只能当成“极端清算/投降式反弹”的线索，不能直接升成主策略。

## 3) 为什么和当前 desk 直接相关
这条线和当前 desk 直接相关，不是因为它已经能上线，而是因为它补的是**我们当前更需要继续扩充的 single-asset mean-reversion 原料池**：
- 它不是 breakout / retest 的旧分支；
- 它给的是**完整 raw alpha 骨架**；
- 而且天然适合拆成两层：
  1. **主信号**：急跌 + 放量后的反弹
  2. **执行 / regime layer**：到底是普通 oversold，还是 liquidation-style capitulation

对 `1m / 3m / 5m / 15m` desk 来说，这条线最有价值的地方在于：
- 信号逻辑非常便宜；
- 公共数据就能先做 yes/no；
- 很容易继续下钻到更微观的执行层。

所以它即便当前 transfer fail，仍然值得留在研究池里做 **“极端事件 pocket”** 的下一轮实验，而不是整条丢掉。

## 3.5) 策略拆解（必填）
- 方向属性：single-asset / mean-reversion / event-driven
- 基础 alpha：单币在 `1h` 内被异常放量地急砸后，后续 `4h~24h` 更容易出现 oversold bounce
- entry：
  - 在 `1h` 级别计算 `close-to-close return`
  - 若 `ret_1h <= -2%` 且 `volume / rolling_mean_24h >= 1.5`，则在下一根 `15m` bar 开始做多
- exit：
  - 先测固定持有 `1h / 4h / 12h / 24h`
  - 第二步可替换成 `bounce-to-VWAP`、`revert-half-shock`、或 `ATR trailing` 的诚实出场
- sizing：
  - 第一版单币等权 / 固定 notional
  - 第二版按 `inverse-vol` 或 `shock size capped sizing`
- risk / veto：
  - 单币 no-overlap
  - funding / basis 极端同向时 size-down
  - news candle / listing day / macro print 时段单独标记
  - 若出现连续 cascade，禁止无限抄底加仓
- cost：
  - 必须显式计入手续费 + spread + 冲击
  - 本次 desk transfer 快检用 **`20 bps/side`，即 `40 bps round-trip`**

## 4) 这条线最该怎么读：不是“repo 说 24h 最优”，而是“它到底在什么市场结构里才成立”
如果机械照抄仓库，很容易得到一句过于轻松的结论：
- “大跌放量就买，拿 24h 就行。”

但把它翻成人话后，当前更诚实的 desk 读法其实是：

1. **repo 里看到的，不一定是一般性 oversold bounce，而更可能是 `Dec 2025` 某段 rebound tape 的局部 pocket；**
2. **Kraken 现货小时级反弹，不等于 Binance perp 的短周期反弹；**
3. **如果这条线真有 residual edge，当前更像坐落在“极端清算 / 情绪投降”那一小撮事件里，而不是普通 `-2% + 1.5x volume`。**

换句话说：
**这轮最值钱的不是“学到一个新抄底模板”，而是把一个看起来很完整的 raw alpha，快速判断成“默认版不行，极端版也许值得继续测”。**

## 5) 可复刻的最小实验（1m/3m/5m/15m 起步）
**数据源与公开性：**
- 数据源：Binance USDⓈ-M Futures Kline / Candlestick Data
- 公开性：公开可得，无需 API key
- 更新频率：可直接拿到 `1m / 3m / 5m / 15m / 1h`

**本轮最小实验口径：**
- universe：`BTCUSDT / ETHUSDT / SOLUSDT / AVAXUSDT`
- signal timeframe：`1h`
- execution timeframe：`15m`
- signal：`ret_1h <= -2%` 且 `vol_ratio_24h >= 1.5`
- execution：下一根 `15m` close 近似进场（快检口径）
- hold：`1h / 4h / 12h / 24h`
- overlap：同币 no-overlap
- cost：`20 bps/side`

**最先看 5 个指标：**
1. `avg net return / trade`
2. `win rate`
3. `trade count`
4. `shock threshold × volume threshold` 网格稳定性
5. `signal-to-fill decay`（信号 bar 结束到执行 bar 之间，edge 掉了多少）

## 6) 下一步怎么测（直接可执行）
1. **把默认 shock 压到“真 capitulation”区间**：先做 `shock <= -4% / -5% / -6%` 与 `vol_ratio >= 3 / 4 / 5` 网格，别再停在 `-2% + 1.5x` 这种太宽的定义。
2. **加入 perp crowding 条件**：只在 `funding 同向极端 + OI flush / long liquidation cluster` 时接这条反弹，验证它是不是本质上更像 liquidation-rebound alpha。
3. **把固定持有改成结构性出场**：
   - `revert 50% of shock`
   - `reclaim rolling VWAP`
   - `first 15m lower-high failure`
   这三种 exit 比“死拿 24h”更像 desk 真实执行口径。
4. **执行下钻到 `5m / 1m`**：现在已经知道信号本身不够强，下一轮要确认问题是“alpha 不存在”，还是“15m entry 已经太慢”。
5. **拆 spot / perp 差异**：同样规则分别在 Kraken/Binance spot 与 Binance perp 做 A/B，对照 funding / leverage / 24/7 panic unwind 是否改写结果。

## 7) 风险与保留意见
- 这轮不是对 repo 的逐行 faithful replication，而是**面向 desk 的 transfer test**。
- 仓库样本非常短：`20` 个交易日、`22` 笔交易；这个量级更像“有趣 pocket”，不是稳健结论。
- 我这轮快检在执行上用了 `next 15m bar` 近似，且不同持有窗共用了同一组信号，所以这里只能读成 **sanity check**，不是最终 production backtest。
- 如果后续极端 pocket 成立，也要高度怀疑它的容量、可持续性和新闻依赖性——它更可能是 **event alpha**，不是日常均值回归底仓。

## 8) 来源
1. **Skylar Shi (2025), _crypto-stat-arb_. GitHub repository.**
   - Venue: GitHub
   - Repo URL: `https://github.com/skylarshi123/crypto-stat-arb`
   - README Raw URL: `https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md`
   - Performance JSON Raw URL: `https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/performance_metrics.json`
   - GitHub API metadata: `https://api.github.com/repos/skylarshi123/crypto-stat-arb`
   - 说明：仓库创建时间 `2025-12-31T08:54:06Z`，更新于 `2026-01-01T00:56:23Z`
2. **Binance Developers. USDⓈ-M Futures Kline/Candlestick Data.**
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`

## 9) 本地产物
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/summary.json`
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/hold_summary.csv`
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/per_symbol_summary.csv`
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/threshold_grid_12h.csv`
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/trades.csv`
- `reports/artifacts/quant_digests/skylar_oversold_reversal_transfer_20260325/notes.txt`
