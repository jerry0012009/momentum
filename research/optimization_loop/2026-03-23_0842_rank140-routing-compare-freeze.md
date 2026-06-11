# 2026-03-23 08:42 UTC · Rank 140 routing compare freeze（最短 decisive 收口）

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 顶板判定：`Paper / 待开启自动运行 = empty`，且未见新的 interrupt，因此继续执行当前最高优先级 Scout 的最短 decisive 验证。

## 0. 本轮主点与紧邻子点
### 主点
- 把 `Rank 140 / pbo-cscv deflated sharpe honesty gate` 与当前顶板里最直接的两条备选（`Rank 145`、`Rank 14b`）做一次**routing compare freeze**：
  - 不再新增 family / pocket / 参数；
  - 只用现成 authoritative artifacts 回答一句最实际的问题：
  - **如果现在必须在这三条里继续保留一个默认 Scout 主位，谁最有资格继续留在前面？**

### 紧邻子点
- 同步产出一张可直接被后续日志 / 邮件 / 首页引用的 compare 表，避免下一轮又回到口头判断。

## 1. 为什么这一步现在最有杠杆
前几轮已经把 `Rank 140` 收紧到：
- shared honesty gate 没成立；
- 真正 surviving 的只剩 `Rank 137 / confirm_window_12` 主 pocket；
- `Rank 145` 已做完 frozen-threshold A/B，但阈值一次都没触发；
- `Rank 14b` 已正式 scorecard 化，但仍只是 cheap fallback。

所以本轮最有杠杆的小步，不是继续切同一家族，而是把三者的**路由优先级**写死成一个最短可验证结论。

## 2. 本轮新增产物
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.json`

## 3. 核心结果
### 3.1 Rank 140 仍然保住默认前位，但只剩 pocket 级理由
- 依据：`rank140_rank137_surviving_pocket_scorecard_20260323.csv`
- 当前唯一主 pocket：`Rank 137 / confirm_window_12`
- `mean_net_bps_6bps_side = +100.6235`
- `positive_asset_count = 3/3`

读法：
- 在三条候选里，`Rank 140` 仍保留**最强、最干净、跨 BTC/ETH/SOL 都为正**的现成证据；
- 但这不是 shared honesty layer 成立，而只是 **family-specific surviving pocket 仍最能打**。

### 3.2 Rank 145 当前不配继续抢默认主位
- 依据：`frozen_threshold_ab_summary.csv` + `promotion_scorecard.csv`
- `PORT_EQW_BTC_ETH_SOL` 基线：
  - `post_cost_return = +47.89%`
  - `max_drawdown = 1.85%`
- 但 `8/10/12%` 回撤阈值在全部组合下 **0 次触发 reduced mode**。

读法：
- 它不是被证伪，而是**在当前 desk 共享代理上根本没被武装起来**；
- 因此目前只能继续留在 `reserve / keep_P1 / budget used`，不能反超 `Rank 140`。

### 3.3 Rank 14b 仍只是 cheap fallback
- 依据：`scout_rank14b_ema_psar_long_veto/scorecard.csv`
- 已知最强读法：`6bps/side` 从 `-16.36 bps` 改到 `+3.80 bps`
- 但：
  - `trade_retention = 59.62%`
  - `ETH` 仍显著拖累
  - `10/15 bps` 后仍为负

读法：
- 它能改读法，但还不能改 desk 主线；
- 更合适的位置仍是 **cheap decisive fallback**，而不是新的默认 primary。

## 4. 人话结论
这轮最短、最硬的收口是：

> **在 Rank 140、145、14b 这三条当前最相关候选里，Rank 140 仍保留默认 Scout 前位，但理由已经收紧成“Rank 137 / confirm_window_12 这个单一 surviving pocket 还最强”；Rank 145 还没被本地 proxy 武装起来，Rank 14b 仍只是 fallback。**

换句话说：
1. 这轮没有把谁升层；
2. 但把“为什么暂时还是 Rank 140 在前”写成了可核对的 compare 表；
3. 同时也把下一步边界写清楚：**如果 Rank 140 再没有新的 decisive cut，就该优先轮转到 fresh reserve / fallback，而不是继续在同一家族里切细片。**

## 5. lightweight scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`
- `recommended_action = keep_P1`
- `why_now = 这一步能把当前 Scout 主位的排序理由正式冻结，减少后续重复争论与同义切片`
- `main_weakness = Rank 140 的优势仍来自 single surviving pocket，而非 shared honesty rule 本身`

## 6. desk verdict
- `Rank 140`：维持 `keep_P1 / active compare anchor / not default primary-for-promotion`
- `Rank 145`：维持 `keep_P1 / budget used / reserve`
- `Rank 14b`：维持 `keep_P1 / cheap decisive fallback`

## 7. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0842_rank140-routing-compare-freeze.md`
- artifacts：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.json`
