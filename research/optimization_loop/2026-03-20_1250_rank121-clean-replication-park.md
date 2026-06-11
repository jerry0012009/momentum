# 2026-03-20 12:50 UTC · Rank 121 / PSAR trailing role fail-safe / clean replication park

## 为什么这次选这个
- 这轮先按 desk 规则实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`。
- 结果继续如实返回：`Paper Seat / EMA = waiting_not_due`；最近 due 仍是美股约 `7.2h`、Crypto 约 `11.2h`、创业板ETF 约 `66.2h`。
- 因此本轮不能继续磨 `EMA`，也不能插队回头做 hosted `P3 continuity`；按 `docs/TODO.md` 顶部当前 `Next 3`，合法主动作就是 **`Rank 121 / PSAR trailing role fail-safe` 的 1 次最小 clean replication**。

## 这轮做了什么
### 1) 先做 Run 1 due-check
已再次实际运行：

```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

结论没有变化：当前全 desk 仍是 `waiting_not_due`，没有新的 `due-now / overdue` lane。

### 2) 对 Rank 121 做最小 clean replication
新增脚本：
- `scripts/build_rank121_psar_trailing_role_clean_replication.py`

本轮把这条线严格收在它自己承诺的最小 clean-room：
- 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache
- 只挂 **`fib_retest_long`** 一个 archetype
- 执行统一为 **`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**
- baseline 继续保留 `fib50_fail`
- 只比较三臂：
  1. `baseline exit`
  2. `immediate PSAR trailing`
  3. `handoff→PSAR`（训练段只允许从 `handoff_bars ∈ {2,3,4}` 中冻结一档，再去测试段验证）

训练段最后三币都只冻结到：
- `handoff_bars = 2`

### 3) 生成 reader-facing 落点
- `reports/artifacts/scout_rank121_psar_trailing_role_fail_safe_15m/overall_summary.csv`
- `reports/artifacts/scout_rank121_psar_trailing_role_fail_safe_15m/asset_summary.csv`
- `reports/artifacts/scout_rank121_psar_trailing_role_fail_safe_15m/train_handoff_grid.csv`
- `reports/site/factors/scout_rank121_psar_trailing_role_fail_safe_15m/report.html`
- `reports/site/reading/repo_scout/rank121_psar_trailing_role_fail_safe_clean_replication.html`

### 4) 同步顶板
已把 `docs/TODO.md` 顶部最新补充更新为：
- `Rank 121` 本轮 clean replication 后直接收口为 `P0 / park / evidence pool`
- 当前 `Run 2` 主点已耗尽
- 当前 `Next 3` 回到：`Run 1 = EMA due-check first -> Run 2 = 承认 Rank 121 已 park，不再继续给旧候选预算 -> Run 3 = tiny-live plumbing fallback`

## 验证 / 证据
### 聚合结果（测试段，`6bps/side`）
- `baseline`：`mean_total_return ≈ -0.09%`，`trade_retention = 100%`，`median_hold ≈ 5.3 bars`
- `immediate PSAR`：`mean_total_return ≈ -0.08%`，`trade_retention = 100%`，`median_hold ≈ 5.3 bars`
- `handoff→PSAR`：`mean_total_return ≈ -0.08%`，`trade_retention = 100%`，`median_hold ≈ 5.3 bars`

### 分资产读法
- `BTC`：`baseline ≈ -0.21% -> PSAR ≈ -0.16%`，有一点减亏
- `ETH`：三臂几乎完全等价（都约 `-0.21%`）
- `SOL`：三臂也几乎完全等价（都约 `+0.13%`）

### 最关键的诚实结论
这轮真正把 `Rank 121` 判掉的，不是“PSAR 完全没用”，而是：
- `handoff→PSAR` 与 `immediate PSAR` 在测试段的 `trade_count / hold / exit mix` 基本一样；
- 也就是说，这轮 clean replication **没有给出“延迟接手”比“立即接手”更有信息量的证据**；
- 当前小幅改善更像局部样本差，而不是一个足够硬、可继续申请 `Light Stability Pack` 的 role uplift。

## 本轮硬结论
**`Rank 121 / PSAR trailing role fail-safe = P0 / park / evidence pool`**。

翻成人话：
- PSAR trailing 这条线当前不该再占 `Scout Seat` 预算；
- 它没有被证明成一个更诚实的 delayed handoff fail-safe；
- 更不配被 shared 化成默认 exit engine。

## 风险 / 边界
- 这轮只验证了 `fib_retest_long` clean-room，不是 desk 全策略总判决。
- 当前结果只能说明：**在这条 archetype 上，Rank 121 不值得继续花预算**；不能反推出“PSAR 在任何地方都没价值”。
- repo 仍有大量与本轮无关的既有脏文件，不适合混提。

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - 当前 board 下先承认 `Rank 121` 已 park
  - 本轮之后默认转去 `tiny-live plumbing fallback`
  - 只有后续 bot2 明确把新的 fresh intake 写回顶板时，才重新打开新的 `Scout Seat` 主点

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 121` 直接相关的最小文件，不适合混提。
