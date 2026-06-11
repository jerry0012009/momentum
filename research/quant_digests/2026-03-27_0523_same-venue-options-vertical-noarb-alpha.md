# 别把这份 2026 options repo 只当报警脚本：更该先测的是「同所同到期 vertical-spread no-arb 违例」事件驱动 raw alpha，但当前 live snapshot 很薄
- 时间：2026-03-27 05:23 UTC
- 类型：仓库
- 主题类型：raw alpha
- 基础 alpha：同一交易所、同一到期日下，若不同 strike 的 call/put 报价违反基本单调性（例如高 strike call 反而比低 strike call 更贵到足以覆盖买卖价差），就做多被低估腿、做空被高估腿，吃 vertical spread 的 no-arbitrage 收敛。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/vertical-spread/no-arbitrage/same-venue/same-expiry/adjacent-strike/relative-value/stat-arb/event-driven/delta-exchange/btc/eth/1m/3m/5m/15m/repo/external-data
- 证据类型：仓库证据（2026 GitHub repo + Delta Exchange India 公共 options API 最小快检）

## 1) 这次看了什么
这次看的是 **vk82313 (2026)** 的 GitHub 仓库 **《crypto-arbitrage-bot》**。它表面上像一个泛泛的 “ETH & BTC Options Arbitrage Bot”，但把源码拆开后，真正值得我们 desk intake 的 **base alpha** 很具体：**同一 venue、同一 expiry、不同 strike 之间的 vertical spread 单调性违例**。换成人话，就是：**如果同到期权链里出现“贵的应该更便宜、便宜的反而更贵”的盘口错位，就做一个几乎 market-neutral 的收敛腿对。**

我额外用仓库里直接调用的 **Delta Exchange India 公共 `/v2/tickers`** 口径做了一个 live quick check，先看这个 raw alpha 在当前公开盘口里是不是至少还看得见。

## 2) 核心结论（先说人话）
- **一句话核心结论：** 这份 repo 真正该进入素材池的，不是“做 options arbitrage”这句大词，而是更窄、更可测的 **same-venue / same-expiry vertical-spread no-arb 违例** 事件驱动 raw alpha。
- **一句话证明方式：** 仓库把信号、执行、超时、加价追单都写成了完整代码；我再对其公开数据源做 live quick check，发现这条 alpha **逻辑完整但当前信号密度很薄**。
- 源码里的信号非常直接：
  - **Call 侧**：若 `K1 < K2`，却出现 `bid(Call, K2) > ask(Call, K1)`，就买低 strike call、卖高 strike call；
  - **Put 侧**：若 `K1 < K2`，却出现 `bid(Put, K1) > ask(Put, K2)`，就卖低 strike put、买高 strike put。
- 这不是拍脑袋规则，而是最基本的 **同到期 strike 单调性 / vertical spread no-arbitrage**。正常情况下：
  - call 价格应随 strike 上升而下降；
  - put 价格应随 strike 上升而上升；
  - 若反过来，而且反过来的幅度足够大到覆盖 fees/slippage，就出现可交易的相对价值机会。
- 仓库执行骨架也算完整：
  - **1 秒轮询** 公共 options tickers；
  - 先卖贵腿，**5 秒**等成交；
  - 再买便宜腿，按 **2 秒 → 加一档 → 2 秒 → 提到对手卖价** 的 ladder 去追；
  - 单笔最多 **100 lots**；
  - 默认阈值是 **ETH 最小毛利 0.20、BTC 最小毛利 3.00**。
- 但 live quick check 很诚实地泼了冷水：
  - 当前公开 endpoint 一次返回约 **942 个 options ticker**；
  - `BTC/ETH` 各有 **7 个 expiry**；
  - 按 repo 的“**相邻 strike**”规则去扫，**BTC 所有 expiry = 0 个 gross 违例，ETH 所有 expiry = 0 个 gross 违例**；
  - 即便把扫描放宽到“**同 expiry 的任意 strike 对**”，也只在 **ETH 当日到期 put** 上看到 **1 个 gross=0.01** 的极小违例，远小于 repo 自己设的 `0.20` 阈值，更别说 fees/slippage。
- 所以这条线当前更像：**一个结构上成立、工程上完整、但 live 盘口里不一定常有肉的 raw alpha 家族**。值钱的地方在于它是 **可直接验证的完整策略骨架**，而不是它今天已经被 quick check 证实“遍地是钱”。

## 3) 为什么和当前项目有关
这条线和当前 desk 相关，不是因为我们一定要转去做 options，而是因为它补的是一类我们还不算多的 **“静态 no-arb / 盘口错位 → 事件驱动收敛”** raw alpha。它和最近那些 perp lead-lag、funding carry、cross-sectional reversal 不同：

- 它是 **同资产、同到期、同 venue** 内部的 relative-value；
- 它天然 **market-neutral / delta 较低**，不是裸方向；
- 它和 `1m/3m/5m/15m` desk 的关系，不是把 15m K 线当信号本体，而是把 **秒级 quote 违例事件** 聚合成可交易事件，再映射成分钟级监控、回放与风控框架。

