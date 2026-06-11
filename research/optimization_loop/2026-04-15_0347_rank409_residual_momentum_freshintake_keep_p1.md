# Rank 409 fresh intake — BTC-beta-neutral residual momentum alpha（keep_P1）

- 时间：2026-04-15 03:47 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：#2 `research/quant_digests/2026-04-15_0237_btcbeta-neutral-residualmomentum-alpha.md`

## 本轮执行
1. 复核 source digest 的最小可复现证据（Binance USDⓈ-M 15m portability probe）：
   - residual 版本相对 raw momentum 明显减噪（IC/Sharpe 方向更优）；
   - 但统一 one-way 4 bps 后仍未过线（net Sharpe 仍为负）。
2. 做最小 honesty/execution realism 子检查（源码级）：
   - `alpha_14_residual_momentum.py` 的 residual 累积使用 `residuals.shift(skip_days)` 后再 rolling sum，未见同 bar 未来信息直连；
   - 但 repo 默认 `market_ret = returns.mean(axis=1)`，属于“当期横截面均值市场因子”，对 live 执行不等价于可交易对冲腿；若 desk 落地，需改为可交易 proxy（如 BTC 或 BTC+ETH）。

## 结论（first verdict）
`Rank 409 / BTC-beta-neutral residual momentum ranking shell`：保留 `keep_P1`，不进 `P2`。

一句改变系统认知的话：
> 该 alpha 家族在短周期上“去 beta 减噪”是成立的，但当前证据仍停留在“质量改善而非费后可交易正收益”，且 live 对冲因子定义需从截面均值替换为可交易 market proxy，故先留在 P1。

## 唯一 survivor follow-up blocker
在 `1h` 主频上完成一次“可交易 market proxy（BTC vs BTC+ETH）+ residual continuation/reversal 符号对照”的单次验证，并在统一成本下拿到明确费后正 pocket；否则回收至 background。
