# 别把 Hummingbot 的 `cross_exchange_market_making` 只读成 bot 框架：对 short-cycle desk，更该先测的是「maker-first cross-venue quote gap × taker-hedge profitability buffer」
- 时间：2026-04-07 15:23 UTC
- 类型：GitHub repo source audit（`README.md` + `cross_exchange_market_making_config_map_pydantic.py` + `cross_exchange_market_making.py` + `start.py`）
- 主题类型：raw alpha
- 基础 alpha：同一标的在两个 venue 的可对冲报价错位；只有当 maker 侧挂单被成交后，能在 taker 侧立刻对冲、且扣掉手续费/滑点后仍保留最小利润，才值得挂单。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / relative-value / stat-arb / market-making / cross-venue / maker-first / taker-hedge / execution / cost / 1m / 3m / 5m / 15m
- 证据类型：工程经验

## 1. 这次看了什么
这次主看 **Hummingbot Foundation / `hummingbot/hummingbot`** 里的成熟策略模块 **`cross_exchange_market_making`**。它不是再讲“跨所套利存在”这句空话，而是把一条能直接跑起来的完整骨架写清楚：**maker 侧先挂单赚价差，taker 侧负责立刻对冲，所有报价都先经过 profitability / slippage / balance / volume 几层约束。**

## 2. 核心结论
- 这条策略的 **base alpha 很朴素**：不是猜方向，而是吃 **同一标的跨 venue 的净价差**。只要 maker 报价相对 taker 对冲价还有足够净边际，就可以挂。
- 它最值钱的地方不是“发现 gap”，而是把 gap 明确翻译成 **可执行报价**：源码里 `get_market_making_price(...)` 会围绕 `min_profitability`、对冲侧可成交价、汇率换算与滑点缓冲来反推 maker 应该挂在哪里。
- 它不是裸冲仓位。配置层直接把 **`order_size_taker_volume_factor`、`order_size_taker_balance_factor`、`order_size_portfolio_ratio_limit`** 暴露出来，说明仓位大小先受对冲深度、可用余额和组合上限约束。
- 它也不是“挂了就不管”。源码里有 **`anti_hysteresis_duration`、`adjust_order_enabled`、`active_order_canceling`** 这类控制，核心目的都是减少顶档抖动带来的频繁改价、无效撤单和被 adverse selection 白打。
- 对我们 desk 来说，这更像一条 **完整 raw alpha shell**：entry、hedge、sizing、cost、inventory/balance 约束都已经成形，比只抄“跨所有价差”更接近能上最小实验的状态。

## 3. 为什么和当前项目有关
这条线直接补的是我们最近很多 raw alpha 还缺的那一层：**怎么把“价差存在”变成真实可挂、可吃、可对冲的单子。**
它尤其适合服务这些已积累方向：
- cross-venue same-underlier spread close
- maker spread capture / market making
- carry / basis / pairs 在执行时的 venue routing

一句话核心结论：**跨 venue alpha 真正值钱的不是看见 gap，而是只挂那些“被打到之后还能立刻在另一边锁住净利润”的价。**  
一句话证明方式：**Hummingbot 不是论文回测，而是把 profitability、slippage、余额、深度、撤单节奏全部写进策略参数和执行逻辑里，用工程约束把这个判断落地。**

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / maker-first
- 基础 alpha：same-underlier cross-venue quote gap 的净价差捕获
- regime：优先流动性正常、两边 order book 都够深、连接稳定、费用可预估的时段
- filter / veto：`min_profitability`、对冲侧可成交量、余额约束、滑点缓冲、顶档抖动/改单阈值
- risk / sizing / execution overlay：maker 先挂、fill 后 taker 立刻对冲；仓位受 taker volume / balance / portfolio cap 限制；必要时取消或调整挂单

## 4. 可复刻的最小实验
- 研究假设：当 `maker_ask >= taker_buy_cost * (1 + hurdle)` 或 `maker_bid <= taker_sell_proceeds * (1 - hurdle)` 时，maker-first 挂单在 fill 后做 taker hedge，仍能留下正的净 edge。
- 一个可计算定义：`hurdle = fees + slippage_buffer + min_profitability`；先用 public L1/L2 或 top-of-book 近似 `taker_buy_cost / taker_sell_proceeds`，再把 maker 可挂价反推出来。
- 最小回测切口：`BTCUSDT / ETHUSDT`，两家高流动性 venue，先跑 `1m / 3m` 事件聚合；再把结果汇总成 `5m / 15m` 的「可对冲机会占比 / 净 edge 分布 / fill 后一跳 adverse selection」。
- 最该先看哪 1~2 个指标：**成本后净 edge 是否仍为正**、**fill 后 hedge 成功率 / hedge 延迟下的 adverse selection**。

## 5. 风险与保留意见
- 这条 alpha 对 **延迟、手续费、maker fill 假设** 极敏感；public top-of-book 快检容易高估真实可吃 edge。
- 它天然更适合 `1m / 3m` 甚至 event-time；若硬塞到 `15m`，更适合作为 **venue-routing / execution overlay**，而不是逐根主方向信号。
- Hummingbot 给的是成熟工程壳，不等于你的 venue 组合一定还有肉；是否还能活，最终取决于 **费用、排队位置、撤单限制、对冲腿成交能力**。

## 6. 来源
1. **Hummingbot Foundation.** `hummingbot/hummingbot`.
   - Repo URL: `https://github.com/hummingbot/hummingbot`
   - Repo metadata: GitHub repo，约 `17,995` stars，`2026-04-07` 仍有更新
2. **Strategy config:** `hummingbot/strategy/cross_exchange_market_making/cross_exchange_market_making_config_map_pydantic.py`
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/cross_exchange_market_making/cross_exchange_market_making_config_map_pydantic.py`
3. **Strategy logic:** `hummingbot/strategy/cross_exchange_market_making/cross_exchange_market_making.py`
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/cross_exchange_market_making/cross_exchange_market_making.py`
4. **Start wiring:** `hummingbot/strategy/cross_exchange_market_making/start.py`
   - Readable URL: `https://github.com/hummingbot/hummingbot/blob/master/hummingbot/strategy/cross_exchange_market_making/start.py`
