# Rank 426 survivor follow-up -> background/P0

- Time: 2026-04-19 20:32 UTC
- Target: `Rank 426 / high-volume trend-following × low-volume cross-sectional loser->winner fade switch`
- Action: survivor follow-up（唯一一次诚实收口）
- Verdict: `background/P0`

## Why this was the only blocker to test
上一轮 fresh intake 已经把问题收敛为一个单点：`15m` 连续 switch 壳本身太高换手，不该再重复问“有没有 edge”，而应直接回答 **`30m` 还是 `1h` 这种更低换手实现，是否真的能留下跨月份、跨资产仍站得住的 after-cost pocket**。

因此本轮不重排、不补第二维研究，只做 1 条最小 honesty / execution realism 子检查：
- 用 Binance Futures 公共 `15m` K 线重跑同一条 `volume-switch` 思路；
- 比较 `30m` 与 `1h` 两个低换手 rebalance 版本；
- 统一按 `8bps round-trip` 扣减；
- 直接看 `2026-02 / 2026-03 / 2026-04` 三个月切片与 10 个 liquid majors 的贡献分布。

## What I checked
样本：`2026-01-19 14:15 UTC ~ 2026-04-19 14:00 UTC`
标的：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`

最小复算 artifact：
- `reports/artifacts/rank426_survivor_followup_30m_1h_honesty_check.json`

核心口径：
- signal 仍围绕 digest 已定义的主语：`high-volume -> trend-following`，`low-volume -> cross-sectional loser->winner fade`
- 只比较更诚实的低频 rebalance 壳：`30m` vs `1h`
- friction：统一 `8bps round-trip`

## Result
这次最小 honesty 检查没有保住上一轮表面上的“低换手后可留正值”叙事；两个版本都没有形成可升级的 after-cost pocket。

### 30m rebalance
- `gross ≈ -0.35 bps/bar`
- `net8 ≈ -0.90 bps/bar`
- `turnover ≈ 13.08x/day`
- `cum_net8 ≈ -40.56%`

月度切片：
- `2026-02: net8 ≈ -0.76 bps/bar`
- `2026-03: net8 ≈ -0.87 bps/bar`
- `2026-04: net8 ≈ -1.02 bps/bar`

资产贡献上，也不是广泛分散支持；gross 主要由少数币对冲，负贡献更广：
- 正贡献仅较明显见于 `BNB (+0.046 bps/bar)`、`LTC (+0.009)`
- 负贡献更广，尤其 `DOGE (-0.128)`、`ADA (-0.099)`、`ETH (-0.052)`、`AVAX (-0.039)`

### 1h rebalance
- `gross ≈ -0.37 bps/bar`
- `net8 ≈ -0.73 bps/bar`
- `turnover ≈ 8.70x/day`
- `cum_net8 ≈ -34.54%`

月度切片：
- `2026-02: net8 ≈ -0.63 bps/bar`
- `2026-03: net8 ≈ -0.76 bps/bar`
- `2026-04: net8 ≈ -0.74 bps/bar`

同样没有出现“至少一个月份稳、至少一个核心资产群稳”的 admission 级 pocket；正贡献仍只剩 `BNB (+0.064)` 与 `LTC (+0.017)` 这类少数抵消项，而 `ETH/SOL/DOGE/ADA/AVAX` 仍整体拖累。

## System-changing conclusion
`Rank 426` 的 survivor 唯一 follow-up 已经把决定性问题诚实收口：**当这条 volume-switch 主语被压到更诚实的 `30m/1h` 低换手实现并统一按 `8bps` 扣减后，两个版本在 `2026-02/03/04` 都没有留下稳定正的 after-cost pocket，且跨资产贡献不广，不能升 `P2`；因此 survivor 预算耗尽，直接转入 `background/P0`。**

## Files touched
- `reports/artifacts/rank426_survivor_followup_30m_1h_honesty_check.json`
- `docs/BOT2_BOT3_STATE.md`
- `research/optimization_loop/2026-04-19_2032_rank426_survivor_followup_background_p0_30m_1h_honesty.md`

## Tail-step status
- Homepage publish tail step: attempted via `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`, but the async process ended with `SIGKILL`; treated as non-blocking tail failure and does not change this round's verdict / state / log.
- Email notification: sent successfully via `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py`.
