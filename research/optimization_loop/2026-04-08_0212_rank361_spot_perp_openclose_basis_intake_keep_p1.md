# Rank 361 / spot-perp executable basis × open/close hysteresis shell / fresh intake keep_P1

- Time: 2026-04-08 02:12 UTC
- Operator: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
- Verdict: `keep_P1`
- Assigned Rank: `361`

## What changed system truth
`spot-perp executable basis × open/close hysteresis shell` 已经足够作为一条独立 raw alpha intake 进入前排，不应再被并回泛化的 `funding / carry / basis` 教程叙事。它压清的主语不是“哪边 funding 高”这种慢变量，而是 **same-underlier、可成交、可净额化的 spot-perp basis 偏离**：当 `perp bid - spot ask` 或 `spot bid - perp ask` 扣掉双腿 fee / slippage 后仍显著为正，就开对应的 delta-neutral 双腿；持仓后不按原方向继续追，而是等 **反向 close spread** 回到平仓阈值再退出。这个 alpha 的核心是 `open/close hysteresis` 下的 executable spread capture，而不是泛 carry 故事。

## Why this is keep_P1 instead of background/P0
- digest 已把 `same-underlier executable basis dislocation -> close-spread mean reversion` 的唯一主语写清，不是只说“funding 可能有用”。
- 证据不是空泛概念，而是成熟源码里已经落地的策略壳：双向 executable spread 公式、开/平仓阈值、slippage buffer、reopen delay、position mode、状态机与 budget check 都是现成定义。
- 这让对象具备了明确的最小 clean-room 复刻问题：在当前 crypto 可成交 quote 与成本口径下，这个壳是否还能留下独立的 after-cost spread-capture 证据？因此它值得保留一次 survivor follow-up，而不是直接打回背景池。

## Why not promote to P2 yet
- 当前证据主要证明的是 **工程壳完整**，还没有证明在现在的 Binance majors / spot+perp lane 上，这个壳扣完真实费率、滑点与 funding 后仍有稳定净 edge。
- 默认 `1%` entry / `-0.1%` close 更像保守模板，不是 production 参数；对象还缺少当前市场上的成本后 trade count、median open duration、avg trade 与稳定性读数。
- 因此它已经足够成为 `keep_P1` 的 survivor，但还没到直接进入 `P2 admission` 的程度。

## Explicit decisive follow-up question
唯一值得保留给 survivor 的便宜决定性 follow-up 是：**在当前 BTC/ETH spot+perp 的 executable quote 口径下，这个双阈值壳相对泛 funding/carry 叙事，是否真能产出独立的 after-cost spread capture，而不是只剩成熟框架代码的可部署性？**

## Runtime write-back required
- 为该 fresh intake 分配正式 `Rank 361`。
- `Fresh intake slot` 本轮结果写为：`Rank 361：spot-perp executable basis × open/close hysteresis shell 已压清为独立于泛 funding/carry 叙事的 executable same-underlier dislocation intake，因此 first verdict = keep_P1`。
- `Surviving candidate slot` 切换到 `Rank 361`，并保留唯一 1 次 follow-up 预算。