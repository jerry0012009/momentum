# 别把这份 2026 coin-margined options repo 继续当“又一个 box scanner”：对 desk 更该先测的是「carry-adjusted same-venue conversion/reversal × parity gap hurdle」raw alpha，但必须先统一 inverse premium 单位
- 时间：2026-03-30 10:18 UTC
- 类型：2026 GitHub 新仓库 + `strategies/arbitrage/conversion.py` / `docs/theory.md` source audit + Deribit BTC options 公共 live sanity check + 2023 *Mathematical Finance* 理论锚点
- 主题类型：raw alpha
- 基础 alpha：**同所、同到期、同执行价的 `call-put-spot/perp` 在 carry 调整后的 put-call parity 上出现可覆盖 frictions 的偏离；当偏离足够大时做 conversion / reversal，吃的是 synthetic forward 向理论 forward 回归的相对价值 alpha。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/relative-value/stat-arb/put-call-parity/conversion/reversal/synthetic-forward/same-venue/coin-margined/inverse-options/deribit/okx/btc/eth/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：代码级策略定义 + 公开 live 行情快检 + 理论论文锚点

## 1. 这次看了什么
这次主看 **`signorloops/crypto-options-research-platform` (2026)** 里的 `strategies/arbitrage/conversion.py`。如果只用一句人话概括，这份 repo 真正适合 desk intake 的，不是再看一遍 box spread，而是：

> **把 same-venue 的 put-call parity 偏离，直接写成 `trade only when deviation > cost hurdle` 的 conversion / reversal 状态机。**

对当前 desk，这条线的价值在于：它是一条**独立完整的 raw alpha**，不是 filter；而且它天然属于 `relative value / stat-arb`，能补现在素材池里更偏 trend / pairs / funding 的另一块。

## 2. 核心结论
- **base alpha 很清楚。** repo 不是拿 parity 做解释，而是直接定义：
  - `synthetic_forward = call_price - put_price`
  - `theoretical_forward = S * exp(-qT) - K * exp(-rT)`
  - `deviation = synthetic_forward - theoretical_forward`
  - 若 `deviation > total_cost` 做 **conversion**；若 `deviation < -total_cost` 做 **reversal**。
- **它已经把完整策略骨架写出来了。** 代码默认：`risk_free_rate = 5%`、`min_profit_threshold = 0.1%`、`transaction_cost = 0.2%` 单边；并把总门槛写成 `3 * transaction_cost * spot`，等于显式要求一次 trade 必须同时覆盖 `call + put + underlying` 三条腿的 frictions。
- **它把 carry 调整写进 parity，而不是假装 `q=0`。** `calculate_parity_deviation()` 允许把 `staking_yield`/carry yield 带入 `S * exp(-qT)`。这点对 crypto 重要，因为这里的“现货腿”很多时候更像 `spot / perp / synthetic cash leg`，不是传统股票的静态 carry 环境。
- **repo 最该借的不是参数，而是 trade-on / trade-off 逻辑。** `get_hedge_position()` 已经把 conversion 写成 `short call + long put + long underlying`，reversal 写成 `long call + short put + short underlying`；`calculate_margin_requirement()`、`calculate_pnl_scenarios()`、`verify_arbitrage_bounds()` 也已经把保证金、情景 PnL、无套利边界检查放进同一个壳子。
- **但这份代码不能直接照抄上实盘。** repo 自己定位是 **coin-margined / inverse options** 平台，`docs/theory.md` 也明确写了 inverse 期权；可 `conversion.py` 里直接用 `call_price - put_price` 去和 `S - K e^{-rT}` 比，默认假设 premium 与 spot/strike 在同一计价单位。若 live 行情是 Deribit 常见的 **BTC 计价 premium**，就必须先统一 numeraire，否则 parity gap 会被“单位错位”污染。

一句话核心结论：

> **对 desk 更值得先测的，不是 box spread 的年化利率故事，而是 same-venue synthetic-forward mispricing 本身；但必须先把 inverse premium 统一到同一计价单位，再谈 alpha。**

一句话说明它怎么证明：

> **不是只在 README 里口头讲 parity，而是把偏离定义、成本门槛、三腿方向、保证金估算、PnL 场景和 bound check 全写成了可审计代码；再用公开 Deribit option chain 做 live sanity check，能直接看出“数据是公开的、机会是稀薄的、单位问题是真的”。**

