# 别把这个 2026 funding-arb 仓只读成“跨所 funding 看板”：对 short-cycle crypto desk，更该先拆的是「opposite-sign funding spread × order-book slippage veto × 8h max-hold」这条完整 raw alpha 壳
- 时间：2026-04-25 10:37 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：cross-exchange opposite-sign funding carry（在负 funding 交易所做多、在正 funding 交易所做空，赚 funding spread）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / carry / funding / cross-venue / delta-neutral / slippage-veto / orderbook / max-hold / Binance / Bybit / OKX / 8h / 15m / 5m
- 证据类型：repo 源码审计 + public-data portability probe

## 1. 这次看了什么
这次看的是 2026 GitHub 仓库 **`johann-clouie/crypto-trading-bot`**。README 表面上把它包装成一个“12 交易所 funding arbitrage bot”，但真正值得 desk intake 的，不是“支持 12 所”这层 UI 叙事，而是它把一条 **可以直接写成完整策略壳** 的 raw alpha 摊得很直白：

- `funding_rate_scanner.py`：找 **一边 funding 为负、另一边 funding 为正** 的同标的跨所机会
- `entry_strategy.py`：先过 **order-book 深度 / slippage** 检查，再决定能不能进
- `fee_calculator.py`：先扣 fees，再判断是不是值得做
- `exit_strategy.py`：给出 **profit target + 8h max duration** 的退出框架
- `strategy_validator.py`：把上面几层串成 pre-trade veto

所以这份材料不是纯看板，更像一个 **cross-venue funding carry 的最小可落地框架**。

## 2. base alpha 先说清楚
这篇东西的 **base alpha 很清楚**：

**同一标的在不同交易所的 funding rate 若出现 opposite sign（例如 A 所为负、B 所为正），就能做 `long negative-funding venue + short positive-funding venue` 的 delta-neutral carry，收益主要来自 funding spread。**

这首先是 **raw alpha**，不是 filter，也不是 overlay。

repo 里最有 desk 价值的旁支，不是“再多接几家交易所”，而是：

**不要把 funding spread 本身当成充分条件；必须再叠一层 order-book slippage veto 和 fee-aware admission。**

## 3. 核心结论
- 这份 repo 最值钱的地方，不是“12 交易所覆盖面”，而是它把一条 **opposite-sign funding carry** 明确写成了完整策略壳。
- `funding_rate_scanner.py` 的核心 admission 很朴素：只有当 **long leg funding < 0 且 short leg funding > 0** 时，才认为存在可收的 spread；并且先做一个简化的 fee 扣减后才留下候选。
- `entry_strategy.py` 的高价值点是：**先查盘口深度和 slippage，再决定能不能进**，而不是看到正 carry 就直接下单。这比很多 funding note 更像真正能上 desk 的版本。
- `exit_strategy.py` 则把这条线从“静态 funding 观察”推进到“可落地策略”：**到达 profit target、或持仓超过 8h 就平**。
- 但我做的 public-data portability probe 给了一个很明确的现实提醒：**公开大所上的 opposite-sign spread 现在并不厚**。即便 opposite-sign 并不罕见，gross carry 大多也只有 `~0.7–1.0 bps / funding period`，远低于可交易成本门槛。

## 4. 为什么和当前 desk 直接相关
虽然 funding carry 不是逐根 `5m` 主信号，但它仍然符合 bot7 当前更高优先级：

- base alpha 清楚：cross-venue opposite-sign funding spread
- entry 清楚：只有 opposite sign + 过 fee/slippage veto 才进
- exit 清楚：profit target / funding 收敛 / 8h max-hold
- sizing 清楚：repo 默认固定 notional，可继续外接 risk budget
- risk 清楚：order-book depth、slippage、funding 收敛、basis / quote drift
- cost 清楚：四腿开平仓 fees 是第一约束

对 short-cycle desk 来说，`15m / 5m` 在这里承担的是：
- child execution timing
- slippage / depth 监控
- add / reduce cadence
- unwind timing

