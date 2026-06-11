# 2026-03-30 04:39 UTC · Rank 246 false structural reclaim short intake — keep P1

- policy read: `docs/BOT2_BOT3_POLICY.md`
- runtime read: `docs/BOT2_BOT3_STATE.md`
- executed cycle item: `Rank 31 park residual -> false structural reclaim traded as short failure-followthrough`
- scope rule: 只执行当前排在最前的 pending 小点；不重排后续 `cycle_plan`

## 本轮要回答的唯一问题
`Rank 31` 的 drafted residual —— `invert false reclaim into short failure-followthrough` —— 是否已经足够从原 `long structural reclaim continuation` 的失败边界中独立出来，作为新的 front-slot `fresh intake` 进入当前运行槽位？

## 读取到的关键证据
1. `research/park_reframe/2026-03-22_0439_rank31-park-reframe.md`
   - 原 `Rank 31` 作为 long-entry 已经是 hard park：`BTC/ETH/SOL, 120d, 15m, 6bps/side` 下，`structural_higher_low_reclaim` 成本后显著为负，且 `mean_false_reclaim_ratio ≈ 35.04%`。
   - 这份 reframe 没有试图救回 long continuation，而是把唯一残余信息收窄成：**只交易 reclaim 失败后的 short followthrough**。
2. `docs/PARK_REFRAME_QUEUE.md`
   - 这条 draft 已被固定成 `Rank 31b`，边界清楚：保留原 `structural_higher_low_reclaim` 作为事件锚；当后续出现 `close back under reclaim level / break back under reclaimed structure` 时，按 `next-bar open` 做 short。
   - `trade off` 也已经写明：第一刀只允许 strict `baseline vs failure-short`，不得顺手叠第二层 gate/overlay。
3. 近邻吸收检查
   - `research/park_reframe/2026-03-25_0657_rank50-park-reframe.md` 与 `2026-03-25_1129_rank53-park-reframe.md` 都明确把“false reclaim -> short failure-followthrough”视为**已被 Rank 31b 先占住的更贴题宿主**。
   - 这说明当前语义并不是泛 failure 家族的大杂烩；相反，它已经稳定收敛成一个具体、窄、未被别的 front-slot 对象替代的对象定义。

## 本轮判断
这条 residual **值得进入新的 fresh intake**，但只到 `keep_P1`，还不到直接升 `P2`。

原因分两层：
1. **它已经足够像新对象，而不是旧 Rank 31 的近义重写。**
   - 原对象主语是 `long structural reclaim continuation`；
   - 这条 residual 的主语是 `false reclaim -> short failure-followthrough`；
   - 方向、触发后的 verdict 语义、以及最小执行框架都已经改变，而且修改轴仍保持单一，没有偷偷回到泛 CHoCH/failure/regime 家族。
2. **但当前还只有“为什么值得测”的 intake 级证据，没有第一轮 clean replication 结果。**
   - `false_reclaim_ratio ≈ 35%` 说明失败形状确实存在；
   - 可是它还没经过当前 desk 口径下的最小诚实 A/B，因此现在最诚实的层级是：**先正式入前排，给它唯一 survivor / first-check 名额，而不是凭故事直接送进 `P2`。**

## 正式结论
- 为这条新 intake 分配下一个未使用的正式整数 `Rank = 246`。
- 对象名：`Rank 246 / false structural reclaim short failure-followthrough`
- 本轮 intake verdict：**`keep_P1`**
- runtime 语义：
  - 进入 `Fresh intake slot`
  - 同时占据 `Surviving candidate slot`
  - `followup_budget_remaining = 1`
  - 下一轮只允许做 1 次最小诚实检查：在同一 `BTC/ETH/SOL, 120d, 15m` 与同一成本口径下，严格比较 `baseline structural reclaim long family` vs `reclaim-failure short followthrough` 的 clean replication；若不能留下干净 pocket，就应快速收口回 `background/P0`

## Runtime writeback
- 已更新 `docs/BOT2_BOT3_STATE.md`：
  - `Fresh intake slot` 改写为 `Rank 246 / false structural reclaim short failure-followthrough`
  - `Surviving candidate slot` 改写为同一对象，并将 `followup_budget_remaining` 设为 `1`
  - 当前 cycle item 3 写成 `done`
  - `result` 写明：`Rank 246` 已正式作为新 fresh intake 进入前排，并维持 `keep_P1`

## 本轮 reader-facing 变化
有真实推进：形成了新的正式 front-slot intake，并产生新的 durable rank identity；因此应同步刷新首页并发送邮件摘要。