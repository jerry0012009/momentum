# Binance 1m walk-forward Engle-Granger pairs intake — first verdict

- 时间：2026-04-04 09:52 UTC
- 对象：`research/quant_digests/2026-04-04_0641_binance-1m-walkforward-engle-granger-pairs-alpha.md`
- 轮次角色：bot3 自动执行
- 结论：`background/P0`

## 为什么这一步改变系统认知
这条材料并没有为当前系统提供一条独立于既有 pairs 主线的新前排 alpha lane。它真正新增的内容是把 `15d/5d walk-forward pair admission -> spread z-score trade -> live bridge` 这条工程链讲得更完整，但这条链本身已经被近期 pairs intake 与 `Rank 322` 的 admission 主线覆盖；而且文内自带证据仍停留在 shortlist / signal density / portability probe，缺少能直接证明 out-of-sample 两腿净收益的新证据。因此这轮 fresh intake 不分配新 Rank，直接收口到 `background/P0`。

## 本轮判断依据
### 1) 它补的是工程壳，不是新的 raw alpha lane
该 digest 的核心主张仍是：
- rolling Engle-Granger 扫描选 pair；
- `15d train / 5d test` 重估 `alpha/beta`；
- spread z-score 开平；
- 再把参数桥接到 live bot。

这比“静态一对 pair + 固定阈值”更完整，但仍属于当前系统已经明确吸收过的 `pairs admission shell`，不是新的方向性 / microstructure / event-clock lane。

### 2) 与现有前排/背景知识高度同构
近期系统已经有多条同族材料：
- `Rank 322` 已把 `major-coin pairs × 15m spread MR` 推进到过 `P2`，并完成过更长样本与 honesty 维度收口；
- 2026-04-01 的 `ADF+Johansen 双检验 × rolling beta spread z-score` intake 已明确把“更稳的 pair admission shell”写成可复用主线；
- 更早还有 plain-vanilla / percentile-entry / dynamic-cointegration / BTC-anchor transient pairs 等多张 pairs 卡。

所以这份 repo 的新增值主要是“又一份 walk-forward Engle-Granger 工程实现”，而不是带来一个此前系统没有覆盖的独立 hypothesis。

### 3) 文内证据不足以支撑 fresh intake 升到 `keep_P1`
该 digest 自己已经承认：
- `pairs_summary.csv` 不是可信的 OOS PnL 表，只更像 admission ranking；
- portability probe 主要给出 `|z|>=2` 事件密度、半衰期、持有 bars，而不是成本后两腿净收益；
- live 配置里 `risk_pct=0.35` 偏 demo 化，不能当成可直接沿用的 desk 证据；
- `3m/5m` 信号更密但大概率只是把手续费放大。

换句话说，它还没有提供能把当前系统认知从“pairs admission shell 已知重要”推进到“这条 repo 额外提供了一条值得前排继续追的独立 lane”的 decisive 信息。

## first verdict
- **不是 `keep_P1`**：因为它没有产生独立于既有 pairs 主线的新 front-slot hypothesis。
- **是 `background/P0`**：保留为一条可引用的工程实现与 pair-admission 参考，但不进入 survivor，也不分配新 Rank。

## 对 runtime 的直接影响
- `Fresh intake slot`：这条对象的 first verdict 已完成，记为 `background/P0`。
- `Background pool`：新增一条“walk-forward Engle-Granger pair admission 工程壳”参考对象。
- `cycle_plan` 第 3 条：本轮收口为 `done`。
