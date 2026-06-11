# 2026-03-19 19:25 UTC — Rank 97 clean replication -> park

## 本轮执行顺序
- 先按 `Run 1` 实跑：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 美股 1d+1wk：约 `43 分钟` 后到点
  - Crypto 1d+1wk：约 `4.7 小时` 后到点
  - 创业板ETF 1d：约 `11.7 小时` 后到点
- 因此按顶板与 `Next 3 bot3 runs`，本轮合法主动作切到 `Run 2`：`Rank 97 / RSRS right-skew shared veto + sizing overlay` 的 **1 次最小 clean replication**。

## 认领点
- 主点：`Rank 97 / RSRS right-skew shared veto + sizing overlay`
- 紧邻子点：无（本轮没有再并行打开 Fib placebo / CLV reserve）

## 本轮新增 / 执行
- 新增脚本：`scripts/build_rank97_rsrs_right_skew_clean_replication.py`
- 固定口径：`BTC/ETH/SOL | 120d | 15m | signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 比较四臂：
  - `no_overlay`
  - `hard_veto`
  - `half_size_overlay`
  - `tiered_sizing_overlay`
- 产物：
  - `reports/artifacts/scout_rank97_rsrs_right_skew_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank97_rsrs_right_skew_15m/asset_summary.csv`
  - `reports/artifacts/scout_rank97_rsrs_right_skew_15m/setup_summary.csv`
  - `reports/artifacts/scout_rank97_rsrs_right_skew_15m/trades.csv`
  - `reports/artifacts/scout_rank97_rsrs_right_skew_15m/meta.csv`
- 网页落点：
  - `reports/site/factors/scout_rank97_rsrs_right_skew_15m/report.html`
  - `reports/site/reading/repo_scout/rank97_rsrs_right_skew_clean_replication.html`

## 硬结论
**`Rank 97 = park`**。

换成人话：
- RSRS right-skew 这条线在当前 desk 里**更像噪声型 sizing overlay**，没有把三条 base setup（`ema_psar_long / fib_retest_long / breakout_short`）的成本后结果推过门槛。
- 它不是“减亏但还能留在主资源位”的情况，而是这次最小 clean replication 已经给出足够诚实的否定：**不值得继续占 Scout Seat**。

## 关键读数（6bps/side）
### Desk 总体
- `no_overlay`
  - `total_return = -0.8437`
  - `mean_total_return = -0.0958%`
  - `trade_count = 881`
  - `positive_asset_ratio = 1/3`
- `hard_veto`
  - `total_return = -1.1495`
  - `trade_count = 726`
  - `positive_asset_ratio = 0/3`
- `half_size_overlay`
  - `total_return = -1.0220`
  - `trade_count = 859`
  - `positive_asset_ratio = 0/3`
- `tiered_sizing_overlay`（主判定臂）
  - `total_return = -1.1696`
  - `mean_total_return = -0.1362%`
  - `trade_count = 859`
  - `mean_position_size = 1.0314x`
  - `positive_asset_ratio = 0/3`
  - `veto_hit_rate = 16.76%`
  - `sizeup_hit_rate = 46.10%`

### 资产侧
- `BTC = -0.5714`
- `ETH = -0.5902`
- `SOL = -0.0080`
- 结果没有形成跨资产共享改善；SOL 接近打平，但 BTC/ETH 被进一步拖差。

### Setup 侧
- `breakout_short = -0.5705`
- `ema_psar_long = -0.2429`
- `fib_retest_long = -0.3563`
- 三条主线没有哪一条被 RSRS overlay 诚实救出来；尤其不是“共享 veto/sizing 一上就统一减假信号”的结构。

## 为什么直接 park
1. **成本后比 baseline 更差**：主判定臂 `tiered_sizing_overlay` 相对 `no_overlay` 没有改善，反而更差。
2. **没有跨资产改善**：`positive_asset_ratio` 从 `1/3` 掉到 `0/3`。
3. **不是靠严格 veto 少做交易就变好**：`hard_veto` 砍了交易数，结果仍更差。
4. **也不是温和 size-down / size-up 就能修好**：`half_size_overlay` 与 `tiered_sizing_overlay` 都没把 desk 结果拉回可升格区。

## 对交易台指挥板的影响
- `Paper Seat`：继续 **`EMA / running paper / waiting_not_due`**（本轮未到 refresh 窗口）
- `Live Seat`：继续空
- `Scout Seat`：`Rank 97` 本轮做完最小 clean replication 后，**直接压回 park / evidence pool**
- 下一优先动作应回到 fresh intake：
  1. `Fib placebo-zone honesty gate` source intake
  2. 若上条不成立，再到 `CLV asymmetric admission layer reserve`
  3. 再之后才允许回退旧 `P1 evidence_pool`

## 本轮对 TODO / board 的最小同步
- 已把 `docs/TODO.md` 的 `Next 3 bot3 runs` 追加本轮结果：
  - `Rank 97 = park`
  - `Run 2` 改为 `Fib placebo-zone honesty gate` source intake
  - `Run 3` 改为 Fib guard-pass 后的 1 次最小 clean replication；若 Fib 也失败，再轮到 `CLV reserve`

## 验证与边界
- 只做了最小必要验证：本地缓存、单次 clean replication、6bps 主口径
- 未追新 bar、未做重型下载、未额外打开 P3 continuity / tiny-live plumbing
- 当前 repo 有大量与本轮无关的脏文件；本轮未做 commit，避免混提

## 给下一轮的直接 handoff
如果下一轮再次 `EMA = waiting_not_due`：
- 不要回头续命 `Rank 97`
- 直接按 `7.10` 切到 `Fib placebo-zone honesty gate` 的 source intake
- 仍然保持“一轮只开 1 个主点”
