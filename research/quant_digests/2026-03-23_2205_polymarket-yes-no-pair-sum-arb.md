# 别把 Polymarket 只当方向押注：更值得先复现的是 `YES+NO 合价 > 1` 的 market-neutral raw alpha
- 时间：2026-03-23 22:05 UTC
- 类型：开源仓库 + Polymarket 官方文档 + 机制拆解
- 主题类型：raw alpha
- 基础 alpha：在 Polymarket 短周期 crypto binary 市场里，当同一事件的 `YES` 与 `NO` 可卖价格之和显著高于 `1.00 + 全部成本` 时，做 `split -> 双边卖出 -> 持有到结算/赎回` 的 market-neutral 相对价值套利
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/stat-arb/relative-value/pairs/polymarket/yes-no/split-merge/redeem/market-making/external-data/crypto/5m/15m
- 证据类型：机制证据 + 工程证据 + 官方文档证据

## 1. 这次看了什么
先回答 base alpha：**不是“猜 BTC 下一根涨跌”，而是利用同一 binary 市场 `YES + NO = $1` 的结算恒等式，去抓二级盘口里 `双边可卖价格之和 > 1` 的短周期错价。**

这次主看两类材料：
- 一个近期高信号开源仓库，把 Polymarket 的 `split -> pair sell -> monitor -> redeem` 做成了完整机器人骨架；
- Polymarket 官方 CLOB / CTF / fee 文档，用来确认这条 alpha 的结算约束、公开数据口径与成本结构。

和我们 desk 的关系很直接：这不是又一个“解释 BTC 为什么会动”的 filter，而是一条**可独立复现、可完整落地、天然 market-neutral 的 relative-value / stat-arb raw alpha**。

## 2. 核心结论
- **一句话结论：** 对短周期 crypto desk 来说，Polymarket 更值钱的不是方向猜测，而是 `YES+NO pair-sum arbitrage` 这条可程序化的 raw alpha。
- **为什么它能单独成立：** Polymarket 官方文档明确写了 binary market 的 `YES` / `NO` token **每一对都由恰好 $1.00 USDC.e 抵押**；也就是说，若你能把一对 outcome token 的总卖出收入做在 `> 1.00 + 成本`，理论 edge 就很清楚。
- **为什么是短周期而不是低频 carry：** Polymarket 官方与开源仓库都支持 5m / 15m / 1h / 4h / 1d 的 crypto up/down 市场；其中 5m / 15m 最适合做快节奏扫描、分时 pair-sell、超时撤单和次优价位跟单。
- **为什么要先过成本关：** Polymarket 官方 fee 文档显示，**crypto 类 taker fee 的峰值有效费率可到 1.80%（在 50% 概率附近）**；所以这条 alpha 不能写成“pair sum > 1 就冲”，而必须写成 `pair sum > 1 + taker/maker fee + 滑点 + 未成交风险 + 赎回摩擦`。
- **为什么 repo 有研究价值：** 开源骨架已经把 `split / 双边挂卖 / timeout / redeem / activity log` 串起来，值得复用的是**策略骨架和执行状态机**，不是 README 里自报的高收益截图。

## 3. 为什么这轮值得优先于继续补 gate
如果答不上“它为什么比继续补 raw alpha 更值得”，这题就不该进 digest。这里能答上：**因为它本身就是 raw alpha，而且是我们当前池子里相对稀缺的 market-neutral / relative-value / stat-arb 分支。**

