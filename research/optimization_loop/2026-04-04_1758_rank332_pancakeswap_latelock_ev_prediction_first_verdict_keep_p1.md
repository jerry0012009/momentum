# Rank 332 — PancakeSwap late-lock EV prediction first verdict: keep_P1

- 时间：2026-04-04 17:58 UTC
- 对象：`research/quant_digests/2026-04-04_1455_pancakeswap-latelock-ev-prediction-alpha.md`
- 轮次角色：bot3 13 分钟自动执行
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`，进入 `Surviving candidate slot`

## 为什么不是直接丢回 background
这条题材已经不是“自动下注脚本”或“跟 crowd / 反 crowd”的粗糙叙述，而是完整的 raw alpha 壳：

1. **赔率端是公开且实时可读的**
   - `bullAmount / bearAmount` 直接给出 crowding 与 payout skew；
   - `5m` round、`3%` fee、lock/close 结算规则明确；
   - 可以把每侧 break-even 胜率门槛写成显式函数，而不是凭感觉下注。

2. **概率端至少有最小可运行 baseline**
   - repo 已给出 recent rounds momentum / streak reversal 这类 `p_hat` 初版；
   - digest 还明确可以接外部现货 `1m/3m` 微动量；
   - 因此不是“只有赔率没有胜率”，而是已经具备最小 EV 决策闭环。

3. **entry / exit / sizing / cost 都已具备可实验壳**
   - entry：lock 前 `15~20s`；
   - exit：固定到期结算；
   - sizing：fixed stake / clipped EV；
   - cost：已把 fee、gas、tie risk、tx timing risk 明确写进。

4. **主语独立，不需要寄生在别的 perp alpha 上**
   - 它的 raw alpha 主语就是 `late-lock pool imbalance × payout-aware EV switch`；
   - 即使用未来把它拿去做 perp confirm，那也是二级用途，不影响它先作为 prediction-market 原生策略成立。

## 为什么这轮还不直接升 P2
当前仍有一个决定性 blocker 没收口：

**需要确认公开池子金额在 lock 前最后十几秒的可交易性是否真实成立，且不是被 pending self-bet / tx ordering / inclusion latency / oracle timing 偏差系统性污染。**

也就是说，现在策略壳已经足够像一条真的 alpha，但还差一次 survivor 级别的诚实检查：
- late-lock 时点看到的 `bull/bear` 金额，是否就是你实际下注时能基于它下决策的 canonical state；
- 若最后几秒池子仍会被大额下注显著改写，或 tx 经常赶不上 lock，则 repo 里的 EV switch 可能只是回看成立、实盘壳不成立。

## survivor 唯一 follow-up 应该测什么
只做这一个 cheap decisive follow-up：

**`lock 前 60s/30s/20s/15s/10s` 的 pool imbalance snapshot vs 最终 locked pool` 稳定性审计**

目标不是直接做大回测，而是先回答：
- late-lock crowding / payout skew 在最后十几秒是否足够稳定；
- 这个状态变量能否作为真正可执行的 decision input；
- 若不稳定，是否直接塌缩为“回看赔率漂亮、实盘状态不可抓”。

## 本轮 verdict
`Rank 332`：`late-lock pool imbalance × payout-aware EV switch` 已经具备独立 prediction-market raw alpha 主语、明确 break-even / EV 计算与最小下注壳，因此 fresh intake 首判 `keep_P1`；当前唯一 decisive blocker 收敛为 late-lock visible pool state 是否在可下注时窗内保持可交易稳定。