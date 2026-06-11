# 2026-03-18 05:08 UTC — OI participation gate clean replication 后压回 park

## 为什么这次选这个
- 先按顶板重读 `Run 1 -> Run 2 -> Run 3`：
  - `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**；最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示 A 股三条 lane `-> 2026-03-18 07:00 UTC`、美股 `-> 2026-03-18 20:00 UTC`、Crypto `-> 2026-03-19 00:00 UTC`，没有新的 `due-now / overdue` bar。
  - 因此当前主资源应落到 `Run 2 / Scout Seat`。
- 上一轮 `Rank 46 / OI participation gate` 已完成 `source intake + 两条轻量诚实守门`，而且它是当时 active Scout 候选里边际价值最高的一条：
  - 比 `Rank 47 / EMA-ADX-VOL skeleton` 更窄；
  - 不重写 entry，只先回答 `OI > OI-SMA20` 能不能在 **不明显砍样本** 的前提下压低 `2~4 bar whipsaw`；
  - 比继续磨已 park 线或挤占 `P3 continuity` 更贴当前 desk 主线。
- 本轮按规则只认领 **1 个主点**：把这条线的唯一那手 **最小 clean replication** 做完，并给出 hard verdict。

## 做了什么改动
### 主点：完成 `Rank 46 / OI participation gate` 最小 clean replication
- 新增脚本：
  - `scripts/build_repo_ema_oi_participation_clean_replication.py`
- 新增 artifact：
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/overall_summary.csv`
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/asset_summary.csv`
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/time_stability_summary.csv`
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/sample_meta.csv`
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/trade_log.csv`
  - `reports/artifacts/scout_repo_ema_oi_participation_15m/oi_cache/*.csv`
- 新增网页落点：
  - `reports/site/factors/scout_repo_ema_oi_participation_15m/report.html`

### 紧邻子点：同步 authoritative board
- 最小改写 `docs/TODO.md` 顶部 authoritative 板：
  - 补记 `2026-03-18 05:08 UTC` 的 clean replication 结果；
  - 把 `Rank 46 / OI participation gate` 更新为 **预算用尽后压回 `park / evidence pool`**；
  - 同步把 `Next 3 bot3 runs` 重置为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = EMA-ADX-VOL skeleton`
    - `Run 3 = Rank 35b / tiny-live plumbing`
- 同时核对 `Rank 32b` 的本次 closed-trade append 已经在：
  - `manual_narrow_paper_status.csv`
  - `manual_narrow_paper_closed_trades.csv`
  - `manual_narrow_paper_last_run_summary.json`
  中完整外显，因此本轮不再额外补一轮近义 writeback。

## 验证 / 证据
### 1）EMA 仍是 waiting_not_due
- 读取 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：
  - 创业板ETF / 贵州茅台 / 沪深300ETF 下一次 close = `2026-03-18 07:00 UTC`
  - 美股 = `2026-03-18 20:00 UTC`
  - Crypto = `2026-03-19 00:00 UTC`
- 结论：当前 `Run 1` 只有 due-check，没有真实 refresh 动作。

### 2）最小 clean replication 口径
- 资产：`BTC / ETH / SOL`
- 价格样本：复用本地 `15m` cache
- OI 数据：Binance USDⓈ-M perpetual `openInterestHist`
- 统一执行口径：`EMA9/15` 给方向，`next-bar open + no-overlap + hold 8 bars`
- 对照四臂：
  1. `ema_raw`
  2. `+oi_level_gate`
  3. `+oi_level_gate+oi_delta_gate`
  4. `+volume_fallback_gate`
- 先回答四个便宜问题：
  - `trade_count retention`
  - `2/4 bar whipsaw`
  - `4/8/12 bar follow-through`
  - `net expectancy / total return`

### 3）6bps/side 核心结果（跨资产均值）
- `ema_raw`：`mean_total_return≈-6.38%`，`positive_asset_ratio=0/3`，`mean_trades≈91.0`，`mean_whipsaw_4bars≈49.09%`
- `oi_level_gate`：`mean_total_return≈-1.83%`，`positive_asset_ratio=1/3`，`mean_trades≈46.0`，`retention≈50.58%`，`mean_whipsaw_4bars≈49.93%`
- `oi_level+delta`：`mean_total_return≈-0.26%`，`positive_asset_ratio=1/3`，`mean_trades≈29.0`，`retention≈31.93%`，`mean_whipsaw_4bars≈51.06%`
- `volume_fallback`：`mean_total_return≈11.82%`，`positive_asset_ratio=3/3`，`mean_trades≈53.7`，`retention≈58.98%`，`mean_whipsaw_4bars≈39.41%`

### 4）时间稳定性（主臂 = `oi_level_gate @ 6bps`）
- `bucket_1`：`mean_total_return≈-1.19%`，`positive_asset_ratio=1/3`
- `bucket_2`：`≈0.08%`，`positive_asset_ratio=2/3`
- `bucket_3`：`≈-0.67%`，`positive_asset_ratio=1/3`
- 结论：真 OI gate 没有形成足够干净的跨时间稳定正 pocket。

### 5）文件存在性 / 最小验证
- 已执行：`python3 scripts/build_repo_ema_oi_participation_clean_replication.py`
- 已检查：
  - `ok_html`
  - `ok_csv`

## 当前硬结论
- **`Rank 46 / OI participation gate` 当前更诚实的 hard verdict = `park / evidence pool`。**
- 直白一点说：
  - 真 `OI` gate 确实比 raw EMA 少亏；
  - 但它没有在跨资产口径下稳定转正，也没有稳定压低 `4-bar whipsaw`；
  - 真正明显更强的是 `volume_fallback`，说明这条 repo 当前更像 **volume-participation proxy**，不是可以直接升格的 `true OI` alpha。
- 因此这条线本轮预算用尽后应压回 evidence pool，不再继续占默认 Scout 主资源位。

## 风险 / 边界
- 这轮仍是 **最小 clean replication**，不是长窗 OOS，也不是 live/paper admission。
- `openInterestHist` 公开窗口有限，因此当前结果更像快筛 hard verdict，不宜被包装成长期结论。
- `volume_fallback` 更强这件事值得记住，但它已经更接近另一条候选（如 `Rank 47 / EMA-ADX-VOL skeleton`），不应把它混成这条 repo 的胜利。

## 下一步建议
1. 下一轮若 `EMA` 仍 `waiting_not_due`，默认主资源切到 **`Rank 47 / EMA-ADX-VOL skeleton`**，先做 `source intake / honesty gate`。
2. 只有 fresh repo intake 再次拿不到诚实结果，才回退到 `Rank 35b`。
3. `Rank 32b` 本次 append 已外显，不要继续补近义 continuity 文档。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，安全 selective commit 条件不够好；本轮避免混提。
