# 别把这份 2026 SMC repo 只读成“形态大全”：对 short-cycle desk，更该先测的是「liquidity-sweep × discount/premium reclaim」这条 raw alpha

- 时间：2026-04-12 23:04 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/single-asset/mean-reversion-continuation/smart-money/liquidity-sweep/order-block/fvg/premium-discount/atr-stop/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：2026 GitHub repo source audit（GitHub API + `README.md` + `config.yaml` + `src/strategies/smart_money.py`）+ Binance USDⓈ-M `15m/5m` public-data probe

- 主题类型：raw alpha
- 基础 alpha：**先等价格扫掉前高/前低流动性，再观察它是否回到 discount/premium 区并与 order block / FVG 重合；若结构没坏，下一段更像回到原方向，而不是继续单边延伸。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = liquidity sweep 后的 reclaim continuation。**

不是泛泛的“SMC 很复杂”，也不是把 FVG / order block 当装饰词。翻成人话：
1. 市场先去扫前高/前低，把追单和止损打出来；
2. 但收盘没有顺着扫破方向继续走，反而收回关键结构；
3. 如果当前位置又刚好落在 discount / premium 区，并和 order block 或 FVG 重合，
4. 那下一段更像**回原方向**，不是继续追 breakout。

所以它是：
- `raw alpha`
- 单资产、结构型、带明确 entry/exit 的完整 strategy shell
- 不是纯 filter
- 不是 regime overlay
- 也不是又一篇解释型“SMC 教程”

## 2. 这次看了什么

主材料是一个很新的仓库：

### 主来源（repo）
- **mefai-dev (2026)**
- **Title**：*Mefai Autotrade*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL / Repo URL**：<https://github.com/mefai-dev/mefai-autotrade>
- **Repo metadata**：创建 `2026-03-25`，最近 push `2026-04-08`，stars `3`

这轮重点看的不是它“大而全”README，而是里面的 `src/strategies/smart_money.py`。源码把 SMC 拆成了 6 个可计算部件：
- swing high / low
- BOS / ChoCH
- order block
- fair value gap
- liquidity sweep
- premium / discount + Fibonacci

真正有用的地方在于：它不是只给术语，而是已经把这些对象写成了**能直接进策略状态机的代码**。

## 3. repo 真正实现了什么

### 3.1 `smart_money.py` 里的 entry 本体并不神秘
源码核心其实很直白：
- 先找 swing points；
- 用最近两个 swing high / low 判当前结构是 bullish 还是 bearish；
- 再标记 order block 与 FVG；
- 再检查当前 bar 是否发生 liquidity sweep；
- 最后按 confluence 打分，达到阈值就开仓。

### 3.2 关键不是“概念多”，而是哪些概念该当 alpha 本体
repo 的 literal 版逻辑是：
- 只要 `order block / FVG / structure / liquidity sweep / premium-discount / fib` 里满足够多项，就能开仓；
- 默认 `min_confluence = 3`；
- 止损是 `1.5 x ATR`；
- 止盈优先看最近 swing，再退回 `2R`；
- 出场还能被 ChoCH 提前打断。

但对 desk 来说，最值钱的不是“confluence>=3”这句空话，而是下面这条更窄、更像真钱入口的分支：

> **必须先有 liquidity sweep，再要求当前位置处在 discount/premium zone，并且同时贴着 order block 或 FVG。**

也就是这轮真正值得 intake 的，不是整个 SMC 大壳，而是：
- `liquidity_sweep` = 触发器
- `premium / discount` = 位置约束
- `order block / FVG` = 失衡回补锚点
- `ATR stop + swing / 2R tp` = 完整执行壳

## 4. public-data probe：literal 大壳不行，但 desk 化的 sweep-reclaim 分支在 15m 是正的

为了避免只写 repo 读后感，我用 Binance USDⓈ-M 公共 K 线做了最小 portability probe。

### 4.1 数据口径
- 数据源：Binance Futures public `fapi/v1/klines`
- 标的：
  - `15m`：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT`
  - `5m`：`BTCUSDT / ETHUSDT`
- 样本：
  - `15m`：`2026-01-01 ~ 2026-04-12`
  - `5m`：`2026-03-01 ~ 2026-04-12`
- 公开性：完全公开可抓
- 更新频率：分钟级可持续刷新

本地 artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_summary_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_trades_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_aggregate_2026-04-12.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/smc_sweep_reclaim_probe_costladder_2026-04-12.csv`

### 4.2 先说坏消息：literal repo 版就是过度交易
按 repo 原意做 `confluence >= 3` 的 literal 版，结果很差：

#### `15m` literal（4 币合并）
- 交易数：`2061`
- 胜率：`42.7%`
- 平均：`-2.46 bps/笔`
- 累计：`-5061.42 bps`
- 平均持有：`15.1 bars`

#### `5m` literal（2 币合并）
- 交易数：`1317`
- 胜率：`44.6%`
- 平均：`-2.17 bps/笔`
- 累计：`-2852.77 bps`

一句话：

> **别把 smart money 大壳直接等同于 alpha。literal 版本质上是在“见结构就上”，交易太密，质量太差。**

### 4.3 真正有意思的，是 desk 化的 `sweep_reclaim` 分支
我把 entry 改成更窄的 desk 读法：
- 必须先出现 `liquidity sweep`
- 且方向结构未坏
- 且当前位置在 `discount / premium` 区
- 且至少命中 `order block` 或 `FVG`
- 总分至少 `4`

