# bot3 optimization loop log — 2026-04-16 15:07 UTC

## 执行小点
- target: `research/quant_digests/2026-04-16_1426_postcost-threshold-admission-fundingbasis-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps + Asia/EU/US`，并补最小 honesty/execution realism）

## 本轮最小核验（基于现有 trade artifact）
- 读取：`reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16_trades.csv`（145 笔）
- 口径：
  - 分时段：Asia(UTC 00-07) / EU(08-15) / US(16-23)
  - 成本：round-trip `4/6/8 bps`
  - `t+2` honesty 代理：仅保留 `hold_bars>=3` 的交易（避免“触发后几乎立即结束”的不可执行样本）

## 结果
- 全样本平均单笔（gross-cost）分别为：
  - `4bps: -2.50 bps`
  - `6bps: -4.50 bps`
  - `8bps: -6.50 bps`
- 分时段三段在 `4/6/8bps` 下均为负（无 `Asia/EU/US` 同向费后为正 pocket）。
- `t+2` 代理后仅剩 `95/145` 笔可执行，且仍为负：
  - `4bps: -2.15 bps`
  - `6bps: -4.15 bps`
  - `8bps: -6.15 bps`

## 结论（first verdict）
`post-cost threshold admission fundingbasis alpha` 在统一 `t+2 + 4/6/8bps + Asia/EU/US` gate 下未通过：分时段与整体费后均为负，且 `t+2` 执行现实过滤后仍无可复制正边际；本轮 fresh intake 直接收口 `background/P0`（不进入 survivor，不分配 Rank）。

## 对 state/cycle_plan 的回写
- Fresh intake slot 更新为本对象并记 `background/P0` 结论。
- cycle_plan #1 写回 `done`。
- Background pool 追加本对象 parked 记录。
