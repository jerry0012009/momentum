# bot3 optimization loop log — 2026-04-15 01:05 UTC

## 本轮执行小点
- cycle_plan item 1（原 pending）
- target: `Rank 407 / cross-venue momentum divergence catch-up shell`
- action: survivor 唯一 follow-up（真实异步腿 + maker/taker 非对称执行 + next-bar 可执行映射）

## 执行内容（最小 honesty / execution 子检查）
- 新增最小回放脚本（inline 执行）：以 **Binance USDⓈ-M perp** 作为交易腿、**OKX SWAP** 作为 reference leg，按 `15m`、`lookback=72`、`entry_z=1.8`、`exit_z=0.5`、`momentum_window=12`、`momentum_divergence_threshold=0.02` 复刻 CED 触发。
- 执行口径：
  - 信号在 bar N 收到；成交统一映射到 bar N+1 open（next-bar）
  - 单腿方向交易 perp
  - 分层成本：
    1) maker entry + taker exit（含滑点）= 10 bps/roundtrip
    2) taker entry + taker exit（含滑点）= 14 bps/roundtrip
- 产出 artifact：
  - `reports/artifacts/quant_digests/ced_crossvenue_async_probe_summary_2026-04-15.csv`
  - `reports/artifacts/quant_digests/ced_crossvenue_async_probe_signals_2026-04-15.csv`

## 核心结果
- BTCUSDT（15m）：`avg_gross_bps=-3.318`，成本后继续为负。
- ETHUSDT（15m）：`avg_gross_bps=10.2346`，10 bps 成本层近零正（`+0.2346`），14 bps 转负。
- SOLUSDT（15m）：`avg_gross_bps=16.8508`，10/14 bps 成本层均保持正（`+6.8508 / +2.8508`）。
- 三资产 next-bar 映射覆盖率均为 `1.0`（无 delayed confirmation / 缺失下一根可成交开盘价问题）。

## 结论（改变系统认知）
- `Rank 407` 的 survivor 唯一 blocker 已被实证突破：在真实异步腿（Binance perp vs OKX perp）口径下，存在费后可行 pocket（以 SOL 15m 为主，ETH 临界，BTC 负）；因此本轮按 success_criterion 直接 `promote_P2`，不转 background。

## Runtime 写回
- `Surviving candidate slot`：用尽唯一 follow-up 预算并收口（`current_target=none`, `followup_budget_remaining=0`）。
- `Active P2 slot`：切换为 `Rank 407`，并记录本轮 admission 入口证据轴为“async-leg + maker/taker asymmetry + next-bar mapping”。
- `cycle_plan item 1`：`status=done`，已写入单句 result。
