# Rank 368 — P3 launch wiring: connected_runner_live

- Time: 2026-04-10 08:05 UTC
- Target: `Rank 368 / cross-exchange funding extreme × band-stretch fade shell`
- Action type: `P3 / Paper launch queue` wiring
- Verdict: `connected_runner_live`

## 本轮改变了什么 runtime truth
`Rank 368` 已完成 P3 接线最低三件套：dedicated runner、scheduler（systemd timer）与 first verified run，且首跑未出现单一 decisive blocker，因此从 `paper launch wiring pending` 收口为 `connected_runner_live`。

## Wiring 落地明细
1. **Dedicated runner script**
   - `scripts/run_rank368_funding_extreme_bandfade_paper_runner.py`
   - 固定 paper scope：`5m alt-heavy (ETH/ADA/DOGE) + funding_abs_quantile>=0.90 + time_stop=12`
   - 固定执行约束：`round-trip friction <= 8bps`

2. **Scheduler**
   - service: `momentum-rank368-paper-refresh.service`
   - timer: `momentum-rank368-paper-refresh.timer`
   - 已安装到 `/etc/systemd/system`，并 `enable --now` 成功；当前 `timer active(waiting)`，下一次触发 `08:15 UTC`

3. **First verified run（成功）**
   - 执行：`systemctl start momentum-rank368-paper-refresh.service`
   - 结果：`status=0/SUCCESS`
   - 产物：
     - `reports/artifacts/paper_rank368_funding_extreme_bandfade/rank368_status.csv`
     - `reports/artifacts/paper_rank368_funding_extreme_bandfade/rank368_state.json`
     - `reports/artifacts/paper_rank368_funding_extreme_bandfade/rank368_launch_checks.csv`
     - `reports/artifacts/paper_rank368_funding_extreme_bandfade/rank368_last_run_summary.json`
     - `reports/site/paper/rank368_funding_extreme_bandfade.html`

## 本轮单句结论（用于 cycle_plan.result）
`Rank 368` 已完成 runner + scheduler + first verified run 三件套并写出 paper artifact，且首跑 `decisive_blocker=none`，现可在 runtime truth 标记为 `connected_runner_live`。
