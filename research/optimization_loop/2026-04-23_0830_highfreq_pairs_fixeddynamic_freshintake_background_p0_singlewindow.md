# 2026-04-23 08:30 UTC — high-frequency pairs fixed-vs-dynamic threshold alpha fresh intake -> background/P0

## 本轮执行对象
- target: `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`
- action: fresh intake first verdict
- policy slot: `Fresh intake slot`

## 最小 decisive blocker
这条线当前**没有通过「非单 pair、非单窗 lucky-run」门槛**。最关键不是 probe 完全没边，而是现有 after-cost 证据**全部只来自单一最近窗口 `2026-04`**，尚不足以证明它是可独立排队的 alpha，而不是 recent pair/regime pocket。

## 本轮复核的现成产物
- digest: `research/quant_digests/2026-04-22_2118_highfreq-pairs-fixeddynamic-threshold-alpha.md`
- summary: `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_summary_2026-04-22.csv`
- pairs: `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_pairs_2026-04-22.csv`
- trades: `reports/artifacts/quant_digests/hf_pairs_fixed_vs_dynamic_probe_trades_2026-04-22.csv`

## 关键读数
summary 口径显示：
- `15m dynamic`: 68 笔，平均 gross `+15.78 bps/笔`；按 digest 里的粗扣 `8 bps round-trip` 后约 `+7.78 bps/笔`
- `5m fixed`: 56 笔，粗扣 `8 bps` 后约 `+6.33 bps/笔`
- `15m fixed`: 粗扣后仅约 `+0.81 bps/笔`
- `5m dynamic`: 粗扣后仅约 `+1.34 bps/笔`

pair 维度看，正边际并非单 pair 独占，说明它**不是纯单 pair 幻觉**；但所有交易的时间戳都落在同一月份：
- `15m dynamic`: `6` 个 pair、`68` 笔交易、**months = 1 (`2026-04`)**
- `15m fixed`: `6` 个 pair、`65` 笔交易、**months = 1 (`2026-04`)**
- `5m fixed`: `6` 个 pair、`56` 笔交易、**months = 1 (`2026-04`)**
- `5m dynamic`: `6` 个 pair、`52` 笔交易、**months = 1 (`2026-04`)**

也就是说，这轮 portability probe 只能说明：
> recent liquid-major majors 上，`selected pair + threshold fade` 在 `2026-04` 这一个短窗里仍有 gross / 粗 after-cost pocket。

它**不能**说明：
- 该 edge 已跨多月成立；
- 该 edge 相比已 live 的 `Rank 424 / Rank 431` pairs family 留下了独立可排队的新 admission；
- `fixed vs dynamic threshold` 本身已经被验证成稳定、可迁移的核心差异来源。

## verdict
`background/P0`

## 改变系统认知的一句话
`high-frequency pairs fixed-vs-dynamic threshold alpha` 已完成 first verdict 并收口 `background/P0`：recent probe 虽显示多 pair 的 gross / 粗 after-cost pocket，但全部证据都只落在单一 `2026-04` 窗口，尚未证明其独立于现有 live pairs family 的跨窗 after-cost alpha，不足以进入 `keep_P1`。

## 尾部执行
- publish_homepage_index: 已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，本轮进程以 `SIGKILL` 结束；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- email: 已执行
  `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] 高频pairs阈值首判收口P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-23_0830_highfreq_pairs_fixeddynamic_freshintake_background_p0_singlewindow.md`
  并成功发送。
