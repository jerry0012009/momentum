# 别把这份 Polymarket liquidation bot 只读成预测市场机器人：对 short-cycle desk，更该先测的是「BTC liquidation shock × 30% pullback stink-bid × 5m hard-expiry continuation」这条完整 raw alpha 壳

- 时间：2026-04-15 19:30 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `liq_stink_bot_v2.py` + `.env.example` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：**当 `BTC` 出现中等规模强平事件（repo 默认 `25k~100k USD`）后，短时方向冲击会传到 `Polymarket` 的 `5m UP/DOWN` 二元市场；但与其追价吃 taker fee，更好的执行壳是：沿强平方向做 `hard-expiry continuation`，只是通过 `30% pullback` 的 maker stink bid 低吸合约，若成交再用 `Hyperliquid` 反向开 perp 对冲。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是，repo 已给出 signal / entry / hedge / time-stop / kill-switch / maker-fee 逻辑，但要先把 liquidation feed 完整迁到公开流并补 fill backtest
- 主题标签：raw-alpha/prediction-market/event-driven/liquidation/continuation/pullback-stink-bid/hard-expiry/maker-entry/polymarket/hyperliquid/binance/1m/3m/5m/repo/public-data/cost/risk
- 证据类型：repo source audit

## 1. 这次看了什么
这轮主看的是一个 **2026-04-01** 创建的新 repo：

- **Author / Repo owner：** `cemdenizexe`
- **Year：** 2026
- **Title：** *polymarket-trade-bot-v1*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/cemdenizexe/polymarket-trade-bot-v1>
- **Repo URL：** <https://github.com/cemdenizexe/polymarket-trade-bot-v1>
- **GitHub API metadata（已复核）：** repo 创建于 `2026-04-01 00:38:56Z`，最近 push 时间 `2026-04-01 15:59:34Z`

README headline 很像“预测市场小机器人”，但源码真正值得 desk intake 的不是“能不能自动下 Polymarket 单”，而是它把一条 **事件驱动方向 alpha** 讲得非常具体：

> **`BTC liquidation shock -> 5 分钟 hard-expiry 二元方向延续`，只是执行上不追价，而用 maker stink bid 去吃回撤。**

这就不是我们前面已经做过的那些 Polymarket 主题：
- 不是 `stale quote`；
- 不是 `negation parity gap`；
- 不是 `same-event strike surface mispricing`；
- 也不是 `favorite-side late-entry continuation`。

它的主轴更像：
> **强平事件本身给方向，prediction market 只是一种更适合挂 maker pullback 单的执行载体。**

## 2. base alpha 先说清楚
这轮的 **base alpha** 不是“预测市场有价差”这么泛。

它是：
> **当 `BTC` 出现一笔足够大的强平事件后，未来几分钟的方向并没有立刻结束；但直接追 Polymarket taker 单太贵，于是更优的壳是：保留原方向判断，等一段短回撤，用 maker stink bid 去拿更便宜的 `UP/DOWN` 合约，然后持有到 `5m` 事件结束，并在 `Hyperliquid` 开反向 perp 做 delta/路径对冲。**

翻成人话：
- **方向来自 liquidation shock 本身**；
- **edge 不是“是否看对方向” alone，而是“方向 edge + maker entry + hard expiry” 三件套一起成立**；
- 这是一条 **event-driven / directional / complete-shell raw alpha**，不是单纯 filter。

README 与源码写得很明确：
- `$25K-$100K LONG liq -> bearish -> buy DOWN`
- `$25K-$100K SHORT liq -> bullish -> buy UP`
- 在 `signal price` 基础上 **下调 `30%`** 做 stink bid
- 若成交，则在 `Hyperliquid` 开 **反向 `3x isolated` hedge**

## 3. 为什么这条线值得，而不是再写一篇 prediction-market 价差
因为它补的是我们当前池子里相对缺的一块：

1. **它是 raw alpha，不是 pricing identity。**
   不是“YES+NO 应该等于 1”这种静态约束，而是“强平后 5 分钟方向可能还会继续”这种事件型 directional alpha。

