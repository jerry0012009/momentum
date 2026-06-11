# 2026-03-29 20:59 UTC — shortleg momentum crash veto / cap for large-cap XS momentum intake closes as background only

- 当前执行小点：`shortleg momentum crash veto / cap for large-cap XS momentum`
- 动作：作为前排链条清空后的首个 fresh intake，判断这篇 2025 momentum paper 是否足够独立到值得转成新的 queue-facing 对象
- 结论：`done`（但 verdict 为 `不进入前排 / background only`）

## 为什么这次不能作为新 fresh intake
这轮要回答的主语被明确限制为：

> `large-cap XS momentum × short-leg single-name jump veto / cap`

而这个主语并不是新对象，已经被 **`Rank 213 / large-cap XS momentum × short-leg jump veto`** 以更完整的 runtime 链条正式占用：

1. **2026-03-28 06:21 UTC** 已完成 fresh intake，并正式分配 `Rank 213`：
   - 记录：`research/optimization_loop/2026-03-28_0621_rank213_largecap_xs_momentum_shortleg_veto_intake_keep_p1.md`
2. 随后已完成唯一 survivor follow-up，并升到 `P2 admission`：
   - 记录：`research/optimization_loop/2026-03-28_0729_rank213_survivor_followup_promote_p2.md`
3. 随后又已完成 `P2 exit decision`，直接升到 `P3 / Paper launch queue`：
   - 记录：`research/optimization_loop/2026-03-28_0852_rank213_p2_exit_promote_p3_deploy_ready_spec.md`
4. 最后已完成 launch wiring，进入正式 live runner：
   - 记录：`research/optimization_loop/2026-03-28_1120_rank213_p3_launch_wiring_connected_runner_live.md`
   - runtime 现状：`Paper launch queue.connected_runner_live` 已明确包含 `Rank 213 / large-cap XS momentum × short-leg jump veto`

## 这次新 digest 带来了什么、又没带来什么
新 digest：`research/quant_digests/2026-03-29_2011_shortleg-momentum-crash-veto-alpha.md`

它带来的新增信息主要是：
- 把同一篇 2025 paper 的 desk 读法重写得更尖锐：
  - 不是泛泛 `vol-managed momentum`
  - 而是 `XS momentum × short-leg single-name jump veto`
- 补了一个新的 liquid-major `15m` transfer check，且结果偏负：
  - base 约 `-10.0 bps/次`
  - hit rate 约 `36.9%`
  - 我设的这版 `short-jump veto` 触发次数为 `0`
  - 说明在 liquid-major 这版 pocket 上，这个 lesson 不能直接平移成现成可交易 alpha

但这些信息**没有形成新的独立主语**，原因是：
1. **它仍在回答与 `Rank 213` 完全同一条核心问题**：crypto XS momentum 的 decisive blocker 是否主要来自 short leg 的 single-name jump concentration；
2. 新 digest 里的 object naming（`short-leg single-name jump veto / cap`）只是把同一 paper 的风险模块说得更细，并没有从 alpha 本体、资产子集、执行假设、entry/exit、或 shared overlay 角色上切出一个与 `Rank 213` 明确不同的新对象；
3. 它给出的 liquid-major 负面 transfer check，更像是 **`Rank 213` 的补充边界条件**：别把该对象误读成“majors 上随手就活”的 generic momentum，而不是一个值得新建 rank 的新 queue-facing candidate。

## policy 对这一步的约束含义
按 `BOT2_BOT3_POLICY.md`：
- 前排对象必须是**独立对象**，不能因为“最近又写了一篇 digest / 又换了个标题”就把同一家族重复拉回前排；
- `Background pool` 中的旧对象不得自动 reopen；
- 已在运行态中完成 `P3 launch wiring` 的对象，如果只是出现新的同义复述或边界说明，不应被重新包装成 fresh intake。

所以这一步最诚实的收口不是：
- 给新 rank；
- 或把它重新写进 `Fresh intake slot`；
- 或把 `Rank 213` 再次拉回 queue 头。

而是：

> **明确记为 `不进入前排 / background only`：这篇新 digest 只是给 `Rank 213` 补了一条“liquid majors 直推不成立、对象仍应理解为 liquid-alt universe 上的 short-leg jump-control 版 XS momentum” 的边界注释，不构成新的独立 queue-facing 对象。**

## runtime implication
- **不分配新 Rank**；
- **不改写 `Fresh intake slot` 当前对象**；
- **不触发新的层级迁移**；
- 只把当前 `cycle_plan` 第 1 项收口为 `done`，并把结果写成“与 `Rank 213` 高度重叠、无新独立主语，因此 background only”。

## result sentence
`shortleg momentum crash veto / cap for large-cap XS momentum` 这条 fresh-intake 检查已收口：新 digest 只是把同一篇 2025 paper 对应的 `short-leg single-name jump concentration` 风险讲得更尖，但该主语已被 `Rank 213 / large-cap XS momentum × short-leg jump veto` 完整占用且已进入 `connected_runner_live`，因此本轮不能再作为新的 queue-facing 对象进入前排，只能记为 `不进入前排 / background only`。