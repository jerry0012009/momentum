# bot3 blocked — BTC anchor transient coint intake cannot run before Rank 284 survivor follow-up closes

- 时间：2026-04-01 22:26 UTC
- 对象：`research/quant_digests/2026-04-01_2013_btc-anchor-transient-coint-oufade-alpha.md`
- 本轮角色：bot3 当前最前 pending 小点执行

## 本轮判定

本轮**不执行**这条 fresh intake；按 policy 直接记为 `blocked`。

原因不是对象本身有 fatal flaw，而是它在当前 runtime 下**不满足开跑前置条件**。

`cycle_plan` 第 3 条自己的 action 已经写明：

> 在当前前排已无真实可执行 `P3 / P2 / P1` 动作的前提下，再把 `BTC anchor × transient cointegration shortlist × walk-forward OU fade` 作为新的 fresh intake。

但当前 authoritative runtime 仍显示：

- `Paper launch queue = none`
- `Active P2 = none`
- `Surviving candidate slot = Rank 284`
- `followup_budget_remaining = 1`
- `Rank 284` 的 latest_result 已明确指定：下一步必须直接检查**禁用 `ADF-only fallback` 后，liquid perp universe 里是否仍存在 after-cost、可执行、且不依赖口径不一致 spread 定义的诚实 pair pool**；若没有，就应按 policy 收口回 background。

这说明当前前排**仍然存在一个具体、合法、且更高优先级的 P1 survivor follow-up**，所以“前排已无真实可执行动作”这个前置条件不成立。

按 `BOT2_BOT3_POLICY.md`：

1. 已有前排对象的收口，优先级永远高于新的发现；
2. `Surviving candidate` 享有那唯一一次 follow-up 的前排锁定权；
3. bot3 若发现 state / cycle_plan 与 policy 冲突，应拒绝执行歪路径，回退到合法动作。

因此，这轮对系统认知的唯一合法更新是：

> `BTC anchor × transient cointegration shortlist × walk-forward OU fade` 这条 intake 不是被研究否决，而是因为 `Rank 284` survivor 尚未完成唯一 follow-up，当前不满足 fresh intake 开跑前置条件，所以本轮按 policy 阻断，不得抢占前排。

## 对 runtime 的影响

- 仅把 `cycle_plan` 第 3 条写成 `blocked`
- 不分配 Rank
- 不改写前排槽位归属
- 不刷新首页（本轮无 reader-facing 新结论）

## 下一合法动作

应先执行 `Rank 284` 的 survivor follow-up：
- 禁用 `ADF-only fallback`
- 统一 spread / residual 定义
- 在 liquid perp universe 下回答是否仍有 after-cost、可执行、诚实的 pair pool

在这一步诚实收口前，不应继续切新的 fresh intake。