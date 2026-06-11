# bot3 optimization loop — clock-hour weekpart cross-sectional alpha first verdict

- Time: 2026-04-24 21:00 UTC
- Cycle item: 2
- Target: `research/quant_digests/2026-04-23_1458_clockhour-weekpart-xs-alpha.md`
- Verdict: `background/P0`

## What I checked
只执行当前最前的 pending 小点：对 `same-hour cross-sectional loser→winner fade / leader continuation` 做 fresh intake first verdict，只回答它是否留下了**非单 hour-bucket、非单 lookback lucky-run**、且能够穿过现实 friction 的 after-cost cross-sectional pocket，而不是只剩 `fixed-hour ranking / child-exec` 提示。

读取了：
- `research/quant_digests/2026-04-23_1458_clockhour-weekpart-xs-alpha.md`
- `reports/artifacts/quant_digests/2026-04-23_1458_clockhour_weekpart_xs_probe_summary.csv`

## Key evidence
### 1) 当前 probe 留下的是 hour-family 级 gross edge，不是已证实的 after-cost pocket
本轮最强结果集中在 `H3_reg_hours_weekdays_momentum`：
- `12d`: `Sharpe ≈ 0.76`, `mean ≈ +0.320 bps/hour`
- `15d`: `Sharpe ≈ 0.88`, `mean ≈ +0.367 bps/hour`
- `18d`: `Sharpe ≈ 1.17`, `mean ≈ +0.477 bps/hour`
- `21d`: `Sharpe ≈ 0.70`, `mean ≈ +0.293 bps/hour`

这说明它确实不是单一 lookback 偶然撑住；weekday regular-hours 的 same-hour continuation 在最近样本里有 **family-level gross consistency**。但 CSV 给出的仍是 `mean_ret_bps_per_hr` 的 gross 结果，没有把真实换仓 friction 扣到策略口径里。

### 2) 这条线的 gross 幅度太小，尚不足以支撑“after-cost 明显成立”
目标 digest 自己给出的现实执行建议是 `4/8/12 bps round-trip` 成本阶梯，而本轮可见最强 gross 均值只有 `~0.48 bps/hour`；其它可行 lookback 也只在 `~0.29–0.37 bps/hour`。对于一个按固定 hour bucket 做横截面重配、默认需要 long-short 篮子轮换的策略，这个 gross 幅度离“费后仍显著成立”还有明显距离。

也就是说，这里真正被证明的是：
- `fixed-hour × cross-sectional continuation` 这个想法有一定可迁移性；

但**尚未被证明**的是：
- 它在统一现实成本口径下形成了可独立交易的净 alpha pocket；
- 不是靠理想化的低换仓或 child-exec 想象把 gross edge 放大成可落地结果。

### 3) H1 已弱，H3 虽较稳但新增价值仍更像设计提示而非可前排排队的新 raw alpha
同一 summary 里：
- `H1_after_hours_weekdays_reversal, 1d`: `Sharpe ≈ -0.07`
- `H1_after_hours_weekdays_reversal, 2d`: `Sharpe ≈ +0.15`

因此 repo 的双主线里，短窗 reversal 已基本失去推进价值；剩下真正站得住的只有 `weekday regular-hours same-hour momentum` 这一个 family。可它目前留下的新增信息主要还是：
- 用 fixed hour / weekpart 去做横截面分桶；
- 把 `1h parent -> 15m/5m child execution` 作为执行层；
- 提醒 desk 不要把所有 intraday cross-sectional edge 当成全天候信号。

这些更像后续 parent-signal / execution design 的研究提示，而不是已经足够进入 survivor 的独立 after-cost raw alpha。

## Result
`same-hour cross-sectional loser→winner fade / leader continuation` 的 fresh intake first verdict 已诚实收口 `background/P0`：当前 portability probe 虽显示 `weekday regular-hours` 的 same-hour continuation 在 `12/15/18/21d` lookback 上具有非单 lookback 的 gross 一致性，但可见收益只有 `~0.29–0.48 bps/hour`，尚未证明能穿过该类 hourly cross-sectional 重配策略所需的现实 friction；H1 reversal 也未复现，因此新增价值主要退化为 `fixed-hour cross-sectional ranking + 1h parent -> 15m/5m child execution` 的设计提示，不足以进入 survivor。

## Tail step status
- homepage publish（best-effort）: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 会话 `kind-tidepool` 在无输出状态下持续挂起，已按非阻断尾部失败处理并终止；不回滚本轮 verdict/state/log。
- email notify: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] clock-hour 横截面时段 alpha 收口 P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-24_2100_clockhour_weekpart_xs_alpha_background_p0.md` 已成功发送。
