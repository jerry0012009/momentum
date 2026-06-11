# bot3 optimization loop — anchored VWAP regime-extreme reversion first verdict -> background/P0

- 时间：2026-04-23 14:40 UTC
- 对象：`research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮执行
按 policy 对当前 front-slot fresh intake 只补 1 个最小 decisive blocker：它是否已经留下 **非单 anchor、非单月份 lucky-run 的 after-cost anchored-VWAP reversion pocket**，足以进入 `keep_P1`。

## 使用证据
- digest 原文：`research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`
- probe summary：`reports/artifacts/quant_digests/2026-04-23_avwap_regimeextreme_probe_summary.csv`
- trade ledger：`reports/artifacts/quant_digests/2026-04-23_avwap_regimeextreme_probe_trades.csv`

## decisive blocker 结果
现有 public-data probe 没有证明这是一条可独立排队的 crypto short-cycle anchored-VWAP reversion alpha：

- pooled 结果只有 `74` 笔，`gross +0.52 bps/笔`，粗扣 `8 bps` 后约 `-7.48 bps/笔`
- 只有 `BTCUSDT` 单桶在当前粗锚点定义下勉强为正：`22` 笔、`net +0.78 bps/笔`
- `ETHUSDT` 与 `SOLUSDT` 分别约 `-9.71 / -12.44 bps/笔`
- reclaim 触发率仅约 `21%~23%`，多数交易仍靠 timeout 退出，说明“向 AVWAP 回归”在当前最小定义下并不是稳定、厚实的主导机制
- 正边际集中在单币（BTC）且厚度极薄，尚不足以通过“非单 anchor、非单 lucky-run、可 after-cost 独立成立”的 first-verdict 门槛

## 为什么不进入 keep_P1
policy 要求 fresh intake 只有在已经显出独立 pocket 时才保留到 survivor。这里的 blocker 不是单一可继续前排补的小瑕疵，而是更根本的事实：

1. alpha 厚度在 broad crypto majors 上不成立；
2. 唯一正样本只剩 BTC 单桶、且成本后余量过薄；
3. 现有证据更像“AVWAP 可作为 BTC / maker-first / 更精细 anchor 的提示层”，不是已经足够前排占位的独立 raw alpha。

因此本轮直接收口到 `background/P0`，不占用 survivor。

## 会改变系统认知的话
`anchored VWAP regime-extreme reversion` 已完成 fresh intake first verdict 并收口 `background/P0`：现有 probe 只有 BTC 单桶在粗 `8 bps` 成本下勉强 `+0.78 bps/笔`，而 pooled / ETH / SOL 仍显著为负、AVWAP reclaim 率仅约 `21%~23%`，说明它目前只够当 BTC maker-first 精细 anchor 的提示层，不够作为独立 after-cost reversion pocket 进入 survivor。