相比继续写一个 BTC 方向 filter，这条线的优先级更高在于：
- 它的 **base alpha 非常清楚**，不是把 veto 伪装成 alpha；
- 它天然自带 **完整策略闭环**：entry、exit、sizing、timeout、成本、结算、资金占用；
- 它和 `5m / 15m` 的映射非常直接：产品本身就有短周期 binary market；
- 它能补 desk 当前相对缺的那一块：**公开 venue 上、低方向暴露的短周期相对价值素材池**。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral / relative-value / stat-arb
- 基础 alpha：`pair_sum_sell = best_bid_yes + best_bid_no` 或更保守地看 depth-adjusted 可成交卖价；当 `pair_sum_sell > 1 + all_in_cost` 时存在理论正 edge
- entry：
  1) 在 Gamma API 找到活跃的 crypto up/down 市场；
  2) 用 CLOB orderbook 拉 `YES` / `NO` 双边盘口；
  3) 若 `pair_sum_sell_net >= 1 + min_edge_buffer`，先 split 成一对 outcome token，再按价差状态顺序卖出两边
- exit：
  - 理想路径：双边都卖出 -> 锁定现金流 -> 等市场结算/赎回
  - 次优路径：若只卖出一边且另一边长时间不成交，按 timeout 规则撤单 / 改价 / merge 回 USDC.e
- sizing：
  - 以 `portfolio_allocation_usdc` 和 `pair_size` 为主；
  - 单市场单周期上限由盘口深度、min order size、挂单存活时间、以及未完成腿风险决定
- risk：
  - **leg risk**：只成交 YES 或 NO 一边，另一边挂不出去；
  - **timeout risk**：临近结算前流动性恶化或点差塌陷；
  - **venue risk**：API、链上结算、builder relayer、订单认证故障；
  - **fee risk**：若被迫吃 taker 或频繁改价，edge 很容易归零
- cost：
  - maker/taker fee（按 Polymarket crypto fee 曲线）
  - 滑点（按 depth-adjusted fill price）
  - 未成交腿对冲/回补成本
  - 资金占用与赎回等待成本

## 4. 外部数据与公开性（必填）
这题主要依赖外部公开数据，但它**不是低频宏观因子**，而是可直接映射到短周期最小实验的 venue data：

- **数据源 1：Gamma API（公开）**
  - 用途：发现活跃 markets / slugs / token IDs
  - 公开性：公开可拉，无需私钥即可做市场发现
  - 更新频率：事件驱动，适合每分钟或更高频轮询
- **数据源 2：Polymarket CLOB orderbook / midpoint / spread（公开）**
  - 用途：YES / NO 双边 best bid、best ask、spread、历史价格
  - 公开性：官方公开 market-data API
  - 更新频率：可近实时读取，足够支撑 5m / 15m 最小实验
- **数据源 3：CTF 机制文档（公开）**
  - 用途：确认 split / merge / redeem 以及 `YES+NO=$1` 的结算约束
  - 公开性：官方公开文档
- **可选执行数据：私钥与 API creds（非公开，仅实盘时需要）**
  - 研究最小实验阶段并不需要；先做 market data + paper execution 就够了

## 5. 可复刻的最小实验（下一步怎么测）
### 研究假设
在 Polymarket 的 5m / 15m crypto up/down 市场里，存在一批时点满足：
`depth_adjusted_yes_bid + depth_adjusted_no_bid - all_in_cost > 1`，
这批时点可支持一个 paper-trade 级别的 market-neutral pair-sell 策略。

### 最小实验口径
1. **市场发现**
   - 每 30~60 秒扫描活跃的 BTC / ETH / SOL / XRP up/down 市场；
   - 记录 slug、token IDs、到结算剩余时间。
2. **盘口抓取**
   - 对 YES / NO 分别抓 best bid / ask、top-N depth、spread；
   - 算 `best_bid_sum`、`depth_adjusted_sell_sum(q)`、`mid_sum`。
3. **信号定义**
   - `gross_edge(q) = depth_adjusted_sell_sum(q) - 1.00`
   - `net_edge(q) = depth_adjusted_sell_sum(q) - 1.00 - fee_est - slippage_est - timeout_penalty`
   - 仅当 `net_edge(q) > edge_buffer` 才允许进场
