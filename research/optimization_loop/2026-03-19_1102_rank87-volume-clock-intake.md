# Rank 87：volume-clock + CS spread interaction gate source intake

## 为什么这次选这个
- 先按 `Run 1 / EMA due-check only` 实际执行了 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`；结果仍是 `waiting_not_due`，当前没有新的 `due-now / overdue` lane，不能伪造 paper refresh。
- 上一轮已经把 `Rank 86 / SignalPro penetration×ATR admission` 因时间稳定性不过关压回 `park / evidence_pool`，所以这轮必须按顶板回到 `fresh paper/repo intake`。
- 我重新比较了当前还能拿的 fresh Scout：`volume-clock + CS spread interaction gate`、两条更 breakout-centric 的 fresh digest backlog（`outside-close -> back-inside-close` failure verdict、`close-range compression` asymmetry），以及 `Rank 82 / 80 / 81 evidence_pool`。当前更高边际价值的是前者：它更贴 `EMA waiting_not_due` 时的 shared continuation/liquidity gate 主线，而且默认不需要重新放大 breakout 叙事。

## 这轮做了什么改动
1. 新冻结 queue-facing fresh source 为 **`Rank 87 / volume-clock + CS spread interaction gate`**。
2. 完成这条线的 `source intake + 两条轻量诚实守门`，并把当前最诚实结论写成：**`guard-passed / admit_to_clean_replication_queue`**。
3. 生成 deployable artifact：
   - `reports/artifacts/literature/scout_rank87_volume_clock_cs_spread_source_intake_card.csv`
4. 生成 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank87_volume_clock_cs_spread_source_intake.html`
5. 最小更新 desk board：把 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 改写为：
   - `Run 1 = EMA due-check only`
   - `Run 2 = Rank 87 minimal clean replication`
   - `Run 3 = 若 Rank 87 hard-fail，则回到 fresh paper/repo intake；只有 fresh intake 也 exhausted 才回退 backlog / plumbing`

## 这条线当前的两条轻量诚实守门
### trade on
- 只把它当 `shared allow/deny gate`，不是独立 alpha。
- 用 `5m -> 30m` 聚合找最近一天成交量最大的 `volume-clock anchor`。
- 只有当 `signed impulse + CS spread state` 同时落在支持区间时，才放行后续 `15m continuation / retest follow-up`。

### trade off
- 如果 signal 与最近 anchor 不邻近、impulse 弱、或 spread 状态不支持，就不得强行放行。
- 这条 overlay 不能单独开仓，也不能把固定 funding 时钟伪装成真实成交时钟。

### lookahead / repaint / leakage
- desk 迁移必须只用 `signal` 当根及之前可得的 `5m/30m OHLCV` 构造 anchor、impulse 与 `CS spread z-score`。
- 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap`。
- 不得用未来哪个 30m 窗口最终成为全日最大成交窗口，也不得用后续 continuation 结果回填 anchor 标签。

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：全 desk 仍无 `due-now / overdue` lane；最近 due 为美股约 `8.9h`、crypto 约 `12.9h`、A 股约 `19.9h`。
  - 结论：本轮合法主动作确实应落在 `Scout Seat`，而不是 paper continuity。
- 文献 / digest 证据：
  - `research/quant_digests/2026-03-19_0956_volume-clock-cs-spread-interaction-gate.md`
  - 其中本地快检已说明：真实最大成交 `30m` 窗口与固定 funding/整点锚点高度不重合，支持“先测 volume-clock，而不是继续固定 first-30m/funding 时钟”的 intake 方向。

## 风险 / 边界
- 这轮只做了 `source intake + honesty gates`，**还没有**做 desk 口径的 clean replication；不能把它写成已验证 alpha。
- `CS spread` 是廉价流动性代理，不等于真实盘口成本；下一轮 replication 若 improvement 只是 early pocket 或 trade retention 掉得太狠，应直接压回 `park`。
- 当前 repo 存在大量与本轮无关的脏文件，本轮不适合安全 commit。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 87` **1 次最小 clean replication**：
  - 固定 `BTC/ETH/SOL 5m -> 15m` 现有 cache；
  - 比 `baseline / fixed-clock gate / volume-clock+spread gate` 三臂；
  - 统一 `next-bar open + no-overlap`；
  - 直接做 `keep_P1 / promote_to_P2 / park` 判断。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件与未跟踪文件；本轮只做最小局部交付，不安全混提。
