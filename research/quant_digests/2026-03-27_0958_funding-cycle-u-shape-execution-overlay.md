# 别把 perp funding 时钟只当结算提醒：这篇 2025 working paper 更该先落地的是「8h funding-cycle U-shape」execution overlay
- 时间：2026-03-27 09:58 UTC
- 类型：论文
- 主题类型：overlay
- 基础 alpha：服务 `funding/basis carry`、`pairs/stat-arb`、`BTC→ALT lead-lag / event beta` 这些本来就想交易的 raw alpha；它本身**不是**独立 raw alpha，而是告诉我们**哪些 funding-cycle 切片更贵、更吵、更该 size-down / 延后进场**。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：overlay/execution/funding-cycle/liquidity/market-quality/perpetual/spot-impact/size-down/execution-veto/binance/crypto/15m/5m/paper/external-data
- 证据类型：working paper / 学校摘要 + Binance Futures 公共数据最小快检

## 1. 这次看了什么
这次主线看的是 Artem Streltsov、Qihong Ruan 的 working paper 线索：**Perpetual Price Discovery and Crypto Market Quality**（SSRN DOI 可得），以及 Cornell 对同一研究脉络的摘要文章 **Perpetual Futures Contracts and Cryptocurrency Market Quality: Insights from Emerging Markets**。

这条材料对 desk 最有价值的，不是再发明一个“funding 前后必涨跌”的主信号，而是给出一句更实用的话：**perp 的 8 小时 funding 机制会把 spot / perp 的交易活跃度与交易成本一起拉成 funding-cycle 内的 U 型结构**。换句话说，很多 raw alpha 不是死在没方向，而是死在**你偏偏挑了最挤、最贵、最容易被 noise 吞掉的 cycle 边缘去下手**。

## 2. 核心结论
- **先把话说清楚：这不是独立 raw alpha。**
  - base alpha 若要硬说，就是 `funding/basis carry`、`short-horizon stat-arb`、`event beta continuation/reversal` 这些原本就存在的 raw alpha。
  - 这篇材料真正提供的是 **execution / sizing overlay**：告诉你 funding-cycle 的哪些时间片更像“高噪音、高冲击、高交易成本区”。
- Cornell 摘要对作者结果的概括很明确：
  - perpetual 的 **8 小时 funding cycle** 可以当自然实验；
  - **trading activity** 和 **bid-ask spreads** 在每个 cycle 内都呈 **U-shaped pattern**；
  - 这个形态不只在 perp，也会传到现货端，说明 perp 不是被动跟随，而是在主动改写市场微观结构。
- 这对 short-cycle desk 的含义很直接：
  - 同一个 raw alpha，放在 funding-cycle 中段做，和放在 cycle 边缘做，**成交成本、滑点容忍度、信号污染程度** 不是一回事；
  - 如果策略本来 edge 就薄（例如 funding carry、basis 回归、多腿 stat-arb），那么 cycle 边缘的额外噪音，足以把“看起来有 edge”打成“实盘不赚钱”。

## 3. 为什么和当前项目有关
- 当前 desk 已经在积累几类会被 execution 明显影响的方向：
  - `funding / basis / carry`
  - `pairs / stat-arb / spread MR`
  - `BTC shock → alt lag` 这类事件驱动 beta 交易
- 这些方向共同的问题不是“有没有信号”而已，而是：
  - 什么时候做最容易被 funding 边界的拥挤流打坏；
  - 什么时候应该降杠杆、缩持仓、放宽确认、或干脆 veto。
- 所以这条 intake 虽然不是 raw alpha 本体，但它能同时服务 **至少 3 类** 已在池中的 raw alpha，边际价值是实打实的。

## 3.5 策略拆解（必填）
- 方向属性：执行层 / 风控层 overlay
- 基础 alpha：
  - `funding/basis carry`：想吃 funding / basis 回归，但不想在最贵的 cycle 边缘开腿；
  - `pairs/stat-arb`：想做 spread 收敛，但不想在最吵的窗口被瞬时冲击打穿；
  - `BTC→ALT / market beta`：想做短时延续或回归，但不想把边界噪音误判成趋势确认。
- regime：优先用于 `1m/3m/5m/15m` 的 perp 策略，特别是 **薄 edge、高换手、多腿、需要 maker 质量** 的分支。
- filter / veto：funding-cycle 边缘（例如结算前后若干个 `5m/15m` slice）默认降低优先级，除非信号强度明显高于平时。
- risk / sizing / execution overlay：
  - cycle 边缘 `size-down`
  - 多腿策略改成分批入场
  - maker-only / post-only 优先
  - 跨 boundary 的持仓允许，但**新开仓**更谨慎

