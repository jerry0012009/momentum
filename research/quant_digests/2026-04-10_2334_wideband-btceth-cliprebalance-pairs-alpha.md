# 别把这份 2025 BTC/ETH pairs repo 只读成入门作业：对 short-cycle desk，更该先测的是「wide-band spread fade × partial clip rebalance」
- 时间：2026-04-10 23:34 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `back_test_v2.ipynb` + `grid_back_test_v1.ipynb` + `checking_stationarity.ipynb` + `get_ohlc_data.ipynb`）+ Binance USDⓈ-M `1m/5m/15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**BTC/ETH relative-value / pairs mean reversion；当 `BTC-ETH` spread 偏离其 rolling mean ± `kσ` 时，做“贵腿回落、便宜腿回补”的双腿 spread fade。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（repo 已给出 `entry + partial sizing + fee` 骨架，但还缺动态 hedge ratio、funding/slippage、time-stop、pair admission 与组合级 risk shell）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/btc-eth/wide-band/partial-rebalance/clip-execution/binance-futures/1m/5m/15m/repo/public-data/cost/risk
- 证据类型：公开 repo 规则证据 + public-data portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = BTC/ETH spread 偏离后的均值回归。**
> 它不是 trend filter，也不是 regime overlay；repo 里真正的交易本体，就是 **双腿 relative-value 的 spread fade**。

## 1. 这次看了什么，为什么这轮值得写
这轮主看的是一个很新、但还没被 desk intake 过的公开 repo：

1. **`amirSamanQ` (2025), _crypto_pairs_stat_arb_. GitHub repository.**
   - Author / Year / Title / Venue：`amirSamanQ` / `2025` / `crypto_pairs_stat_arb` / GitHub repository
   - Repo URL：`https://github.com/amirSamanQ/crypto_pairs_stat_arb`
   - Readable URL：`https://github.com/amirSamanQ/crypto_pairs_stat_arb`
   - README Raw：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/README.md`
   - Notebook Raw（回测）：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/back_test_v2.ipynb`
   - Notebook Raw（参数网格）：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/grid_back_test_v1.ipynb`
   - Notebook Raw（stationarity）：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/checking_stationarity.ipynb`
   - Notebook Raw（data fetch）：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/get_ohlc_data.ipynb`
   - GitHub API metadata：`https://api.github.com/repos/amirSamanQ/crypto_pairs_stat_arb`

这轮值得写它，不是因为它发明了新奇统计学，而是因为它给的是一条 **非常容易压成最小实验的 raw alpha**：

- 标的就 2 条腿：`BTCUSDT` / `ETHUSDT`
- 数据就 Binance Futures 公共 klines
- 信号就 rolling mean / std 的 spread 偏离
- sizing 不是满仓翻面，而是 **partial clip rebalance**
- 代码骨架直接公开，几乎不用猜作者到底怎么下单

对当前 desk 来说，这种材料的价值不在“学术 headline”，而在：

> **它把 pairs / stat-arb 的最小可复现骨架写得足够直白，适合立刻做 `1m → 5m → 15m` portability sanity check。**

## 2. 一句话核心结论
**repo 原始思路是成立的：它确实是一条可复现的 BTC/ETH pairs mean-reversion alpha；但直接照搬到我们 desk 时，更值得保留的不是“固定 7 天 + `k=2.5`”这个参数，而是“wide-band 进场 + partial clip rebalance”这套执行骨架。**

我这轮 public-data probe 的结论是：

- **`5m` 比 `15m` 更像可继续打磨的主 lane；**
- **更宽的 band（`k≈3`）+ 更长的滚动窗（`≈10d`）比 repo 默认参数更适合当前 BTC/ETH 环境；**
- **`15m` 目前更像 relative-value drawdown smoother，不像能直接上线的 standalone raw alpha。**

## 3. repo 里真正写了什么
这份 repo 很小，但骨架够完整：

### 3.1 数据获取
`get_ohlc_data.ipynb` 直接调用 Binance Futures REST：
- endpoint：`/fapi/v1/klines`
- interval：支持 `1m / 5m / 1h ...`
- 通过 sliding window 抓多天历史数据

