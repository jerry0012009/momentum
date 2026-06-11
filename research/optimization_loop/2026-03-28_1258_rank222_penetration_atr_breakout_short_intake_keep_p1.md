# Rank 222 / breakout-short penetration×ATR short-admission reframe — fresh intake 首轮判分：keep_P1

- 时间：2026-03-28 12:58 UTC
- 对象：`research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
- 结论：`keep_P1`
- 新分配 Rank：`222`
- 前序 alias：`Rank 86b`（queue-only draft）
- 本轮角色：fresh intake 首判

## 一句话结论
这条 park-reframe 真正留下的不是“把 penetration×ATR shared gate 再调细一点”，而是一条值得保留到前排做唯一一次 strict A/B clean replication 的 **`breakout-short 专用 penetration×ATR short-side admission / veto`**；但当前证据仍停在 role rewrite + proxy 旁证层，还不足以直接升到 `P2`。

## 为什么不是直接 drop
1. **角色收缩已经足够具体**：原 Rank 86 被否掉的是“shared gate”这层职责，不是 `penetration / ATR` 变量彻底失效；本轮提案把职责明确收缩成 `breakout-short` 专用 short-side admission / veto，已经不是泛泛措辞重写。
2. **有新的直接旁证**：`2026-03-23_0058_donchian-strength-short-admission-not-shared-gate.md` 已给出最关键的新事实——`penetration / ATR` 在 15m 更像 short-side admission score，而不诚实支持对称地服务 Fib / EMA long。
3. **与现有提案没有被完全吸收**：它不是 Rank 30b 的 post-break hold/reclaim、也不是 Rank 25c 的 HTF context role split，更不是 generic candle-quality；它保留的是 breakout 发生当下的 `penetration_strength` 单轴判决。
4. **第一刀可做得很便宜**：最小验证不需要新 universe、不需要新 exit，也不需要 second-layer regime；只要在既有 `breakout-short` baseline 上做 `baseline` vs `short_only_threshold_veto` 的 strict A/B 就能回答核心问题。

## 为什么还不能直接升 P2
1. **当前证据仍是 proxy + digest 级**：现有旁证证明的是“这条轴值得测”，不是它已经在 desk 的 frozen `breakout-short` 定义上跑出 admission 级结论。
2. **砍样本美化风险仍高**：`penetration / ATR` 最容易伪装成“把 weak short 砍掉后均值变好”；若不同时报告 `trade_retention`、`post-cost avg pnl`、`continue vs fail spread`，就很容易把 gate 写成样本修饰器。
3. **阈值稳定性还没回答**：支持证据提示 `0.2 / 0.4 / 0.6` 可能都值得看，但并未证明存在跨 BTC/ETH/SOL、跨成本档稳定的一把尺。
4. **还没完成 desk 口径对接**：必须先在当前项目真实的 `breakout-short` 事件集、真实 after-cost 口径下证明增益，才能进入 admission 级别的 `P2`。

## 本轮正式 verdict
- `Rank 222 / breakout-short penetration×ATR short-admission reframe`：**keep_P1**
- 保留原因：它已经收缩成一条 queue-facing、setup-specific、可 strict A/B 的单轴假设，不再是原 Rank 86 那种 shared-gate 宽命题。
- 不升 `P2` 原因：现在还缺唯一关键 admission bridge——**在 desk 真实 `breakout-short` baseline 上，`penetration_strength` 的 short-only veto 是否能在不靠过度砍单的前提下留下稳定的 after-cost 增益**。

## 唯一 survivor follow-up 应该回答什么
只做一次最小诚实检查：

> 在冻结的 `breakout-short` baseline 上，对 BTC/ETH/SOL 做 `baseline` vs `penetration_strength short-only threshold veto`（优先 `0.2 / 0.4 / 0.6` frozen grid）的 strict A/B，统一 `next-bar open + no-overlap + after-cost`，并一次性回答 `trade_retention`、`post-cost avg pnl`、`continue vs fail spread` 是否留下可交易增益；若没有，就按 `keep_P1 后转 background` 收口。

## 对 runtime 的影响
- fresh intake 已正式判分并获得 `Rank 222`
- survivor 槽位应切换到 `Rank 222`
- `followup_budget_remaining = 1`
