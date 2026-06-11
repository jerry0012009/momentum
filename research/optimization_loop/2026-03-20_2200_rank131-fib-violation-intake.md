# Rank 131 / fib violation-cluster + 1-bar memory gate intake

## 为什么这次选这个
- 先按 desk 规则执行了 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回仍是 `waiting_not_due`，当前没有新的 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk`，约 `2.0` 小时后到点。
- 随后核对最近轮次与当前顶板，发现上一轮（`2026-03-20 21:41 UTC`）已经把 **`Rank 130`** 的那 `1` 次最小 clean replication 跑完，并且如实压回了 `P0 / park / evidence pool`；因此这轮不该重复认领旧 `Run 2`。
- 再比较当前 active Scout 的边际价值：
  - `Rank 127 / 125 / 112 / 111` 都是 `P1 / budget used / evidence_pool`，不该继续磨；
  - hosted `P3` (`122 / 2 / 17 / 29 / 32b`) 这轮没有新的 status-changing event；
  - 因而按 `Run 3 = 若 Rank 130 hard-fail / exhausted，则回 fresh intake reserve`，本轮最诚实动作就是认领 **1 条新的 paper-based 15m 候选**。
- 在本地 seed pool 里，最新 digest `2026-03-20_2142_fib-violation-cluster-memory-gate.md` 最贴近 desk 主线：它直接补 `Fib retest_hold` 缺的“最近击穿记忆”确认层，同时也能服务 `breakout-short` 的 follow-up failure 边界，所以本轮将其正式编成 **`Rank 131`**。

## 做了什么改动
1. 新建 queue-facing artifact：
   - `reports/artifacts/literature/scout_rank131_fib_violation_cluster_memory_source_intake_card.csv`
2. 新建 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank131_fib_violation_cluster_memory_source_intake.html`
3. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 把 `Scout Seat` 当前主点切到 `Rank 131`；
   - 把 `Active Scout` 排序改为 `Rank 131 > 127 > 125 > 112 > 111`；
   - 把 `Rank 130` 压回 `P0 / park / evidence pool`；
   - 把 `Next 3` 改成：`Run 1 = EMA due-check` → `Run 2 = Rank 131 minimal clean replication` → `Run 3 = honest uplift / park / fresh intake reserve`。

## 验证 / 证据
### 1) Paper Seat 仍是 waiting_not_due
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
关键信号：
- `当前没有 due-now / overdue lane`
- 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 2.0 小时后到点`
- `require-due` 已开启：当前应等待下一根 completed bar，而不是伪造 refresh

### 2) 为什么不是继续认领旧 P1 / P3
- `Rank 130`：上一轮已完成最小 clean replication，当前结论已是 `P0 / park`。
- `Rank 127 / 125 / 112 / 111`：顶板当前都写成 `P1 / budget used / evidence_pool`，这轮继续认领不符合“只给 1 次便宜诚实检查后偏向升格/park”的规则。
- `Rank 122 / 2 / 17 / 29 / 32b`：仍是 `P3 / hosted paper continuity / sidecar only`，且这轮没有新的 status-changing event，不该抢主资源位。

### 3) Rank 131 两条轻量诚实守门
当前最诚实的 `trade on / trade off`：
- **trade on**：它只配当 `Fib retest_hold` 的 `confirmation / veto gate`。先有 baseline 的 retest/hold 场景，再检查最近 `1~2` 根是否发生同向 `violation-cluster`；若没有，允许 hold verdict；若 `t-1` 或 `t-1,t-2` 已连续击穿，则当前 hold 应被 veto 或降级。
- **trade off**：它不是独立 alpha，不是新主触发器，也不是把 Fib 画得更玄。若没有既定 retest/hold 场景、若记忆项来自 signal 之后的数据、或若它把交易数砍到不可交易，就不得单独开仓。
- **honesty gate**：通过。memory 变量只能来自 `signal 当根及之前、已完成 bar` 的历史 violation 状态；阈值（如 `0.5/0.618 + epsilon*ATR`）必须在训练段或滚动过去窗口冻结；后续 clean replication 必须统一到 `next-bar open + no-overlap`，禁止用 future breach/path 倒灌。

## 当前硬结论
**`Rank 131 / fib violation-cluster + 1-bar memory gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
Fib 回踩确认不该继续写成“单次触位就确认”；更诚实的版本是——**如果前一两根已经连续破位，这次更像是假守住，不该再硬判成 hold**。

## 风险 / 边界
- 这轮只做了 `fresh intake + honesty gate`，还没有做 clean replication，更没有进入 `Light Stability Pack`。
- 上游证据来自日频论文机制迁移，不是现成的 15m crypto full replication；这轮保留的是“记忆型 veto 值得测”，不是“Fib 已被重新证明”。
- 若后续最小 clean replication 让 `trade_count_retention` 明显塌陷，应直接 `park` 或弱化 veto 强度，不要为了好看硬保留。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，则严格只给 `Rank 131` **1 次最小 clean replication**：
  - 对照：`baseline / t-1 veto / t-1,t-2 cluster veto`
  - 统一口径：`signal 当根及之前数据 + next-bar open + no-overlap`
  - 资产：`BTC/ETH/SOL perpetual 15m`（必要时辅以 `5m` 做执行层）
  - 主看：`post_cost_expectancy / false_hold_ratio@4bars / trade_count_retention / timeout_share`
- 若这 `1` 次 clean replication 不能形成 honest uplift，就直接 `park`，不要继续磨 admission wording。

## Commit hash
- 未提交。
- 原因：当前 repo 工作区仍有大量与本轮无关的脏文件，这轮不适合做安全 selective commit。
