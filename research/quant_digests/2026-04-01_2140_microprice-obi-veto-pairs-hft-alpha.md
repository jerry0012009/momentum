# 别把这份 2026 新 repo 只读成“C++ 低延迟秀肌肉”：对 short-cycle desk，更该先测的是「1h cointegration shortlist × microprice spread z-score fade × OBI veto」这条完整 pairs raw alpha
- 时间：2026-04-01 21:40 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `analyzer.py` + `optimizer.py` + `book_recorder.py` + `main.cpp` + `strategies.json`）
- 主题类型：raw alpha
- 基础 alpha：cointegrated pair spread mean reversion；先用 `1h` 协整筛 pair，再在更快执行层对 `log(microprice_1) - beta * log(microprice_2)` 的 z-score 偏离做均值回复
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/microprice/order-book-imbalance/obi/execution-veto/binance-perpetual/1h/15m/5m/3m/1m/repo/public-data/cost/latency
- 证据类型：repo-based source audit + 方法锚点

## 1. 这次看了什么
这次看的是 **Samarth Chaudhary (GitHub, 2026)** 的仓库 **Crypto_Stat-Arb_HFT_Model**。表面看，它像一份“研究层 Python + 执行层 C++”的 HFT 项目；但对我们 desk 真正有价值的，不是 `4-7ms RTT` 这种工程秀肌肉，而是它把一条 **可以独立落地的 pairs raw alpha 壳** 写得比较完整：

- `data_loader.py` 先抓 Binance Futures **top 50 quote-volume** USDT perp 的 **1m 数据、回看 365 天**；
- `analyzer.py` 把 1m 数据 **resample 成 1h**，先过 **相关性 > 0.85**，再做 **Engle-Granger OLS + ADF**，并给出 `hedge_ratio / p-value / half-life`；
- `optimizer.py` 再对 spread 做 **rolling z-score** 参数扫描：`window = 30/60/120/240/360`，`entry = 1.5~3.0`，`exit = 0~0.5`，`stop = 4~8`；
- `book_recorder.py` / `main.cpp` 在执行层引入 **microprice + OBI**：不再只看 mid，而是用盘口量加权价与一档不平衡去决定是否放行入场；
- `main.cpp` 里写死了 **`Z_ENTRY = 2.0`、`Z_EXIT = 0.5`、单 pair notional = 1000 美元、单仓亏损止损 = -20 美元、全局 kill = -100 美元**。

一句话：**base alpha 不是 OBI，也不是低延迟；base alpha 仍然是 pair spread mean reversion。真正值得 intake 的，是它把 “慢频选 pair + 快频执行 veto” 接成了一条完整策略链。**

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：就是 **cointegrated spread 的均值回复**，因此它是 raw alpha，不是纯 filter。
- 对当前 desk 最值得偷走的，不是 repo 的 C++ 外壳，而是 **“1h discovery / 1m execution” 的分层思路**：pair 发现和交易触发不必在同一频率上完成。
- `main.cpp` 里执行价不是普通 mid，而是 **microprice**：`(bid * askVol + ask * bidVol) / (bidVol + askVol)`；同时再加 **OBI veto**：
  - `z > 2` 只在 `obi1 < 0.2 && obi2 > -0.2` 时做 `short leg1 / long leg2`
  - `z < -2` 只在 `obi1 > -0.2 && obi2 < 0.2` 时做 `long leg1 / short leg2`
  这相当于要求盘口短时压力不要和 spread fade 完全打架。
- `optimizer.py` 说明 repo 想给一条完整策略壳：**entry / exit / stop / sizing / cost** 都有定义，而不是只给“这个 pair 看起来会回归”一句空话。
- 但 repo 有 3 个必须先修的硬伤：
  1. `analyzer.py` 在 **1h resample** 后仍把 `MAX_HALF_LIFE = 240` 注释成“最多 4 小时回归”，**单位明显错位**；按代码实际口径更像 240 小时。
  2. `optimizer.py` 的成本近似是 `abs(spread) * fee_pct`，**不是双腿名义金额成本**，会低估真实 friction。
  3. `strategies.json` 里一开始缺 `mean/std_dev`，后来又靠 `fix_strategies.py` 现场补，这说明 repo 的研究层和执行层 **口径并没完全锁死**。

一句话核心结论：**真正该复现的不是“低延迟 C++”，而是“慢频筛出可交易 pair，再让 microprice+OBI 只负责决定这次 spread 偏离要不要做”这条 pairs raw alpha。**

一句话说它怎么证明：**证据主要来自 repo 源码本身——数据下载、pair discovery、参数扫描、盘口记录、执行与风控模块是同一条链，说明作者不是只写了概念，而是把完整策略壳真的连起来了。**

## 3. 为什么和当前项目有关
最近两天 intake 里，pairs / relative-value 家族已经补了不少：
- pair admission（ADF + Johansen）
- half-life gate / wide-band entry
- threshold governance / plateau-first
- cluster residualization

这轮补的不是“再来一个 pairs headline”，而是一个当前素材池里更缺的组件：**spread alpha 怎么和盘口执行层接上。**

这和当前学习进展的关系也很直接：
- `momentum` 原主线还是趋势 / breakout / ATR / volume；
- bot7 这阶段则要持续给 desk 补 **可独立复现的 raw alpha 素材池**；
- 而 desk 真正迟早要面对的问题不是“有没有 alpha”，而是 **这条 alpha 在 `1m/3m/5m/15m` 上该怎么进场，才不会被盘口噪声直接吃掉**。

