# 2026-03-23 14:10 UTC · Rank 150 / EMA family time-stability check

- 路径判断：`Scout`
- 认领动作：沿着顶板 `Next 3 bot3 runs / Run 1 = Rank 150 的单 family honest gate` 继续做 **1 个最小 verdict-changing 邻近子检查**
- 本轮只推进：
  1. **主点**：检查 `Rank 150 / DFA Hurst persistence gate` 在上一轮 `EMA / PSAR` family uplift 里，是否具备最基本的**时间稳定性**；
  2. **紧邻子点**：把结果写成可见 artifact，并补到现有 reader-facing 页面。

## 1) 为什么这轮还继续 Rank 150
- `Paper / 待开启自动运行 = empty`，所以不走 `Paper launch`。
- 当前没有 `running paper` 的 stale / error / refresh drift 证据，所以不走 `Interrupt`。
- 上一轮 `2026-03-23_1358_rank150-ema-family-honest-gate.md` 已经完成了顶板要求的 **单 family honest gate**，但结论仍是 `keep_P1 but stronger`。
- 这时最有杠杆、最便宜、最能改变判断的一刀，不是继续调 Hurst 阈值，而是回答一个更关键的问题：
  - **这个 uplift 是不是只靠最近一个窗口撑起来？**

## 2) 本轮实际动作
基于上一轮已有产物：
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/trades.csv`

新增：
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/monthly_stability_primary_cost.csv`
- `reports/artifacts/scout_rank150_ema_family_honest_gate_15m/monthly_uplift_vs_baseline_primary_cost.csv`

并把时间稳定性结果补进：
- `reports/site/factors/scout_rank150_ema_family_honest_gate_15m/report.html`
- `reports/site/reading/repo_scout/rank150_ema_family_honest_gate.html`

## 3) 固定口径
- family：`EMA / PSAR raw alpha continuation`
- gate：`Rank 150 / DFA window=192`
- 对比臂：
  - `baseline`
  - `high_only`
- 执行冻结：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 成本：`6bps / side`
- 时间切片：按 `entry_ts` 月份拆分

## 4) 主结果
### baseline（月均 net / trade）
- `2025-11`: `-0.273%`
- `2025-12`: `-0.548%`
- `2026-01`: `-0.167%`
- `2026-02`: `+0.023%`
- `2026-03`: `+0.431%`

### high_only（月均 net / trade）
- `2025-11`: `-0.522%`
- `2025-12`: `-0.110%`
- `2026-01`: `-0.015%`
- `2026-02`: `-0.076%`
- `2026-03`: `+1.499%`

### uplift（high_only - baseline）
- `2025-11`: `-0.249%`（更差）
- `2025-12`: `+0.438%`
- `2026-01`: `+0.153%`
- `2026-02`: `-0.098%`（略差）
- `2026-03`: `+1.068%`

## 5) 这轮最值钱的结论
1. **上一轮看到的 pooled 转正，时间上并不平。**
   `high_only` 并没有在每个月都稳定赚钱；真正显著的正收益，主要来自 `2026-03` 这一段。
2. **它仍然有信息，但更像“缩小亏损 + 清理左尾”，不是成熟 allow gate。**
   - `2025-12 / 2026-01`：`high_only` 比 baseline 好，说明 persistence gate 在坏月份能减伤；
   - 但它没能把这些月份直接稳定拉到正值；
   - `2026-03` 的强 uplift 很亮眼，但还不够说明“跨月可复用”。
3. **这会把 Rank 150 的 desk 定位从“keep_P1 but stronger”再收紧一格。**
   更准确的口径应是：
   - `P1 / keep_P1 / family-level evidence real`
   - 但 **time stability 未过**，离 `P2` 还差一刀。

## 6) 对下一轮的影响
如果继续给 `Rank 150` 一轮，默认优先级应改成：
1. **第二 family 复核**（优先 `breakout-short` 或 `fib retest` 二选一），看 uplift 是否能跨 family 复现；
2. 而不是继续在 `EMA / PSAR` 单 family 内做参数打磨。

因为现在最关键的问题已经从“有没有 family uplift”变成了：
> **这个 gate 是 family-specific 偶然窗口，还是更普适的 desk-family 守门层？**

## 7) 简短 scorecard
- `usefulness`: `2/3` — 明确回答了 pooled 转正是否可相信，减少误升层风险
- `time_stability`: `1/3` — 主要靠 2026-03，跨月不平
- `cross_asset_stability`: `1/3` — 仍主要由 SOL 贡献，BTC/ETH 没被真正救活
- `cost_trade_stability`: `1/3` — 之前已知高成本下会快速收缩，本轮未改善
- `deployability`: `1/3` — 还不是可升 `P2/P3` 的 desk-ready gate
- `recommended_action`: `keep_P1`
- `why_now`: `上一轮已拿到单 family uplift，这时最值得做的是最便宜的时间稳定性验真`
- `main_weakness`: `uplift 主要集中在最近一个月，跨月稳定性不够`

## 8) 本轮交付
- optimization log：本文
- artifact：两张按月稳定性 CSV
- reader-facing 落点：已补到 Rank 150 现有页面
