# 2026-03-23 06:24 UTC · Rank 146 vs Rank 111 active compare

## 本轮执行顺序（按顶板）

### 1) 先读 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 未见顶板定义的真实 interrupt：
  - 无 `Paper / 正在自动运行` runner 的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
  - 无 tiny-live / live-shadow plumbing 的 blocking anomaly
- 因此本轮合法动作落在：
  - **Run 2 = `Rank 146` 与 `Rank 111` 的最短 decisive compare**

### 2) 范围控制
本轮只做 **1 个主点 + 1 个紧邻子点**：
- 主点：判断 `Rank 146` 在首刀 frozen-skeleton cut 之后，是否还值得继续占 active Scout 主资源
- 紧邻子点：与 `Rank 111` 这个已完成 clean replication + strictness delta compare 的 evidence anchor 做 desk-level 最短对照

本轮**不**：
- 重跑任何已完成的 clean replication
- 新开 `Rank 146` 第二刀 skeleton
- 触碰任何已自动运行的 paper runner

---

## 使用的 authoritative evidence

### Rank 146
- `research/optimization_loop/2026-03-23_0553_rank146-structure-verdict-optimizer-intake.md`
- `research/optimization_loop/2026-03-23_0607_rank146-frozen-skeleton-cut.md`
- 关键口径：repo 内置 `EMA-ADX-VOL` 15m frozen-skeleton 首刀在 `BTC/ETH/SOL` 上
  - `positive_asset_ratio = 0/3`
  - `full_stack_mean_total_return @ 6bps ≈ -18.93%`
  - `full_stack_trade_retention @ 6bps ≈ 17.97%`

### Rank 111
- `research/optimization_loop/2026-03-20_0652_rank111_event_clock_clean_replication.md`
- `research/optimization_loop/2026-03-23_0539_rank111-strictness-delta-compare.md`
- 关键口径：
  - `same_window_only @ 6bps`: `positive_asset_ratio = 2/3`, `mean_total_return ≈ -2.44%`
  - `window_plus_timeout @ 6bps`: `positive_asset_ratio = 2/3`, `mean_total_return ≈ -3.41%`
  - 放宽 strict 定义后，`PBO` 由 `0.7143` 变差到 `0.8000`

---

## 本轮新增轻量 compare artifact
- `reports/artifacts/pbo_cscv_honesty_gate/rank146_vs_rank111_active_compare_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank146_vs_rank111_active_compare_20260323.json`

---

## 结果：谁更该保留 active Scout 主资源？

### 结论
**`Rank 111` 保留 active Scout 主资源优先级；`Rank 146` 退回 method-evidence reserve。`**

### 为什么这个结论已经足够 decisive

#### A. `Rank 146` 的唯一允许首刀已经把最关键问题问完了
它的首刀目标不是证明“优化器无用”，而是回答：
> 只要把结构交给 repo 内置 optimizer skeleton，是否就会出现最小正 pocket？

当前答案是否定的：
- `BTC/ETH/SOL` 三资产仍全负
- `positive_asset_ratio = 0/3`
- 改善主要来自砍交易，不是形成稳定正 pocket
- `full_stack retention` 只剩约 `18%`

这说明它此刻更像：
- **方法层 reserve / honesty accelerator**，而不是应该继续占默认主资源的 active Scout primary

#### B. `Rank 111` 虽然没升层，但 still gives cleaner routing evidence
`Rank 111` 的当前价值不在“快升 P2”，而在：
- 它已经证明 **same-window 跟单** 比 baseline 更诚实
- 已经有 clean replication
- 已经有 strictness delta compare
- 已经把“放宽 strict 语义会不会更可信”这个常见借口也提前问掉了，答案还是 **不会**

换句话说：
- `Rank 111` 剩下的是 **低成本的 routing / evidence 工作**
- `Rank 146` 剩下的则是 **更贵、且尚未被顶板授权的第二刀 skeleton compare**

#### C. desk 当前需要的是“更快做出 P1 routing”，不是继续养一个方法想象位
顶板本轮的真正问题是：
> 在 fresh intake `Rank 146` 首刀没触发升层后，谁还更配继续占 active Scout 主资源？

如果把预算继续留给 `Rank 146`：
- 下一步必须新开 apples-to-apples skeleton compare
- 成本更高
- 也还不一定能改层级

而留给 `Rank 111`：
- 至少是在已经完成 clean replication 的 evidence anchor 上做剩余最短判断
- 边际价值更直接
- 更贴近顶板写明的 `Run 3` fallback 口径

---

## desk-level verdict

### 对 `Rank 146`
- 由：`keep_P1 / one frozen-skeleton cut spent / no promote yet`
- 收紧为：**`keep_P1 / method-evidence reserve / no longer active Scout main-resource priority`**

### 对 `Rank 111`
- 维持：**`keep_P1 / evidence anchor / compare value > standalone budget`**
- 并明确：**在当前 desk 阶段，它比 `Rank 146` 更值得继续保留 residual Scout 预算**

---

## 轻量 scorecard
- `usefulness = Rank111 > Rank146 for immediate desk routing`
- `time_stability = both weak; Rank111 slightly better`
- `cross_asset_stability = Rank111 better (2/3 vs 0/3)`
- `cost_trade_stability = both weak; Rank146 relies on retention collapse`
- `deployability = both low`

### hard-fail flags
- `rank146_no_positive_asset_pocket`
- `rank146_first_cut_spent`
- `rank146_retention_collapse`
- `rank111_looser_strictness_worsens_pbo`
- `neither_candidate_is_p2`

### recommended_action
- **`keep_P1`**

### why_now
顶板已经明确要求：`Rank 146` 首刀若未触发升层，下一轮就只允许做它与 `Rank 111` 的最短 decisive compare，判断它是否仍配占 active Scout 主资源。本轮这一步已经完成，而且结论足够稳定：**不配。**

### main_weakness
`Rank 146` 的方法层想象仍未被更贴近 desk skeleton 的 apples-to-apples compare 覆盖；`Rank 111` 也仍然受 `ETH` 结构性拖累，所以当前没有任何一方值得升到 `P2`。

---

## TODO writeback
本轮建议做**最小局部修改**：
1. 把 `Rank 146` 从“active Scout 默认首位”收紧成 `method-evidence reserve / 不再占 active Scout 主资源优先级`
2. 在 `Rank 111` 行补一句：`当前边际价值高于 Rank146 的继续二刀`
3. `Next 3` 保持简洁，只把这次 compare 的结论压进去，不重写长时间线

---

## 交付
- 日志：`research/optimization_loop/2026-03-23_0624_rank146-vs-rank111-active-compare.md`
- artifact：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank146_vs_rank111_active_compare_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank146_vs_rank111_active_compare_20260323.json`
