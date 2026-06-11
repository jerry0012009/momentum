# 别把这份 Drift↔Hyperliquid 套利 bot 只读成“双所价差扫描”：更该先测的是「same-asset perp-perp basis pocket + rollback execution」完整 raw alpha

- 时间：2026-03-28 09:03 UTC
- 类型：raw alpha
- 主题标签：raw-alpha/relative-value/stat-arb/cross-exchange/perpetual/basis/drift/hyperliquid/execution/cost/slippage/maker-pocket/1m/3m/5m/15m/repo/live-snapshot
- 证据类型：2025 GitHub 新仓库 + source audit + Drift/Hyperliquid 公共 order-book live snapshot
- 主题类型：raw alpha
- 基础 alpha：同一标的在 Drift 与 Hyperliquid 两个永续 venue 之间出现可交易净价差时，做 `short rich venue / long cheap venue`，等待 cross-venue basis 回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但 taker-only 版本当前大概率不过成本，必须把 maker / pocket / rollback 一起设计）

## 1. 这次看了什么

这次主看的是 **Alex Bitok (2025)** 的 GitHub 仓库 **Drift ↔ Hyperliquid Arbitrage Bot**。它不是那种只给一个“套利机会监控面板”的半成品，而是把两条可独立运行的策略都写出来了：

- **Basis arbitrage**：同一标的在两个 venue 的永续价格出现净价差时，做跨所 market-neutral 收敛；
- **Funding arbitrage**：同一标的在两个 venue 的 funding rate 出现差异时，做 long-low-funding / short-high-funding。

我这轮只把它的 **basis branch** 拎出来，因为这条线的 **base alpha 很清楚**：

> **同一资产、同一合约类型、不同 venue 的 perp-perp basis 会在短时间内向可成交的公允区间回归。**

这比继续补一篇泛 trend/filter 更值得当前 desk 收进素材池，原因很直接：

- `docs/LEARNING_TRACK.md`、`docs/FACTOR_BACKLOG.md` 里，当前主线已经有不少 trend / breakout / pullback 组件；
- 但 **relative value / stat-arb / cross-venue** 这类可完整落地的 raw alpha，仍然值得持续补货；
- 这份 repo 直接把 `entry / cost / slippage / rollback / timeout / safe_mode` 都写进去了，天然适合做 **admission check**。

## 2. 对 desk 真正有用的，不是“扫描价差”，而是把它改写成 pocket 型 raw alpha

repo 最值钱的地方，不是“发现 Drift 和 Hyperliquid 有价差”这句话，而是它已经把**完整策略骨架**搭好了：

- 配置里直接给了：`amount=1.0`、`max_slippage_bps=10`、`min_profit_usd=1.0`、`poll_interval_sec=1`；
- 成本预算写得很明白：`fees.drift=8bps`、`fees.hyperliquid=7bps`；
- 执行层不是单腿乱打，而是 `ExecutionEngine` 协调双腿下单、等待成交、失败回滚；
- 还有 `safe_mode`、`order_submit_sec=10`、`order_cancel_sec=5` 这些实盘保护；
- 测试文件里也明确测了 basis/funding 两条策略的方向判定与 runner 行为。

对我们 desk 来说，这意味着它不是“想法线索”，而是已经接近 **可直接 dry-run 的完整策略底盘**。

但我做了最小 live snapshot 后，结论也很明确：

- **纯 taker/taker basis-arb，当前大概率不活。**
- 这份 repo 真正该先测的，不是 `always-on` 扫描，而是：
  - **maker/taker pocket**，或
  - **极端短时错价 pocket**，或
  - **basis 主信号 + funding/latency veto**。

换句话说，这条 raw alpha 不是没有，而是**生存条件非常苛刻**；要先把“什么时候值得出手”测清楚，而不是直接默认常开。

## 3. live snapshot：当前 gross spread 远小于 repo 默认 taker 成本

我用公开可得的两边盘口做了一个最小 live snapshot（UTC 2026-03-28 约 09:10）：

- **SOL**
  - Drift best bid/ask：`83.0623 / 83.0863`
  - Hyperliquid best bid/ask：`83.1040 / 83.1050`
  - 若做 `long Drift / short Hyperliquid`，当前可交叉 gross spread 约 **2.13 bps**
