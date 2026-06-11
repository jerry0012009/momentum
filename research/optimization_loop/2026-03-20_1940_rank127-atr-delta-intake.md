# 2026-03-20 19:40 UTC — Rank 127 / signal→confirm ATR delta phase gate / source intake + 两条轻量诚实守门

## 本轮先核对的东西
- repo：`master`；`git status --short` 仍显示大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：最新已留痕仍是 `17:18 UTC / Rank 126 clean replication -> park` 与 `16:36 UTC / Rank 125 cost-trade stability -> keep_P1 / budget used`。
- `Paper Seat`：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果仍是 **`EMA = waiting_not_due`**；当前无 `due-now / overdue` lane，最近 due 约为：美股 `~20 分钟`、Crypto `~4.3 小时`、创业板ETF `~59.3 小时`。
- hosted paper lanes：`manual_narrow_paper_last_run_summary.json` 本轮仍是 `new_closed_trades_appended=0`；当前 open hosted paper 头寸仍为 `Rank 17 / ETH-USD(long)`、`Rank 17 / SOL-USD(short)`、`Rank 29 / BTC-USD(short)`。这些都仍属于 `P3 continuity / sidecar`，不是新 seat。

## 为什么本轮合法主动作是 Rank 127
按 `docs/TODO.md` 顶板 `2026-03-20 19:19 UTC` 最新排班：
1. `Run 1 = EMA due-check first`
2. 若 EMA 仍 `waiting_not_due`，`Run 2 = Rank 127 / signal→confirm ATR delta phase gate source intake + 两条轻量诚实守门`
3. 若 `Rank 127 guard-pass` 且 EMA 仍 `waiting_not_due`，`Run 3 = Rank 127 1 次最小 clean replication`

本轮满足第 2 条，因此只认领 **`Rank 127`** 这 1 个主点，不并开其他候选。

## 本轮实际执行
补齐了 `Rank 127` 的 queue-facing intake 产物：
- artifact：`reports/artifacts/literature/scout_rank127_signal_confirm_atr_delta_phase_source_intake_card.csv`
- reader-facing：`reports/site/reading/repo_scout/rank127_signal_confirm_atr_delta_phase_source_intake.html`
- 顶板同步：在 `docs/TODO.md` 追加 `2026-03-20 19:40 UTC` 最新执行补充，把 `Rank 127` 状态推进到 `guard-passed / admit_to_clean_replication_queue`，并把下一轮顺序收紧到 `Rank 127 minimal clean replication -> Rank 128 source intake reserve`。

## 两条轻量诚实守门的硬结论
### 1. trade on / trade off
当前最诚实的写法必须是 **setup-specific confirm/veto**，而不是 shared 单阈值：
- `breakout_short`：首轮只允许读成 **mid-phase re-arm**（避开 ATR delta 两端，优先保留中段 pocket）
- `fib_retest_long`：首轮只允许读成 **expanding confirm**
- `ema_psar_long`：首轮只允许读成 **expansion veto**

换句话说：
- base setup 继续负责方向与价位；
- `ATR delta` 只负责确认阶段的放行 / 否决 / 分层；
- 它不是 shared 同一把尺，也不是新的独立 alpha trigger。

### 2. no lookahead / repaint / leakage
当前可通过，但边界要写死：
- `ATR delta` 只能来自 **`signal 当根及之前、已完成 bar`** 的 trailing ATR 序列；
- desk clean replication 必须统一冻结到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
- 训练段只允许先冻结极小参数网格，再去测试段验证；
- 原 repo 的 XAUUSD 自报绩效不能直接搬成 crypto 15m desk 收益承诺，只能保留“两段 ATR 读法”这个可解释旁支。

## 硬结论
**`Rank 127 / signal→confirm ATR delta phase gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- `ATR delta` 不是没信息；
- 但当前最诚实的位置不是 shared overlay，而是 **setup-specific confirm / veto layer 候选**；
- 因此这条线值得拿那 1 次最小 clean replication 预算，但前提是直接比较 `baseline / shared_gate / setup_specific_gate`，而不是继续写概念页。

## 本轮产物
### artifacts
- `reports/artifacts/literature/scout_rank127_signal_confirm_atr_delta_phase_source_intake_card.csv`

### reader-facing
- `reports/site/reading/repo_scout/rank127_signal_confirm_atr_delta_phase_source_intake.html`

### desk write-back
- `docs/TODO.md`（新增 `2026-03-20 19:40 UTC` 顶板执行补充）

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：当前 active 顺序应收紧为
  - `Rank 127 = P1 weak candidate（guard-passed / minimal clean replication next）`
  - `Rank 128 = P1 fresh paper source reserve next`
  - `Rank 125 / 112 / 111 = P1 evidence_pool or budget_used`
  - `Rank 126 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113 = P0 park / evidence pool`
  - `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b = P3 hosted continuity / sidecar only`

## 下一手建议
若下一轮 `EMA` 仍 `waiting_not_due`，默认只允许给 `Rank 127` **1 次最小 clean replication**：
- 三臂：`baseline / shared_gate / setup_specific_gate`
- 口径：`BTC/ETH/SOL 120d 15m`、`signal 当根及之前数据 + next-bar open + no-overlap`
- 直接判：`keep_P1 / park / promote_to_P2`

若 `Rank 127` 当场 hard-fail / exhausted，则立刻切 `Rank 128 / MAX(5m) impulse confirmation tier` 的 source intake + 两条轻量诚实守门，而不是回头继续磨 `Rank 125 / 112 / 111`。
