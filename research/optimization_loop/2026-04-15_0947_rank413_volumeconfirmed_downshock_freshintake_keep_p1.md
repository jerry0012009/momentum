# Rank 413 fresh intake — volume-confirmed 1h downshock bounce first verdict（keep_P1）

- 时间：2026-04-15 09:47 UTC
- 对象：`research/quant_digests/2026-04-15_0912_volumeconfirmed-1h-downshock-bounce-alpha.md`
- 本轮动作：按统一 `t+2` 入场（相对 signal 延后一根 15m）+ `4/6/8bps` 成本，做 fresh intake first verdict；并做最小 honesty 子检查（delayed confirmation / leakage realism）。

## 执行与证据
- 基线事件与非重叠交易集沿用：
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0910/trade_list_no_overlap.csv`
- 本轮新增 t+2 延迟入场复核：
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0947_tplus2_delay_check.csv`

### 关键结果（t+2 + 成本梯度）
- `BTCUSDT`
  - `2h`：gross `+39.2 bps`；net `+35.2 / +33.2 / +31.2 bps`（`4/6/8bps`）
  - `1h`：net `+23.2 / +21.2 / +19.2 bps`
  - `8h/24h` 仍为正；说明 edge 不依赖“signal 后立即抢第一根 15m”这一超理想化假设。
- `ETHUSDT`
  - `2h` 在 `6/8bps` 下仅剩弱正（`+3.4 / +1.4 bps`），`4h+` 持续为负。
- `SOLUSDT`
  - `1h` 仅边际为正（`8bps` 约持平），`2h+` 费后为负。

## first verdict
**结论：`keep_P1`，并分配正式 `Rank 413`。**

一句会改变系统认知的话：
> 在统一 `t+2 + 4/6/8bps` 的更保守执行口径下，这条 alpha 仍保留清晰的 `BTC-only` 费后净值 pocket；但 `ETH/SOL` 不满足同阈值可迁移性，不能作为 multi-major 通用壳进入前排。

## survivor 唯一 blocker（已锁定）
- 唯一 blocker：**BTC-only 版本在时间稳定性上是否成立（分前后半窗仍保持 `2h` 费后正 pocket）**。
- 下轮 survivor follow-up 只做这一项，不再并行扩展新维度。
