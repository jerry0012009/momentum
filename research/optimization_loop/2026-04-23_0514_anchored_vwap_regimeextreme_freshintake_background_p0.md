# bot3 optimization loop — 2026-04-23 05:14 UTC

## 执行对象
- cycle_plan slot 2
- target: `research/quant_digests/2026-04-23_0419_anchored-vwap-regimeextreme-reversion-alpha.md`
- action: fresh intake：对 `swing-anchored VWAP 偏离 × regime-extreme reversion` 做 first verdict，只补 1 个最小 decisive blocker（它是否在更诚实的 anchor / execution realism 下保住独立 MR pocket，而不是只剩 BTC maker-first 单点 hint）

## 本轮最小检查
直接使用 digest 已落地的最小公开 probe 与相关 AVWAP 历史 artifact，回答唯一 blocker：
1. 这条线是否在 `BTC/ETH/SOL` 上留下可迁移、可独立排队的 after-cost pocket；
2. 还是仅剩 `BTC` 偏好的 maker-first / 精细 anchor 提示。

## 关键证据
### A. 本轮 raw-alpha portability probe（`reports/artifacts/quant_digests/2026-04-23_avwap_regimeextreme_probe_summary.csv`）
- `BTCUSDT`: `22` 笔，`gross_bps_per_trade ≈ +8.78`，`net_bps_per_trade_8bps ≈ +0.78`
- `ETHUSDT`: `28` 笔，`gross_bps_per_trade ≈ -1.71`，`net_bps_per_trade_8bps ≈ -9.71`
- `SOLUSDT`: `24` 笔，`gross_bps_per_trade ≈ -4.44`，`net_bps_per_trade_8bps ≈ -12.44`
- reclaim rate 三个币都只有约 `20%~23%`，大多数交易实际靠 timeout 而不是快速回到 AVWAP 完成兑现。

### B. trade-level 现实含义（`...probe_trades.csv`）
- BTC 虽保留薄正 pocket，但同样存在趋势继续走远的 fat-loss timeout（例如 `2026-04-17 12:45 UTC` short，`gross ≈ -117.49bps`）。
- ETH / SOL 多次出现偏离后继续扩张，说明“recent swing anchor + next-open/taker execution”下，MR 壳并没有形成稳定公平价回拉。

### C. 相关 AVWAP 历史 artifact 也没把它抬成通用独立 alpha
参考 `reports/artifacts/scout_rank58_event_anchored_vwap_15m/overall_summary.csv` 与 `asset_setup_summary.csv`：
- `event_avwap_gate` 只把总体现实结果从 `mean_total_return ≈ -2.02%` 改善到 `≈ -1.35%`；
- 更严格 `event_avwap_plus_proximity` 仍是总体负值 `≈ -0.37%`，且 retention 明显下降；
- 资产层面呈强分化：`BTC` 某些 long setup 可转正，但 `ETH` 多数组合持续明显负，`SOL` 只在个别 setup 留下薄 pocket。

## 结论
`anchored VWAP 偏离 × regime-extreme reversion` 已完成 fresh intake first verdict 并诚实收口 `background/P0`：当前更诚实的 anchor / execution 现实下，它没有证明存在至少两个非单币、非单一 setup 支撑的独立 after-cost MR pocket；可见新增价值主要收敛为 `BTC maker-first + 更精细 anchor 选择` 的单点 hint，而不是值得前排保留的 standalone raw alpha。

## 为什么这就是当前唯一 decisive blocker 的答案
本轮不需要继续补更多指标：
- 如果它是独立 front object，最小证据应先在 majors 里留下可迁移的 after-cost pocket；
- 现在只有 `BTC` 仍贴近成本线，`ETH/SOL` 明显失败，且兑现主要靠 timeout，不像干净的回归壳；
- 因此不足以进入 survivor，更不足以占用 P2/P3 资源。

## 回写动作
- 将 `Fresh intake slot` 更新为本对象与本结论；
- 将 cycle_plan 第 2 项写成 `done`；
- 不改动 policy / 其他槽位 / 排班顺序。

## 尾部执行
- best-effort 刷新首页
- 中文邮件摘要发送
