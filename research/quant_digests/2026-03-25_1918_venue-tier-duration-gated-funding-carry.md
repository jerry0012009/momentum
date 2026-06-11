# 别把 cross-venue funding carry 当成“大 venue 都能跑”的公共票息：这篇 2026 论文更该先落地的是「venue tier + 持续时长」双门槛
- 时间：2026-03-25 19:18 UTC
- 类型：2026 论文（Crossref/OpenAlex 摘要可得）+ 多 venue 公共 funding 数据最小快检
- 主题类型：raw alpha
- 基础 alpha：同一币种跨 venue 做 `long 低 funding venue + short 高 funding venue` 的 delta-neutral funding spread carry，并要求 spread 在成本覆盖前持续足够久
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/cross-venue/relative-value/stat-arb/delta-neutral/cex/dex/duration-gate/cost/1m/3m/5m/15m/paper
- 证据类型：论文结构证据 + 公共 API 快检

## 1. 这次看了什么
先回答 base alpha：**这篇东西的 base alpha 不是“交易所分层解释”，而是跨 venue funding spread carry 本体。**

更具体地说，交易逻辑是：
- 在 funding 更贵的一侧做空；
- 在 funding 更便宜的一侧做多；
- 方向尽量 delta-neutral；
- 真正决定能不能赚钱的，不只是 spread 有多大，还包括 **它能持续多久**、以及这个 spread 是不是来自 **CEX/DEX 分层错位** 而不是即将回归的短暂噪音。

所以这篇 2026 新论文对我们 desk 最值钱的，不是“世界上存在 funding arbitrage”这句废话，而是把它 desk 化成一句更实用的话：**先做 venue tier classification，再做 duration gate；否则很多看起来很肥的 spread，根本活不到覆盖 round-trip cost。**

## 2. 核心结论
- **一句话核心结论：** 这条线仍然是可执行的 raw alpha，但它不该被读成“只要看到 funding spread 就上”；更诚实的读法是：**只有 `大 spread × 足够持续 × venue tier 合适` 的那一小撮机会，才配进入 live 候选池。**
- **一句话它怎么证明：** 论文用 26 家交易所、749 个合约、3570 万条 1 分钟观测做结构检验与 delta-neutral 组合仿真；我再用 Binance / Bybit / Hyperliquid 的公开 funding history 做 21 天快检，确认大 venue 主流币上的 spread 大多又薄又短，确实很容易被成本吃掉。

关键数据点（论文）：
1. 论文样本是 **26 家交易所（11 CEX、15 DEX）× 749 个 symbol × 8 天 × 3570 万条 1 分钟观测**。
2. 作者发现 **CEX 的市场整合度比 DEX 高 61%**，且显著信息流方向是 **CEX → DEX**，没有反向因果。
3. 全样本里只有 **17%** 的观测出现“经济上显著”的 funding arbitrage spread（论文口径：`>= 20 bps`）；而在作者挑出来的 top opportunities 里，**扣掉交易成本和 spread reversal 后只有 40% 仍为正收益**。
4. 更关键的是，**95% 的机会最后都要靠 forced exit 结束**，说明“等自然收敛”在实盘里并不可靠，持有时长本身就是生死线。

关键数据点（本地快检，2026-03-05 ~ 2026-03-25，BTC/ETH/SOL × Binance/Bybit/Hyperliquid，统一换算成 8h funding bps）：
1. 主流币大 venue 之间的 funding spread 其实很薄：`median abs spread` 大多只在 **0.24 ~ 0.65 bps/8h**。
2. `>= 2 bps/8h` 的 spread 在 BTC/ETH 基本是 **0%**；SOL 也只有 **3.2%** 左右的 8h bucket 够到这条线。
3. `>= 1 bps/8h` 的 episode 中位持续时间几乎都是 **8 小时（基本只活 1 个 funding bucket）**；按 **4 bps round-trip** 粗糙成本估算，除了 `SOL × Hyperliquid` 相关 pair 只有 **8.3%** 的 episode 勉强覆盖成本外，其余组合都是 **0%**。

## 3. 为什么和当前项目有关
- 这不是纯 filter，也不是纯解释型综述；它服务的是 **carry / relative value / stat-arb** 家族里非常明确的一条 raw alpha。
- 它对当前 short-cycle desk 的直接价值，不在于“给你一个更花的 funding 看板”，而在于：
  - 告诉你 **哪里更可能有 alpha**：更碎片化的 CEX/DEX、长尾币、次级 venue；
  - 告诉你 **哪里大概率没 alpha**：BTC/ETH 主流币 × 主流 venue 的核心组合，spread 往往薄到不够覆盖成本；
  - 告诉你 **该把 1m/3m/5m/15m 用在哪里**：不是伪装成逐根方向预测，而是用来盯 spread persistence、进出场切片、腿间滑点与强平/挤仓风险。

## 3.5 策略拆解（必填）
- 方向属性：relative value / carry / cross-venue stat-arb（market-neutral 优先）
- 基础 alpha：`cross_venue_funding_spread - trading_cost - hedge_slippage - spread_reversal_risk`
- regime：
  - `CEX ↔ DEX` 分层更重要，优先做高碎片化组合；
  - 主流币核心 venue 通常太有效，更多是监控，不一定值得下单；
  - 长尾 alt / 次级 venue 更可能有厚 spread，但运维/风控也更重。
