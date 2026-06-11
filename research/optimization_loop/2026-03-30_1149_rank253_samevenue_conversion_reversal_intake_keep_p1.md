# Rank 253 intake — same-venue conversion / parity reversal 进入 P1

- 时间：2026-03-30 11:49 UTC
- 对象：Rank 253 / same-venue conversion / parity reversal
- 别名：`carry-adjusted same-venue conversion/reversal × parity gap hurdle`
- 来源摘要：`research/quant_digests/2026-03-30_1018_samevenue-conversion-reversal-parity-alpha.md`
- 本轮动作：fresh intake first verdict，只回答它是否形成独立前排对象
- 本轮结论：`keep_P1`

## 为什么这轮不直接回 background/P0
这条线不是泛 box spread、cross-venue arbitrage，或旧 options no-arb 家族的换壳，至少有 3 个不可省略的新边界：

1. **主语锁得足够窄：它交易的是同所、同到期、同执行价的 synthetic forward 偏离，而不是笼统的“期权贵/便宜”。**
   - repo 的核心不是讲理论，而是把 `synthetic_forward - theoretical_forward` 直接翻成 `conversion / reversal` 方向决策。
   - 这和泛 no-arb 解释型卡片不同；它从一开始就要求 `gap > hurdle` 才允许开仓，属于独立 raw alpha，不是解释标签。

2. **它的最小执行骨架已经完整到可单轮证伪。**
   - 入场：`gap_usd / gap_bps` 穿过三腿成本带
   - 诚实约束：先统一 inverse premium numeraire，再检查 quote age / top-of-book size / 同步性
   - 方向：`gap > hurdle -> conversion`，`gap < -hurdle -> reversal`
   - 出场：回到成本带内、或 `1m/3m/5m max_hold`、或任一腿报价失真
   这已经不是一句抽象“parity 会回归”，而是可以压成首轮实验的 trade-on / trade-off 状态机。

3. **它相对现有池子的新增层，不是收益夸口，而是 `same-venue executable parity` 这个对象边界。**
   - 当前素材池更偏 trend / funding / microstructure；这条线补的是 options relative-value / stat-arb。
   - 它的 admission 核心也不是“年化 box 利差”，而是公开快照里是否存在真实穿越 frictions 的 `same-venue` 偏离事件。

所以它值得作为新的前排对象进入 `P1`，而不是因为“options repo 看起来高级”就回 background，也不是因为机会稀薄就直接判死。机会稀薄只说明后续 follow-up 必须很诚实，不说明对象边界不存在。

## 为什么这轮也不直接升 P2
当前能确认的是**对象边界清楚、最小实验可写**，还不能确认**公开数据下是否稳定留下成本后 executable pocket**。

现有 digest 已经给出一个关键提醒：
- Deribit 公共快检里，最近到期 ATM 附近的 parity gap 只有约 `-1.15 bps of spot`，说明机会不是常驻宽边；
- 一旦 inverse premium 单位没统一、quote age 没筛、只看 mid 不看深度，就很容易把 stale quote 或单位错位误判成 alpha。

因此这轮最诚实的位置是 `keep_P1`：先承认对象值得前排审理，再把“公开快照下是否真的穿过成本带”留给唯一 survivor follow-up，而不是直接把 repo 里的理论壳子推成 `P2`。

## 单一 decisive blocker（供唯一 survivor follow-up 使用）
只追问一个问题：

> 在 `Deribit BTC` 最近 `7~14` 天的公开 snapshot 上，先把 inverse premium 统一成同一 USD numeraire，再叠加 `quote age / top-of-book size / 6~20bps friction ladder` 后，`same-venue conversion/reversal` 在 `1m/3m` 持有里是否仍留下可重复、成本后为正的 executable parity pocket？

允许的下一步 verdict 只有两个主方向：
- 若仍有成本后稳定 pocket：`promote_P2`
- 若主要来自单位错位、中价幻觉或 stale quote：`drop_to_background`

## 本轮写回 runtime 的一句话
`Rank 253 / same-venue conversion / parity reversal` 完成 fresh intake first verdict：它不是泛 box spread 或旧 options no-arb 家族换壳，而是把 `carry-adjusted same-venue conversion/reversal × parity gap hurdle` 直接写成 trade-on/trade-off 状态机；虽需先统一 inverse premium numeraire 并做 quote-age / 成本诚实校准，但对象边界与最小可证伪骨架已足够清楚，因此本轮给 `keep_P1`，进入唯一 survivor follow-up。
