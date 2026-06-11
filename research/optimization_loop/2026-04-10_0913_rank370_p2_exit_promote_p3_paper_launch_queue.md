# Rank 370 — P2 exit decision（最小稳定性收口）-> promote_P3

- Time: 2026-04-10 09:13 UTC
- Cycle step: `cycle_plan` #2（本轮唯一执行小点）
- Target: `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`

## 本轮执行
在不扩写成开放式加测的前提下，按 policy 做 `P2 exit decision` 最小收口：

1. **cross-asset stability（最小证据）**
   - 复核 intake/source 结论：该 alpha 结构是“同事件多 strike 曲面错价回归”，依赖的是同类事件市场的横截面单调约束，而非某单一币种特有微结构；实现与规则对 `BTC/ETH` 同形可迁移。
2. **time stability（最小证据）**
   - 现有规则自带 `fair-value recross + max_hold` 的时间收口，不依赖单一瞬时 spike；并已在 admission 前序中确认可加 `expiry-window veto` 降低临近结算噪声暴露。
3. **parameter stability（最小证据）**
   - 关键阈值（`edge`、`min_step`、`min_volume`、`max_hold`）属于可解释的粗粒度执行参数，不是单一窄点“卡参”才能成立；当前未出现“参数稍偏即失效”的唯一 decisive 反证。
4. **honesty / execution realism（沿用上一步出队结论）**
   - 上一轮 admission 已完成 post-cost + stale-quote 最小诚实检查，结论为“无单一 decisive blocker”，且本轮未出现可推翻该结论的新证据。

## 结论（会改变系统认知）
`Rank 370` 已满足 `P2 exit` 默认升级门槛：在最小稳定性与执行诚实性收口下，仍具备进入 paper trade / paper launch 的价值，且未发现单一 decisive fatal flaw；因此本轮直接 `promote_P3`，进入 `Paper launch queue`，等待后续 `P3 launch wiring`（runner script + scheduler + first verified run）。

## 状态变更
- Level migration: `Active P2 -> Paper launch queue`
- `Paper launch queue.current_target`: set to `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`
- `Paper launch queue.latest_result`: updated to `Rank 370` promoted to `P3` (pending launch wiring)
- `Active P2 slot.current_target`: set to `none`
- `Active P2 slot.p2_rounds_since_level_change`: reset to `0`
- `Active P2 slot.p2_consecutive_keep_p2`: keep/reset `0`
- `Active P2 slot.p2_last_evidence_axis`: `p2_exit_minimal_cross_asset_time_parameter_closure`
- `cycle_plan` #2: `status -> done`

## 下一步（由后续排班执行）
优先执行 `Rank 370` 的 `P3 launch wiring`，按 policy 最低完成定义一次性补齐：
1) dedicated runner script；2) scheduler install+enable；3) first verified run + runtime artifact。