2. **它有完整执行壳。**
   很多 repo 只给信号；这份直接把：
   - 触发条件
   - maker 入场
   - 硬到期
   - 对冲
   - 日损 kill switch
   全部写进去了。

3. **它天然适配 `1m/3m/5m`。**
   这里不是低频情绪故事，而是：
   - liquidation stream：秒级/亚秒级
   - Polymarket orderbook：tick 级
   - Hyperliquid hedge：实时
   - 决策窗口：`<5m`

也就是说，这不是把慢变量硬塞进短周期；它从一开始就是短周期事件交易。

## 4. repo 里哪些实现支撑这条读法
### 4.1 信号层：强平事件不是噪音，而是主触发器
`liq_stink_bot_v2.py` 顶部的策略说明写得很直白：

1. `Stream BTC liquidations from Binance Futures + HyperLiquid`
2. `LONG liq -> bearish signal -> buy DOWN`
3. `SHORT liq -> bullish signal -> buy UP`
4. `Place stink bid at PULLBACK_PCT below signal price`
5. `On Polymarket fill -> hedge inverse on HyperLiquid`

源码默认参数：
- `LIQUIDATION_THRESHOLD_MIN = 25_000`
- `LIQUIDATION_THRESHOLD_MAX = 100_000`
- `LIQUIDATION_WINDOW = 600`（10 分钟滚动窗口）

这说明它不是把任意小额清算都当信号，而是在做一个“中等规模、足够有信息量”的事件 pocket。

### 4.2 入场层：核心不是追价，而是 `30% pullback stink bid`
源码默认：
- `PULLBACK_PCT = 0.30`
- `MIN_TIME_LEFT = 60`
- `MARKET_DURATION = 300`

这几行其实很关键：
- 如果你直接 taker 追 `UP/DOWN`，prediction market fee/spread 很容易把 edge 吃掉；
- 这个 repo 的真正创意不是“看到清算就追方向”，而是：
  **保留方向判断，但只在短回撤里挂 maker 单。**

所以它更像：
> **liquidation continuation alpha + execution alpha**

而不是裸方向赌大小。

### 4.3 成本层：这是个明显在跟 2026 Polymarket 新 fee 结构对齐的壳
源码注释明确写了 2026 规则变化：
- `500ms taker delay removed`
- `Dynamic taker fees up to ~1.56%`
- `makers pay ZERO + earn rebates`

然后它做了两件事：
- WebSocket 订阅 orderbook，不再 REST 轮询；
- 动态请求 `fee-rate`，但默认以 maker 视角处理。

这说明作者不是只在讲概念，而是在围绕：
> **“如果 prediction market taker 变贵，那就把 alpha 改写成 maker-first。”**

对 short-cycle desk 来说，这很值钱，因为这不是 UI 层优化，而是直接决定策略能不能活下来的成本建模。

### 4.4 对冲层：方向判断在 Polymarket，路径风险在 Hyperliquid 管
源码给的默认对冲参数：
- `POLY_USD_PER_POSITION = 5.0`
- `HEDGE_USD = 3.0`
- `HEDGE_LEVERAGE = 3`
- `HEDGE_FILL_WAIT = 0.5`
- `HEDGE_MAX_ATTEMPTS = 10`

这意味着作者默认是：
- Polymarket 名义仓位更大（约总风险的 60%）
- Hyperliquid 反向 perp 作为剩余 40% 的路径/尾部管理工具

这不是纯套利，因为两腿 payoff 结构并不等价；但它确实是一个很短周期、很实际的 **event trade + hedge shell**。

### 4.5 风控层：它不只是会下单，还明确知道自己可能在哪些地方死
源码 / `.env.example` 至少给了：
- `PAPER_TRADING=true`
- `DAILY_LOSS_LIMIT_USD=10`
- `MIN_TIME_LEFT = 60`
- 订单取消 / 重新拉取 fee / reconnect backoff

这里还有一个很值得记的 audit 点：
- README 里写的是：
  - `POLY_USD_PER_POSITION = $15`
  - `HEDGE_USD = $10`
  - `DAILY_LOSS_LIMIT_USD = $50`
- 但源码 / `.env.example` 实际默认是：
  - `POLY_USD_PER_POSITION = 5`
  - `HEDGE_USD = 3`
  - `DAILY_LOSS_LIMIT_USD = 10`

