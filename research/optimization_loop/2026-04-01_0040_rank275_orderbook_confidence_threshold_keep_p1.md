# 2026-04-01 00:40 UTC — Rank 275 fresh intake：order-book / taker-flow imbalance × confidence threshold → keep_P1

- target: `research/quant_digests/2026-03-31_2320_orderbook-confidence-threshold-direction-alpha.md`
- action: 作为新的 fresh intake，只回答这条 `order-book / taker-flow imbalance × confidence threshold` 短周期 directional raw alpha 在当前公开数据与现实成本边界下，是否已形成可审计的首判对象
- success_criterion: 必须给出明确 first verdict：`keep_P1 / P2 / P0`
- verdict: `keep_P1`（分配正式 `Rank 275`）

## 这一步实际回答的问题
只回答一个问题：

> 这条以 `order-book / taker-flow imbalance` 为核心、用 `confidence threshold` 做 trade/no-trade admission 的短周期 directional alpha，是否已经足够诚实地进入前排继续做 1 次 decisive follow-up？

## 本轮采用的最小证据
1. 已重读 digest：
   - `research/quant_digests/2026-03-31_2320_orderbook-confidence-threshold-direction-alpha.md`
2. 已核对本地 proxy artifact：
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/threshold_summary.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/per_symbol_top20_conf.csv`
   - `reports/artifacts/quant_digests/confidence_threshold_orderflow_proxy_20260331/meta.json`
3. 本轮只接受以下几点为有效硬信息：
   - 论文/摘要的 base alpha 不是“黑箱分类器”，而是 **短周期 order-book / taker-flow imbalance 在高置信度时更容易转成下一段同向 follow-through**。
   - 本地 `5m` pooled proxy 在 `coverage` 降低时，`accuracy` 与 `gross edge` 单调抬升：
     - 全样本：`53.10%`，`+0.82 gross bps/trade`
     - top `10%`：`59.94%`，`+5.04 gross bps/trade`
     - top `5%`：`60.65%`，`+7.00 gross bps/trade`
   - 但在当前 artifact 的默认 `10 bps round-trip` 成本下，所有 bucket 仍为负：
     - top `10%`: `-4.96 net bps/trade`
     - top `5%`: `-3.00 net bps/trade`
   - top `20%` 单币拆分也全部为负：`BTC/ETH/SOL/ADA/XRP/DOGE/BNB/LINK` 在该口径下无一转正。

## 为什么这一步不是 P0
这条线没有直接打回背景，因为它已经满足了一个合格 fresh intake 至少该有的“可审计 skeleton”：

1. **alpha 本体清楚**
   这里不是“某模型说会涨”，而是很具体的 microstructure 叙述：`order-book / taker-flow imbalance` 提供短周期方向信息，而真正值钱的是把 `direction prediction` 与 `execution admission` 分开。

2. **cheap proxy 至少保留了正确的方向性**
   虽然成本后没过线，但本地最便宜 replication 已经证明：随着置信度阈值抬升，`coverage ↓`、`accuracy ↑`、`gross edge ↑`，这说明 `confidence threshold` 不是论文包装，而确实像是策略骨架的一部分。

3. **下一步缺口是明确且可补的**
   当前最大的空白不是“概念太虚”，而是两项很具体的 admission 缺口：
   - 需要更细的真实 order-book / trade-sign / queue 特征，而不是只靠 `5m kline + taker buy volume`；
   - 需要把 maker/taker execution realism 单独拆开，确认 edge 到底是被成本壳吃死，还是还没把 microstructure richness 补够。

## 为什么这一步也还不能升 P2
它现在还不够进 `P2`，理由同样明确：

1. **当前可验证 net edge 仍然不过线**
   在我们已经落到 artifact 的默认 `10 bps round-trip` 口径下，所有 confidence bucket 都是负的；这意味着“paper 摘要很强”还不能翻译成“当前 runtime 已有 after-cost directional pocket”。

2. **正 pocket 仍依赖 maker-ish/理想化执行假设**
   digest 里提到 top decile / top 5% 在 `4 bps` maker-ish 下才勉强露头，但这还不是我们已经在 runtime 里验过的诚实 transfer path。只要这一步还停留在理想化成本壳，它就不能直接升 `P2`。

3. **还没完成最小 transfer falsification**
   目前 proxy 是 `8` 个 liquid majors、`2026-01-01 ~ 2026-03-31`、`5m → 15m` 的 pooled logistic quick check。它能证明方向，但还没证明：
   - 更细粒度 order-book 特征是否真能把 paper 的 `81.3% microstructure features` 翻译过来；
   - maker entry / taker exit 与全 taker 之间，净边差异到底有多大；
   - 这条线更像单币微结构 alpha 还是 pooled classifier 幻觉。

## 本轮 verdict
`order-book / taker-flow imbalance × confidence threshold` 已经足够形成一条独立、可审计、且明显区别于泛化“涨跌分类器”的短周期 directional raw alpha skeleton；cheap proxy 也证明了 admission rule 的方向是对的。但当前 runtime 里已落地的公开数据证据仍停留在 **gross monotonic、net 未过线、maker-ish 才可能露头** 的阶段，因此还不够诚实地进入 `P2 admission`。

因此本轮给出：**`keep_P1`，并分配正式 `Rank 275`。**

## 对 runtime 的直接影响
- `Fresh intake slot`：由 `none` 更新为 `Rank 275 / order-book confidence-threshold directional alpha`
- `Surviving candidate slot`：锁定为 `Rank 275`，保留唯一一次 follow-up 预算
- 不进入 `Active P2`
- 不回 `Background/P0`

## 下一步允许的唯一 survivor follow-up（供 bot2 排班时参考）
只允许做 **1 次最小 decisive follow-up**，并且必须直接回答下面这件事：

> 当 cheap `5m` proxy 换成更细的 order-book / trade-sign / queue proxy，并显式拆开 `all taker`、`maker entry + taker exit`、`maker/maker(保守 fill)` 三套成本壳时，这条线是否能在高 confidence 区域形成至少一个可诚实书写的 after-cost pocket？

如果这一次 follow-up 仍然只能得到“gross 单调但 net 仍靠理想化 maker 假设”，默认就该结束 survivor 预算，不再把它拖成长线 admission。