- **ETH**
  - Drift best bid/ask：`1994.35 / 1995.74`
  - Hyperliquid best bid/ask：`1995.90 / 1996.00`
  - 同方向 gross spread 约 **0.80 bps**
- **BTC**
  - Drift best bid/ask：`66306.7 / 66314.5`
  - Hyperliquid best bid/ask：`66330.0 / 66331.0`
  - 同方向 gross spread 约 **2.34 bps**
- **repo 默认 taker round-trip 成本**：
  - `2 × (8bps + 7bps) = 30bps`

这几个数放一起就够说明问题：

- 当前 majors 上的**瞬时可交叉 gross basis**，大约只有 **0.8 ~ 2.3 bps**；
- 但 repo 默认 taker/taker round-trip 成本是 **30 bps**；
- 所以如果照 repo 配置把它理解成“看见价差就双边 taker 打掉”，那基本等于**拿 execution 去补 alpha 的空洞**。

因此，这篇东西的正确 desk 化读法不是：

> “双所有价差，所以能套利。”

而是：

> “cross-venue perp-perp basis 是一条真实 raw alpha，但只有在 fee budget、slippage、queue priority、rollback 风险都被严肃约束后，才会变成可活 pocket。”

## 4. desk 化后的完整策略骨架

### 4.1 Base alpha

- **raw alpha**：`basis_t = rich_venue_crossable_bid - cheap_venue_crossable_ask`
- 当 `basis_t` 足够大，且扣掉成本后仍显著为正时，做：
  - `short rich venue`
  - `long cheap venue`
- 等待 basis 收敛或价差回到 rolling fair band。

### 4.2 Entry

不要直接沿用“`profit >= min_profit_usd` 就打”这种静态写法，建议改成 **net-edge pocket**：

- 用目标 size 的**深度加权成交价**，不是只看 top-of-book；
- 计算两个方向的：
  - `gross_edge_bps`
  - `entry_fee_bps`
  - `expected_exit_fee_bps`
  - `slippage_buffer_bps`
  - `rollback_buffer_bps`
- 只有当：
  - `net_edge_bps = gross_edge_bps - all_costs_bps > threshold`
  - 且盘口更新时间、深度、两腿健康度都满足条件，才允许开仓。

一个更诚实的起点是分三档：

- **taker/taker 档**：先当高门槛稀有 pocket，要求 `net_edge_bps` 明显大于 0；
- **maker/taker 档**：rich venue 被动挂单、cheap venue 主动对冲；
- **maker/maker 档**：只做研究，不先上生产，因为 queue 与 legging 风险更大。

### 4.3 Exit

建议别做“赚到固定金额就走”的粗口径，而是：

- **价差回归 exit**：当 `basis_t` 压缩到入场时的 `25%~50%` 以下；
- **时间止盈/止损**：`30s / 60s / 180s / 300s` 多档观察；
- **异常扩张止损**：如果价差在开仓后继续逆向扩大到 `entry + stop_buffer`，直接平；
- **execution failure exit**：任一腿未成交、挂单超时、quote stale，立刻撤退/回滚。

### 4.4 Sizing

适合用**深度约束 + notional cap**，而不是固定手数：

- `size <= min(drift_depth_cap, hyper_depth_cap, venue_margin_cap, strategy_notional_cap)`
- 初版可先限制成 top-of-book 或前 `3~5` 档的 `5%~10% participation`；
- 大币先做 `BTC/ETH/SOL`，别一开始上小币。

### 4.5 Risk / Cost

这条策略的核心不是预测错，而是 **execution / latency / fee cliff**：

- `max_slippage_bps` 要单独统计两腿，不要只看 max；
- `rollback` 成功率本身就是主 KPI；
- 要区分：
  - **信号胜率**（价差会不会回归）
  - **执行胜率**（双腿能否在预算内对上）
- 如果净 edge 大部分都落在 `0~5bps`，那不是“再调调参数”，而是这条实现方式不该上。

## 5. 它和当前 `1m / 3m / 5m / 15m` 的关系

这条 alpha 的**天然周期其实比 5m 更快**，更像 `seconds → 1m / 3m` 的高强度 raw alpha。对当前 desk，最合理的定位是：

- **`1m / 3m`**：可以直接做主策略 admission check；
- **`5m / 15m`**：更适合作为
  - relative-value 子策略，或
  - execution-quality pocket overlay，或
  - “当跨所错价显著时，允许更积极做 mean-rev / spread 收敛”的补充模块。

