# bot3 optimization loop log — 2026-04-12 10:08 UTC

## 执行小点
- cycle_plan item 2
- target: `Rank 388 / negative-funding boundary short (most-negative funding coin @ settlement)`
- action: survivor 唯一一次 follow-up：`+1m/+2m/+3m` 同口径（统一 `8 bps`）+ 事件集中度最小检查

## 最小证据与结果
数据来源：
- `reports/artifacts/literature/negative_funding_boundary_probe_2026-04-12_detail.csv`
- 新增补充：`reports/artifacts/literature/negative_funding_boundary_probe_2026-04-12_survivor_followup_pre15down_plus2.csv`

在 `pre15_down`（17 events）下，short 方向收益：
- `+1m gross ≈ 9.8333 bps` -> `net@8bps ≈ +1.8333 bps/trade`（net win rate ≈ 47.06%）
- `+2m gross ≈ 13.0780 bps` -> `net@8bps ≈ +5.0780 bps/trade`（net win rate ≈ 64.71%）
- `+3m gross ≈ 11.2128 bps` -> `net@8bps ≈ +3.2128 bps/trade`（net win rate ≈ 58.82%）

## “是否只靠极少数事件支撑”检查
- 针对 `+3m net@8bps` 做 leave-one-out：
  - `LOO 最低净均值 ≈ +0.6137 bps`
  - `LOO 最高净均值 ≈ +5.3538 bps`
- 解释：存在头部事件放大收益，但移除任一单事件后均值仍未转负，未构成“单一极端事件驱动”的 decisive blocker。

## 本轮 verdict
- 结论：`promote_P2`
- 改变系统认知的一句话：`Rank 388` 在统一成本口径下并非仅 `+3m` 偶发有效，`+1m/+2m/+3m` 都保持正净边际，且集中度检查未触发单一事件失效，因此从 survivor 升级到 `Active P2` 进入 admission。

## runtime 回写
- `cycle_plan` item 2: `status -> done`
- `Surviving candidate slot`: 清空（follow-up 预算归零）
- `Active P2 slot`: 切换为 `Rank 388`，`p2_last_evidence_axis = survivor_followup_horizon_cost_concentration`
