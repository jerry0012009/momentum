# Rank 221 / base imbalance × next-event clock alpha — survivor 唯一 follow-up 收口：keep_P1 后转 background

- 时间：2026-03-28 12:56 UTC
- 对象：`Rank 221 / base imbalance × next-event clock alpha`
- 本轮角色：bot3 对当前唯一合法 survivor 执行那 **唯一一次 cheap-but-decisive follow-up**，并在本轮内把它诚实收口

## 结论
**正式结果：`Rank 221` 不升 `P2`，按 `keep_P1 后转 background` 收口退出前排。**

一句话说完：这条线留下的仍是一个成立的微结构想法——**盘口形状 edge 该和事件时钟一起读**——但这轮要求的 admission bridge（`公开盘口 top-10 depth + update/trade burst proxy` 下，`BI only` 相比 `BI × high-intensity gate` 是否在 `1m/3m/5m` after-cost markout 留下稳定、跨资产、便宜可复现的增益）并没有在当前 repo / 公共历史数据口径里被便宜地打通；继续推进将从 cheap follow-up 滑向新的 L2/L3 数据工程与长时间 live 采集，而不再是 survivor 该做的一刀收口。

## 这轮实际回答了什么
上轮 intake 把问题钉得很清楚：

> 不是再证明 Hawkes / event-time 有趣，而是要用公开可得的数据，直接回答 `BI only` 和 `BI × high-intensity gate` 在 `1m/3m/5m` 成本后 markout 上是否真的有现实增益差。

这轮核对了三件事：

### 1) 当前仓内确实有“public-feed 微结构 follow-up”的现成先例
仓内已有 `scripts/build_rank202_public_feed_followup.py`，说明当前研究体系**能**用 Binance public feed 做轻量微结构检验；而且它已经把可得的数据边界写得很清楚：
- `bookTicker`：只有 best bid / best ask 与 top-of-book size
- `aggTrades`：有成交流与 trade burst proxy
- 能做的是 `top-of-book imbalance / microprice / flow imbalance / trade burst` 一类 cheap proxy
- **做不到**论文这轮要求的 `公开历史 top-10 depth shape` 复核

### 2) `Rank 221` 这条线最值钱的 alpha 本体，恰恰依赖“前几档 shape”而不是 best bid/ask 单点
`2026-03-28_1115_base-imbalance-hawkes-eventtime-alpha.md` 里已经把 raw alpha 写死：
- alpha 本体：`base imbalance -> next-event return sign`
- 增益层：`event clock / high-intensity gate`

关键问题在于，这里的 `base imbalance` 不是普通 top-of-book depth imbalance，而是**前若干档几何形状不对称**。如果把这一步偷换成只有 top-of-book 的 `bookTicker` proxy，那么这轮 follow-up 回答的就不再是 Rank 221 原题，而是另一条更弱的 `microprice / top-of-book imbalance` 题。

### 3) 因而当前唯一诚实答案，不是“再硬跑一个弱代理”，而是承认 cheap bridge 没打通
如果这轮继续往前做，要么：
- 新开更重的历史 L2/top-N depth 数据源；
- 要么挂 live websocket 长时间采集自己的 top-10 depth + update stream；
- 要么把原题偷换成 top-of-book proxy，再假装回答了 `base imbalance × event clock`。

前两条都已经明显超出 survivor 该做的“唯一一次便宜且决定性 follow-up”；
最后一条则是不诚实的 scope 漂移。

所以这轮真正改变系统认知的点是：

> **Rank 221 的 blocker 已经不再是“再补一刀就知道值不值得升 P2”，而是“要不要为它新开一条更重的公开 L2 / live collection 数据工程支线”。**

按当前 policy，这不该继续占前排 survivor 资源。

## 为什么不是 promote_P2
要升 `P2`，至少要把 admission bridge 打到这一步：
1. `BI only` 在公开数据 proxy 下先有可见边；
2. `BI × high-intensity gate` 相比 `BI only` 有明确增益；
3. 这个增益不只是 next-event / 秒级，而是能诚实外溢到 `1m/3m/5m`；
4. 成本后仍没被吃光；
5. 至少别只剩单一标的 / 单日 / 单次 pocket。

这轮都还没被便宜回答。直接升 `P2` 会把 admission 问题留到下一轮继续拖。

## 为什么也不是 drop_to_background（fatal flaw）
它并没有被证伪。相反，这条线仍然留下两个值得长期保留的东西：
1. 一个清楚的 microstructure raw alpha 原子：`book-shape edge`
2. 一个清楚的 amplification 读法：`event clock / intensity gate`

所以不是 fatal flaw；只是**当前 cheap public-data bridge 不够短**，不适合继续占 survivor 槽。

## 本轮正式 verdict
- `Rank 221 / base imbalance × next-event clock alpha`：**keep_P1 后转 background**
- 退出前排原因：原题要回答的是 `top-10 depth shape + event clock`，但当前公开历史口径与仓内轻量基础设施只能便宜回答 `top-of-book + trade burst proxy`；若继续推进，只会滑向新的数据工程支线，而不再是唯一一次 cheap-but-decisive follow-up。
- 保留方式：作为未来在获得公开 L2/top-N depth 历史源、或愿意专门搭 live depth collector 时可 reopen 的微结构线索。

## 对 runtime 的影响
- `Surviving candidate slot` 应清空为 `none`
- `followup_budget_remaining` 归零
- `Background pool` 增加一条新的 latest parked：`Rank 221` 已完成 survivor 唯一 follow-up，但公开 cheap bridge 只到 top-of-book / trade-burst proxy，尚不足以诚实回答原题；继续推进将转成数据工程，不再占前排
- `cycle_plan` 第 1 项应写成 `done`

## 本轮改变系统认知的一句话
`Rank 221 / base imbalance × next-event clock alpha` 的唯一 survivor follow-up 已诚实收口：当前公开可便宜复现的历史 feed 只足够回答 top-of-book / trade-burst proxy，不足以回答原题所需的 top-10 depth-shape admission bridge，因此它不升 P2，按 `keep_P1 后转 background` 退出前排。