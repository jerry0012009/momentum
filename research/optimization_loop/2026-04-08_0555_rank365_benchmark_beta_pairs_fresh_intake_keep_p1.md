# Rank 365 / benchmark-beta return differential × thresholded pair fade — fresh intake first verdict

- Time: 2026-04-08 05:55 UTC
- Target: `research/quant_digests/2026-04-07_2321_benchmark-beta-pairs-meanreversion-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `365`

## Why this changes runtime truth
`benchmark-beta adjusted relative return gap -> thresholded pair fade` 已经不是泛 pairs-trading 教科书表述，而是一个可独立复现、可直接落地最小 clean-room 实验的 raw alpha：主语明确是 `先对 crypto benchmark 去 beta -> 再交易 residual / return differential mean reversion`，并且已经给出统一宿主（majors perp）、统一时间框架（先 15m，再 5m）、统一成本口径（双腿 round-trip 8/16/24 bps）与最小 entry/exit 壳（|z| 入场、z→0 / time-stop 出场）。

## Evidence used
1. Digest 明确把基础 alpha 写成 `beta-adjusted return differential residual 的均值回复`，不是简单价格比值 / 相关性配对。
2. Digest 明确标注 `是否可独立复现：是`、`是否可直接落地完整策略：是`。
3. 最小实验口径已收敛：top 8~10 liquid perp、rolling 3d beta、`eps_t = (r_i - β_i r_m) - (r_j - β_j r_m)`、再累积 spread 并做 z-score / ADF / half-life 过滤。
4. 成本与执行诚实性已被前置写出：双腿合并 round-trip 成本、maker-first / taker fallback、time-stop、事件 veto。

## Why not higher than P1 yet
当前仍缺三类会决定是否升 `P2` 的 clean-room 证据：
1. benchmark 定义敏感度（cap-weighted / equal-weight / liquidity-weighted proxy）是否会让 residual 稳定性明显漂移；
2. 相对简单的“原始价差 z-score”基线相比，post-cost `PnL / pair-day` 与 `positive pair ratio` 是否真的更稳；
3. 在当前 majors perp 样本上，edge 是否主要来自 beta-neutral residual，而不是旧式 pairs MR 在特定子样本上的偶然存活。

## Slot handling
当前 `Surviving candidate slot` 仍被 `Rank 364` 合法占据，按 policy 不应被新的 `keep_P1` 自动覆盖；因此本轮只给本对象分配正式 `Rank 365` 并写入 fresh-intake 结果，不擅自改写 survivor 槽位。

## Result sentence
`Rank 365` 已把 `benchmark-beta adjusted relative return gap -> thresholded pair fade` 压成独立 raw alpha 与最小 clean-room 实验壳，因此 fresh first verdict 为 `keep_P1`；但在 `Rank 364` survivor 锁仍存在时，本轮只分配正式 rank 并留在 fresh-intake 结果层，不直接挤占 survivor 槽。
