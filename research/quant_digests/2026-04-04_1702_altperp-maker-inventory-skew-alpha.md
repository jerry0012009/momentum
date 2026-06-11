# 别把这份 2026 新 repo 只读成夸张收益截图：对 short-cycle desk，更该先测的是「mid-liquidity alt-perp 宽价差 maker × inventory skew / trend-veto」这条完整 raw alpha
- 时间：2026-04-04 17:02 UTC
- 类型：2026 GitHub 新 repo source audit（`README.md` + `strategies/market-making/mm_engine.py` + `mm_futures_backtest.py` + `mm_futures_scanner.py` + `mm_pair_scanner.py`）+ 经典 inventory-based market making 文献 grounding
- 主题类型：raw alpha
- 基础 alpha：**在中等成交、非主流 USDT perpetual 上，持续挂双边被动单，吃的是“可覆盖 maker 成本后的稳定宽价差”；再用 inventory skew、depth cap、trend/vol veto 去压 adverse selection。换句话说，alpha 本体不是方向判断，而是“宽价差流动性供给”的重复 spread capture。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/maker/market-making/spread-capture/inventory-skew/liquidity-provision/altcoin-perpetual/binance-futures/orderbook-depth/adverse-selection/trend-veto/volatility-circuit-breaker/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：开源代码仓 + 经典 market making 论文 grounding

## 1. 这次为什么选它
这轮我不想继续在 pairs / spread forecast / basis shell 里内循环，原因很简单：

1. **最近 intake 已经连续补了不少 pairs / relative-value / basis 题**；
2. 但从 `docs/MAINLINE1_STRATEGY_FACTOR_MAP.md`、`docs/FACTOR_BACKLOG.md`、`docs/LEARNING_TRACK.md` 这轮对照看，**显式写成“maker raw alpha shell”的条目并不多**；
3. 对 short-cycle crypto desk 来说，**流动性供给本身就是一类独立 raw alpha**，不该永远被当成 execution 附件。

这份 repo 虽然很新、而且 README 收益明显偏理想化，但它有一个优点：

> **它不是只给一个抽象想法，而是把 universe、entry、quote shape、sizing、inventory control、risk kill-switch、pair scanner 全写成了完整壳。**

这正符合这轮优先级里最值钱的那一档：
**可独立复现、可直接落地成完整策略的 raw alpha 候选。**

## 2. 这条东西的 base alpha 到底是什么
先把最关键的一句讲清楚：

> **base alpha = 在非主流 alt perpetual 上，稳定存在的、能覆盖 maker 费和保守滑点的 bid-ask spread。**

更具体一点，这条壳不是在赌：
- breakout；
- retest；
- funding 单边；
- 某个趋势方向。

它赌的是：
1. 某些币对的**天然盘口价差够宽**；
2. 这些币对的**订单簿深度还没差到完全不能挂单**；
3. 只要把 quote 放在合适距离，且在波动/趋势恶化时收手，
4. 就能重复赚到**双边被动成交的 spread capture**。

所以这不是 filter，也不是 overlay 伪装货；
它本身就是一条**maker/liquidity-provision raw alpha**。

## 3. 这份 repo 里真正值钱的硬信息

### 3.1 来源与版本
- **Repo**：`monkeyjack123/quant-research-portfolio`
- GitHub：<https://github.com/monkeyjack123/quant-research-portfolio>
- 最近提交：`30a15a0eff8c5ae8730a04b924a7fdeb8c539641`
- 提交时间：`2026-03-29T23:14:53-05:00`
- 当前仓库只有 1 个初始提交，说明它**非常新**，也说明结论更该按“研究假设壳”来读，而不是成熟 production track record。

### 3.2 它定义的 universe 其实很像一条可执行的 admission layer
`mm_futures_scanner.py` 先做了一层非常清楚的 pair admission：

- Binance **USDT perpetual**
- 排除 majors（`BTC / ETH / BNB / SOL / XRP / DOGE / ADA ...`）
- `24h quote volume` 在 **`100K ~ 20M` USDT**
- 实时盘口 `spread_pct > 0.04%`
- 打分公式：

```text
score = net_spread × sqrt(volume) × (1 - volatility_penalty)
```

其中：
- `net_spread = spread_pct - 0.04%`（round-trip maker fee）
- `volatility_penalty = max(0, (|24h priceChange%| - 10) / 10)`

翻成人话就是：

> **先挑“价差够宽、量别太小、但也别大到已经被专业 MM 碾平、同时 24h 方向别太疯”的标的。**

