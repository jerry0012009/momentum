# Bybit high positive funding persistence × exit-threshold carry shell — fresh intake first verdict

- Time: 2026-04-21 07:20 UTC
- Target: `research/quant_digests/2026-04-21_0700_bybit-positive-funding-decay-carry-shell.md`
- Cycle step: item 1 / fresh intake first verdict
- Verdict: `background/P0`

## Why this changed system state
`Bybit high positive funding persistence × exit-threshold carry shell` 在当前 same-venue liquid majors、统一 round-trip 成本与 recent 事件稀疏度口径下，没有保住不是单一极端 funding spike 驱动的 after-cost carry pocket，因此本轮 fresh intake 直接收口 `background/P0`。

## Evidence used
- digest 已给出最小 decisive blocker：Bybit public funding history 对 `BTC/ETH/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC/BCH` 的 `180d` portability probe。
- 在 `entry >= 10% APY` 的 `1087` 个事件里，未来 `2` 次 funding 的平均 `gross carry ≈ +1.42bps`，按 repo 风格粗扣 `17bps` round-trip 后，`net ≈ -15.58bps`。
- 更高阈值 `entry >= 15% APY` 在当前 10-major recent 样本里直接 `0` 个事件；live snapshot 最高也仅 `BCHUSDT ≈ +1.0bps/8h ≈ 10.95% APY`。
- 因此这条线当前只证明“完整 carry 壳存在”，没有证明在 broad liquid-major same-venue 版本上存在可复制、非单币、能覆盖成本的 recent carry pocket。

## Decision
- 不给 `keep_P1`。
- 不分配 Rank。
- 直接写入 `background/P0`，保留它作为 funding/carry family 的 admission 教训：先问 persistence 是否足以覆盖真实摩擦，而不是把 funding 排行榜当 raw alpha。

## Runtime writeback
- `Fresh intake slot.latest_result` 更新为本条 first verdict。
- `Fresh intake slot.source_record` 指向本次 digest。
- `Fresh intake slot.latest_result_record` 指向本日志。
- `Background pool.latest_parked` / `latest_parked_record` 追加本条。
- `cycle_plan` item 1 标记为 `done`，写回 result。

## Tail steps
- homepage publish: 执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，异步结果为 `signal SIGKILL`；按 policy 记为非阻断尾步失败，不回滚本轮 verdict/state/log。
- email summary: 执行 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Bybit funding carry首判收口P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-21_0720_bybit_positive_funding_decay_freshintake_background_p0.md` 成功，收件人 `18810813576@163.com`。
