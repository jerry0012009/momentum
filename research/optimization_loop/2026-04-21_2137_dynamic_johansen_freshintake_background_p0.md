# 2026-04-21 21:37 UTC — dynamic Johansen spread × forecast-percentile fade fresh intake first verdict

## 执行动作
- 按 `cycle_plan` 执行当前最前 pending 小点：`research/quant_digests/2026-04-21_1438_dynamic-johansen-forecast-spread-alpha.md`
- 只补 1 个最小 decisive blocker：检查这条 `dynamic Johansen spread × forecast-percentile fade` 在 desk 口径 `5m/15m`、更严 percentile admission、time-stop 替代慢速 zero-cross、统一双腿/多腿成本与 turnover realism 下，是否还保有独立 after-cost spread pocket。

## 读取证据
- `reports/artifacts/quant_digests/2026-04-21_dlcointegration_thresholdscan_5m.csv`
- `reports/artifacts/quant_digests/2026-04-21_dlcointegration_thresholdscan_15m.csv`
- `reports/artifacts/quant_digests/2026-04-21_dlcointegration_probe_5m.json`
- `reports/artifacts/quant_digests/2026-04-21_dlcointegration_probe_15m.json`

## 最小 honesty / realism 结论
### 5m
- 默认 `10/90` admission：`entries=4`，`active_bar_share≈77.78%`，`cum_net≈-0.5718%`，`trade_mean_net_bps≈-14.34bps`
- 更严 `5/95` admission：`entries=3`，`active_bar_share≈27.12%`，`cum_net≈-0.2187%`，`mean_net_bps_per_bar≈-0.0412bps`
- 说明：把 admission 收紧以后，持仓黏性确实下降，但 after-cost 仍没有翻正；这不是“只差一点 time-stop 微调”的状态，而是 pocket 本身仍薄。

### 15m
- 默认 `10/90` admission：`entries=6`，`active_bar_share≈80.84%`，`cum_net≈-1.5025%`，`trade_mean_net_bps≈-25.23bps`
- 更严 `5/95` admission：`entries=6`，`active_bar_share≈78.97%`，`cum_net≈-1.3368%`
- 说明：`15m` 比 `5m` 更差；把分位阈值收紧并没有把它从“慢、黏、成本吃掉”的形态中救出来。

## 对 cycle 小点的回答
- `success_criterion` 要求：只有当更严 percentile admission + time-stop 后，至少一个 basket/pair 组合在统一成本后为正，且不是对已 live pair-MR family 的弱重复，才允许 `keep_P1`。
- 当前证据不满足：
  1. `5m/15m` 在更严 admission 下仍全部费后为负；
  2. 信号 active share 仍偏高，显示它依旧容易演变成持仓黏滞的慢速 MR；
  3. 语义上它只是 `pair/stat-arb mean-reversion` 家族的多腿 forecast 版壳，没有证明比已 live 的 `Rank 431 / cointegration maker-first + hard time-stop pairs`、`Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade` 留下独立、可迁移、after-cost 更厚的新 pocket。

## 本轮 verdict
`dynamic Johansen spread × forecast-percentile fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：现有 `5m/15m` probe 在更严 `5/95` admission 下仍分别只有 `3/6` 笔、active bar share 约 `27%/79%`，统一成本后 `cum_net≈-0.22%/-1.34%`；默认 `10/90` 更差且 trade mean net 分别约 `-14.34/-25.23bps`，说明它没有在 time-stop/成本现实下留下区别于已 live `Rank 431/424` pair-MR family 的独立 after-cost spread pocket。

## 回写
- `Fresh intake slot` 已切换到下一条：`research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
- `cycle_plan` 第 2 项已写成 `done`
- `Background pool` 已追加本轮 parked 结论

## 尾部执行状态（非阻断）
- 首页刷新命令 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步返回 `signal SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件命令 `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] dynamic Johansen收口P0" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-21_2137_dynamic_johansen_freshintake_background_p0.md` 已成功发送。
