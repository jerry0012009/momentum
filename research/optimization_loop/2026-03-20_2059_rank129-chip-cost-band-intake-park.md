# 2026-03-20 20:59 UTC — Rank 129 / chip cost-band reclaim + winner-ratio re-expansion / source intake hard-park

## 本轮先核对的东西
- repo：`master`；`git status --short` 仍显示大量与本轮无关的脏文件，**不混提**。
- 最近 optimization loop：最新已留痕是 `2026-03-20 20:47 UTC / Rank 128 minimal clean replication -> park`。
- `Paper Seat`：本轮再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果继续如实返回 **`EMA = waiting_not_due`**；当前无 `due-now / overdue` lane，最靠前的仍是 `Crypto 1d+1wk -> due_soon / 约 3.0 小时后到点`。
- hosted paper lanes：这轮没有新的 `P3 status-changing event` 插队，因此仍不回头占 continuity 预算。

## 为什么这轮合法主动作是 fresh intake，而不是回头磨旧 P1
按 `docs/TODO.md` 顶板 `2026-03-20 20:47 UTC` 最新排班：
1. `Run 1 = EMA due-check first`
2. 若 `EMA` 仍 `waiting_not_due`，`Run 2 = 优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条新的 fresh intake`
3. 只有当新 source 真正 `guard-pass` 时，才允许在后续轮次给 `1` 次最小 clean replication

因此本轮只认领 **1 个 fresh intake 主点**，不并开第二条候选。

## 本轮如何比较 active Scout 的边际价值
### 旧 active Scout
- `Rank 127 / ATR delta`：`P1 weak candidate / budget used`
- `Rank 125 / range location veto`：`P1 keep_P1 / budget used`
- `Rank 112 / 111`：`P1 evidence_pool / budget used`
- `Rank 128`：刚在上轮最小 clean replication 后已压回 `P0 / park`

这些都不适合在 `EMA = waiting_not_due` 时继续吃主资源位。

### 本轮 fresh options 的取舍
这轮优先在 **fresh source** 里比较：
- `2026-03-20 20:38 quant digest / chip cost-band reclaim + winner-ratio re-expansion`
- 其他更 breakout-follow-up 的新鲜旁支（如 intrahour skew band）

最终优先认领这条 `chip cost-band reclaim`，原因不是它更强，而是：
1. **它更贴近当前 desk 双轨主线**：直接服务 `Fib retest / EMA continuation`，比 breakout-follow-up 更符合当前默认不再强调 breakout 的要求；
2. **它可以用现有证据低成本收口**：已有 digest + clean replication 复盘足够支持 source intake 的诚实硬 verdict，不必再开新下载或重跑重型实验；
3. **它能更快告诉交易台“别浪费预算在这里”**：比把旧 P1 再磨一轮，更有边际价值。

## 本轮实际执行
### 1. 真实先做 EMA due-check
实际运行：

`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果继续如实返回：当前仍无 `due-now / overdue` lane，因此不能伪 refresh，也不能空转。

### 2. 认领新的顺序 Rank
按 `7.10.1`，任何新的 Scout 方向只要进入 queue-facing / reader-facing 层，都必须先拿下一个顺序 `Rank` 编号。

因此本轮把这条 holder-structure 方向登记为：
- **`Rank 129 / chip cost-band reclaim + winner-ratio re-expansion`**

### 3. 写回本轮 deployable artifact
- artifact：`reports/artifacts/literature/scout_rank129_chip_cost_band_reclaim_source_intake_card.csv`
- reader-facing：`reports/site/reading/repo_scout/rank129_chip_cost_band_reclaim_source_intake.html`

## 两条轻量诚实守门的结论
### 1. trade on / trade off
当前最诚实的缩写只能是：
- **trade on**：若一定要保留，它只配当 `Fib retest / EMA continuation` 的窄口径 holder-structure evidence——先有 baseline setup，再问价格是否 reclaim `cost_p50 / avg_cost band`，且 `winner_ratio` 是否重新扩张；
- **trade off**：它不是 `15m shared retest gate`，不是 breakout-short 默认组件，也不是新的独立 alpha。

### 2. no lookahead / repaint / leakage
当前并没有发现明确 `lookahead / repaint`；
但真正的诚实问题在于：**主 pocket 对 `shares / turnover anchor` 的建模假设太敏感**。

现有 digest / clean replication 已足以说明：
- 在宽松 `synthetic shares` 假设下，它看起来像有 edge；
- 一旦 anchor 收紧，收益和交易数会明显翻脸；
- 再叠加 `winner_ratio` 也没有把鲁棒性救回来。

因此，这轮不应把它继续送进 clean-replication queue。

## 硬结论
**`Rank 129 / chip cost-band reclaim + winner-ratio re-expansion = park / evidence pool / do_not_admit_to_clean_replication_queue`**。

翻成人话：
- “价格重新站回估算成本带、浮盈筹码重新占优”这个想法不是完全没启发；
- 但当前 15m 公开数据口径下，它太容易变成 `synthetic shares / turnover` 的参数故事；
- 所以更诚实的处理，不是再补一轮最小 clean replication，也不是磨更多说明页，
- 而是直接把它压回 `P0 / park`，把下一轮 Scout 主资源位继续留给 **fresh intake**。

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：当前主资源位应继续写成
  - `fresh intake（优先 quant digests / RECENT_PAPER_SEEDS / validated shortlist）`
  - `Rank 127 = P1 weak candidate / budget used`
  - `Rank 125 = P1 keep_P1 / budget used`
  - `Rank 112 / 111 = P1 evidence_pool / budget used`
  - `Rank 128 / Rank 129 = P0 park / evidence pool`
  - `P3 hosted continuity sidecar only`

## 下一手建议
若下一轮 `EMA` 仍 `waiting_not_due`：
1. 继续先做 `EMA due-check first`；
2. 若仍无 `due-now / overdue` lane，则继续按 fresh intake reserve 认领 **1 条新的 5m / 15m crypto paper / repo source**；
3. 只有新 source 真 `guard-pass` 时，才给 `1` 次最小 clean replication；
4. 不建议回头继续磨 `Rank 129` 的 `admission wording / operator packet / closeout docs`。

## Commit hash
未提交。

原因：工作区存在大量与本轮无关的脏文件，当前不适合做安全 selective commit。
