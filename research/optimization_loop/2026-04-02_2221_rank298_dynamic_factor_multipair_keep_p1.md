# Rank 298 — dynamic factor multipair stat-arb intake keep_P1

- Time: 2026-04-02 22:21 UTC
- Object: `research/quant_digests/2026-04-02_2128_dynamic-factor-multipair-statarb-alpha.md`
- Verdict: `keep_P1`
- Rank assigned: `298`
- Slot impact:
  - `Fresh intake slot` -> `done`
  - `Surviving candidate slot` -> `Rank 298 / dynamic factor stripped multipair stat-arb`

## Why this is not just old pairs/PCA wording
这条对象已经具备一个独立、可复核的 raw-alpha 主语：

1. **信号主语明确**：先剥离共同市场因子，再根据 stationary 第二因子驱动的 forecast ranking 做多空轮换，不是单 pair z-score，也不是只讲解释框架。
2. **交易壳完整**：文中给了 rolling estimation、next-step forecast、top-half short / bottom-half long、threshold `c`、one-step hold 的闭环，已经能直接改写成 desk clean-room 最小实验。
3. **honesty gate 明确**：只有 `f2` 仍平稳、且 `corr(f1,f2)` 低于阈值时才交易；这不是事后修辞，而是策略定义的一部分。
4. **public-data path 可行**：高流动永续的 `15m` / `5m` 行情就足够先做两因子近似实验与成本分层，不依赖私有数据。

## Why it does not jump straight to P2
当前证据还停留在论文层与可执行 spec 层，尚未完成 clean-room transfer check；还没有回答下面这些 admission 级问题：

- 在我们可交易的高流动 perp universe 上，是否真能稳定出现 `integrated-like market factor + stationary factor` 的结构；
- `top-half/bottom-half` 与 `top-2/bottom-2 sparse` 哪个能活过成本；
- `15m` 下一根 / 两根 / 四根持有下，净收益与换手是否诚实；
- `ADF(f2)` 与 `corr(f1,f2)` gate 触发后，trade/no-trade 比例是否仍支持足够样本。

因此最诚实的一步是：**给它正式 Rank，保留到 P1，下一轮只做一次 survivor follow-up，验证 short-cycle clean-room transfer 是否成立。**

## System-changing result
`Rank 298` 不是旧 pairs/PCA family 的抽象重述；它已具备独立 raw-alpha 主语、完整 factor-gated 多对轮换交易骨架与 public-data clean-room 路径，因此 fresh intake first verdict 记为 `keep_P1`，进入 `Surviving candidate slot` 做唯一一次最小 follow-up。
