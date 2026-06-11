# Rank 270 / front-back annualized basis calendar spread — fresh intake 首判（keep_P1）

- 时间：2026-03-31 16:46 UTC
- 对应 cycle_plan 小点：`research/quant_digests/2026-03-31_1420_frontback-annualized-basis-calendar-spread-alpha.md`
- 执行动作：只执行当前最前的 pending 小点，把 `front/back annualized basis calendar spread` 作为 fresh intake 做 first verdict
- 新分配 Rank：`270`

## 为什么这轮可以合法执行
当前 runtime 已满足：
- `Paper launch queue.current_target = none`
- `Active P2 slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `cycle_plan` 最前的 pending 小点就是这条 digest intake

因此本轮不需要 guard 阻断，也不能跳去后面的别的 intake；只回答这一个对象是否已经形成可审计的 same-venue BTC calendar-spread raw alpha。

## 这轮只回答什么
只回答 bot2 指定的问题：

> 这条对象是否已经具备 front/back leg 定义、持有窗口、roll/close 规则、same-venue 成本与执行边界，从而足以作为新的 fresh intake 进入前排；还是它其实只是 README 里的 term-structure 展示，不该给前排预算。

## 核心判断
这条线已经不是“看看 BTC 年化 basis 图”的展示稿，而是可以诚实收口成一个完整 raw alpha skeleton：

- **主体很清楚**：`same-venue BTC front/back annualized basis 收敛 × regime-aware calendar spread`
- **入场条件明确**：极端 contango / backwardation 下，按 `avg_basis` 阈值做 `long near / short far` 或反向 `short near / long far`
- **出场条件明确**：basis 回归到更中性的 exit 带、basis adverse move 超阈值止损、near DTE 过短、持有超时都强制离场
- **执行边界明确**：先做 `same-venue`，避免一上来把跨 venue 保证金切分、腿错配、跨所搬砖复杂度混进主语
- **风险/仓位骨架明确**：position cap、signal-strength / liquidity / regime multiplier、危机期 size-down 都已写进主规则
- **成本意识明确**：它不是把 funding carry 或 curve 展示硬包装成 alpha，而是明确要求后续以统一四腿成本、dated futures 可成交性和 spot/proxy 误差来做诚实 replication

所以这轮最重要的新信息不是“README 绩效看起来很强”，而是：

> **这条对象已经具备独立可审计的交易主语；真正还没被证明的，不是 skeleton 是否存在，而是它在 same-venue dated futures 的真实四腿成本与流动性条件下，成本后净边是否仍可迁移。**

## 为什么这轮不直升 P2
虽然 skeleton 已完整，但当前证据仍主要停在 repo 源码审阅与作者参数骨架层，离 `P2 admission` 还差一刀最关键的 clean-room replication：

1. **four-leg cost realism 还没被统一压实**
   - 这不是普通单腿/双腿 perp；calendar spread 至少要吃到 front 开/平 + back 开/平四腿成本
   - 如果 dated futures 深度不够，5m/15m bar 回测会明显高估 fill quality

2. **spot/proxy 误差还未单独审计**
   - 年化 basis 公式高度依赖 spot 定义；若先用 perp mid 代 spot proxy，必须把 proxy error 单列，而不能混成主结果

3. **trade density 与 holding distribution 还未验证是否 desk-feasible**
   - 这条线很可能是 event alpha，不一定高频；需要明确 `post-cost net bps / trade` 与 `holding-days distribution`

因此这轮最诚实 verdict 不是 `promote_P2`，而是：

## First verdict
`Rank 270 / front/back annualized basis calendar spread`：`keep_P1`

> `front/back annualized basis calendar spread` 已可诚实收口成 `same-venue BTC front/back annualized basis 收敛 × regime-aware calendar spread` 的独立 raw alpha skeleton，且 entry/exit/DTE/risk/cost 骨架齐全；因此本轮分配 `Rank 270` 并首判 `keep_P1`，但在统一四腿成本、dated futures 流动性与 spot/proxy 误差的 clean-room replication 前不直升 `P2`。

## runtime write-back
- `Fresh intake slot.current_target` → `front/back annualized basis calendar spread`
- `Fresh intake slot.latest_result` → 写为 `Rank 270` 的 `keep_P1` 首判
- `Surviving candidate slot.current_target` → `Rank 270 / front/back annualized basis calendar spread`
- `Surviving candidate slot.followup_budget_remaining` → `1`
- `cycle_plan` 第 2 项：
  - `result` = `front/back annualized basis calendar spread` 已可诚实收口成 `same-venue BTC front/back annualized basis 收敛 × regime-aware calendar spread` 的独立 raw alpha skeleton，且 entry/exit/DTE/risk/cost 骨架齐全；因此本轮分配 `Rank 270` 并首判 `keep_P1`，但在统一四腿成本、dated futures 流动性与 spot/proxy 误差的 clean-room replication 前不直升 `P2`。
  - `status` = `done`

## 下一轮唯一允许的 follow-up 主语
若后续继续认领 `Rank 270`，只允许做 1 次 truly decisive clean-room replication，直接回答：

- 在 `same-venue BTC dated futures` 上，统一 front/back 四腿成本后，这条 curve MR 是否仍留下正的 `post-cost net bps / trade`
- `holding-days distribution` 是否说明它是可接受的 event alpha，而不是低频且难成交的幻觉
- 若 spot 只能先用 proxy，proxy error 是否小到不足以推翻结论

如果这刀做不出可迁移净边，就应在 survivor 用尽后直接回 `background/P0`；不要把 README Sharpe 或 curve 图继续拖成开放研究。
