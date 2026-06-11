# 别把这份 2026 HFT repo 只读成 C++ 低延迟引擎：对 short-cycle desk，更该先测的是「cointegrated perp spread fade × microprice/OBI confirm」这条 raw alpha
- 时间：2026-04-11 22:38 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `analyzer.py` + `optimizer.py` + `fix_strategies.py` + `strategies.json` + `main.cpp`）+ Binance USDⓈ-M 公共 `1m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**同一交易所内、相关性高且协整的 perp 对，其 log spread 偏离 rolling 均值到极端 z-score 后，短周期内更容易向均值回归；microprice 与顶级盘口 OBI 不是 alpha 本体，而是用来确认“这次回归不是坏报价/单腿继续挤压”的执行确认层。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/microprice/order-book-imbalance/obi/binance-perpetual/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：源码审计 + 公共 1m portability probe

## 1. 这次看了什么
这次看的是 `SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model`。表面上它最显眼的是：
- C++20 执行层
- `!bookTicker` 实时流
- AWS Tokyo colocated 的低延迟叙事
- `~42us` 内部决策、`4~7ms` 网络 RTT 这类工程指标

但对我们 desk 真正更值钱的，不是“又一个低延迟引擎”，而是它把一条 **crypto perp pairs raw alpha** 写成了比较完整的研究到执行链：

1. `data_loader.py`：抓 Binance USDⓈ-M top-50 liquid assets 的 `1m` K 线；
2. `analyzer.py`：先做相关性筛选，再做 OLS hedge ratio + ADF，找协整 pair；
3. `optimizer.py`：对 rolling window / entry z / exit z / stop z 做网格；
4. `main.cpp`：用实时 microprice 和顶级盘口量差，决定是否执行 spread fade。

所以这次真正可迁移的主题，不是“C++ 快”，而是：

> **cointegrated perp spread mean reversion 这条 raw alpha，能不能在 `1m/3m/5m/15m` 上，加上一层 honest 的 microprice/OBI confirmation 后，变成更可执行的短周期相对价值壳。**

## 2. 核心结论
### 2.1 一句话结论
这份 repo 最值得 desk 拿走的，不是 HFT 外壳，而是：

> **用协整筛出来的 perp 对做 spread fade，把 top-of-book microprice 与 OBI 当作 entry confirmation / veto。**

这仍然是 **raw alpha**，不是 filter 伪装成 alpha：
- alpha 本体是 **spread mean reversion**；
- microprice / OBI 只是告诉你这次回归是否更像“能下手”的回归。

### 2.2 为什么这不是又一篇普通 pairs 教材
我们最近已经补了不少 pairs / stat-arb 线，但这份 repo 多了一层 **short-cycle 可执行性**：
- 不是只在 bar close 上看 z-score；
- 而是把 `!bookTicker` 里的 **microprice** 和 **盘口失衡** 接到 runtime；
- 让 raw alpha 从“回测能看见”往“实盘能不能少踩几次单腿继续挤压”推进一步。

这点对 `1m/3m/5m` 尤其重要，因为很多 pair spread 在 candle close 上像会回归，但一到真实盘口就会发现：
- 一腿在被持续扫单；
- 另一腿只是慢半拍；
- 你看到的 spread 扩张，其实是单边压力还没结束。

这时，top-of-book imbalance 才真的开始有意义。

## 3. 源码里最该拿走的 3 个零件
### 3.1 pair formation：它不是盲配，而是先做相关性 + 协整 + half-life 约束
`analyzer.py` 的主流程是：
- top-50 liquid USDT-M assets
- 先在 `1h` 重采样数据上做相关性筛选（`MIN_CORRELATION = 0.85`）
- 对候选 pair 做 OLS hedge ratio
- 对 spread 做 ADF（`p < 0.05`）
- 再加 half-life 过滤

对 short-cycle desk 来说，最可迁移的不是“协整”三个字，而是它把 pair formation 明确成：

> **先让 pair 至少像一个会回来的东西，再谈入场和执行。**

### 3.2 runtime 信号：spread 用 microprice，confirmation 用 OBI
`main.cpp` 里不是直接拿 last trade price，而是读取 `!bookTicker`：
- `p1 / p2` 实际用的是 top-of-book microprice proxy
- 同时读取 bid/ask volume
- `obi = (bid_vol - ask_vol) / (bid_vol + ask_vol)`

runtime 核心就是：
- spread 极端（`|z| > 2`）才考虑动手；
- 两腿盘口失衡别明显反着你；
- 回到 exit band 再平。

这比“只要 z-score 到了就进”诚实得多。对 short-cycle 而言，这个 confirmation 层比再多加一个技术指标更有用，因为它直接碰到 **执行时刻的订单簿现实**。

### 3.3 执行外壳：它天然适合 market-neutral / relative-value sleeve
repo 的执行是双腿同步下单、固定 notional、实时风控暂停。这意味着它天然服务于：
- pairs / stat-arb sleeve
- relative-value intraday book
- 可与现有 directional alpha 解耦的 market-neutral 子仓

这正好补我们当前素材池里一块缺口：

> **pairs alpha 不缺，缺的是更接近真实盘口的短周期执行确认层。**

## 4. 但源码里也有 3 个不能忽略的硬伤
这份 repo 不能直接照抄上线，至少有 3 个地方必须先拆开看。

### 4.1 half-life 注释和实际单位对不上
`analyzer.py` 先把数据 `resample('1h')`，然后算 half-life，并设：
- `MAX_HALF_LIFE = 240  # Max 4 hours to revert`

