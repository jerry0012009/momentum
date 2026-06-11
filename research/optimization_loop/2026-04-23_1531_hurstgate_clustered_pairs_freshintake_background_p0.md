# 2026-04-23 15:31 UTC — Hurst-gated clustered pairs shell fresh intake -> background/P0

## 本轮执行小点
- target: `research/quant_digests/2026-04-23_0347_hurstgate-clustered-pairs-shell.md`
- action: fresh intake first verdict

## 执行摘要
本轮只补 1 个最小 decisive blocker：`Hurst-gated clustered pairs shell` 是否相对已 live 的 `Rank 424 / Rank 431` pairs family，留下了新的、非单 pair / 非单窗口 lucky-run 的独立 after-cost pocket。

结论：**没有**。本对象本轮直接收口 `background/P0`。

## 关键证据
### 1) aggregate 层面并没有留下可独立承接的 after-cost pocket
读取 digest 附带 artifact：
- `reports/artifacts/quant_digests/hurstgate_pairs_probe_agg_2026-04-23.csv`

可见：
- `15m + no_gate`: `net_bps_per_trade ≈ -1.06`
- `15m + hurst_lt_0.60`: `net_bps_per_trade ≈ -1.17`
- `5m + no_gate`: `net_bps_per_trade ≈ -12.09`
- `5m + hurst_lt_0.60`: `net_bps_per_trade ≈ -9.73`

也就是说，Hurst gate 在 `5m` 噪声段确实有改善，但**并没有把组合级结论翻成 after-cost 为正**；`15m` 甚至略差。

### 2) 正边际基本只剩单一 pair，不满足 front-slot 的独立性要求
读取：
- `reports/artifacts/quant_digests/hurstgate_pairs_probe_pair_summary_2026-04-23.csv`

其中 `15m` 里唯一清晰为正的是：
- `LINKUSDT__AVAXUSDT`
  - `no_gate net ≈ +20.37 bps/trade`
  - `hurst_lt_0.60 net ≈ +22.14 bps/trade`

但同一份 pair summary 的其余 `15m` pair（`BTC/SOL`, `BTC/ETH`, `ETH/SOL`）均为负；`5m` 汇总也没有形成“多 pair 同向为正”的簇级 pocket。说明当前可见厚度主要仍是**单 pair pocket**，而不是 clustered-pairs 壳本身已经证明了可独立排队的 after-cost alpha。

### 3) 与已 live pairs family 的新增价值不足
即便承认 `LINK/AVAX` 这个 pocket 可能真实存在，本对象当前新增价值也主要退化为：
- cluster-first pair discovery
- Hurst regime gate
- hub/concentration cap

这些更像 `Rank 424 / Rank 431` 现有 pairs family 可吸收的 admission / governance / execution 设计提示，而**不是一个已经证明自己值得单独占用 survivor/front-slot 的新 raw alpha 主语**。

### 4) digest 文案与 artifact 汇总存在不一致，但不改变结论
本轮复核发现 digest 正文里提到若干 `5m` 正 pocket，但 aggregate artifact 明确显示 `5m` 组合级 `net` 仍显著为负；因此本轮只能以 artifact 可复核结论为准，不把文案中的局部亮点当作足以保留 front-slot 的系统级证据。

## 本轮 verdict
`Hurst-gated clustered pairs shell` 的 fresh intake first verdict 已诚实收口 `background/P0`：当前 after-cost 证据没有跨出 `LINK/AVAX` 单 pair pocket，aggregate 层面 `15m/5m` 仍为负，且新增价值主要退化为可被已 live `Rank 424 / 431` pairs family 吸收的 cluster/Hurst admission 与 concentration-cap 组件提示，因此不保留 survivor。
