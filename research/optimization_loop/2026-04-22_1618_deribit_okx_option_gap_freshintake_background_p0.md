# Deribit ↔ OKX 同合约 option quote-gap fresh intake：background/P0

- 时间：2026-04-22 16:18 UTC
- 对象：`research/quant_digests/2026-04-22_0353_deribit-okx-option-quote-gap-shell.md`
- 执行动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只补的最小 decisive blocker
检验这条 `Deribit ↔ OKX 同合约 quote-gap capture` 在最小多腿执行现实下，是否还留有值得单独排队的新 after-cost pocket，而不只是一个 maker-first / hedging execution shell。

## 读取到的最小证据
来自 `reports/artifacts/quant_digests/2026-04-22_deribit_okx_option_gap_probe_summary.csv` 的 12 次连续 snapshot：

- 每次可匹配合约约 `492` 个
- 正向 gap 约 `6~12` 个
- `>0.05%` 的 gap 约 `5~8` 个
- `>0.10%` 的 gap 基本只有 `1` 个
- `>0.25%` 的 gap 为 `0`
- 最大 gap 仅 `0.001`（约 `0.10%`）

digest 自身也已经把对象描述成“能跑的跨所期权价差壳”，而不是“常态厚边机器”。

## 为什么这一步足以收口
1. 当前可见 edge 厚度只到 `~0.10%` 顶格，且绝大多数更薄；
2. 这是期权跨 venue 双腿执行，不仅有两侧撮合/撤单/legging-loss，还要面对期权特有的宽 spread、深度不足与 hedge 误差；
3. 在这样的厚度分布下，公开 probe 没有留下能证明“扣掉最小多腿执行现实后仍有独立 after-cost pocket”的证据；
4. 因此它当前更像 `options / cross-venue / maker-first / hedge` 的执行壳与研究提示，而不是值得前排保留的新 raw alpha 主语。

## runtime-impact
`Deribit ↔ OKX 同合约 quote-gap capture` 的 fresh intake first verdict 已诚实收口 `background/P0`：12 次连续 snapshot 虽确认 492 个匹配合约里偶发 `6~12` 个正向 quote gap，但最大 gap 仅约 `0.10%`、`>0.25%` 为零，未证明跨 venue 期权在多腿成交、撤单与 legging-loss 现实后仍留下独立新增 after-cost pocket；当前只保留为 options/cross-venue maker-first execution shell 提示，不占用 survivor。
