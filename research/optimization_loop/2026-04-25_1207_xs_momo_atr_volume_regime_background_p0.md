# Rank pending fresh intake verdict — 24h relative-strength rotation × ATR/volume 确认 × daily regime sizing → background/P0

- Time: 2026-04-25 12:07 UTC
- Target: `research/quant_digests/2026-04-25_1001_xs-momo-atr-volume-regime-shell.md`
- Cycle slot: `Fresh intake slot`
- Action: first verdict with one minimal decisive blocker check
- Verdict: `background/P0`

## What I checked
I used the digest plus the source repo README / strategy report to answer the single decisive question in this cycle-plan item: does this repo already show at least one portable, after-cost `1h parent -> 15m/5m child` cross-sectional rotation pocket that is clearly positive and not just a gross small-universe story?

## Evidence that matters
1. The repo does define a real raw-alpha shell: `24h` relative momentum ranking, long top 2 / short bottom 2, with ATR and volume as veto layers and a daily regime score as sizing overlay.
2. Out-of-sample headline numbers are gross-only: README explicitly says `All returns are gross of transaction costs`.
3. Execution realism is still optimistic: fills assumed at next bar open; 15m/5m features are computed but `not yet integrated into execution timing`.
4. The tested universe is only 7 coins, with common start date anchored to AVAX listing, so the claimed pocket is still a narrow fixed-basket result rather than a portability proof across a broader liquid universe.
5. The repo/report provide no after-cost child-execution artifact showing that any specific bucket/hold variant survives `8/12/20 bps`-style friction or even a simpler taker-fee haircut.

## Why this changes the system view
This object is still useful as a design shell for future cross-sectional research, but the decisive blocker for front-slot survival was proof of an independently tradable after-cost pocket. That proof is absent. The current evidence supports `methodology value / reusable shell`, not `keep_P1`.

## Result sentence for runtime
`24h relative-strength rotation × ATR/volume × daily regime sizing` first verdict 收口 `background/P0`：repo 证明了 cross-sectional winner/loser rotation 壳可复现，但公开证据仍停留在 7 币 fixed-universe 的 gross open-fill 回测，既没有成本后 `1h parent -> 15m/5m child` pocket artifact，也没有排除结果主要来自小样本 bull/beta 暴露的可迁移证明，因此当前更适合作为 background methodology shell，而不是前排候选。

## State impact
- `Fresh intake slot` front object resolved to `background/P0`.
- Front slot advances to the next pending fresh intake item: `research/quant_digests/2026-04-25_1116_xs-rank-sign-router-paper.md`.
- No rank assigned, because verdict did not reach `keep_P1`.

## Tail actions
- Homepage refresh attempt: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` did not complete successfully in this run (process ended by `SIGKILL`); treated as non-blocking tail failure per policy.
- Email notify: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] 横截面动量壳收口到后台" --body-file ...` succeeded (`Email sent to: 18810813576@163.com`).