## 4. 可复刻的最小实验
- **研究假设**：perp 的 funding-cycle 边缘，不一定提供方向 edge，但更可能抬高交易活跃度、波动代理和隐含执行成本；因此更适合做 `execution veto / size-down`，而不是默认做主信号。
- **数据源**：Binance Futures 公共 `15m klines`（OHLCV、quote volume、trade count、taker buy volume）；完全公开可拿。
- **最小口径**：`BTC/ETH/SOL/XRP/DOGE/BNB` 六个主流 perp，样本 `2026-01-01 ~ 2026-03-27`；按 UTC `00/08/16` funding 边界，把每个 `15m` bar 映射到 `8h cycle` 内的 `slot 0~31`。
- **代理指标**：
  - `range_bps = (high/low - 1) * 1e4`
  - `quote_volume`
  - `trade_count`
  - 方向本身只看均值，不把它误包装成主 alpha
- **我这轮快检结果**：
  - cycle **边缘 8 个 15m slot**（`0~3` 与 `28~31`）的平均 `range` 约 **55.0 bps**；
  - cycle **中段 16 个 15m slot**（`8~23`）的平均 `range` 约 **45.5 bps**；
  - 也就是边缘的波动代理大约比中段 **高 20.9%**；
  - 边缘的平均 `quote volume` 约 **64.2M**，中段约 **46.3M**，高出约 **38.8%**；
  - 但边缘和中段的平均收益方向差别很小（约 **-0.12 bps vs -0.24 bps**），说明 **边缘更像成本 / 冲击问题，而不是稳定方向问题**。
- **desk 化解释**：
  - 若一个策略主要靠很薄的 `3~10 bps` 单次 edge 活着，这类 `range + volume` 的边界抬升，足以把它从“纸面可做”打成“实盘磨损过大”；
  - 反过来，若是极强事件驱动信号，cycle 边缘也许还能做，但应该 `size-down`，而不是照常下满。

## 5. 可以怎么直接落成完整策略 / 规则
把它先当 **共享 execution overlay**，不要上来就神化成新 alpha：

1. **适用对象**
   - 所有 `1m/3m/5m/15m` perp 策略；优先级最高的是：
     - funding / basis carry
     - pairs / stat-arb
     - lead-lag / beta 跟随

2. **entry / veto**
   - 若拟开仓时间落在 funding-cycle 边缘（例如 boundary 前后 `30~60m`），默认先记为 `yellow/red zone`；
   - 只有当原始信号分数高于平时阈值（例如 z-score / rank / classifier score 提升一个档位）才允许新开仓。

3. **sizing**
   - `green zone`（cycle 中段）用基准仓位；
   - `yellow zone`（边缘前后较近）仓位打 `0.5x~0.7x`；
   - `red zone`（边界最挤的几个 slice）默认 `0~0.3x`，或干脆不开新仓。

4. **execution**
   - 多腿策略优先 maker / post-only；
   - 新开仓尽量别把所有腿都压在同一个 boundary slice；
   - 若一定要跨 boundary 开仓，至少把第一腿和第二腿拆开，避免同时吃最差流动性。

5. **risk / exit**
   - 已有仓位可以跨 boundary 持有，但止损不要因为边界噪音过紧；
   - cycle 边缘更适合 `减仓 / 锁盈 / 降杠杆`，不适合把薄 edge 策略开到最满。

## 6. 风险与边界
- 论文与学校摘要强调的是 **market quality / microstructure**，不是“某个 funding 时刻必涨跌”。
- 我这轮快检用的是 `kline` 代理，不是真正的 order-book spread；因此它更像 **执行粗筛**，不是最终成本模型。
- 不同 venue、币种、maker/taker 费率、VIP 等级，对 overlay 强度会有明显影响；Binance 主流币结果不能直接外推到所有交易所与长尾币。
- 如果策略 edge 很厚（例如极强新闻事件、链上冲击、清算踩踏后反身性反转），边界时段未必需要 veto；这时应该 `size-down`，不是机械不做。

## 7. 下一步怎么测
1. **把 funding-cycle slot 写进所有回测器**：给每笔交易打上 `slot_in_cycle` 标签，先看 edge 是否在边缘显著衰减。
2. **做 maker/taker 成本分层**：同一策略分别在 `green/yellow/red zone` 下测净值，确认它究竟是“信号失效”还是“成本吃掉”。
3. **升级微观代理**：从 `kline` 升到 `bookTicker / depth / premiumIndex`，直接看 spread、冲击与 mark-index 偏离。
4. **优先连接 3 条现有主线**：
   - `funding carry`
   - `basis dislocation mean reversion`
   - `BTC→ALT delayed follow-through`
   看 overlay 是否稳定提升净值 / 降低回撤，而不是只改善纸面 hit-rate。

## 8. 来源
- Streltsov, A.; Ruan, Q. (working paper / SSRN). *Perpetual Price Discovery and Crypto Market Quality*. DOI: `10.2139/ssrn.4218907`
- DOI URL: https://doi.org/10.2139/ssrn.4218907
- Readable summary: https://business.cornell.edu/article/2025/02/perpetual-futures-contracts-and-cryptocurrency/
- AFA / conference abstract page: https://afajof.org/management/viewp.php?n=169764
- Repo URL：未见官方 repo

## 9. 本地产物
- 快检目录：`reports/artifacts/quant_digests/perp_funding_cycle_overlay_20260327/`
- 关键文件：
  - `funding_cycle_slot_stats_15m.csv`
  - `summary.json`
