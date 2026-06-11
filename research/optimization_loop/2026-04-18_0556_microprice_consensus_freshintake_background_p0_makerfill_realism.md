# microprice deviation × top-book imbalance consensus fresh intake first verdict

- Time: 2026-04-18 05:56 UTC
- Target: `research/quant_digests/2026-04-17_1835_microprice-imbalance-consensus-mm-shell.md`
- Cycle slot: item2 / conditional fresh intake
- Verdict: `background/P0`

## Why this changed runtime truth
这条 `microprice deviation × top-book imbalance consensus` 目前可见 strongest edge 仍主要停留在 `BTCUSDT` 单标的、约 `240s` 的 `1s` REST depth snapshot 上的 pre-cost mid drift：summary 显示 `micro_dev` / `imbalance` 的 top-bottom spread 约为 `1s:+0.55bps`、`5s:+1.02bps`、`10s:+1.38bps`。这能说明 signal direction 有，但还不足以诚实支撑一个新的 ultra-short microstructure front object。

决定性 blocker 不是“信号完全不存在”，而是 **maker-fill / queue-latency realism**：
1. strongest spread 仍只有 `~0.5–1.4bps` 的 cost-before-drift；
2. probe 只看 future mid move，没有把 maker 成交概率、排队优先级、撤单/改价时滞、挂单未成交的 adverse selection 算进去；
3. 采样口径还是 `1s` REST 轮询，不是更接近真实做市时序的增量 WebSocket/L2 queue replay；
4. digest 自己也把下一步明确指向 `maker simulator` 与 `WebSocket L2`，说明当前证据层级仍停在 signal sanity，而非可交易 shell admission。

因此，本轮 fresh intake 直接收口为 `background/P0`：当前证据只足以说明“盘口压力和未来几秒 mid drift 同向”，还不足以说明 desk 能在诚实的 maker fill / cancel-delay 现实下拿到这段边际。

## Evidence used
- `research/quant_digests/2026-04-17_1835_microprice-imbalance-consensus-mm-shell.md`
- `reports/artifacts/quant_digests/2026-04-17_kalman_imbalance_fairvalue_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-17_kalman_imbalance_fairvalue_probe.py`

## Runtime-facing result sentence
`microprice deviation × top-book imbalance consensus` 当前 strongest 证据仍只是 `~0.5–1.4bps` 的 pre-cost mid drift，且 maker fill / queue priority / cancel-delay realism 尚未闭合，因此本轮 fresh intake 直接收口 `background/P0`。

## Tail-step execution notes
- Homepage publish (`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`) 未在轮次窗口内完成，异步结果为 `SIGKILL`；按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- Email notify (`send_text_email.py`) 已成功发送。
