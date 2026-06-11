# 别把这份 2025 Deribit repo 只读成“期权偏度可视化工具”：对 short-cycle desk，更该先测的是「near-vs-far risk-reversal term-skew spread」这条 options relative-value raw alpha
- 时间：2026-04-17 19:36 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `websocket_client.py` + `draw_graph_skew.py` + `get_spd_pdf_log.py` + `create_tables.sql`）+ Deribit 公共 options live snapshot sanity check
- 主题类型：raw alpha
- 基础 alpha：同一标的 BTC 的不同到期日，其 OTM call-vs-put 偏度（repo 用 risk reversal / ATM slope 代理）大部分时间共享一个相对平滑的期限结构；当 **近月偏度相对远月异常变陡/变平**，并且四腿组合按当前 bid/ask 计算仍有正的净入场 edge 时，做 `short rich skew leg / long cheap skew leg`，赌 term-skew spread 回归。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给四腿下单、保证金预检与监控壳；参数与平仓规则需补全）
- 主题标签：raw-alpha / options / relative-value / stat-arb / skew / risk-reversal / term-structure / deribit / btc / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 源码 + Deribit 公共 API live probe

## 1. 为什么这轮选它
这轮优先目标不是再补一个解释型 filter，而是补一条 **能独立复现、能直接进实盘组件池的 raw alpha**。

我最后选的是 GitHub 仓库 **chanhyeong28 / SkewnessTrade_Deribit**（2025，repo 最近提交日期 2025-09-25）。这不是论文型材料，而是一个已经把实时监控、四腿组合、保证金预检、Telegram 告警都写出来的 Deribit 期权策略原型。

先把 base alpha 说清楚：

> **它赌的不是 BTC 方向，而是 BTC 期权 surface 上“不同到期日的偏度相对位置”会回到常态。**

这和我们最近几篇 digest 不同：
- 不是 funding / basis carry；
- 不是 perp-vs-future quote gap；
- 也不是 order-book microstructure continuation。

它补的是当前池子里相对少的那类：
**options relative-value / skew term-structure raw alpha。**

## 2. repo 里真正可复用的 alpha 是什么
### 2.1 repo 表面上写的是“skewness strategy”，但交易本体其实很具体
README 说法偏泛：
- 用 **Risk Reversal (RR)** 当 skewness proxy；
- 监控两个不同 expiration 的 skew；
- 若成本为负（即入场即有正 edge），才允许执行。

真正落到代码里，交易本体比 README 更清楚：

1. 选两个 expiration；
2. 每个 expiration 各挑一只 OTM call 与一只 OTM put；
3. 用 call/put 的 bid/ask IV 与 bid/ask price 计算每个到期日的 RR leg；
4. 把 **远月 RR** 和 **近月反向 RR** 组合成一个四腿 spread；
5. 只有当组合后：
   - `latest_rr_spread > 0`（IV 维度正 edge）
   - `latest_rr_spread_price > 0`（价格维度正 edge）
   - `simulate_portfolio` 保证金检查通过
   才真正下单。

这就已经不是“偏度故事”，而是一条很明确的 **四腿 options stat-arb / relative-value alpha**。

### 2.2 base alpha 用人话说
repo 的 base alpha 可以压缩成一句：

> **如果某个时刻近月 put-skew 相对远月贵太多，或远月 skew 相对近月便宜太多，而四腿对敲后依然留有正的 net edge，那么这块 term-skew spread 往往比纯方向更容易向中枢回归。**

换句话说：
- 交易对象不是“买 BTC 还是卖 BTC”；
- 交易对象是 **skew 的期限结构差**；
- 这本质上是 `relative-value / stat-arb / options raw alpha`。

## 3. 源码里最关键的、值得 desk 继承的结构
### 3.1 选腿规则：固定 log-moneyness，不是随便挑两只期权
`update_subscribe()` 里，repo 不是乱选 strike，而是：
- call 取接近 `S * exp(0.1)` 的 OTM call；
- put 取与之大致对称 log-moneyness 的 OTM put；
- 对两个 expiration 都这么做。

所以它在尽量保持：
- 同标的；
- 相近 log-moneyness；
- 不同到期日。

这使得你做的是 **偏度期限差**，不是混入一堆 moneyness 漂移噪声。

### 3.2 信号公式：代码比 README 更实
`risk_manager()` 里写得很直白。

若选择 `SHORT`，组合信号是：
- 远月：`bid_iv_call_far - ask_iv_put_far`
- 近月：`bid_iv_put_near - ask_iv_call_near`
- 两者相加得 `RR_spread`

同时再用 bid/ask price 算一遍 `RR_spread_price`。

也就是说它不是只看 IV，不管实际成交；而是要求：
- **vol edge 为正**
- **price edge 也为正**

