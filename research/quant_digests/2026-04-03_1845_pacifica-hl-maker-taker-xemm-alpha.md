# 别把这份 Pacifica × Hyperliquid XEMM repo 只读成“做市工程”：对 short-cycle desk，更该先测的是「maker 宽价差挂单 × taker 紧价差秒级对冲」这条完整 relative-value raw alpha
- 时间：2026-04-03 18:45 UTC
- 类型：2025/2026 GitHub repo source audit（GitHub API metadata + `README.md` + `config.json` + `src/strategy/opportunity.rs` + `src/services/order_monitor.rs` + `src/services/hedge.rs` + `src/config.rs`）
- 主题类型：raw alpha
- 基础 alpha：**同一标的在两家 venue 的微观流动性不对称**——当 Pacifica 的盘口更宽、Hyperliquid 的盘口更紧时，在 Pacifica 挂 maker 单吃“宽 spread / 慢流动性”给出的价差，再在成交后立刻去 Hyperliquid 用 taker 对冲，赚的是 **maker venue 价格滞后 + taker venue 价格发现更快** 之间的短暂 gap。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/cross-venue/xemm/maker-taker/liquidity-asymmetry/microstructure/hyperliquid/pacifica/orderbook/hedge/latency/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：repo README + source 规则级证据 + GitHub API metadata

## 1. 先把 base alpha 说清楚
一句话：

> **这不是“做市系统介绍”，也不是单纯执行优化；它的 alpha 本体就是：在流动性差的 venue 挂单、在流动性好的 venue 对冲，吃同标的跨 venue 的 maker-taker 微观价差。**

翻成人话：
- 同样是 `SOL` / `ETH` / `BTC` 这类币，**Pacifica 的盘口有时更宽、Hyperliquid 的盘口更紧**；
- 如果 Hyperliquid 现在能卖到 `bid_HL`，那我们就能反推：Pacifica 上最多该挂多低的买价，才会在考虑 maker fee、taker fee 之后仍然赚钱；
- 反过来，如果 Hyperliquid 现在能买到 `ask_HL`，那我们就能反推：Pacifica 上至少该挂多高的卖价；
- 一旦 Pacifica 的挂单被动成交，马上在 Hyperliquid 反向吃单锁住价差。

也就是：

> **alpha 不是“猜方向”，而是“同一标的在两个 venue 的流动性质量不同步”。**

这条线为什么值得进当前素材池：
1. **它是完整 raw alpha，不是 filter / gate / overlay。**
2. **entry / hedge / cancel / sizing / cost 全都有。**
3. **它补的是 desk 目前相对少的一类：maker-taker 微观结构 relative-value。**
4. **虽然频率比 5m/15m 更快，但完全能作为 `1m / 3m` 高频补充 sleeve，也能反向服务更慢策略的 execution / venue-routing 研究。**

## 2. 这次看的主材料是什么
### 2.1 主 repo
- **Author / Repo owner**：`djienne`
- **Year**：2025 创建，2026 持续更新
- **Title / Repo**：*XEMM Rust - Cross-Exchange Market Making Bot on Pacifica (Maker) and Hyperliquid (Taker)*
- **Venue**：GitHub repository
- **DOI**：无
- **Readable URL**：<https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID>
- **Repo URL**：<https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID>
- **GitHub metadata**：created `2025-11-11`；pushed `2026-01-05`；stars `12`

### 2.2 repo 内附的二级材料
- **Author**：Hummingbot Foundation（repo 内附文档快照）
- **Year**：文档年份未明；按仓库快照使用
- **Title**：*Cross-Exchange Market Making (XEMM) - Hummingbot*
- **Venue**：documentation snapshot bundled in repo
- **DOI**：无
- **Readable URL**：<https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/blob/master/docs/Cross-Exchange%20Market%20Making%20(XEMM)%20-%20Hummingbot.html>
- **Repo URL**：同上主 repo