但这里 half-life 是在 **小时频率** 上算的；`240` 更像 **240 小时**，不是 4 小时。它后面只是把结果乘 `60` 打印成分钟。

也就是说：
- 注释写的是“4 小时内回归”；
- 实际筛选更接近“10 天内回归都能进”。

这会把 pair universe 放得比 README 读起来宽很多。

### 4.2 optimizer 和 runtime 实际没真正接上
`optimizer.py` 会产出：
- `window_minutes`
- `entry_z`
- `exit_z`
- `stop_z`

但 `main.cpp` 真正运行时是硬编码：
- `Z_ENTRY = 2.0`
- `Z_EXIT = 0.5`
- `BET_SIZE = 1000.0`

并且 runtime 读取 `strategies.json` 时实际依赖的是：
- `leg1`
- `leg2`
- `hedge_ratio`
- `mean`
- `std_dev`

这也是为什么 repo 额外放了一个 `fix_strategies.py`：它重新补 `mean/std_dev`。换句话说：

> **research layer 的参数优化，目前并没有被 honest 地带进 live runtime。**

所以我们应该把它当成：
- 一套有用的 research skeleton；
- 不是一套已经 fully wired 的完整策略。

### 4.3 OBI 阈值现在更像“宽松 veto”，还不像“强确认”
当前 `main.cpp` 里的 OBI 阈值：
- `OBI_LONG_THRESHOLD = -0.2`
- `OBI_SHORT_THRESHOLD = 0.2`

但实际入场条件更像：
- 对 spread 过高要做空 leg1 / 做多 leg2 时，只要求 `obi1 < 0.2` 且 `obi2 > -0.2`
- 对 spread 过低时反向入场，也只是镜像条件

这其实很宽：
- 它能排掉极端反向盘口；
- 但还称不上“只有当 OBI 真支持回归才动手”。

对我们 desk 来说，更 honest 的写法应该是：
- 要么做 **sign-aligned** 硬确认；
- 要么把 OBI 做成分层 score，而不是几乎处处放行的门槛。

## 5. 为什么这轮值得写，而不是继续补别的 funding / basis 题
因为它直接服务于当前阶段更该补的那一类：
- **raw alpha 素材池里的 pairs / stat-arb / relative-value**；
- 而且是能往 `1m/3m/5m` execution reality 再走一步的那种。

如果继续补 funding / basis，我们当然也能找到题；但那条线最近已经比较密。相反，这个 repo 给的是另一块更缺的东西：

> **pair spread fade 不只是 formation / z-score / hedge ratio，真正会卡住 short-cycle 的，是“入场那一刻订单簿是否站在你这边”。**

这就是它比继续补一个 generic pairs 教材更值得的地方。