也就是说：
> **repo 的“对外文案口径”和“实际代码口径”并不一致。**

这类不一致很常见，但对我们做复现特别重要：
- 如果只读 README，很容易高估仓位与风险预算；
- 真正复现时应该以源码/`.env.example` 为主。

## 5. 这条策略为什么算“可直接落地完整策略”
因为 entry / exit / sizing / risk / cost 五层它都给了最小实现：

### Entry
- liquidation shock 触发
- 决定 `UP` / `DOWN` 方向
- 挂 `signal price * (1 - 0.30)` 的 maker stink bid

### Exit
- `5m` hard-expiry 到期天然结算
- 未成交则取消
- 剩余时间 `<60s` 不再参与

### Sizing
- Polymarket leg 固定美元仓位
- Hyperliquid leg 固定美元对冲 + 杠杆

### Risk
- daily loss kill switch
- paper trading default
- hedge fill wait / retry

### Cost
- maker-first
- dynamic fee-rate
- taker 高费率背景显式建模

当然，“可直接落地完整策略” 不等于“今天就能实盘上”。
这里最诚实的说法是：
> **这是一条已经把完整策略骨架写出来的 raw alpha 壳，但它还没完成 public-feed migration 与 fill/backtest 审计。**

## 6. 外部数据口径：公开性、更新频率、最小可复现实验
这条主题主要依赖外部实时数据，所以口径必须写清楚。

### 6.1 数据源
1. **Binance Futures liquidation / trade stream**
   - 公开性：公开可得
   - 更新频率：实时 WebSocket
   - 作用：生成 liquidation shock 主信号

2. **Hyperliquid public book / meta / execution path**
   - 公开性：公开可得（行情层）
   - 更新频率：实时或近实时
   - 作用：hedge 定价与路径风险管理

3. **Polymarket Gamma / CLOB orderbook**
   - 公开性：公开可得（行情与市场元数据层）
   - 更新频率：实时 orderbook + market metadata
   - 作用：选择对应 `5m UP/DOWN` 市场、挂 maker stink bid、到期结算

### 6.2 为什么它能映射到 `1m / 3m / 5m / 15m`
- 原始策略壳本身就是 `5m` 硬到期；
- liquidation 触发与 maker 入场判断完全可以在 `1m` 或更细粒度上做；
- `3m` 可作为一个更粗的 fill/反弹确认层；
- `15m` 更适合做上层 veto，例如：高波动时段 / 大盘单边时段是否禁开。

### 6.3 最小可复现实验口径
最小实验其实不复杂：

1. 收集近 `30d~60d` 的 BTC liquidation 事件（公开流）；
2. 对齐对应时刻的 BTC 现货/永续价格路径；
3. 对齐对应 `5m` Polymarket `UP/DOWN` 市场的 mid / bid / ask；
4. 定义事件：
   - `25k~100k USD` 强平
   - LONG liq -> 做 `DOWN`
   - SHORT liq -> 做 `UP`
5. 模拟执行：
   - 在信号时刻的 Polymarket 价格基础上下调 `30%` 挂 maker 单
   - 若 `60s` 内/到期前成交则持有至结算
   - 成交后同步开 Hyperliquid 反向 hedge
6. 输出：
   - fill rate
   - unhedged PnL
   - hedged PnL
   - maker rebate / fee 影响
   - “无 hedge / 40% hedge / 100% hedge” 对比

## 7. 这轮的 first verdict
先给最关键的 5 个判断：

1. **这不是 filter，而是真 raw alpha。**
   方向源头很清楚：`liquidation shock -> short-horizon continuation`。

2. **这不是“prediction market 一定更慢”的泛论。**
   真正可测的是：
   - liquidation 事件先给方向
   - Polymarket 用于 maker-first 执行
   - Hyperliquid 负责 hedge

3. **它是完整策略壳，不只是信号片段。**
   这点比很多 repo 强，因为它连 kill switch 和 fee handling 都考虑到了。

4. **它最大的工程缺口不是想法，而是 feed migration 与 fill simulation。**
   README 也承认 liquidation feed 从 MoonDev 迁到 Binance + Hyperliquid public streams “pending”。

