# 2026-04-07 20:39 UTC — session VWAP σ-band fade first verdict：background / P0

## 本轮执行对象
- target: `research/quant_digests/2026-04-07_1902_session-vwap-sigma-fade-alpha.md`
- action: 判断 `session VWAP σ-band fade` 是否真提供了独立于既有 `VWAP mean-reversion / session-anchor fade / intraday overextension fade` 家族的新 raw alpha 主语
- verdict: `background / P0`

## 会改变系统认知的一句话结论
`session VWAP σ-band fade` 的可交易主语仍是老的 `session-anchored VWAP deviation mean-reversion`，当前新增主要只是把 entry/exit/fee 壳写得更完整，并没有把独立于既有 VWAP fade 家族的新 pocket、可迁移时钟边界或新的诚实执行约束压清，因此本轮不保留为新的前排对象，直接收口到 `background / P0`。

## 为什么这次不保留为 keep_P1
1. **独立 raw alpha 主语不够新。**
   - 当前 digest 的核心定义就是：`close - session VWAP` 的滚动 σ 偏离达到阈值后做 fade。
   - 这本质上仍是 `session-anchored VWAP deviation mean-reversion`，不是新的经济机制。
   - 和池内已出现过的 `VWAP deviation band`、`session VWAP reclaim/defense`、以及多条 `VWAP 作为日内锚点/确认线/偏离回归中线` 家族相比，这次更像同族实现的工程化重写，而不是新的 raw alpha intake。

2. **新增价值主要在工程壳，不在 alpha 本体。**
   - repo 确实把 `entry_std=1.5 / exit_std=0.2`、成本、冷却、kill switch 写得更完整；
   - 但这证明的是“它是个可直接回测/部署的实现样本”，不是“它拥有独立于旧 VWAP fade 家族的新 alpha 主语”。
   - 按当前 policy，fresh intake 首判要回答的是它是不是一个值得占用前排的新对象，而不是它写得是否工整。

3. **24/7 crypto 的 session 任意性仍是老问题，不是新增解决。**
   - digest 自己也承认：UTC 日切未必是最优 session，亚洲/欧洲/美盘切法都值得对照。
   - 这说明对象的关键敏感点仍是老的 `session anchor definition`，而不是一个已经压清的、跨时钟稳定的新 pocket。
   - 在没有给出“为什么这个 session 锚点比旧的 session VWAP / anchored VWAP 方案更独立、更诚实”的证据前，不适合再开一条新前排。

4. **与既有研究池的重叠度高。**
   - 早期已明确把 `VWAP deviation band + volatility filter` 读成结构偏厚、session anchoring 重、source intake 阶段就有过拟合风险的同族来源；
   - 也已有 `Rank 51 / session VWAP reclaim + breadth gate`、`Rank 58 / event-anchored VWAP` 等围绕 VWAP 锚点语义与 24/7 session 边界的前序记录；
   - 因此这次对象没有提供足够强的“为什么它不是旧族再包装”的分界线。

## 诚实收口理由
- 这不是说 `session VWAP fade` 永远不能赚钱；
- 而是说 **以当前 intake 口径**，它还不足以占用一个新的 `keep_P1` 名额；
- 更诚实的处理是把它记为：`old VWAP fade family 的一份完整工程样本`，供以后需要实现细节时参考，而不是假装它是新的前排 alpha。

## 对 runtime 的直接影响
- `Fresh intake slot` 当前对象完成 first verdict，结果为 `background / P0`
- 不分配新 Rank
- 不触发 `Surviving candidate` / `Active P2` / `Paper launch queue` 迁移

## 相关旧记录（用于这次去重判断）
- `research/optimization_loop/2026-03-17_1806_rank40-ema-pullback-intake.md`
- `research/optimization_loop/2026-03-18_0845_rank51-vwap-source-intake.md`

## 本轮最小交付
- 内部日志已落盘
- runtime state 将同步写回 `docs/BOT2_BOT3_STATE.md`
- 因为产生了新的 first verdict，会刷新首页并发送中文邮件摘要
