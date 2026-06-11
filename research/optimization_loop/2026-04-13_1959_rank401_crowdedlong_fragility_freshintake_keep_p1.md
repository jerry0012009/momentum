# bot3 optimization loop log — 2026-04-13 19:59 UTC

## 本轮执行小点
- cycle_plan item 2
- target: `research/quant_digests/2026-04-13_1913_crowdedlong-fragility-cascade-alpha.md`
- action: fresh intake first-verdict（统一成本口径 + 最小 honesty/execution realism 检查）

## 关键证据（直接来自现有 artifact）
- `reports/artifacts/quant_digests/yolobot_fragility_cascade_probe_summary_2026-04-13.json`
- BTC+ETH core lane：
  - 事件数 `12`
  - 事件后 `15m` 空头均值 `+5.96 bps`
  - 事件后 `60m` 空头均值 `+14.29 bps`
- SOL 仅 `2` 个事件，样本稀疏，不纳入首轮可迁移主结论。

## 本轮最小 honesty / execution realism 子检查
- 检查触发与收益口径是否含未来信息：
  - 触发条件使用当根与历史信息（`fundingRate` backward 对齐、`ret1`、`oi_chg`、历史分位）；
  - 收益使用触发后 `ret_f1/ret_f4`，未把未来窗口反写回触发条件。
- 结论：未发现明显 lookahead/repaint 型硬性违规；但触发事件稀疏（BTC/ETH 合计 12 次），当前仅可作为 `P1` 存活，不足以直接升 `P2`。

## 统一成本口径下的 first verdict
- 若按短持有 `15m`（1bar）看，core lane `+5.96 bps` 接近 `6 bps` 成本阈值，费后不稳。
- 若按 `60m`（4bar）持有看，core lane `+14.29 bps` 仍保留正边际。
- 因此该对象不是直接 `background/P0`，但也未达 `P2` admission 充分度。

## 结果
- 分配新正式 Rank：`Rank 401`（next unused integer）。
- fresh intake first verdict：`keep_P1`。
- 将 `Rank 401` 置入 `Surviving candidate slot`，并保留唯一 follow-up 预算 `1`（下一步 blocker：在 BTC/ETH 上补最小样本扩展与 2/4/6 bps 成本分层，验证 60m 边际是否稳健可迁移）。
