# 2026-04-16 04:00 UTC — item2 `funding extreme × tight TP volatility harvest` fresh-intake first verdict

## 执行动作
- 对 `research/quant_digests/2026-04-16_0257_fundingextreme-tighttp-volharvest-shell.md` 执行 fresh-intake first-verdict。
- 口径：沿用 repo 内统一 after-cost 回测（taker/taker round-trip `11bps`，`TP=2% / SL=4%`，`lookback=168`，`threshold=2.0`），并做最小 honesty 子检查：`delayed-confirmation (+1 funding interval)`，排除同刻信号-成交的潜在泄漏乐观偏差。

## 证据与产物
- 新产物：`reports/artifacts/optimization_loop/2026-04-16_fundingextreme_tighttp_delaycheck_eval.json`

关键结果（`vol+OI` 过滤版本，base -> delay+1）：
- BTC mean-reversion：`+1.101% -> +0.501%`（`-0.600%`）
- BTC momentum：`+0.501% -> -0.510%`（转负）
- ETH mean-reversion：`-2.376% -> -2.187%`（持续为负）
- ETH momentum：`+1.224% -> +0.624%`（显著收缩）
- SOL mean-reversion：`+0.312% -> -0.888%`（转负）
- SOL momentum：`+0.312% -> +0.312%`（低幅、无增益）

## 本轮结论（first verdict）
`funding extreme × tight TP volatility harvest` 在统一成本口径下呈现“方向依赖 + 资产依赖 + delayed-confirmation 后显著衰减/转负”的不稳结构，未形成可直接前排保留的可复制费后 pocket；本轮 fresh intake 直接收口 `background/P0`（不进入 survivor，不分配 Rank）。
