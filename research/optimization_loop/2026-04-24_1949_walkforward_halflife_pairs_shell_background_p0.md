# bot3 optimization loop — walk-forward pair admission × half-life-matched spread z-score fade first verdict

- Time: 2026-04-24 19:49 UTC
- Cycle item: 1
- Target: `research/quant_digests/2026-04-24_0503_walkforward-halflife-pairs-shell-honest-oos.md`
- Verdict: `background/P0`

## What I checked
只执行当前最前的 pending 小点：对 `walk-forward pair admission × half-life-matched spread z-score fade` 做 fresh intake first verdict，只回答它是否在保留作者诚实 OOS 亏损口径后，仍留下相对已 live `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade` 与 `Rank 431 / cointegration maker-first + hard time-stop pairs` 可独立排队的 after-cost pairs pocket，而不是只剩 walk-forward / half-life / admission hygiene 提示。

读取了：
- `research/quant_digests/2026-04-24_0503_walkforward-halflife-pairs-shell-honest-oos.md`
- `reports/artifacts/literature/walkforward_pairs_portability_probe_2026-04-23.csv`
- 已有同族收口记录：
  - `research/optimization_loop/2026-04-23_0912_walkforward_cointegration_halflife_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-21_2322_dynamic_cointegration_halflife_freshintake_background_p0.md`
  - `research/optimization_loop/2026-04-24_0352_pairs_zscore_shell_freshintake_background_p0.md`

## Key evidence
### 1) repo 自带最诚实的信息仍是：真实 OOS 亏损，新增价值首先是 honest shell
目标 digest 已明确记录原 repo 的真实 OOS 结果为负：Kraken 11 币、2025-02~2026-01 walk-forward OOS 下，raw annual return 约 `-18.8%`、risk-managed 版约 `-15.7%`。这说明它最强的新意首先是把 pair discovery / hedge ratio / z-score / cost / walk-forward / drawdown stop 串成完整研究壳，而不是已经证明 short-cycle crypto desk 上存在可直接排队的新 after-cost alpha。

### 2) 本地 portability probe 的正 pocket 仍主要集中在少数 alt-heavy pairs，没有形成独立 family
`walkforward_pairs_portability_probe_2026-04-23.csv` 里，费后为正的可见 pocket 主要集中在：
- `15m BNBUSDT/DOGEUSDT`: `14` 笔，`avg_net_bps ≈ +46.37`
- `15m SOLUSDT/DOGEUSDT`: `18` 笔，`avg_net_bps ≈ +13.08`
- `5m ADAUSDT/LINKUSDT`: `11` 笔，`avg_net_bps ≈ +11.72`
- `5m DOGEUSDT/LINKUSDT`: `12` 笔，`avg_net_bps ≈ +10.02`
- `5m ADAUSDT/DOGEUSDT`: `8` 笔，`avg_net_bps ≈ +9.55`

但同一 probe 下，多数其它 pairs 仍明显转负：
- `15m XRPUSDT/DOGEUSDT`: `avg_net_bps ≈ -4.89`
- `15m DOGEUSDT/LINKUSDT`: `avg_net_bps ≈ -7.54`
- `15m SOLUSDT/XRPUSDT`: `avg_net_bps ≈ -7.78`
- `15m SOLUSDT/BNBUSDT`: `avg_net_bps ≈ -26.46`
- `5m SOLUSDT/DOGEUSDT`: `avg_net_bps ≈ -4.63`
- `5m SOLUSDT/ADAUSDT`: `avg_net_bps ≈ -6.03`

这说明可见正边际仍是少数 `DOGE/ADA/LINK` 偏 alt-heavy pair 的 pocket，不是可与已 live pairs queue 并列的新广谱宿主。

### 3) 新增语义仍退化为已 live pairs family 可吸收的设计提示
当前 runtime 已 live：
- `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
- `Rank 431 / cointegration maker-first + hard time-stop pairs`

而这次对象真正留下的新增语义仍是：
- `walk-forward` pair admission
- `half-life` 绑定 rolling window / timeout
- 更诚实地公开 OOS 失败结果

这些更像现有 pair-MR family 的研究卫生、admission discipline 与 timeout tuning 提示，并没有证明：
1. 留下不同于 `Rank 424 / 431` 的 durable pair set；
2. 在非单 pair、非单窗口 lucky-run 之外形成新的 after-cost pocket；
3. 把 walk-forward + half-life 从“方法卫生”抬升成值得独立排队的新 raw alpha 主语。

## Result
`walk-forward pair admission × half-life-matched spread z-score fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：它虽然提供了比常见 pairs repo 更完整、且愿意公开亏损的 honest shell，本地 portability probe 也在 `BNB/DOGE`、`SOL/DOGE` 与若干 `ADA/LINK/DOGE` 组合上留下费后正 pocket，但这些结果仍集中于少数 alt-heavy pairs，没有证明超出已 live `Rank 424 / 431` pairs family 的独立、可迁移 after-cost alpha；新增价值主要退化为 `walk-forward admission + half-life-matched window/timeout + honest OOS discipline` 的 pairs 设计提示，因此不进入 survivor。

## Tail step status
- homepage publish（best-effort）: `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步会话 `marine-slug` 最终 `SIGKILL` 失败（无输出）；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- email notify: `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] walk-forward pairs 壳收口 P0" --body-file ...` 已成功发送。
