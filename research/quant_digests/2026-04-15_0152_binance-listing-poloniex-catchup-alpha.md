# 别把这份 2025 新 listing bot 只读成“公告抢跑脚本”：对 short-cycle desk，更该先测的是「Binance 上新公告 × 外部 venue 滞后补涨」这条 1m/3m event-driven raw alpha
- 时间：2026-04-15 01:52 UTC
- 类型：GitHub / repo source audit（README + Program.cs + worker/service 源码）
- 主题类型：raw alpha
- 基础 alpha：当 **Binance 官方发出“will list”公告** 时，若同币已在其他 venue 可交易，公告后最初几分钟该币在外部 venue 往往会先出现一段 **attention-driven catch-up jump**；可交易对象不是 Binance 新上市腿本身，而是 **先去买仍可交易的 lagging venue 现货/永续腿**，赌的是公开事件引发的跨 venue 价格重估
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / event-driven / cross-venue / listing-announcement / lead-lag / catch-up / single-asset / Poloniex / Binance / 1m / 3m / 5m / repo / public-data / latency / execution
- 证据类型：工程证据（repo README + source audit）

## 1. 这次看了什么
先回答 base alpha：**这不是“又一个自动化公告机器人”，而是一条能独立成立的 event-driven raw alpha——Binance 上新公告本身就是公开催化剂，若同币在别的 venue 已可交易，那条腿通常会先被动补涨。**

这轮主材料是 2025 GitHub repo `CyberPunkMetalHead/new-listings-trading-bot`。repo 表面上是在做“监听 Binance 公告、去 Poloniex 市价买入”，但对 desk 更有价值的 intake 不是 C# 工程壳，而是背后的 **公告→跨 venue 重估** 逻辑：
- 催化剂：Binance 官方 listing announcement
- 可交易腿：其他已挂牌 venue 的现货腿（repo 当前默认 `Poloniex`）
- 方向：long lagging leg
- 时间尺度：**秒级到分钟级**，天然更像 `1m / 3m` 高强度 alpha，而不是 `15m` 慢节奏 carry/pairs

repo 的公开结构也很清楚：
- `ListingsGetterService.cs`：直接轮询 Binance 公告 API
- `BuyListingWorker.cs`：检测到 `will list` 就抓 ticker 并下市价单
- `ExitStrategyWorker.cs`：用固定止损 + 动态 trailing take-profit 管理离场
- `Program.cs`：写死接入 `Poloniex`
- `appsettings.example.json`：给出默认 `BuyAmount=20`、`StopLoss=1%`、`TakeProfit=1%`

所以这轮最该记住的不是“这个 bot 能不能直接跑真钱”，而是：**公开公告本身就是事件源，listing 前的跨 venue 可交易腿就是 lagging leg。**

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 short-cycle desk intake 的，不是“抢公告”这件事本身，而是它把一条很清楚的 event alpha 说透了：**Binance 公告是公共信号，外部 venue 是可交易的滞后腿。**
- **一句话证明方式：** 我直接审了公告抓取、symbol 抽取、入场、出场和配置源码，确认这条线不是抽象想法，而是已经被写成了完整的最小执行骨架。
- 这条 alpha 和 4/13 那篇 `listing-phase overheat short` 不是一回事：那篇赌的是**上线几天后的过热回落**；这篇赌的是**公告后几分钟的先手补涨**。
- 对当前 desk，它最大的价值不是 broad-frequency，而是**补一条极短周期 event sleeve**：频率低，但 alpha 纯度高、base alpha 很清楚。
- repo 当前更像 **research skeleton / execution prototype**，不是现成 production：没有严格成本/滑点/延迟建模，`ExitStrategyWorker.cs` 里的卖出单还把 `IsBuy` 写成了 `true`，说明工程实现本身需要先修。

### 2.1 raw alpha 到底怎么写
repo 的核心链路非常直接：

1. `ListingsGetterService.cs` 轮询 Binance 公告接口：
   - `/bapi/apex/v1/public/apex/cms/article/list/query?type=1&pageNo=1&pageSize=10`
2. 只盯标题里含 `will list` 的公告
3. 用正则 `\(([A-Z]+)\)` 从公告标题里抽 ticker
4. 对每个 symbol 检查数据库里是否已经买过，避免重复开仓
5. 若未持仓，就去外部 venue（repo 默认 `Poloniex`）对 `${symbol}_USDT` 下 **市价买单**
6. 开仓后立刻记录：
   - `TakeProfitPrice = entry * (1 + TP%)`
   - `StopLossPrice = entry * (1 - SL%)`
