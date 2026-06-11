# US close-window loser→winner fade fresh intake — first verdict

- Time: 2026-04-22 05:39 UTC
- Target: `research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`
- Slot: Fresh intake
- Action: 对 `US close-window loser→winner fade` 做 fresh intake first verdict，只回答它是否在统一成本/执行现实下仍保留值得前排保留的独立 after-cost alpha，还是更应诚实收口为定时 router

## Readout used
- Digest: `research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`
- Broad portability artifact: `reports/artifacts/quant_digests/us_session_xs_reversal_probe_summary_2026-04-22.csv`
- Earlier perp portability artifact: `reports/artifacts/literature/us_session_xs_reversal_perp_probe_2026-04-12.csv`
- Earlier asset probe: `reports/artifacts/literature/us_session_xs_reversal_perp_asset_probe_2026-04-12.csv`

## Minimal decisive blocker
这条线是否已经留下“统一成本/执行现实下仍值得 desk 保留为独立 raw alpha”的证据，而不只是 close-window 定时横截面 router。

## Findings
1. 最新 digest 自己给出的 strongest pocket 已经是 **mid-cap 子集、top1/top2、固定 close-window** 的窄口袋，而不是 broad basket 稳定规律：
   - broad 10-coin close-window basket 只有 `gross ≈ +0.06 bps/day`、Sharpe 约 `0.06`，几乎没有厚度；
   - 所谓 strongest claim 主要来自缩到 `ADA/XRP/DOGE/AVAX/LINK/LTC` 一类 mid-cap 子集后的 `top1/top2 loser vs winner`。
2. 更早的 perp portability 也说明这条线只有 **gross edge**，还没有跨过统一现实摩擦：
   - best close window (`15:30–16:00 -> 16:15–17:15`) 只有 `gross_mean_bps ≈ +4.03`；
   - 同一口径统一按 `8bps` roundtrip 后直接变成 `net8_mean_bps ≈ -3.97`，Sharpe 也转负；
   - 更短持有或更晚入场都没有把 net 拉回正值。
3. asset probe 虽显示 loser leg 在 `BTC/ETH/SOL/BNB/XRP/DOGE` 上经常有反弹方向感，但 cross-sectional short winner leg 很薄，最佳窗口里 `XS_leg long_loser ≈ +8.11bps`、`short_winner ≈ -0.06bps`，说明当前更像“定时挑弱者反弹 + 对强者做相对锚”的 router 语义，而不是已经闭合的四腿独立 alpha。
4. 现有证据没有证明它在统一成本下仍保留“至少两个非单一 symbol/月份支撑的 after-cost pocket”；相反，edge 明显依赖：
   - 单一 US close 时间窗；
   - mid-cap universe 筛选；
   - maker-first / 低冲击执行假设尚未验证。

## Verdict
`background/P0`。

## Why not keep_P1
这条 `US close-window loser→winner fade` 当前没有诚实证明自己是可独立承接的 short-cycle after-cost alpha：broad basket 几乎无边，最强 pocket 只存在于收窄后的 mid-cap close-window 选择题里，而现成 perp portability 在统一 `8bps` 摩擦下已经转负。它更适合被降格为 **time-scheduled cross-sectional router / child-execution admission hint**，而不是继续占用前排 survivor 槽位的新独立对象。

## Result sentence for runtime
`US close-window loser→winner fade` 已完成 fresh intake first verdict：broad basket close-window reversal 几乎没有厚度，最强 mid-cap top1/top2 pocket 也仍停留在 maker-first 假设下的 gross edge；在现有统一成本/执行现实证据里更像定时横截面 router，而不是值得保留 survivor 的独立 after-cost alpha，因此本轮直接收口 `background/P0`。

## Tail actions
- Homepage refresh: attempted via `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`; non-blocking tail failure (`SIGKILL` before captured output), verdict/state/log retained.
- Email: sent via `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] 收口为定时路由" --body-file <this log>`.
