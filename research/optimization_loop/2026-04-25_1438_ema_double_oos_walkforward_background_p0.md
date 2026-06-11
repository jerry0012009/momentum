# Rank none / EMA double-OOS walk-forward shell first verdict -> background/P0

- Time: 2026-04-25 14:38 UTC
- Target: `research/quant_digests/2026-04-24_1938_ema-double-oos-walkforward-shell.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this changed system belief
这篇材料**没有给出足够证据证明至少一个 `15m signal + 5m execution` 的 after-cost EMA trend pocket 明显成立**；当前更可信的结论是：

> `EMA fast/slow crossover × double-OOS walk-forward` 目前应保留为 **methodology / honesty discipline**，而不是进入 survivor 的可交易 short-cycle raw alpha。

## Minimal decisive blocker checked
本轮只补了一个最小 decisive blocker：

- 上游 paper / repo 是否拿出了能支撑 `15m signal + 5m execution`、成本后仍明显存活的具体 tradable pocket，还是只证明了 walk-forward / single-time unseen 这套方法学更诚实。

## Evidence used
1. digest 已明确写出：
   - 原论文最好的 unseen 结果**集中在 `60m`**；
   - 对我们 desk 更关键的 `5m/15m` 只是“可映射、可复测”，并**不能直接等同于已证明成立**。
2. 上游 analysis README / paper abstract 一致表述：
   - unseen period 里，策略与 buy-and-hold **performed similarly**，主优势在 **lower drawdown / higher Information Ratio**；
   - cross-asset validation 只展示 BTC 参数迁移到 ETH / BNB 的方向性稳健；
   - strongest portfolio claim 也是 `buy-and-hold + strategy` 的组合降低回撤约 50%。
3. 上游 reproduction README 里真正明确排队复现的 unseen runs 只有：
   - `general.tfmin=60`
   - `train/test = 14/10` 与 `7/28`
   也就是说，作者正式强调并复现的 unseen 核心验证点仍是 **60m**，而不是我们 success criterion 要求的 `15m signal + 5m execution` 口径。
4. 当前公开材料没有给出：
   - 某个具体 `15m` EMA pair 在统一成本后仍明显为正；
   - `15m fixed params` vs `15m WFO` 的 pocket 级对照，能证明 WFO 不只是回撤更好而收益同样偏薄；
   - 任何 `5m child execution` artifact / trade ledger / after-cost trade pocket。

## Why not keep_P1
`keep_P1` 的门槛是：至少一个 `15m signal + 5m execution` 的 after-cost EMA trend pocket 明显成立，且 WFO 优势不只是“更稳/回撤更低”。当前公开证据没有满足这个门槛。

更具体地说：
- 这篇东西证明了 **double-OOS discipline 很值得抄**；
- 但它**没有证明** short-cycle crypto desk 现在已经拿到一个可直接保留的 `15m+5m` EMA crossover alpha pocket；
- 若继续推进，下一步更像“把这套 honesty framework 套到别的 raw alpha 上”，而不是继续给这条 EMA 壳 survivor 预算。

## Runtime impact
- 当前 fresh intake 诚实收口为 `background/P0`。
- front slot 应顺延到下一条 pending intake：`research/quant_digests/2026-04-24_2120_tightened-supertrend-feeaware-verdict.md`。

## One-line result
`EMA fast/slow crossover × double-OOS walk-forward` 当前只证明了 WFO / unseen honesty 与 beta-diversification value；公开证据没有拿出一个满足 `15m signal + 5m execution` success criterion 的 after-cost tradable trend pocket，因此 first verdict 收口为 `background/P0`.
