# HFT pairs shell：1h 选对 + 1m spread fade + OBI veto，base alpha 仍是配对均值回归

- 时间：2026-04-18 18:05 UTC
- 类型：GitHub repo source audit + Binance public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先用较慢频的 cointegration / half-life 筛出可回归配对，再在 `1m` 上做 `spread z-score` 极值回归；盘口 `OBI` 只负责放行/否决更微观的入场时点
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / cointegration / zscore / OBI / Binance Futures / HFT shell / 1m / 5m / 15m / execution / cost
- 证据类型：GitHub 工程实现 + repo 自带参数文件 + Binance public-data quick probe

## 1. 这次看了什么

看的是 `SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model`。它不是泛泛的“配对交易 notebook”，而是一个**研究到执行分层很清楚**的壳：

1. `data_loader.py`：抓 Binance USDⓈ-M `1m` 数据，按 `quoteVolume` 先筛 top-50 流动性合约；
2. `analyzer.py`：先在 `1h` 级别做相关性、Engle-Granger、ADF、half-life 筛 pair；
3. `optimizer.py`：在 spread 上扫 `window / entry_z / exit_z / stop_z`；
4. `main.cpp`：把结果推到一个低延迟执行器里，用 `bookTicker` / depth 信息加 `OBI` 做更细的放行。

这套结构对我们最有价值的，不是“C++ 很快”本身，而是：**它把 pair admission、spread alpha、本地微观结构 gate、执行线程壳分开了。**

## 2. 核心结论

- **base alpha 很清楚**：`cointegrated pair spread extreme -> mean reversion`。不是 trend，不是 breakout，也不是纯 execution trick。
- 这个 repo 真正适合 short-cycle desk 借的，不是“东京机房 4–7ms”这层包装，而是：
  - `1h` 做 pair admission，减少乱配对；
  - `1m` 做 z-score 入场；
  - `OBI` 只作为更快一级的 veto / timing layer。
- 代码里执行逻辑非常直白：`Z_ENTRY=2.0`、`Z_EXIT=0.5`、`BET_SIZE=1000`，并且要求两腿盘口失衡不要和 spread 方向打架：
  - `z > 2` 时做 `leg1 short / leg2 long`；
  - `z < -2` 时做 `leg1 long / leg2 short`；
  - 只有 spread 回到 `|z| < 0.5` 才平。
- 我用 Binance 公共 `1m` 最近 `1500` 根 bar 做了一个最小 portability probe：
  - `ENAUSDT/LINKUSDT`：`|z|>2` 触发后，平均 `|z|` 从 `2.23 -> 1.14 (30m) -> 0.99 (60m)`，`94.6%` 的事件在 `60m` 内收敛，`58.9%` 在 `60m` 内回到 `|z|<1`；
  - `LINKUSDT/SOLUSDT`：平均 `|z|` 从 `2.29 -> 1.03 (30m) -> 1.19 (60m)`，`96.5%` 事件在 `60m` 内收敛，但只有 `45.6%` 回到 `|z|<1`。
- 这说明：**repo 的主线不是假 alpha**；但它更像“spread 先明显回收、再看能不能完全归中”的壳，而不是保证短时间 fully close 的无脑收敛机。

## 3. 一句话结论

这份 repo 最值得保留的不是“低延迟 C++ 外壳”，而是 **`1h pair admission -> 1m spread-zscore fade -> OBI veto execution` 这条可独立复现、可继续压缩到短周期的 raw alpha 结构。**

## 4. 它是怎么证明这件事的

它不是靠论文口头说服，而是靠**工程分层 + 参数文件 + 直接执行逻辑**来证明：
- `analyzer.py` 明确先做 cointegration / ADF / half-life 过滤；
- `optimizer.py` 明确只优化 spread 交易参数；
- `main.cpp` 明确把 `OBI` 放在 entry gating，而不是把 OBI 当成 alpha 本体。

换句话说，repo 自己已经在结构上回答了一个关键问题：**base alpha 是 pair spread 回归，不是盘口失衡。盘口只是 timing layer。**

## 5. 为什么和当前项目有关

当前 digest 池里虽然已经有很多 pairs / stat-arb 主题，但这份 repo 仍有一个没那么重复的价值：

- 它不是只给“研究卡片”，而是给了**research-to-execution** 的壳；
- 它不是把微观结构硬当主 alpha，而是老老实实把 OBI 降级为 admission / veto；
- 它很适合服务我们现在的 desk 目标：
  - raw alpha 素材池继续补 `pairs / stat-arb`
  - 同时顺手拆出一个可复用组件：**配对 alpha 的微观结构入场 gate**

这比继续做纯 regime/filter 主题更值钱，因为它直接服务于“怎么把 pairs 从 paper signal 往实盘壳推进”。

## 6. 策略拆解

- 方向属性：market-neutral / relative-value / stat-arb
- 基础 alpha：cointegrated spread 在极端偏离后向均值回归
- pair admission：`top liquid universe -> corr filter -> Engle-Granger -> ADF -> half-life`
- entry：`|z| > 2`
- exit：spread 回到 `|z| < 0.5`
- stop / safety：`MAX_SAFE_Z = 25`；优化器里另有 `stop_z`
- sizing：名义单腿 `BET_SIZE=1000`，第二腿按 `hedge_ratio` 配
- microstructure filter：`OBI` 只决定现在这一下要不要进，不改 base alpha
- execution shell：生产者-消费者队列、持久 HTTP session、精度规则、reduceOnly close

## 7. 这份 repo 最值得借的 3 个点

### 7.1 先在慢一点的频率做 pair admission