如果后续我们继续扩 raw alpha 素材池，这类“**价差错位收敛**”家族值得保留一条：它不跟 breakout / momentum 内循环撞车，也能补上 options / static-arb / quote-dislocation 这块空白。

## 3.5) 策略拆解（必填）
- 方向属性：**relative-value / stat-arb / 低方向暴露收敛型**
- 基础 alpha：**同所同到期 vertical spread 单调性违例会在短时间内回归 no-arb 区间**
- regime：**近到期、盘口稀疏、报价刷新不同步、局部流动性空洞** 的时段更容易出现
- filter / veto：
  - 仅做 `gross_edge > fees + slippage + legging_buffer`
  - 两腿最小可成交量都要过线
  - quote age 不能太老
  - underlying 在挂单期间不能大幅跳动
  - 到期前最后几分钟若流动性断裂，默认降权或 veto
- risk / sizing / execution overlay：
  - 单 expiry / 单资产设置 notional cap
  - 优先 IOC/FOK 或超短 timeout，减少单腿裸露时间
  - 对“先卖后买”的 legging risk 单独记账
  - 把 `edge / strike_gap`、盘口深度、距到期时间一起纳入 sizing

## 4) 可复刻的最小实验
**研究假设：** 即便 repo 当前的“相邻 strike + 固定阈值”版本在 live snapshot 上几乎抓不到 gross edge，**更宽的 strike 对扫描 + 更严的 quote 质量过滤**，仍可能在 near-expiry、薄盘口时段留下可交易的秒级错位事件。

**一个最小可计算定义：**
1. 直接调用公开数据源：`https://api.india.delta.exchange/v2/tickers?contract_types=call_options,put_options`；
2. 对 `BTC/ETH` 按 `expiry × strike × option_type` 重组 order book top-of-book；
3. 同一 expiry 下同时计算两类信号：
   - **adjacent vertical arb**：只看相邻 strike；
   - **full-pair vertical arb**：看任意 `K1 < K2`，但把 edge 用 `gross_edge / (K2-K1)` 归一化；
4. 成本口径先别乐观：至少扣 **双边 taker fee + 2 腿半个 spread + legging shock buffer**；
5. 记录每次违例的：出现时长、最大 gross edge、净 edge、两腿 size、到期剩余时间、underlying 同期波动。

**最小回放切口：**
- 资产：`BTC/ETH options`
- 频率：**1 秒轮询**；对 desk 展示时再聚合成 `1m/3m/5m/15m` 的 **事件计数 / 最大净 edge / 持续时长**
- 时间窗：先抓 **近 7 天 × 全部 expiry**，优先盯 **当日到期 + 次日到期**

**先看 4 个指标：**
- `violations/day`
- `median net edge / opportunity`
- `median dwell time`（违例能活多久）
- `legging-adjusted fill ratio`

## 5) 风险与保留意见
- **这是 repo 证据，不是论文证据。** 理论没问题，但没有看到严肃样本内外检验。
- 当前 live quick check 基本判定：**repo as-is 的信号非常稀薄**。如果继续做，必须接受“这可能主要是 stale quote artifact，而不是稳定 alpha”。
- 仓库默认只扫 **相邻 strike**，这会漏掉不少跨档位异常；但扫太宽又会引入更多假信号。
- 仓库执行是明显的 **legging**：先成交贵腿，再追便宜腿；真实交易里最容易死在这里。
- Delta Exchange India 不是 Deribit 这类更深的主战场，**venue transfer** 不一定成立；但也正因为更薄，才更可能有 quote-dislocation。
- 代码里的固定阈值 `ETH 0.20 / BTC 3.00` 没有按 strike gap、手续费、到期时间归一化，作为 production 规则太粗。

## 6) 来源
1. **vk82313. (2026). _crypto-arbitrage-bot_. GitHub repository.**
   - Repo URL: <https://github.com/vk82313/crypto-arbitrage-bot>
   - Readable README: <https://raw.githubusercontent.com/vk82313/crypto-arbitrage-bot/main/README.md>
   - Source code: <https://raw.githubusercontent.com/vk82313/crypto-arbitrage-bot/main/app.py>
2. **Delta Exchange India public options ticker endpoint**
   - Publicity: 公开可得
   - Update frequency: 秒级可轮询（repo 按 `1s` 轮询）
   - Endpoint used: <https://api.india.delta.exchange/v2/tickers?contract_types=call_options,put_options>
   - Minimal reproducible experiment: 重建 `expiry × strike × option_type` 顶层盘口，扫描 call/put vertical monotonicity 违例并扣除双边成本
3. **Merton, R. C. (1973). _Theory of Rational Option Pricing_. Bell Journal of Economics and Management Science.**
   - DOI: <https://doi.org/10.2307/3003143>
   - Readable URL: <https://www.jstor.org/stable/3003143>
   - 用途：作为同到期 strike 单调性 / no-arbitrage 约束的理论地基，而不是 crypto-specific 证据

## 7) 下一步怎么测（一句话）
别先把它当 live bot，上来先做 **7 天秒级抓数 + full-pair vertical 扫描 + 成本后净 edge 分布**；如果连 `violations/day` 和 `dwell time` 都起不来，就把这条线降级为“薄盘口 quote-artifact 监控”，别进主复现队列。
