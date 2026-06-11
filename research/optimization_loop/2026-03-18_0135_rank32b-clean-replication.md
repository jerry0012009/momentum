# 2026-03-18 01:35 UTC — Rank 32b clean replication：删 reclaim 后没塌，但仍只配 P1

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行。
- `Run 1 / EMA` 已在 `00:02 UTC` 消化完 crypto due-now refresh，当前回到 `running paper / waiting_not_due`。
- 当前 authoritative board 已把 `Rank 32b / slope-floor continuation gate` 指定为 active Scout 主线，因此这轮不再回头磨 `Rank 17 / Rank 2 / Rank 29` 的 P3 continuity，也不去碰 `Rank 35b`。
- 本轮只认领 1 个主点 + 1 个紧邻子点：
  1. 主点：把 `Rank 32b` 从 `source intake` 推到 **最小 clean replication**；
  2. 子点：补 **1 次会改 verdict 的最小诚实检查**，优先做时间稳定性。

## 做了什么改动
1. 新增独立脚本：
   - `scripts/build_rank32b_slope_floor_continuation.py`
2. 用现有 `BTC/ETH/SOL 120d 15m` cache 生成 `Rank 32b` 独立 artifact：
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/asset_summary_primary_6bps.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/trades_primary_6bps.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/time_bucket_summary.csv`
   - `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/meta.csv`
3. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank32b_slope_floor_continuation_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/rank32b_slope_floor_continuation_clean_replication.html`
4. 对 `docs/TODO.md` 做最小局部写回：
   - 把 `Rank 32b` 当前状态从 `source intake -> clean replication next` 更新为 **`P1 weak candidate / evidence pool`**；
   - 同步把 `Next 3 bot3 runs` 改成：下一轮若 `EMA` 仍是 `waiting_not_due`，`Run 2` 只允许给 `Rank 32b` 那唯一 1 次便宜诚实检查（优先参数稳定性 / friction 邻域），不再重复 source intake。

## 验证 / 证据
### 1) clean replication 主证据
固定只比较两档：
- `ema_cross_only`（baseline）
- `ema_cross_plus_slope_floor`（Rank 32b 主变体）

`Rank 32b` 主变体在 `6bps/side` 下的跨资产结果：
- `mean_total_return≈50.76%`
- `positive_asset_ratio≈100.00%`
- `mean_trades≈75.7`
- `mean_false_reclaim_ratio≈7.87%`
- `mean_no_trade_ratio≈99.34%`

对照 baseline：
- `ema_cross_only @ 6bps/side -> mean_total_return≈-18.73%`
- 说明删掉 `spread-mid reclaim` 后，edge 没有塌回 baseline，反而保住了更强 pocket。

### 2) 时间稳定性（本轮唯一额外诚实检查）
把主变体交易样本按时间三等分：
- `bucket_1≈+16.07% / positive_asset_ratio=100.00%`
- `bucket_2≈+9.48% / positive_asset_ratio=100.00%`
- `bucket_3≈+16.95% / positive_asset_ratio=100.00%`

这说明 `Rank 32b` 当前至少**不是只靠单一时间 pocket 偶然翻正**。

### 3) 为什么仍不是 P2
虽然 clean replication 与时间稳定性都站住了，但当前更诚实的 blocker 仍是：
- `mean_no_trade_ratio≈99.34%`，交易密度还是偏稀；
- 它还没到“可以默认推进成 paper candidate”的可执行密度。

所以本轮 hard verdict 只能是：
- **`P1 weak candidate / evidence pool`**
- 而不是 `P2 paper candidate`

## 核心结论
- **一句话结论**：`Rank 32b` 证明了真正有信息量的更像 `aligned slope floor`，不是那层更漂亮的 `spread-mid reclaim`；但它的交易密度仍偏稀，所以当前最多只配保留 **1 次便宜诚实检查预算**。
- **证据怎么支持它**：baseline 为负、`slope_floor_only` 在跨资产与时间 tercile 上都保持为正，说明删 reclaim 后 pocket 没塌；但 `no_trade_ratio` 仍高到不适合直接升为 `paper candidate`。

## 风险 / 边界
- 本轮没有补完整 `Light Stability Pack` 四件套，只补了其中最便宜且最会改 verdict 的一项：时间稳定性。
- 当前最该警惕的不是“收益不够漂亮”，而是 **trade density 仍偏稀**；因此后续若继续认领，默认应优先看 `参数稳定性 / friction 邻域` 是否一碰就碎。
- 这条线当前仍不应抢走 `Paper Seat`，也不应误升到 `Live Seat`。

## 下一步建议
- 若下一轮 `EMA` 仍是 `waiting_not_due`，则对 `Rank 32b` 默认只允许做 **1 次便宜诚实检查**：
  - 优先 `参数稳定性`（小 slope floor 邻域）或
  - `friction / trade-count` 邻域检查。
- 若这唯一检查也没能把它推到更清楚的 admission 状态，应更偏向把它压回 `park / evidence pool`，然后回到新的 fresh intake，而不是长期绑死在 `32b`。

## Commit hash
- 未提交。
- 原因：repo 中存在大量与本轮无关的脏文件；当前只适合保留 selective artifact / log / site 更新，不适合安全混提。
