# Rank 183 / 186 / 187 — paper runner wiring complete

时间：2026-03-27 13:28 UTC

## 结论
本轮不是继续写 `queued_handoff_ready` 文案，而是把 `Rank 183 / 186 / 187` 真正推进到 **已接线完成**：

- dedicated python runner 已写好
- systemd `service + timer` 已安装并 `enable --now`
- 三条 service 已完成一次 **首跑验证成功**
- runtime artifacts / state / HTML status 已落地

因此，这三条对象不应再继续停留在 `Paper launch queue` 里被表述成“等待下游接线”；**写 runner、挂调度、验证首跑** 现在明确属于 `P3 handoff / launch wiring` 的组成部分。

---

## 1) Rank 183 / cbeth-eth-rolling-fair-basis-mr
### runner / schedule
- runner: `scripts/run_rank183_cbeth_eth_paper_runner.py`
- service: `momentum-rank183-paper-refresh.service`
- timer: `momentum-rank183-paper-refresh.timer`
- cadence: `15m`

### current artifacts
- status: `reports/artifacts/paper_rank183_cbeth_eth_basis/rank183_status.csv`
- state: `reports/artifacts/paper_rank183_cbeth_eth_basis/rank183_state.json`
- ledger: `reports/artifacts/paper_rank183_cbeth_eth_basis/rank183_closed_trades.csv`
- latest pair series: `reports/artifacts/paper_rank183_cbeth_eth_basis/rank183_latest_pair_series.csv`
- html: `reports/site/paper/rank183_cbeth_eth_basis.html`

### first-run verification
- service 首跑：成功
- 当前状态：`connected_runner_live`
- 当前读法：`CBETH Coinbase spot + ETHUSDT perp hedge` 的 `15m` rolling fair-basis MR 已进入 autonomous paper refresh

---

## 2) Rank 186 / CME expiry postfix short BTC
### runner / schedule
- runner: `scripts/run_rank186_cme_expiry_paper_runner.py`
- service: `momentum-rank186-paper-refresh.service`
- timer: `momentum-rank186-paper-refresh.timer`
- cadence: `1m`

### current artifacts
- status: `reports/artifacts/paper_rank186_cme_expiry/rank186_status.csv`
- state: `reports/artifacts/paper_rank186_cme_expiry/rank186_state.json`
- ledger: `reports/artifacts/paper_rank186_cme_expiry/rank186_closed_trades.csv`
- events: `reports/artifacts/paper_rank186_cme_expiry/rank186_events.csv`
- html: `reports/site/paper/rank186_cme_expiry.html`

### first-run verification
- service 首跑：成功
- 当前状态：`connected_runner_live`
- 当前读法：`last Friday 16:00 Europe/London`、`+5m short entry`、`+120m exit` 的月频事件 runner 已接管后续自动刷新

---

## 3) Rank 187 / BTCUSDT 15m late-session path-shape swing
### runner / schedule
- runner: `scripts/run_rank187_path_shape_paper_runner.py`
- service: `momentum-rank187-paper-refresh.service`
- timer: `momentum-rank187-paper-refresh.timer`
- cadence: `15m`

### current artifacts
- status: `reports/artifacts/paper_rank187_path_shape/rank187_status.csv`
- state: `reports/artifacts/paper_rank187_path_shape/rank187_state.json`
- ledger: `reports/artifacts/paper_rank187_path_shape/rank187_closed_trades.csv`
- signal snapshot: `reports/artifacts/paper_rank187_path_shape/rank187_signal_snapshot.csv`
- html: `reports/site/paper/rank187_path_shape.html`

### first-run verification
- service 首跑：成功
- 当前状态：`connected_runner_live`
- 历史基线：先用已批准的 `h32_k3` research ledger 作为 seed，再由 live runner 负责 forward updates
- 当前读法：`60d lookback / first 8h path / k=3 / late-session long swing` 已进入 autonomous paper refresh

---

## 4) 对 bot2 / bot3 policy 的直接影响
从现在开始，`P3 handoff` 的最小完成定义不再只是：
- 有 handoff packet
- 有 queue-side 文档

而必须至少包含：
1. runner script 已写出
2. scheduler（`service/timer/cron`）已安装启用
3. 至少一次首跑验证成功
4. runtime state 明确写成 `connected_runner_live` 或同等语义

也就是说，**“写 runner 并运行”就是接线任务的一部分**，不能再把它当成 queue 外部、默认会自动发生的事。

## 一句话结果
`Rank 183 / 186 / 187` 已从 `P3 queue-side handoff ready` 正式推进为 **paper runner wiring complete / connected_runner_live**；后续 bot2 不应再把它们排成“继续等待下游接线”，而应把它们视为已完成接线并退出默认前排。