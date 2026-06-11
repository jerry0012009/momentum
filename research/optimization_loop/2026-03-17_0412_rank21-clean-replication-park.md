# 2026-03-17 04:12 UTC · Rank 21 clean replication + Light Stability Pack 完成并压回 park

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查席位：
  - `Paper Seat = EMA`，当前是 `waiting_not_due`；
  - `Live Seat = 暂空`；
  - 默认顺序应落到 `Run 2 / Scout Fast Lane`。
- 先比较 active Scout 候选边际价值：
  - `Rank 2`、`Rank 17` 已是 `narrow paper pilot approved`，当前没有真实 `append/review need`；
  - `Rank 7~20` 已基本给出 `park` 结论；
  - `Rank 21` 上一轮仅完成 `source intake + clean-room spec`，还缺最关键的 `clean replication + Light Stability Pack` 三选一 verdict。
- 因此本轮主点固定为：**把 Rank 21 从 spec 推进到 hard verdict（paper candidate / park 二选一）**。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 21 market risk-on/off regime gate` 的 `clean replication + Light Stability Pack`。
- 紧邻子点：把结论写回 `docs/TODO.md` 顶部作战板（Next 3 runs + 2n 条目），避免只留日志。

## 做了什么
### 1) 新增并执行 clean replication 脚本（可部署产物）
- 新增脚本：
  - `scripts/build_market_risk_onoff_clean_replication.py`
- 该脚本直接复用本地现有 `Binance 120d 15m` cache 与 repo 信号模块：
  - `momentum.signals.market_risk_on_off_filter`
- 一次跑完四档最小对照：
  - `baseline_mtf`
  - `trend_only_gate`
  - `market_risk_2of3`
  - `market_risk_3of3`
- 一次补齐 Light Stability Pack 四项：
  - 时间稳定性
  - 参数稳定性
  - 跨标的稳定性
  - 成本 / 交易数稳定性

### 2) 产出 artifacts + 网页可见落点
写出：
- `reports/artifacts/scout_market_risk_onoff_15m/clean_replication_summary.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/clean_replication_asset_summary.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/time_stability.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/parameter_stability.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/cross_asset_stability.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/cost_trade_stability.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/paper_candidate_admission_memo.csv`
- `reports/artifacts/scout_market_risk_onoff_15m/clean_replication_meta.csv`
- `reports/site/factors/scout_market_risk_onoff_15m/report.html`

### 3) 作战板写回（reader-facing 变化）
更新：
- `docs/TODO.md`
  - `Next 3 bot3 runs` 顶部窗口排班改为：`Rank 21` 已完成快筛并压回 `park`，下一轮默认继续 fresh intake。
  - `2n` 条目改为已完成 `clean replication + Light Stability Pack`，并写入硬结论与关键数值证据。

## 核心证据（hard verdict）
候选：`Rank 21 market risk-on/off regime gate`

主变体：`market_risk_2of3`
- `6bps/side`：`mean_total_return ≈ -25.01%`，`positive_asset_ratio = 0/3`，`mean_trades ≈ 265.0`，`mean_no_trade_ratio ≈ 51.29%`
- `10bps/side`：`≈ -39.22%`
- `15bps/side`：`≈ -53.14%`
- 时间稳定性：`0/3` bucket 为正
- 参数稳定性：最佳邻域 `trend0.5_ema24_q90_2of3` 仍仅 `≈ -17.06%`

对照补充：
- `baseline_mtf @6bps ≈ -38.69%`
- `trend_only_gate @6bps ≈ -21.34%`
- `market_risk_3of3 @6bps ≈ -25.94%`（虽然 `positive_asset_ratio=1/3`，但总体仍负且 no-trade 更高）

## 本轮 hard verdict
**Rank 21 当前更诚实的 desk 读法是 `park / evidence pool`，不进入 `paper candidate pool`。**

原因：
1. 主变体在 6bps 仍显著为负；
2. 跨标的没有达到最小正向覆盖；
3. 成本抬升后继续恶化；
4. 时间与参数两项稳定性都没有出现可升格 pocket。

## 最小验证
已执行：
1. `python3 -m py_compile scripts/build_market_risk_onoff_clean_replication.py`
2. `python3 scripts/build_market_risk_onoff_clean_replication.py`
3. 校验 `clean_replication_meta.csv` 与 `paper_candidate_admission_memo.csv` 中 verdict 一致为 `park / evidence pool`
4. 校验 `docs/TODO.md` 已写入 `Rank 21` 的 clean replication 完成与 park 结论

## 风险 / 边界
- 本轮只使用固定 `BTC/ETH/SOL 120d 15m` 历史样本，不代表更长周期下永久结论；
- 但按当前 Scout 快筛预算规则，已经足够给出 `park` 并释放主资源；
- 后续除非 bot2 明确点名重开，否则不应继续占默认主资源。

## 下一步建议
1. `EMA` 继续 `waiting_not_due` 时，Scout 默认继续新的 `paper/repo based 5m/15m crypto` fresh intake；
2. `Rank 2 / Rank 17` 仅在出现真实 `append/review need` 或 genuinely verdict-changing check 时回补；
3. 不再围绕 `Rank 21` 追加近义 closeout 文档。

## Git / 提交
- 本轮未提交。
- 原因：当前工作区存在大量与本轮无关脏文件/未跟踪文件，避免混提。