### 2.3 这次实际核对了哪些 source
- `README.md`
- `config.json`
- `src/strategy/opportunity.rs`
- `src/services/order_monitor.rs`
- `src/services/hedge.rs`
- `src/config.rs`

## 3. 这份 repo 真正给了什么完整策略骨架
### 3.1 Entry：价差是否足够厚
repo 最关键的一段，不在 UI，而在 `src/strategy/opportunity.rs`。

它把机会写成两条非常明确的公式。

#### 买 Pacifica、卖 Hyperliquid
如果 Pacifica 上挂买单，成交后去 Hyperliquid 卖出，那么可接受的 Pacifica 买价上限是：

`buy_limit_price = (HL_bid * (1 - taker_fee)) / (1 + maker_fee + target_profit)`

然后：
- 向下按 Pacifica tick size 取整；
- 用 `notional_usd / buy_limit_rounded` 算下单数量；
- 再算实际 profit bps。

#### 卖 Pacifica、买 Hyperliquid
如果 Pacifica 上挂卖单，成交后去 Hyperliquid 买回，那么可接受的 Pacifica 卖价下限是：

`sell_limit_price = (HL_ask * (1 + taker_fee)) / (1 - maker_fee - target_profit)`

然后：
- 向上按 tick size 取整；
- 算 size；
- 再算实际 profit bps。

这说明 alpha 本体已经非常清晰：

> **只要 maker venue 给你的挂单价，和 taker venue 此刻可对冲价之间，还留得下“手续费 + 目标收益 + rounding 后残余利润”，就开仓。**

### 3.2 Cost：repo 没有回避成本，反而把成本放进信号定义里
`config.json` 默认参数直接给了第一版 economics：
- `pacifica_maker_fee_bps = 1.5`
- `hyperliquid_taker_fee_bps = 4.0`
- `profit_rate_bps = 15.0`
- `profit_cancel_threshold_bps = 3.0`
- `order_notional_usd = 20.0`
- `order_refresh_interval_secs = 60`
- `hyperliquid_slippage = 0.05`

这里最值钱的不是参数值本身，而是 repo 的态度：

> **目标收益阈值不是后验 KPI，而是 entry 公式的一部分。**

也就是说，repo 不是“先下单，再祈祷对冲后有利润”；而是：
- 先把 maker fee、taker fee、目标 safety margin 一起算进去；
- 只有净边际还为正，才挂单。

对 short-cycle desk 很重要，因为很多“跨 venue spread”一进实盘就死在两件事上：
1. 只看 mid/mid，不看可成交 bid/ask；
2. 只看理论 spread，不把 fee/slippage/rounding 放进 admission。

这份 repo 至少在规则层先把这两个坑补了。

### 3.3 Exit / cancel：不是挂上就不管
`src/services/order_monitor.rs` 写得也很实在：
- **热路径监控**每 `1ms` 跑一次；
- 只要订单还挂着，就持续重算当前对冲利润；
- 如果距离下单时的 `initial_profit_bps` 偏离超过 `profit_cancel_threshold_bps`（默认 `3bps`），就发起取消；
- 如果订单年龄超过 `order_refresh_interval_secs`（默认 `60s`），也会取消重来。

而 README 还给出整体 task 配置：
- main opportunity loop：`100ms`
- profit monitoring：`25ms`
- REST fill detection backup：`500ms`
- orderbook fallback polling：`2s`

这条线的含义是：

> **挂 maker 单不是被动等死，而是持续盯着“如果现在成交，再去另一边对冲，还赚不赚钱”。**

所以这不是静态套利，更像一个：
- **挂单等待成交** 的 maker alpha，
- 外加一个 **实时利润存活监控** 的 veto 壳。