7. 之后 `ExitStrategyWorker.cs` 每秒轮询一次当前价：
   - 跌破 stop 就平
   - 涨破 take-profit 就把 TP/SL 一起往上抬，变成 trailing lock-in

翻成人话就是：
> **事件确认后，立刻买 lagging venue；如果继续冲，就跟着抬 trailing stop；如果冲不动就很快认错。**

这是一条非常典型的 **public event → cross-venue repricing** raw alpha，不是 filter，也不是只给别的策略做 overlay。

### 2.2 为什么它值得被当成独立 raw alpha，而不是“公告脚本”
因为它把 alpha 本体讲得很清楚：
- **信息源**不是私有流，而是公开 Binance 公告；
- **边**不在 Binance 自己，而在“别的地方已经能买、但市场还没完全反应过来”的那条腿；
- **盈利机制**不是长期均值回复，而是公告后的短时 attention / accessibility shock；
- **退出机制**也不是长拿，而是分钟级 trailing / stop 管理。

所以它本质上更像：
- `event-driven`
- `cross-venue lead-lag`
- `single-asset catch-up momentum`

而不是传统的 pairs / basis / funding 玩法。

### 2.3 为什么我把“可直接落地完整策略”记成 `否`
不是因为它没有 entry/exit——它其实都有；而是因为它离 production 还差几块关键砖：

1. **没有严肃的延迟/滑点建模**
   - 这条线的边很大概率主要活在最初几秒/几分钟
   - 如果不知道 announcement detection latency、下单 RTT、外部 venue 流动性，就没法判断 edge 还剩多少

2. **实现里有明显工程硬伤**
   - `ExitStrategyWorker.cs` 的“卖出”分支里 `ExchangeOrderRequest.IsBuy = true`
   - 如果不是 exchange wrapper 的特殊语义，这几乎就是方向写反的硬 bug

3. **没有统一成本口径**
   - repo 纸面单 `Fees = 0`
   - 对这种秒级/分钟级事件单，手续费和冲击成本根本不是可忽略项

所以更合理的结论是：
> **alpha 本体清楚、执行壳雏形也有，但现在更像可复现 skeleton，不像已经能直接上线的完整策略。**

## 3. 为什么和当前项目有关
这轮对当前 desk 有直接价值，而且不是重复最近的 pairs / funding / XS 主题：

1. **它补的是 `1m / 3m` 事件驱动 raw alpha 素材池。**
   最近 intake 里很多是持续型 alpha（pairs、carry、cross-sectional）。这条线则是稀缺的“**触发式 alpha**”：平时不交易，一旦来事件就要求极快响应。

2. **它的 base alpha 非常清楚。**
   不是“可能有点情绪影响”，而是：**Binance 上新公告 → 其他 venue 同币补涨**。

3. **它天然适合拆成完整 desk 组件。**
   - event listener
   - symbol parser
   - venue availability filter
   - immediate entry
   - trailing/kill switch
   - post-trade review

4. **它能当别的事件策略模板。**
   即便最后不做 listing，这条 skeleton 也可以迁到：
   - ETF / 上线 / 上架 / 空投 / partnership 公告
   - prediction market resolution 前公开催化剂
   - 其他“信息先公开、可交易腿后反应”的事件

## 3.5 策略拆解（必填）
- 方向属性：event-driven / cross-venue / 单资产顺势 catch-up
- 基础 alpha：Binance listing 公告触发公开 attention shock，已在其他 venue 挂牌的同币会在公告后短时间出现补涨
- regime：只在 `announcement == will list` 且外部 venue 已有可交易市场时激活
- filter / veto：ticker 抽取成功；目标市场存在；未重复持仓；必要时应再加 `min quote depth / max spread / fresh listing age / announcement category whitelist`
- risk / sizing / execution overlay：固定买入金额、初始止损、动态 trailing take-profit；真正的核心 overlay 应该是 **latency budget + liquidity veto + notional cap**

## 4. 可复刻的最小实验
### 4.1 最小研究假设
**如果 Binance 首次发布某币“will list”公告，而该币在 Poloniex/Bybit/KuCoin 等 venue 已可交易，那么公告后 `1m / 3m / 5m / 15m` 的 forward return 会显著偏正；其中真正可交易的 edge 主要活在最初几分钟。**

### 4.2 数据源、公开性、更新频率
- **公告源：** Binance 公告 API（repo 已给出公开 endpoint）
  - 公开性：公开可拿
  - 更新频率：近实时，适合轮询/监听
