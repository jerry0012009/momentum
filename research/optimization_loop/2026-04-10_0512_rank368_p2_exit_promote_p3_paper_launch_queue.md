# Rank 368 — P2 exit decision: promote to P3 / Paper launch queue

- Time: 2026-04-10 05:12 UTC
- Target: `Rank 368 / cross-exchange funding extreme × band-stretch fade shell`
- Action type: `Active P2` 出口决策
- Verdict: `promote_P3`

## 本轮改变了什么 runtime truth
`Rank 368` 不再停留在开放式 `P2`：它在既有 `5m alt-heavy (ETH/ADA/DOGE)` 证据下已满足进入 paper 阶段的最低门槛，因此本轮直接升级到 `P3 / Paper launch queue`。同时，本轮最小 honesty / execution realism 补检确认其 edge 对摩擦高度敏感，后续 launch wiring 必须显式绑定低摩擦执行约束。

## 本轮执行的小检查（仅 1 项）
围绕 cycle_plan 要求的 `lookahead/leakage + friction realism`，做了最小补检：

1. **lookahead / leakage 口径确认（最小）**
   - 当前对象沿用的策略定义来自 source digest：`stretch ∩ funding_extreme` 触发后 **next-bar open** 入场（非同 bar 未来值成交），不属于显式 future-peek 口径。

2. **friction realism 头寸空间补检（最小）**
   - 基于既有 survivor artifact（`reports/artifacts/literature/rank368_altheavy_5m_threshold_timestop_sensitivity_2026-04-10.csv`）对 pooled `12bar` 方案做成本压力重算。
   - 输出：`reports/artifacts/literature/rank368_p2_exit_friction_stress_from_existing_2026-04-10.csv`
   - 关键结果（pooled, 12bar）：
     - `q90`: `post8=+570bps`, `post10=+104bps`, `post12=-362bps`
     - `q95`: `post8=+256bps`, `post10=-178bps`, `post12=-612bps`
     - `q97.5`: `post8=+176bps`, `post10=-252bps`, `post12=-680bps`

## 出口决策理由
- **支持升级到 P3 的点**：
  - 既有主证据链已给出一致正结论：`5m alt-heavy`、`q90~q97.5`、`12bar` 下仍是 `post-8bps` 正收益；且上轮已排除明显的 honesty fatal flaw。
  - 目前没有出现单一“立即否决”的 decisive blocker（例如明确 leakage、不可执行入场定义、或完全不可成交）。
- **保留但不阻断升级的点**：
  - 边际摩擦容忍度偏低，`10~12bps` 下多数口径转负；这不是“继续拖在 P2”的理由，而是 **P3 接线时必须写成硬约束**（低摩擦成交、滑点/费用预算、触发后失真监控）。

因此本轮合法收口为：**`promote_P3 / Paper launch queue`**。

## Runner / launch wiring 前置约束（写给下一步接线）
- universe 固定：`ETH/ADA/DOGE`（不默认扩到 BTC/XRP）
- 默认参数起点：`funding_abs_quantile in [0.90, 0.975]`，`time_stop=12 bars`
- 执行预算：`round-trip friction <= 8~10bps`（超过阈值要降频/停机）
- 必须记录首跑后的真实成交摩擦与信号保真度（否则自动降级审查）

## Reader-facing takeaway
`Rank 368` 已够格进 paper 阶段，但它不是“随便跑都行”的泛化 alpha：它更像一个 **低摩擦条件下的 alt-heavy crowding snapback pocket**。本轮结论是先升级到 `P3`，把“摩擦敏感”作为接线硬约束，而不是继续在 `P2` 无限打转。