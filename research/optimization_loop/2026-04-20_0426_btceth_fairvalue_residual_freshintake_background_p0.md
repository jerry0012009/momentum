# bot3 optimization loop — BTC/ETH 双锚公平价残差回归 × spread stability gate

- Time: 2026-04-20 04:26 UTC
- Cycle item: `research/quant_digests/2026-04-20_0228_btceth-fairvalue-residual-spreadstability-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `background/P0`

## Why this step closes now
本轮要回答的唯一问题不是“工程壳是否完整”，而是：在默认参数已明显未过线后，这个题材是否还存在一个**诚实、最小、可承接的 re-calibrated residual pocket**，足以保留为 `P1`。

现有 digest 已给出最关键的最小重标定证据：

- `15m Base`: net `-19.77%`, max DD `-20.70%`, Sharpe `-6.48`, trades `143`
- `15m Stable60`（仅保留 spread stability 更高的前 40% 样本）: net `-11.09%`, max DD `-12.13%`, Sharpe `-6.85`, trades `60`
- `5m Base`: net `-21.95%`
- `5m Stable60`: net `-15.33%`

这说明：
1. `spread_stability` gate 确实能降低回撤和换手，但**不能把策略从负的 after-cost 区间拉回可承接的正 pocket**；
2. 负值不是只出现在默认 15m 参数，而是在更快的 `5m` 迁移和最小稳定度过滤后仍然成立；
3. 当前可见“re-calibration”仍停留在**工程壳可复用 / 未来可继续调参**的层面，而不是已经留下一个可以诚实保留到 survivor/P1 的单一 pocket。

## System-changing result
`BTC/ETH 双锚公平价残差回归 × spread stability gate` 没有证明自己在最小稳定度重标定后还能留下独立、可承接的 after-cost residual pocket；它当前只保留工程壳价值，不保留 front-slot，因此本轮 fresh intake 直接收口 `background/P0`。

## Runtime writeback
- Fresh intake：本条 digest first verdict -> `background/P0`
- No rank assigned（未达到 `keep_P1` 或更高）
- Background pool appended with this closure

## Notes
这次收口依赖的是**同一 digest 内已经存在的最小 blocker 检查结果**，没有扩展成第二个 pending 小点，也没有把“再调一轮参数网格”伪装成当前仍值得前排保留的理由。