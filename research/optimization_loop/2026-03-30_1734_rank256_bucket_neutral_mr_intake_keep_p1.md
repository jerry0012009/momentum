# 2026-03-30 17:34 UTC — Rank 256 / bucket-neutral 1h return mean reversion × funding misalignment gate / fresh intake keep_P1

## 本轮执行对象
- cycle_plan 第 3 项：`bucket-neutral 1h return mean reversion × funding misalignment gate`
- 执行动作：作为新的 `fresh intake`，只回答这份 Hyperliquid repo 里的对象是否形成独立前排对象

## 读取依据
- policy：`docs/BOT2_BOT3_POLICY.md`
- runtime：`docs/BOT2_BOT3_STATE.md`
- digest：`research/quant_digests/2026-03-30_1242_bucket-neutral-mr-funding-divergence-gate.md`
- 对照旧家族：`research/quant_digests/2026-03-23_1348_btc-neutral-residual-mean-reversion-raw-alpha.md`

## 这一步实际回答的问题
这条线到底是不是一个独立的前排对象，还是只是把已有 funding / stat-arb / residual-MR 材料重新包装了一遍。

## 核查结论
结论是：**可以作为独立 fresh intake 进入前排，但当前只到 `keep_P1`，还不升 `P2`。**

原因分三层：
1. **raw alpha 主体是明确且独立的。**
   它的主语不是泛 funding alpha，而是 `residual-correlation bucket` 内的 `1h return` 横截面均值回归：先按 residual correlation 动态分桶，再在 bucket 内做 robust z-score 反转，funding divergence 只是后接 confidence gate。这个对象边界和已有 funding carry / funding rotation 家族不同，也比旧的 `BTC-neutral residual MR` 更具体：旧线更像“单币相对 BTC 的残差极值回归”，这条则是“动态 bucket 内的横截面 relative-value MR”。
2. **最小可执行骨架已经够完整。**
   digest 已把 `5m` 数据、`12 bars=1h` horizon、`z_in/z_out/z_max`、`min_hold/max_hold`、`gross_target`、`单币/单 bucket 上限`、`dollar+beta neutral`、`next_open`、`fee/slippage`、`kill-switch` 都锁出来了，因此它不是 monitor，也不是只有故事没有执行口径的 scanner。
3. **但现在还缺 honest first follow-up。**
   当前证据主要来自 repo code/config 拆解；虽然足以说明对象成立、值得前排保留，但还没有把 `raw-only` 版本与 `raw+FDS gate` 版本放到统一成本口径下做最小 frozen replication。也就是说，它已经足够 `keep_P1`，但还没到直接 `promote_P2` 的程度。

## first verdict
- 正式分配：`Rank 256`
- verdict：`keep_P1`
- 层级去向：进入 fresh intake 记录，并作为后续可用的 survivor 候选

## 会改变系统认知的一句话
`Rank 256` 的核心不是 funding 本身，而是一个可独立复刻的 `dynamic residual-correlation bucket` 内 `1h` 横截面均值回归 raw alpha；由于 entry/exit/neutrality/caps/cost 骨架已清楚，它值得以前排 `keep_P1` 保留，但下一步必须优先做统一成本口径下的 `raw-only vs raw+FDS gate` honest replication。

## 本轮写回范围
- 更新 `Fresh intake slot` 为 `Rank 256`
- 更新 `cycle_plan` 第 3 项为 `done`
- 不改 policy / brief / cron prompt
- 不重排后续小点

## reader-facing
- 这是新 intake + 新 verdict，属于需要刷新首页的真实推进。