`analyzer.py` 不是直接拿 `1m` 噪音去跑全市场配对，而是先 resample 到 `1h`，再做：
- correlation > `0.85`
- ADF `p < 0.05`
- half-life < `240` 分钟

这很符合 desk 现实：**pair selection 可以慢，entry timing 才需要快。**

### 7.2 OBI 是 timing veto，不是 alpha 本体

`main.cpp` 里 spread 还是用：
`log(p1) - hedge_ratio * log(p2)`

真正进场条件则是：
- spread 已经足够极端；
- 两腿盘口失衡方向别明显反着来。

这很重要，因为很多 repo 会把“看见 OBI”误写成“alpha 来自 OBI”；这份 repo 至少在结构上没犯这个错。

### 7.3 研究层和执行层真的分开了

这对后续复现很关键：
- 研究时你可以只跑 `pair admission + spread signal`；
- 执行时再决定是否加 `bookTicker/OBI/microprice`。

也就是说，它天然支持分阶段验证，而不是一上来就把 low-latency、网络、线程、盘口特征全部绑死。

## 8. 但它现在还不能直接照抄上线

这里有两个明显问题，反而也是这篇 digest 最值得记下来的地方：

### 8.1 优化器和执行器的 spread 口径不一致

- `optimizer.py` 用的是：`spread = leg1 - hedge_ratio * leg2`
- `main.cpp` 用的是：`spread = log(p1) - hedge_ratio * log(p2)`

这不是小问题。它意味着：**离线最优参数和线上触发空间可能根本不是同一个 spread。**

### 8.2 `main.cpp` 读取 `mean/std_dev`，但 `strategies.json` 默认并不带这两个字段

repo 里专门又写了个 `fix_strategies.py` 去补 `mean/std_dev`。这说明当前仓库更像“工程壳 + 研究草稿”，还不是可以闭眼上线的 production artifact。

所以这篇东西更适合作为：
- raw alpha 壳：保留
- 生产实现：继续审计
- 直接上线：暂缓

## 9. 可复刻的最小实验

### 9.1 当前最小实验

先不碰低延迟和盘口，只做最小 spread 回归验证：

1. Universe：Binance USDⓈ-M top `20~50` 流动性合约；
2. Pair admission：按 repo 的 `corr + EG/ADF + half-life`；
3. Signal：
   - `spread = log(p1) - beta * log(p2)`
   - `z = (spread - rolling_mean) / rolling_std`
   - `entry: |z| > 2`
   - `exit: |z| < 0.5`
4. Frequency：
   - pair admission 用 `1h`
   - execution 先测 `1m`，再下放 `5m/3m`
5. 先不加盘口，先看 gross 收敛、持有时长、事件密度。

### 9.2 当前 quick probe 结果

- 数据源：Binance USDⓈ-M 公共 `1m` klines
- 样本：最近 `1500` 根 `1m` bar
- 代表 pair：
  - `ENAUSDT/LINKUSDT`
  - `LINKUSDT/SOLUSDT`
- 结果：说明 spread 极值之后的“回收 tendency”是存在的，但完全回中比例不算夸张，下一步必须加入成本与持有时长约束。

## 10. 与当前短周期 `1m/3m/5m/15m` 的关系

- **最自然落点：`1m` entry / exit**。这是 repo 的原始设计频率。
- **更稳一点的 desk 迁移版：`5m` 做 spread 观测，`1m` 只做 child execution**。
- **`15m` 不该直接照抄**：pairs reversion 放到 `15m` 容易变成更慢、更少、更受 regime 影响的版本，和这份 repo 的 HFT 壳不完全同类。

所以它对我们最有价值的映射不是“把整套系统搬到 15m”，而是：
**把 pair selection 慢一点保留，把 spread alpha 放在 `1m/3m/5m` 里重验。**

## 11. 风险与保留意见

最大风险不是“回测太漂亮”，而是**数学与执行口径不一致**：
- offline 用 raw spread
- online 用 log spread
- OBI 还是 top-of-book 粗版本
- 成本与 funding 处理也远没到完整 production 级

另外，repo 给出的 pair 里不少是中小币对，流动性与冲击成本可能比纯 majors 更差。也就是说，这套壳更像：
- 能证明结构
- 能指导复现
- 但还没证明“扣完真实 frictions 之后能稳活”

## 12. 下一步怎么测

1. **先统一 spread 定义**：raw spread / log spread 二选一，不要离线线上两套口径；
2. **做 friction ladder**：0 / `4bps` / `8bps` / `12bps` / maker-taker split；
3. **把 pair admission 跟 entry 分层回测**：
   - A 版：只有 spread z-score
   - B 版：spread + OBI veto
   - C 版：spread + OBI + cooldown / max-hold
4. **先做 majors-relative pocket**：例如 `LINK/SOL`、`ETH/BTC proxy` 这种更接近可交易 pair；
5. **记录持有时长分布**：如果大多数 edge 要 `>60m` 才回收，那就和 repo 宣称的 HFT 壳不匹配；
6. **如果 `1m` 过于吃成本**，就把它降级成：`5m signal, 1m execution filter`，而不是硬做秒级策略。

## 13. 来源

- Author: Samarth Chaudhary
- Year: 2026
- Title: `Crypto_Stat-Arb_HFT_Model`
- Venue: GitHub
- DOI: N/A
- Repo URL: https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model
- Readable URLs:
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/README.md
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/analyzer.py
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/optimizer.py
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/main.cpp
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/fix_strategies.py
  - https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/strategies.json
- 本地 artifacts：
  - `reports/artifacts/quant_digests/2026-04-18_pairs_hft_shell_summary.json`
  - `reports/artifacts/quant_digests/2026-04-18_pairs_hft_shell_events.csv`
