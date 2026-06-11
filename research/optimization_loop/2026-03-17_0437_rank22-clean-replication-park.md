# 2026-03-17 04:37 UTC · Rank 22 up/down wave + MA20 persistence gate clean replication + Light Stability Pack 完成并压回 park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：
  - `Paper Seat = EMA`，当前仍是 `waiting_not_due`
  - `Live Seat = 暂空`
  - 因此默认顺序应落到 `Run 2 / Scout Fast Lane`
- 先比较 active Scout 候选的边际价值：
  - `Rank 17`、`Rank 2` 都已是 `P3 / narrow paper pilot`，当前没有新的 `append/review need`
  - `Rank 7~21` 里已完成快筛的线都已回到 `park / evidence pool`
  - `Rank 22` 是当前唯一还停在 `source intake / pending clean replication` 的 active Scout 候选
- 因此本轮最诚实的主点就是：**把 Rank 22 从 intake 直接推进到 hard verdict（park / paper candidate / narrow paper pilot 三选一）**，而不是继续磨旧 P3 wiring。

## 开始前检查
- `git status --short` 显示 repo 工作区存在大量与本轮无关的历史脏文件 / 未跟踪文件；本轮只做 selective 写入，不混提。
- 最近相关 runs：
  - `2026-03-17_0416_rank22-updownwave-intake.md`
  - `2026-03-17_0412_rank21-clean-replication-park.md`
  - `2026-03-17_0334_rank17-narrow-paper-pilot.md`