## 5.5 策略拆解（必填）
- 方向属性：**pairs / stat-arb / relative-value / market-neutral-ish / short-horizon mean reversion**
- 基础 alpha：**协整 perp 对的 spread 极端偏离后向均值回归**
- regime：更适合横盘到弱趋势、pair relationship 尚未结构性断裂、两腿都仍有正常盘口深度的时段
- filter / veto：
  - 先做 pair formation（相关性 + ADF + half-life）
  - `|z|` 未达阈值不做
  - OBI / microprice 若明显反着回归腿，不做
  - 一腿盘口陈旧 / 薄书 / 单腿交易失败，不做
- risk / sizing / execution overlay：
  - 双腿 notional 配平
  - spread stop + time stop + pair-breakdown veto
  - maker/taker 组合分开做成本预算
  - 单 pair 同时只允许一笔 active spread

## 6. 本地 portability probe：这条线在 Binance 公共 `1m` 上有 first verdict 吗？
我用 Binance USDⓈ-M 公共 `1m` K 线，对 repo `strategies.json` 里几组 pair 做了一个最小快检。

### 6.1 口径
- 数据：Binance USDⓈ-M public klines
- 窗口：最近 `14` 天 `1m`
- spread 定义：`log(P1) - hedge_ratio * log(P2)`
- `z-score`：rolling `60m`
- 事件：`|z| >= 2`
- 指标：未来 `5m / 15m / 60m` 的 `signed spread-close bps`
  - 正值 = 朝均值回归
- 注意：**这里只是 close-proxy**，没有历史 top-of-book OBI，因此它只能验证“price-level 上有没有 first-pass mean reversion”，不能直接当 executable PnL

### 6.2 结果先看一句话
- **AXSUSDT/FILUSDT** 的 close-proxy 边最大，但 `AXSUSDT` 当前 24h quote volume 只有约 `7.48M`，更像“统计上好看、执行上要小心”的候选。
- **ADAUSDT/HYPEUSDT** 更像当前更值得优先推进的 live candidate：两腿 24h quote volume 约 `165M / 220M`，流动性体感比 `AXS/FIL` 健康得多。

### 6.3 ADAUSDT/HYPEUSDT 的 first-pass 数字
本地 artifact：`reports/artifacts/literature/statarb_hft_repo_portability_summary_2026-04-11.csv`

对 `ADAUSDT/HYPEUSDT`：
- hedge ratio：`0.01967848`
- 样本行数：`20160`
- `|z| >= 2` 事件数：`2476`
- 事件占比：`12.28%`
- 当前 24h quote volume：
  - `ADAUSDT ≈ 165.45M`
  - `HYPEUSDT ≈ 219.88M`

未来 signed spread-close：
- `5m`: **+2.67 bps**，胜率 **59.6%**
- `15m`: **+5.95 bps**，胜率 **60.6%**
- `60m`: **+5.48 bps**，胜率 **59.1%**

这组数字说明两件事：
1. **spread fade 本体没有死**——至少在公共 `1m` close-proxy 上，极端 z-score 后未来 `15m` 的回归倾向仍然存在；
2. 但它的 edge 也没有大到可以无视成本——若双腿都 taker，很多时候未必够厚；这反而正好解释了 repo 为什么要往 microprice / OBI / 低延迟执行去补壳。

### 6.4 为什么我不把 AXSUSDT/FILUSDT 直接写成主 pair
`AXSUSDT/FILUSDT` 在同一份 summary 里，`15m` mean spread-close 约 **+10.48 bps**，明显更亮眼；但：
- `AXSUSDT` 当前 24h quote volume 约 **7.48M**；
- 比 `ADA/HYPE` 薄不少；
- 真正进 executable BBO 回测后，滑点与 fill-risk 更可能把优势吃掉。

所以更合理的读法不是“最大 close-proxy edge 就是最佳 live candidate”，而是：

> **先用 close-proxy 找可能有回归生命迹象的 pair，再按流动性把它们分成“先上 BBO 回放”和“先放观察名单”。**

## 7. 可复刻的最小实验
### 7.1 数据源 / 公开性 / 更新频率
- Binance USDⓈ-M klines：公开 REST，可拿 `1m`
- Binance `!bookTicker`：公开 websocket，可拿准实时 top-of-book
- 不需要专有数据就能做第一轮 replication

### 7.2 最小研究假设
> 当 Binance perp pair 的 rolling spread z-score 达到 `|z| >= 2`，且订单簿 microprice / OBI 不反着均值回归方向时，未来 `5m~15m` 的 spread-close 更可能为正；若再加 maker/taker 成本后仍为正，这条 raw alpha 才算真正过第一关。

