# 别把这份 2026 lead-lag repo 只读成“BTC 先跌、山寨后跟”的直觉故事：对 short-cycle desk，更该先拆的是「BTC shock × dual-regime alt-lag basket」这条完整 raw alpha 壳

- 时间：2026-04-15 04:39 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `scripts/simulate_6months.py` + `scripts/paper_trade.py` + `src/paper/config.py` + `src/paper/trader.py` + `src/paper/position_manager.py` + `src/paper/price_tracker.py` + `src/features/engineering_v2.py`）+ Binance Spot `1m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**BTC 在 `5m` 内先发生足够大的方向冲击，alt basket 的反应存在可交易时滞；bear regime 做 `BTC dump -> short lagging alts`，bull regime 做 `BTC dip -> long lagging alts`。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-asset/lead-lag/event-driven/btc-shock/alt-lag/basket/dual-regime/fixed-hold/leverage-scaling/binance/kraken/1m/5m/15m/30m/repo/public-data/cost/risk
- 证据类型：repo + public-data probe

## 1. 这次看了什么
主来源是一份 2026 GitHub 新 repo：
- **Authors：** `mamipour`（GitHub handle；README 未写实名）
- **Year：** 2026
- **Title：** *Crypto Lead-Lag Trading Bot*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/mamipour/lead-lag-trader>
- **Repo URL：** <https://github.com/mamipour/lead-lag-trader>

先把 base alpha 说清楚：
> **这份东西的 base alpha 不是“BTC 是市场龙头”这种宏观废话，而是一个很具体的事件驱动 lead-lag：`BTC 5m shock 先发生，alt 在后续 15m/30m 里继续朝同方向补跌 / 反打`。**

它和我们最近收过的几类题不一样：
- 它**不是** pairs / spread fade；
- 它**不是** funding / basis / carry；
- 它也**不是** cross-sectional leader-lagger ranking 论文那种“先算谁是 leader bucket”；
- 它更像一条 **single-leader（BTC）→ multi-follower（alt basket）** 的 event-driven raw alpha shell，而且 repo 已经把 **entry / hold / leverage / cost / live paper trading** 都写出来了。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的，不是“BTC 先跌、alts 会跟”这句口号，而是 **`BTC shock × dual-regime alt-lag basket`** 这条完整 raw alpha 壳：同样是 BTC 先动，**熊市做补跌 short，牛市做 dip-buy long**，并且用固定持有期和 regime filter 把它变成一条可执行策略。
- **一句话证明方式：** README + 回测脚本口径一致：repo 用 **Binance `1m` 历史数据（约 4 年）** 做特征与回测、用 **Kraken Futures 公共 WebSocket** 做实时 paper trading，给出完整参数、费用、持仓管理与滚动窗口统计。
- **repo 的策略骨架是完整的。** `scripts/simulate_6months.py` 明确写了两条分支：
  - **Bear branch：** 当 `BTC 5m` 跌幅 `>=1%`，且 `BTC 7d return <= -5%`，做 **short alt basket**，默认 **持有 `15m`**；若跌幅超过 `2%` 则跳过，避免 crash 反抽。
  - **Bull branch：** 当 `BTC 5m` 跌幅 `>=0.5%`，且 `BTC 7d return >= 0%`、`BTC 3d return >= 0%`，做 **long alt basket**，默认 **持有 `30m`**。
- **risk / sizing / cost 也不是空白。** bear 支路有 **1x~2x** 的 leverage scaling：`lev = clip(1 + 2*(drop_pct-1), 1, 2)`；时间过滤明确跳过 **UTC 7~11 点**；round-trip cost 写死为 **maker `0.02%/side` + slippage `1bp/side` = `6bps`**。
- **live path 也给了。** `scripts/paper_trade.py` + `src/paper/trader.py` 直接连 Kraken Futures 公共 ticker 做无 API key 的 paper trading，这意味着它不是“只有 notebook 没有交易状态机”的 repo。

## 3. 为什么和当前项目有关
这条题和当前 `momentum` 主线直接相关，原因有三层：

1. **它补的是 raw alpha，而不是解释层。**
   这不是“BTC 很重要”的宏观叙事，而是一个可以在 `1m -> 5m formation -> 15m/30m exit` 上立刻做最小实验的 event-driven alpha。

2. **它补的是我们近期 intake 里相对少的“跨资产单 leader 冲击路由”。**
   这几天 intake 很多是 pairs / spread / cross-sectional mean reversion；这份 repo 提供的是另一条可复现主线：**leader shock routing**。

3. **它天然 desk 化。**
   不需要专有数据，不需要闭源 order flow；只要 **公开 BTC/alt `1m` klines** 就能回放，执行层还可以从现货 proxy 升级到 perp / cross-venue / faster routing。

## 3.5 策略拆解（必填）
- 方向属性：**cross-asset / event-driven / basket / directional / lead-lag**
- 基础 alpha：**BTC 冲击先发生，alts 对该冲击的价格补偿存在可交易延迟**
- regime：**`BTC 7d return` 决定 bear / bull / neutral；bull branch 还要额外检查 `BTC 3d return >= 0`**
- filter / veto：**UTC `7~11` 禁做；bear branch 跳过 `BTC 5m drop > 2%` 的 crash-like 事件；持仓期间不叠加新事件**
- risk / sizing / execution overlay：**bear branch 1x~2x leverage scaling、equal-weight basket、固定 `15m/30m` time exit、`6bps` round-trip maker+slippage 基线**

## 4. repo 真正给了哪些可执行细节
### 4.1 Entry / Exit
**Bear short（补跌支路）**
- 触发：`BTC 5m return <= -1%`
- regime：`BTC 7d return <= -5%`
- veto：若 `BTC 5m drop > 2%`，直接 skip
- 持有：`15m`
- 方向：`short` 全部 follower alts

**Bull dip-buy（反打支路）**
- 触发：`BTC 5m return <= -0.5%`
- regime：`BTC 7d return >= 0%`
- extra gate：`BTC 3d return >= 0%`
- 持有：`30m`
- 方向：`long` 全部 follower alts

### 4.2 Universe
README 写的是 **19 个 altcoins**，覆盖 large / mid / small cap：
`ETH, SOL, BNB, XRP, ADA, AVAX, LINK, DOT, NEAR, SUI, ARB, OP, APT, INJ, FET, PEPE, TIA, DOGE, SHIB`。

这点很关键：
> **它不是单币 ETH/BTC lead-lag，而是“BTC 事件 -> alt basket”路由。**

### 4.3 Size / Capital Use
- `src/paper/position_manager.py` 的 live paper-trading 版本默认是**等权拆到每个 coin**；
- 回测脚本 `simulate_6months.py` 在 event timestamp 上按可交易 coin 数量做 **equal-weight capital split**；
- bear 分支 leverage 随 BTC 跌幅增加，但 capped at `2x`。

### 4.4 Cost / Friction
repo 明确给了费用：
- maker fee：`0.02% / side`
- slippage：`1bp / side`
- round trip：`6bps`

这不是 production-ready 成本建模，但已经足够支持 first-pass replication。

## 5. 我补做的 portability probe
为了避免只抄 repo headline，我额外用 **Binance Spot 公共 `1m` 数据**做了一个最近样本快检，镜像 repo 的核心规则，但先只测流动性更高、最容易被套利抹平的 `BTC -> {ETH, SOL, DOGE}`。

### 5.1 probe 口径
- **数据：** Binance Spot public `1m` klines
- **样本：** 近 `30d`
- **leader：** `BTCUSDT`
- **followers：** `ETHUSDT, SOLUSDT, DOGEUSDT`
- **bear 规则：** `BTC 5m <= -1%`、`BTC 7d <= -5%`、持有 `15m`、跌幅上限 `2%`、lev scaling 同 repo
- **bull 规则：** `BTC 5m <= -0.5%`、`BTC 7d >= 0%`、`BTC 3d >= 0%`、持有 `30m`
- **费用：** 统一扣 `6bps` round trip
- **事件去重：** bear `15m` 内不重叠，bull `30m` 内不重叠
- **时段过滤：** 跳过 UTC `7~11`

### 5.2 probe 结果
- **Bear events：** `1` 个
  - 平均事件净收益：`-32.98 bps`
- **Bull events：** `13` 个
  - 平均事件净收益：`-31.85 bps`
  - 中位数事件净收益：`-37.80 bps`
  - 胜率：`30.8%`
  - 近似累计：`-4.12%`

### 5.3 这组 probe 怎么读
这组 quick check 给出的 first verdict 很直接：

> **结构是清楚的，但在最近 `30d` 的 liquid-major spot proxy 上，这条 edge 没有自然穿过成本线；尤其 bull dip-buy 分支，已经明显偏负。**

也就是说：
- 这条 repo **作为 raw alpha skeleton 是成立的**；
- 但如果你直接把它搬到最近 majors、同 venue、慢速 execution，上线就大概率先死在 **lag 被压缩 / 过度拥挤 / 成本**；
- 真正值得继续测的，不是“完整照抄 19 币一起上”，而是：
  1. **是否只剩 mid/small-cap pocket 还活着**；
  2. **是否只有 bear short 分支还值得保留**；
  3. **是否必须做 event 后的 follower ranking，而不是全篮子等权。**

## 6. 先记 7 个最重要的数据点
1. **repo 的 formation clock 非常明确：** `BTC 5m move` 触发。  
2. **双 regime 分叉明确：** bear 做补跌 short，bull 做 dip-buy long。  
3. **持有期也明确：** bear `15m`，bull `30m`。  
4. **bear 支路有硬风险闸：** `BTC drop > 2%` 直接不做。  
5. **成本基线明确：** round-trip `6bps`。  
6. **README headline 很强：** `2022-04 ~ 2026-03`，`$10k -> $47,839`，总回报约 `+378%`，年化约 `49%`，`25,230` trades，win rate `55%`。  
7. **但我补的 recent-30d portability probe 很弱：** majors spot proxy 上 bull branch 已显著负值，说明这不是当前可以无脑进 production 的“完整可用 alpha”。

## 7. 下一步怎么测
### 最小实验
先不要照 repo 一口气上 19 币全篮子，而是做一个更 desk-friendly 的分层实验：

- **市场：** Binance USDⓈ-M perp 优先；Spot 只做 proxy
- **频率：** `1m` 数据；formation 维持 `5m`
- **leader：** `BTCUSDT`
- **followers：** 先分三层：`liquid majors / mid-caps / small caps`
- **事件：**
  - bear：`BTC 5m <= {-0.8%, -1.0%, -1.2%}`
  - bull：`BTC 5m <= {-0.4%, -0.5%, -0.6%}`
- **exit：** `10m / 15m / 20m / 30m` 网格
- **cost ladder：** `4 / 8 / 12 bps`
- **ranking overlay：** 只做 event 时刻 **catch-up 最弱** 的 bottom `k` followers，而不是等权全篮子

### 优先级最高的 5 个后续问题
1. **Bear / bull 两条分支要拆开验，不要再混着看。**
   最近样本里 bull dip-buy 明显在拖后腿；它可能应该直接降级为可选分支。

2. **先测 “lagger ranking” 是否比“全篮子等权”更诚实。**
   repo 里 `engineering_v2.py` 已算了 `catchup_ratio_5m`、`momentum_div_5m/10m/15m`，这说明作者也知道“谁还没跟上”才是核心，不该永远所有币一起做。

3. **把 venue 问题单独拎出来。**
   repo 的回测数据来自 Binance，但 live paper trade 放在 Kraken Futures；如果 edge 的一部分来自 venue 间时滞，那就不该用 same-venue spot proxy 一刀切判死，也不该忽略执行延迟。

4. **把小币口袋和大币口袋拆开。**
   如果 liquid majors 已被套利压平，edge 可能只剩 `mid/small-cap`，那 production 版就该改成“事件触发 + 分层 universe + 流动性上限”，不是无脑 19 币全开。

5. **检查是否需要更快的入场，而不是更长的持有。**
   如果 lag 主要存在于 shock 后最初几分钟，`15m/30m` 可能已经太慢；下一轮可以测 `entry latency 0/1/2m` 与 `hold 5/10/15m`。

## 8. first verdict
我的判断是：

> **这份 2026 repo 值得进素材池，因为它提供了一条“可直接跑起来”的跨资产 lead-lag raw alpha skeleton；但按我补的 recent-major portability probe 看，它还不配被当成当前 desk 的现成 production shell。**

更直白地说：

> **可以 intake 这条结构，但不要相信“BTC 一跌，alts 必补跌 / 必反打”在 2026 还天然有肉。现在更像需要二次拆解成：`BTC shock router` + `lagger ranking` + `universe tiering` + `faster exit`。**

所以这轮最合理的定位是：
- **它是合格的 raw alpha 候选；**
- **也是完整策略骨架；**
- **但 recent portability verdict 偏负，下一步应优先做 pocket 化和分支删减，而不是直接全盘照搬。**

## 9. 数据与可得性
- **数据源：** Binance / Kraken 公共 `1m` 价格流；repo live 端用 Kraken Futures WebSocket，无需 API key
- **公开性：** 公开可得
- **更新频率：** `1m` 历史 / 实时 ticker
- **最小可复现实验口径：** `BTC 5m shock` 触发 follower basket，按 regime 决定方向，持有 `15m/30m`，先做 equal-weight baseline，再加 lagger ranking

## 10. 来源
- `mamipour` (2026). *Crypto Lead-Lag Trading Bot*.
  - Readable URL / Repo URL: <https://github.com/mamipour/lead-lag-trader>
  - README: <https://github.com/mamipour/lead-lag-trader/blob/main/README.md>
  - `scripts/simulate_6months.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/scripts/simulate_6months.py>
  - `scripts/paper_trade.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/scripts/paper_trade.py>
  - `src/paper/config.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/src/paper/config.py>
  - `src/paper/trader.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/src/paper/trader.py>
  - `src/paper/position_manager.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/src/paper/position_manager.py>
  - `src/paper/price_tracker.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/src/paper/price_tracker.py>
  - `src/features/engineering_v2.py`: <https://github.com/mamipour/lead-lag-trader/blob/main/src/features/engineering_v2.py>
  - DOI: N/A
