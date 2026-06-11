# bot3 optimization loop log — 2026-04-13 21:05 UTC

## 本轮执行小点
- cycle_plan item 1
- target: `Rank 401 / crowded-long fragility cascade`
- action: survivor 唯一 follow-up（BTC/ETH 最小样本复核 + 统一 `2/4/6bps` 成本分层 + execution realism 延迟注入）

## 本轮新增 artifact
- `reports/artifacts/quant_digests/rank401_crowdedlong_followup_summary_2026-04-13.json`
- `reports/artifacts/quant_digests/rank401_crowdedlong_followup_events_2026-04-13.csv`

## 关键证据（BTC/ETH core lane）
- 事件定义沿用首轮 proxy（crowded long + down bar + OI flush）。
- 当前样本：`12` 个事件（BTC `5` / ETH `7`）。
- 不注入延迟时：
  - `t+1 (15m)` 空头毛收益均值 `+5.96 bps`；双边成本后：
    - `2/2 bps` => `+1.96 bps`
    - `4/4 bps` => `-2.04 bps`
    - `6/6 bps` => `-6.04 bps`
  - `t+4 (60m)` 空头毛收益均值 `+14.29 bps`；双边成本后：
    - `2/2 bps` => `+10.29 bps`
    - `4/4 bps` => `+6.29 bps`
    - `6/6 bps` => `+2.29 bps`
- execution realism（触发后延迟 1 根再入场）子检查：
  - 延迟入场持有 `1` 根：毛收益 `+12.02 bps`，`6/6 bps` 双边后约 `+0.02 bps`
  - 延迟入场持有 `4` 根：毛收益 `+14.65 bps`，`6/6 bps` 双边后约 `+2.65 bps`

## blocker 判定
- 未发现单一 decisive honesty/execution blocker：
  - 信号构造仍为当根+历史信息（funding backward align，未把未来收益写回触发）；
  - 注入 1 bar 延迟后，`60m` 侧仍保留正边际（即便在 `6/6 bps` 双边成本下）。
- 仍存在样本偏小风险（仅 12 事件），但该风险不构成“立即打回 P0”的单一致命 blocker。

## 本轮出口决策（按二选一约束）
- `Rank 401` 从 survivor `promote_P2`（不落回 `background/P0`）。
- 系统认知变化：该对象已从“仅 P1 存活假设”进入“P2 admission 候选”，下一步应在 P2 admission 维度完成出口判定（优先检查跨资产/时间稳定性与容量边际，而非重复同轴验证）。