4. **paper execution**
   - 模拟 `split -> sell YES -> sell NO -> monitor -> redeem`
   - 若单腿超时未成交，按撤单/追价/merge fallback 规则处理
5. **统计输出**
   - 按 5m / 15m 分桶，输出：
     - `candidate_count`
     - `fillable_count`
     - `avg_net_edge_bps`
     - `two_leg_completion_rate`
     - `timeout_rate`
     - `post_cost_pnl_per_pair`

### 第一轮只测什么
先别急着真钱执行。第一轮只做三件事：
- **测有没有净 edge**：不是 `pair_sum > 1`，而是 `net_edge > 0`
- **测能不能两腿都卖出去**：completion rate 决定这是不是现实策略
- **测 edge 是否集中在某些时间窗**：例如离结算前最后 30~90 秒、或流动性突然抬升的时段

## 6. 对 1m / 3m / 5m / 15m 的映射
- **5m：最自然。** 这是产品原生周期之一，适合做 end-of-cycle / near-expiry 扫描与 pair-sell。
- **15m：也自然。** 挂单和完成双腿的时间预算更宽，超时管理相对友好。
- **1m / 3m：不建议把它硬写成单独产品 alpha。** 更合理的做法，是把 1m / 3m 用作**盘口重采样与执行刷新频率**，而不是假装 venue 本身有同样丰富的 1m 合约深度。

## 7. 风险与保留意见
- **repo 的收益截图不应当直接采信。** 这个题值钱的是骨架，不是 README 里的高收益宣传。
- **pair-sum alpha 最大风险不是方向，而是 execution。** 只成交一边、另一边卖不掉，会把无方向套利变成裸方向暴露。
- **费用曲线不是常数。** 在 50c 附近 crypto taker fee 最贵，越接近 0/1 越便宜，所以 entry 阈值必须按价格区间动态调。
- **不能只看 best bid。** 若盘口深度很薄，best bid sum 看上去 >1，但一吃深度就没 edge 了。
- **这条 alpha 更像 venue-specific pocket。** 它对主流 crypto perp/spot 主战场不是替代关系，而是补充关系：给 desk 增加一类公开、可程序化、低方向暴露的短周期策略素材。

## 8. 这条线最值得偷的不是哪一条参数，而是哪一个组件
真正值得复用的不是 README 里某个 `min_pair_sum=1.03`，而是这个**完整状态机**：

`market discovery -> yes/no token mapping -> pair-sum edge calc -> split -> dual-leg execution -> timeout fallback -> redeem -> activity attribution`

如果后续要迁回更主流的 crypto venue，这套拆法也能迁移：
- 在 perp/spot 上对应的是 `relative-value spread + 双腿成交率 + timeout fallback`
- 在 prediction market 上对应的是 `YES/NO pair-sum + 到期结算`

## 9. 来源
1. **Gabagool2-2. (ongoing, accessed 2026). _polymarket-trading-bot-python_. GitHub repository.**
   - Repo URL: https://github.com/Gabagool2-2/polymarket-trading-bot-python
   - Readable URL: https://github.com/Gabagool2-2/polymarket-trading-bot-python
2. **Polymarket Docs. (accessed 2026). _Conditional Token Framework_.**
   - Readable URL: https://docs.polymarket.com/trading/ctf/overview
3. **Polymarket Docs. (accessed 2026). _Orderbook_.**
   - Readable URL: https://docs.polymarket.com/trading/orderbook
4. **Polymarket Docs. (accessed 2026). _Fees_.**
   - Readable URL: https://docs.polymarket.com/trading/fees
5. **Polymarket Docs. (accessed 2026). _Fetching Markets_.**
   - Readable URL: https://docs.polymarket.com/market-data/fetching-markets
6. **Gnosis. (ongoing). _conditional-tokens-contracts_. GitHub repository.**
   - Repo URL: https://github.com/gnosis/conditional-tokens-contracts
   - Readable URL: https://github.com/gnosis/conditional-tokens-contracts