这点很关键。很多 options relative-value 研究死在“模型上有 edge，但落到盘口就没 edge”。这个 repo 至少意识到了这件事。

### 3.3 执行壳：保证金预检先于下单
repo 还有三层实盘味很重的结构：

1. `simulate_portfolio()` 先测 projected margin；
2. 只有 `pre_margin_check_long/short == True` 才允许开仓；
3. 下单后还会持续看 `get_account_summary()`，若保证金逼近 maintenance margin，就触发平仓。

这让它不只是一个“信号脚本”，而是已经带有：
- entry
- margin pre-check
- execution toggle
- live monitoring
- forced close

的完整雏形。

## 4. 但 repo 也有明显缺点：不能原样照抄
### 4.1 entry 规则偏粗糙
代码真正用于触发交易的条件其实很朴素：
- `RR_spread > 0`
- `RR_spread_price > 0`

源码虽然还算了 `mean ± 2*std`，但当前版本并没有把这组 band 真正接进 entry 逻辑。

所以 repo 更像是在做：
- **盘口有正 carry/正 edge 就试图吃掉**
而不是严格意义的：
- **spread 偏离历史分布足够远才开仓**

对我们 desk 来说，正确读法是：
> repo 给的是执行母板，不是最终参数答案。

### 4.2 风控和平仓还不完整
当前实现里，真正显式可见的硬风控主要是保证金层面；但：
- 没有成熟的 time-stop；
- 没有明确的 spread reversion exit band；
- 没有更细的 vega / gamma / fill-risk 约束；
- 平仓部分还有明显代码瑕疵（close 某些 put 腿时 instrument type 似乎写成了 `-C`）。

因此它适合做 **raw alpha intake**，不适合直接接生产。

## 5. public live probe：今天的 Deribit snapshot 能不能支持它不是纯故事
我用 Deribit 公共 API 做了一个最小 live probe，口径尽量贴 repo：
- 标的：BTC
- 近月：`24APR26`
- 远月：`29MAY26` 与 `26JUN26`
- 用 `BTC-PERPETUAL` mark 近似 spot，按 repo 规则挑 OTM call / put
- 选到的 strike 均为：`85000C` 与 `70000P`

### 5.1 单腿 RR 当前确实有明显期限差
抓到的 live IV（约 2026-04-17 19:33~19:35 UTC）：

#### `24APR26`
- `85000C`：bid IV ≈ **41.92**，ask IV ≈ **43.34**
- `70000P`：bid IV ≈ **49.95**，ask IV ≈ **51.12**
- 对应 long-RR leg（`-ask_call + bid_put`）≈ **+6.61 vol pts**

#### `29MAY26`
- `85000C`：bid IV ≈ **39.98**，ask IV ≈ **40.43**
- `70000P`：bid IV ≈ **43.73**，ask IV ≈ **44.23**
- long-RR leg ≈ **+3.30 vol pts**

#### `26JUN26`
- `85000C`：bid IV ≈ **40.05**，ask IV ≈ **40.68**
- `70000P`：bid IV ≈ **43.01**，ask IV ≈ **43.71**
- long-RR leg ≈ **+2.33 vol pts**

这说明什么？

> **同样的 OTM pair 下，近月 put-skew 显著比远月更陡。**

所以“近月 vs 远月 skew 有可交易 term spread”这件事，在 live quote 上是能看见的，不是 README 空谈。

### 5.2 按 repo 的四腿组合口径，当前 `SHORT` 方向一度是正 edge
若拿 `24APR26` 对 `26JUN26` 按 repo 的 `SHORT` 公式组合：
- `RR_spread` ≈ **+2.95 vol pts**
- `RR_spread_price` ≈ **+0.0021 BTC**

拿 `24APR26` 对 `29MAY26`：
- `RR_spread` ≈ **+2.36 vol pts**
- `RR_spread_price` ≈ **+0.0001 BTC**

也就是说，在至少这组 live snapshot 里，
repo 设想的那种：
- **IV 上有正 edge**
- **按盘口价格算也没把 edge 全吃掉**

并不是不存在。

对 desk 来说，这已经足够把它从“机制故事”升级成“值得进研究池的 raw alpha 候选”。

## 6. 它和 `1m / 3m / 5m / 15m` 的关系应该怎么理解
别把它误会成“期权到期很慢，所以只能做低频”。

更准确地说：
- **alpha 本体**：skew term-structure relative-value
- **信号刷新**：quote 级 / 秒级都能变
- **研究基准频率**：先用 `1m / 3m / 5m`
- **更稳的持仓观察窗**：`15m` 可做 reversion / decay 检查

也就是：
- `1m`：最适合记 RR spread 的瞬时异常与回补速度；
- `3m/5m`：更接近 desk 默认快频；
- `15m`：判断是不是只是一跳报价噪声，而不是真正 spread pocket。