5. **它更像 production candidate，而不是解释型材料。**
   不是说它已经验证过线，而是：
   > 这份材料已经足够让我们直接开始做最小回放，而不是先写半天框架文档。

## 8. 这条 alpha 应该怎么 desk 化
如果把它改写成更适合我们 desk 的壳，我会这样拆：

### 8.1 Entry
- 主时钟：`1m`
- 触发：`BTC liquidation shock`
- 方向：
  - `LONG liq -> buy DOWN`
  - `SHORT liq -> buy UP`
- 执行：
  - 不追 Polymarket ask
  - 用 `30%` pullback 做 maker stink bid

### 8.2 Exit
先测三种：
1. repo 原始版：持有到 `5m` 结算
2. 若 Hyperliquid hedge 已经覆盖掉主要路径风险，则允许 Polymarket 腿持有到期
3. 若 `BTC` 在事件后 `1~2m` 迅速反向收回超过阈值，可提前平 hedge/取消后续挂单

### 8.3 Sizing
先不要盲信 repo 固定值，建议直接做三组：
- `5 / 3`（源码默认）
- `15 / 10`（README 口径）
- 波动标准化 notional

### 8.4 Risk
至少补：
- 单市场日内最大连亏次数
- 同时挂单上限
- 同分钟重复 liquidation 去重
- 大波动时段禁开（例如宏观数据前后）

### 8.5 Cost
这里的关键不是“手续费多少”一句话，而是：
- maker fill 概率
- partial fill
- time priority
- Polymarket 最小 tick / 最小 size
- Hyperliquid hedge 的冲击成本

prediction market 这种壳，**fill assumption 比方向预测还重要**。

## 9. 为什么它和已有 digest 不重复
虽然我们前面已经写过几篇 Polymarket / prediction-market 相关题目，但这篇的核心不同：

- 不是 `stale quote lag-arb`
- 不是 `negation pair parity`
- 不是 `same-event strike surface mispricing`
- 不是 `favorite-side VWAP stretch`

这篇真正独立的 base alpha 是：
> **`liquidation shock` 本身提供方向 edge，而 `Polymarket maker stink bid` 只是执行层最优解之一。**

所以它在研究池里的位置更接近：
- `event-driven directional alpha`
- `hard-expiry execution shell`
- `prediction market as execution venue`

而不是又一篇 prediction-market 定价一致性文章。

## 10. 下一步怎么测
优先按下面 6 步走，不要直接实盘：

1. **先做 public-feed 回放，不接私有 API。**
   用 Binance / Hyperliquid 公共流 + Polymarket 历史 orderbook 快照或可得 market replay，先重建事件簇。

2. **先跑纯方向版，再跑 stink-bid 版。**
   先看 liquidation shock 本身有没有 `5m` 方向 edge；
   再看 `30% pullback maker entry` 是否改善 payoff。

3. **把 fill 当第一层研究对象。**
   至少扫：
   - `10% / 20% / 30% / 40%` pullback
   - `30s / 60s / 90s` min-time-left
   - maker-only vs maker-then-cross

4. **hedge 要单独 ablation。**
   对比：
   - 不对冲
   - `40%` notional 反向 hedge
   - `100%` delta hedge

5. **补“事件质量”分层。**
   不是所有 liquidation 都一样，至少分：
   - `25k~50k`
   - `50k~100k`
   - 单边趋势中 vs 横盘中
   - 高波动时段 vs 普通时段

6. **最终只接受成本后结论。**
   这类壳最容易被“maker fill 幻觉”骗到，所以最后必须给：
   - fill-adjusted PnL
   - fee/rebate 后 PnL
   - hedge 后 PnL
   - resolution payout vs path PnL 分解

## 11. 一句话结论
如果只用一句话概括这轮 intake：

> **这份 2026 repo 最值钱的地方，不是“Polymarket bot” 四个字，而是它把一条很少被完整写清的短周期 raw alpha 壳讲透了：`BTC liquidation shock` 给方向，`5m hard-expiry binary` 给 payoff，`maker stink bid` 给成本优势，`Hyperliquid hedge` 给路径控制。**
