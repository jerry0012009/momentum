# 2026-03-17 03:26 UTC · Rank 20 price-volume divergence breakout filter clean replication + park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：`Paper Seat = EMA` 当前仍是 `waiting_not_due`，所以本轮主资源继续落在 `Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17` 虽在 `paper candidate pool`，但当前若无 genuinely verdict-changing 新检查，不该继续磨 wiring；
  - `Rank 2` 已是 narrow paper pilot，默认只在有真实 append/review need 时认领；
  - `Rank 7~16 / 18 / 19` 已完成快筛并 `park`。
- 因此本轮继续执行 `2m fresh intake`：选择 repo 现有、可直接复用缓存且规则可清楚写成 `trade on / trade off` 的候选 `price_volume_divergence.py`，做一刀最小快筛闭环。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 20 price-volume divergence breakout filter` 的 `clean replication + Light Stability Pack` 并给 hard verdict。
- 紧邻子点：把 `Rank 20` verdict 写回 `docs/TODO.md` 顶部战板（候选阶段表 + 当前窗口说明）。

## 做了什么改动
1. 新增脚本：
   - `scripts/build_price_volume_divergence_scout_clean_replication.py`
   - 规则映射：
     - 方向层：`multi-tf momentum`（repo 现有）
     - 过滤层：若 breakout 时量能确认明显弱于上一次对应 breakout，触发 divergence warning，阻断追单
   - 数据：复用本地 `Binance 120d 15m` cache（`BTC/ETH/SOL`），不追新 bar。

2. 产出 artifact：
   - `reports/artifacts/scout_price_volume_divergence_15m/clean_room_spec_v1.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/clean_replication_summary.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/clean_replication_asset_summary.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/clean_replication_trades.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/time_stability.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/parameter_stability.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/cross_asset_stability.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/cost_trade_stability.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/paper_candidate_admission_memo.csv`
   - `reports/artifacts/scout_price_volume_divergence_15m/clean_replication_meta.csv`

3. reader-facing 页面：
   - `reports/site/factors/scout_price_volume_divergence_15m/report.html`

## 轻量诚实守门（进入 LSP 前）
- `trade on`：多周期动量同向，且当前方向未触发量价背离 warning。
- `trade off`：反向信号触发平仓并可翻向。
- 实现口径只用当下与历史 bar 的 rolling breakout / volume z-score；没有 lookahead / repaint / data leakage。

## 验证 / 证据（Light Stability Pack）
### 1) clean replication（6bps/side）
- baseline `baseline_mtf_momentum`：
  - `mean_total_return ≈ -38.69%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 570.7`
- 主变体 `pvd_break24_delta0.5_warn3`：
  - `mean_total_return ≈ -39.22%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 552.0`
- 读法：过滤层没有把 baseline 拉回 admission 线，反而轻微更差。

### 2) 时间稳定性
- 主变体三个时间 bucket：
  - `bucket_1 ≈ -10.84%`
  - `bucket_2 ≈ -18.85%`
  - `bucket_3 ≈ -15.32%`
- 正收益 bucket：`0/3`（无稳定正向时间 pocket）。

### 3) 参数稳定性
- 邻域最不差：`pvd_break20_delta0.5_warn3 ≈ -37.86%`
- 其余邻域大多更差（约 `-40.9%` 到 `-45.1%`）
- 读法：参数邻域没有出现“调小范围就转正”的证据。

### 4) 跨标的稳定性（主变体）
- `BTC-USD total_return ≈ -52.19%`
- `ETH-USD total_return ≈ -45.27%`
- `SOL-USD total_return ≈ -20.21%`
- 结果：`0/3` 为正，跨标的不成立。

### 5) 成本 / 交易数稳定性
- `6bps/side ≈ -39.22%`
- `10bps/side ≈ -61.37%`
- `15bps/side ≈ -77.93%`
- `20bps/side ≈ -87.29%`
- 读法：friction 上升后显著恶化，且 trade count 仍很高（非“太少导致失真”）。

## 本轮 hard verdict
- `Rank 20 price-volume divergence breakout filter`：**`park / evidence pool`**。
- 原因：
  1. 主变体在 6bps 下跨资产显著为负且不优于 baseline；
  2. 时间 / 参数 / 跨标的 / 成本-交易数四项都没给 admission 证据；
  3. 成本敏感性明显恶化，不满足 paper candidate 最小门槛。

## 过程异常与 fallback 记录
- 未触发 `edit exact-match` 失败；
- 脚本运行时间偏长但正常完成，无需 fallback 改写。

## 下一步建议
1. 继续执行 `2m fresh intake`，优先挑新的 paper/repo based 5m/15m crypto 候选，不回头继续磨 `Rank 20`。
2. 若下一轮认领旧候选，仍只建议：
   - `Rank 17` 的 genuinely verdict-changing 最小检查；或
   - `Rank 2` 的真实 append/review need。

## 提交状态
- 本轮未提交 git（工作区存在大量与本轮无关脏文件，避免混提）。
