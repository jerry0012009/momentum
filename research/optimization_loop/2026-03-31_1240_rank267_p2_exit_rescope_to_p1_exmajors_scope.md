# Rank 267 / crypto factor momentum × size/vol rotation P2 exit → one-time P2->P1 re-scope

- 时间：2026-03-31 12:40 UTC
- 轮次来源：bot3 13 分钟自动执行轮次
- 依据文件：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 执行动作：执行 `cycle_plan` 最前项 pending 小点，即 `Rank 267` 的 `P2` 出口决策
- 正式结论：`one-time P2->P1 re-scope`

## 本轮只回答的唯一问题
> 在已经完成 `cross-asset blocker + time stability passed + parameter/honesty passed` 的前提下，`Rank 267` 是否已经足够诚实、足够稳定，值得直接进入 `paper trade / paper launch`；如果还不够，是否存在唯一明确的 re-scope 方向？

## 已有 admission 结论如何收口
当前已经写回 runtime 的三条关键事实是：
1. `survivor -> P2`：在 Binance perp 当前高流动 universe、4h 横截面换仓与单边 `10bps` 成本下，`short-horizon momentum` 与 `size` sleeves 有明确成本后净边，winner rotation 还能进一步增益；
2. `cross-asset`：`leave-one-out` 仍为正，说明不是单一币幻觉；但 `BTC/ETH/SOL majors` 单独拆开后几乎只剩手续费边缘，当前净边主要来自 `ex-majors` 高流动 alt basket；
3. `parameter + honesty`：最优结果不是单一点参数；真正能活下来的参数面是 `72h~7d` 排序、`12h~24h` 持有、`1d~5d` rotation，而更快的 `4h` 版本已经明显被摩擦压薄；同时 broad-crypto 叙事不诚实，真实有效 scope 更接近 `ex-majors high-liquidity alt basket`。

因此，这轮已经不能再产出第三次开放式 `keep_P2`。必须只在三种出口里选一个：
- `promote_P3`
- `one-time P2->P1 re-scope`
- `drop_to_background`

## 为什么这轮不应直接 `promote_P3`
### 1) 当前 blocker 没被推翻，paper-ready 主语还没站稳
如果要升 `P3`，对象至少应已经能被诚实地写成一个接近 paper 的可执行主语。但对 `Rank 267` 来说：
- `majors` 拆开后 rotation 仅约 `+11.17 bps/period`，命中率约 `50.07%`；
- 真正支撑结果的是 `ex-majors` alt basket，rotation 约 `+117.44 bps/period`；
- 也就是说，当前并不能把它写成“broad crypto factor rotation 已成立”的 paper candidate。

这不是一个轻微瑕疵，而是对象定义层面的收窄：**真实有效的对象不是 broad-crypto / majors-capable 轮动，而是更窄的 ex-majors 高流动 alt basket。**

### 2) honesty 虽未见 fatal flaw，但也没有把 scope 问题消掉
上一轮已经很清楚：
- 没发现足以一票否决的 lookahead / leakage / 明显不可执行结构；
- 但 broad-crypto 叙事被样本选择放大；
- 能活下来的，是较慢的 `72h~7d rank + 12h~24h hold` 结构，并且主要靠 alt basket。

这意味着对象离 `P3` 还差的，不是“再补一点小验证”，而是**先把主语改写诚实**。在主语尚未改写前直接升 `P3`，等于把 `majors 不成立` 这个 admission blocker 硬吞掉。

## 为什么也不应直接 `drop_to_background`
因为当前并没有出现足以判死的 fatal flaw：
- 结果不是单一参数孤点；
- `leave-one-out` 没显示单一币救全局；
- 时间稳定性已通过；
- friction 敏感性虽限制了节奏，但没有把慢频版本全部打成负值。

所以这条线的问题不是“根本没 alpha”，而是：
> **alpha 的真实适用范围比先前叙事窄得多，只能诚实地定义成 `ex-majors high-liquidity alt basket` 上的较慢节奏 factor rotation。**

这正是 policy 允许的一次性 `P2->P1 re-scope` 场景：
- 改 `scope`
- 改 `asset subset`
- 同时把可执行节奏写实

## 唯一明确的 re-scope 方向
本轮允许的唯一一次 `P2->P1` 回退，必须写成具体改法，而不是“再看看”。这里唯一清晰、非模糊的方向是：

> **把 `Rank 267` 从“crypto factor momentum × size/vol rotation”重写为一个更窄的 `ex-majors high-liquidity alt basket` 轮动对象：只保留 `72h~7d` 排序、`12h~24h` 持有、`1d~5d` sleeve rotation` 这片已显示连续正区间的慢频参数面，不再把 `majors` 或 broad-crypto 普适性写进主语。**

这不是新增另一条完全不同的策略，而是对同一条线做一次明确的 `scope + execution tempo` 重定义。

## 正式 verdict
`Rank 267 / crypto factor momentum × size/vol rotation`：`one-time P2->P1 re-scope`

一句话收口：

> **`Rank 267` 的 P2 admission 说明它并非单一参数或单一币幻觉，但当前成本后净边主要由 `ex-majors high-liquidity alt basket` 支撑，`majors` 单独拆开后并不成立；因此它还不够诚实地直接升入 `P3 / paper launch queue`，也不该被判死，而应一次性从 `P2` 回到 `P1`，重写成“仅面向 ex-majors 高流动 alt basket、只保留慢频有效参数面”的 re-scoped 对象。**

## 对 runtime 的写回语义
- `Active P2 slot`：当前出口决策已完成，`Rank 267` 不再保留在 `Active P2`
- `Surviving candidate slot`：接手这个一次性 re-scoped `P1` 对象，等待 bot2 在后续轮次为该窄版对象安排唯一明确的 follow-up
- `cycle_plan[2]`：写成 `done`

## 一句话 result（用于 state / cycle_plan）
`Rank 267：不是单一参数或单一币幻觉，但当前净边主要由 ex-majors 高流动 alt basket 支撑、majors 单独并不成立；因此本轮不升 P3，也不直接回 background，而是一次性从 P2 回到 P1，重写成仅面向 ex-majors 高流动 alt basket、只保留慢频有效参数面的 re-scoped 对象。`
