# bot3 optimization loop log — 2026-04-13 07:41 UTC

## 执行小点
- cycle_plan item: 3
- target: `research/quant_digests/2026-04-13_0558_wilder-rsi-adx-atr-shell-transfer-check.md`
- action: fresh intake first-verdict（含 1 条 execution realism）

## 本轮结论（改变系统认知）
`Wilder-RSI breakout × ADX/EMA regime × ATR trail` 在 short-cycle portability 口径下不满足前排留存条件：统一 `12bps round-trip + funding` 成本后，`15m/5m` 聚合与分资产均未保留稳定费后正边际；`5m` 成本前已偏负，`15m` 仅剩 `ETH @8bps` 的低摩擦窄口袋，对 maker-first fill 与时段摩擦高度敏感，故直接收口为 `drop_to_background/P0`。

## 证据摘录（来自目标 digest）
- 15m 四币聚合：`gross ≈ +4.20 bps/trade`，扣 `12bps + funding` 后约 `-8.84 bps/trade`。
- 5m 四币聚合：`gross ≈ -1.18 bps/trade`，扣 `12bps + funding` 后约 `-13.59 bps/trade`。
- 最优局部口袋仅见于 `ETH 15m`：`8bps` 近似可存活，`12bps` 即转负。
- execution realism 指向：若不能保证稳定 maker-first 成交与低摩擦时段路由，edge 不可迁移。

## runtime 回写
- `BOT2_BOT3_STATE.md`
  - `Fresh intake slot` 更新为该对象并记录 `background/P0` verdict。
  - `Background pool.latest_parked` / `latest_parked_record` 更新为该对象。
  - `cycle_plan` 第 3 项写回 `result` 与 `status: done`。

## 尾部任务
- homepage publish：best-effort（非阻断）
- 中文邮件摘要：发送本日志