而不是把 8h funding 本身硬装成逐根短周期主信号。

## 5. 源码里真正值得复用的部分
### 5.1 opposite-sign admission 比“谁 funding 更高”更干净
`funding_rate_scanner.py` 不是简单做 funding ranking，而是明确要求：
- long leg funding `< 0`
- short leg funding `> 0`

然后 gross spread 近似写成：
`abs(long_rate) + short_rate`

这件事的好处是：
- base alpha 定义非常清楚
- 避免把“正 funding vs 更正 funding”的弱 edge 和真正 opposite-sign pocket 混在一起
- 更方便后续做 public-data first verdict

### 5.2 slippage veto 是这份 repo 最像 desk 组件的地方
`entry_strategy.py` 会：
- 拉两边 order book
- 用目标 size 沿盘口吃深度，估算平均成交价
- 再和 mid 做比较
- 若任一边 slippage 超过 `0.1%`，直接 veto

这比“看到正 APR 就冲”强很多。对 funding carry 这类边很薄的策略来说，**slippage veto 不是锦上添花，而是 admission 本体的一部分**。

### 5.3 8h max-hold 让它更像 funding pocket，而不是常开仓位
`exit_strategy.py` 给的核心规则很简单：
- profit target 到了就走
- 否则最多持有 `8h`

这个设定很有用，因为它隐含了一个更 desk 化的读法：

**这条线不应该被当成 always-on 收租机，而更像“只在 funding dislocation 足够厚时短时持有”的 pocket strategy。**

## 6. public-data portability probe：Binance / Bybit / OKX 最近 51 个 funding 点
我用三家公开 API：
- Binance USDⓈ-M funding history
- Bybit linear perpetual funding history
- OKX swap funding history

对 `BTCUSDT / ETHUSDT / SOLUSDT` 做了最近 `51` 个对齐 funding period 的快检；每个时点都在三所里找 **best opposite-sign pair**，然后计算：
- gross spread
- repo 风格简化净值：`gross - 4bps`
- maker 四腿粗扣净值（按 repo/常见费率近似）
- taker 四腿粗扣净值

产物：
- `reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_detail.csv`

### 6.1 关键结果
- `BTC`：`51` 个对齐 funding 点里，出现 opposite-sign 的有 `22` 个，占比约 `43.1%`
  - gross 平均仅约 `0.71 bps / 8h`
  - 粗扣 `4 bps` 后平均约 `-3.29 bps / 8h`
  - 粗扣 maker 四腿后平均约 `-6.38 bps / 8h`
- `ETH`：`51` 个里有 `26` 个 opposite-sign，占比约 `51.0%`
  - gross 平均约 `0.96 bps / 8h`
  - 粗扣 `4 bps` 后平均约 `-3.04 bps / 8h`
  - maker 四腿后平均约 `-5.50 bps / 8h`
- `SOL`：`51` 个里有 `12` 个 opposite-sign，占比约 `23.5%`
  - gross 平均约 `1.00 bps / 8h`
  - 粗扣 `4 bps` 后平均约 `-3.00 bps / 8h`
  - maker 四腿后平均约 `-5.16 bps / 8h`

### 6.2 这组数怎么读
一句话：

**opposite-sign 不是没有，但公开大所 majors 上现在通常只够当 signal candidate，不够直接下场。**

也就是说，这份 repo 最值得保留的不是“这条 alpha 已经能在 BTC/ETH/SOL 上直接赚钱”，而是它给了一套很清楚的 **admission / veto / hold framework**：
- 只有 opposite-sign pocket 才入围
- 必须过 fee-aware 检查
- 必须过盘口 slippage veto
- 不能当 always-on carry，要有 time-box

## 7. 最小可复现实验
### 最小实验 A：三所 opposite-sign carry 生存性
- 标的：`BTC / ETH / SOL`
- 交易所：`Binance / Bybit / OKX`
- parent frequency：funding period（8h）
- child execution：`15m`，必要时细到 `5m`
- 规则：
  1. 每个 funding 时点找 best opposite-sign pair
  2. 要求 gross spread > fee hurdle
  3. 再要求两边盘口 size 下的 expected slippage < threshold
  4. 持有到下一 funding 或提前 profit-take / convergence-exit

