# Rank 358 / benchmark-beta return differential × thresholded pair fade intake：keep_P1
- 时间：2026-04-08 00:02 UTC
- 类型：bot3 optimization loop
- 对象：`research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
- 结论：`keep_P1`
- Rank：`358`

## 本轮判断
这条 fresh intake 已经足够作为独立 raw alpha 进入 `P1`，不该被并回“老式 pairs 换壳”。核心不是 plain spread / plain z-score，而是**先对两条腿分别做 market benchmark beta 去市场化，再对 beta-adjusted return differential 做 thresholded pair fade**。这一步把 alpha 主语从“相关性高的两条腿”改成了“共同 beta 已剥离后仍会回归的 idiosyncratic residual”，和现有 `plain z-score / cointegration / OU pairs` 家族存在清楚职责分界。

## 为什么不是直接丢回 background
1. **独立性已压清**：digest 已明确最小定义 `eps_t = (r_i - β_i r_m) - (r_j - β_j r_m)`，并要求双腿合并成本、rolling ADF/cointegration pass、半衰期筛选；这不是泛泛的 old-school correlation pairs。
2. **执行壳已足够具体**：`15m -> 5m`、`3d` rolling beta、`|z|>1.5/2.0` 入场、`z→0` 或 `8 bars` time-stop、`8/16/24 bps` 双腿 round-trip 成本，这些已经够支撑一个 survivor follow-up，而不是只有摘要级概念。
3. **与旧 desk family 的区别成立**：当前 desk 已有很多 `cointegration / z-score / OU` 壳，但 digest 明确指出“先 market-neutralize，再做 pair fade”尚未被单独拿出来做最小实验，因此它是新的 raw-alpha 入口，而不是旧壳同义改写。

## 为什么本轮先停在 P1
还没到 `promote_P2`，因为有一个决定性口径仍未压实：**benchmark 定义本身**（cap-weighted / equal-weight / OI-weighted / liquidity proxy）会直接改写 beta 与 residual 稳定性，目前还只是 digest 级建议，没有通过最小 A/B 把“beta-adjusted spread 比原始 spread 更稳”压成对象自己的 admission 证据。所以最诚实的 first verdict 是 `keep_P1`，并把唯一 survivor follow-up 留给 benchmark proxy 与 simple baseline 的最小对照。

## 对 runtime 的影响
- 分配新正式身份：`Rank 358`
- 对象从 `Fresh intake slot` 升为新的 `Surviving candidate slot`
- survivor 唯一 follow-up 应聚焦：`benchmark proxy choice + raw spread baseline` 是否真的让 beta-adjusted residual 在 `15m/5m` 上更稳、更有 after-cost 增量
