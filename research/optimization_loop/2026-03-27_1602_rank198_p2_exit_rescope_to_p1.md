# Rank 198 P2 exit decision — one-time P2->P1 re-scope

- Time: 2026-03-27 16:02 UTC
- Target: `Rank 198 / dynamic cointegration pair-basket spread convergence`
- Verdict: `one-time P2->P1 re-scope`

## 本轮只回答的问题
只执行当前 `cycle_plan` 中排在最前的 pending 小点：

> 在 `Rank 198` 已经形成第二次连续 `keep_P2` 之后，必须直接给出正式出口 verdict：它现在究竟应 `promote_P3`、`one-time P2->P1 re-scope`，还是 `drop_to_background`。

## 本轮使用的证据
1. `research/optimization_loop/2026-03-27_1450_rank198_survivor_followup_promote_p2.md`
2. `research/optimization_loop/2026-03-27_1459_rank198_p2_admission_keep_p2_effectiveness_cross_asset.md`
3. `research/optimization_loop/2026-03-27_1530_rank198_p2_admission_keep_p2_time_parameter_honesty.md`
4. `research/quant_digests/2026-03-27_1332_dynamic-cointegration-minute-binned-pairs.md`
5. `research/quant_digests/2026-03-23_0958_dynamic-cointegration-pairs-raw-alpha.md`
6. `reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`

## 会改变系统认知的结论
### 1) 现在不该直接 `promote_P3`
`Rank 198` 的有效部分已经被压缩得很窄：
- 广谱等权 pair deployment 已经被 contemporaneous Binance perp `15m` 成本后结果否掉；
- 当前真正留下净边的，基本只剩 `TRXUSDT/ADAUSDT` 这一类单一 surviving pocket；
- 而这条 pocket 的净边本身也不宽，当前主规格下只是从 gross cumulative `≈ +5.36%` 留到 net cumulative `≈ +2.12%`。

这说明它确实不像伪 alpha，但也还没有强到足以直接变成 paper launch 对象。若现在直接升 `P3`，实质上等于默认接受“单一 pocket + 单一参数口径”就足够，这和本轮前面 admission 已经明确指出的唯一 decisive blocker——`parameter stability`——冲突。

### 2) 现在也不该直接 `drop_to_background`
尽管 broad deployment 失败，但现有证据仍不支持把整个对象判死：
- 两份同主题证据都指向同一结构性结论：dynamic cointegration 真正活着的，不是“任意 pair 都做”，而是 **selection-sensitive pocket deployment**；
- honesty / execution realism 维度已经过关，没有看到 lookahead / repaint / friction denial 级 fatal flaw；
- surviving pocket 不是只剩 gross 幻觉，而是在明示 `6 bps round-trip` 后仍保留正净边。

因此把整个对象直接打回 background，会把“框架还活着，但广谱 deployment 不成立”与“整条线不值得继续”混为一谈，过度否定了当前证据。

### 3) 当前唯一合法且高杠杆的出口，是明确收窄对象定义
既然 admission 的唯一 decisive blocker 已经收敛到 `parameter stability`，而现存可交易证据又只剩 selection-sensitive pocket，那么本轮唯一明确的 re-scope 方向其实已经足够清楚：

> 不再把 `Rank 198` 维持为“dynamic pair-selection / basket-selection + spread convergence` 的广义母对象，
> 而是收窄成 **`TRXUSDT/ADAUSDT`-style surviving pocket deployment`：在 liquid perp universe 里，先用 dynamic cointegration funnel 找到极少数仍成本后存活的 pair pocket，再只对这些 pocket 做 spread convergence，并优先验证邻近参数/持有期扰动下是否仍保留净边。**

这不是模糊的“再看看”，而是对象层级上的一次明确缩窄：
- 从“selection-sensitive framework”
- 收窄到“single-pocket / sparse-pocket deployment spec”

也就是说，接下来该验证的已不再是“这整类框架是否存在”，而是：
- `TRX/ADA` 这类 surviving pocket 在邻近 `entry_z / exit_z / max_hold / cost` 扰动下是否仍然存活；
- 若不存活，则这条线就应直接退出前排；
- 若存活，再考虑是否重新回到 `P2` 并争取 `P3`。

## 决策
本轮对 `Rank 198` 给出：

> **`one-time P2->P1 re-scope`**

新的工作定义：

> `Rank 198` 不再以“dynamic cointegration pair-basket spread convergence”广义框架形式停留在 `Active P2`；
> 它应回到 `P1`，并被明确收窄为 **`dynamic cointegration surviving-pocket deployment`**：重点围绕 `TRXUSDT/ADAUSDT` 这类当前仍成本后存活的单一/稀疏 pocket，验证邻近参数与持有期扰动后的净边稳健性，而不是继续拿 broad deployment 或抽象 framework 叙事去争取 `P3`。

## 为什么这是合法出口，而不是第三次 `keep_P2`
- 当前 `Active P2` 已出现 2 次连续 `keep_P2`；
- policy 明确禁止第三次开放式 `keep_P2`；
- 当前又确实存在唯一明确的 re-scope 方向，因此不能假装还在做 admission。

## Runtime writeback
- `Active P2 slot`：清空，结束 `Rank 198` 当前这段 admission。
- `Surviving candidate slot`：写回 `Rank 198`，但对象定义改为 `dynamic cointegration surviving-pocket deployment`，并给这次 re-scope 留下唯一一次便宜、诚实的 follow-up 预算。
- `cycle_plan #2`：标记为 `done`，明确 result 为本轮正式出口 verdict。

## Reader-facing takeaway
`Rank 198` 这轮的结论不是“dynamic cointegration 不行”，也不是“已经强到该 paper launch”，而是更窄、更诚实的一句：

**广谱 pair/basket deployment 不成立，但 `TRXUSDT/ADAUSDT` 这类 surviving pocket 仍值得保留；因此这条线应从 `P2` 正式收窄回 `P1`，改成 `single-pocket / sparse-pocket deployment` 的 re-scope 对象，而不是继续拿抽象母框架硬冲 `P3`。**
