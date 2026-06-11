# 别把 `ATR compression → ROC ignition` 当 shared anti-chop：它在 15m 更像 breakout-short 的 short-side re-arm gate，对 Fib / EMA long 明显有害
- 时间：2026-03-20 12:53 UTC
- 类型：GitHub 仓库 + Binance 公共数据代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/atr/compression/roc/ignition/re-arm/asymmetry/continuation/failure/filter/repo/crypto/15m
- 证据类型：仓库代码（工程证据）+ 公开 OHLCV 最小代理快检

## 1. 这次看了什么
这轮主看一个近 5 年新仓库：**ricketter1984/my-futures-trading-bot（2025）**。它的 headline 是“consolidation breakout + momentum ignition”，但这次我没有照搬它整套 futures 模板，而是只拎出一个更适合我们当前收口线的旁支：

- `src/strategy.py::is_consolidating()`：用 **ATR14 低于其近 20 根平均 ATR 的 0.7 倍** 定义压缩；
- `src/strategy.py::get_momentum_ignition_signal()`：用 **ROC(5) 超过 ±0.5%** 定义点火；
- 把这两个模块理解成 **breakout 之后能不能 re-arm / follow-up** 的短周期过滤层，而不是独立开仓系统。

之所以这题比继续泛化别的方向更值得做，是因为它**直接回答当前第一优先收口线**：`V3 final-verdict / breakout-short follow-up` 到底要不要再加一个便宜、price-only 的 re-arm 条件；同时也能顺手回答它能不能 shared 到 `Fib retest_hold / EMA-PSAR raw alpha`。

## 2. 核心结论
- **一句话核心结论：** `ATR compression → ROC ignition` 不适合升成三条线共享的 anti-chop / re-arm gate；它在 15m 上更像 **breakout-short 的 short-side 可选 re-arm 层**，而不是 Fib / EMA long 的 shared 放行键。
- **一句话证明方式：** 我按 repo 的 strict 口径，在 Binance 公共 `BTC/ETH/SOL` perp 近 **120 天** 15m 上，对比 `raw 20-bar breakout`、`strict ATR compression + ROC ignition`、以及一个更宽松的 `mild` 版本，检查 4-bar signed return 与 re-entry 率。

关键数据点：
1. **repo 原味 strict 规则只对 short 侧像样，但样本很稀。** `short raw` 合并均值约 **+5.7 bps**、re-entry 约 **72.2%**；`short strict comp+ign` 只有 **16** 笔，但均值约 **+38.7 bps**、re-entry 降到 **56.7%**。说明它更像稀疏高门槛的 short re-arm，不像 shared 默认键。
2. **同一套 strict 规则放到 long 侧明显变坏。** `long raw` 合并均值约 **-0.8 bps**、re-entry 约 **77.3%**；`long strict comp+ign` 仅 **16** 笔，但均值掉到 **-58.7 bps**，re-entry 反而升到 **84.1%**。也就是：**压缩后点火 ≠ long continuation 更干净**。
3. **放宽到 mild 版本后，short 侧还保留一点边，long 侧仍然不行。** `short mild comp+ign` 有 **217** 笔，均值约 **+9.9 bps**、re-entry 约 **68.9%**；但 `long mild comp+ign` **205** 笔，均值约 **-14.3 bps**，仍显著差于 raw long。对 desk 来说，这意味着**如果要先测，先测 short-side soft re-arm，不要镜像到 long 侧**。

## 3. 为什么和当前三条收口线有关
### V3 final-verdict / breakout-short follow-up
这是这轮最直接受益的线。当前收口线缺的不是再堆一个“反震荡”名词，而是**breakdown 之后哪些短暂压缩再点火，值得允许 second-leg / follow-up**。这轮证据支持：
- `ATR compression → ROC ignition` 可以先作为 **breakout-short 的 short-side re-arm 候选**；
- 但它更像 **高门槛附加层**，不是 shared default admission；
- strict 太稀，mild 版更适合先做最小实验。

### Fibonacci confirmation / retest_hold
这轮基本是在提醒：**别镜像。** 同样的压缩→点火逻辑，放到 long retest / hold 侧不但没更稳，反而更容易回到破位线附近。也就是说，它不该被写成 `Fib retest_hold` 的默认确认骨架。

### EMA / PSAR raw alpha focus
对 EMA / PSAR，这轮更像**角色排雷**：
- 如果把它强行 shared 化，会把 long continuation 弄坏；
- 更合理的做法，是把它单独放在 **short-side continuation / failure follow-up** 桶里测试；
- 对 raw alpha 主干，先别让它接管 admission 层。