### 3.4 Hedge：成交后立刻反向锁仓
`src/services/hedge.rs` 把 hedge 流程写得很完整：
1. 收到 fill event；
2. 背景任务先再次取消 Pacifica 其余挂单；
3. 在 Hyperliquid 发反向 market order；
4. 默认优先走 **WebSocket hedge**，失败再 fallback 到 REST；
5. 成交后再拉取 trade history 算真实利润。

README 里强调的是：
- hedge event queue 用 `mpsc`，fill detection 不会被 hedge 阻塞；
- WebSocket-first hedging 为了最小化 latency；
- 如果 WS 失败，自动 fallback REST。

也就是说，repo 给的不是“发现 edge”，而是 **发现 → 挂单 → fill detect → hedge → post-trade verify** 的完整链路。

### 3.5 Fill detection：它不是只靠一种填单检测
README 明写了 **5 层 fill detection**：
1. Pacifica `account_order_updates` WebSocket
2. Pacifica `account_positions` WebSocket
3. REST order polling（`500ms`）
4. REST position monitor（`500ms`）
5. 监控任务里的 safety check

这对研究意义很大。因为 maker-taker alpha 的实盘死亡点，很多时候不在“有没有 edge”，而在：
- fill 了你没及时发现；
- partial fill 检测延迟；
- cancel 与 fill race condition；
- hedge 重复触发或漏触发。

repo 至少说明：

> **作者知道这条 alpha 的最大脆弱点不是公式，而是 fill → hedge 这 100ms~500ms 链条。**

## 4. 为什么这东西和当前 desk 直接相关
先回答那句必须回答的话：

> **它为什么比继续补一篇普通 filter 更值得？因为它本身就是可独立复现、可直接落地的完整 raw alpha。**

而且它补的不是又一篇：
- breakout
- trend gate
- RSI/BB 过滤器

它补的是：
- **relative-value / stat-arb** 方向里的一个微观结构分支；
- **maker-taker cross-venue** 这类此前库里数量还不算多的完整壳；
- 同时还能反过来服务更慢速策略的 **execution veto / venue selection**。

对当前 desk，我会把它归类成：
- **主题类型**：raw alpha
- **风格归属**：relative value / stat-arb / microstructure
- **更适合的运行层级**：`1m / 3m` 高频 sleeve，或 `5m / 15m` 策略的 venue-routing/quote-quality 子模块

换句话说：

> **它不是主打 15m bar-close 的“方向 alpha”，而是主打 quote-event 的“成交质量 alpha”。**

这仍然符合当前 intake 目标，因为用户已经明确允许：只要能快速复现、快速验证、能落到 entry/exit/sizing/risk/cost，就值得进池。

## 5. 这条 alpha 在我们这边该怎么读
### 5.1 不要把它读成“传统搬砖”
真正 low-value 的搬砖，是：
- 两边都 taker；
- 纯拼更低延迟；
- 机会稀少，而且常常抢不过专业队。

repo README 反而明确说：
- 选择 **Pacifica maker / Hyperliquid taker**；
- 理由是 Hyperliquid spread 更紧、流动性更好；
- 比传统 taker-to-taker arbitrage 更容易找到机会。

也就是它打的不是“抢别人已经看见的显性价差”，而是：

> **用自己的被动挂单去制造一个别人不一定拿得到的成交价，再去更深的 venue 对冲。**

这是一条完全不同的经济学。

### 5.2 它更像哪类传统 desk 思路
如果翻译成更熟悉的 desk 语言，它更像：
- maker-first spread capture
- queue-aware cross-venue hedge
- liquidity asymmetry arbitrage
- venue-quality relative value

也可以理解成：

> **你不是在赌涨跌，而是在赌“差 venue 给你的成交价，会比好 venue 当前的可对冲价更慷慨”。**

