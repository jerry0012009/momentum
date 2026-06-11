# Rank 79 / one-regime-per-session clean replication park
- 时间：2026-03-19 05:13 UTC
- 席位：Scout Seat
- 主点：按 `TRADING DESK BOARD` 的 `Next 3`，在 `EMA = waiting_not_due` 前提下完成 `Rank 79 / one-regime-per-session shared allocation overlay` 的唯一那手最小 clean replication
- 紧邻子点：把 `Next 3 bot3 runs` 最小写回到 `docs/TODO.md`

## 0. 开场检查
- `git status --short` 仍显示 repo 内外大量与本轮无关的脏文件；本轮只新增 `Rank 79` clean replication 相关脚本 / artifact / reader-facing 页面 / 日志，不混提其他脏改。
- 最新 desk 指挥：`docs/TODO.md` 顶部 `TRADING DESK BOARD` 明确要求先做 `Run 1 / EMA due-check only`，若仍 `waiting_not_due`，则切到 `Run 2 / Rank 79 minimal clean replication`。
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 复核结果：全 desk 仍无 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T04:33:36Z`：`new_closed_trades_appended=0`，说明当前没有新的 `P3 status-changing event` 需要抢主资源。

## 1. 为什么这轮继续做 Rank 79，而不是回头磨 P3 continuity
当前 `Paper Seat = EMA / running paper / waiting_not_due` 没变，`P3` sidecar 也没有新的真实异常；因此这轮仍必须遵守：
`EMA waiting_not_due -> Scout Seat -> tiny-live plumbing`。

上轮 `04:42 UTC` 已把 `Rank 79` 推到 `guard-passed / admit_to_clean_replication_queue`，所以这轮最诚实的动作不是再开新 source，也不是回头做 `Rank 17 / 2 / 29 / 32b` 的 continuity，而是把 `Rank 79` 那唯一一次会改 verdict 的最小 clean replication 跑完。

## 2. 本轮做了什么
### 2.1 新增最小 clean replication 脚本
新增：
- `scripts/build_rank79_one_regime_per_session_clean_replication.py`

口径冻结为：
- 资产：`BTC / ETH / SOL`
- 样本：复用本地 `120d 15m` cache
- 基础 lane：`ema_psar_long` / `fib_retest_long` / `breakout_short`
- 对照四臂：
  - `baseline_all_lanes`
  - `continuation_only`
  - `retest_only`
  - `one_regime_per_session`
- 执行统一：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`

### 2.2 session overlay 的最小诚实实现
`one_regime_per_session` 不再靠事后解释整段 session，而是只允许用每段 session 前 `4` 根 `15m` 的：
- opening range
- VWAP
- ATR14
- 首小时净变动 / close location

先把 session 粗分成：
- `continuation`
- `retest`
- `unclear`

然后再做分配：
- `continuation`：只放 `breakout_short + EMA/PSAR continuation`
- `retest`：只放 `Fib retest_hold`
- `unclear`：不放行这条 overlay（相当于 `no-trade`）

这保证了本轮检查仍是 budget-allocation overlay，而不是偷渡成一个新的独立 alpha。

### 2.3 产出 reader-facing / artifact 落点
新增：
- `reports/artifacts/scout_rank79_one_regime_per_session_15m/overall_summary.csv`
- `reports/artifacts/scout_rank79_one_regime_per_session_15m/compare_vs_baseline.csv`
- `reports/artifacts/scout_rank79_one_regime_per_session_15m/window_summary.csv`
- `reports/artifacts/scout_rank79_one_regime_per_session_15m/session_meta_summary.csv`
- `reports/artifacts/scout_rank79_one_regime_per_session_15m/summary.json`
- `reports/site/factors/scout_rank79_one_regime_per_session_15m/report.html`
- `reports/site/reading/repo_scout/rank79_one_regime_per_session_clean_replication.html`

并把 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 做了最小写回：
- `Rank 79 = park / evidence pool`
- 默认主资源从 `Rank 79` 切回 `first-30m impulse quality gate > RS+/RS- asymmetry gate > 其他 fresh source`

## 3. 验证 / 证据
执行：
- `python3 scripts/build_rank79_one_regime_per_session_clean_replication.py`

`6bps/side` 下 overall 对照：
- `baseline_all_lanes`：`trade_count=177`，`total≈-16.70%`，`positive_session_ratio≈40.68%`，`same_session_conflict_rate≈11.30%`
- `one_regime_per_session`：`trade_count=56`，`retention≈31.64%`，`total≈-6.72%`，`positive_session_ratio≈37.50%`，`same_session_conflict_rate≈5.36%`
- 相对 baseline：
  - `delta_total_vs_baseline≈+9.99%`
  - `delta_conflict_vs_baseline≈-5.94%`
  - 但 `retention≈31.64%`

按资产看：
- `BTC`：`total≈-2.03%`，比 baseline 更差
- `ETH`：`total≈-8.96%`，虽然比 baseline 少亏，但仍明显为负
- `SOL`：`total≈+4.27%`，接近 baseline 但不构成跨资产一致改善

## 4. 本轮 hard verdict
**`Rank 79 / one-regime-per-session shared allocation overlay = park / evidence pool`**

核心原因不是它完全没信息，而是：
1. 它确实降低了同 session 冲突率；
2. 也把总亏损从 baseline 的 `-16.70%` 收敛到 `-6.72%`；
3. 但代价是只剩 `31.64%` 的 trade retention；
4. 且只有 `1/3` 资产（SOL）还能保住正向，跨资产改善不够统一；
5. 因此当前更像“会大幅砍样本的 allocation 证据”，还不够诚实到升 `P1/P2`。

换句话说：它证明了“同场冲突值得关注”，但还没证明“one-regime-per-session 这个实现”值得继续占默认 fast lane。

## 5. 风险 / 边界
- 本轮仍是最小 clean replication，不是最终 desk execution policy。
- session 分类阈值是为了做首轮诚实检查而冻结的简化口径，不等于已经找到稳定 regime classifier。
- 本轮没有追求更复杂的 5m execution layer，也没有做更重的跨窗口稳健性扩展；因为在当前 retention 已明显下滑的前提下，先给 `park` 更诚实。

## 6. 下一步建议
按当前 `TODO` 顶板，下一轮若 `EMA` 仍 `waiting_not_due`：
1. 先回到 **`first-30m impulse quality gate`**
2. 再比较 **`RS+/RS- asymmetry gate`**
3. 再看 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 的其他 fresh source
4. 只有 fresh source 这一层也 exhausted，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`

## 7. Commit hash
- 未提交。
- 原因：当前工作区存在大量与本轮无关的历史脏文件；本轮虽然文件组相对集中，但在未先做更细的 selective audit 前，不适合安全提交。
