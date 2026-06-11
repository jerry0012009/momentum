# 2026-03-17 08:41 UTC · Rank 28 cross-market intraday leader-laggard TSMOM clean replication

## 为什么这轮选这个
- 先按 desk 顶板检查当前席位：`EMA / Paper Seat` 仍是 `waiting_not_due`，最新 `due guardrail` 没有新的 `due-now / overdue` lane。
- 继续比较 active Scout 候选的边际价值后，当前最便宜诚实的动作仍是 `Rank 28`：
  - `Rank 17 / Rank 2` 没有新的真实 `append/review need`；
  - `Rank 26 / Rank 27` 已完成当前默认预算并压回 `park / evidence pool`；
  - `Rank 5 / Rank 6` 仍卡在 prediction-market / equity proxy 外部数据依赖。
- 因此本轮按顶板要求，只认领 1 个主点：把 `Rank 28` 从 `admit_to_clean_replication_queue` 推到真实 first verdict，而不是继续停留在 source intake 口头排队。

## 本轮主点
- 主点：对 `Rank 28 = cross-market intraday leader-laggard TSMOM` 做 **1 个最小 clean replication + Light Stability Pack**。
- 没有额外打开第二条候选，也没有把这轮扩成新的大框架。

## 冻结后的 clean-room 规则
- 样本固定：`BTC / ETH / SOL`，沿用现有 `Binance 120d 15m` cache。
- session 只测两档：`utc_day` 与 `funding_8h`。
- `trade on`：同一 session 前 `2` 根 15m bar 内，先找出绝对 `lead move` 超过该资产本地分位阈值、且幅度最大的 `leader`；若其余资产中存在同方向但更弱的 `laggard`，则在同一 session 最后 `2` 根 15m bar 按 leader 方向跟随入场。
- `trade off`：没有合格 `leader / laggard`，或前段方向不一致，就不交易。
- 诚实边界：不接 prediction-market / equity proxy 外部 feed；不追新 bar；不把最小 clean replication 偷扩成重型研究。

## 做了什么
### 1) 新增 Rank 28 clean replication 脚本
- `scripts/build_rank28_crossmarket_intraday_clean_replication.py`

脚本完成了：
- `utc_day / funding_8h` 两档 pseudo-session 切分；
- `q50 / q60 / q70` 三档 leader 阈值对照；
- `6 / 10 / 15 / 20 bps per side` 成本梯度；
- `Light Stability Pack` 四项输出：
  - 时间稳定性
  - 参数稳定性
  - 跨标的稳定性
  - 成本 / 交易数稳定性
- reader-facing 报告页输出。

### 2) 生成新的 artifact + 网页落点
生成目录：
- `reports/artifacts/scout_rank28_crossmarket_intraday_tsmom_15m/`

关键文件：
- `variant_aggregate.csv`
- `asset_summary.csv`
- `leader_laggard_events.csv`
- `leader_laggard_trades.csv`
- `time_stability_drycheck.csv`
- `parameter_stability_drycheck.csv`
- `cross_asset_stability_drycheck.csv`
- `cost_trade_stability_drycheck.csv`
- `trial_meta.csv`

网页落点：
- `reports/site/factors/scout_rank28_crossmarket_intraday_tsmom_15m/report.html`

### 3) 把 hard verdict 写回 authoritative board
- `docs/TODO.md`

本轮已把 `Rank 28` 从 `admit_to_clean_replication_queue` 改成 **`park / evidence pool`**，并同步刷新 `Next 3 bot3 runs`：
- 不再默认重开 `Rank 28`；
- 在 `EMA waiting_not_due` 且现有 `P3/P2` 无真实动作时，恢复成重新比较 active Scout / fresh intake 边际价值，再挑下一条新的 `paper / repo based 5m / 15m crypto` 候选。

## 验证 / 证据
已执行：
```bash
python3 /root/clawd/jerry/momentum/scripts/build_rank28_crossmarket_intraday_clean_replication.py
```

脚本成功输出新 artifact 与网页报告，核心证据如下：

### 1) primary variant（`funding_8h_q60 @ 6bps/side`）直接为负
- `mean_total_return ≈ -16.58%`
- `positive_asset_ratio = 0/3`
- `mean_false_follow_ratio ≈ 66.42%`
- `mean_trades ≈ 124`

这说明问题不是“没有样本”，而是**有样本但跟随方向本身不赚钱**。

### 2) 更不差的邻近版本也没救活
- `utc_day_q70 @ 6bps/side` 只是相对最不差，但仍约 `-5.28%`
- 仍然是 `0/3` 资产为正

因此这不是单一 primary 设定挑错，而是**整条最小 lead-lag 口径都没形成可用 pocket**。

### 3) Light Stability Pack 四项全部硬 fail
- 时间稳定性：`0/3 positive buckets`
- 参数稳定性：`funding_8h_q50~q70` 邻域 `0/3 positive`
- 跨标的稳定性：`0/3 assets positive`
- 成本 / 交易数稳定性：`6/10/15/20bps` 下 `0/4 positive cost levels`

这轮最关键的结论很干净：**它不是“差一点点就能 paper candidate”，而是当前就该诚实 park。**

## 当前 hard verdict
**`Rank 28 -> park / evidence pool`**

一句话结论：
- 当前这条 cross-market intraday lead-lag 规则，在现有 `BTC/ETH/SOL 120d 15m` 样本里没有形成能通过最小快筛门槛的 alpha。 

证据支持：
- primary variant 与全部邻近阈值都在成本后转负，且时间 / 参数 / 跨标的 / 成本四项稳定性同时失败。

## 风险 / 边界
- 这轮只验证了 **不依赖外部数据** 的最小 crypto-only lead-lag clean-room 版本；它并不证明论文原始跨市场设定“永远无效”。
- 但对当前 desk 来说，这已经足够回答更重要的问题：**这条线值不值得继续占默认 Scout 预算？答案是不值得。**
- 若后续要重开，必须有 bot2 明确点名，或出现新的 genuinely verdict-changing 证据；不能继续在同一 clean replication 上续命。

## 对下一轮的含义
1. `EMA / Paper Seat` 若仍是 `waiting_not_due`，默认继续先看 `Scout Seat`。
2. 但 `Rank 28` 已 park，后续默认不再重复重做。
3. 下一轮应恢复到：重新比较当前 active Scout / fresh intake 的边际价值，再挑 1 条新的 `paper / repo based 5m / 15m crypto` 候选做最小 `source intake` 或 `clean replication`。

## Git
- 当前 repo 里仍有大量与本轮无关的脏文件 / 未跟踪文件。
- 为避免混提，本轮不做 commit。