这意味着它不依赖私有 feed，也不依赖难复现的第三方库，**公开数据可直接重跑**。

### 3.2 stationarity 检查
`checking_stationarity.ipynb` 里作者先对：
- `BTC / ETH` ratio
- `BTC - ETH` difference

做了：
- **ADF**
- **KPSS**

这一步虽然不豪华，但至少说明作者不是“看到两个价格一起动就直接做 pair”，而是先问：

> **这条 spread 到底有没有一点 mean-reverting 统计基础？**

### 3.3 交易逻辑
repo 的核心回测逻辑非常直白：

1. spread 定义为 **`BTC close - ETH close`**（不是 log spread，也不是 rolling beta residual）
2. 用 rolling window 算：
   - `mean_t`
   - `std_t`
3. 阈值：
   - `upper = mean + k * std`
   - `lower = mean - k * std`
4. 若 `spread > upper`：
   - **sell BTC / buy ETH**
5. 若 `spread < lower`：
   - **sell ETH / buy BTC**
6. 每次不是满仓，而是只 rebalance 一个 clip：
   - 默认单次 notional 大小约 **`$200`**
7. 初始资本：
   - `BTC $500 + ETH $500`
8. 手续费：
   - repo 示例使用 **`0.1%`**（`fee_rate=0.001`）

翻成人话：

> **它做的不是“all-in 方向切换”，而是每次 spread 过宽时，拿固定 clip 把组合往均衡方向扳一点。**

这点对 short-cycle desk 很关键，因为它天然比“满仓翻边”更接近可执行版本。

## 4. repo 自带结果里，最值得记住的数字
`back_test_v2.ipynb` 内嵌输出里，作者给的一个示例是：

- 区间：`2025-01-01 → 2025-09-01`
- 参数：`k=2.5`、`window_days=7`
- 频率：README / notebook 口径默认为 **`1m` candles**
- 初始资金：`$1000`
- 手续费：`10bps`

示例输出：
- **Strategy**：`$1927.83`，回报 **`+92.78%`**
- **BTC buy & hold**：`$1156.21`，回报 **`+15.62%`**
- **ETH buy & hold**：`$1311.57`，回报 **`+31.16%`**
- **50/50 组合**：`$1233.89`，回报 **`+23.39%`**
- **总交易数**：`229`

所以这份 repo 至少回答了两件事：

1. **它不是纯概念文档，作者确实把策略写成了回测。**
2. **它的 sizing 不是抽象“做多做空”，而是固定 clip 的 inventory rebalance。**

## 5. 这份材料对当前 desk 真正值钱的，不是 pair formation，而是 clip-based shell
如果把它和我们已经积累的一堆 pairs / stat-arb digest 放一起看，这份 repo 最值钱的地方并不是：

- pair selection 多高级
- hedge ratio 多精细
- statistical test 多全面

而是它给了一个 **很容易转到实盘工程语言** 的雏形：

### 5.1 它是“逐次修正库存”，不是“每次翻满整个 book”
很多 pairs 教程都默认：
- zscore 一超阈值就一把满仓进
- 回到中线就一把全平

但这份 repo 做的是：
- **每次偏离只打一个 clip**
- 让组合逐步向便宜腿倾斜
- 偏离越久，仓位越积累

这在实盘里更像：
- inventory-aware scaling
- 分段入场
- 用偏离次数代替一次性豪赌

### 5.2 它特别适合压到 `5m`
因为 `1m` 上很多 pairs alpha 很容易被：
- 噪音
- funding / taker fee
- 微观结构冲击
- 短期同步跳变

直接吃掉。

而 **clip-based shell + wide band** 恰好是一个非常适合移植到 `5m` 的思路：
- band 放宽一点，减少噪音触发
- clip 分批，避免一次性冲太重
- time-stop/mean-cross exit 后补上即可形成完整最小策略

## 6. 我做的 public-data portability probe
### 6.1 实验口径
我用 Binance USDⓈ-M public klines，对 `BTCUSDT / ETHUSDT` 跑了一版 repo 同款简化逻辑：

