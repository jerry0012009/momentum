# Rank154 Final Archive Close-out

时间：2026-05-10 03:34 UTC

## Verdict

Rank154 系列正式收口：

- **Rank154 / Crypto-Stat-Arb**：`ARCHIVED / failed release candidate`
- **Rank154b / young funding continuation**：`ARCHIVED / research lead only / no paper lane`

本 close-out 的目的不是再提出一个优化方向，而是防止后续文档、网页、TODO 或旧 paper runner 把 rank154 误读成当前可推进候选。

## 证据链

1. 原 Rank154 长历史验证失败：combined carry+momo+breakout 组合不能跨 regime 保持稳定 IC / spread。
2. Postmortem 进一步确认：combined 信号本身长期接近无预测力，不是单纯执行成本问题。
3. 154b 拆出 funding-only young coin lead 后，price IC 有轻微正值，但扣 funding 后 long_total IC 转负。
4. 154b 严格 portfolio 回测在 realistic 20bps 成本下为负，且 2024/2025 OOS 弱，2026 前四个月贡献过大。

## Final numbers

### Rank154b core backtest

- Universe：`listing_days 180-365d` + trailing 30d quote volume Top30
- Signal：`funding_rate_last`，高 funding long / 低 funding short
- Portfolio：5d staggered，20bps turnover cost
- Period：2021-05-03 → 2026-04-30
- Return：`-4.3%`
- Annualized：`-0.9%`
- MaxDD：`-63.1%`
- Sharpe：`0.14`

### Rank154b IC

- 5d price IC：`+0.0195`
- 5d long_total IC：`-0.0089`
- 10d price IC：`+0.0230`
- 10d long_total IC：`-0.0125`

解释：funding 因子能预测一点价格延续，但高 funding 做多需要支付 funding；扣 funding 后不是净 alpha。

## Files / pages updated

- `docs/RANK154_ARCHIVE_CLOSEOUT.md`
- `docs/TODO.md`
- `research/optimization_loop/2026-05-09_rank154b_young_funding_hypothesis.md`
- `scripts/build_rank154_hub.py`
- `scripts/build_rank154_archive_closeout_report.py`
- `scripts/publish_report_site.sh`
- `reports/site/paper/rank154_hub.html`
- `reports/site/paper/rank154_archive_closeout.html`
- `reports/site/paper/rank154b_young_funding_backtest.html`

## Operational close-out

Rank154 paper sidecar timer was active before close-out. It has been stopped and disabled as part of archive closure:

```bash
systemctl stop momentum-rank154-paper-sidecar-refresh.timer
systemctl disable momentum-rank154-paper-sidecar-refresh.timer
```

The paper artifacts remain as historical evidence. They should not be used as current live/paper status.

## Reopen conditions

Do not reopen Rank154 by parameter tuning. A future reopen requires a new hypothesis and a new rank/name.

Minimum requirements for any future funding-age lead:

1. Explicit regime definition before testing.
2. IC positive on `long_total`, not just `price`.
3. Portfolio positive after realistic new-coin slippage and funding.
4. 2024/2025-style weak regimes handled by predeclared gate, not explained after the fact.
5. Separate release candidate name; do not call it Rank154 fix.
