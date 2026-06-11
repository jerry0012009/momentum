# Rank 286 — adjacent-maturity calendar-spread ratio dislocation × carry normalization：first verdict = keep_P1

- 时间：2026-04-02 00:26 UTC
- 对象：`adjacent-maturity ratio dislocation × carry normalization`
- 来源：`research/quant_digests/2026-04-01_2252_adjacent-maturity-calendar-spread-alpha.md`
- 本轮角色：bot3 当前唯一 pending 小点执行

## 本轮结论

这条 fresh intake 已经形成**可独立审计的 futures-curve relative-value raw alpha skeleton**，因此本轮正式记为 `Rank 286` 并首判 `keep_P1`。

它能进入前排的原因很具体：

1. alpha 本体清楚，不是泛泛的“做 carry”——真正值得保留的是**相邻到期 calendar spread 在按剩余天数归一后出现 ratio dislocation，并向理论 carry 比值回归**这条 raw alpha；
2. digest 已经把最小交易壳写得足够完整：对象是同一标的相邻 dated futures，信号是 `days-normalized spread ratio` 偏离理论比值，entry/exit、pre-expiry cutoff、time-matched sizing、cost ladder 与 roll/legging 风险都已明确；
3. repo 给出的 trade shell 不是空叙事，而是明确的 `35d/28d ≈ 1.25` 理论锚、`4×35d vs 5×28d` 的基础配比，以及 `equal absolute spread pricing + 2–3σ deviation + implied carry divergence` 的入场框架；
4. 这条线在当前素材池里也有独特性：它补的是 `futures-curve internal relative value` 这一栏，而不是再堆一条 funding / pairs / directional momentum 变体。

但这轮还不能诚实地直升 `P2`，原因同样明确：

1. 当前硬证据仍主要来自 repo 自述与研究摘要，不是我们已经在 Binance Delivery / OKX dated futures 上完成的 clean-room replication；
2. digest 虽然明确了可做的最小实验口径，但目前还没有回答最关键的 desk 问题：**公开可拿的 dated futures 上，days-normalized spread ratio 的回归是否稳定到足以穿过 realistic fee + roll + legging friction**；
3. repo 报出来的 `15 months CAGR 8%, Sharpe 1.4` 与近 `6 months Sharpe 4.0` 只能当线索，不能当 admission evidence；
4. 这类 alpha 天然受制于合约可得性、期限窗口稀疏、曲线 regime 切换与 pre-expiry execution，若这些现实约束下 signal 只偶发出现，它更可能是一个 niche carry bucket，而不是已经接近 paper launch 的对象。

所以更准确的口径是：

> `Rank 286` 值得保留的，不是“crypto futures 有 carry”这种老叙事，而是“相邻期限 spread 在按剩余天数归一后会不会出现可持续回归的 ratio dislocation”这条可审计 raw alpha；在公开 dated futures clean-room replication 与 friction 后验证完成前，它应停在 `keep_P1`，不应直接跳升 `P2`。

## 为什么不是 P0

因为它已经具备一个可迁移、可验证的最小策略定义：

- universe：有（BTC / ETH 的相邻 dated futures）；
- signal：有（`days-normalized spread ratio` 偏离理论 carry 比值）；
- entry/exit：有（`z=2/2.5/3` 入场、回理论 band 或 `|z|<0.5/1.0` 退出、expiry cutoff）；
- sizing/risk：有（time-matched ratio、bucket cap、roll cutoff、legging risk）；
- cost realism：有（maker/taker friction ladder + roll slippage 假设）；
- transfer path：有（先测公开 venue 的 `5m/15m` ratio panel，再看 fee 后是否仍有 pocket）。

这已经超过“只有术语、没有壳子”的程度，足以保留为 survivor。

## 为什么不是 P2

因为 admission 还缺最关键的一层现实检验：

1. Binance / OKX / Bybit 等公开可得 dated futures 上，是否真的能稳定拿到相邻期限、且 trade count 不至于过稀；
2. `5m/15m` 监控下的 ratio reversion，在 maker/mixed/taker 成本与 roll slippage 后，净 pocket 是否仍为正；
3. 这条线是只活在少数到期窗口，还是能跨 BTC / ETH 与不同期限段稳定存在；
4. curve 从 contango 切到 backwardation 时，理论比值是否仍有足够稳健的 reversion 含义。

这些问题没回答前，把它升到 `P2` 会把“值得做一次便宜诚实 replication”的对象误写成“已接近 paper-worthy”。

## 对 runtime 的实际影响

- 新分配正式 `Rank`：`286`
- 当前 fresh intake 首判：`keep_P1`
- survivor 槽应切换为 `Rank 286`
- 唯一 follow-up 应直接检查：在公开可拿的 BTC / ETH dated futures 上，`days-normalized adjacent-maturity spread ratio` 的回归是否在 realistic fee / roll / legging friction 后仍保留净 pocket。
