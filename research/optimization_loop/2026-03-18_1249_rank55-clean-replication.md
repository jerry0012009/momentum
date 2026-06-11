# 2026-03-18 12:49 UTC — Rank 55 最小 clean replication（order-imbalance crash-risk overlay）

## 为什么这次选这个
- 先执行 `Run 1`：`ema_paper_trading_due_guardrail_snapshot.csv` 显示全 desk 仍是 `waiting_not_due`（美股 `2026-03-18 20:00 UTC`、Crypto `2026-03-19 00:00 UTC`、A股 `2026-03-19 07:00 UTC`）。
- 因此按当前 `TRADING DESK BOARD` 的 `Next 3`，本轮应执行 `Run 2 = Rank 55 minimal clean replication`。
- active Scout 边际价值仍是：`Rank 55 > Rank 35b > Rank 16b > tiny-live plumbing`，所以主资源继续给 Rank 55。

## 本轮主点（1）
### Rank 55 / order-imbalance crash-risk overlay：完成唯一那手最小 clean replication
- 新增脚本：`scripts/build_rank55_order_imbalance_crash_risk_clean_replication.py`
- 固定口径：`BTC/ETH/SOL 120d 15m`、`next-bar open + no-overlap + hold 8 bars`。
- 对三条 base archetype（`ema_psar_long` / `fib_retest_long` / `breakout_short`）比较三臂：
  - `base`
  - `binary_crash_gate`
  - `size_haircut`
- crash-risk 信号采用降级可复刻口径：setup 前最后 `5` 分钟 `aggTrades` 的 `sell pressure + flow shock`，叠 `15m downside move + realized vol` 得到 `crash_score`（只作 overlay，不当主 alpha）。

## 紧邻子点（1）
### 写回 authoritative board + reader-facing
- `docs/TODO.md` 顶部新增 `2026-03-18 12:49 UTC` 补充，写明本轮 replication 结论与下一步排班。
- reader-facing 页面：
  - `reports/site/factors/scout_rank55_order_imbalance_crash_risk_15m/report.html`
  - `reports/site/reading/repo_scout/rank55_order_imbalance_crash_risk_clean_replication.html`
- artifact：
  - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/overall_summary.csv`
  - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/setup_compare.csv`
  - `reports/artifacts/scout_rank55_order_imbalance_crash_risk_15m/asset_summary.csv`

## 验证 / 证据
- 脚本执行输出：`verdict=P1 weak candidate / evidence pool`
- `6bps/side` setup-level摘要（`setup_compare.csv`）：
  - `ema_psar_long`：`base≈+1.63%`，`binary_crash_gate≈+3.15%`，`size_haircut≈+2.40%`
  - `fib_retest_long`：`base≈+0.03%`，`binary_crash_gate≈+0.00%`，`size_haircut≈+0.02%`
  - `breakout_short`：`base≈-2.49%`，`binary_crash_gate≈-1.88%`，`size_haircut≈-2.68%`
- 结论：
  - overlay 在 `ema_psar_long` 与 `breakout_short` 上有“少亏/改善回撤”的迹象；
  - 但 `fib_retest_long` 基本无增量，跨 setup 一致性不足；
  - 目前更诚实层级是 **`P1 weak candidate / evidence pool`**，尚不足以直接升 `P2`。

## 风险 / 边界
- 这是论文思想的 desk 降级复刻（shared risk overlay），不是完整日级 crash nowcast 管线。
- 当前结果容易受样本与阈值影响，下一轮若继续应优先做 `Run 3` 指定的一次 truly verdict-changing `Light Stability Pack`（默认先时间稳定性），直接做 `P2 / park`。
- 本地存在大量与本轮无关脏文件，未做 commit，避免混提。

## 执行中遇到的真实阻塞与处理
- 首次 Rank55 clean replication 运行因 `aggTrades` 下载窗口过大导致长时间无产出（外部数据 I/O 阻塞）。
- 本轮已切换为“缓存优先 + 每 asset/setup 限定最近样本预算”的最小实现（仍保持同一 replication 口径），避免整轮空转。

## 下一步建议
1. 下一轮先继续 `Run 1 = EMA due-check only`。
2. 若仍 `waiting_not_due`，按板上规则给 `Rank 55` 仅 1 个 truly verdict-changing 的 `Light Stability Pack`（优先时间稳定性），并直接做 `P2 / park`。
3. 若该检查后仍不满足升格，按 `Run 3` 回退：`Rank 35b > Rank 16b > tiny-live plumbing`。

## Commit hash
- 未提交（工作区存在大量与本轮无关改动，当前不安全 selective commit）。
