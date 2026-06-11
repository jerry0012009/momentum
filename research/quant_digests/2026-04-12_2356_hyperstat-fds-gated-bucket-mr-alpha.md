# 别把这份 2026 Hyperliquid stat-arb repo 直接当完整交易系统：对 short-cycle desk，更该先测的是「bucket dispersion MR × funding-divergence admission」这条 raw alpha

- 时间：2026-04-12 23:56 UTC
- 类型：quant_digest
- 主题标签：raw-alpha/stat-arb/cross-sectional/relative-value/mean-reversion/bucket-dispersion/funding/funding-divergence/gate/hyperliquid/5m/1h/repo/public-data/cost/risk
- 证据类型：2026 GitHub repo source audit（`README.md` + `configs/default.yaml` + `configs/strategy_stat_arb.yaml` + `src/hyperstat/strategy/stat_arb.py` + `src/hyperstat/strategy/funding_divergence_signal.py` + `src/hyperstat/strategy/regime.py` + `src/hyperstat/strategy/allocator.py` + `src/hyperstat/backtest/engine.py` + `src/hyperstat/backtest/costs.py`）+ repo bundled public-data probe（`data/candles/*/5m.parquet` + `data/funding/*/8h.parquet`）

- 主题类型：raw alpha
- 基础 alpha：同 bucket alt 在过去 `1h` 出现显著相对偏离后，做 `short rich / long cheap`，赌的是 **bucket 内 dispersion 压缩与相对收益回归**；funding divergence 只负责 admission / confidence gate，不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否

## 1. 这次看了什么
### 主材料（repo）
- **Jbdelrio (2026)**
- **Title**：*hyperstat-arb-bot*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL / Repo URL**：<https://github.com/Jbdelrio/hyperstat-arb-bot>
- **Repo metadata**：`created_at=2026-02-20`，`pushed_at=2026-02-25`

这轮最值得 intake 的，不是把 repo 整体照抄成“又一个完整 stat-arb 系统”，而是先把它拆开成两层：

1. **alpha 本体**：`5m` 频率下、看过去 `12 bars = 1h` 的 bucket 内 cross-sectional mean reversion；
2. **过滤层**：funding-divergence signal（FDS）只在资金费率和价格错位时给 alpha 放行或加权。

也就是说，这轮真正值得 desk 先测的不是：
> “repo 里整套配置能不能直接搬上线？”

而是：
> **“bucket dispersion MR 这条 raw alpha 单独站不站得住？以及 funding divergence 能不能把一堆垃圾反转信号筛掉？”**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
很清楚：

> **base alpha = bucket 内过去 1 小时相对强弱偏离过大后的 cross-sectional mean reversion。**

翻成人话：
- 若同一 bucket 里某个 alt 明显跑赢同组其他币，它不是自动等于“更强趋势”；
- 在短周期上，它常常只是短时拥挤、错位或局部情绪失衡；
- 所以更合理的交易动作是 `short rich / long cheap`，赌偏离回归，而不是追强追弱。

funding 在这里不是主信号，只是：
- 判断这次偏离是不是“拥挤得更像会回”；
- 或者说，**funding divergence 是 confidence gate，不是 alpha 本体。**

所以本轮主题归类应是：
- `raw alpha`
- 服务于 `stat-arb / relative-value / cross-sectional mean reversion`
- 不是纯 filter / regime / overlay 摘要

## 3. repo 到底怎么写这条 alpha
### 3.1 `stat_arb.py`：核心信号其实很朴素
repo 的 `StatArbStrategy` 并不神秘，本体就是：
- `timeframe = 5m`
- `horizon_bars = 12` → 看过去 `1h` 收益
- 在 bucket 内对每个币的 `1h` log return 做 **median + MAD** 标准化
- 当 `|z| >= 1.5` 开始激活，`|z| <= 0.5` 才允许退出
- `min_hold_minutes = 30`
- `max_hold_minutes = 1440`

也就是：
> **过去 1h 明显相对偏离的币，按 contrarian 方向做 fade。**

这是标准的 raw alpha 骨架，而且是可直接复现的，不靠私有数据，不靠模型黑箱。

### 3.2 `allocator.py` / `regime.py`：真正复杂的是“怎么别把它做烂”
repo 真正费力写的不是 alpha 本体，而是：
- 波动缩放
- beta / dollar neutral
- gross target
- 风险关停
- funding overlay / FDS gate

这恰恰说明一个现实：

> **这条 alpha 的难点不在“有没有想法”，而在“怎样把换手和拥挤过滤掉”。**

### 3.3 `funding_divergence_signal.py`：repo 里最值钱的旁支
FDS 不是简单看 funding 高低，而是揉了三件事：
- funding 的 cross-sectional carry 水平
- funding 变化和价格方向是否错位
- funding velocity 是否加速到过热区