### 7.3 最小回测切口
第一轮别贪多，直接做：
- universe：先从 repo summary 里流动性更健康的 `ADA/HYPE`, `DOGE/HYPE`, `LINK/SOL` 开始
- formation：滚动 `14d` 或 `30d` 重估 hedge ratio + cointegration
- signal：`60m` rolling z-score，先试 `1.5 / 2.0 / 2.5`
- confirm：
  - short leg `OBI <= -0.15`
  - long leg `OBI >= +0.15`
  - 或至少做三档 score 分层
- exit：`|z| <= 0.5`、`15m/30m time stop`、`spread stop`
- 成本：至少做 `maker/maker`、`maker/taker`、`taker/taker` 三档

## 8. 下一步怎么测
下一步我不会先扩 universe，而是先做 4 件最值钱的事：

1. **把 close-proxy 升级成 live BBO event log**
   - 连 Binance `!bookTicker`
   - 记录 spread、microprice、bid/ask size、OBI、触发时刻
   - 先做 paper fill，不急着真钱撮合

2. **把 formation 和 runtime honest 接线**
   - 不再让 optimizer 和 live engine 脱节
   - 把 `window / entry_z / exit_z / stop_z` 真正写入 runtime
   - 同时修 half-life 单位混乱问题

3. **把 OBI 从宽松 veto 改成真正 confirmation**
   - 不是“别太反着就行”
   - 而是要求两腿盘口压力对回归方向有明确支持，或至少做 score ranking

4. **先用流动性把 pair 分层**
   - `AXS/FIL` 这种 close-proxy 更亮但偏薄的，先放观察名单
   - `ADA/HYPE` 这种 edge 没那么夸张但更厚的，优先做 executable-BBO 回放

如果 `ADA/HYPE` 这类 pair 在 `maker/taker` 成本下，`15m` 仍能保留正的净 spread-close，那这条线就值得进入 clean replication 队列；如果只在 close-proxy 下好看，一上 BBO 就塌，那它更适合降级成 **pairs sleeve 的 entry confirmation / veto layer**，而不是独立交易壳。

## 9. 风险与保留意见
- 这份 repo 的核心价值是 **research skeleton + execution idea**，不是已经 fully productionized 的策略。
- 当前 public probe 没有历史 OBI，只验证了 price-level 上的 mean reversion 倾向；**不能把这些数字直接解释成实盘净值**。
- pairs alpha 最大的风险不是“z-score 不回”，而是 **pair relationship 坏掉、单腿流动性塌陷、或一腿继续被挤压**。
- 如果 microprice / OBI confirmation 做不好，这条线很容易从“均值回归”退化成“接刀子”。
- 这条线最值得的地方，不是保证赚钱，而是它把 **pair formation -> spread signal -> order-book confirmation -> 双腿执行** 这条链路写得足够清楚，值得我们拿来做 honest replication。

## 10. 来源
### 主来源（repo）
- Samarth Chaudhary. (2026). *Crypto Stat-Arb HFT Engine*. GitHub repository.
- Venue / DOI：GitHub repository / 无 DOI
- Repo URL：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model`
- README：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/README.md`
- Pair discovery：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/analyzer.py`
- Historical loader：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/data_loader.py`
- Parameter optimizer：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/optimizer.py`
- Strategy repair script：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/fix_strategies.py`
- Runtime engine：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/main.cpp`
- Strategy config sample：`https://github.com/SamarthChaudhary-22/Crypto_Stat-Arb_HFT_Model/blob/main/strategies.json`

### 本地 portability artifacts
- Summary：`/root/clawd/jerry/momentum/reports/artifacts/literature/statarb_hft_repo_portability_summary_2026-04-11.csv`
- ADA/HYPE detail：`/root/clawd/jerry/momentum/reports/artifacts/literature/statarb_hft_repo_portability_detail_adausdt_hypeusdt_2026-04-11.csv`

### 本地 probe 说明
- 数据源：Binance USDⓈ-M public `1m` klines + `24hr ticker`
- 作用：验证 repo 给出的 pair shell 在公开可得数据上，是否至少存在 first-pass spread-close 倾向
- 不包含：历史 top-of-book OBI、真实成交回放、maker/taker fill model
