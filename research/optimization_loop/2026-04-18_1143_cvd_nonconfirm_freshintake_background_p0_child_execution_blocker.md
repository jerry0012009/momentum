# 2026-04-18 11:43 UTC — CVD non-confirm fresh intake 收口 `background/P0`

## 执行对象
- cycle_plan item1
- target: `research/quant_digests/2026-04-18_0715_cvd-nonconfirm-extreme-fade-shell.md`
- action: fresh intake first-verdict

## 本轮执行
按 digest 里的 repo source audit + Binance public-data portability probe，只补最小 honesty / execution realism 检查：确认这条 `price extreme × non-confirming CVD` 到底能不能直接压成裸 `15m` 主信号，还是只能停留在 `30m context -> 15m/5m child execution`。

## 关键证据
- `30m` 全样本有轻微回摆味道，但不足以直接跨过成本。
- 只有 `30m strength q75` 强信号 bucket 才出现可观 gross：next `4 bar ≈ +15.91bps`，next `8 bar ≈ +24.48bps`。
- 一旦直接压成裸 `15m` 主信号，edge 明显坏掉：全样本 next `4 bar ≈ -3.34bps`，`q75` 强信号 next `4 bar ≈ -6.33bps`，next `8 bar ≈ -12.53bps`。
- 当前 digest 只证明了 `30m` context 上存在 strong-signal gross pocket，但没有给出可验证的 `15m/5m child-entry + friction ladder` 后正 net 证据。

## 结论
`price extreme × non-confirming CVD` 的 `30m q75` 强信号虽有 gross edge（4/8 bar 约 +15.91/+24.48bps），但直接压成裸 `15m` 主信号已整体转负，且当前没有可验证的 `15m/5m child-entry + friction ladder` 后正 net 证据，因此本轮 fresh intake 直接收口 `background/P0`。

## 回写
- `BOT2_BOT3_STATE.md`
  - cycle_plan item1 -> `done`
  - Fresh intake latest_result / latest_result_record 已改写为本结论
  - Background pool latest_parked / latest_parked_record 已追加本结论

## 尾注
这是 first-verdict 收口，不保留 survivor/front-slot。若后续人工 reopen，唯一合理入口应是单独验证 `30m strong-signal -> 15m/5m child execution + friction ladder` 是否能留下稳定正 net，而不是重复把它当裸 `15m` exhaustion-fade 主信号。