# 2026-03-16 21:49 UTC — intraday tsmom session park

## 本轮定位
- 读取 authoritative `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 后，确认当前 `Paper Seat = EMA running paper / waiting_not_due`，因此本轮应落到 **Run 2 / Scout Fast Lane**。
- 先比较 active Scout 候选的当前边际价值：
  - `Rank 1 τ-band`：已 `park`，不再值得继续占主资源；
  - `Rank 2 combo_all`：已进入 `narrow paper pilot approved`，但当前只剩近义 wiring，可等待真实 append/review need；
  - `Rank 3` / `Rank 4`：都已 `park`；
  - 因此本轮主资源改投 **新的 paper-based 5m/15m crypto intake**，而不是继续磨 `Rank 2`。

## 开工前检查
### repo / dirty state
- `git status --short --branch` 显示工作区本来就有大量历史脏文件与未跟踪产物；本轮**只触碰**：
  - `docs/TODO.md`
  - `scripts/build_intraday_tsmom_session_first_verdict.py`
  - `reports/artifacts/scout_intraday_tsmom_session_15m/*`
  - `reports/site/factors/scout_intraday_tsmom_session_15m/report.html`
  - 本日志文件
- 因存在大量与本轮无关脏文件，**不做混提、不做 commit**。

### 最近 runs（用于避免重复劳动）
- `2026-03-16_2038_rank2-continuity-snapshot.md`
- `2026-03-16_2052_ema-due-followup-reset-to-scout.md`
- `2026-03-16_2107_rank2-refresh-history-seed.md`
- `2026-03-16_2133_scout-routing-reset.md`

### 当前席位状态
- `Paper Seat`：EMA 仍是运行中的 paper pilot，但当前 `waiting_not_due / due_soon`，不该在本轮继续空转。
- `Live Seat`：保持为空；没有新的 promoted candidate。
- `Scout Seat`：按 board 指令，优先新的 `paper / repo based 5m / 15m crypto` intake。

## 本轮主点
**新的 paper-based Scout 候选：session-aware intraday TSMOM（Li, Sakkas, Urquhart 2022）**

### source intake（规则先写清楚）
把文献里的 intraday time-series momentum 思路，收敛成适合当前 desk 的最小 clean-room 规则：
- 样本：沿用 repo 内已有 `Binance 120d 15m` cache（BTC / ETH / SOL）
- 两类 session：
  - `utc_day`（00:00 UTC 日切）
  - `funding_8h`（00/08/16 UTC，贴近 crypto 节奏）
- `trade on`：同一 session 前 2 根 15m bar 收益方向明确，且 `|lead_ret|` 超过分位阈值（q50 / q60 / q70）
- `trade off`：方向为 flat，或绝对幅度不够，则 no-trade
- 执行：交易同一 session 最后 2 根 15m bar 的方向
- 诚实边界：只使用 session 前段收益做 signal，尾段执行；不追最新 bar，不引入未来信息

### clean replication
新增脚本：
- `scripts/build_intraday_tsmom_session_first_verdict.py`

产物落点：
- `reports/artifacts/scout_intraday_tsmom_session_15m/variant_aggregate.csv`
- `reports/artifacts/scout_intraday_tsmom_session_15m/asset_summary.csv`
- `reports/artifacts/scout_intraday_tsmom_session_15m/time_stability_drycheck.csv`
- `reports/artifacts/scout_intraday_tsmom_session_15m/parameter_stability_drycheck.csv`
- `reports/artifacts/scout_intraday_tsmom_session_15m/cross_asset_stability_drycheck.csv`
- `reports/artifacts/scout_intraday_tsmom_session_15m/cost_trade_stability_drycheck.csv`
- `reports/site/factors/scout_intraday_tsmom_session_15m/report.html`

## 结果（hard verdict）
### primary verdict
- reader-facing primary 选 `funding_8h_q60`（比 UTC 日切更贴近 crypto）
- 结果：**`park / evidence pool`，不进入 `paper candidate pool`**

### 关键数字
- `funding_8h_q60 @ 6bps/side`
  - `mean_total_return = -22.74%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades = 145`
  - `mean_direction_hit_rate = 42.53%`
- per-asset：
  - `BTC = -20.65%`
  - `ETH = -23.93%`
  - `SOL = -23.64%`
- 全部 6bps variants 里相对最不差的是 `utc_day_q70`，但也仅为 `mean_total_return = -6.35%`，仍明显不够。

## Light Stability Pack
### 1) 时间稳定性
- `positive_bucket_floor`：**fail**（`0/3 positive buckets`）
- `bucket_trade_floor`：pass（最少 bucket trades 充足）
- `worst_bucket_watch`：watch（最差 bucket 平均回报约 `-10.22%`）

### 2) 参数稳定性
- `neighbor_positive_floor`：**fail**（`0/3 funding-threshold neighbors positive`）
- `neighbor_trade_floor`：pass
- `worst_neighbor_watch`：watch（最差邻域约 `-26.77%`）

### 3) 跨标的稳定性
- `positive_asset_floor`：**fail**（`0/3 assets positive`）
- `min_trade_floor`：pass
- `worst_asset_watch`：watch（`ETH = -23.93%`）

### 4) 成本 / 交易数稳定性
- `cost_survival_floor`：**fail**（`0/4 cost levels positive`）
- `trade_count_floor`：pass（交易数够，不是样本稀疏问题）
- `20bps_watch`：watch（`-48.55%`）

## 结论
- 这条线不是“证据不够”，而是当前 **clean replication 本身就偏负且四项稳定性一起 fail**。
- 因此本轮最诚实的 desk 结论不是继续写 paper wiring，而是：
  - 把它记为 **新的 Rank 5 Scout 候选，但状态直接定为 `park`**；
  - 不进入 `paper candidate pool`；
  - 不继续占用下一轮 Scout 主资源，除非后续出现更强的 session spec 或新的外部 repo / 数据证据。

## 本轮附带同步
- 已更新 `docs/TODO.md` 的 `Scout Seat` 候选阶段表，加入：
  - `Rank 5 session-aware intraday TSMOM` → `park`
- 已新增 reader-facing 页面：
  - `reports/site/factors/scout_intraday_tsmom_session_15m/report.html`

## 最小验证
- 运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_intraday_tsmom_session_first_verdict.py`
- 成功生成 artifact 与网页页签，无需重型下载。

## 下一轮建议（不是本轮继续做）
- 仍按当前 board：优先继续找**新的** `paper / repo based 5m / 15m crypto` 候选；
- 默认不要回去给 `Rank 2` 继续补近义 paper wiring，除非出现真实 `append-ready refresh/review` need 或 verdict-changing minimal check。