## 4. repo 里最值得复用/复现的点
这轮真正有价值的不是“ATR 或 ROC 本身”，而是 repo 把它们写成了**先压缩、后点火**的状态机：
1. **压缩定义足够便宜**：`current_atr < avg_atr * 0.7`，完全 price-only；
2. **点火定义也足够直接**：`ROC(5)` 过阈值，而不是等一堆复杂共振；
3. **天然适合作为 re-arm / follow-up 层**，因为它描述的是“刚压缩过、现在重新发动”。

翻成人话：这不是新的主信号，更像是一个**短促再加速标签**。问题不在它能不能算出来，而在它**只能用于哪一边、哪一层**。

## 5. 这轮最小代理快检怎么做的
### 事件定义
- `raw long`：收盘价突破前 **20** 根最高价；
- `raw short`：收盘价跌破前 **20** 根最低价；
- `strict comp`：前一根 `ATR14 / mean(ATR14,20) < 0.7`；
- `strict ignition`：`ROC(5) > +0.5%`（long）或 `< -0.5%`（short）；
- `mild comp`：前 **4** 根里最小 `ATR ratio < 0.8`；
- `mild ignition`：`ROC(5) > +0.4%`（long）或 `< -0.4%`（short）。

### 观察指标
1. **4-bar signed return（bps）**
2. **4-bar re-entry rate**：未来 4 根内是否回到突破线反侧

### 样本
- 资产：BTC / ETH / SOL perpetual
- 周期：15m
- 区间：近 120 天
- 用途：只做角色判断与最小实验排序，不等于完整策略回测

## 6. 可复刻的最小实验（下一步怎么测）
### 研究假设
`ATR compression → ROC ignition` 不是三条线 shared gate；它只可能在 **breakout-short** 里，以 **short-side re-arm / follow-up filter** 的形式成立。

### 第一轮应先冻结的实现
- 只挂到 `breakout-short follow-up`，**不要接到 Fib / EMA long**；
- 先测两个版本：
  1. `strict`: `ATR ratio<0.7` + `ROC5<-0.5%`
  2. `mild`: `min ATR ratio(last4)<0.8` + `ROC5<-0.4%`
- 入场仍沿用 breakout-short 当前 baseline，不改主触发；它只负责 **允许 second-leg / re-arm**。

### 最小回测切口
- 资产：BTC / ETH / SOL perp
- 周期：15m 信号，必要时补 5m 执行层
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap`
- 成本：先看 **6 / 10 / 15 bps per side**

### 先看哪 3 个指标
1. `post-cost expectancy`（只看 short follow-up 子样本）
2. `trade retention`（相对 baseline 还剩多少交易）
3. `false-follow / re-entry rate`（是否明显减少 back-inside）

### 最该补的两个切片
- **时段切片**：Asia / Europe / US active hours 分开看，确认 short 边是不是集中在特定时段；
- **路径切片**：区分 `first break` 与 `follow-up / re-arm`，避免把“初始破位”和“二次发动”混在一起。

## 7. 风险与保留意见
- 这轮是 **repo 模块 + 公共数据代理快检**，不是完整策略级回测；
- strict 版本样本只有 **16** 笔 short，统计不稳，不能直接升正式 gate；
- mild 版本虽然样本够一些，但提升幅度并不大，可能一上成本就被吃掉；
- 当前结论应理解为：**“只值得 short-side follow-up 先测”**，不是“这就是 breakout-short 的终版答案”。

## 8. 来源
1. **ricketter1984. (2025). _my-futures-trading-bot_. GitHub repository.**
   - Authors: GitHub user `ricketter1984`
   - Year: 2025
   - Title: My Futures Trading Bot — Consolidation Breakout with Momentum Ignition Strategy
   - Venue: GitHub
   - DOI: `N/A`
   - Readable URL: `https://github.com/ricketter1984/my-futures-trading-bot`
   - Repo URL: `https://github.com/ricketter1984/my-futures-trading-bot`
   - Key files:
     - `https://github.com/ricketter1984/my-futures-trading-bot/blob/main/src/strategy.py`
     - `https://github.com/ricketter1984/my-futures-trading-bot/blob/main/src/indicators.py`

2. **Binance. (2026). _USDⓈ-M Futures Market Data REST API: Kline/Candlestick Data_.**
   - Authors/Org: Binance
   - Year: 2026 (live docs)
   - Venue: Official API docs
   - DOI: `N/A`
   - Readable URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Data URL example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`
   - 公开性：公开可得
   - 更新频率：逐根 K 线更新（15m）
   - 最小可复现实验口径：BTC / ETH / SOL perp，15m breakout 事件法，4-bar follow-up / re-entry

---
快检文件：
- `reports/artifacts/literature/atr_roc_ignition_pool_summary_2026-03-20.csv`
- `reports/artifacts/literature/atr_roc_ignition_asset_summary_2026-03-20.csv`
- `reports/artifacts/literature/atr_roc_ignition_event_examples_2026-03-20.csv`
- `reports/artifacts/literature/atr_roc_ignition_metadata_2026-03-20.json`
