# Rank 314 — ORCA tradability-aware cluster pairs P2 turnover / replacement-friction check: keep_P2

- 时间：2026-04-03 18:38 UTC
- 对象：`Rank 314 / ORCA tradability-aware cluster pairs`
- 执行动作：P2 admission 出口决策轮前置检查（`turnover / pair replacement friction / refresh cadence / stability penalty / honesty`）
- 结论：`keep_P2`

## 这一步回答的问题
在上一轮已经确认 `top tradability-score pairs` 比 classic `top-corr pairs` 拿到更高累计净后回报之后，这层优势在更诚实的 **换仓摩擦 / refresh cadence / pair stability** 口径下，是否已经足够硬到直接升 `P3 / paper launch`？

本轮结论：**还不够硬，先 `keep_P2`。**

## 本轮直接复核的 runtime artifact
沿用上一轮已落地的统一 `5m/15m` walk-forward shell artifact：
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/summary.csv`
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/5m_pair_selection_windows.csv`
- `reports/artifacts/optimization_loop/rank314_survivor_followup_20260403/15m_pair_selection_windows.csv`

核心数字回顾：
- `5m`：`top_tradability` 净后 `0.277151` vs `top_corr` `0.186484`，优势 `+0.090667`
- `15m`：`top_tradability` 净后 `0.294181` vs `top_corr` `0.244820`，优势 `+0.049361`
- `5m`：交易笔数 `28` vs `14`，平均持有 `99.975` vs `177.55` bars
- `15m`：交易笔数 `37` vs `24`，平均持有 `34.667` vs `49.962` bars

## 本轮新增认知：优势存在，但本质是“更高轮换的 admission alpha”
从 pair window 直接数换仓：

### 5m
- `top_corr` 两窗之间只有 **1/5** 个 pair 被新 pair 替换
- `top_tradability` 两窗之间有 **4/5** 个 pair 被新 pair 替换
- 同时它比 `top_corr` 多出 `14` 笔交易，只多赚了 `0.090667`
- 等价地说，若把新增 churn 对应的现实摩擦折成 **每笔额外约 `64.8 bps`**，这层优势就会被吃光

### 15m
- `top_corr` 每次滚窗平均新增 pair 约 **1.33** 个
- `top_tradability` 每次滚窗平均新增 pair 约 **3.67** 个
- 它比 `top_corr` 多出 `13` 笔交易，只多赚了 `0.049361`
- 等价地说，若更真实换仓与刷新摩擦折成 **每笔额外约 `38.0 bps`**，优势就会被吃光

翻成人话：

> `tradability-score` 的确把 pair book 从“稳定但偏慢的 majors 相关对”改成了“回归更快、轮换更猛的 alt-heavy admission book”；
> 但这层 edge 现在还更像 **高 churn 换来的 backtest 优势**，而不是已经证明能稳稳穿过真实 refresh / remap 摩擦的 paper-ready book。

## 为什么这轮不能直接 promote_P3
### 1) 当前优势还没跨过「更真实换仓摩擦」这道门
上一轮已经知道它单笔 `pnl/turn` 低于 `top_corr`；本轮进一步明确：
- `5m/15m` 的优势都明显依赖 **更高 turnover**；
- `top_tradability` 的 pair book 更像经常重排的动态白名单，而不是较稳定的可接线 basket；
- 一旦 refresh 不是“零代价重选 pair”，而是需要承受 mapping、信号切换、执行磨损，这层优势没有硬到可以直接跳去 `P3`。

### 2) honesty 口径还缺最后一块：maker/taker 与 refresh lag 的联动
当前证据仍是固定 roundtrip 成本壳；它已足够证明“不是纯幻觉”，但还不足以回答：
- pair 重排发生时，是否会把最赚钱的快回归 spread 变成 **最难稳定吃到** 的交易；
- monthly / multi-day refresh 若改成更懒的 cadence，优势是否还能保住；
- maker-first / taker-exit 现实下，alt-heavy 组合的 fill quality 会不会劣化得更快。

### 3) 没有 fatal flaw，所以也不该直接 drop_to_background
这条线不是塌了。
相反，本轮确认了它确实已经和 classic `top-corr` 分出结构性差异：
- 更短 half-life
- 更高 crossing / turnover
- 更快兑现，但更依赖 pair remap

所以最诚实的结论不是 `P0`，而是：
**保留在 `P2`，但下一步必须把 admission 收口到一个单一 decisive blocker：`refresh cadence × replacement penalty × maker/taker realism`。**

## 对 runtime 的影响
- `Rank 314` 维持在 `Active P2 slot`
- `p2_rounds_since_level_change` 增加到 `1`
- `p2_consecutive_keep_p2` 增加到 `1`
- `p2_last_evidence_axis` 改写为 `replacement_friction_refresh_cadence_stability_penalty`

## 一句话 result
`Rank 314` 本轮完成 turnover / replacement-friction admission 检查：`tradability-aware` 组合相对 classic `top-corr` 的净后优势仍存在，但当前优势主要来自更高轮换而非更高单笔效率；在 `5m/15m` 下，这层 edge 对额外换仓摩擦的容忍度只约为每新增交易 `64.8bps / 38.0bps`，还不足以诚实直升 `P3`，因此本轮结论是 `keep_P2`。