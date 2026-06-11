# bot3 optimization loop log — beta-corr gated pairs fresh intake -> background/P0

- Time: 2026-04-21 03:13 UTC
- Cycle item: `research/quant_digests/2026-04-20_0455_betacorr-gated-betaweighted-futures-pairs-shell.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## What I checked
只执行 bot2 当前最前的 pending 小点：对 `beta-corr gated pair admission × beta-weighted spread fade × asset exclusivity guard` 做最小 decisive blocker 检查。

使用 digest 已落地的最小实验与 artifact：
- script: `scripts/run_quant_digest_ctos_beta_pair_probe.py`
- artifacts: `reports/artifacts/quant_digests/ctos_beta_pairs_probe_20260420_0448/`
- universe: Binance USDⓈ-M majors, `15m`, recent `1500` bars
- admission: train corr `>=0.85`, beta `>0`, dynamic threshold, dirty-spike veto
- execution shell: beta-weighted sizing + `asset exclusivity`
- cost lens: round-trip `8bps`

补了 1 个最小 honesty/concentration 子检查：直接读取 `portfolio_selected_trades.csv`，按月份与 pair 统计 `gross/net8`，确认它是不是“非单 pair、分月可复制”的 pocket，而不是被少数 pair 或单月窗口撑住。

## Key findings
1. 最近窗口只有 `6` 组 pair 通过 admission，但真正有交易的只有 `3` 组，其中组合壳实际只选到 `2` 组 pair、`17` 笔。
2. 组合壳在统一双腿 `8bps` 下：
   - `gross_total ≈ +90.15bps`
   - `net_total@8bps ≈ -45.85bps`
   - 已经整体费后转负。
3. 唯一费后仍为正的 pair 是 `ETHUSDT-SOLUSDT`：
   - `4` 笔
   - `net_total@8bps ≈ +18.16bps`
4. 交易最密的 `XRPUSDT-LINKUSDT` 虽有 `13` 笔、gross 为正，但：
   - `net_total@8bps ≈ -64.01bps`
   - 说明高频 pair 的毛边基本被成本吞噬。
5. 月份检查显示当前可见样本全部集中在 `2026-04`：
   - portfolio `2026-04 net8_total ≈ -45.85bps`
   - 不存在“跨月份仍稳健”的证据
   - 且剩余正边际只来自单一 `ETH-SOL` pair，不满足“非单 pair”成功标准。

## Decision
`beta-corr gated pair admission × beta-weighted spread fade × asset exclusivity guard` 在当前最小可复算版本里，没有通过本轮 success criterion：
- after-cost 正边际没有扩展成非单 pair 可复制 pocket；
- recent 可见月份只有 `2026-04`，且组合整体 `net8` 为负；
- asset exclusivity / beta clamp 没有制造明显造假，但也没有拯救成本敏感性。

因此本轮直接把它收口为 `background/P0`，不保留为 survivor。

## State-changing sentence
`beta-corr gated pair admission × beta-weighted spread fade × asset exclusivity guard` 在统一双腿 `8bps`、asset exclusivity 与 recent month/pair concentration realism 下只剩 `ETH-SOL` 单 pair 薄正 pocket，而组合壳 `2026-04 net8≈-45.85bps`、高频 `XRP-LINK` pair 明显费后转负，因此本轮直接收口 `background/P0`。