这不是泛泛筛币，而是一条能直接复现的 admission 规则。

### 3.3 live engine 的核心参数，已经足够拼出完整策略
`mm_engine.py` 里的默认 futures maker 壳，关键参数是：

- 默认交易对：`1000SATS / ALICE / IO / ACT / DENT`
- 初始 capital：`200 USDT`
- leverage：`3x`
- `capital_per_pair_pct = 20%`
- `base_spread_pct = 0.40%`
- `min_spread_pct = 0.08%`
- `order_size_pct = 5%`
- `max_position_pct = 15%`
- `n_layers = 5`
- `layer_step_pct = 0.02%`
- 只在价格偏移 `> 0.05%` 时重挂单
- 冰山单阈值：`50 USDT`
- top-5 深度 sizing cap：`depth_max_pct = 2%`
- vol breaker：`当前波动 > 2 × rolling mean` 时暂停
- trend veto：`30 ticks` 累计方向移动 `> 0.3%` 时，把下单规模缩到 `30%` 左右
- portfolio DD：`-5%` 减半，`-10%` 全清

这说明它不是“只有 alpha 没有壳”，而是天然已经拆成：
- **entry**：双边挂单入场
- **exit**：被动对手成交 / 风控暂停 / 组合清算
- **sizing**：capital slice + depth cap + trend scale
- **risk**：inventory cap + vol pause + trend scale + DD kill-switch
- **cost**：maker fee floor 明确写在 scanner / backtest 假设里

### 3.4 inventory skew 的想法是对的，而且跟经典 MM 文献一致
这份 repo 最值得保留的，不是收益截图，而是它对**库存风险**的处理方向：

- 持仓偏多时，把 bid / ask **整体下移**，鼓励卖出减仓；
- 持仓偏空时，把 bid / ask **整体上移**，鼓励买回减仓；
- 同方向仓位越满，同方向继续加仓的 quote size 越小；
- 在 adverse move + 高波动同时出现时，反向减仓单会被放大。

这跟 Avellaneda–Stoikov 那条经典逻辑是一致的：

> **做市不是只盯 spread，而是要把 inventory risk 价格化。**

对 short-cycle desk 很重要的一点是：
这类 inventory skew 完全可以迁移到 `1m / 3m / 5m / 15m` crypto 执行层，不依赖私有数据。

## 4. repo 自己声称的结果，哪些能看，哪些不能信
README 里给了很多漂亮数字，我只挑最有信息量的几条：

### 4.1 可作为“候选吸引力”参考的数字
README 给的 futures backtest（`Mar 2025 – Mar 2026`, `$200`, `1x`）里：

- `1000SATS`: **+609%**, DD `-3.67%`, `15,826` trades, spread `0.526%`
- `ALICE`: **+467%**, DD `-3.60%`, `15,876` trades, spread `0.488%`
- `IO`: **+426%**, DD `-1.86%`, `16,082` trades, spread `0.457%`
- `ACT`: **+402%**, DD `-3.97%`, `15,816` trades, spread `0.453%`
- `DENT`: **+395%**, DD `-5.62%`, `15,933` trades, spread `0.410%`

这组数最有用的地方不在收益本身，而在于它告诉我们：

> **作者真正想做的是“平均价差 41–53 bps”的 alt-perp maker 书，而不是 BTC/ETH 那种被专业做市挤平的市场。**

### 4.2 但这些结果明显不能直接当已验证结论
因为 README 还给了 IO 的 full-history leverage analysis：

- `1x`: `+3,002%`, DD `-1.87%`, Sharpe `27.64`
- `3x`: `+3.17M%`, DD `-5.49%`, Sharpe `27.93`
- `5x`: `+25.6B%`, DD `-8.96%`, Sharpe `27.68`

这种结果本身就在提醒我们：

> **repo 的 backtest 更像“概念验证 + optimistic simulator”，而不是可直接采信的收益证明。**

也正因此，这轮 digest 的价值不在于“抄收益”，而在于把其中**可迁移的 raw alpha 结构**抽出来。

## 5. 这份源码最重要的 source-audit 发现

### 5.1 live engine 比 backtest 更像真东西
`mm_engine.py` 至少接了：
- Binance Futures WebSocket depth stream（`@depth5@100ms`）
- top-5 book depth sizing cap
- layered quoting
- inventory skew
- vol breaker
- trend scale-down
- price drift threshold 才更新订单

也就是说，**真正值钱的是 live shell**。

