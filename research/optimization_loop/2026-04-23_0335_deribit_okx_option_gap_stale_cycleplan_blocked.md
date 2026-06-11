# Deribit ↔ OKX 同合约 option quote-gap fresh intake：blocked（stale cycle_plan / already closed）

- 时间：2026-04-23 03:35 UTC
- 对象：`research/quant_digests/2026-04-22_0353_deribit-okx-option-quote-gap-shell.md`
- 执行动作：cycle_plan front item audit
- 结论：`blocked`

## 阻断原因
当前 `cycle_plan` 的第 1 个 pending 小点要求对 `Deribit ↔ OKX 同合约 quote-gap capture` 再做一次 fresh intake first verdict；但该对象已经在 `research/optimization_loop/2026-04-22_1618_deribit_okx_option_gap_freshintake_background_p0.md` 被明确收口为 `background/P0`。

按 `BOT2_BOT3_POLICY.md`：
- `Background pool` 对象不得自动回到前排；
- bot3 若发现旧候选被自动拉出 `Background pool`，应拒绝执行该歪路径并回退到合法动作；
- 但本轮又禁止 bot3 自行重排 `cycle_plan` 或替 bot2 执行下一条 pending 小点。

因此，本轮对这个最前 pending 项的唯一合法处理是：把它标记为 stale / blocked，而不是重复做一次已完成的 first verdict。

## 已核实的既有 runtime 事实
- 已存在先前收口日志：`research/optimization_loop/2026-04-22_1618_deribit_okx_option_gap_freshintake_background_p0.md`
- 已存在对应 probe artifact：`reports/artifacts/quant_digests/2026-04-22_deribit_okx_option_gap_probe_summary.csv`
- 该先前结论已明确写出：12 次连续 snapshot 下最大 gap 仅约 `0.10%`、`>0.25%` 为零，未证明多腿期权 execution realism 后仍有独立新增 after-cost pocket。

## runtime-impact
`cycle_plan` 第 1 项 `Deribit ↔ OKX 同合约 quote-gap capture` 已被历史 first verdict 收口到 `background/P0`，本轮继续把它作为 front pending fresh intake 属于 stale cycle_plan / background reopen 冲突；因此当前小点只可标记 `blocked`，不得重复执行或据此占用前排 fresh intake 资源。
