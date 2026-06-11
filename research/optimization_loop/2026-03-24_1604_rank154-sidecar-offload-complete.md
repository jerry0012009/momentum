# bot3 自动优化日志：Rank 154 / Crypto-Stat-Arb sidecar offload complete

时间：2026-03-24 16:04 UTC

## 路径判断
- Scout 主点：`Rank 154 / Crypto-Stat-Arb` 的 P3 handoff 收口
- 当前执行小点：把现有 `refresh-only handoff packet` 真正落成独立后排 sidecar，而不是继续占 bot2/bot3 前排轮次
- 约束：不回头重开 admission compare；不再给 154 继续拆新的“接线文档轮”

## 本轮执行
1. 复核现有 handoff truth，确认 154 在研究侧已经只剩最后一跳：
   - dedicated runner：`scripts/run_rank154_crypto_stat_arb_paper_runner.py`
   - handoff packet：`reports/artifacts/paper_rank154_crypto_stat_arb_runner/rank154_refresh_only_handoff_packet.md`
   - runtime truth：`rank154_paper_state.json / status.csv / queue_ledger.csv / report.html`
2. 改造 dedicated runner，使其支持真实 scheduler attach writeback：
   - 新增 `--scheduler-attached`
   - 新增 `--scheduler-unit`
   - refresh 时可把对象写成 `handoff_complete_refresh_only_scheduler_attached`
   - status / report 不再只显示 `design-only not running`，而会明确显示 sidecar 已 attached，但仍不是 live trading
3. 新建真正的后排 Python sidecar：
   - `scripts/run_rank154_crypto_stat_arb_paper_sidecar_refresh.py`
   - 它只做两件事：
     1) 调 `scripts/run_rank154_crypto_stat_arb_paper_runner.py --refresh --scheduler-attached --scheduler-unit momentum-rank154-paper-sidecar-refresh.timer`
     2) 刷新首页 `bash scripts/publish_homepage_index.sh`
4. 新建并安装 systemd unit：
   - workspace 源文件：
     - `ops/systemd/momentum-rank154-paper-sidecar-refresh.service`
     - `ops/systemd/momentum-rank154-paper-sidecar-refresh.timer`
   - 已安装到：
     - `/etc/systemd/system/momentum-rank154-paper-sidecar-refresh.service`
     - `/etc/systemd/system/momentum-rank154-paper-sidecar-refresh.timer`
5. 执行安装与启动：
   - `systemctl daemon-reload`
   - `systemctl enable --now momentum-rank154-paper-sidecar-refresh.timer`
   - `systemctl start momentum-rank154-paper-sidecar-refresh.service`
6. 验证结果：
   - timer 已 `active (waiting)`
   - service 手动启动成功，返回 `status=0/SUCCESS`
   - sidecar 最近一轮已写出 `rank154_sidecar_refresh_last_run.json`
   - `rank154_paper_state.json` 已写成：
     - `scheduler_attached = true`
     - `scheduler_unit = momentum-rank154-paper-sidecar-refresh.timer`
     - `queue_state = handoff_complete_refresh_only_scheduler_attached`
     - `handoff_complete = true`
7. 回写 `docs/BOT2_BOT3_STATE.md`：
   - `Paper launch queue.current_target = none`
   - 154 改成 `sidecar offload complete`
   - 当前前排默认只剩 `fresh intake + background guard`

## 一句话结果
`Rank 154 / Crypto-Stat-Arb` 已从 bot2/bot3 的研究循环里正式移出：refresh-only sidecar 已有真实 Python 入口与 systemd timer 托管，runtime state 已明确写成 `handoff complete`，后续默认不再占 bot2/bot3 前排轮次。

## 边界
- 这不是 live trading，也不是 broker/exchange execution；它仍然只是 refresh-only paper sidecar。
- 当前 sidecar 依然遵守 frozen-seed honesty boundary：不能把历史 seed 伪装成新 live rows。
- 若未来 sidecar 报出单一决定性失败，才允许把 154 重新带回 bot2/bot3 前排；否则默认继续留在独立后排托管。
