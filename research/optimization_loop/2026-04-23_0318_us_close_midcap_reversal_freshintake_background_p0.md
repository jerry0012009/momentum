# US close-window loser→winner fade fresh intake — first verdict

- Time: 2026-04-23 03:18 UTC
- Target: `research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`
- Slot: Fresh intake
- Action: 对 `US close-window loser→winner fade` 做 fresh intake first verdict，只回答它是否在最小 child execution / turnover realism 下仍保留值得前排保留的独立 after-cost alpha

## Readout used
- Digest: `research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`
- Prior intake log: `research/optimization_loop/2026-04-22_0539_us_close_midcap_reversal_freshintake_background_p0.md`
- Summary artifact: `reports/artifacts/quant_digests/us_session_xs_reversal_probe_summary_2026-04-22.csv`
- Daily artifact: `reports/artifacts/quant_digests/us_session_xs_reversal_close_daily_2026-04-22.csv`

## Minimal decisive blocker
mid-cap scoped close-window loser→winner pocket 在 child execution / turnover realism 下，是否已经证明自己不是单窗口、单调度、maker-first 假设驱动的 gross-only router，而是值得独立排队的 after-cost alpha。

## Findings
1. digest 自己已经承认 broad basket 基本没厚度， strongest claim 只剩 mid-cap scoped `top1/top2 loser vs winner` close-window pocket；这说明对象从一开始就不是 broad close reversal，而是窄化后的定时横截面选择题。
2. 当前唯一明确 summary 里，broad 10-coin `15:30–16:00 -> 16:15–17:00 ET` 只有 `gross_bps_day≈+0.059`、`Sharpe≈0.064`、`cum≈+0.096%`，几乎没有足够厚度支持独立策略身份。
3. 已有 portability readout 也没有证明 mid-cap pocket 在现实摩擦后闭合：上一轮 intake 记录里，best close-window gross 约 `+4.03bps`，统一 `8bps roundtrip` 后转成约 `-3.97bps`；它仍停留在 maker-first / 低冲击 child execution 需要额外成立的 gross edge。
4. 当前可见 daily artifact 还显示 close-window LS 表现高度噪声化，且对象语义更像 `long loser` 方向感强于 `short winner` 的 time-scheduled relative-value router；并没有拿出至少两个非单月、非单 lucky window 支撑的 after-cost 独立 pocket。

## Verdict
`background/P0`。

## Why not keep_P1
这条线没有在现有最小 honesty 证据下证明自己能跨过 child execution / turnover realism。broad basket 几乎无边，而 mid-cap strongest pocket 也仍只是定时 gross edge，需要 maker-first / 低冲击执行才可能存活；因此当前更适合作为 `US close-time router / child-execution admission hint`，而不是继续占用 survivor 的独立 raw alpha。

## Result sentence for runtime
`US close-window loser→winner fade` 已完成 fresh intake first verdict：broad basket close-window reversal 基本无厚度，而 strongest mid-cap top1/top2 pocket 仍停留在 maker-first 假设下的 gross edge，尚未证明能跨过最小 child execution / turnover realism 成为独立 after-cost alpha，因此本轮直接收口 `background/P0`，前排切到下一条 fresh intake `Deribit ↔ OKX 同合约 quote-gap capture`。