## 3. 为什么和当前项目有关
这轮值得写它，而不是再补一篇纯解释型 options 综述，原因很直接：

1. **它是 raw alpha，而且是完整策略。** 信号、入场、对冲腿、出场思路、成本门槛、保证金全能落地。
2. **它补的是 relative-value / stat-arb 素材池。** 不是继续围绕 breakout / trend / funding 单线内循环。
3. **它天然适合短周期。** 这类机会不是靠日频持有，而是靠 `event-driven snapshot -> 短时间收敛 -> 快速平仓`；最自然的实验频率就是 `1m / 3m`，`5m` 做容错，`15m` 只适合做机会热度面板，不适合当主时钟。
4. **它还能服务后续更多 options 线。** 同一套 numeraire 校准、费用建模、quote staleness 检查，以后还能复用于 box / vertical / cross-venue parity 线。

## 3.5 策略拆解（必填）
- 方向属性：**relative value / stat-arb / same-venue options-parity arbitrage**
- 基础 alpha：**carry-adjusted put-call parity 偏离会回归无套利带**
- regime：**短到期、链路稳定、盘口非极端稀薄时更适合；重大波动/事件前后的 quote staleness 要单独标记**
- filter / veto：**偏离不过 `friction hurdle` 不交易；腿的盘口深度不足、不同时戳、spread 过宽、估算 carry 不可靠时 veto**
- risk / sizing / execution overlay：**按最短板腿的可成交名义 sizing；优先限价/半主动成交；加总三腿手续费、滑点、borrow/funding/carry；设置 quote age 与 max hold kill-switch**

## 4. 3 个关键数据点
1. **repo 默认门槛并不低：** `transaction_cost = 0.2%` 单边，`total_cost = 3 * cost * spot`，意味着策略不是“看到一点点 parity 漂移就上”。
2. **repo 默认只收够大的净边：** `min_profit_threshold = 0.1%`，利润/现货价不过线直接过滤。
3. **live 公共链快检显示机会很稀：** 2026-03-30 UTC，Deribit 公共接口可见 **`880` 个未到期 BTC options**；其中最近到期 ATM 附近的 `BTC-31MAR26-67500-C/P` 中间价折成 USD 后，`synthetic_forward - theoretical_forward ≈ -7.73 USD`，约 **`-1.15 bps` of spot**，说明 **same-venue parity 机会大概率不是“常驻宽边”，而是要做事件驱动 + 高质量费用口径。**

## 5. 真正值得 desk 先偷哪一段
最该先偷的，不是 repo 里写的 `5%` 无风险利率，也不是名义年化，而是这条 admission rule：

> **parity 偏离只有在穿过三腿总 frictions 后，才允许变成仓位。**

这件事对 options alpha 特别关键，因为很多“看起来有 gap”的机会其实会死在：
- call / put / underlying 不同步；
- 其中一条腿的盘口很薄；
- premium 单位没对齐；
- 你以为是 same-venue arb，实际吃的是 stale quote / latency illusion。

repo 的价值正是把这些坑的框架搭好了：**先算 deviation，再比 hurdle，再决定 conversion 还是 reversal。**

## 6. 可复刻的最小实验
### 6.1 数据源、公开性、更新频率
- **主数据源：** Deribit Public API（options instrument list、book summary、index price）
- **公开性：** 公开可得，无需私钥即可拉取 snapshots
- **更新频率：** 可秒级轮询；第一轮最小实验直接做 `1s~5s` snapshot，再聚合到 `1m / 3m`
- **可迁移源：** OKX 公共 options API；若要用 perp 替 spot，也可接同所 perp mid

### 6.2 最小可复现实验口径
1. **只做 BTC 单标的。** 先抓同所、同到期、同执行价的 call/put + index/perp mid。
2. **先统一 numeraire。** 若 premium 为 BTC 计价，先转成 USD 等价，再和 `S * exp(-qT) - K * exp(-rT)` 比；不要直接 `call_price - put_price` 硬减。
3. **定义信号：**
   - `gap_usd = synthetic_forward_usd - theoretical_forward_usd`
   - `gap_bps = gap_usd / spot * 10000`