repo 把它设计成：
- 不反转原有 MR 方向；
- 只做 `confidence gate`，决定这次是否值得放大或放行。

这很符合 desk 用法，因为它回答的是：
> **哪些 MR 偏离更像 crowding 失衡，哪些只是趋势里你去逆着接飞刀。**

## 4. 最小 public-data probe：先看“原始 alpha”，再看“FDS 是否有用”
这次我没有停在源码阅读，而是直接用 repo 自带公开数据做最小实验：

### 4.1 数据口径
- **数据源**：repo bundled parquet（可公开获取 / 可直接复现实验）
  - `data/candles/{symbol}/5m.parquet`
  - `data/funding/{symbol}/8h.parquet`
- **标的**：`ETH / SOL / AVAX / ARB / OP`（bucket 侧）+ `BTC`（base factor）
- **价格样本区间**：`2026-02-03 12:50 UTC` → `2026-02-20 22:05 UTC`
- **funding 可对齐区间**：`2026-02-16 11:00 UTC` → `2026-02-20 22:05 UTC`
- **最小实验频率**：`5m`
- **alpha horizon**：过去 `12 bars = 1h` 偏离；向前看 `12 bars = 1h` 的相对回归

为什么这口径是合格的：
- 数据公开可得；
- 频率直接是 `5m`，不用硬降采样；
- 可以很快映射到后续 `1m/3m/15m` 变体测试。

## 5. 结果一：repo 默认整套 stat-arb 在自带数据上，先被成本吃掉
我先按 repo 默认参数跑了一轮最小回测（`BTC + ETH/SOL/AVAX/ARB/OP`，bucket MR + neutralization + funding overlay/FDS + repo 默认成本）：

### 5.1 默认成本配置
- taker fee：`6 bps`
- maker fee：`2 bps`
- base slippage：`8 bps`
- RV1h slippage 放大：`10 bps / 1pct RV1h`

### 5.2 回测摘要
- 样本 bars：`5,013`
- `total_return = -45.70%`
- `pnl_gross = +0.92`
- `fees = 172.84`
- `slippage = 513.57`
- `pnl_net = -685.49`
- 初始权益：`1500`

这组数的核心意思很简单：

> **raw idea 不是完全没回归味道，但默认做法的 gross 基本打平，净值则被换手成本狠狠干穿。**

所以这题不能老实巴交写成“可直接落地完整策略”，那样是在骗自己。

## 6. 结果二：bucket dispersion 本身会压缩，但“怎么分配腿”才是胜负手
我把 alpha 本体拆出来，不走整套 backtest engine，而是直接看 bucket 内结构是否在未来 `1h` 有压缩：

### 6.1 bucket spread 压缩证据
定义：
- 当前 `1h` 回报横截面的 `80% quantile - 20% quantile` 作为 bucket spread；
- 看未来 `1h` 这个 spread 是扩还是缩。

结果：
- 当 spread 处在样本 **前 20% 扩张区** 时：
  - 未来 `1h` 平均变动：**`-36.17 bps`**
  - spread 收缩命中率：**`82.3%`**
  - 事件数：`999`
- 当前 spread 与未来 `1h` spread 变化的相关：**`-0.58`**

翻成人话：

> **bucket dispersion 会压缩，这件事是真的。**

但问题也正出在这里：
- spread 会压缩，不代表你随便按每个单币的 z-score 去分配仓位就能挣钱；
- alpha 的结构对了，执行和腿分配也可能把它做废。

## 7. 结果三：vanilla 单做 MR 事件不行，但 FDS 过滤后的 pocket 变得像样
接着我只看真正会触发交易的事件：
- `|z| >= 1.5`
- 用 contrarian 方向看未来 `1h` 的相对收益

### 7.1 不加 FDS，原始 MR 事件是负的
在 funding 可对齐的样本里：
- active MR basket events：`957`
- 平均未来 `1h` gross：**`-3.68 bps`**
- hit rate：**`45.0%`**

也就是说：
> **vanilla bucket MR 在这个 pocket 里并不够好。**

### 7.2 一旦用 FDS 做 admission，质量明显改善
我把 repo 的 FDS 思路做成最小 batch gate，对 active MR 事件按 gate score 做筛选：

#### 当加权 FDS 分数 `> 0`
- 事件数：`189`
- 平均未来 `1h` gross：**`+15.65 bps`**
- 中位数：**`+13.44 bps`**
- hit rate：**`56.6%`**

#### 当加权 FDS 分数 `> 0.25`
- 事件数：`50`
- 平均未来 `1h` gross：**`+24.12 bps`**
- 中位数：**`+19.82 bps`**
- hit rate：**`60.0%`**

