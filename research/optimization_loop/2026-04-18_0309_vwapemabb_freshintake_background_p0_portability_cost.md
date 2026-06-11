# 2026-04-18 03:09 UTC — `trend-up VWAP reclaim × lower-band pierce` fresh-intake first verdict

## 执行对象
- target: `research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
- action: fresh intake first-verdict + 1 个最小 honesty / execution realism 检查（`BTC/ETH/SOL 5m` portability 后是否仍只是 asset/side-selective 薄 pocket）

## 读取证据
- digest：`research/quant_digests/2026-04-18_0203_vwap-ema-bb-trendpullback-alpha.md`
- artifact：`reports/artifacts/quant_digests/vwap_ema_bb_probe_20260418_0203/trade_summary_all.csv`
- artifact：`reports/artifacts/quant_digests/vwap_ema_bb_probe_20260418_0203/signal_summary_all.csv`

## 最小 honesty / execution realism 检查
只用 digest 已给出的 `BTC/ETH/SOL 5m` portability 与 toy shell 汇总，检查这条线在简单 round-trip 成本梯度下还能否诚实支撑独立 front-slot。

### toy shell 原始均值（bps/笔）
- `BTC long`: `+2.69bps`（`n=9`）
- `BTC short`: `+3.51bps`（`n=12`）
- `ETH long`: `-17.27bps`（`n=11`）
- `ETH short`: `-7.63bps`（`n=7`）
- `SOL long`: `+4.82bps`（`n=14`）
- `SOL short`: `+9.00bps`（`n=17`）

### 扣除统一 round-trip cost 后（bps/笔）
- `2bps`：
  - `BTC long +0.69`
  - `BTC short +1.51`
  - `ETH long -19.27`
  - `ETH short -9.63`
  - `SOL long +2.82`
  - `SOL short +7.00`
- `4bps`：
  - `BTC long -1.31`
  - `BTC short -0.49`
  - `ETH long -21.27`
  - `ETH short -11.63`
  - `SOL long +0.82`
  - `SOL short +5.00`
- `8bps`：
  - `BTC long -5.31`
  - `BTC short -4.49`
  - `ETH long -25.27`
  - `ETH short -15.63`
  - `SOL long -3.18`
  - `SOL short +1.00`

## 结论
这条 `trend-up VWAP reclaim × lower-band pierce` 的 raw shape 虽然可读，但当前公开 probe 里的可见价值没有形成可诚实保留的独立 front object：
- 正边际主要集中在少数 `BTC long / BTC short / SOL short` pocket；`ETH` 双边整体塌掉；
- 一旦压到统一 `4bps` 成本，`BTC` 双边都转负，只剩 `SOL short` 明显为正、`SOL long` 仅剩 `+0.82bps`；
- 压到 `8bps` 后连 `SOL long` 也转负，只剩 `SOL short` `+1.00bps` 的薄余量，难以诚实覆盖 further execution slippage / exit realism；
- 事件样本本身也偏稀疏（`9~17` 笔/side），不足以把这条线当成 broad-book 的 trend-pullback continuation alpha 保留到前排。

## verdict
`trend-up VWAP reclaim × lower-band pierce` 在 `BTC/ETH/SOL 5m` portability + 简单 `2/4/8bps` cost realism 下暴露为 asset/side-selective 薄 pocket，而不是可诚实保留的独立 front-slot alpha；本轮 fresh intake first verdict 直接收口 `background/P0`。

## runtime impact
- `Fresh intake slot` 当前对象收口到 `background/P0`
- 由于没有形成新的 survivor / P2，front-slot 顺位切到下一条 pending：`auction-profile value-area re-entry × LVN traverse shell`

## tail-step status
- `publish_homepage_index.sh` 异步尾步在 `2026-04-18 03:14 UTC` 以 `SIGKILL` 结束，按 policy 记为**非阻断尾部失败**；本轮研究结论、state 写回与邮件通知均保持有效，不做回滚。
