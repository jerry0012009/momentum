# 2026-03-17 05:31 UTC · Rank 24 trend regime filter source intake

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD`：
  - `Paper Seat = EMA waiting_not_due`，当前不能在 waiting-window 空转；
  - `Live Seat = 暂空`；
  - 因此本轮合法落点仍是 `Run 2 / Scout Seat`。
- 先比较当前 active Scout 候选的边际价值：
  - `Rank 17`：刚补过 `P3 weekly review queue`，当前没有新的真实 `append/review need`；
  - `Rank 2`：已有 `narrow paper refresh history`，当前也没有新的真实 `append/review need`；
  - `Rank 7`：唯一允许的 cheap honesty recheck 已完成，并已压回 `park / evidence pool`；
  - `Rank 21 / 22 / 23`：都刚完成 `clean replication + Light Stability Pack`，并已压回 `park / evidence pool`。
- 因此本轮最诚实的主点，不是继续磨旧 P3 wiring，而是回到 board 允许的 **fresh intake**：只开 1 条新的 repo-based `15m crypto` 候选，并把下一轮要做的 clean replication 路径冻结清楚。

## 本轮主点 + 紧邻子点
- 主点：把新的 `Rank 24 trend regime filter / trend-strength-over-noise gate` 冻结成可执行的 source-intake 卡。
- 紧邻子点：把结论同步写回 `docs/TODO.md` 顶板 / shortlist / reader-facing 页面，确保下一轮可以直接接 `clean replication`，而不是再次花时间选题。

## 为什么是 Rank 24，而不是别的 fresh intake
- `ema_donchian_breakout` / 其他 breakout 导向模块会把当前 desk 叙事又拉回 breakout，而当前默认明确“不再强调 breakout”。
- `trend_regime_filter` 更贴当前 desk 想回答的问题：
  - 不是再找一个更花哨的 trigger；
  - 而是测试 **环境过滤** 能不能给当前 `15m crypto baseline` 留下更诚实的存活 pocket。
- 它还是 repo-based / 规则简短 / 不需要新数据源，适合当前 `source intake -> clean replication -> Light Stability Pack` 的快筛节奏。

## 本轮做了什么
### 1) 新增 deployable artifact：Rank 24 source intake card
新增：
- `reports/artifacts/literature/scout_rank24_trend_regime_filter_source_intake_card.csv`

冻结规则：
- 来源：`src/momentum/signals/trend_regime_filter.py` + `docs/SIGNALS_TREND_REGIME_FILTER.md`
- 标的：`BTC / ETH / SOL`
- 周期：`15m`
- `trade on`：保留现有 `multi_tf_momentum` 方向层；仅当近 `N` 根的 `trend_strength` 超过最小阈值，且 `trend_strength / noise_level` 形成足够高的 `regime_score` 时允许入场
- `trade off`：基线方向缺失；或 `trend_strength` / `regime_score` 任一门未过

### 2) 完成 Stage A honesty gate
当前只做最小诚实守门，不偷跑 clean replication：
- 只用 rolling past returns 与当前已完成 bar 计算 `trend_strength / noise_level / regime_score`
- 默认下一根 bar 执行
- 没有明显 `lookahead / repaint / data leakage`

因此它当前只通过了：
- 规则能清楚写成 `trade on / trade off`
- 通过便宜的因果 / honesty gate

但**还没有**：
- clean replication 结果
- Light Stability Pack
- `paper candidate` 级别证据

### 3) 同步 board / shortlist / reader-facing 落点
更新：
- `docs/TODO.md`
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
- `reports/site/factors/scout_trend_regime_filter_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`

同步内容：
- 顶部 authoritative override 更新为 `2026-03-17 05:31 UTC`
- `Next 3 bot3 runs` 新增 `2q` 条目
- shortlist 新增 `Rank 24`
- 新建 reader-facing 页面，明确当前只到 `fresh intake accepted / pending Stage A + clean replication`

## 当前 hard verdict
**`Rank 24 trend regime filter / trend-strength-over-noise gate` 当前状态 = `fresh intake accepted / pending Stage A + clean replication`。**

这不是 `paper candidate`，更不是 `narrow paper pilot`。
当前最诚实的下一步只有一个：
- 若后续 `EMA` 仍是 `waiting_not_due`，且 `Rank 17 / Rank 2` 仍无真实 `P3 append/review need`，就直接在固定 `BTC/ETH/SOL 120d 15m` cache 上做最小 `clean replication`；
- 比较 `baseline_mtf / trend_regime_default / stricter_trend_threshold / stricter_regime_score`；
- 然后再补 `Light Stability Pack`，最后只给 `park / paper candidate / narrow paper pilot` 三选一。

## 最小验证
已执行并通过：
1. `grep -n "05:31 UTC\|Rank 24 trend regime filter\|2q\." docs/TODO.md`
2. `tail -3 reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
3. `grep -n "fresh intake accepted\|trend_strength\|Stage A honesty gate" reports/site/factors/scout_trend_regime_filter_15m/report.html`
4. `grep -n "Latest Scout intake\|scout_trend_regime_filter_15m" reports/site/reading/trendline_alpha_scout/report.html`

## 风险 / 边界
- 本轮没有重跑回测、没有引入新下载、没有给出任何 alpha 正负结论。
- 这轮只是把下一条候选压成“下一轮可以直接 clean replicate”的状态。
- 若后续 clean replication 一跑就显示成本后归零、交易数过薄或稳定性很差，应按 desk 规则直接压回 `park`。

## 网页可见落点
- `reports/site/factors/scout_trend_regime_filter_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## Git / 提交
- 本轮未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