#### `15m` sweep_reclaim（4 币合并）
- 交易数：`369`
- 胜率：`53.7%`
- 平均：`+5.76 bps/笔`
- 中位数：`+3.42 bps/笔`
- 累计：`+2124.37 bps`
- 平均持有：`7.75 bars`

这组数最重要的含义不是“已经可上线”，而是：

> **当你强制要求“先扫流动性，再 reclaim 关键结构”，SMC 才开始像一条可交易 raw alpha，而不是一堆图形标签。**

### 4.4 `5m` 不成立，说明这题不是越快越好
#### `5m` sweep_reclaim（2 币合并）
- 交易数：`179`
- 胜率：`44.1%`
- 平均：`-6.10 bps/笔`
- 累计：`-1091.92 bps`

这说明：
- 这条 alpha 不是天然的 `5m taker` 书；
- 更像 `15m first lane`；
- 再往快周期压，会被更多噪音 wick 和手续费吃掉。

### 4.5 哪些币最像值得继续测的 pocket
`15m sweep_reclaim` 分 symbol 看：
- `XRPUSDT`：`88` 笔，胜率 `58.0%`，平均 **`+14.76 bps/笔`**
- `ETHUSDT`：`97` 笔，胜率 `56.7%`，平均 **`+4.53 bps/笔`**
- `SOLUSDT`：`99` 笔，胜率 `49.5%`，平均 **`+2.47 bps/笔`**
- `BTCUSDT`：`85` 笔，胜率 `50.6%`，平均 **`+1.67 bps/笔`**

这很像一个典型 desk 结论：
> **这条 raw alpha 不是“全资产平均有效”，而是更偏高 beta majors / alt-major 上的结构性 pocket。**

## 5. 成本怎么读

诚实讲，当前 blocker 还是成本。

对 `15m sweep_reclaim`：
- gross 平均约 `+5.76 bps/笔`
- 若按 round-trip `4 bps` 粗扣，约还剩 `+1.76 bps/笔`
- 若按 round-trip `8 bps` 粗扣，就会转负

所以当前最准确的判断是：

> **这条 alpha 已经有 gross edge，但更像 maker-first / passive-entry / selective-universe 候选，还不能直接当 taker-first 全市场策略宣称过线。**

## 6. 为什么和当前项目有关

这轮值得写，不是因为我们又回到“breakout / retest 老路”，而是因为它补的是另一种 raw alpha 原语：
- 不是顺势 breakout
- 不是纯 mean reversion
- 而是**sweep 后的 reclaim continuation**

它对当前素材池的价值在于：
1. 给了一个**明确可编程**的结构型 raw alpha；
2. 自带完整策略壳（entry / exit / ATR stop / target）；
3. 可以直接和已有的 order-flow / OFI / CVD 材料拼接，做更严格的 admission；
4. 能自然落到 `15m`，不需要硬伪装成超高频。

## 6.5 策略拆解（必填）
- 方向属性：结构型 / 单资产 / sweep 后顺原方向回归
- 基础 alpha：liquidity sweep 后的 reclaim continuation
- regime：当前主要靠内部结构状态（bullish / bearish）承担，外部 regime 还没单列
- filter / veto：必须有 `discount/premium` 位置约束，且命中 `order block` 或 `FVG`
- risk / sizing / execution overlay：`ATR stop`、`swing/2R take profit`、后续应补 maker-first / spread veto / asset routing

## 7. 下一步怎么测

1. **只做 `15m`，不要再硬压 `5m`**
   - 先把这条线当 `15m first lane`
   - `5m` 暂时只作为 child execution，不当主信号

2. **做 asset routing**
   - 第一版先重点盯 `XRP / ETH / SOL`
   - `BTC` 更像 control group，不一定是最值钱标的

3. **加一个 execution veto**
   - 若 sweep 当根的成交价差 / ATR 比太差，直接不做
   - 看能不能把 `4bp` 档保住、把 `8bp` 档抬回来

4. **加一层 order-flow 确认，而不是再堆更多形态词**
   - 例如 sweep 后的下一根要求 taker imbalance 反向收敛
   - 或 CVD 不能继续恶化

5. **做 fixed time-stop 对照**
   - 当前平均持有 `7.75 bars`
   - 下一步直接测 `4 / 6 / 8 bars` time-stop
   - 看是否能把尾部拖单砍掉

## 8. 一句话带走

这份 2026 repo 真正值得留在研究池里的，不是“SMC 概念很多”，而是：

> **当你把它收窄成“liquidity sweep × discount/premium reclaim × OB/FVG 锚点”后，它在 Binance perp `15m` 上开始表现出像样的 raw alpha；但当前仍是 gross-first、maker-first 候选，不是 taker 直上。**

## 9. 关键来源
- Repo：<https://github.com/mefai-dev/mefai-autotrade>
- README：<https://raw.githubusercontent.com/mefai-dev/mefai-autotrade/master/README.md>
- Config：<https://raw.githubusercontent.com/mefai-dev/mefai-autotrade/master/config.yaml>
- Smart Money strategy：<https://raw.githubusercontent.com/mefai-dev/mefai-autotrade/master/src/strategies/smart_money.py>
