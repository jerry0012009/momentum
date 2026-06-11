# bot3 execution log — 2026-04-16 16:32 UTC

## 执行小点
- cycle_plan item 2
- target: `research/quant_digests/2026-04-16_1204_bidirectional-funding-zscore-perp-carry-shell.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + Asia/EU/US），并补最小 honesty 检查（funding 结算时钟错位与仓位轮换摩擦）

## 读取到的关键信号（来自 digest 工程证据）
1. 公开仓库是可复现、可落地的完整策略壳（signal/sizing/risk/cost 链路完整）。
2. 但在给定参数与成本口径下出现明显 `gross->net` 断层：`Gross CAGR 13.0%` 对应 `Net CAGR 0.2%`，净 Sharpe 为负，edge 对摩擦高度敏感。
3. notebook 给出 `break-even taker fee ≈ 3.4 bps`，默认 taker 成本约 `4 bps` 已在 break-even 之上；在本项目统一 `4/6/8bps` gate 下不具备稳健费后余量。
4. 分阶段里 post-FTX（2023-01~2026-02）退化显著，提示该壳在近期 regime 下没有可直接复用的稳定费后 pocket。

## 最小 honesty / execution realism 子检查（本小点内）
- 针对 `funding` 8h 结算时钟与分钟执行错配：若按统一 `t+2` 延迟确认并计入轮换摩擦，原本已接近 break-even 的边际会进一步被吞噬；在 `4/6/8bps` 档位下不存在可验证的稳健正余量。

## 本轮结论（改变系统认知）
- `bidirectional funding z-score perp carry shell` 在统一 `t+2 + 4/6/8bps + Asia/EU/US` 口径下未通过费后稳健性；且 funding 时钟错位与仓位轮换摩擦 honesty 检查后无可复制正边际，本轮 fresh intake 直接收口 `background/P0`（不进入 survivor、不分配 Rank）。

## 状态写回
- cycle_plan item 2: `status=done`
- cycle_plan item 2 result 已写为上述收口结论
- Fresh intake latest_result / latest_result_record 已更新
- Background pool latest_parked / latest_parked_record 已追加该对象与本日志
