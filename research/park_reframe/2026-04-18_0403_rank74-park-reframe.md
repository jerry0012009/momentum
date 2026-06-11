# 2026-04-18 04:03 UTC — Rank 74 park reframe review

## Scope
- source rank: `Rank 74 / ADX+ER price-only trend-readiness gate`
- source evidence read:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`
  - `research/optimization_loop/2026-03-19_0140_rank74-clean-replication.md`
- new evidence checked this round:
  - `research/optimization_loop/2026-04-12_2032_rank74_freshintake_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-17_1700_rank74_fallback_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-11_0138_rank74_freshintake_first_verdict_background.md`

## Why Rank 74 this round
- 本轮继续遵守 `50~79 -> 80~110 -> 1~24 -> 25~49` 的低频轮转，优先仍看 `50+`。
- `Rank 74` 上一次 `bot6` park-reframe 复盘是 `2026-04-10 15:16 UTC`，已跨过 `7` 天窗口。
- 它在 4 月 10 日还保留了一个 `soft_reframe_candidate` 口径，但 4 月 11~17 又出现了 fresh-intake 首判分歧与 fallback 收口，适合低频复核这条 residual 是否已被消费。

## 1) 原 rank 为什么 park
原 `Rank 74` 被 park，不是因为 `ADX / ER` 完全没信息，而是因为它被写成了三条 archetype 共用的 `shared trend-readiness gate`。

`2026-03-19_0140_rank74-clean-replication.md` 已把 blocker 审计清楚：
- `breakout_short` 的 `adx_plus_er_plus_di` 确实从约 `-2.58%` 拉到约 `-0.48%`，但 `trade_count_retention≈41.22%`，改善主要来自砍样本；
- `ema_psar_long` 是“更少但没更好”，`adx_plus_er_plus_di≈-5.90%`，反而差于 baseline；
- `fib_retest_long` 只有 `ER only` 留下局部 pocket（约 `+2.16%`，但 `retention≈27.27%`），而 shared 主读法 `adx_plus_er_plus_di` 的 retention 已掉到 `≈6.06%`。

所以原 `park` verdict 的审计意义必须保留：
> **旧 Rank 74 作为 `ADX+ER+DI` shared gate，没有证明自己在三条 lane 上都提供了可独立部署的 trend-readiness 增量。**

## 2) 它更像 hard park 还是 soft park
结论：**从 4 月 10 日那轮的 `soft park`，进一步收紧到 `keep_park`，且现在更接近 `hard park with consumed residual`。**

原因：
- `soft` 的部分仍在：`fib_retest_long` 上的 `ER-only` 局部 pocket 不是纯噪声；
- 但更接近 `hard` 的部分已经更明确：这个 pocket 在 4 月中旬被拿去做过 fresh-intake 首判，最终又被 fallback 收口到 `background/P0`，说明它更像 family 内共享 residual，而不是还能诚实长成独立对象。

## 3) 有没有“可救信号”
有，但唯一可救信号仍只剩：
- **`fib_retest_long` lane 内的 `ER-only` trend-readiness pocket**。

4 月 12 日的 first verdict 一度给过它 `keep_P1`：
- `baseline` 约 `+1.33%`；
- `ER20 >= 0.20` 后约 `+2.28%`；
- 但平均每个 asset 只剩 `3` 笔左右，样本非常薄。

紧接着 4 月 17 日 fallback first verdict 又把这条 residual 压回 `background/P0`，理由也很直接：
- 它保留的语义已经不是旧 `shared ADX+ER+DI gate` 的独立继承物；
- 它更像 generic `pullback / trend-readiness` 过滤层；
- 与既有 `Rank 35b / Rank 40` 所代表的 pullback-quality / confirmation skeleton 高重叠。

所以当前“可救信号”仍然存在，但已经**不足以支撑继续命名为旧 Rank 74 的新派生对象**。

## 4) 最值得改的唯一一刀是什么
如果还要保留这条线唯一值得记住的一刀，它仍然只能是：

**把 `shared ADX+ER+DI gate` 收窄成 `Fib-family-local ER-only veto / admission`。**

但 4 月 17 日的 fallback 收口已经进一步说明：
- 这刀保住的是 `Fib pullback quality` 的 shared 语义；
- 不再是旧 `Rank 74` 自己足够独立的 queue-facing 主语；
- 继续写成 `Rank 74b`，会模糊原 `park` 的审计边界。

## 5) 是否值得形成新的 derived hypothesis
结论：**不值得；本轮应从此前的 `soft_reframe_candidate` 收紧为 `keep_park`。**

原因：
1. 原 `shared gate` 的 blocker 没被推翻；
2. 唯一 residual（`Fib-family-local ER-only`）已经被 4 月中旬的 fresh-intake / fallback 过程证明 distinctness 不够；
3. 现在再写 `Rank 74b`，更像给 generic pullback/trend-readiness filter 借旧 rank 换壳续命；
4. 因此更诚实的做法是：保留原 `park` verdict，并明确这条 residual 已被 family 吸收，不再保留 queue-facing soft 候选身份。

## 6) trade on / trade off（作为不派生的判断说明）
若勉强继续派生，理论上最像的一刀会是：
- `trade on`：在 `fib_retest_long` 上，仅用 `ER-only` 过滤“回踩后已失去顺推空间”的弱样本；
- `trade off`：放弃原 `ADX+ER+DI shared gate` 身份，也放弃旧 Rank 74 的独立主语，承认它只是 pullback / trend-readiness family 的 shared quality layer。

这恰好说明它已经不该再被命名成新的 `Rank 74b`。

## Final verdict
`keep_park`

## Short answer
- 原 rank 为什么 park：因为 `ADX+ER+DI` 当作 shared trend-readiness gate 时，只留下局部少亏/少量 pocket，没有证明跨 lane 的独立增量。
- 它更像 hard park 还是 soft park：现在仍可称 `soft park` 的尾巴，但已更接近 `hard park with consumed residual`。
- 有没有可救信号：有，但只剩 `Fib-family-local ER-only` 这条很窄的 pullback-quality residual。
- 最值得改的唯一一刀是什么：把 shared gate 收窄成 `Fib-family-local ER-only veto/admission`。
- 是否值得形成新的 derived hypothesis：不值得；4 月 17 日 fallback 已证明 distinctness 不够，当前更诚实的是维持 `keep_park`。

## File / git hygiene
- 本轮最小改动：
  - 新增本日志；
  - 更新 `research/park_reframe/INDEX.md`；
  - 更新 `docs/PARK_REFRAME_QUEUE.md`。
- 当前 git 工作区存在大量无关脏文件；为避免混提，本轮默认不做 commit。

## 邮件摘要建议标题
- `Rank 74 维持 park，ER-only残余收口`
