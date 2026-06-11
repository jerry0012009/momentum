# 2026-03-18 17:40 UTC — Rank 61 source intake：把 lower-TF volume-delta polarity 正式推进到 guard-passed

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍无新的 `due-now / overdue` lane：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最近一次托管刷新为 `2026-03-18T17:25:06Z`，`new_closed_trades_appended=0`，当前不构成比 fresh Scout intake 更高优先级的 `P3` 抢占理由。
- `Rank 60` 已在 `17:22 UTC` 完成最小 clean replication 并给出 **`park / evidence pool`** hard verdict，因此当前合法主动作应切到新的 fresh paper / repo based 5m / 15m crypto source。
- 按当前 active Scout 边际价值比较：`Rank 61 / lower-TF volume-delta polarity mismatch veto` `>` `continuation fail-fast overlay` `>` `pullback-quality / CQI` `>` `Rank 35b` `>` `Rank 16b` `>` `tiny-live plumbing`。原因不是 Rank 61 已验证，而是它比外部 aggTrades flow veto 更便宜、更容易部署，而且更像三条主线共用的 shared veto / confirmation layer。

## 开轮检查（repo / 最近 runs / 脏文件 / 当前席位）
- repo 状态：工作区仍有大量与本轮无关的既有脏文件和未跟踪产物，本轮不做混提 commit。
- 最近 optimization runs：
  - `2026-03-18_1722_rank60-clean-replication-park.md`
  - `2026-03-18_1656_rank60-source-intake.md`
  - `2026-03-18_1640_rank59-time-stability-park.md`
- 当前席位：
  - `Paper Seat = EMA`：`running paper / waiting_not_due`
  - `Live Seat`：暂空
  - `Scout Seat`：本轮主资源位 = `Rank 61` source intake + 两条轻量诚实守门

## 本轮主点
完成 **`Rank 61 / lower-TF volume-delta polarity mismatch veto`** 的 source intake + 两条轻量诚实守门，并直接给出 queue-facing hard verdict。

## 做了什么改动
### 新增 / 刷新 artifact
- `reports/artifacts/literature/scout_rank61_volume_delta_polarity_veto_source_intake_card.csv`

### reader-facing 落点
- `reports/site/reading/repo_scout/rank61_volume_delta_polarity_veto_source_intake.html`

### authoritative writeback
- 更新了 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把 `Rank 61` 的 source intake 结果冻结为 `guard-passed / admit_to_clean_replication_queue`，并把下一手默认主资源位收紧成：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 61 minimal clean replication`
  - `Run 3 = 若 Rank 61 仍不足以升格，再比较 continuation fail-fast overlay > pullback-quality / CQI > Rank 35b > Rank 16b > tiny-live plumbing`

## 两条轻量诚实守门 / 证据
### 1) trade on / trade off 已能冻结
- `trade on`：base setup 继续负责方向与价位；lower-TF volume-delta polarity 只回答 pre-entry 最后 `3~5` 分钟里是否存在真实同向跟随。第一轮冻结成：long setup 需要 lower-TF delta proxy 为正、short setup 需要为负；若 polarity 与 setup 方向相反，则只允许 `veto / 降级`，不能单独开仓。
- `trade off`：若 lower-TF delta proxy 与信号方向相反或接近中性，这层只负责 veto / 延后，不能被包装成独立 alpha；也不允许把 README 里的夸张回测数字、Supertrend / RSI / ALMA / order block 等 kitchen-sink 组件一起偷渡进第一轮。

### 2) 为什么没有被 honesty gate 直接判死刑
- 当前只复刻 repo 里最便宜且最诚实的那一块：用 `request.security_lower_tf(...)` 对应的 lower-TF OHLCV proxy，先试 `1m`（必要时再比较 `30s`）。
- delta 定义固定成：`sub close > open` 记正量、`sub close < open` 记负量；可选进阶版才是 candle-pressure 近似。
- 所有判断都必须只用 setup 触发前最后 `3~5` 分钟子周期窗口，并统一冻结到 **`next-bar open + no-overlap`**；当前未见一眼可判死刑的 `lookahead / repaint / leakage`。
- 当前真正需要防的不是未来函数，而是**把入场后 volume 倒灌回 pre-entry delta**，或把更复杂的 lower-TF stack 一股脑偷渡进第一轮。

## 当前硬结论
- **`Rank 61 / lower-TF volume-delta polarity mismatch veto = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 **1 次最小 clean replication** 预算，但现在还只是 shared participation veto 候选，不是新 alpha，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 61` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d 15m` 主图 + `1m` 子周期 proxy；
  - 只比较四臂：`base`、`same_direction_gate`、`opposite_delta_veto`、`strong_same_direction_only`；
  - 统一冻结到 `setup 前最后 3~5 分钟子周期窗口 + next-bar open + no-overlap + hold 8 bars`；
  - 先看 `post_cost_return@6bps`、`trade_count_retention`、`4-bar false-break / false-hold rate`、`positive_asset_ratio`。
- 若改善主要来自极端减样本、只在单一 archetype 上成立，或 `1m` proxy 本身无边，就快速压回 `park / evidence pool`。

## 最小验证
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank61_volume_delta_polarity_veto_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank61_volume_delta_polarity_veto_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 17:40 UTC` 补充。

## Commit hash
- 未提交。
- 原因：工作区有大量与本轮无关的既有脏文件和未跟踪产物，当前不适合做安全 selective commit。
