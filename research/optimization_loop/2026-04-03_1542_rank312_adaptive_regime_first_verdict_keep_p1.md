# Rank 312 — adaptive regime switch × trend/MR dual sleeve — first verdict keep_P1

- 时间：2026-04-03 15:42 UTC
- 轮次：bot3 13 分钟自动执行
- 对象：`research/quant_digests/2026-04-03_1020_adaptive-regime-switch-trend-mr-alpha.md`
- 本轮动作：fresh intake first verdict
- 结论：分配正式 `Rank 312`，first verdict = `keep_P1`，进入 `Surviving candidate slot`

## 为什么不是 P0
这条对象不是空泛“多策略大杂烩”包装，源码里确实已经写清楚了：
- `ATR expansion + ADX` 的 regime router；
- trend sleeve：`MA crossover + DI confirmation`；
- range sleeve：`BB overshoot + RSI fade`；
- 统一的 `ATR trailing stop`、仓位上限、手续费/滑点、drawdown kill switch。

也就是说，它不是只有因子描述，而是一个可独立回测、可独立下单、可独立做风险壳的完整策略对象，足够构成一条单独候选。

## 为什么还不直接升 P2
本轮不直接给 `promote_P2`，原因也很明确：
1. 当前公开证据主样本仍是 **90 天 hourly Hyperliquid** 回测，不是我们更关心的 `15m/5m` short-cycle admission 证据；
2. 当前 alpha 主体更像 **“regime router 把 trend continuation 和 range mean reversion 拼成一条完整壳”**，而不是已经证明 router 本身在 short-cycle / post-cost 上显著优于单腿 trend-only 或 MR-only；
3. digest 已经诚实写出下一步最关键的问题是 ablation：`regime-switched vs trend-only vs MR-only`，说明 admission blocker 还不是 wording，而是要验证 router 是否真产生新增系统认知。

## 会改变系统认知的一句话结果
`Rank 312` 不是单纯把常见 trend/MR 模块重新拼装成壳的空包装；它已经形成一条可独立 desk 化的 `regime-switched dual-alpha` 候选，但当前公开证据还不足以直接证明其在 short-cycle、成本后口径下优于单腿 sleeve，因此本轮先定为 `keep_P1`，不直升 `P2`。

## 对 survivor follow-up 的唯一便宜检查建议
若下一轮做 survivor 唯一一次 follow-up，最便宜且最 decisive 的检查应聚焦：
- 在统一 `BTC/ETH/SOL 15m` universe、统一成本口径下，
- `regime-switched` 是否相对 `trend-only` 与 `MR-only` 至少一边保留更稳定的 post-cost pocket，
- 且收益不是完全由单一 sleeve 或单一 meme-like 标的支撑。

若这一步成立，再考虑 `promote_P2`；若 router 只是把两个普通 sleeve 混在一起、ablation 后没有新增优势，则应诚实回到 `background/P0`。
