# 2026-03-21 00:27 UTC — Rank 135 fresh intake（retest tolerance stop decoupling gate）

## 本轮先做的桌面检查（按 TRADING DESK BOARD）
- `git status --short`：repo 仍有与本轮无关的脏文件，继续 **不混提**。
- 先按 `Run 1 = EMA due-check first` 复核当前 desk 状态：上一轮刚完成 `require-due fast-precheck`，顶板最新状态仍是 `EMA / running paper pilot / waiting_not_due`，当前没有 `due-now / overdue` lane。
- 因此本轮合法主位继续落在 `Scout Seat`；且 `Run 2` 明确要求认领 `Rank 135 / fresh intake slot`，不得回头继续磨旧 `P1`。

## 3.5 Active Scout 边际价值比较（本轮只取 1 条）
- `Rank 127 / signal→confirm ATR delta phase gate`：已有最小检查，属于 `budget-used` 旧 P1，继续追加预算的边际价值偏低。
- `Rank 125 / range location veto gate`：已 `keep_P1 / budget used`，本轮不如 fresh intake 更能改变桌面排序。
- `Rank 112 / basis dislocation short veto`、`Rank 111 / abnormal-return event clock`：都偏旧 evidence pool，不该继续占主位。
- `Rank 122 / 2 / 17 / 29 / 32b`：属于 `P3 hosted continuity`，当前没有真实 status-changing event，不抢主位。
- `tiny-live plumbing`：按顶板只能排在 `Scout Seat` 后面。

**结论：fresh intake 仍是本轮最高边际价值动作。**

## 本轮主点：认领 `Rank 135 / retest tolerance stop decoupling gate`
来源：
- `research/quant_digests/INDEX.md`
- 对应 digest：`2026-03-20_1429_retest-tolerance-stop-decoupling-gate.md`

### 为什么挑它
这条线比继续磨旧 P1 更值钱，因为它直接回答一个当前 desk 很常见、也很容易自欺的问题：
- 回踩容差到底是在描述“价格几何是否还算守住结构”，
- 还是偷偷把风险预算 / 止损宽度伪装成信号过滤？

若不先把这两者拆开，breakout-short / Fib / EMA 三条线都会把 execution 容错误读成 admission 优势。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on**：冻结既有 `breakout_short / fib_retest_long / ema_psar continuation` 的 entry 家族，只把 `retest tolerance` 明确定义成几何容差（例如：相对前高前低、zone depth、ATR-normalized distance），并与 `stopDistancePct` / 风险预算脱钩。
- **trade off**：它不是新主策略，不负责决定方向；若结果表明 uplift 主要来自更宽风险预算、只在单一 setup / 单一点值偶然有效，直接 `park`。

### 2) no lookahead / repaint / data leakage
- 容差只能使用 **signal 当根及之前** 已完成的 swing / zone / ATR 信息；
- 执行口径固定为 `next-bar open + no-overlap`；
- 禁止用未来最大不利波动、最终是否打止损、后验回踩深度去倒算“合理容差”。

**本轮 hard verdict：`guard-passed / admit_to_clean_replication_queue`。**

## 新增产物
1. `reports/artifacts/literature/scout_rank135_retest_tolerance_stop_decoupling_source_intake_card.csv`
2. `reports/site/reading/repo_scout/rank135_retest_tolerance_stop_decoupling_source_intake.html`

## 对 desk board 的最小 write-back
- `Scout Seat 当前主点`：从“待认领 fresh intake slot”切到 **`Rank 135 / retest tolerance stop decoupling gate`**。
- `Active Scout 排序`：将 `Rank 135` 置顶为 `P1 / source intake done / guard-passed`。
- `Next 3 runs`：
  - `Run 2` 改为：若 EMA 仍 `waiting_not_due`，执行 `Rank 135` 的 1 次最小 clean replication；
  - `Run 3` 改为：若 `Rank 135` replication 不诚实/guard-fail，则回下一条 fresh intake；若 replication 通过，再决定 `keep_P1 / promote_P2 / park`。
- `最近关键 evidence`：补入本轮 `Rank 135 fresh intake + honesty gate` 结论。

## 下一轮最小动作建议
- 若 `EMA` 仍非 due-now：给 `Rank 135` **仅 1 次最小 clean replication**（BTC/ETH/SOL、15m、next-bar open、no-overlap、6/10/15bps），直接输出 `keep_P1 / promote_P2 / park`。

## commit
- 未提交（当前工作区存在大量与本轮无关脏文件，按规则不混提）。
