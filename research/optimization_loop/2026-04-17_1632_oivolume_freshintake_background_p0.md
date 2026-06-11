# OI-Volume 失衡冲击 × 短窗延续：fresh intake first verdict = background/P0

- Time: 2026-04-17 16:32 UTC
- Target: `research/quant_digests/2026-04-16_1818_oivolume-shock-continuation-alpha.md`
- Slot action: conditional fresh intake -> first verdict
- Verdict: `background/P0`

## Why this round was decisive
本轮只回答 cycle_plan 里要求的一个问题：`OI-Volume 失衡冲击 × 短窗延续` 在统一 `t+2 + 4/6/8bps` 下是否仍值得保留，并补 1 个最小 honesty / execution realism blocker：**5m OI 历史口径发布时间/修订时滞，不能把当根完整 OI 当作实时已知。**

## Evidence used
1. digest 自带 public-data probe：
   - `reports/artifacts/quant_digests/oi_volume_imbalance_probe_2026-04-16_summary.csv`
   - 原始零延迟口径 cross-symbol 平均：`cont5=+0.72bps`，`cont15=+2.42bps`
2. 既有 integrity gate 记录：
   - `research/quant_digests/2026-03-21_2248_oi-volume-reconciliation-integrity-gate.md`
   - 其中已说明 Binance OI 在短窗更像存在错位/延迟一致性，`5m/15m` 不应把 OI jump 直接当作当根硬信号。
3. 本轮最小 honesty / execution realism probe：
   - 将 signal bar 的 `OIV shock` 视为**至少在后两根 bar 后**才可稳定确认，按 `t+2` 入场；
   - 同时保持 digest 原始定义：事件仍由 `5m OIV ratio >= rolling P95` 与当根方向决定；
   - 对 `BTC/ETH/SOL` 各自近 29d `5m` 样本重算 `5m/15m` continuation gross，并直接扣除 `4/6/8bps` round-trip 成本。

## Minimal honesty result (`t+2` delayed confirmation)
### Per-symbol
- BTCUSDT
  - `5m gross = +2.42bps` -> `net4/6/8 = -1.58 / -3.58 / -5.58bps`
  - `15m gross = +3.73bps` -> `net4/6/8 = -0.27 / -2.27 / -4.27bps`
- ETHUSDT
  - `5m gross = +2.75bps` -> `net4/6/8 = -1.25 / -3.25 / -5.25bps`
  - `15m gross = +5.51bps` -> `net4/6/8 = +1.51 / -0.49 / -2.49bps`
- SOLUSDT
  - `5m gross = -3.93bps` -> `net4/6/8 = -7.93 / -9.93 / -11.93bps`
  - `15m gross = -9.08bps` -> `net4/6/8 = -13.08 / -15.08 / -17.08bps`

### Read-through
- 原 digest 的优势本来就只在零延迟下是 `+0.72bps / +2.42bps` 级别，远低于统一成本梯度；
- 一旦按最小 honesty 处理成 `t+2`，样本数收缩到每币约 `25~26` 个事件，**只剩 ETH 的 15m 在 `4bps` 下勉强为正，`6/8bps` 立刻失效**；
- BTC 的 15m 也已在 `4bps` 下转负；
- SOL 在 `5m/15m` 都明显反向，说明该事件轴并不具备可复制的 cross-asset portability；
- 因此这条 alpha 不能作为 front-slot 候选保留，更不应升为 survivor。

## System-changing conclusion
`OI-Volume 失衡冲击 × 短窗延续` 的原始 continuation 边际依赖把短窗 OI 历史值视作当根已知；按最小可执行 honesty 改成 `t+2 + 4/6/8bps` 后，跨资产不再成立，只剩 ETH 15m 在最低成本档勉强为正、且不足以支撑 portability，因此本轮 first verdict 直接收口 `background/P0`。
