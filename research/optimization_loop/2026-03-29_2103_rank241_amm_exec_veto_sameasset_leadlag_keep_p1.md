# Rank 241 / AMM executable-price reconstruction × slippage/gas veto / same-asset lead-lag / keep_P1

- 时间：2026-03-29 21:03 UTC
- 轮次动作：`cycle_plan` 第 2 项（首个 pending）
- 目标主语：`same-asset relative-value / lead-lag` 家族的 shared execution veto
- 来源 digest：`research/quant_digests/2026-03-29_1619_amm-book-slippage-veto-sameasset-leadlag.md`

## 这轮只回答一件事
这条对象是否已经足够独立到值得从 digest 升成新的 queue-facing fresh intake。

## 这轮证据
1. 这不是在重复造一个新的 `CEX 领先 DEX` raw alpha。本地素材池里已经有 `2026-03-26_0922_cex-dex-eth-leadlag-spread-alpha.md`、`2026-03-26_0252_futures-lead-spot-lag-spread-alpha.md`、`2026-03-25_1705_btc-cross-exchange-spread-vol-congestion-pocket.md` 等 same-asset / cross-venue raw alpha 主语，raw-alpha 本体并不稀缺。
2. 这篇新 digest 的独立主语是清楚的：不是方向预测，而是 `naive mid-gap` vs `executable spread after fee/gas/slippage` 的 admission A/B；它要求先把 AMM / 薄深度腿的可执行价、滑点、fee、gas 重建出来，再决定这笔 lead-lag / basis 单能不能做。
3. 它和泛泛的 `execution realism` 不同，因为服务边界已经收窄到 `same-asset relative-value / lead-lag` 家族，且最小实验也写死了：`ETH Binance ↔ Uniswap` 近 `60~90` 天 `1m` A/B，对比 naive mid-gap catch-up 与 executable-gap gate，并输出 `trade count / net pnl / p95 loss / gas 分位表现`。
4. 但它当前仍只是 intake 级证据：还没有任何已落库的 `with veto vs without veto` 策略级净增量来证明这层 gate 在现有 same-asset 线里真的能留下更厚的成本后边。因此现在只能给 `keep_P1`，不能直接升 `P2`。

## 结论
这条对象已经足够独立，不该被压成“只是论文复述”或泛 execution 备注；应正式立为新鲜 intake，并分配下一个未使用整数 `Rank 241`。

正式命名：`Rank 241 / same-asset executable-spread veto`

本轮 first verdict：`keep_P1`

一句会改变系统认知的话：

> `AMM executable-price reconstruction × slippage/gas veto` 已足够独立成 `Rank 241 / same-asset executable-spread veto`：它不是重复讲 `CEX 领先 DEX`，而是把 same-asset lead-lag / basis 家族真正缺的 `naive mid-gap vs executable spread after fee/gas/slippage` admission A/B 单独钉成 shared execution filter，因此本轮 fresh intake 记为 `keep_P1`，但在出现策略级 with/without overlay 净增量前不升 `P2`。

## 回写要求
- `BOT2_BOT3_STATE.md`：将 Fresh intake slot 改写为 `Rank 241 / same-asset executable-spread veto`
- `cycle_plan` 第 2 项：写入上述结果并标记为 `done`
- 不改 policy / brief / operating card / cron prompt