所以它不是典型 bar-close 15m 因子，但**完全符合用户允许的更快高强度 alpha intake**。

## 6. 下一步最小实验（这次最重要）

先别急着回测 PnL，先做 **pocket existence check**：

1. **数据抓取**
   - 每 `1s` 拉一次 Drift `l2` 与 Hyperliquid `l2Book`
   - 先只做 `BTC/ETH/SOL`
   - 持续 `3~7` 天
2. **构造两个方向的可成交净边**
   - `gross_edge_bps(long Drift / short Hyper)`
   - `gross_edge_bps(long Hyper / short Drift)`
   - 用 depth-weighted price，不用裸 best bid/ask
3. **分三种成本口径**
   - taker/taker
   - maker/taker
   - maker/taker + rollback buffer
4. **做 pocket 统计**
   - `gross_edge_bps > 5 / 10 / 15 / 20 / 30 bps` 的出现频率
   - pocket 持续时间（`1s/3s/5s/10s/30s`）
   - pocket 发生后 `5s/15s/60s/180s` 的 markout
5. **只回答一个 admission question**
   - 在现实成本下，这条策略到底有没有**可重复 pocket**？

如果结果显示：

- taker/taker 几乎没有 pocket；
- 但 maker/taker 在少数时段有稳定 pocket；

那下一步就转成：

> **“maker-first cross-venue basis pocket”**

而不是继续把它包装成“普适双边套利”。

## 7. 风险与诚实约束

- **成本悬崖极高**：当前 snapshot 已经说明，gross edge 很容易远小于默认 taker 成本；
- **Drift 的流动性结构与 Hyperliquid 不完全同质**：同样叫 perp，微观成交体验不同；
- **回滚风险不是附属问题，是主问题**；
- **不能把 funding branch 混成 basis 胜率**：两条策略必须分开评估；
- **不能只看 top-of-book**：真正能不能做，取决于 size 后的成交价，而不是屏幕上那一跳。

## 8. 结论

这份 2025 repo 值得进素材池，但要换一个更诚实的标题：

- 它不是“发现一个常开套利机”；
- 它更像是：
  - **一条很清楚的 raw alpha**：cross-venue perp-perp basis convergence；
  - **一个很完整的执行骨架**：双腿协调、超时、回滚、safe mode；
  - **一个必须先过 pocket-existence check 的 admission candidate**。

一句话总结：

> **alpha 在，execution 更大；先验证 pocket 是否存在，再决定这是不是策略，而不是先假设它能赚钱。**

## 9. 来源

1. **Alex Bitok (2025). _Drift ↔ Hyperliquid Arbitrage Bot_. GitHub repository.**  
   Venue: GitHub  
   DOI: N/A  
   Repo URL: `https://github.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_`  
   Readable README: `https://raw.githubusercontent.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_/main/README.md`  
   Key source files:  
   - `https://raw.githubusercontent.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_/main/strategies/basis.py`  
   - `https://raw.githubusercontent.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_/main/strategies/funding.py`  
   - `https://raw.githubusercontent.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_/main/execution/engine.py`  
   - `https://raw.githubusercontent.com/Alex-bitok/drift-hyperliquid-arbitrage-bot_/main/config/main.example.yaml`

2. **GitHub metadata (2025).**  
   URL: `https://api.github.com/repos/Alex-bitok/drift-hyperliquid-arbitrage-bot_`  
   用于确认仓库创建时间、最近更新时间、stars 与描述。

3. **Drift public DLOB endpoint.**  
   URL 示例：`https://dlob.drift.trade/l2?marketName=SOL-PERP`  
   公开性：公开可得  
   更新频率：近实时 order-book  
   本轮最小实验口径：每秒抓取 `BTC-PERP / ETH-PERP / SOL-PERP` 的 bids/asks，构造 depth-weighted crossable edge。

4. **Hyperliquid public Info API.**  
   URL: `https://api.hyperliquid.xyz/info`  
   本轮使用 payload：  
   - `{"type":"l2Book","coin":"SOL"}`  
   - `{"type":"l2Book","coin":"ETH"}`  
   - `{"type":"l2Book","coin":"BTC"}`  
   公开性：公开可得  
   更新频率：近实时 order-book  
   本轮最小实验口径：与 Drift 同步抓取后，计算双方向 crossable basis 与 pocket 持续时间。