### 最小实验 B：只保留极端 pocket
因为目前 gross 太薄，更值得先测的是：
- 只做 `gross spread >= 5 bps / 8h`
- 或只做该 spread 的 rolling `p95` 以上事件
- 再看这些极端 pocket 是否主要集中在 `mid-cap / event regime / 单一交易所异常`，而不是 BTC/ETH 常态期

## 8. 下一步怎么测
1. **先不要扩 12 所。** 先固定 `Binance / Bybit / OKX` 三所，把 opposite-sign pocket 的历史分布跑干净。
2. 把 admission 从“只要 opposite sign”升级成三层：
   - `gross spread > fee hurdle`
   - `gross spread > rolling p90 / p95`
   - `order-book slippage < threshold`
3. 按币种分层：`BTC/ETH` 先当 base reality check；如果一直不够厚，再把注意力转去 `SOL / XRP / DOGE / PEPE` 这类 funding 更容易失衡的币。
4. 把 exit 分成两版对照：
   - 持有一个 funding period
   - `15m/5m` child-level convergence exit
5. 若 majors 持续不过线，这条线就不该被当成主 raw alpha，而应转成：
   - **event-driven carry pocket scanner**
   - 或 **跨所风险看板 / deployment whitelist**

## 9. 风险与保留意见
- 这份 repo 的代码结构是清楚的，但目前仍偏 MVP：不少成本假设写得比较粗，和真实多所执行还有距离。
- scanner 里先减 `4 bps` 的简化处理，**对真实四腿开平仓来说偏乐观**；我自己的 quick probe 说明，现实里更像要面对 `~5–7 bps` maker、甚至更差的成本层。
- 它把 funding carry 写成了完整壳，这点很有价值；但 **不是所有完整壳都能直接赚钱**。这次 portability probe 更像在帮我们决定：这条线该继续做 deployment pocket，还是该降级成 event-only scanner。
- 当前公开大所 majors 的 opposite-sign spread 更像“偶发 dislocation”，不是稳定厚边。

## 10. 一句话总结
**这份 2026 repo 最值得 desk intake 的，不是“支持 12 交易所”，而是它把 opposite-sign funding carry 明确写成了一个“先过 fee，再过 slippage，再限定 8h 持有”的完整 raw alpha 壳；但最近三所 majors 的公开数据告诉我们：常态 edge 太薄，下一步必须只盯极端 pocket。**

## 11. 来源（尽量结构化）
- Source A（主来源，仓库）
  - Authors：`johann-clouie`（GitHub handle；README 未写实名）
  - Year：2026
  - Title：*Crypto Funding Rate Arbitrage Bot*
  - Venue：GitHub repository
  - DOI：N/A
  - Readable URL：https://github.com/johann-clouie/crypto-trading-bot
  - Repo URL：https://github.com/johann-clouie/crypto-trading-bot
- Source B（README）
  - Readable URL：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/README.md
- Source C（核心 admission / shell 文件）
  - `funding_rate_scanner.py`：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/backend/core/funding_rate_scanner.py
  - `entry_strategy.py`：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/backend/core/entry_strategy.py
  - `exit_strategy.py`：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/backend/core/exit_strategy.py
  - `fee_calculator.py`：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/backend/core/fee_calculator.py
  - `strategy_validator.py`：https://raw.githubusercontent.com/johann-clouie/crypto-trading-bot/main/backend/core/strategy_validator.py
- Source D（本轮 public-data portability probe）
  - Binance funding history：https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
  - Bybit funding history：https://bybit-exchange.github.io/docs/v5/market/history-fund-rate
  - OKX funding history：https://www.okx.com/docs-v5/en/#public-data-rest-api-get-funding-rate-history
  - 本地产物：
    - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_summary.csv`
    - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-25_crossvenue_funding_oppositesign_probe_detail.csv`