- 当前 desk 状态：
  - `Paper Seat = EMA / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat = Rank 22 clean replication first`

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 22 up/down wave + MA20 persistence gate` 的 `clean replication + Light Stability Pack`
- 紧邻子点：把 verdict 写回 `docs/TODO.md` 顶部作战板，并给出 reader-facing factor 页，避免只留日志

## 做了什么
### 1) 新增并执行 clean replication 脚本（deployable artifact）
新增：
- `scripts/build_updownwave_scout_clean_replication.py`

脚本直接复用：
- 现有 `Binance 120d 15m` cache
- repo 里的 `multi_tf_momentum.py`
- repo 里的 `up_down_wave.py`
- 现有 backtest/evaluation 管线

固定规则：
- `trade on = baseline multi-tf momentum 同向 + upwave/downwave 成立`
- `trade off = baseline 消失或对应 wave 不成立`
- 执行方式：统一 `t+1` 开盘执行，不追新 bar，不下载新数据

### 2) 一次跑完 clean replication + Light Stability Pack 四项
本轮完成：
- 时间稳定性
- 参数稳定性（`MA15 / MA20 / MA25 / MA30` 邻域）
- 跨标的稳定性（`BTC / ETH / SOL`）
- 成本 / 交易数稳定性（`6 / 10 / 15 / 20 bps per side`）

### 3) 产出 artifacts + 网页可见落点
写出：
- `reports/artifacts/scout_updownwave_persistence_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/clean_replication_summary.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/clean_replication_asset_summary.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/clean_replication_trades.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/time_stability.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/parameter_stability.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/cross_asset_stability.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/cost_trade_stability.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/paper_candidate_admission_memo.csv`
- `reports/artifacts/scout_updownwave_persistence_15m/clean_replication_meta.csv`
- `reports/site/factors/scout_updownwave_persistence_15m/report.html`

### 4) 作战板写回
更新：
- `docs/TODO.md`

同步内容：
- 顶部 authoritative override 改为：`Rank 22` 已完成 clean replication + Light Stability Pack 并回到 `park / evidence pool`
- `2o` 条目从 `fresh intake accepted / pending clean replication` 改为已完成快筛并给出硬结论

## 核心证据（hard verdict）
候选：`Rank 22 up/down wave + MA20 persistence gate`

### 主变体：`updownwave_ma20`
- `6bps/side`：`mean_total_return ≈ -7.94%`
- `positive_asset_ratio = 1/3`
- `mean_trades ≈ 297.0`
- `mean_no_trade_ratio ≈ 81.41%`
- `mean_gate_pass_ratio ≈ 18.59%`

### 基线对照：`baseline_mtf`
- `6bps/side ≈ -38.69%`
- 说明 persistence gate 的确减少了亏损和交易密度，但**仍没有把策略带到可 admission 的正侧**

### 参数稳定性
- `MA15 ≈ -3.26%`（邻域里最不差）
- `MA20 ≈ -7.94%`
- `MA25 ≈ -12.02%`
- `MA30 ≈ -14.91%`
- 即便把参数往邻域里最有利的方向挪，仍然没有出现足够诚实的正收益 pocket

### 时间稳定性（主变体 MA20）
- `bucket_1 ≈ +0.23%`
- `bucket_2 ≈ -12.70%`
- `bucket_3 ≈ -0.30%`
- 时间上没有形成稳定的正向覆盖，中段 bucket 明显失守

### 跨标的稳定性（主变体 MA20）
- `BTC ≈ -14.05%`
- `ETH ≈ -18.92%`
- `SOL ≈ +9.15%`
- 当前只剩 `SOL` 单腿为正，不足以支撑 admission

### 成本 / 交易数稳定性（主变体 MA20）
- `10bps/side ≈ -27.51%`
- `15bps/side ≈ -46.17%`
- `20bps/side ≈ -59.98%`
- 交易数不变，但成本上升后快速恶化，说明 edge 不够厚

## 本轮 hard verdict
**Rank 22 当前更诚实的 desk 读法是 `park / evidence pool`，不进入 `paper candidate pool`。**

原因：
1. intake 原始 `MA20` 版本在 `6bps/side` 下仍显著为负
2. 参数邻域里最不差的 `MA15` 也只是少亏，不是通过 admission 的证据
3. 跨标的只剩 `1/3` 为正，不能支撑 paper candidate
4. 成本抬升后继续线性恶化，说明当前信号更像是“减亏过滤器”，不是足够强的可部署候选

## 对 desk 的意义
- 这轮把 `Rank 22` 从研究态推进成了**明确的否决结论**，释放了 Scout 主资源
- 也让顶板更干净：
  - 当前 active 的高优先级 Scout 不再是假活跃的 `Rank 22`
  - 只剩真实存活的 `P3`（`Rank 17 ETH+SOL-only`、`Rank 2`）以及下一条待 intake 的 fresh candidate
- 换句话说，这轮交付不是“多一页说明”，而是**减少了一条还没定性的 active 线**

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_updownwave_scout_clean_replication.py`
2. `python3 scripts/build_updownwave_scout_clean_replication.py`
3. 校验以下 artifacts 已写出：
   - `clean_replication_meta.csv`
   - `paper_candidate_admission_memo.csv`
   - `reports/site/factors/scout_updownwave_persistence_15m/report.html`
4. 校验 `docs/TODO.md` 已写入：
   - `Rank 22 ... park / evidence pool`
   - 顶部 authoritative override 已包含 `Rank 22`

## 风险 / 边界
- 本轮只使用固定 `BTC/ETH/SOL 120d 15m` 历史样本，不代表更长周期下的永久结论
- 但按当前 Scout 快筛预算，这已经足够给出 `park`
- 后续除非 bot2 明确点名重开，或引入新的 market / timeframe / execution framing，否则不应继续占默认主资源

## 下一步建议
1. 若下一轮 `Paper Seat` 仍是 `waiting_not_due`，Scout 默认回到新的 `paper / repo based 5m / 15m crypto` fresh intake
2. `Rank 17 / Rank 2` 仅在出现真实 `append/review need` 或 genuinely verdict-changing check 时回补
3. 不要再把 `Rank 22` 留在“看起来还活着”的 pending 状态

## 网页可见落点
- `reports/site/factors/scout_updownwave_persistence_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`
- 首页索引将在本轮结尾刷新

## Git / 提交
- 本轮未提交
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit
