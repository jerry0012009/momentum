# Rank 333 — dynamic-coint spread forecast × percentile trigger：first verdict = keep_P1

- Time: 2026-04-04 19:16 UTC
- Target: `research/quant_digests/2026-04-04_1855_dynamic-coint-dwe-percentile-pairs-alpha.md`
- Slot acted on: `Fresh intake slot`
- Verdict: `keep_P1`
- Assigned rank: `Rank 333`

## Why this changes system belief
这条对象不是又一版“spread 偏离就做回归”的旧 pairs 壳；它已经把最小可迁移 raw alpha 讲成一条完整链路：

1. **admission**：先做 dynamic-coint / Johansen（并允许回到更轻的 Engle-Granger + residual ADF clean-room 壳）；
2. **forecast target**：预测 future k-bar spread direction，而不是只看当前 z-score 偏离；
3. **trigger**：只在 forecast score 穿越上下 percentile threshold 时出手，天然带 signal thinning；
4. **exit shell**：forecast 翻向 / spread 回中性带 / 固定 time-stop 三选一或并用；
5. **cost shell**：明确要求与 plain z-score fade 在相同 cost / time-stop / admission 口径下做 A/B，而不是只拿 paper Sharpe 讲故事。

## First-verdict reasoning
- **Distinctness passed**：增量不在 deep-learning 叙事本身，而在 `dynamic-coint admission × spread-direction forecast × percentile trigger` 这条 forecast-driven pairs raw alpha 骨架；这与普通 z-score fade 有明确对象级区别。
- **Spec completeness passed**：digest 已把 `pair admission / forecast target / trigger threshold / exit-cost shell` 分账讲清，并且明确给出第一轮应做的 clean-room 路径：`15m` 主时钟、`5m` 下钻执行、对照 `forecast shell vs plain z-score fade`。
- **Honesty preserved**：digest 明说原论文主样本是日频、成本粒度不足、正文更接近 dynamic-coint 多资产 spread；因此当前只能得出“值得进 survivor 做一次便宜诚实 follow-up”，还不能直接升 P2。

## What is the single next cheap follow-up
唯一值得花的 survivor 预算，是做一个**spec-level honesty / distinctness 收口**：
- 先把对象压回最小两腿或小篮子 spread；
- 明确 `15m discovery -> 5m execution` 的 clean-room baseline；
- 只回答一个问题：**在同 admission / 同成本 / 同 time-stop 下，forecast shell 是否有机会系统性打赢 plain z-score fade。**

如果这一步连 clean-room 对照问题都讲不清，或 forecast shell 只是重新命名旧 fade，则应直接结束并回 background；如果问题保持清楚，才值得后续升到 P2 admission。

## Result sentence
`Rank 333`：`dynamic-coint spread forecast × percentile trigger` 已形成 distinct 且可迁移的 forecast-driven pairs raw alpha 骨架，first verdict 为 `keep_P1`，进入 survivor 做唯一一次 clean-room A/B follow-up。