- **价格源：** 目标 venue 的公开 ticker / kline / trades / BBO
  - 公开性：Poloniex、Bybit、KuCoin 等都能拿到公开行情
  - 更新频率：秒级或更高
- **最小可复现实验口径：**
  - 先不追求 tick 级成交回放
  - 先用 `1m` bar + announcement timestamp 做 event study
  - 再下钻到 `trades/BBO` 做 latency/cost stress test

### 4.3 最小实验设计
第一版先做最简单的 event study：
- 样本：近 `1~2` 年 Binance `will list` 公告
- 只保留：公告当时该 symbol 在参考 venue 已可交易的事件
- 事件时间 `t0`：公告 API 首次出现该标题的时间
- 入场：
  - `t0+1m`、`t0+3m` 两档
- 出场：
  - 固定持有 `5m / 15m / 60m`
  - 或 `1%` trailing / `1%` stop-loss
- 先看：
  - gross forward bps
  - hit rate
  - time-to-peak
  - 公告后首 `15m` 最大回撤

### 4.4 必做对照组
至少同时跑这四组：
1. **announcement long**：公告后立刻买 lagging venue
2. **delayed long**：公告后 `15m` 才买，估计 edge 衰减
3. **same-day placebo**：同 symbol 非公告时段同长度窗口
4. **listing-day-open long**：不按公告时点，而按 Binance 实际开市时点买，比较“公告 edge”与“正式上线 edge”谁更厚

### 4.5 先看哪些指标
这条线不要先看 Sharpe，先看：
- `net bps / event`
- `announcement-to-entry latency`
- `spread + slippage as % of gross move`
- `win rate in first 5m / 15m`
- `time-to-peak`
- `availability ratio`（有多少公告对应外部 venue 真有可交易腿）

### 4.6 下一步怎么测
- **第一步：** 先抓历史 Binance listing 公告时间线，建立事件表，不急着做实时监听。
- **第二步：** 对每个事件先做 `1m` event study，确认 edge 是否集中在 `0~5m` 还是还能活到 `15~60m`。
- **第三步：** 如果 `1m` study 显示 gross edge 足够厚，再加 `spread / fee / slippage / latency` 四件套做 friction ladder。
- **第四步：** 若 edge 只活在极短时间，就把它定位成 **special-situations sleeve**，不要硬塞进常规 `15m` 连续交易主线。

## 5. 风险与保留意见
- **事件频率低。** 它不是日常稳定产出的 broad sleeve，更像低频高强度 special situation。
- **latency 是头号敌人。** 这条线若没有快检测、快下单、快风控，纸面 gross edge 可能很快被吃光。
- **外部 venue 可交易性不稳定。** 不一定每次都有“已挂牌但未完全重估”的好腿。
- **symbol 抽取会有脏数据风险。** repo 直接用 `\(([A-Z]+)\)` 抽 ticker，遇到多个 ticker 或公告格式变化时需要额外清洗。
- **现成 repo 不能直接信成 production。** 除了 `Fees=0`，卖出分支的 `IsBuy=true` 也说明这更像概念验证，不是上线版。

## 6. 来源
- CyberPunkMetalHead. (2025). *new-listings-trading-bot*. GitHub repository.  
  Repo URL: `https://github.com/CyberPunkMetalHead/new-listings-trading-bot`
- CyberPunkMetalHead. (2025). *readme.md*. GitHub repository documentation.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/readme.md`
- CyberPunkMetalHead. (2025). *Program.cs*. GitHub source file.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/Program.cs`
- CyberPunkMetalHead. (2025). *Workers/BuyListingWorker.cs*. GitHub source file.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/Workers/BuyListingWorker.cs`
- CyberPunkMetalHead. (2025). *Workers/ExitStrategyWorker.cs*. GitHub source file.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/Workers/ExitStrategyWorker.cs`
- CyberPunkMetalHead. (2025). *Services/ListingsGetterService.cs*. GitHub source file.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/Services/ListingsGetterService.cs`
- CyberPunkMetalHead. (2025). *Services/ExchangeService.cs*. GitHub source file.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/Services/ExchangeService.cs`
- CyberPunkMetalHead. (2025). *appsettings.example.json*. GitHub config example.  
  Readable URL: `https://raw.githubusercontent.com/CyberPunkMetalHead/new-listings-trading-bot/main/appsettings.example.json`

## 7. 本地产物
- Digest：`research/quant_digests/2026-04-15_0152_binance-listing-poloniex-catchup-alpha.md`
