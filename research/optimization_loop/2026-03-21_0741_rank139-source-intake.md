# 2026-03-21 07:41 UTC — Rank 139 / CUSUM event-bar confirm-veto gate / source intake + 两条轻量诚实守门

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，所以本轮主动作切去 **Scout Seat**。比较当前 active Scout 的边际价值后，正式认领 **`Rank 139 / CUSUM event-bar confirm-veto gate`**，并完成 `trade on / trade off` 与 `no leakage` 两条轻量诚实守门，硬结论是：**guard-passed / admit_to_clean_replication_queue**。

## 先检查了什么
- `git status --short`
  - repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- 最近 runs
  - 最近两轮 Scout 主资源已给过 `Rank 138 -> minimal clean replication -> park` 与 `Rank 127 -> cheap time-stability -> park`。
  - 当前顶板已把 active Scout 顺序收紧到 `Rank 139 > Rank 125 > Rank 112 > Rank 111`。
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：当前仍没有 `due-now / overdue` lane。
  - 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 `16.3h` 后到点。
  - 说明：本轮继续合法从 `Paper Seat` 切去 `Scout Seat`，不能在等待窗口里空转。

## 为什么这轮认领 Rank 139，而不是回旧 P1 / P3 continuity
当前 authoritative 顶板写的是：
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，执行 Rank 139 的 source intake + 两条轻量诚实守门`
3. `Run 3 = 若 Rank 139 guard-pass，只给它 1 次最小 clean replication`

结合 active Scout 边际价值：
- `Rank 125 / 112 / 111`
  - 都已是 `P1 / weak candidate or evidence_pool / budget used`；按 desk 规则，本轮默认不该继续磨旧 `P1`。
- `Rank 2 / 17 / 29 / 32b / 122`
  - 都属于 `P3 continuity / sidecar only`；而且 `EMA = waiting_not_due` 时，默认预算要先给 fresh Scout，而不是继续消费 hosted continuity。
- `fixed partial → R/ATR partial`
  - 只有在 `Run 3` 且 `Rank 139 hard-fail / exhausted` 时才允许接棒；本轮还不到它。

**结论：** 本轮最该认领的是 `Rank 139` 这条 fresh paper/docs source，而不是回头打磨旧候选。

## 本轮主点：Rank 139 source intake
来源：
- digest：`research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`
- paper：`Algorithmic crypto trading using information-driven bars, triple barrier labeling and deep learning`（Financial Innovation, 2025）
- 公开数据：Binance public market data

翻成人话：
这条线值钱，不是因为我们要把整套策略改写成 event bars，而是因为它把确认层从“固定 15m close 有没有站稳”改写成了一个更诚实的问题：
- **entry 之后，市场有没有真的沿目标方向走出 first event？**
- 如果 first event 先走反向，很多 breakout-short / Fib / EMA continuation 本来就该被更早 veto；
- 如果长时间都等不到事件，也更像 weak follow-up / no continuation，而不是继续假装信号还活着。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on：**
  - 每个现有 `15m entry` 保持不变；
  - 只在 entry 触发后，观察未来固定 latency budget（首轮先用 `45 分钟`）内的 `1m directional CUSUM`；
  - 统一收敛成 3 类：`same_dir_first / opp_dir_first / no_event_timeout`；
  - 它的角色只允许是 **shared confirm / veto / weak-follow-up timeout layer**，不允许直接替代 breakout-short / Fib / EMA-PSAR 的原始入场。
- **trade off：**
  - 它不是把 desk 变成 tick-level 主 alpha；
  - 不是无限等待式 confirmation；
  - 不是用 future path 反推出“这一笔本来该归哪类”；
  - 如果 clean replication 证明 uplift 只来自单一 pocket、trade retention 过度塌缩、或 first-event 分类并没有稳定帮助，就直接 `park`。

### 2) no lookahead / repaint / leakage
- CUSUM 只允许使用 entry 之后按时间顺序到达的 **已完成 1m close**；
- 阈值必须事前冻结，首轮只允许很小网格：`{0.4, 0.6, 0.8} × ATR15m%`；
- 每笔只记录 **first qualifying event**，不允许等看完整条未来 path 后再挑最顺眼的事件；
- baseline 执行口径继续冻结为 `next-bar open + no-overlap`；
- 不允许用 future outcome、完整持仓结果、或回看后的最优 timeout 去回填 gate 标签。

**本轮 hard verdict：`guard-passed / admit_to_clean_replication_queue`。**

## 本轮新增产物
### artifacts
- `reports/artifacts/literature/scout_rank139_cusum_event_bar_confirm_veto_source_intake_card.csv`

### reader-facing
- `reports/site/reading/repo_scout/rank139_cusum_event_bar_confirm_veto_source_intake.html`

### desk write-back
- `docs/TODO.md`
  - `Scout Seat 当前主点` 改成 `guard-passed / minimal clean replication next`
  - `Active Scout` 中将 `Rank 139` 从 `source intake reserve` 推进到 `guard-passed / admit_to_clean_replication_queue`
  - `Run 2` 改为 `最小 clean replication`
  - `最近关键 evidence` 补入本轮 due-check 与 guard-pass 结论

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：当前最诚实的下一手不是再写概念页，而是给 `Rank 139` **1 次最小 clean replication**，直接判它是否值得继续保留为 shared event-confirm 候选。

## 下一轮最小动作建议
若下一轮 `EMA` 仍非 due-now：
- 只给 `Rank 139` **1 次最小 clean replication**；
- 固定复用 `BTC/ETH/SOL 15m` baseline 与 `1m` 本地数据；
- 只做 entry 后 `45 分钟` 的 first-event 分类；
- 主看：`same_dir_first rate`、`opp_dir_first rate`、`no_event_timeout share`、`post_cost_expectancy`、`trade_count_retention`、`failure_rate`
- 若 retention / 成本后表现明显塌缩，就直接 `park`，不要继续磨 wording。

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前无 `due-now / overdue` lane；最近 due 为 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `16.3h` 后到点。

## 风险 / 边界
- 这轮还只是 intake，不是假装已经完成 replication；
- 当前证据只够支持“它值得拿 1 次 clean replication 预算”，不够支持“它已经是 desk 默认 shared confirm layer”；
- 论文主实验是 tick data + 深度学习，我们这里只借 sampling / first-event confirmation 思路；
- 若后续 replication 发现它本质只是重新包装 waiting / timeout，不应硬保留。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部 intake card、reader-facing 页面、顶板 write-back 与 run log，不适合混提。