### 5.3 它真正的脆弱点是什么
repo 写得越完整，脆弱点也越容易看见：
1. **Pacifica 的挂单不一定成交**：理论 edge 很厚，但没 fill 就没有 alpha。
2. **fill quality 不确定**：如果你只吃到 partial fill，成本结构会变。
3. **hedge latency 是 PnL 核心变量**：尤其在币价抖动快时，几十到几百毫秒都可能吃掉 3~10bps。
4. **maker queue position 不可见时，paper/live 差异会很大**。
5. **Pacifica venue 风险**：容量、深度、异常撮合、撤单确认速度，都可能限制放大。

所以对这类策略要老实：

> **它的难点不是“信号不够聪明”，而是 fill probability 与 hedge latency。**

## 6. 对 `1m / 3m / 5m / 15m` 的关系该怎么写
必须诚实写：

### 6.1 直接适配层
- **最自然的是 sub-second / second 级**，因为 repo 本身是 orderbook event 驱动。
- 如果强行映射到 bar frequency，**`1m / 3m` 比 `5m / 15m` 更自然**。

### 6.2 对 `5m / 15m` 的价值不是没有，但角色不同
它可以服务两类更慢策略：
1. **execution/venue-routing overlay**：当某币在 Pacifica 相对 Hyperliquid 的 quote edge occupancy 很高时，说明该时段 maker side 更友好；
2. **shared microstructure gate**：当跨 venue spread-close 很差、hedge latency proxy 恶化时，减少同币其它快策略的下单积极度。

所以不要硬说“这就是 15m 主信号”。更准确的说法是：

> **它本身是一条更快的 raw alpha；同时还能给 1m/3m/5m/15m 体系提供 execution-quality 侧信息。**

## 7. 最小可复现实验：先怎么测
这部分最关键。

### 实验 A：只测“理论 edge 是否常出现”
**目标**：先不碰 fill probability，只看 public book 上这条 maker-taker edge 是否存在、多久存在、厚度多大。

#### 数据源
- **Pacifica public orderbook WebSocket / REST top-of-book**：公开可得，tick 级更新
- **Hyperliquid public L2 / top-of-book**：公开可得，tick 级更新
- 标的先做：`SOL`, `ETH`, `BTC`

#### 口径
每 `200ms ~ 1s` 采样一次，计算双边 edge：
- 买 Pacifica / 卖 Hyperliquid：
  `edge_buy_bps = ((HL_bid*(1-taker_fee) - PAC_ask*(1+maker_fee)) / (PAC_ask*(1+maker_fee))) * 10000`
- 卖 Pacifica / 买 Hyperliquid：
  `edge_sell_bps = ((PAC_bid*(1-maker_fee) - HL_ask*(1+taker_fee)) / (HL_ask*(1+taker_fee))) * 10000`

#### 先看 4 个统计量
1. `edge > 0` 的占比
2. `edge > 15bps` 的占比
3. 连续存活时长分布（edge spell duration）
4. 各币种 / 各 UTC 时段的 edge occupancy

#### 判定标准
- 如果 `edge > 15bps` 只是偶发单点尖刺，且持续时间通常 `< 1s`，那这条线更偏“展示型”；
- 如果能观察到稳定的 `2s~20s` 存活段，才值得继续测 fill 模型。

### 实验 B：做最保守的 maker fill 近似
**目标**：回答“理论 edge 不等于可成交 edge”。

#### 最简 fill 近似
对 Pacifica 挂单，只有满足以下任一条件才算 fill：
- 后续 best ask/bid 触碰我们的挂单价并持续 `N` 个采样点；
- 或后续 trade print 穿过挂单价；
- 或盘口量被吃掉超过某阈值。

然后在 fill 时刻：
- 用 Hyperliquid 当时 best bid/ask，外加 `4bps taker fee + slippage haircut` 去模拟 hedge；
- 输出净收益分布。

#### 第一版参数
- target edge：`15bps`
- cancel threshold：`3bps`
- max order age：`60s`
- slippage stress：`0 / 2 / 5 / 10bps`
- sampling：`200ms` 与 `1s` 各一版

