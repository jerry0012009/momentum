# 2026-03-17 06:10 UTC · Rank 25 EMA+Donchian 快筛并升入 P2

## 为什么这轮选这个
- 先读 `TRADING DESK BOARD`：
  - `Paper Seat / EMA` 当前是 `waiting_not_due`；
  - `Live Seat` 仍空；
  - 所以按顺序落到 `Run 2 / Scout Seat`。
- 先比较 active Scout 候选边际价值：
  - `Rank 17 / Rank 2` 都是 `P3`，本轮未出现新的真实 `append/review` 缺口；
  - `Rank 7` 的唯一 cheap honesty recheck 已做完并压回 park；
  - 因此应转 `fresh paper/repo based 5m/15m crypto intake`。
- 本轮只认领 1 条新线：`Rank 25 EMA + Donchian breakout confirmation`（repo + 信号文档可对照）。

## 本轮主点 + 紧邻子点
- 主点：完成 `Rank 25` 的 `source intake -> clean replication -> Light Stability Pack -> verdict` 闭环。
- 紧邻子点：将 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 与 `Run 2` 排班更新到最新状态，明确该候选当前是 `P2 / time-stability red-watch`。

## 做了什么
### 1) 新增可部署脚本与产物
新增脚本：
- `scripts/build_ema_donchian_scout_clean_replication.py`

基于现有缓存（不追新 bar、不下载新数据）生成：
- `reports/artifacts/scout_ema_donchian_breakout_15m/clean_room_spec_v1.csv`
- `.../clean_replication_summary.csv`
- `.../clean_replication_asset_summary.csv`
- `.../clean_replication_trades.csv`
- `.../time_stability.csv`
- `.../parameter_stability.csv`
- `.../cross_asset_stability.csv`
- `.../cost_trade_stability.csv`
- `.../paper_candidate_admission_memo.csv`
- `.../clean_replication_meta.csv`

网页可见落点：
- `reports/site/factors/scout_ema_donchian_breakout_15m/report.html`

### 2) 快筛口径（先硬门槛）
- 规则可清楚写成 `trade on / trade off`：
  - trade on = `1h EMA bias` 同向 + `Donchian breakout` 连续 3 根收盘确认；
  - trade off = 任一条件缺失，或反向信号 / ATR stop 触发。
- 无明显 lookahead/repaint/data leakage：
  - Donchian 上下轨使用 `shift(1)`，信号执行使用“上一根收盘信号、下一根开盘执行”的因果顺序。

### 3) Light Stability Pack（4 项）
- 时间稳定性：
  - 3 资产都呈 `bucket_1负 / bucket_2正 / bucket_3负`，正收益 bucket 仅 `3/9`（red-watch）。
- 参数稳定性：
  - 邻域 `lookback=20/30/40 × confirm=2/3` 中，`l30_c3 / l40_c3` 为正 pocket，`confirm=2` 组合普遍偏弱。
- 跨标的稳定性：
  - 主变体 `ema_donchian_l30_c3` 在 6bps 下 `positive_asset_ratio=3/3`。
- 成本/交易数稳定性：
  - 6/10/15/20 bps 下聚合回报仍保持正值（约 `+16.83% / +13.74% / +10.00% / +6.37%`）；
  - 平均交易数约 `33.7`，未稀疏到不可用。

## 本轮 hard verdict
- `Rank 25 EMA + Donchian breakout`：**升入 `paper candidate pool（P2）`**。
- 同时标记：**`time-stability red-watch`**（当前不直接升 `P3`）。
- 下一轮默认只允许 1 次 genuinely verdict-changing 最小检查，回答：`升 P3 / 压回 park`。

## 最小验证
已执行：
1. `python3 -m py_compile scripts/build_ema_donchian_scout_clean_replication.py`
2. `python3 scripts/build_ema_donchian_scout_clean_replication.py`
3. 检查 `paper_candidate_admission_memo.csv` 与 `clean_replication_summary.csv`
4. 检查网页落点目录：`reports/site/factors/scout_ema_donchian_breakout_15m/report.html`

## 同步更新
- 已更新 `docs/TODO.md`：
  - 顶部 `Next 3 bot3 runs` authoritative override；
  - `Run 2` 增补 `2r Rank 25` 当前 verdict 与下一步约束；
  - Scout 候选阶段表新增 `Rank 25` 条目（P2 + red-watch）。

## 风险 / 边界
- 本轮没有追最新 bar、没有重型下载、没有改动 live seat。
- 只开了 1 条 fresh Scout 候选，避免并行扩散。
- 当前最大风险是时间稳定性；若下一次最小诚实检查不能改善，应按规则压回 park。

## Git / 提交
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件/未跟踪文件，避免混提。
