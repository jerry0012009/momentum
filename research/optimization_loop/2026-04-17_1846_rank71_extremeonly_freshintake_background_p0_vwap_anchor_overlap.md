# 2026-04-17 18:46 UTC · Rank 71 extreme-only binary gate first verdict

## 本轮执行小点
- target: `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
- action: `conditional fresh intake`
- scope: 只回答 `EMA-VWAP-ATR-volume extreme-only binary gate / veto` 是否足以留下独立 residual；并补 1 个最小 honesty / execution realism blocker（只检查 `session VWAP / score` 组件在 crypto 24/7 下是否引入不诚实 anchor 或样本美化）

## 读取依据
- `research/park_reframe/2026-04-09_0244_rank71-park-reframe.md`
- `research/optimization_loop/2026-03-18_2326_rank71-source-intake.md`
- `research/optimization_loop/2026-03-18_2345_rank71-clean-replication-park.md`

## 最小结论
`Rank 71 / EMA-VWAP-ATR-volume extreme-only binary gate / veto` 不保留为新的 `keep_P1`；本轮 fresh intake 直接收口 `background/P0`。

## 为什么直接 background/P0
1. **extreme-only 没有拉出足够独立的新 residual。**
   - 已知 clean replication 里真正相对较好的只剩 `score>=75` 极高分桶，但这更像把原来的 graded score 砍到只留最稀的一层。
   - 当前没有新证据表明这层 residual 已经脱离既有 trend-shell / continuation admission family，只看到“高共振时少亏一些”，还没看到 queue-facing 的独立命名必要性。
2. **改善仍主要依赖 retention 下滑，而不是形成 decisively positive pocket。**
   - `score>=75` 仅保留约 `60.64%` 的交易；6bps/side 下 `post_cost_expectancy≈+0.02%` 只是在低成本口径勉强贴近打平。
   - 一旦成本更诚实抬升到 `10/15/20bps`，原 clean replication 已明确写出三臂仍整体为负；因此 extreme-only 更像阈值换壳，不是新的 surviving candidate。
3. **最小 honesty blocker 就卡在 VWAP anchor 本身。**
   - source-intake 当时已把 `session VWAP` 标成 crypto 24/7 环境下的潜在弱点；park reframe 也把它列为“先天可疑”。
   - 也就是说，本轮并不是发现了一个只差再补一步就能存活的单一 blocker，而是发现 extreme-only 方案仍把最可疑的 `session VWAP` anchor 留在核心定义里。
   - 在没有证明该 anchor 在 24/7 crypto 下具备诚实、稳定、非样本美化的解释前，这条线不足以占用新的 `keep_P1` / survivor 配额。
4. **distinctness 不足以支持新的 queue-facing failure / admission 名称。**
   - 当前更像“把旧 graded admission score 缩成高阈值版本”，而不是新对象。
   - 因此按 policy，应直接收口，而不是继续把它伪装成 fresh intake 存活对象。

## 本轮 hard verdict
- verdict: `background/P0`
- one-line result: `Rank 71：extreme-only 高共振桶仍主要是旧 graded admission score 的阈值换壳，改善依赖砍样本且核心 session VWAP anchor 在 crypto 24/7 下仍属未诚实组件，因此 fresh intake 直接收口 background/P0。`

## 对 runtime 的影响
- 不形成新的 `keep_P1`
- 不占用 `Surviving candidate slot`
- 不进入 `Active P2 slot`
- `Fresh intake slot` 维持 `open_pending_first_verdict / current_target=none`，等待 bot2 下轮重排

## 最小验证
- 已核对 `Rank 71` 原 source-intake 与 clean replication 一致指出：改善集中在高分稀疏桶、成本稍抬即塌、`session VWAP` 是先天可疑组件。
- 已核对当前 reframe 仅是把旧 graded score 收窄成 extreme-only binary gate，没有新增独立 execution edge 或新的诚实 anchor。

## 提交
- 未提交。
