# bot3 optimization loop log — 2026-04-18 10:22 UTC

## 执行对象
- cycle item: 1
- target: `research/quant_digests/2026-04-18_0621_funding-4h-context-divergence-overlay.md`
- action: fresh intake first-verdict

## 本轮最小检查
按 policy 只做 1 个最小、最便宜、最能改变结论的 honesty / execution realism 子检查：
- 不再泛看 paper headline；只检查这条线是否已经收敛成 **BTC/ETH 上单边 anti-chase veto 的明确可承接 pocket**，且粗口径上足以跨过最小执行成本门槛。

读取的现成 portability artifact：
- `reports/artifacts/quant_digests/2026-04-18_funding_4h_context_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_funding_4h_context_probe_portfolio.json`

## 关键证据
组合层面先否掉 headline continuation：
- `all_align`: next `4h=-5.44bps`, next `8h=-22.61bps`
- `strong_align`: next `4h=-9.59bps`, next `8h=-56.38bps`
- 说明这篇东西**不能**诚实地保留成新的 `funding-confirmed continuation` front object。

再看最像可承接 pocket 的单边 divergence：
- BTC `down_pos_fade_candidate`: next `4h=+18.79bps`, next `8h=+39.11bps`, `n=43`
- ETH `up_neg_fade_candidate`: next `4h=+11.92bps`, next `8h=+23.29bps`, `n=49`

但这两个 pocket 目前仍只停留在 **gross event study**：
- 入场定义仍是 funding 结算后的 bar-open proxy；
- 尚未给出 `t+2` / child execution / maker-taker ladder / slippage after event；
- BTC/ETH 两个 pocket 方向不对称，说明它更像 continuation alpha 的 **anti-chase veto overlay**，而不是一条已经自洽、可独立排前的 shared overlay front object；
- 若粗扣最常见的短周期 round-trip friction（约 `6~8bps+`），ETH `4h` pocket 余量已经很薄；而 overlay 本身又没有独立母体 PnL 来证明它在真实执行后仍能稳定改善 after-cost outcome。

## first verdict
本轮 fresh intake 直接收口 `background/P0`。

一句会改变系统认知的话：
> `4H directional move × funding disagreement` 当前公开 portability 虽在 BTC/ETH 各留下一个单边 anti-chase gross pocket，但它们仍只是未扣 child-execution / friction ladder 的 event-study 余量，且对象本质更像依附既有 continuation 母体的 overlay 提示，不足以作为新的 shared overlay front object 保留，因此本轮 fresh intake 直接收口 `background/P0`。

## runtime writeback
- fresh intake slot: 清空 `current_target`
- cycle item 1: `done`
- 不分配新 Rank（因为 verdict 不是 `keep_P1` 或更高）

## tail steps
- homepage publish: best effort，独立命令执行
- email: 独立命令执行