- spread：`BTC close - ETH close`
- entry：`spread` 突破 rolling `mean ± kσ`
- action：
  - `spread > upper` → sell BTC / buy ETH
  - `spread < lower` → sell ETH / buy BTC
- 单次 rebalance：`$200`
- 初始：`BTC $500 + ETH $500`
- fee：`10bps`
- 不加 funding / slippage / time-stop
- 先做 `1m / 5m / 15m` baseline，再对 `5m / 15m` 做小网格

本地产物：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_1m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_1m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_5m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_5m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_15m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_15m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_portability_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_grid_portability_2026-04-10.csv`

### 6.2 baseline 结果：原样直搬，并没有天然很强
baseline（`k=2.5`、`window_days=7`）结果：

- **1m / 近 30d**：
  - 策略回报 **`+5.07%`**
  - 50/50 BH **`+6.27%`**
  - excess ≈ **`-1.20%`**
  - 交易数：`8`
- **5m / 近 60d**：
  - 策略回报 **`+4.75%`**
  - 50/50 BH **`+4.96%`**
  - excess ≈ **`-0.21%`**
  - 交易数：`18`
- **15m / 近 120d**：
  - 策略回报 **`-19.07%`**
  - 50/50 BH **`-26.12%`**
  - excess ≈ **`+7.05%`**
  - 交易数：`21`

这说明两件事：

1. **repo 的核心逻辑不是假 edge**，因为它在下跌阶段能明显减轻双腿组合损失；
2. **但默认参数并不能直接证明它就是当前环境下的最优 short-cycle 版本。**

## 7. 小网格后，最值得保留的是 `5m` 的 wide-band 读法
我对 `5m / 15m` 做了一个很小的参数网格：
- `k ∈ {1.5, 2.0, 2.5, 3.0}`
- `window_days ∈ {3, 5, 7, 10}`

### 7.1 `5m` 最优读法：更宽 band、更长窗口
当前样本里，`5m` 最好的组合是：
- **`k=3.0`**
- **`window_days=10`**
- 交易数：`8`
- 策略回报：**`+7.50%`**
- 50/50 BH：**`+5.01%`**
- 相对 BH excess：约 **`+2.37%`**

其次是：
- `k=2.0, window_days=5`
- 回报：**`+5.69%`**
- 交易数：`25`

这说明对当前 desk 更有价值的读法不是“照搬 repo 默认 1m 参数”，而是：

> **在 `5m` 上把触发带放宽，主动少做、但只做更极端的 spread 偏离。**

### 7.2 `15m` 更像防守型 relative-value，不像强 standalone alpha
`15m` 网格里，最好的绝对结果也仍然是亏损：
- **`k=3.0, window_days=5`**
- 策略回报：**`-17.79%`**
- BH：**`-26.08%`**
- 相对 BH excess：约 **`+11.21%`**

所以 `15m` 当前更像：
- **下跌阶段减震器 / overlay**
- 而不是可直接单独上桌的 raw alpha

这正好把 lane 分清楚了：
- **主 lane：`5m`**
- **辅助 lane：`15m`（看相对抗跌，不看绝对盈利）**

## 8. 这轮给 desk 的最值钱结论
### 8.1 要保留的是 shell，不是字面 spread 定义
repo 直接用的是：
- `BTC close - ETH close`

这很方便，但也很粗：
- 没对冲 beta
- 没做 log transform
- 没处理波动尺度差异

所以真正该搬的不是这个 spread 定义本身，而是：
- **wide-band entry**
- **partial clip rebalance**
- **双腿库存逐次修正**

### 8.2 这条线对 short-cycle desk 依然是 raw alpha，不是 filter
尽管我上面一直在讲 shell，但别搞混：
- 本体仍然是 **spread mean reversion**；
- shell 只是把这条 alpha 变得更可执行。

因此这轮主题仍然该归在：
- `raw alpha`
- `pairs / relative value / stat-arb`

而不是 `filter / regime / overlay`。

### 8.3 当前最合理的 desk 改写
如果要把这条线正式往 desk 版本推进，我会建议这样改：

1. **spread 改成 log-beta residual**
   - `spread_t = log(BTC) - beta_t * log(ETH)`
   - `beta_t` 用 rolling OLS / EWLS
2. **保留 partial clip，不做 all-in flip**
   - 单次 clip 可改成组合净值的 `10%~20%`
3. **entry 用 wider band**
   - 当前样本优先看 `k=2.5~3.0`
4. **补退出机制**
   - `z -> 0`
   - 或 `time-stop = 24~48 bars`
5. **把 funding / taker fee 真扣进去**
   - 当前 probe 只扣了简化手续费
6. **把 pair admission 前置**
   - 不要默认 BTC/ETH 永久可做
   - 先测 rolling correlation / cointegration / half-life

## 9. 为什么这轮仍比继续补抽象 filter 更值得
因为这份材料和当前 desk 的 raw alpha 素材池是直接相连的：

- 它不是泛泛讲“市场状态”；
- 它不是单纯讲“相关性变了没”；
- 它给的是一条 **可独立开工、可写成回测、可压到 5m** 的 pairs alpha。

而且它有一个额外优点：

> **即便最终 BTC/ETH 这对不够强，这套 shell 也能直接迁移到别的 majors pair。**

也就是说，这轮 intake 的价值不只在单一 pair，而在 **execution skeleton**。

## 10. 下一步怎么测
最值得立刻做的是一个很小但诚实的 A/B/C：

### A. repo faithful baseline
- 标的：`BTCUSDT / ETHUSDT`
- bar：`5m`
- spread：`BTC - ETH`
- `k = 2.5 / 3.0`
- `window_days = 7 / 10`
- clip：固定 notional 或 NAV `15%`
- exit：不开额外 time-stop，先看原始 shell

### B. spread 升级版
- spread 改为 `log-beta residual`
- beta 窗口：`288 / 576` bars
- 比较：
  - trade count
  - net bps / trade
  - holding bars
  - max inventory tilt

### C. execution honest版
- fee：`8 / 12 / 16 bps`
- funding：按真实 funding 扣减
- exit：`z -> 0` 或 `24 / 48` bars time-stop
- 输出：
  - 每笔净 bps
  - 按方向拆的胜率
  - 连续加仓次数分布
  - 极端偏离下的库存占用

如果 B 明显优于 A，说明可继续升成 desk 级 pair shell；
如果 B 也只是在熊市里相对抗跌，那就把它降级成：
- `relative-value drawdown smoother`
- 而不是主 alpha 书。

## 11. 风险与保留意见
1. **repo 当前只做 BTC/ETH。**
   - 它更像 pair shell demo，不是完整 pairbook。
2. **spread 定义偏粗。**
   - 直接用价格差，而不是对冲后的 residual，容易把趋势差异误当均值回归。
3. **成本仍偏乐观。**
   - repo/本地 probe 都没把 funding / slippage / queue position 认真写进去。
4. **当前 `15m` 结果不支持把它吹成可直接上线的完整 raw alpha。**
   - 最多说明它在风险收缩期可能有相对抗跌价值。

## 12. 这轮给 Jerry 的一句话建议
**把这份 repo 收进素材池，但别照抄它的 spread 定义；优先保留的是 `5m` 上“wide-band + partial clip rebalance”的 pair shell，再用 `log-beta residual + honest costs` 做一次 desk 版最小复现。**

## 13. 来源
1. **amirSamanQ (2025). _crypto_pairs_stat_arb_. GitHub repository.**
   - Repo URL：`https://github.com/amirSamanQ/crypto_pairs_stat_arb`
   - README Raw：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/README.md`
   - Backtest notebook：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/back_test_v2.ipynb`
   - Grid notebook：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/grid_back_test_v1.ipynb`
   - Stationarity notebook：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/checking_stationarity.ipynb`
   - Data fetch notebook：`https://raw.githubusercontent.com/amirSamanQ/crypto_pairs_stat_arb/main/get_ohlc_data.ipynb`
   - GitHub API metadata：`https://api.github.com/repos/amirSamanQ/crypto_pairs_stat_arb`

### 本地实验产物
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_1m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_1m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_5m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_5m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_15m_series_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_15m_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_portability_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/amir_pairs_grid_portability_2026-04-10.csv`
