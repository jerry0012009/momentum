# Rank 431 survivor follow-up（rolling admission + maker fill realism）-> promote_P2

- 时间：2026-04-21 10:34 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 431 / cointegration maker-first + hard time-stop pairs`

## 本轮只执行的动作
按 `survivor` 唯一 follow-up 预算，补 1 个最小且会改结论的 honesty 子检查：
1) `rolling pair admission`（28d lookback、daily refresh）
2) `maker fill realism`（maker-first 未成交 -> timeout cross，追加摩擦）

## 过程与最小实现
- 先尝试直接复用 statsmodels 版脚本：
  - `python3 .../2026-04-21_rank431_survivor_followup_probe.py`
  - 结果：`ModuleNotFoundError: No module named 'statsmodels'`
- 因环境缺失依赖，改为最小 numpy/pandas 代理实现（不改排班、不扩展为第二小点）：
  - `reports/artifacts/quant_digests/2026-04-21_rank431_survivor_followup_probe_nostatsmodels.py`
  - 生成 artifacts：
    - `reports/artifacts/quant_digests/rank431_rolling_admission_proxy_1h_2026-04-21.csv`
    - `reports/artifacts/quant_digests/rank431_rolling_admission_proxy_freq_2026-04-21.csv`
    - `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_summary_2026-04-21.csv`
    - `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_trades_2026-04-21.csv`

## 关键证据（会改变层级）
### A) rolling admission 稳定性（28d, daily refresh）
高频入选 pair（top）：
- `AVAXUSDT-SUIUSDT`: `23` 次
- `NEARUSDT-ATOMUSDT`: `15` 次
- `AVAXUSDT-ATOMUSDT`: `13` 次

=> 不是单 pair 单窗偶然命中。

### B) 最小 maker fill realism + 成本梯度（15m child execution）
`rank431_survivor_followup_proxy_summary_2026-04-21.csv` 显示：
- `AVAXUSDT-SUIUSDT`：`trades=24`，`maker_fill_rate≈79.17%`，`net_mean_8/12/16≈+7.94/+3.94/-0.06bps`
- `NEARUSDT-ATOMUSDT`：`trades=23`，`maker_fill_rate≈86.96%`，`net_mean_8/12/16≈+60.45/+56.45/+52.45bps`
- `AVAXUSDT-ATOMUSDT`：`net_mean_8/12/16` 为负（不作为核心宿主）

=> 在 rolling admission + fill realism 下，仍至少两对（`AVAX-SUI`、`NEAR-ATOM`）保留同向 after-cost pocket（8/12bps 明确为正），不满足直接收口 background 的条件。

## 本轮结论（按 success_criterion 二选一）
`promote_P2`。

## 为什么不是 background/P0
本轮 blocker 要求的是：若 rolling admission 后仍有至少两对在 recent + fill realism 下保留同向净边际，则应进入 `P2 admission`；当前满足该条件。

## runtime 写回
- `Surviving candidate slot`：`Rank 431` 移出，`followup_budget_remaining -> 0`
- `Active P2 slot`：`current_target -> Rank 431`
- `cycle_plan` item1：`status -> done`，`result` 写为 promote 结论

## 一句话结果（写回 state）
`Rank 431` survivor 唯一 follow-up 已完成：rolling admission + 最小 maker fill realism 后仍保留至少两对同向 after-cost pocket（`AVAX-SUI`、`NEAR-ATOM`），因此本轮直接 `promote_P2` 并迁入 `Active P2 slot`。

## 尾部执行状态（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 成功，已刷新 `/var/www/momentum-report/index.html`。
- 邮件通知：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank431 survivor跟进已升P2" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-21_1034_rank431_survivor_followup_promote_p2.md` 已成功发送。
