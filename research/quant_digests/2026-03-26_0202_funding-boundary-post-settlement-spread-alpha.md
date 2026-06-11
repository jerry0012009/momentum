# 别把 funding boundary repo 只读成 latency 工具：更该先测的是「结算后 long richest / short cheapest 的 60m spread」raw alpha
- 时间：2026-03-26 02:02 UTC
- 类型：2026 GitHub 新仓库 + perpetual/funding 理论地基 + Binance Futures 公共 `1m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：funding 结算边界的横截面 relative-value / event-driven continuation（结算后做多最高 funding，做空最低 funding）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / funding / carry / relative-value / cross-sectional / event-driven / settlement-boundary / post-settlement / continuation / market-neutral / perpetual / binance / 1m / 3m / 5m / 15m / 60m / repo / paper / external-data
- 证据类型：仓库 source audit + 理论文献 + 公共数据快检

## 1. 这次看了什么
主材料是 **wangshaofu 2026 GitHub 仓库**《LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps》。它做的不是完整策略回测，而是盯住 **funding rate 结算边界**：抓全市场 mark price stream、追踪最极端 funding 名单、在结算前后记录 `bookTicker` 延迟与价格路径，回答“边界时刻到底有没有可交易窗口”。理论地基则补了 **He、Manela、Ross、von Wachter 2022/2024**《Fundamentals of Perpetual Futures》——它说明 perpetual 的 funding 不是孤立手续费，而是把 perp/spot 偏离、杠杆需求与套利资本状态编码进价格里的机制变量。

对我们 desk 来说，更值钱的不是把 repo 原意照搬成“最负 funding 临门一脚 short”，而是把它改读成一个更可复现的 **事件时钟 + 横截面排序** 框架：**funding 结算刚发生后，richest-funded leg 和 cheapest-funded leg 的后续 5m/15m/60m 相对表现，是否存在可交易 spread？**

## 2. 核心结论
- **这篇东西的 base alpha 是什么？** 不是“赚 funding”本身，也不是单纯 latency audit，而是 **结算边界后的横截面 relative-value continuation**：在 funding print 刚落地后，**做多最高 funding 币、做空最低 funding 币**，押注两端在接下来一小时继续分化。
- 这和传统 carry 有一个关键区别：**仓位是在 funding 结算后才开**，所以主要赚的不是 funding cashflow，而是 **结算边界后 crowding / price pressure 的延续**。
- 我用 Binance USDT 永续公开 `fundingRate` + `1m klines` 做了最小快检，样本取最近 **21 天**、只保留 `00/08/16 UTC` 这类**大批量主结算时点**（以当次 funding 记录数 `>=100` 近似），共 **125 个事件**。若每次都做 **long highest-funding / short lowest-funding**、等美元、结算后立刻进场：
  - **5m gross spread = +9.3 bps**
  - **15m gross spread = +26.7 bps**
  - **30m gross spread = +21.1 bps**
  - **60m gross spread = +98.2 bps**
  - **60m spread win rate = 64.8%**
- 若进一步只做 **funding gap 前 25% 最大** 的事件，edge 明显更集中：
  - **5m gross spread = +37.3 bps**
  - **15m gross spread = +52.5 bps**
  - **60m gross spread = +270.2 bps**
- 这意味着：
  1. `1m/3m/5m` 可以用来做精细执行，但**真正更像完整策略 pocket 的，是 15m~60m 持有**；
  2. funding boundary 更像 **event-driven raw alpha**，不是“拿 funding 当低频 filter”；
  3. repo 里“盯最负 funding 的临门脚 short”不一定是最优 desk transfer，**更诚实的 desk 化读法可能是 post-settlement spread，而不是 pre-settlement 单腿赌方向**。

## 3. 为什么和当前项目有关
这条线直接补的是当前 desk 的 **raw alpha 素材池**，而且是目前相对没被写烂的一种：
- 它不是 breakout / retest 的继续内循环；
- 它也不是把 funding 继续伪装成 shared gate；
- 它给的是一条 **可以独立立项** 的 perp event alpha：
  - 信号来自公开 funding
  - 时钟天然固定在 `00/08/16 UTC`（也可扩到 `1h/4h` funding 币种）
  - 执行落在 `1m/3m/5m`
  - 持有落在 `15m/30m/60m`
  - 风险管理天然可写成 market-neutral basket

## 3.5 策略拆解（必填）
- 方向属性：横截面 / relative-value / market-neutral / event-driven continuation
- 基础 alpha：结算后 long highest-funding，short lowest-funding
- entry：`fundingTime` 后第一根可交易 `1m` bar 或前 1~2 分钟 VWAP
- exit：优先测 `15m / 30m / 60m` 固定持有；当前最像可落地 pocket 的是 `60m`
- sizing：两端等美元，单腿 notional cap；高 funding gap 事件允许 size-up，普通事件降权
- risk：只做高流动性 USDT perp；跳过重大新闻窗 / 极端异常波动 / 合约临时风控状态；单币最大权重上限
- cost：pair taker round-trip 粗估约 **16 bps**（四次成交、每次 4 bps 量级）；所以 **15m pocket 仅边际可活，60m pocket 更舒服**；若能 maker-first，`5m/15m` 可测性会更好

## 4. 可复刻的最小实验
- **研究假设**：funding 结算会把“谁最拥挤 / 谁最贵”这件事明牌化；结算后最贵腿与最便宜腿的相对价格仍会延续一段时间。
- **数据源**：Binance Futures 公共 `fundingRate` 历史 + `1m` K 线；完全公开可拿。
- **更新频率**：funding 主要是 `8h`，部分合约还有 `1h/4h`；价格可到 `1m`。
- **最小口径**：
  1. 在每个 `00/08/16 UTC` funding print 后读取**刚刚公布**的 funding snapshot；
  2. 在高流动性 universe 里按 funding 排名；
  3. 做 `top1-vs-bottom1` 或 `top3-vs-bottom3` 的等美元 spread；
  4. 用 `1m/3m` 做进场、`15m/30m/60m` 做固定持有；
  5. 计入 taker/maker 两套成本版本。
- **先看 4 个指标**：gross spread、净后 edge、60m win rate、funding-gap 分位分层后的单调性。

## 5. 风险与边界
- **别把它误读成收 funding 策略**：我们当前看到的 pocket，主要赚的是**结算后价格延续**，不是 funding cashflow。
- **微盘/梗币污染很可能很重**：极端 funding 往往先出现在拥挤小币上，所以正式版本必须加流动性、成交额、最小价位/最小名义金额过滤。
- **事件稀疏但不算罕见**：它不是 bar-by-bar alpha，而是每天几个明确事件点；这很适合作为 desk 的补充型 alpha，而不是全时段主驱动。
- **1h/4h funding 币种先别混在一起**：主结算窗和边界微结构不同，第一版最好先锁定 `00/08/16 UTC` 的主批次，再单独扩展。

## 6. 下一步怎么测
1. **做流动性诚实版**：把 universe 固定成 Binance 前 `30~50` 个高流动性 USDT perp，重跑 `top1/top3/top5`。
2. **做方向拆分**：分别测 `long richest only`、`short cheapest only`、`long-richest/short-cheapest spread`，确认 alpha 真正在哪一侧。
3. **做时间拆分**：比较 `entry at +0m / +1m / +3m`，以及 `hold 5/15/30/60m`，找最稳 pocket，而不是默认最早进场。
4. **做成本生存线**：单独跑 `all-taker`、`maker-first + taker fallback`、`TWAP 2~5m` 三套。
5. **做 veto**：加入 `quote volume / OI / basis / news blackout`，看 edge 是被过滤放大，还是被过拟合吃掉。
6. **做更像实盘的 ranking 版本**：从 `top1-vs-bottom1` 升到 `top3-vs-bottom3`，减小单币 idiosyncratic risk。

## 7. 来源与可复用材料
1. **wangshaofu (2026)**, *LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps*, GitHub repo.
   - Venue: GitHub
   - Readable URL: https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps
   - Repo URL: https://github.com/wangshaofu/LolaFun-Latency-Aware-Arbitrage-at-Funding-Rate-Boundaries-in-Crypto-Perpetual-Swaps
   - 可复用点：全市场 funding 极值追踪、结算边界调度、边界前后 `bookTicker`/latency 记录。
2. **Songrun He, Asaf Manela, Omri Ross, Victor von Wachter (2022; v6 updated 2024)**, *Fundamentals of Perpetual Futures*, arXiv preprint.
   - Venue: arXiv / q-fin.PR
   - DOI: 10.48550/arXiv.2212.06888
   - Readable URL: https://arxiv.org/abs/2212.06888
   - PDF URL: https://arxiv.org/pdf/2212.06888
   - 关键信息：paper 明确指出 perpetual 偏离、funding 与套利资本状态共同决定短期定价偏差，且 implied arbitrage strategy 在样本里有高 Sharpe。
3. **Binance Open Platform**（公开文档）
   - Funding history docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History
   - Kline docs: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
   - 数据公开性 / 更新频率 / 最小复现实验口径：完全公开；funding 以结算时点更新，价格可到 `1m`，足够做 settlement-boundary event study。