这条线完全符合 short-cycle desk 的使用方式：
**信号是 options relative-value，执行和风控时钟则可以是 1m~15m。**

## 7. 今天如果把它改写成更适合 desk 的完整策略
### 7.1 Entry
先只做最朴素版本：
1. 选一组 `near expiry` / `far expiry`；
2. 固定 log-moneyness（如 repo 的 ±0.1）；
3. 计算四腿 `RR_spread` 与 `RR_spread_price`；
4. 仅在以下同时满足时进场：
   - `RR_spread > 0`
   - `RR_spread_price > 0`
   - `RR_spread_z >= 2.0` 或高于 rolling `p95`
   - quote size 足够
   - margin pre-check 通过

### 7.2 Exit
任一满足就平：
1. `RR_spread` 回到 `0 ~ 0.5σ`；
2. 固定 time-stop（先试 `5m / 15m / 30m / 60m`）；
3. 一侧腿 fill quality 恶化，剩余 edge 被 spread 吃掉；
4. 组合净 delta / vega 超上限；
5. 到近月剩余 DTE 太短（如 `< 2d`），避免 gamma 爆炸。

### 7.3 Sizing
- 先按最小可成交张数 / quote size 做小额；
- 优先用 **vega-neutral-ish** 而不是名义数量完全相等；
- pair-level notional cap；
- expiry bucket cap；
- 近月 gamma 更高时自动 size-down。

### 7.4 成本与风险
主要风险：
- 四腿 fill risk；
- skew 不是回归，而是事件驱动重定价；
- 近月 gamma 爆炸；
- surface 并非平移，而是 smile 局部扭曲；
- Deribit options 某些 strike 深度不足。

主要成本：
- option bid-ask；
- taker fee / maker fee；
- 多腿成交不同步带来的 slippage；
- 可能的频繁改价 / 撤单成本。

## 8. first verdict
这轮我的结论很明确：

> **这不是 filter，也不是解释层；它是可以独立复现的 options relative-value raw alpha。**

而且它比 repo README 听起来更“可交易”：
- 选腿明确；
- 组合公式明确；
- 保证金预检明确；
- live snapshot 也确实能看到正 edge pocket。

但也要老实：
- repo 的 entry 还太粗；
- risk / exit 还不完整；
- 需要把它从“正 edge 就上”升级成“正 edge + 偏离分布 + 可成交性一起满足”。

所以它当前最合适的定位是：
**高优先级 raw alpha intake，值得做最小实验，但还不是可直接生产化的终版。**

## 9. 下一步怎么测
### 9.1 最小可复现实验
先不要碰复杂 Greeks 回放，第一轮只做这 4 步：
1. 每 `1m` 抓一次 Deribit 两个 expiration 的目标 call/put top-of-book；
2. 复现 repo 的 `RR_spread` / `RR_spread_price`；
3. 记录未来 `1m / 3m / 5m / 15m / 30m` 的 spread 变化；
4. 扣掉保守 fee + slippage 假设，看净 markout 是否仍为正。

### 9.2 必须同时做的三个版本
- **A**：repo 原版 `RR_spread > 0 & RR_spread_price > 0`
- **B**：加入 `z-score / percentile` admission
- **C**：加入 `vega-balance + min quote size + max gamma` 风控壳

先看哪一版在净成本后还活着。

### 9.3 这张表必须出
- hit rate
- avg / median markout
- time-to-half-reversion
- fee-adjusted expectancy
- worst legging loss
- vega / gamma exposure drift

### 9.4 若第一轮成立，再做两步扩展
1. 把固定 strike 改成固定 delta（如 25d RR）——更像标准 skew 交易；
2. 把 BTC 扩到 ETH，但不要默认 BTC 经验会直接复制到 ETH。

## 10. 来源
### Repo
- GitHub: `chanhyeong28 / SkewnessTrade_Deribit`
- Repo URL: https://github.com/chanhyeong28/SkewnessTrade_Deribit
- Readable URL: https://github.com/chanhyeong28/SkewnessTrade_Deribit/blob/main/README.md

### 关键源码
- `websocket_client.py`
- `draw_graph_skew.py`
- `get_spd_pdf_log.py`
- `create_tables.sql`

### Public data probe
- Deribit public API docs: https://docs.deribit.com/
- Instruments endpoint: `public/get_instruments`
- Ticker endpoint: `public/ticker`

## 11. 一句话版结论
如果只用一句话总结这轮 intake：

> **别把它当“偏度可视化脚本”；对 short-cycle desk 更值得先测的是：近月 vs 远月的 RR term-skew spread 在多腿净成交后是否还能稳定回归，这是一条能独立复现的 options relative-value raw alpha。**
