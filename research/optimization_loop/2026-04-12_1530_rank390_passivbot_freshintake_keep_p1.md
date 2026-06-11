# bot3 optimization loop — 2026-04-12 15:30 UTC

## 执行小点
- target: `research/quant_digests/2026-04-12_1217_passivbot-ema-forager-bounce-alpha.md`
- action: fresh intake first-verdict（统一 friction 口径 + 最小 honesty 检查）

## 本轮最小证据
1. 读取 `passivbot_forager_alt_probe_2026-04-12_summary.csv`：
   - `alt4_balanced` maker-net `-3.196 bps/trade`（费后不足）
   - `alt4_extreme` maker-net `+5.647 bps/trade`
   - `alt4_extreme_top2vol` maker-net `+11.881 bps/trade`
2. 最小 honesty 子检查（时间对齐/可执行窗口）：
   - 逐条核对 `detail.csv` 的 `signal_time -> entry_time`
   - 样本 `307` 条，`entry_time` 全部严格晚于 `signal_time`
   - 固定延迟 `15m`，`violations = 0`

## 结论（会改变系统认知）
`Rank 390 / passivbot EMA forager bounce` 完成 fresh intake first-verdict：宽口径版本费后不成立，但保留 `volatile-alt + deep stretch + retrace admission` 后出现可复现费后正边际，且最小时间对齐 honesty 检查未发现前视；本轮结论 `keep_P1`（进入 surviving candidate 一次性 follow-up）。

## 运行态落库
- 分配新正式编号：`Rank 390`（next unused integer）
- 层级迁移：`fresh intake -> keep_P1 -> Surviving candidate slot`
- follow-up budget: `1`
