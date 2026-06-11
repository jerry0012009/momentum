# bot3 optimization loop — 2026-04-16 13:47 UTC

## 执行小点
- target: `research/quant_digests/2026-04-16_1048_stability-filtered-spotperp-basis-shell.md`
- action: fresh intake first-verdict：在统一 `t+2 + 4/6/8bps` + Asia/EU/US 口径下检验 `stability-filtered spot-perp basis shell` 的费后可复制性，并补 1 个最小 honesty/execution realism blocker（borrow/funding 时钟错配与成交容量）

## 本轮执行
1. 复核 digest 给出的可用证据：当前仅有 repo 自述与 notebook 汇总结果（`research` 模式有交易，`strict/moderate` 为 0 交易），尚未提供按本项目统一口径可直接复算的事件级导出。
2. 对齐 first-verdict 硬口径：要求统一 `t+2` delayed-confirmation + `4/6/8bps` 成本 + Asia/EU/US 分时段可复制费后证据；现有材料无法直接形成该口径下的可验证净值统计。
3. 最小 honesty 子检查（本小点内唯一补充）：针对 `borrow/funding` 时钟错配与成交容量，判定当前证据无法排除“8h funding 映射到 15m/5m 产生对齐偏差 + taker 执行容量吞噬边际”的执行现实性风险。

## 结论（改变系统认知）
`stability-filtered spot-perp basis shell` 在统一 `t+2 + 4/6/8bps` + Asia/EU/US 口径下缺少可复算事件级样本，且最小 honesty（funding/borrow 时钟错配 + 容量执行）未通过；本轮 fresh intake first-verdict 直接收口 `background/P0`（不进入 survivor，不分配 Rank）。

## runtime 回写
- `Fresh intake slot.latest_result` 更新为本轮 `background/P0` 收口结论。
- `Fresh intake slot.latest_result_record` -> `research/optimization_loop/2026-04-16_1347_item2_stabilityfiltered_basis_freshintake_background_p0.md`
- `cycle_plan` item2 写回：`status=done`，`result` 已落地。
- `Background pool.latest_parked` 与 `latest_parked_record` 追加本对象与本日志。