# 2026-03-17 05:03 UTC · Rank 23 volatility regime mid-band / cost-survival gate clean replication park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat` 上两个现存 `P3`（`Rank 17`、`Rank 2`）当前都没有真实 `append/review need`
- 因此本轮不能在 `Run 1` 空转，也不该继续磨旧 `P3 wiring`；最诚实的主点就是把上一轮刚冻结的 `Rank 23` 从 `fresh intake accepted / pending clean replication` 直接推进到 hard verdict。

## 开始前检查
- `git status --short --branch` 显示工作区仍有大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提
- `TODO` 顶板最新口径：`Rank 23` 是当前 `Scout Seat` 默认主资源位，要求固定 `BTC/ETH/SOL 120d 15m cache` 比较 `baseline_mtf / no_high_vol_extreme / rv_midband_q20_80`
- 当前没有新的 `EMA due-now` 信号，因此本轮合法落点仍是 `Run 2 / Scout Fast Lane`

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 23 volatility regime mid-band / cost-survival gate` 的最小 **clean replication + Light Stability Pack**
- 紧邻子点：把结果写回 `TODO` 顶板与 shortlist，并给出 reader-facing 网页落点

## 这轮做了什么

### 1) 新增 clean-replication 脚本与 artifact
新增脚本：
- `scripts/build_vol_regime_midband_clean_replication.py`

新增 artifact 目录：
- `reports/artifacts/scout_vol_regime_midband_15m/`

新增网页落点：
- `reports/site/factors/scout_vol_regime_midband_15m/report.html`

固定口径：
- `baseline_mtf`
- `no_high_vol_extreme`
- `rv_midband_q20_80`
- `rv_midband_q30_70`

全部复用：
- `BTC / ETH / SOL`
- `Binance 120d 15m cache`
- 现有 `multi_tf_momentum` backtest 管线
- 1h realized-vol rolling quantile gate（只用历史已完成 bar，避免 lookahead / repaint）

### 2) 完成 Light Stability Pack 四项
已写出：
- `clean_replication_summary.csv`
- `clean_replication_asset_summary.csv`
- `clean_replication_trades.csv`
- `time_stability.csv`
- `parameter_stability.csv`
- `cross_asset_stability.csv`
- `cost_trade_stability.csv`
- `paper_candidate_admission_memo.csv`
- `clean_replication_meta.csv`
- `clean_room_spec_v1.csv`

### 3) 同步 reader-facing / board 落点
更新：
- `docs/TODO.md`
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

同步内容：
- `Rank 23` 已从 `fresh intake accepted / pending clean replication` 更新为
  - **`clean replication + Light Stability Pack 已完成`**
  - **`hard verdict = park / evidence pool`**
- `Next 3 bot3 runs` 顶部 authoritative override 也同步改成：
  - `Rank 21 / 22 / 23` 已全部压回 `park`
  - 下轮默认应先比较 `Rank 17 / Rank 2` 是否出现真实 `append/review need`；若没有，再回到新的 fresh intake

## 结果

### aggregate clean replication（6bps/side）
- `baseline_mtf`：`mean_total_return ≈ -38.69%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 570.7`
- `no_high_vol_extreme`：`mean_total_return ≈ -43.30%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 402.3`
- `rv_midband_q20_80`：`mean_total_return ≈ -33.33%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 335.7`，`mean_no_trade_ratio ≈ 46.52%`
- `rv_midband_q30_70`：`mean_total_return ≈ -31.75%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 247.7`，`mean_no_trade_ratio ≈ 63.71%`

### 轻量稳定性结论
#### 1. 时间稳定性
- 主变体 `rv_midband_q20_80` 的 `time positive bucket = 0/3`
- 说明并不是“少数时间片翻正、只是 aggregate 被拖累”，而是三个 bucket 都没有给出足够诚实的正向信号

#### 2. 参数稳定性
- 参数邻域最佳是 `rv_midband_q20_80_slowrv`
- 但它也只有 `mean_total_return ≈ -14.79%`
- 其余邻域：
  - `q10_90 ≈ -32.40%`
  - `q20_80 ≈ -33.33%`
  - `q30_70 ≈ -31.75%`
  - `q20_80_fastq ≈ -39.38%`
- 这说明它不是“差一点点就能调正”的近邻结构，参数邻域没有形成可升格 pocket

#### 3. 跨标的稳定性
主变体 `rv_midband_q20_80`：
- `BTC ≈ -50.50%`
- `ETH ≈ -40.15%`
- `SOL ≈ -9.34%`
- `positive_asset_ratio = 0/3`

即使 `SOL` 相对没那么差，也还没到能支持 `paper candidate` 的程度。

#### 4. 成本 / 交易数稳定性
主变体 `rv_midband_q20_80`：
- `6bps ≈ -33.33%`
- `10bps ≈ -49.46%`
- `15bps ≈ -64.17%`
- `20bps ≈ -74.54%`

成本抬升后继续明显恶化，不存在当前 desk 需要的 `cost survival`。

## 本轮 hard verdict
**Rank 23 当前状态 = `park / evidence pool`。**

不进入 `paper candidate pool`。

原因不是“完全没净改善”，而是：
1. `rv_midband` 相比 baseline 确实少亏一些；
2. 但它仍然是全资产为负、时间稳定性 `0/3`、参数邻域也整体为负；
3. `no_high_vol_extreme` 甚至比 baseline 更差；
4. 这说明“避开极端高 vol / 只留中间 vol 带”在当前 15m BTC/ETH/SOL 样本上，不足以形成当前 desk 可升格的环境门。

## 对 desk 的意义
- 这条线已经完成它当前预算内应做的事：
  - `source intake`
  - `cheap honest check`
  - `clean replication`
  - `Light Stability Pack`
  - `hard verdict`
- 因此它不应再继续占 `Scout Seat` 默认主资源
- 当前更诚实的排兵布阵应回到：
  - 先看 `Rank 17 / Rank 2` 是否出现真实 `append/review need`
  - 若没有，就继续新的 `paper / repo based 5m / 15m crypto` fresh intake

## 最小验证
已执行并通过：
1. `python3 scripts/build_vol_regime_midband_clean_replication.py`
2. 校验以下 artifact 已写出：
   - `reports/artifacts/scout_vol_regime_midband_15m/clean_replication_summary.csv`
   - `reports/artifacts/scout_vol_regime_midband_15m/parameter_stability.csv`
   - `reports/artifacts/scout_vol_regime_midband_15m/cost_trade_stability.csv`
   - `reports/site/factors/scout_vol_regime_midband_15m/report.html`
3. 校验 `docs/TODO.md` 已同步写入：
   - `Rank 23 ... hard verdict = park / evidence pool`
   - 顶部 authoritative override 已不再把 `Rank 23` 写成 pending clean replication
4. 校验 shortlist 已把 `Rank 23` 更新为 `clean replication + Light Stability Pack 已完成`

## 失败 / 修复
- 新脚本第一跑失败一次：`build_vol_gate_signals() got an unexpected keyword argument 'label'`
- 原因：参数邻域配置把 `label` 一并传入了执行函数
- 修复：在参数循环里剔除 `label` 字段后重跑
- 这次失败只影响脚本执行，不影响研究结论；修复后已正常产出完整 artifact

## 风险 / 边界
- 这轮没有追最新 bar，也没有扩样本或下载新数据
- 这轮只验证了 `baseline + vol gate` 这类最小 clean-room 变体；它不等于对更复杂 regime 结构做了总否定
- 但就当前 `Scout Seat` 的预算与标准而言，`Rank 23` 已经足够诚实地被压回 `park`

## 网页可见落点
- `reports/site/factors/scout_vol_regime_midband_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`
- 首页索引将在本轮结尾刷新

## Git / 提交
- 本轮未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit
