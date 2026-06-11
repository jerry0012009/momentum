# Rank 298 survivor follow-up 收口：不升 P2，回 background/P0

- 时间：2026-04-02 22:58 UTC
- 对象：`Rank 298 / dynamic factor stripped multipair stat-arb`
- 本轮角色：bot3 执行器
- 对应 cycle_plan 小点：第 1 项（唯一合法 survivor follow-up）

## 本轮执行内容
按 policy 只执行 `Rank 298` 这一条 survivor follow-up，不重排 cycle plan，不扩展到后续 fresh intake。

本轮直接回答的核心问题是：
- 这条 `market-factor stripped × stationary-factor multi-pair rotation`，是否已经具备足够 short-cycle clean-room 证据，可以从 survivor 直接升到 `P2`？

## 结论
**不能升 `P2`。**

本轮把 `Rank 298` 的 survivor budget 用完并收口到 `background/P0`。

一句会改变系统认知的话：

> `Rank 298` 目前只完成了“值得做 15m/5m clean-room 检查”的 paper-level 假说确认，还没有形成足以支撑 short-cycle admission 的实证；因此 survivor budget exhausted，不升 `P2`，回 `background/P0`。

## 为什么这次不能升 P2
### 1) 已经确认的部分
当前材料已经足以确认它不是旧 pairs/PCA 家族的空泛重述，而是一条结构完整的 raw alpha 假说：
- 先剥离共同市场因子；
- 再用 stationary 第二因子驱动 ranked long-short rotation；
- 自带 stationarity / correlation honesty gate；
- 论文里 entry / threshold / hold / cost-aware 壳子都比较清楚。

所以它作为 fresh intake 拿到 `keep_P1` 是成立的，这一点本轮不推翻。

### 2) 但 survivor follow-up 要回答的是 short-cycle transfer 是否已经足够可信
要升 `P2`，至少得看到它在 desk 目标语境里不只是“论文上看起来合理”，而是已经足够像一条可 admission 的对象。

本轮看下来，缺口仍然是决定性的：
- 还没有高流动 perp clean-room 结果，证明 `integrated-like common factor + stationary factor` 结构在 `15m/5m` 上稳定存在；
- 还没有证据说明 `top-half/bottom-half` 或 `top-2/bottom-2 sparse` 的 short-cycle 版本在成本后可存活；
- 也还没有样本密度/换手层面的 admission 级证据，能证明这不是“日频结构看起来成立，但缩到短周期就被噪音和 turnover 吃掉”的对象。

换句话说：
**这条线现在更像“值得测试的 clean-room 假说”，还不像“已经够格进入 Active P2 admission 的候选”。**

## 为什么本轮不继续拖成开放式 keep_P1
按 policy，survivor 只有一次最小 decisive follow-up。

这一次 follow-up 已经回答了最关键的问题：
- 它有研究价值；
- 但现阶段仍缺 short-cycle decisive evidence；
- 所以不能无限挂在 survivor，也不能在没有新证据的情况下假装已经够格进 `P2`。

因此本轮必须诚实收口，而不是继续保留在前排。

## runtime 回写
本轮已同步更新：
- `Surviving candidate slot -> none`
- `followup_budget_remaining -> 0`
- `Background pool.latest_parked -> Rank 298`
- `cycle_plan[1].result/status -> done`

## 后续含义
`Rank 298` 不是被否定为“坏对象”；它是被归类为：
- 目前缺少 short-cycle clean-room admission 证据；
- 默认不再占用当前前排；
- 若未来用户明确要求 reopen，或后续出现真正的新 clean-room 结果，再重新进入运行槽位。

## 最终 verdict
- 当前 verdict：`survivor budget exhausted -> background/P0`
- 不执行升级：`not promote_P2`
- 原因：缺少 high-liquid perp short-cycle 上对稳定第二因子与成本后可存活 ranked rotation 的决定性证据
