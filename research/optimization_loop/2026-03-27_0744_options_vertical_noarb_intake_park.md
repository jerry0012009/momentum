# Rankless options vertical no-arb intake -> park to background

- Time: 2026-03-27 07:44 UTC
- Target: `research/quant_digests/2026-03-27_0523_same-venue-options-vertical-noarb-alpha.md`
- Action type: fresh intake first verdict
- Policy basis: bot3 只执行当前 `cycle_plan` 最前的 pending 小点；首轮只回答这个对象是否值得保留成单一 same-venue / same-expiry vertical-spread no-arb raw alpha。

## Verdict
本轮给出 **park_to_background**，且**不分配 Rank**。

## Why
这条线的 clean-room 对象其实很清楚：同所、同到期、不同 strike 的 call/put top-of-book 若违反最基本单调性，就做 vertical spread 收敛。但当前 digest 已经把最关键的首轮问题回答得够明确了：

1. repo 里的 alpha 定义是完整的，不是空概念；
2. 但当前 Delta Exchange India 公共 live snapshot 上，按 repo 的相邻 strike 扫描，`BTC/ETH` 都是 **0 个 gross 违例**；
3. 就算放宽到任意 strike 对，也只看到 **ETH 当日到期 put 上 1 个 gross=0.01** 的极小违例；
4. 这个厚度离覆盖 options 双腿执行、买卖价差、手续费、legging risk 还差得很远；
5. 因而它更像“薄盘口 quote artifact / 监控素材”，还不像值得占用唯一 survivor 锁位的 raw alpha 前排对象。

## Runtime consequence
- 不进入 `keep_P1`
- 不占用 `Surviving candidate slot`
- 不进入 `Active P2`
- 直接记入 `Background pool`

## One-line result for state writeback
`same-venue / same-expiry vertical-spread no-arb violation` 这条 options intake 虽然对象定义清楚，但当前公开 live 盘口几乎没有可覆盖摩擦的 gross 违例，首轮不足以诚实保留为前排 raw alpha，因此本轮直接 `park_to_background`。
