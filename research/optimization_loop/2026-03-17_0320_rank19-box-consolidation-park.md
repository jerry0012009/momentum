# 2026-03-17 03:20 UTC · Rank 19 box consolidation / structure breakout clean replication + park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat = EMA` 当前仍是 `waiting_not_due`，所以这轮主资源必须切到 `Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17` 仍在 `paper candidate pool`，但刚补完最小 wiring；若没有 genuinely verdict-changing 的新证据，不该继续磨它；
  - `Rank 2` 只剩 narrow-paper append/review 类最小维护；
  - `Rank 7~16 / 18` 都已完成 clean replication + Light Stability Pack 并压回 `park`。
- 因此这轮按 board 的默认顺序，认领一个新的 `paper / repo based 15m crypto` 候选：把 Lo / Jiang 的“价格结构本身有信息”语义，映射到 repo 已有 `box_consolidation.py` 模块，做一刀最小快筛闭环。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 19 box consolidation / structure breakout` 的 `clean replication + Light Stability Pack`。
- 紧邻子点：把新 verdict 写回 `docs/TODO.md` 顶部战板，并落一个 reader-facing report 页面。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_box_consolidation_scout_clean_replication.py`
   - 规则来源：
     - 论文锚点：`Lo et al. (2000)` / `Jiang, Kelly, Xiu (2023)`
     - repo 锚点：`src/momentum/signals/box_consolidation.py`
   - 只复用本地 `Binance 120d 15m` cache（`BTC/ETH/SOL`），不下载新数据、不追新 bar。

2. 新增 artifact：
   - `reports/artifacts/scout_box_consolidation_15m/clean_room_spec_v1.csv`
   - `reports/artifacts/scout_box_consolidation_15m/clean_replication_summary.csv`
   - `reports/artifacts/scout_box_consolidation_15m/clean_replication_asset_summary.csv`
   - `reports/artifacts/scout_box_consolidation_15m/clean_replication_trades.csv`
   - `reports/artifacts/scout_box_consolidation_15m/time_stability.csv`
   - `reports/artifacts/scout_box_consolidation_15m/parameter_stability.csv`
   - `reports/artifacts/scout_box_consolidation_15m/cross_asset_stability.csv`
   - `reports/artifacts/scout_box_consolidation_15m/cost_trade_stability.csv`
   - `reports/artifacts/scout_box_consolidation_15m/paper_candidate_admission_memo.csv`
   - `reports/artifacts/scout_box_consolidation_15m/signal_snapshot.csv`
   - `reports/artifacts/scout_box_consolidation_15m/clean_replication_meta.csv`

3. 新增 reader-facing 页面：
   - `reports/site/factors/scout_box_consolidation_15m/report.html`

4. 更新战板：
   - `docs/TODO.md`
   - 新增 `Rank 19 box consolidation / structure breakout -> park / evidence pool`
   - 同步更新当前窗口说明：这轮完成后，默认仍应继续 fresh intake，而不是回头继续磨 `Rank 19`。

## 规则冻结（trade on / trade off）
- `trade on`：先出现近期回撤，再出现窄幅箱体或更宽箱体；当前 bar 满足 `narrow_accum_ready / box_breakout_ready / accumulation_ready` 三档结构触发之一，下一根 `open` 才进场。
- `trade off`：信号撤销、`1 ATR` 止损、`2 ATR` 止盈，或持有 `8` 根 bar 到时退出。
- 诚实口径：全部条件只使用当下和过去 bar 计算；没有 future label，也没有回头改箱体。

## 验证 / 证据（Light Stability Pack）
### 1) Clean replication（6bps/side）
- `accumulation_ready`（主变体 `d1.5_nb1.5_box20_buf5`）
  - `mean_total_return ≈ -20.13%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 177.3`
  - `mean_no_trade_ratio ≈ 88.26%`
- `narrow_accum_ready`
  - `mean_total_return ≈ -20.10%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 170.7`
- `box_breakout_ready`
  - `mean_total_return ≈ -0.77%`
  - `positive_asset_ratio = 1/3`
  - `mean_trades ≈ 9.3`
  - `mean_no_trade_ratio ≈ 99.91%`

### 2) 时间稳定性
- 主变体 `accumulation_ready` 的三个时间 bucket 分别约：
  - `bucket_1 ≈ -7.06%`
  - `bucket_2 ≈ -5.22%`
  - `bucket_3 ≈ -9.30%`
- 结果：`0/3` bucket 为正，没有出现“只是某一小段坏、其他时间还行”的读法。

### 3) 参数稳定性
- 邻域里最不差的一档是 `d2.0_nb1.5_box20_buf5`，但跨资产 `mean_total_return` 仍约 `-9.87%`；
- 其余邻域多在 `-18% ~ -31%` 区间。
- 结果：参数邻域没有把它拉回 admission 线，不是“热像素幸运点”。

### 4) 跨标的稳定性（主变体）
- `BTC-USD total_return ≈ -16.88%`
- `ETH-USD total_return ≈ -22.59%`
- `SOL-USD total_return ≈ -20.92%`
- 结果：`0/3` 为正，跨资产不成立。

### 5) 成本 / 交易数稳定性
- `6bps/side ≈ -20.13%`
- `10bps/side ≈ -30.70%`
- `15bps/side ≈ -41.96%`
- `20bps/side ≈ -51.40%`
- 结果：随着 friction 增加持续恶化；而较窄的 `box_breakout_ready` 虽然“少亏”，但交易数只有 `~9.3` 笔/资产，太稀疏，不能诚实地拿来做 admission 依据。

## 本轮 hard verdict
- `Rank 19 box consolidation / structure breakout`：**`park / evidence pool`**。
- 原因：
  1. 主变体 `accumulation_ready` 在 6bps 下已是高交易数持续亏损；
  2. 时间 / 参数 / 跨标的 / 成本-交易数四项都没有把它拉回 admission 线；
  3. 更窄的 `box_breakout_ready` 虽然只是轻微少亏，但交易样本太薄，不足以支撑 `paper candidate`。

## 风险 / 边界
- 这轮的结论是：当前 repo 里的这套 `box_consolidation` 语义，**并没有**在 15m crypto 上转成可 admission 的候选；
- 但它留下了一个有用反例：`价格结构` 这条大方向不等于“任何结构规则都有效”，尤其不能把低交易数少亏误读成 candidate；
- 因此下一轮默认应继续 fresh intake，而不是继续在 `Rank 19` 上追加 closeout / wording。

## 过程异常与 fallback 记录
- 本轮没有触发 `edit exact-match` 失败；
- clean replication 脚本首次运行无逻辑报错，只出现 `numpy` 的 `FutureWarning: DataFrame.swapaxes` 提示，不影响结果；未额外处理。

## 下一步建议
1. Scout 默认继续找新的 `paper / repo based 5m / 15m crypto` 候选，不回头继续磨 `Rank 19`。
2. 若下一轮仍想认领旧候选，优先级仍是：
   - `Rank 17` 仅限 genuinely verdict-changing 的最小检查；
   - `Rank 2` 仅限真实 append/review need；
   - 否则继续 fresh intake。

## 提交状态
- 本轮未提交 git。
- 原因：工作区存在大量与本轮无关的历史脏文件 / 未跟踪产物；本轮只做 selective 产物写入与战板最小更新，避免混提。