### 5.2 backtest 用的是 1h kline，不是 order book replay
`mm_futures_backtest.py` 的核心假设是：

- 每根 bar 的 `mid = (high + low) / 2`
- bid 放在 `mid - spread/2`
- ask 放在 `mid + spread/2`
- 如果 `bar low <= bid` 就算买单成交
- 如果 `bar high >= ask` 就算卖单成交

这就带来几个明显乐观项：

1. **没有 queue position**
   - 你挂到了那个价，不等于你真排到了量。
2. **可能同一根 bar 双边都成交**
   - 这在粗粒度 K 线上容易高估回转效率。
3. **没有真实盘口路径**
   - bar 的 high/low 触达，并不代表你的 passive quote 真有可成交对手盘。
4. **没有 cancel/replace latency**
   - 而 live maker 最怕的恰恰就是 stale quote。

所以：

> **repo 的 alpha 想法可以收，但回测收益绝不能直接抄。**

### 5.3 docstring 写了 funding，但代码里并没真正结算 funding
`mm_futures_backtest.py` 顶部说明写了：

- maker fee `0.02%`
- funding rate every 8 hours

但实际回测逻辑里只看到了：
- fee 扣减
- inventory / capital / equity curve

**没有真正 funding cashflow 的结算实现。**

这意味着：
- 如果 inventory 在单边累积，真实收益会被 funding 影响；
- 尤其在 alt-perp 上，funding 有时不是小数点后噪音。

### 5.4 alpha 本体没问题，但 README 收益大概率混进了 fill-model 幻觉
这也是我这轮最想写清楚的一点：

> **“宽价差 alt-perp maker” 这个 base alpha 本身是成立的；问题不在 alpha 类型，而在 repo 回测把它模拟得太顺了。**

也就是说：
- **题目值得收**；
- **收益不值得抄**；
- **该复现的是壳，不是截图。**

## 6. 它和 `1m / 3m / 5m / 15m` 的关系
这条东西跟 short-cycle desk 的兼容性其实很强：

### `15m`
适合做 **symbol routing / admission refresh**：
- 哪些币今天还值得做；
- 哪些币已从“宽价差可吃”变成“方向太毒不能碰”。

### `5m`
适合做 **health layer / state gate**：
- 最近 realized vol 是否过高；
- spread 是否开始塌缩；
- inventory 是否需要强制去风险。

### `1m / 3m`
适合做 **真正执行层**：
- quote placement
- reprice
- layered order management
- stale quote cancel

翻成人话：

> **这不是只能在小时级回测里好看的东西；相反，它天然更适合快频执行，只是 admission 和风控最好稍慢一层。**

## 7. 最小可复现实验：怎么把它变成 desk 可跑的第一版

### 7.1 数据源
全部公开可得：
- Binance USDⓈ-M `bookTicker` / depth stream
- Binance USDⓈ-M `aggTrades` 或 recent trades
- Binance USDⓈ-M klines（做状态聚合）
- Binance funding rate history

### 7.2 第一版不要直接照抄 repo 的 5 层+3x
我建议先做一个更克制的版本：

#### Universe / admission（`15m` 刷新）
保留 repo 的核心筛选：
- USDT perpetual
- 排除 majors
- 24h volume `100K ~ 20M`
- live gross spread 要明显大于 fee floor
- 再加一个我们自己的条件：
  - `top-5 depth / target order size >= 20x`

#### Entry（`1m/3m` 执行）
- 双边挂 maker quote
- 先只上 **2–3 层**，不要一开始就 5 层
- 初始 quote 宽度：
  - `max(live spread × 0.8, fee_floor + slippage_buffer + stale_quote_buffer)`

#### Exit / inventory reduction
- 单边 inventory 超过 pair capital 的 `5%~8%` 就开始 aggressive skew
- 超过 `10%` 就只挂减仓边，不再补同方向仓
- 若 `N` 分钟内 inventory 无法回到安全区，直接 taker flatten 一部分

#### Sizing
- 第一版固定美元 notional
- 单笔 quote size 不超过：
  - `top-5 depth` 的 `0.5%~1.0%`
  - pair allocated capital 的 `2%~3%`

#### Risk / veto
- `1m realized vol > 2 × 30m median` → pause
- `30~60 ticks` 单向移动超阈值 → scale down
- `spread collapse` 到 fee floor 附近 → 停止做这个币
- funding 异常跳变 → 只保留减仓边

#### Cost
必须显式记：
- maker fee
- occasional taker flatten fee
- quote drift 带来的 adverse selection
- 未成交导致的 inventory carry / funding drag

