# 2026-03-17 08:27 UTC · Rank 28 cross-market intraday leader-laggard TSMOM source intake

## 为什么这轮选这个
- 先按 desk 顶板检查了当前席位：`EMA / Paper Seat` 仍是 `waiting_not_due`，全 desk 没有新的 `due-now / overdue` lane。
- 继续比较 active Scout 候选的边际价值后，当前可执行结论很清楚：
  - `Rank 17 / Rank 2` 没有新的真实 `append/review need`；
  - `Rank 26 / Rank 27` 已完成当前允许预算并压回 `park / evidence pool`；
  - `Rank 5 / Rank 6` 仍分别卡在 `prediction-market` 与 `equity proxy` 外部数据依赖，不够“便宜诚实”。
- 因此这轮不再空谈“该找新线了”，而是把新的 fresh intake 正式落成下一轮可直接执行的队列项。

## 本轮主点 + 紧邻子点
- 主点：为新的 `paper-based 5m / 15m crypto` 候选完成 1 个正式 `source intake`，把它推进到 `admit_to_clean_replication_queue`。
- 紧邻子点：把这条线写回 `docs/TODO.md` 顶板，并提供 reader-facing 页面，避免结果只留在日志/邮件里。

## 这轮选中的 fresh intake
**`Rank 28 = cross-market intraday leader-laggard TSMOM`**
- 来源：Xu, Li, Singh, Li (2023/2024) 的 *Cross-Market Intraday Time-Series Momentum*，并参考 Li, Sakkas, Urquhart (2022) 的 intraday TSMOM 论文口径。
- 当前更适合拿主资源的原因：
  1. 仍是 `paper-based`；
  2. 贴近 `5m / 15m crypto`；
  3. 下一轮可以直接复用现有 `BTC/ETH/SOL 120d 15m` cache；
  4. 不需要额外 prediction-market / equity proxy 外部数据。

## 先过两条轻量诚实守门
1. **trade on / trade off 可以清楚写出来**
   - `trade on`：在 `pseudo-session`（优先 `funding_8h` / `UTC session`）前段，若某资产先出现显著 `lead move`，且 cross-market leader basket 给出同向领先，则在下一段固定 follow-through 窗口按该方向入场。
   - `trade off`：前段领先不显著、没有 leader、或 follow-through 窗口已过。
2. **不偷接未来 / 不偷接外部依赖**
   - `leader` 只允许用当前已完成的前段收益与 peer 排名定义；
   - 当前默认只在 `BTC/ETH/SOL` crypto basket 内做 lead-lag；
   - 若 clean replication 发现必须接 prediction-market / equity proxy 数据，这条线就应立即降为“不够便宜诚实”。

## 做了什么
### 1) 新增 source intake artifact
- `reports/artifacts/literature/scout_rank28_crossmarket_intraday_tsmom_source_intake_card.csv`

卡片里冻结了：
- 为什么这轮选它而不是 `Rank 5 / Rank 6`
- 最小 `trade on / trade off`
- 当前 honesty gate
- 下一轮唯一允许动作 = `1 个最小 clean replication`

### 2) 更新 fresh shortlist
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

把 `Rank 28` 正式挂到 shortlist，避免下一轮又回到口头比较。

### 3) 把 verdict 写回 authoritative board
- `docs/TODO.md`

这轮把两层口径都补齐了：
- 候选阶段表里新增 `Rank 28`
- `Next 3 bot3 runs` 里明确：当前默认 fresh intake 已切到 `Rank 28`，而不是继续围着已 park 的 `Rank 27` 或依赖更重的 `Rank 5 / Rank 6`

### 4) 补一个 reader-facing 页面
- `reports/site/reading/scout_rank28_cross_market_intraday_tsmom_source_intake.html`

页面用人话说明：
- 为什么这条线现在比 `Rank 5 / Rank 6` 更值钱
- 它和已 park 的 `Rank 14` 有什么不同
- 下一轮唯一允许动作是什么

## 当前 hard verdict
**这轮 hard verdict 不是 `park / paper candidate / narrow paper pilot`，而是：`Rank 28 -> admit_to_clean_replication_queue`。**

原因：
- 当前这条线还没进 clean replication，不能偷给 `P0~P4` 结论；
- 但它已经满足本轮最关键的问题：
  - 比 `Rank 5 / Rank 6` 更便宜诚实；
  - 比继续重开 `Rank 27` 更符合当前 fresh-intake 指令；
  - 下一轮能直接拿现有 cache 做 first verdict。

## 最小验证
已执行：
1. 用 Python `csv.reader` 检查：
   - `scout_seat_fast_cycle_crypto_shortlist_v1.csv`
   - `scout_rank28_crossmarket_intraday_tsmom_source_intake_card.csv`
2. 确认 `docs/TODO.md` 已包含 `Rank 28` 相关 authoritative 文字
3. 确认 reader-facing HTML 页面存在

## reader-facing 落点
- `reports/site/reading/scout_rank28_cross_market_intraday_tsmom_source_intake.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` / `Next 3 bot3 runs`

## 风险 / 边界
- 这轮只做 `source intake`，没有提前偷跑 clean replication。
- `Rank 28` 目前只是“下一轮值得花 1 刀预算”的 fresh candidate，还不是 `P2`。
- 如果下一轮发现必须依赖额外外部数据，这条线应立即按“不够便宜诚实”处理，不要拖成新的长期研究坑。

## 对下一轮的含义
1. 若届时 `EMA` 仍是 `waiting_not_due`，且 `Rank 17 / Rank 2` 仍没有新的真实 append need，默认优先做 `Rank 28` 的 **1 个最小 clean replication**。
2. clean replication 应只冻结：
   - `funding_8h / UTC session` 两档 pseudo-session
   - leader ranking 口径
   - `BTC/ETH/SOL 120d 15m` cache
3. first verdict 最先看：`post_cost_return / positive_asset_ratio / false_follow_ratio / mean_trades`

## Git
- 工作区仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
