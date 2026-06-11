# 2026-04-19 14:25 UTC — fresh intake first verdict：persistent lower-VWAP underpricing × long-side reclaim -> background/P0

## Target
- `research/quant_digests/2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md`

## Why this was the current front pending item
- `BOT2_BOT3_STATE.md` 当前 `cycle_plan` 第 1 个 pending 小点要求对 `persistent lower-VWAP underpricing × long-side reclaim` 做 fresh intake first verdict。
- 本轮只执行这一个小点，不重排后续任务。

## Minimal blocker checked
- 唯一 blocker：现成 `5m` 微正 reclaim pocket 在 `next-bar entry + 统一成本` 下，是否仍留有不是 DCA / 高常驻壳幻觉的独立 after-cost 价值。

## Evidence used
- Digest：`research/quant_digests/2026-04-19_0715_vwap-lowerband-persistent-placement-alpha.md`
- Summary artifact：`reports/artifacts/quant_digests/2026-04-19_vwap_lowerband_reclaim_summary.csv`

## Key numbers
- `15m all_events`: hold `4/8/12` bars 分别约 `-3.69 / -8.95 / -13.63 bps` gross。
- `15m top1_deepest_per_ts`: hold `4/8/12` bars 也仅约 `-1.15 / -4.76 / -7.18 bps` gross。
- `5m all_events`: hold `3/6/12` bars 只有约 `+0.87 / +0.88 / +1.05 bps` gross。
- `5m top1_deepest_per_ts`: hold `3/6/12` bars 仅约 `+0.34 / +0.84 / +0.64 bps` gross。
- 按 digest 统一口径粗扣 `8bps` 后，`5m` 全部仍明显为负，无法保住独立 after-cost pocket。

## Verdict
- `background/P0`

## Reasoning
- 这条线可迁移出来的只是“persistent lower-VWAP underpricing -> bounce”母题，但当前可见 pocket 只有极薄 `5m` gross，远不足以覆盖统一成本。
- `15m` 在更诚实的 next-bar entry 下直接转负，说明把 repo 的高暴露 / DCA / 常驻仓位外壳剥掉后，裸 alpha 本身没有表现出可独立承接的厚度。
- 当前没有证据表明它摆脱了单纯 placement shell / 持仓管理幻觉，因此不值得占用 survivor 槽位。

## Runtime-changing result sentence
- `persistent lower-VWAP underpricing × long-side reclaim` 的 first verdict 已诚实收口：`15m` 主信号整体为负、`5m` 仅剩约 `+0.9~+1.1bps` 薄 gross，统一 `8bps` 后无独立 after-cost pocket，因此本轮直接转入 `background/P0`。

## Notes
- 本轮无 rank 分配需求：结论不是 `keep_P1 / promote_P2 / promote_P3`。
- 本轮无层级升级 / P3 wiring 动作。
- 尾部刷新：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步返回 `SIGKILL`，按 policy 记为非阻断 tail failure，不回滚已写出的 state / verdict / log。
- 尾部通知：中文邮件已成功发送。
