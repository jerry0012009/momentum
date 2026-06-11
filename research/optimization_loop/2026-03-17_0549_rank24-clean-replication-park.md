# 2026-03-17 05:49 UTC · Rank 24 clean replication → 压回 park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD`：
  - `Paper Seat = EMA waiting_not_due`，当前不能在 waiting-window 空转；
  - `Live Seat = 暂空`；
  - 因此本轮合法落点仍是 `Run 2 / Scout Seat`。
- 先比较当前 active Scout 候选的边际价值：
  - `Rank 17`：已经是 `P3 narrow paper pilot`，但当前没有新的真实 `append/review need`；
  - `Rank 2`：同样仍是 `P3`，当前也没有新的真实 `append/review need`；
  - `Rank 7`：唯一允许的 cheap honesty recheck 已完成，并已压回 `park / evidence pool`；
  - `Rank 24`：上一轮刚完成 `source intake + Stage A honesty gate`，最诚实的下一步就是直接用固定 cache 做最小 `clean replication`，不要继续磨 intake 卡。
- 因此本轮主点固定为：**把 `Rank 24 trend regime filter / trend-strength-over-noise gate` 从 intake 推到 clean replication + Light Stability Pack verdict，并给出 `park / paper candidate / narrow paper pilot` 三选一硬结论。**

## 本轮主点 + 紧邻子点
- 主点：新增 `Rank 24` 的 clean replication + Light Stability Pack artifact / report。
- 紧邻子点：把 `docs/TODO.md` 顶部交易台指挥板与 `trendline_alpha_scout` reader-facing 页面同步到最新 hard verdict。

## 本轮做了什么
### 1) 新增脚本
- `scripts/build_trend_regime_filter_clean_replication.py`

作用：
- 复用固定 `BTC/ETH/SOL 120d 15m` cache；
- 直接比较：
  - `baseline_mtf`
  - `trend_regime_default`
  - `stricter_trend_threshold`
  - `stricter_regime_score`
- 同轮补齐 `Light Stability Pack`：
  - 时间稳定性
  - 参数稳定性
  - 跨标的稳定性
  - 成本 / 交易数稳定性

### 2) 新增 deployable artifact
新增目录：
- `reports/artifacts/scout_trend_regime_filter_15m/`

关键文件：
- `clean_room_spec_v1.csv`
- `clean_replication_summary.csv`
- `clean_replication_asset_summary.csv`
- `clean_replication_trades.csv`
- `time_stability.csv`
- `parameter_stability.csv`
- `cross_asset_stability.csv`
- `cost_trade_stability.csv`
- `paper_candidate_admission_memo.csv`
- `clean_replication_meta.csv`

### 3) 新增 reader-facing 页面
- `reports/site/factors/scout_trend_regime_filter_15m/report.html`

并同步：
- `docs/TODO.md`
- `reports/site/reading/trendline_alpha_scout/report.html`

## 关键结果
### 最小 clean replication 对照（6bps/side）
- `baseline_mtf`：
  - `mean_total_return ≈ -38.69%`
  - `positive_asset_ratio = 0/3`
- `trend_regime_default`：
  - `mean_total_return ≈ -28.29%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 289.3`
  - `mean_no_trade_ratio ≈ 65.24%`
- `stricter_trend_threshold`：
  - `mean_total_return ≈ -9.81%`
  - `positive_asset_ratio = 1/3`
  - `mean_no_trade_ratio ≈ 74.94%`
- `stricter_regime_score`：
  - `mean_total_return ≈ -24.24%`
  - `positive_asset_ratio = 0/3`

### 跨标的稳定性（主变体）
- `BTC-USD ≈ -37.56%`
- `ETH-USD ≈ -24.01%`
- `SOL-USD ≈ -23.31%`
- 没有任何资产转正，因此不是 `paper candidate`。

### 时间稳定性
- 主变体确实有少数单资产时间 bucket 为正：
  - `BTC bucket_2 ≈ +4.45%`
  - `ETH bucket_2 ≈ +30.19%`
  - `SOL bucket_3 ≈ +39.25%`
- 但这没有形成跨资产、跨时间同时可复用的稳定 pocket；同一资产其他 bucket 仍明显转负。

### 参数稳定性
- 邻域最佳是 `w36_t018_s20`：
  - `mean_total_return ≈ -17.83%`
  - `positive_asset_ratio = 1/3`
- 它只是在亏损上收敛，没有给出可升格的参数平台。

### 成本 / 交易数稳定性（主变体）
- `10bps ≈ -43.31%`
- `15bps ≈ -57.57%`
- `20bps ≈ -68.10%`
- 成本梯度持续恶化，因此不具备进入 `paper candidate pool` 的诚实基础。

## hard verdict
- `Rank 24 trend regime filter / trend-strength-over-noise gate` 当前应 **压回 `park / evidence pool`**。
- 更诚实的 desk 读法是：
  - 这条线能把 baseline 的亏损收窄；
  - 但它没有把结果推进到跨资产成本后可用，更没有形成可升格的稳定 pocket；
  - 因此它更适合作为 **regime gate 反例 / evidence**，而不是 `paper candidate`。

## 对 desk 主线的意义
- 这轮没有继续在 Rank 24 上做 wording / intake 近义卡，而是把它迅速收口成一个 hard verdict；
- 做完之后，Scout Seat 的当前默认顺序更干净：
  - 先看 `Rank 17 / Rank 2` 是否出现真实 `P3 append/review need`；
  - 若没有，就继续转去新的 `paper / repo based 5m / 15m crypto` fresh intake；
  - 不再让 `Rank 24` 继续无期限占用快筛预算。

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_trend_regime_filter_clean_replication.py`
2. `python3 scripts/build_trend_regime_filter_clean_replication.py`
3. 读取并核对：
   - `reports/artifacts/scout_trend_regime_filter_15m/clean_replication_summary.csv`
   - `reports/artifacts/scout_trend_regime_filter_15m/cross_asset_stability.csv`
   - `reports/artifacts/scout_trend_regime_filter_15m/time_stability.csv`
   - `reports/artifacts/scout_trend_regime_filter_15m/paper_candidate_admission_memo.csv`
4. 核对 reader-facing 页面：
   - `reports/site/factors/scout_trend_regime_filter_15m/report.html`
   - `reports/site/reading/trendline_alpha_scout/report.html`
5. 核对 `docs/TODO.md` 顶部 `TRADING DESK BOARD / 2q` 已写回最新 verdict。

## 风险 / 边界
- 本轮没有重开 breakout，也没有并行打开其他 fresh intake。
- 本轮只在现有 cache 上做最小 clean replication；没有新下载、没有新数据源。
- 时间稳定性里存在零散正 bucket，但当前没有形成跨资产可复用 pocket；因此不应把“局部有亮点”误写成可升格证据。

## 下一步建议
- 若下一轮 `EMA` 仍是 `waiting_not_due`：
  1. 先看 `Rank 17 / Rank 2` 是否出现新的真实 `P3 append/review need`；
  2. 若没有，就回到新的 fresh intake，继续寻找更快能给出 `park / paper candidate / narrow paper pilot` verdict 的 repo-based `5m / 15m crypto` 候选。

## 网页可见落点
- `reports/site/factors/scout_trend_regime_filter_15m/report.html`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`

## Git / 提交
- 本轮未提交。
- 原因：工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
