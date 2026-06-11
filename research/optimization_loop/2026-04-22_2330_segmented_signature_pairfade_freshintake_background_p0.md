# bot3 优化执行日志 — segmented-signature pairfade fresh intake 直接收口 background/P0

- 时间：2026-04-22 23:30 UTC
- 执行对象：`research/quant_digests/2026-04-22_1026_segmented-signature-pairfade-shell.md`
- cycle_plan 小点：`fresh intake：对 spread z-score fade × segmented-signature admission 做 first verdict`
- 结论：`background/P0`

## 本轮只补的最小 decisive blocker
验证这层 nonlinear admission 是否在当前 Binance perp `5m/15m`、最小双腿成本口径下，相对已 live 的 pairs family（`Rank 424 / 431`）留下**独立新增 after-cost pocket**，而不只是“pair-MR family 再加一层过滤”。

## 最小 honesty / portability 检查
我没有尝试完整 rough-path signature 复现，而是按 digest 允许的最小迁移版，只测它最核心、最可解释的 gate 代理：
1. base alpha 仍然是 rolling-OLS pair `spread z-score fade`；
2. gate 代理要求最近窗口两腿同向（`ΔX1 * ΔX2 > 0`）；
3. 同时要求近期 co-move 强度高于其 trailing mean（用 rolling return correlation 相对其历史均值作近似），作为 `segmented-signature < historical mean` 的 cheap proxy；
4. 统一使用 `entry |z|>=2`、`exit |z|<=0.25 or timeout`，并粗扣最小双腿 `8bps round-trip`。

样本：最近约 120 天 Binance perp，首批高流动性/同主题 pairs：
- `BTC/ETH`
- `ETH/SOL`
- `ARB/OP`
- `AAVE/COMP`
- `LINK/PYTH`

artifact：`reports/artifacts/quant_digests/2026-04-22_segmented_signature_proxy_pairs_probe.csv`

## 关键结果
### 1) gate 并没有把 family 变成新的 after-cost alpha
- `BTC/ETH 5m`：baseline `avg_net8≈-11.71bps`，gate 后也只有 `≈-10.16bps`
- `BTC/ETH 15m`：baseline `≈-7.70bps`，gate 反而恶化到 `≈-18.05bps`
- `ETH/SOL 5m`：baseline `≈-4.74bps`，gate `≈-4.82bps`
- `ETH/SOL 15m`：baseline `≈-3.39bps`，gate `≈-5.68bps`
- `ARB/OP 5m`：baseline `≈-6.55bps`，gate `≈-15.87bps`
- `AAVE/COMP 5m`：gate 虽较 baseline 改善（`-15.42 -> -8.35bps`），但仍未过成本线
- `LINK/PYTH 5m`：这是最像“有点用”的 pocket，baseline `≈-3.87bps`，gate 后 `≈-1.90bps`，仍然费后为负

### 2) 没有留下“至少两个可排队 pocket”
在可取到数据的 5 组 pairs × `5m/15m` 中：
- gate 后**没有一组**达到正的 `avg_net8_bps`；
- 正月度只零散出现，且没有形成跨多个 pair 的稳定新增结构；
- 最强 pocket 也只是把原本亏损的 pair-MR 壳亏得少一点，不足以证明独立新增 alpha。

### 3) 它更像 family 内的 shared admission hint，而不是前排对象
这次最小复核支持 digest 的“它是 gate，不是新 alpha 本体”这一判断；但当前真实迁移结果也说明：
- gate 的主要效果只是减少一些交易，
- 并没有把 short-cycle crypto pairs 从已知的 after-cost 困境里救出来，
- 更没证明相对已 live `Rank 424 / 431` 留下独立、可排队的新 pocket。

## 系统 verdict
`spread z-score fade × segmented-signature admission` 的 fresh intake first verdict 已诚实收口 `background/P0`：最近约 120 天 Binance perp `5m/15m` 的最小迁移复核中，segmented-signature 的 cheap proxy gate 虽偶尔降低亏损，但在 `BTC/ETH`、`ETH/SOL`、`ARB/OP`、`AAVE/COMP`、`LINK/PYTH` 上没有留下任何正的费后均值 pocket，最强 `LINK/PYTH 5m` 也仅从约 `-3.87bps` 改善到约 `-1.90bps`；因此它当前只保留为 pairs family 的 admission / veto 提示，不进入 survivor，也不构成相对已 live `Rank 424 / 431` 的独立新增排队价值。
