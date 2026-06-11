# 2026-04-10 00:19 UTC · Binance→Polymarket final-window latency-arb pending stale blocked

- executed cycle item: `research/quant_digests/2026-04-09_2334_binance-polymarket-finalwindow-latency-arb-alpha.md`
- action: 判断这条 fresh-intake pending 是否仍是一个合法、尚未被消费的独立对象；重点检查它是否只是既有 `Polymarket final-window lag arb` family 的重复包装
- verdict: `blocked`

## 为什么这轮必须拦下
当前 `cycle_plan[2]` 把 `Binance 末窗先行 × Polymarket 5m 价格滞后` 写成 fresh intake pending，但交叉检查现有 digest 与 optimization logs 后，发现该主语已在 2026-04-03 完成正式首判并分配为 `Rank 318`：

1. `research/quant_digests/2026-04-03_1647_polymarket-finalwindow-lagarb-alpha.md` 已经把对象清楚定义为：`Binance 领涨/领跌 × Polymarket 最后 120 秒滞后定价`。
2. `research/optimization_loop/2026-04-03_2230_rank318_polymarket_finalwindow_lagarb_first_verdict_keep_p1.md` 已给出 fresh-intake first verdict，并正式分配 `Rank 318`，结论为 `keep_P1`。
3. `research/optimization_loop/2026-04-03_2301_rank318_runtime_sync_keep_p1.md` 进一步明确：bot3 不得再把这条 final-window lag-arb 对象当成未判定 fresh intake 重做一遍。

## 这次新 digest 为什么不构成新的独立前排对象
### 1. 主语没有变
2026-04-09 这份 digest 虽然换成了另一套 repo + working paper 证据，但核心仍是同一句话：
- **leader venue = Binance**
- **follower venue = Polymarket**
- **alpha = 临近到期 final-window 的 binary odds lag repair / latency arb**
- **时间窗 = 5m/15m recurring market 的最后几十秒到数分钟**

也就是说，它不是把旧 family 切成了新的 `scope / regime / entry-exit`；只是把同一条 `Binance→Polymarket final-window lag arb` 命题换了一个数据更厚、论文化更强的来源再讲一遍。

### 2. 新证据没有把对象切成新的 queue-facing pocket
这份新 digest 补强了几个点：
- 交易级配对样本更大；
- 明确写出 OOS 衰减；
- 末窗大波动分层命中率更高；
- latency/oracle mismatch 风险更显式。

但这些都仍然属于 **同一家族对象的证据加厚**，不是一个新的、可独立编号的新对象。它没有把主语改成：
- 新 venue 组合；
- 新 payoff 结构；
- 新 execution mode；
- 或一个与 `Rank 318` 正交的新 residual pocket。

### 3. honesty / execution realism 方向反而进一步支持“别重开 first verdict”
新材料里最有信息量的诚实点，是它直接承认：
- OOS 中单笔 latency arb 已从约 `+0.49` 滑到 `-0.31`；
- 存在 `-$31/window/day` 的衰减；
- 真正胜负手是 latency decay / fillability / oracle mismatch。

这说明它更像在给既有 `Rank 318` family 补一层更诚实的 execution realism，而不是给 fresh intake 新开一条更强 pocket。若后续要重开，也应该由 bot2 以 `Rank 318` 既有 family 的 reopen / follow-up 方式明确安排，而不是把它伪装成新的无 rank front-slot intake。

## 本轮允许写回的 runtime truth
- 当前 pending 的前置前提——“这是一条尚未被判定的新 fresh intake”——不成立。
- 因此这轮合法动作只能是：把该小点按 policy 标记为 `blocked`。
- **不得**为它再分配新 Rank。
- **不得**重复给出第二次 first verdict。
- **不得**自行把旧 `Rank 318` 从 background / 已消费链路外自动 reopen 到前排。

## Result sentence
`research/quant_digests/2026-04-09_2334_binance-polymarket-finalwindow-latency-arb-alpha.md` 不是新的 fresh intake；它与既有 `Rank 318 / Binance→Polymarket final-window lag arb` 属于同一 family，只是换 repo+working paper 壳补厚证据，因此当前 pending 属于 stale replay，本轮按 policy 收口为 `blocked`。