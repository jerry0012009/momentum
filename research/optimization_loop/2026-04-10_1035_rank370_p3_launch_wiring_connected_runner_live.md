# Rank 370 — P3 launch wiring 第2步：scheduler + first verified run -> connected_runner_live

- Time: 2026-04-10 10:35 UTC
- Target: `Rank 370 / same-event strike surface mispricing × fair-value recross / time-stop`
- Action type: `P3 / Paper launch queue` wiring
- Verdict: `connected_runner_live`

## 本轮改变了什么 runtime truth
`Rank 370` 已完成 P3 接线最低三件套：scheduler（systemd timer）已启用、first verified run 成功且写出 runtime artifact，`decisive_blocker=none`，因此从 `scheduler_ready_runner_seeded` 收口为 `connected_runner_live`。

## Wiring 落地明细
1. **Scheduler 安装并启用**
   - service: `momentum-rank370-paper-refresh.service`
   - timer: `momentum-rank370-paper-refresh.timer`
   - 安装到 `/etc/systemd/system/` 后执行：
     - `systemctl daemon-reload`
     - `systemctl enable --now momentum-rank370-paper-refresh.timer`
   - 当前状态：`timer active(waiting)`
   - 下一次触发：`2026-04-10 10:45:00 UTC`

2. **First verified run（成功）**
   - 执行：`systemctl start momentum-rank370-paper-refresh.service`
   - 结果：`Result=success`, `ExecMainStatus=0`

3. **首跑产物（artifact/status/ledger）**
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_status.csv`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_state.json`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_queue_ledger.csv`
   - `reports/artifacts/paper_rank370_surface_mispricing/rank370_last_run_summary.json`
   - `reports/site/paper/rank370_surface_mispricing.html`

## 本轮单句结论（用于 cycle_plan.result）
`Rank 370` 已完成 scheduler + first verified run 并写出 paper runtime artifact，且首跑 `decisive_blocker=none`，现可在 runtime truth 标记为 `connected_runner_live`。
