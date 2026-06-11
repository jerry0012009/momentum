# 2026-03-19 07:30 UTC — Rank 82 ETF lead regime 最小 clean replication（keep P1）

## 为什么这轮认领这个
- 先执行 `Run 1`：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前无 `due-now / overdue`，仍是 `waiting_not_due`（脚本按 guardrail 返回等待，不伪造 refresh）。
- 按 `TRADING DESK BOARD` 当前 `Next 3`，合法主动作切到 `Run 2`：
  - `Rank 82 / ETF lead regime gate minimal clean replication`。
- 本轮只做 1 个主点（Rank 82 clean replication），未并行开新候选。

## 本轮做了什么（主点）
- 新增脚本：
  - `scripts/build_rank82_etf_lead_clean_replication.py`
- 冻结口径并执行最小 clean replication：
  - 基础信号：复用本地 `BTC/ETH/SOL 120d 15m`（`ema_psar_long / fib_retest_long / breakout_short`）
  - ETF 特征：实时拉取 `IBIT/FBTC/GBTC 60d 5m`（Yahoo），构建
    - `lead_edge_3bars`
    - `impulse_z`
    - `volume_z`
  - 三臂比较：`baseline / regime_filter / regime_sizing`
  - 执行统一：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 产物落盘：
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/by_setup_summary.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/per_asset_setup_summary.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/etf_5m_raw.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/etf_5m_feature_panel.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/etf_regime_feature_snapshot.csv`
  - `reports/artifacts/scout_rank82_etf_lead_regime_15m/trade_samples.csv`
- reader-facing 页面：
  - `reports/site/factors/scout_rank82_etf_lead_regime_15m/report.html`
  - `reports/site/reading/repo_scout/rank82_etf_lead_regime_clean_replication.html`
- 指挥板同步：
  - `docs/TODO.md` 中 Rank 82 分级与 `Next 3 bot3 runs` 已更新到 clean replication 后状态。

## 核心结果（6bps/side）
- `baseline`：
  - `mean_total_return ≈ -2.00%`
  - `mean_expectancy ≈ -0.065%`
  - `mean_early_fail_rate ≈ 27.25%`
- `regime_filter`（严格筛选）：
  - `mean_total_return ≈ -0.69%`（明显减亏）
  - 但 `mean_trade_count_retention ≈ 20.65%`（砍单过重）
- `regime_sizing`（冲突时半仓）：
  - `mean_total_return ≈ -1.77%`
  - `mean_expectancy ≈ -0.051%`
  - `positive_cell_ratio: 33.3% -> 44.4%`
  - `mean_avg_size ≈ 0.76x`
  - 但 `mean_early_fail_rate` 基本未改善（仍约 `27.25%`）

## Hard verdict
- **`Rank 82 = keep_P1 / evidence_pool`**

一句话：ETF 先行强度有信息，但当前更像“共享 gate 线索”，还不够统一到可直接升 `P2`。

证据链：strict filter 虽减亏但 retention 仅 20.65%（过严）；sizing 版更诚实但仅小幅改进总收益/expectancy，且未降低 early-fail，并对 `ema_psar_long / fib_retest_long` 仍有稀释。

## 对当前排班的影响（Next 3）
- `Run 1 = EMA due-check only（若仍 waiting_not_due，不得空转）`
- `Run 2 = 若 Rank 82 仍值得继续，只允许 1 个 truly verdict-changing 最小检查；否则切 Rank 83 source intake`
- `Run 3 = volume-price interaction admission layer > 其他 fresh source`
- `P3 continuity` 继续仅低频 sidecar，不抢默认 Scout 主资源。

## 验证 / 边界
- 已执行最小必要验证：
  - `python3 scripts/build_rank82_etf_lead_clean_replication.py` 成功。
  - 读回 CSV 与页面确认落盘。
- 数据边界：Yahoo ETF 5m 可得窗口是 `60d`，本轮如实按 60d 做最小 replication，不伪装为 120d ETF 回填。

## 风险与下一步
- 风险：ETF 版 strict filter 对 trade count 削减过重，容易产生“看起来好但不可执行”的错觉。
- 下步建议（若继续 Rank 82）：只允许做 1 个真正改变 verdict 的最小检查（例如 setup-specific gating：仅对 breakout_short 启用 ETF gate，避免稀释 fib/ema lane），做完即 `升格或park`，不再循环文案打磨。

## Git / 提交
- 工作区存在大量与本轮无关脏文件；本轮未做 commit，避免混提。
