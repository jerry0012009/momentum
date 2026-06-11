# funding carry scanner shell — fresh intake first verdict（background/P0）

- 时间：2026-04-24 02:28 UTC
- 对象：`research/quant_digests/2026-04-23_2112_funding-carry-scanner-shell.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮最小 decisive blocker 检查
只补 1 个最小 honesty / distinctness 检查：用 Binance USDⓈ-M 近 90 个 funding 点（约 30 天）看 8 个主流合约的 funding 持续性与粗略费后空间，判断它是否留下**可独立排队**的 after-cost funding-carry pocket，而不是只剩 scanner / routing / execution-shell 提示。

### 快检结果（90 个 funding prints）
- `BTCUSDT`：`pos_ratio=0.389`，`mean_apr=-1.85%`，`mean_8h=-0.169bps`
- `ETHUSDT`：`pos_ratio=0.467`，`mean_apr=-1.11%`，`mean_8h=-0.101bps`
- `SOLUSDT`：`pos_ratio=0.433`，`mean_apr=-3.27%`，`mean_8h=-0.299bps`
- `DOGEUSDT`：`pos_ratio=0.578`，`mean_apr=+2.27%`，`mean_8h=+0.207bps`
- `ADAUSDT`：`pos_ratio=0.644`，`mean_apr=+1.03%`，`mean_8h=+0.094bps`
- `XRPUSDT`：`pos_ratio=0.522`，`mean_apr=-1.05%`，`mean_8h=-0.096bps`
- `AVAXUSDT`：`pos_ratio=0.656`，`mean_apr=+1.85%`，`mean_8h=+0.169bps`
- `LINKUSDT`：`pos_ratio=0.722`，`mean_apr=+3.42%`，`mean_8h=+0.313bps`

## 为什么这一步改变结论
1. **确实存在分币种的正 funding pocket**：DOGE / ADA / AVAX / LINK 在最近 30 天里正 funding 比例偏高，说明 repo 指向的 carry 宿主不是完全虚构。
2. **但 pocket 还没大到能诚实独立成新前排对象**：这些均值只在 `+0.09 ~ +0.31 bps / 8h`，离真实可交易净值还隔着现货/合约双腿手续费、滑点、借币/库存与资金占用；当前 digest 没有给出统一 after-cost ledger，也没给出跨多币、跨多窗口的净 carry 留存证据。
3. **distinctness 没有成立**：这条线的 alpha 主语仍是 funding carry，本质上没有脱离 desk 已 live 的 `Rank 389 / cross-venue net-carry ranking alpha` 家族；本轮新增信息更像“单 venue funding pocket scanner + maker-first execution 提示”，不是相对现有 carry family 的新 durable pocket。
4. **因此唯一 decisive blocker 仍未穿透**：还没有证据证明至少一个非单 coin、非单 funding-window lucky-run 的 pocket，在真实成本后仍留下可独立排队的 carry alpha。

## verdict
`funding carry scanner shell` 的 fresh intake first verdict 已诚实收口 `background/P0`：public funding probe 只证明了单 venue 分币种正 funding pocket 的存在，但最近 30 天均值大多仍只有亚 `1bp/8h` 级别，尚未给出跨多币、多 funding window 的 after-cost net-carry ledger；其新增价值也主要退化为已 live `Rank 389` carry 家族的 scanner / routing / execution-shell 提示，而不是新的独立 front-slot alpha。