- filter / veto：
  - 只有当 `abs(funding_spread)` 超过最小成本覆盖线才允许进场；
  - 只有当 spread 已持续 `>= N` 个短周期窗（如 3h / 2 个 1h funding tick / 2 个 8h bucket）才允许进场；
  - 若 CEX 领先腿已明显回归、DEX 只是滞后补价，避免追最后一口残差；
  - 主流币主流 venue 上若 spread 长期低于成本，直接 veto。
- risk / sizing / execution overlay：
  - 头寸按 venue tier、symbol liquidity、可对冲深度分层；
  - 设置 `max_hold`，不要假设 spread 一定自然回归；
  - 监控 funding 时钟差异、预估 funding 与实缴 funding 偏差；
  - 用 1m/3m/5m 切片对冲，减少四腿一次性冲击。

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- Binance USDⓈ-M `fundingRate`：公开 REST，历史 funding 可直接取。
- Bybit V5 `market/funding/history`：公开 REST。
- Hyperliquid `info` / `fundingHistory`：公开 API。
- 更新频率：
  - Binance / Bybit 常见是 8h funding；
  - Hyperliquid 为更高频 funding（本地快检汇总成 8h 等价口径）；
  - 可自然映射到 `1m / 3m / 5m / 15m` 的执行与 persistence 监控。

### 4.2 最小实验口径（先 1m/5m 盯 persistence，再按 funding 时钟结算）
- 标的：先从 `BTC/ETH/SOL` 起步，再扩到 `20~50` 个流动性可接受的 perp。
- venue 组合：`Binance × Bybit`、`Binance × Hyperliquid`、`Bybit × Hyperliquid`。
- 信号：
  - `spread_t = funding_high_t - funding_low_t`（统一换算成相同结算时长，例如 8h bps）；
  - `persist_t = spread` 是否已持续 `>= N` 个短周期窗口；
  - `entry_score = abs(spread_t) - cost_floor`。
- 交易规则（样例）：
  - entry：`abs(spread_t) >= max(q95, 2 bps/8h)` 且 `persist_t >= 2`；
  - direction：`long 低 funding venue + short 高 funding venue`；
  - exit：`abs(spread_t)` 回落到 `q50` 以下、或到达 `max_hold=1~3 funding cycles`、或腿间滑点/风控触发；
  - veto：若该 symbol 在最近 30 天的大 venue 组合里 `share(spread >= cost_floor) < 5%`，降级为观察池。
- 成本：至少做 `4 / 8 / 12 bps round-trip` 三档压力测试。
- 先看指标：`spread persistence`、`episode gross carry`、`post-cost win rate`、`forced-exit ratio`、`净 carry / max adverse excursion`。

## 5. 下一步怎么测（必须）
1. **把 universe 从 BTC/ETH/SOL 扩到 30~100 个 perp**：验证 paper 的厚 spread 是否主要来自长尾 symbol，而不是核心大币。  
2. **拆开做 `CEX-CEX / CEX-DEX / DEX-DEX` 三组**：别把 venue tier 混成一个池子。  
3. **给 spread persistence 建一个 ex-ante 生存模型**：只用最近 `1h/3h` 的 spread 斜率、成交额、OI、基差斜率，先回答“这口 spread 能活多久”。  
4. **把 funding spread 与执行成本联立**：尤其是四腿进出、maker/taker 切换、腿间不同步导致的残余 delta 风险。  
5. **若主流币主流 venue 继续太薄，就诚实降级**：把它们从 live 候选池移到监控/基准池，别浪费 desk 带宽。

## 6. 风险与保留意见
- 论文的 headline spread 很大，但来自 **更广的 venue-symbol 长尾截面**；主流币核心 venue 上不一定复制得出来。  
- funding 结算频率不一致，若直接横比而不统一到相同时间基准，很容易高估 edge。  
- 真实跨 venue 策略不只是一条 spread 序列，还包括：资金碎片、充值提币延迟、保证金占用、强平规则、DEX 预言机风险。  
- 若没有 duration gate，只盯 spread 大小，极容易在“看起来最肥”的地方接到最后一跳 reversal。  
- 本地快检只覆盖 21 天、3 个币、3 个 venue，结论更像 **负面筛查**：告诉我们主流大 venue 组合有多薄，而不是替代完整 alpha discovery。

## 7. 来源
1. **Zhivkov, P. (2026). _The Two-Tiered Structure of Cryptocurrency Funding Rate Markets_. Mathematics, 14(2), 346.**  
   - Venue: Mathematics (MDPI)  
   - DOI: https://doi.org/10.3390/math14020346  
   - Readable URL: https://doi.org/10.3390/math14020346  
   - Repo URL: N/A
2. **Binance Developers. _USDⓈ-M Futures API: Get Funding Rate History_.**  
   - Venue: Official API Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History  
   - Repo URL: N/A
3. **Bybit. _V5 Market API: Get Funding Rate History_.**  
   - Venue: Official API Docs  
   - DOI: N/A  
   - Readable URL: https://bybit-exchange.github.io/docs/v5/market/history-fund-rate  
   - Repo URL: N/A
4. **Hyperliquid. _Info endpoint / funding history_.**  
   - Venue: Official API  
   - DOI: N/A  
   - Readable URL: https://api.hyperliquid.xyz/info  
   - Repo URL: N/A

## 8. 本地复现产物
- `reports/artifacts/quant_digests/2026-03-25_funding_tier_duration_gate/summary.csv`
- `reports/artifacts/quant_digests/2026-03-25_funding_tier_duration_gate/episodes_ge_1bps.csv`
- `reports/artifacts/quant_digests/2026-03-25_funding_tier_duration_gate/meta.json`