翻成人话：**pair spread 会不会回归，是第一层；这次偏离值不值得立刻出手，是第二层。repo 的价值就在把第二层写成了可执行规则。**

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative value / market-neutral
- 基础 alpha：协整 pair 的对数 spread 偏离均值后会回归；交易对象是 `log(p1) - beta * log(p2)` 的 spread，而不是单腿方向判断
- regime：优先用于高流动性 USDT perp；pair discovery 慢频更新，执行层只在 pair 关系仍稳定时启用
- filter / veto：相关性阈值、ADF 协整筛选、half-life 上限、`|z| > 2` 触发、OBI veto、`MAX_SAFE_Z = 25` 异常极值跳过
- risk / sizing / execution overlay：beta-consistent 双腿名义配比、`|z| <= 0.5` 止盈、单仓美元亏损止损、全局 kill-switch、microprice 作为更细盘口执行价代理

## 4. 可复刻的最小实验
- 研究假设：**同样做 cointegration spread fade，加入 microprice + OBI veto 后，能否在短周期上减少“刚进就被盘口继续挤压”的坏交易。**
- 数据：
  1. Binance / Bybit / OKX 公开 perpetual `1m` klines 做 pair discovery 输入；
  2. Binance `bookTicker` 或 top-of-book 快照做 `best bid / best ask / bid size / ask size`；
  3. 先不要求真 tick-by-tick 撮合，第一轮只做 `1s~5s` 盘口 proxy。
- universe：`15~30` 个最液态 USDT perp；先分 bucket（majors / L1 / meme），不要第一刀全市场乱配。
- pair discovery：
  1. 用 `30~60` 天 `1h` 数据重算 pair；
  2. 相关性 `> 0.8`；
  3. ADF `p < 0.05`；
  4. half-life 先明确统一到 **bar 数**，别再混“小时/分钟”单位。
- 交易层：
  1. 在 `15m` 先做 baseline：spread rolling `z` 的 `entry 2.0/2.5`、`exit 0.5`、`stop 3.5/4.0`；
  2. 然后把入场那一刻下钻到 `1m` 或盘口流：
     - baseline A：只看 mid/mid-return
     - baseline B：看 microprice
     - variant C：microprice + OBI veto
- sizing / risk：pair 内美元中性，再做 beta 调整；单 pair gross cap；最大持有 `8/16/24` 根 `15m`；把 funding 加回 pair PnL。
- 成本：必须做 **pair round-trip 12 / 20 / 32 bps friction ladder**，并把 legging risk 单独记一栏。
- 验证重点：
  1. 入场后 `1~3` 根 adverse excursion 是否下降；
  2. 胜率变化是不是主要来自“少做错单”，不是“多做神单”；
  3. turnover、持有时长、止损触发率是否改善；
  4. `15m signal + 1m veto` 是否优于纯 `1m signal` 直接交易。

## 5. 先测什么，不先测什么
先测 **“microprice / OBI 是否能当 execution veto，而不是 alpha 本体”**。

别一上来就测：
- 真毫秒级撮合；
- C++ 低延迟栈；
- 超大 universe 扫描；
- 复杂 order book 深度特征。

第一刀更合理的是：**保留一个最朴素的 spread z-score baseline，再只替换入场口那一层的执行判定。**

如果这一刀都不能改善 post-entry path，就没必要急着把它升级成“高频系统”。

## 6. 风险与误区
- **单位错位风险**：repo 的 half-life 注释与代码不一致，直接复刻很容易把 pair 筛选口径弄脏。
- **成本低估风险**：spread 成本不能用 `abs(spread)` 近似，必须回到双腿名义、手续费、滑点、funding 与 legging risk。
- **盘口代理风险**：microprice / OBI 对 top-of-book 很敏感；在 alt 上，挂单撤单噪声会显著放大假信号。
- **频率错配风险**：`1h` 上协整成立，不代表 `1m` 上一定值得做；中间必须经过 `15m/5m` 的桥接测试。
- **工程幻觉风险**：低延迟不是 alpha。若 pair 本身不干净、成本没算对，再快也只是更快亏钱。

## 7. 来源与复现线索
### 主来源（repo）
- Samarth Chaudhary (GitHub, 2026), *Crypto_Stat-Arb_HFT_Model*, GitHub repository, Venue: GitHub, DOI: N/A, Readable URL: <https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>, Repo URL: <https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model>
- README（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/README.md>
- Pair discovery（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/analyzer.py>
- Optimizer（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/optimizer.py>
- Book recorder（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/book_recorder.py>
- Execution engine（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/main.cpp>
- Strategy params（raw）：<https://raw.githubusercontent.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/main/strategies.json>

### 方法锚点（概念地基）
- Engle, Robert F.; Granger, Clive W. J. (1987), *Co-integration and Error Correction: Representation, Estimation, and Testing*, *Econometrica*, DOI: <https://doi.org/10.2307/1913236>, Readable URL: <https://www.jstor.org/stable/1913236>
- Cartea, Álvaro; Jaimungal, Sebastian; Penalva, José (2015), *Algorithmic and High-Frequency Trading*, Cambridge University Press, DOI: N/A, Readable URL: <https://doi.org/10.1017/CBO9781316086454>

## 8. 一句话带走
如果把这份材料变成 desk 可测策略，我会把它定义成：**“1h 慢频筛 pair，15m 做 spread 触发，1m / bookTicker 用 microprice + OBI 决定这笔 fade 要不要放行”的完整 pairs raw alpha 壳**，而不是一份单纯炫低延迟的 C++ 项目。
