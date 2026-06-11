# 别把这份 2026 Deribit options scanner 只当可视化页面：对 desk 更该先测的是「same-expiry butterfly / convexity violation」事件型 raw alpha，但当前 live snapshot 极干净
- 时间：2026-03-30 15:45 UTC
- 类型：GitHub / 论文地基 / 公共 API 快检
- 主题类型：raw alpha
- 基础 alpha：同到期 BTC options 链上，若中间 strike 的 bid 明显高于两翼 ask 线性插值，或整条链存在可收取正初始现金流且到期非负 payoff 的静态无套利违例，则做 same-expiry 凸性修复
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/options/relative-value/stat-arb/butterfly/convexity/static-arbitrage/same-expiry/deribit/btc/1m/3m/5m/15m/repo/public-data/cost
- 证据类型：工程经验 + 论文地基 + 公共数据快检

## 1. 这次看了什么
看了 Jasper Chan 2026 的 `BTC-Options-Arbitrage-Detector` 仓库：它把 Deribit BTC 期权同到期链转成一个 LP，最大化初始权利金收入，同时要求 `S=0`、全部 strike 节点、以及右端斜率下 payoff 都非负。本质是在扫 box / butterfly / convexity 一类 static-arb。对我们更值得先拿出来单测的，不是 UI，而是**同到期 butterfly / convexity 违例是否能在 1m~15m 维持到足够成交**。

## 2. 核心结论
- 这篇东西的 **base alpha** 很清楚：**same-expiry 凸性违例回补**，不是 filter，也不是解释层。
- 仓库默认参数已经很 desk-friendly：`minVolume=10`、`maxSpreadPct=20`、1 分钟刷新、可加 fee toggle（30 bps × 0.001? 代码里实际是 `0.0003`）。
- 我用 Deribit BTC 公共 `get_book_summary_by_currency` 做了 live sanity check：全链 **759** 个合约里，满足 `vol>=10 & spread<=20%` 的有 **245** 个、覆盖 **12** 个 expiry；按 repo 的 LP 口径，**0 fee 下也没有扫到正初始现金流 static-arb**。
- 我再把筛选放宽到近乎“不过滤脏链”的级别（最多 **760** 个合约，`spread<=100%`），LP 结果仍是 **0 个** 可执行同到期 static-arb。说明当前 Deribit BTC 链在静态无套利上相当干净。
- 所以它更像**低频稀有事件扫描器**，不是 always-on 收租策略；若要进 desk，必须把它做成“有 edge 才触发”的事件队列，而不是常驻占资。

## 3. 为什么和当前项目有关
这和 `momentum` 主线的关系，不是因为它会稳定产出高频单边收益，而是因为它能补一块目前较少的 **options relative-value / stat-arb raw alpha 素材**：规则清楚、公共数据可拿、成本口径能快速加进去，而且一旦真出现违例，entry/exit/risk 都比主观 discretionary 更容易写死。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / 事件驱动
- 基础 alpha：same-expiry butterfly / convexity static-arb
- regime：仅在同到期链完整、盘口未坏死、临近到期但仍可成交时启用
- filter / veto：最小成交量、最大价差、最少连续两帧仍存在、edge 必须超过 fee+slippage+hysteresis
- risk / sizing / execution overlay：限制 3~4 腿组合；按最差腿深度定 size；若任一腿 spread 扩张、盘口消失或 edge 回落到阈值下方则立刻撤退

## 4. 可复刻的最小实验
- 研究假设：同到期 butterfly / convexity 违例在 BTC options 上虽少见，但一旦出现，短时间内会向无套利曲面回归。
- 数据源：Deribit 公共 REST `public/get_book_summary_by_currency?currency=BTC&kind=option`；公开可得；分钟级拉取即可，必要时补 `get_order_book` 做腿级深度。
- 最小口径：每分钟抓一帧，按 expiry 分组；先跑 repo 同款 LP，再补一个更轻的“三点 butterfly 可执行不等式”扫描；观察事件频率、持续时长、edge 衰减。
- 交易规则：`entry`= LP 正利润或三点 butterfly 正 credit 且连续 2 帧存在；`exit`= edge 回到 0 附近、任一腿失去流动性、或距到期不足 30 分钟；`sizing`= 不超过最弱腿可成交量的 25%~33%；`cost`= 手续费 + 半个 spread / 一个 spread / 1.5 个 spread 三档。
- first verdict：先看最近 7~14 天分钟快照里，事件数是否足够、平均存活时间是否 > 2 帧、成本后是否仍有正 edge；若长期为 0，就把它降级为“尾部机会报警器”，而不是主策略。

## 5. 风险与误读
- 最大风险不是模型错，而是**Quote 看起来有洞，真实成交根本吃不到**。
- Deribit 盘口很可能已经足够有效，导致 raw alpha 频率过低。
- inverse / coin-margined 期权的 premium、手续费、腿间同步成交与保证金占用都要统一口径，否则会把假 edge 当真钱。

## 6. 来源与可复用点
1. **Jasper Chan (2026), _BTC Options Arbitrage Detector_, GitHub repo**  
   - Repo URL: https://github.com/JasperChan-24/BTC-Options-Arbitrage-Detector  
   - Readable URL: https://github.com/JasperChan-24/BTC-Options-Arbitrage-Detector/blob/main/README.md  
   - 可复用点：`src/services/arbitrageService.ts` 的 LP 约束写法、`deribitService.ts` 的公开链抓取、默认流动性过滤参数。
2. **Paul Cousot (2005), _A note on sufficient conditions for no arbitrage_, Finance Research Letters**  
   - DOI: https://doi.org/10.1016/j.frl.2005.04.005  
   - Readable URL: https://doi.org/10.1016/j.frl.2005.04.005  
   - 可复用点：用 shape restriction（单调 / 凸性）理解 butterfly arbitrage 的充分条件。
3. **Jim Gatheral, Antoine Jacquier (2014), _Arbitrage-free SVI volatility surfaces_, Quantitative Finance**  
   - DOI: https://doi.org/10.1080/14697688.2013.819986  
   - Readable URL: https://doi.org/10.1080/14697688.2013.819986  
   - 可复用点：提醒我们 static-arb 最终要落到整条曲面的一致性，而不只是单个 strike 对。

## 7. 下一步怎么测
先别做大而全回测，直接做一个 **Deribit BTC options static-arb event logger**：连续抓 7~14 天分钟快照，记录每次 LP edge、持续时长、最弱腿深度、费用后三档净 edge；若事件稀少但偶发净边明显，再进入 paper trading；若长期全 0，就把这条线收编成 options 风险雷达，不再占 bot7 主 intake。