4. **入场条件：**
   - `|gap_bps| > fee + slip + stale_quote_buffer`
   - 三腿时间戳差 < `1~2s`
   - call/put/underlying 的 top-of-book notional 都过阈值
5. **方向：**
   - `gap > hurdle` -> conversion
   - `gap < -hurdle` -> reversal
6. **出场：**
   - gap 回到零轴附近 / 压回成本带；或
   - `max_hold = 1m / 3m / 5m`；或
   - 任一腿报价失真/失联强平
7. **第一轮 friction ladder：** round-trip 先跑 `6 / 10 / 14 / 20 bps`，并把三腿分别记账，而不是只看总费用。

### 6.3 第一轮先回答什么
- same-venue parity gap 在公开快照里到底有多少次真正穿过成本？
- 这些事件主要出现在**临近到期**、**波动突增**，还是**盘口切换**时刻？
- `1m` hold 与 `3m` hold 谁更像收敛而不是噪音？
- 用 **spot** 还是 **perp** 当 underlying 腿，哪个更容易成交、哪个 funding/borrow 更诚实？

## 7. 这张卡最容易错在哪里
- **错法 1：** 忽略 inverse premium 单位问题，直接把 BTC premium 当 USD premium 做 parity。  
- **错法 2：** 只看 mid，不看 top-of-book size 与 quote age。  
- **错法 3：** 把这条线误写成 `15m` bar-close alpha；它更像 event-driven scanner。  
- **错法 4：** 看到小 gap 就激动；真实生存线取决于三腿费用、成交同步和仓位约束。  
- **错法 5：** 把 carry 写死成 `q=0`；crypto 里 spot/perp/staking 的持有收益和融资拖累都可能改掉 fair value。  

## 8. 为什么值得进入研究池
它值得进池，不是因为 repo 已经给了可信回测，而是因为它补了一个当前素材池里**很像 raw alpha、又很容易做 first verdict** 的槽位：

> **同所 options parity mispricing 本身就是 alpha；而且比很多“模型先行”的 options 线更容易被拆成干净的 trade-on / trade-off 规则。**

对当前 desk，这比继续补一个纯 overlay 更值钱，因为它能直接产出一轮诚实的 `1m/3m` 事件驱动验证。

## 9. 下一步怎么测
1. **先做 `Deribit BTC` 最近 `7~14` 天 snapshot 采集。** 只抓同到期 call/put + index/perp。  
2. **把 premium 单位统一作为第一优先。** 先做 USD 等价版 parity，再谈回测。  
3. **按 `same-venue conversion/reversal` 跑 friction ladder。** 先测是否存在真正穿过 `10~20 bps` 成本带的事件。  
4. **对照 two-leg vs three-leg 版本。** 比较 `call-put + spot` 与 `call-put + perp` 哪个更可执行。  
5. **若 BTC 能活，再扩 ETH。** 不要一开始全链铺开。  

## 10. 来源与链接
1. **signorloops (2026). _crypto-options-research-platform_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/signorloops/crypto-options-research-platform>  
   - Repo URL: <https://github.com/signorloops/crypto-options-research-platform>  
   - Key files:  
     - <https://github.com/signorloops/crypto-options-research-platform/blob/master/strategies/arbitrage/conversion.py>  
     - <https://github.com/signorloops/crypto-options-research-platform/blob/master/docs/theory.md>
2. **Alexander, C., Chen, J., & Imeraj, A. (2023). _Crypto quanto and inverse options_. Mathematical Finance.**  
   - DOI: <https://doi.org/10.1111/mafi.12410>  
   - Readable URL: <https://doi.org/10.1111/mafi.12410>  
   - Repo URL: N/A
3. **Deribit API Docs / Public Endpoints (live snapshot sanity check, accessed 2026-03-30).**  
   - Venue: Deribit Developer Docs  
   - DOI: N/A  
   - Readable URL: <https://docs.deribit.com/>  
   - Example endpoints used:  
     - <https://www.deribit.com/api/v2/public/get_instruments?currency=BTC&kind=option&expired=false>  
     - <https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name=BTC-31MAR26-67500-C>  
     - <https://www.deribit.com/api/v2/public/get_book_summary_by_instrument?instrument_name=BTC-31MAR26-67500-P>  
     - <https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd>