### 实验 C：给更慢策略做 shared overlay
如果实验 A/B 发现：
- 某些时段跨 venue maker-taker edge 很常见；
- 某些时段几乎没有；

那第三步不是急着 live，而是先做一个低成本共享因子：
- `xemm_edge_occupancy_1m`
- `xemm_edge_p95_bps_3m`
- `xemm_spread_survival_5m`

拿它去看：
- 是否能筛掉 execution 特别差的 1m/3m momentum 交易；
- 是否能帮助 same-underlier cross-venue spread-close alpha 只在“好做”的时段开仓。

## 8. 我会怎么给这条材料下研究结论
### 8.1 结论
> **这份 repo 值得 intake 的，不是“Rust 工程很完整”，而是它把一条可独立落地的 maker-taker relative-value raw alpha 写到了规则级。**

尤其值得拿走的不是 UI、部署脚本、AWS Tokyo 建议，而是这四件事：
1. **entry 公式把 fee + target profit 写死进 admission；**
2. **order monitor 明确盯利润存活，不是傻等 fill；**
3. **hedge 流程是 fill-triggered，而不是周期轮询；**
4. **fill detection 用多层冗余，承认 maker 策略真正难点在 fill/hedge 链条。**

### 8.2 在当前优先级里的位置
我会把它放进：
- **raw alpha 候选池：高优先级**
- 但不是“立刻实盘”，而是“立刻做 public-data viability + fill approximation”。

原因很简单：
- 它是完整策略；
- base alpha 说得清；
- 和当前 desk 的 raw alpha 扩充方向直接相关；
- 但 live feasibility 对 venue/latency/queue 很敏感，必须先用最保守方法验证。

## 9. 下一步怎么测（可直接开工）
### 9.1 今天就能做的最小实验
1. 拉 Pacifica + Hyperliquid 同步 top-of-book 流；
2. 对 `SOL / ETH / BTC` 跑 24h edge occupancy；
3. 先不建 fill 模型，只画：
   - `edge > 0bps`
   - `edge > 5bps`
   - `edge > 10bps`
   - `edge > 15bps`
   的占比和持续时间；
4. 按 UTC 小时切 bucket，找最值得做的 session。

### 9.2 第二步
在实验 A 的最好币种上，加最保守 fill proxy：
- 只允许“价格触碰并持续 / trade print 穿过 / queue 消耗”三类 fill；
- hedge 端强制加 `2~10bps` slippage stress；
- 输出净 edge 分布、胜率、平均 holding time、取消率。

### 9.3 第三步
如果 B 仍然有正的净收益，再决定它走哪条分叉：
- **分叉 1**：当独立 raw alpha，继续做 live paper trading；
- **分叉 2**：降级成 shared execution-quality overlay，服务现有 `1m / 3m / 5m / 15m` 其它快策略。

## 10. 参考资料
1. **djienne. (2025/2026). _XEMM Rust - Cross-Exchange Market Making Bot on Pacifica (Maker) and Hyperliquid (Taker)_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID>  
   - Repo URL: <https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID>
2. **Repo source files used in this digest**  
   - README: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/README.md>  
   - Config: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/config.json>  
   - Opportunity evaluator: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/src/strategy/opportunity.rs>  
   - Order monitor: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/src/services/order_monitor.rs>  
   - Hedge service: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/src/services/hedge.rs>  
   - Config schema/defaults: <https://raw.githubusercontent.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/master/src/config.rs>
3. **Hummingbot Foundation. _Cross-Exchange Market Making (XEMM)_ (documentation snapshot bundled in repo).**  
   - Venue: Documentation snapshot  
   - DOI: N/A  
   - Readable URL: <https://github.com/djienne/XEMM_CROSS_EXCHANGE_MARKET_MAKING_PACIFICA_HYPERLIQUID/blob/master/docs/Cross-Exchange%20Market%20Making%20(XEMM)%20-%20Hummingbot.html>
