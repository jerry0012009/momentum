# Rank 151：接入 scheduler + status page（2026-03-23 17:12 UTC）

## 本轮路径
- `Paper launch`
- 认领动作：`attach scheduler + status page`

## 本轮完成
1. 新增 host-side cron wrapper：`scripts/run_rank151_breakout_bandpass_paper_runner_cron.sh`
   - 复用已有 paper lane 模式：`flock` 防重入。
   - 若 state 已存在则 `--refresh`，否则 `--init-from-now`。
   - refresh 后自动调用 publish 脚本。
2. 新增 reader-facing status page builder：`scripts/build_rank151_breakout_bandpass_paper_report.py`
   - 读取 `rank151_paper_status.csv` / `rank151_paper_closed_trades.csv` / `rank151_paper_last_run_summary.json` / `rank151_paper_state.json`。
   - 输出页面：`reports/site/factors/paper_rank151_breakout_bandpass_gate/report.html`。
3. 新增发布脚本：`scripts/publish_rank151_breakout_bandpass_paper_page.sh`
   - 发布页面和对应 artifacts 到 `/var/www/momentum-report/...`。
4. 已执行一次 runner + publish 验证
   - runner 输出：`closed_trades_total=1033`
   - `new_closed_trades_appended=0`（符合 frozen digest seed 预期）
   - 页面发布成功：
     - `https://jp.jerrypsy.top/momentum/factors/paper_rank151_breakout_bandpass_gate/report.html`
5. 已接入 host `crontab`
   - `*/15 * * * * /root/clawd/jerry/momentum/scripts/run_rank151_breakout_bandpass_paper_runner_cron.sh >> /root/clawd/jerry/momentum/logs/rank151_breakout_bandpass_paper_runner.log 2>&1`

## 为什么这一步有杠杆
- Rank 151 已完成 launch step 1（runner seed），当前最缺的是“自动跑起来 + 状态能被看见”。
- 这轮没有继续扩策略研究，而是把它从“单次脚本”推进到“host 会定时跑、网页能看状态”的可交付状态。
- 这样下一轮只需做 `verify + handoff`，即可把它移入 `Paper / 正在自动运行` 候选。

## 可验证证据
- 代码：
  - `scripts/run_rank151_breakout_bandpass_paper_runner_cron.sh`
  - `scripts/build_rank151_breakout_bandpass_paper_report.py`
  - `scripts/publish_rank151_breakout_bandpass_paper_page.sh`
- 产物：
  - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_status.csv`
  - `reports/artifacts/paper_rank151_breakout_bandpass_gate/rank151_paper_last_run_summary.json`
  - `reports/site/factors/paper_rank151_breakout_bandpass_gate/report.html`
- host 调度：
  - `crontab -l` 已出现 `momentum-rank151-breakout-bandpass-paper`

## 对 TODO 顶板的回写
- 已把 Rank 151 launch step 2 标记为 `[done] attach scheduler + status page`。
- 下一步保持为：`verify + handoff`。

## 风险 / 边界
- 当前 runner 仍是 `frozen_digest_runner_seed`，不是 raw-bar/live runner。
- 因此 cron 目前验证的是“接线完整、状态一致、可见性正常”，不是“有新真实 closed trade 持续流入”。
- 若后续要升为 raw-bar runner，应作为单独 scope，不应伪装成 routine refresh。

## 建议下一轮（verify + handoff）
1. 等待至少一个 cron 周期后检查 `logs/rank151_breakout_bandpass_paper_runner.log` 和 `rank151_paper_last_run_summary.json` 更新时间是否自然推进。
2. 确认 homepage 已挂出该因子页入口。
3. 若 cron 正常、页面可见、状态时间戳推进，则把 Rank 151 从 `launch queue` 移入 `Paper / 正在自动运行`，并写出 handoff note。