### 7.3 第一版最该看的不是 PnL，而是这四个 execution KPI
1. **双边成交占比**：有多少 inventory 能靠被动对手盘自然回转？
2. **单位库存的 adverse selection**：持仓后 1m/3m markout 是否持续为负？
3. **spread capture / fee**：净 spread 收益是否稳定覆盖 maker+taker+funding
4. **stale quote hit rate**：被趋势扫掉的比例高不高？

如果这四个数站不住，收益曲线再好看都没意义。

## 8. 下一步怎么测

### Step 1：先做 `15m admission + 1m execution` 的简化壳
只保留：
- spread admission
- depth cap
- inventory skew
- vol pause

先别上冰山、先别上 5 层、先别上 3x leverage。

### Step 2：做真实 markout 统计，而不是只看 bar 内是否触价
至少统计：
- fill 后 `30s / 60s / 180s` markout
- long inventory vs short inventory 的 markout 非对称
- maker fill 之后的 spread survival time

### Step 3：单独测 trend veto 的增量价值
做两版对照：
- A：只有 spread + inventory skew
- B：A + `30 ticks > 0.3%` 的 trend scale-down

看它到底是：
- 真减少 adverse selection；
- 还是只是把成交量砍掉。

### Step 4：补 funding 到 inventory carry 里
尤其 alt-perp 容易出现：
- 本来 spread capture 是正的；
- 但 inventory 偏一边太久，被 funding 吃回去。

这一步不补，策略评估会偏乐观。

### Step 5：再决定是否扩到 shared gate
如果 raw maker alpha 先站住，再考虑把这几类状态输出给别的策略：
- `spread regime`
- `depth regime`
- `toxicity / trend regime`

也就是把它进一步变成：
- maker 主策略；
- 以及别的 breakout / MR / pairs 策略的 execution veto。

## 9. 我对这条题的结论
这份 repo **不是**“可直接信的高收益做市系统”；
但它**是**一条值得放进研究池的完整 raw alpha shell。

我给它的定位是：

> **“mid-liquidity alt-perp 宽价差 maker × inventory-skewed liquidity provision” 这条 short-cycle raw alpha。**

它之所以值得收，不是因为 README 写了几百上千个点的收益，
而是因为它把真正重要的几件事写全了：
- universe admission
- quote width
- inventory control
- depth-aware sizing
- vol/trend veto
- portfolio kill-switch

对我们当前 desk 来说，它的价值在于：

1. **base alpha 清楚**：赚的是宽价差流动性供给，而不是方向；
2. **可独立复现**：公开 orderbook / trade / funding 数据足够；
3. **可直接落地完整策略**：entry/exit/sizing/risk/cost 都能拆；
4. **和 `1m/3m/5m/15m` 节奏天然兼容**：15m 选币，1m/3m 执行，5m 风控；
5. **能扩成 shared gate**：做市状态也能反哺别的 alpha 执行层。

如果只给一句落地建议，那就是：

> **不要复刻它的收益；先复刻它的“admission + inventory + veto”骨架。**

## 10. 参考来源
1. **monkeyjack123 (2026). _quant-research-portfolio_. GitHub.**  
   Repo：<https://github.com/monkeyjack123/quant-research-portfolio>
2. **Market making engine source**  
   <https://github.com/monkeyjack123/quant-research-portfolio/blob/main/strategies/market-making/mm_engine.py>
3. **Futures backtest source**  
   <https://github.com/monkeyjack123/quant-research-portfolio/blob/main/strategies/market-making/mm_futures_backtest.py>
4. **Futures pair scanner source**  
   <https://github.com/monkeyjack123/quant-research-portfolio/blob/main/strategies/market-making/mm_futures_scanner.py>
5. **Spot pair scanner source**  
   <https://github.com/monkeyjack123/quant-research-portfolio/blob/main/strategies/market-making/mm_pair_scanner.py>
6. **Avellaneda, M., & Stoikov, S. (2008). _High-frequency trading in a limit order book_. Quantitative Finance, 8(3), 217–224.**  
   DOI：<https://doi.org/10.1080/14697680701381228>

## 11. 文件与页面
- Digest：`research/quant_digests/2026-04-04_1702_altperp-maker-inventory-skew-alpha.md`
- 页面 URL（发布后）：`https://jp.jerrypsy.top/momentum/reading/quant_digests/2026-04-04_1702_altperp-maker-inventory-skew-alpha.html`
