# Rank 342 / same-chain cross-DEX price-gap close — P3 launch wiring connected_runner_live

- 时间：2026-04-06 00:12–00:16 UTC
- 对象：`Rank 342 / same-chain cross-DEX price-gap close`
- 本轮角色：bot3 只执行当前 `cycle_plan` 第 1 个 pending 小点，把 queue-side 的 `P3` 对象真正接成 `connected_runner_live`

## 结论
**正式结果：`Rank 342` 已完成最小 `launch wiring`，运行态应从 `Paper launch queue` 头对象改写为 `connected_runner_live`。**

这轮没有回到开放式研究，而是把已经通过 `P2 exit decision` 的对象收窄成最小可运行 paper lane：

- scope：`Base-first / Arbitrum-second / same-chain only / exclude Ethereum high-gas lane`
- dedicated runner：`scripts/run_rank342_samechain_crossdex_paper_runner.py`
- scheduler：
  - `ops/systemd/momentum-rank342-paper-refresh.service`
  - `ops/systemd/momentum-rank342-paper-refresh.timer`
- 首跑验证：成功，`ExecMainStatus=0`

## 这次接线具体落了什么

### 1) dedicated runner 已落库
本轮新增 runner：

- `scripts/run_rank342_samechain_crossdex_paper_runner.py`

它做的事很明确：
- 从 DexScreener `token-pairs v1` 拉取当前低 gas same-chain lane 快照；
- 只覆盖已批准的 launch scope：
  - `Base WETH/USDC (floor >= $1m)`
  - `Base cbBTC/WETH (floor >= $1m)`
  - `Arbitrum WETH/USDC (floor >= $250k)`
  - `Arbitrum WBTC/WETH (floor >= $250k)`
- 按冻结 paper friction spec 计算 `gross_bps` 与 `net_bps($5k/$10k/$25k)`：
  - 非 gas friction floor：`13 bps`
  - gas：`Base $0.2`、`Arbitrum $0.5`
- 写出 runner-grade artifacts：
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_lane_snapshots.csv`
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_current_lane_frame.csv`
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_status.csv`
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_state.json`
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_last_run_summary.json`
  - `reports/artifacts/paper_rank342_samechain_crossdex/rank342_frozen_launch_spec.json`
  - `reports/site/paper/rank342_samechain_crossdex.html`

这一步是诚实的接线，不是假装已经有逐笔 fill replay 或 MEV-perfect execution；它只是把 `P3` 对象正式接成一个定时记录 low-gas pocket 的 paper lane。

### 2) scheduler 已安装并启用
本轮新增 repo 内 unit 文件：

- `ops/systemd/momentum-rank342-paper-refresh.service`
- `ops/systemd/momentum-rank342-paper-refresh.timer`

并已安装到 `/etc/systemd/system/` 后执行：

- `systemctl daemon-reload`
- `systemctl enable --now momentum-rank342-paper-refresh.timer`
- `systemctl start momentum-rank342-paper-refresh.service`

验证结果：

- service：`Result=success`
- service：`ExecMainStatus=0`
- timer：`ActiveState=active`
- timer：`SubState=waiting`
- next fire：`Mon 2026-04-06 00:17:20 UTC`

### 3) first verified run 已产出 runtime artifact
首跑后关键 runtime 快照：

- `runner_mode`: `live_snapshot_low_gas_samechain_lane`
- `active_lane_count`: `4`
- `positive_lane_count`: `4`
- `best_lane_label`: `base WETH/USDC floor>=1000000`
- `best_lane_best_net_bps`: `+5.80 bps`
- `best_lane_gross_bps`: `18.88 bps`
- `best_lane_buy_dex`: `pancakeswap`
- `best_lane_sell_dex`: `uniswap`
- `best_lane_captured_at_utc`: `2026-04-06T00:15:38Z`
- `wiring_status`: `connected_runner_live`

对应 artifact：
- 状态：`reports/artifacts/paper_rank342_samechain_crossdex/rank342_status.csv`
- state：`reports/artifacts/paper_rank342_samechain_crossdex/rank342_state.json`
- 当前 lane frame：`reports/artifacts/paper_rank342_samechain_crossdex/rank342_current_lane_frame.csv`
- 页面：`reports/site/paper/rank342_samechain_crossdex.html`

## 为什么这一步改变了系统认知
在这轮之前，`Rank 342` 只是已经完成 `P2 -> P3` 判断、但还没真正接线的 queue 头对象。

在这轮之后，它已经变成一个：
- 有专用 runner；
- 有启用中的 systemd timer；
- 有首跑 runtime artifact；
- 并且 scope 被明确收窄在 `Base-first / Arbitrum-second / same-chain only` 的 live paper lane。

因此最重要的 runtime 变化不是“又多了一份 handoff 文档”，而是：

> `Rank 342` 不应再继续占据 `Paper launch queue.current_target` 的待接线位置，而应正式并入 `connected_runner_live`。

## 本轮改变系统认知的一句话
`Rank 342 / same-chain cross-DEX price-gap close` 已完成最小 `launch wiring`：低 gas same-chain paper lane 的专用 runner、已启用 scheduler 与首跑验证都已落地，运行态正式写回 `connected_runner_live`，不再只是 `Paper launch queue` 里的待接线对象。

## Ops note
- 本轮属于真实推进（`P3 queue -> connected_runner_live`），应刷新首页并发送中文邮件摘要。
- 后续如果继续跟进 `Rank 342`，应围绕 runner 产出的 lane freshness / pocket persistence / close half-life 做运行态观察，而不是把它重新拖回 desk-side admission。
