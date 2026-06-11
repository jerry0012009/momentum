# bot3 execution log — 2026-04-13 09:59 UTC

## 执行小点
- target: `research/quant_digests/2026-04-13_0233_postcost-fundingbasis-deltaneutral-shell.md`
- action: fresh intake first-verdict（统一成本+funding 口径）+ 1 条 honesty/execution realism（funding 结算时点与成交对齐）

## 本轮最小证据
- 使用现有 artifact：
  - `reports/artifacts/quant_digests/2026-04-13_menger_funding_basis_shell_probe/trade_log.csv`
  - `.../summary_8h_fixed.csv`
  - `.../summary_24h_fixed.csv`
- 关键读数（与 digest 口径一致）：
  - signal-off 聚合：`78` 笔，`avg net_bps_20 = -18.87`，`avg net_bps_322 = -31.07`
  - 8h fixed：聚合约 `avg net20 ≈ -18.40`
  - 24h fixed：聚合约 `avg net20 ≈ -17.10`
- honesty/execution 子检查（funding 结算时点对齐）：
  - `trade_log.csv` 中 `funding_bps == 0` 占比 `97.44%`（76/78）
  - 说明当前 15m 直译壳大多数持仓未覆盖有效 funding carry 捕获窗口，执行现实与“靠 carry 补贴成本”的叙事不对齐。

## 结论（改变系统认知）
`post-cost funding×basis delta-neutral shell` 在当前 `15m` portability 的最小可执行路径（signal-off/8h/24h）均未形成费后正边际，且 funding 结算时点对齐检查显示 carry 捕获几乎缺失，不满足 `keep_P1`；本轮 fresh intake 首判收口为 `background/P0`。

## runtime 回写
- 已更新 `docs/BOT2_BOT3_STATE.md`：
  - `Fresh intake slot` 的 `current_target/latest_result/source_record/latest_result_record`
  - `Background pool.latest_parked/latest_parked_record`
  - `cycle_plan` 第 3 项 `result/status=done`

## 尾部动作
- homepage publish：已按要求独立执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但进程无输出且长时间未返回，本轮按“非阻断尾部失败”处理，不回滚 verdict/state/log。
- 中文邮件摘要：已独立执行并成功发送（subject: `[momentum-bot3-auto] funding×basis壳首判降级P0`）。