从单腿事件角度再看也类似：
- 所有 active legs：平均 edge **`-5.57 bps`**，hit **`40.4%`**
- `gate > 0` 的 active legs：平均 edge **`+33.91 bps`**，hit **`52.4%`**
- `gate > 0.25` 的 active legs：平均 edge **`+37.57 bps`**，hit **`53.6%`**

这组数最关键：

> **不是“funding 自己就是 alpha”，而是“funding divergence 能把原本质量很差的 MR pocket 筛成勉强像样的 pocket”。**

## 8. 这题该怎么落在我们研究池里
### 8.1 正确标签
我会把这题标成：

- **主题类型**：`raw alpha`
- **基础 alpha**：`bucket dispersion mean reversion`
- **辅助层**：`funding-divergence admission filter`

不是：
- “funding alpha”
- 也不是“纯 overlay”

### 8.2 它对 desk 真正的价值
这题最值钱的不是“repo 已经写好了回测引擎”，而是它给了一个更适合 desk 的拆法：

1. **先承认 bucket MR 本体很脆**；
2. **再用 crowding / funding 错位去筛 pocket**；
3. **最后只做最值得做的几次，不要整本书一直滚。**

这比直接抄 full-book stat-arb，更接近真钱研究。

## 9. 与 `1m / 3m / 5m / 15m` 的关系
### `5m`
这是本题当前最自然的第一落点：
- repo 原始口径就是 `5m`
- `1h = 12 bars` 很直观
- bundled 数据可以立即复现

### `3m / 1m`
可以做，但不是马上压过去：
- 先把 `1h` 时钟长度保持不变，映射成 `20 bars / 60 bars`
- 重点看 gate 后事件是否仍能留下足够 edge 覆盖更高换手

### `15m`
更像控制组或低频版：
- 若映射成 `4 bars ≈ 1h` 会太粗
- 更合理的是保持时间长度、把 lookback / hold 重新标时钟而非死守 bars

## 10. 下一步怎么测
这里必须很具体，不然这篇 digest 只有阅读价值，没有研发价值。

### 10.1 第一优先：别再做 whole-book，改做 sparse book
直接测这三版：
1. **top1 rich / top1 cheap only**
2. **top2 / bottom2 only**
3. **只保留 `FDS > 0.1 / 0.25` 的 event**

目标：
- 看 gross 是否稳定高于 `15~25 bps / 1h event`
- 看事件频率是否足够支持一周内有样本积累

### 10.2 第二优先：把持有逻辑从“迟钝 hysteresis”改成“clock exit + compression exit”
当前 repo 是：
- `z_in = 1.5`
- `z_out = 0.5`
- `min_hold = 30m`

下一步该测：
- 固定 `30m / 60m` clock exit
- 或 `spread shrink x%` 就先走
- 避免因为“等 z_out”把已到手的 dispersion compression 吐回去

### 10.3 第三优先：把成本分成 maker / taker 两张账
当前 repo 默认成本对 short-cycle 太狠，下一步必须拆开：
- taker-only
- maker-entry / taker-exit
- maker-first with timeout

因为这题现在最像的是：
> **gross edge 只在精选 pocket 上存在，能不能活下来主要看是否能把执行从“持续滚动 taker”改成“低频 + 更偏 maker”。**

### 10.4 第四优先：跨 venue 可移植性
若后续想从 repo bundled 数据走向更通用研究，先复现到：
- Binance USDⓈ-M `5m klines`
- Binance / Hyperliquid funding 公共接口
- 先用 majors + liquid alts 小篮子

## 11. 一句话结论
这题最后我会给一个很明确的结论：

> **`hyperstat-arb-bot` 里真正该 intake 的，不是“默认 full-book stat-arb”，而是“bucket dispersion MR 这条 raw alpha + funding-divergence admission 这层过滤”。**

更直接一点：
- **base alpha 是真的，但 standalone 版本不够好；**
- **FDS 不是 alpha 本体，却显著提高了 pocket 质量；**
- **所以这轮更适合进研究池的形态，是“MR alpha skeleton + funding gate”，而不是把整套 repo 宣布为 ready-to-trade。**

## 12. 文件与来源
- 本文路径：`research/quant_digests/2026-04-12_2356_hyperstat-fds-gated-bucket-mr-alpha.md`
- 主要来源：<https://github.com/Jbdelrio/hyperstat-arb-bot>
- 关键源码：
  - `src/hyperstat/strategy/stat_arb.py`
  - `src/hyperstat/strategy/funding_divergence_signal.py`
  - `src/hyperstat/strategy/regime.py`
  - `src/hyperstat/strategy/allocator.py`
  - `src/hyperstat/backtest/engine.py`
  - `src/hyperstat/backtest/costs.py`
- 关键配置：
  - `configs/default.yaml`
  - `configs/strategy_stat_arb.yaml`
