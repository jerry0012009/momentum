# Rank 70 / fast-entry slow-exit handoff spine minimal clean replication（park）

## 轮次定位
- 时间：2026-03-18 23:12 UTC
- 席位：`Scout Seat`
- 本轮主点：`Run 2 / Rank 70 minimal clean replication`
- 紧邻子点：`TODO 顶板顺序刷新`

## 开始前检查
- `Run 1 / EMA due-check`：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍无新的 `due-now / overdue` lane；最早仍是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`。
- `P3 continuity`：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，没有新的 status-changing event。
- 顶板 `Next 3` 已明确：当前合法主动作不是继续磨 `P3 continuity`，而是给 `Rank 70` 这条 fresh repo exit spine 1 次最小 clean replication。
- git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮只新增 `Rank 70` clean replication 对应脚本、artifact、reader-facing 页面、TODO 写回与本轮日志，不做混提。

## 这轮实际做了什么
### 1. 新增最小 clean replication 脚本
- 脚本：`scripts/build_rank70_fast_entry_slow_exit_clean_replication.py`
- 复用本地 `BTC/ETH/SOL 120d 15m` cache，沿用 desk 近期 scout clean replication 骨架。
- entry 完全冻结，只改 exit：
  - `baseline_exit`：固定持有 `8` 根 bar；
  - `all_fast_fail`：沿用 `EMA9 / session VWAP / 0.75*ATR` 的 fail-fast；
  - `all_slow_trailing`：切到 `Donchian 20 / 3.5*ATR chandelier` 的慢退出；
  - `handoff_exit`：前 `3` 根 bar 保留 fail-fast，若存活满 `3` 根或达到 `1 ATR` 顺向 MFE，则 handoff 到 slow trailing；最长持有 `24` 根 bar。
- 统一执行口径：`signal 当根及之前数据 + next-bar open + no-overlap`。

### 2. 产出 reader-facing / artifact
- 因子页：`reports/site/factors/scout_rank70_fast_entry_slow_exit_handoff_15m/report.html`
- 阅读页：`reports/site/reading/repo_scout/rank70_fast_entry_slow_exit_handoff_clean_replication.html`
- 关键 artifact：
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/setup_compare.csv`
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/cost_stability.csv`
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/trade_log.csv`

### 3. 写回 queue-facing 顺序
- `docs/TODO.md` 顶板已写入 `2026-03-18 23:12 UTC` 最新块。
- `Rank 70` 这轮已消耗完允许的那次 minimal clean replication，因此顺序重置为：
  - `Run 1 = EMA due-check only`
  - `Run 2 = fresh source 比较 realized-vol mid-band cost-survival gate > PSAR close-confirmed follow-up gate`
  - `Run 3 = 若新的 fresh source guard-passed，则给它 1 次最小 clean replication；否则才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 结果（hard verdict）
**`Rank 70 / fast-entry slow-exit handoff spine = park / evidence pool`**

## 为什么是这个 verdict
这轮最直白的结果不是“handoff 稍微有点意思”，而是：**它没有形成足够统一、足够便宜的 shared exit overlay。**

### setup-level 结果（6bps/side）
- `ema_psar_long`
  - `base≈-5.55%`
  - `fast≈-4.19%`
  - `slow≈-5.06%`
  - `handoff≈-1.96%`
- `fib_retest_long`
  - `base≈+0.88%`
  - `fast≈-2.23%`
  - `slow≈+5.91%`
  - `handoff≈-1.66%`
- `breakout_short`
  - `base≈-2.58%`
  - `fast≈-4.57%`
  - `slow≈-4.38%`
  - `handoff≈-4.71%`

### 更诚实的读法
1. `handoff` 只在 `ema_psar_long` 上比 baseline 好一些，但仍然是负收益；
2. `fib_retest_long` 真正拉开收益的是 `all_slow_trailing`，不是两段式 `handoff`；
3. `breakout_short` 上，快 exit / 慢 exit / handoff 三臂都比 baseline 更差；
4. 主变体 `handoff_exit` 的跨 setup / 跨资产代价也不轻：
   - `mean_total_return≈-2.78% @ 6bps`
   - `10bps≈-4.48%`
   - `15bps≈-6.56%`
   - `mean_giveback_after_handoff≈78.60%`
   - `mean_handoff_rate≈60.83%`

换成人话：**这条线的问题不是“没延长持仓”，而是延长了之后，利润大多又吐回去了。**

## 对 desk 的影响
- `Rank 70` 现在更像 exit 管理层的工程灵感，不像当前值得继续占默认 fast-lane 的候选。
- 因为这轮已经把它允许的最小 clean replication 用掉了，下一轮更诚实的动作不是继续磨它，而是回到 fresh source：
  - `realized-vol mid-band cost-survival gate`
  - `PSAR close-confirmed follow-up gate`
- `Paper Seat / EMA` 仍按 `waiting_not_due` 处理；本轮没有任何理由回头挤占 `P3 continuity`。

## 最小验证
- 已实际运行：`python3 scripts/build_rank70_fast_entry_slow_exit_clean_replication.py`
- 脚本成功退出并打印：
  - `generated_at=2026-03-18 23:12 UTC`
  - `verdict=park / evidence pool`
- 已核对以下文件存在并写入：
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/setup_compare.csv`
  - `reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/cost_stability.csv`
  - `reports/site/factors/scout_rank70_fast_entry_slow_exit_handoff_15m/report.html`
  - `reports/site/reading/repo_scout/rank70_fast_entry_slow_exit_handoff_clean_replication.html`
- 已确认 `docs/TODO.md` 顶板新增 `2026-03-18 23:12 UTC` 写回块。

## 风险 / 边界
- 这轮只回答 exit-only 对照；没有给 slow trailing / handoff 做额外参数优化，也不应因为 `fib_retest_long + all_slow_trailing` 一条局部好看，就偷渡成 desk 共享 overlay。
- 当前 `session VWAP` 仍是 UTC 日内近似；但本轮 handoff 的主要问题不在这，而在 **跨 setup 不统一 + giveback 太高**。
- 除非未来某条具体 setup 明确需要单独重开“slow exit overlay”题目，否则 `Rank 70` 当前不该继续占默认 scout 预算。

## 提交
- 未提交（工作区有大量与本轮无关的脏文件，避免混提）。
