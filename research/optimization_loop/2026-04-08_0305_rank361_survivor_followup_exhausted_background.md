# Rank 361 / spot-perp executable basis × open/close hysteresis shell / survivor follow-up exhausted -> background

- Time: 2026-04-08 03:05 UTC
- Operator: bot3 auto loop
- Source intake: `research/quant_digests/2026-04-08_0012_spot-perp-openclose-basis-shell.md`
- Prior intake verdict: `research/optimization_loop/2026-04-08_0212_rank361_spot_perp_openclose_basis_intake_keep_p1.md`
- Survivor action: the one allowed cheap decisive follow-up
- Verdict: `keep_P1 exhausted -> background`

## What changed system truth
`Rank 361` 证明了 Hummingbot 的 `spot_perpetual_arbitrage` 是一套成熟的 same-underlier spot+perp 执行壳，但就当前 desk 已有的可成交 basis 证据口径看，它还没有留下足够独立的 **after-cost spread-capture** 证据；因此这条线本轮应诚实收口为 `keep_P1 exhausted -> background`，而不是升 `P2`。

## Decisive evidence used
本轮不再重复做新的同维度实验，直接用当前项目里已存在、且最接近该对象主语的两组运行证据收口：

1. `reports/artifacts/quant_digests/2026-03-30_samevenue_basis_revert_quickcheck.json`
   - 这是同 venue、same-underlier basis 回归的快速检视。
   - 对 `BTCUSDT / ETHUSDT / SOLUSDT`，在 `4~16` bars 的非重叠持有口径下，**平均 gross capture 只有约 `1.43 ~ 3.28 bps`**。
   - 该读数连双腿 taker fee 都很难覆盖，更别说再叠加滑点与跨 funding 持仓 frictions。
   - 这说明当前 majors 上的可见回归幅度更像“方向是对的，但肉太薄”，不足以单独支持 queue-facing 的 after-cost alpha 结论。

2. `reports/artifacts/rank179_basis_survivor_followup_20260326/summary.json`
   - 这是更系统的 basis 组合跟进证据。
   - 在 `12 bps` 成本口径下，主结果 `primary_best_12bps.mean_net_bps = -10.98`，更严格切法 `strict_16x32_12bps.mean_net_bps = -12.53`，正收益 symbol ratio 也只有 `0.14 ~ 0.17`。
   - 换句话说，**只要把真实成本抬到接近可成交世界，basis 回归主语就从“看起来会收敛”变成“净值不够活”**。

## Why this is enough to close the survivor
`Rank 361` 的 survivor follow-up 只需要回答一个问题：

> 在当前 BTC/ETH 等 liquid majors 的 spot+perp executable quote 与真实费率/滑点/funding 口径下，这个 Hummingbot 双阈值壳是否仍保留独立于泛 funding/carry 叙事的 after-cost spread-capture 证据？

答案现在更接近：**没有。**

更准确地说：
- 有的是 **成熟执行模板**；
- 缺的是 **当前 market lane 上可复述、可过成本的净 edge**。

这意味着它适合作为将来别的 basis/funding 候选的工程宿主或 execution shell 参考，但不该继续占用前排 survivor 资源。

## Why not promote_P2
按 policy，`P2` 不是“工程代码写得完整”就能进，而是要开始接近可 admission 的独立对象。`Rank 361` 目前没有给出：
- 当前 majors 上足够厚的 after-cost trade capture；
- 清楚能覆盖 fee/slippage/funding 后仍为正的 trade count；
- 相对泛 basis/funding 家族的新增 edge，而不只是更成熟的 strategy wiring。

因此它不满足本轮 `promote_P2` 条件。

## Result sentence for runtime
`Rank 361` 的唯一 survivor follow-up 已收口：当前项目已有 same-venue basis quickcheck 与 basis follow-up 证据都显示 gross/after-cost capture 不足以支撑独立 queue-facing alpha，因此该对象作为成熟 execution shell 保留证据，但本轮诚实结论为 `keep_P1 exhausted -> background`。

## Ops note
- 已按流程发送中文邮件摘要到默认收件人。
- 已两次尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 刷新首页，但进程均被系统 `SIGKILL`；本轮运行态与日志已落库，首页刷新需后续轮次或人工重试。
