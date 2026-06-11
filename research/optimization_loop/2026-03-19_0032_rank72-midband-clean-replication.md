# Rank 72 / realized-vol mid-band 成本生存门最小 clean replication

## 为什么这轮选这个
- `Run 1 / EMA due-check` 先核对后仍是 **`waiting_not_due`**：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示全 desk 当前没有 `due-now / overdue` lane，最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`。
- `P3 continuity` 也没有新的状态变化：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T00:05:52Z` 仍是 `new_closed_trades_appended=0`。
- 因此本轮不能回头磨 `EMA` 或 `P3`。按顶板最新 `Next 3`，合法主动作就是 **`Run 2 / Rank 72 minimal clean replication`**。
- `Rank 72` 已在上一轮完成 `source intake + 两条轻量诚实守门`，而且它是 shared allow/deny gate，边际价值高于继续磨旧 rank 或直接掉到 tiny-live。

## 这轮做了什么
1. 新增脚本：
   - `scripts/build_rank72_realized_vol_midband_clean_replication.py`
2. 用现有 `BTC/ETH/SOL 120d 15m` cache 做最小复刻：
   - archetype：`ema_psar_long / fib_retest_long / breakout_short`
   - variants：`baseline / no_high_vol_extreme / rv_midband_q20_80`
   - 执行口径：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
   - 成本：`6 / 10 / 15 bps per side`
3. 生成本轮 artifact：
   - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/per_asset_summary.csv`
   - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/window_summary.csv`
   - `reports/artifacts/scout_rank72_realized_vol_midband_cost_survival_15m/trades.csv`
4. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank72_realized_vol_midband_cost_survival_15m/report.html`
   - `reports/site/reading/repo_scout/rank72_realized_vol_midband_cost_survival_clean_replication.html`
5. 刷新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把 `Rank 72` 的 hard verdict 写回到交易台。

## 核心证据
### 6bps/side 主读法：`rv_midband_q20_80`
- `ema_psar_long`
  - `mean_total_return ≈ +1.78%`
  - `trade_count_retention ≈ 21.49%`
  - `failure_before_target ≈ 67.82%`
  - 对照 baseline：`return ≈ -4.11%`
- `fib_retest_long`
  - `mean_total_return ≈ -1.22%`
  - `trade_count_retention ≈ 21.90%`
  - `failure_before_target ≈ 52.78%`
  - 对照 baseline：`return ≈ -0.22%`
- `breakout_short`
  - `mean_total_return ≈ -2.53%`
  - `trade_count_retention ≈ 17.76%`
  - `failure_before_target ≈ 70.71%`
  - 对照 baseline：`return ≈ -3.36%`

### 这组结果最诚实的读法
- 它不是“shared vol gate 通过了”，而是：
  - **EMA 那一条看起来改善了，但主要代价是交易数被砍到只剩约 1/5；**
  - `Fib` 没被救活；
  - `breakout_short` 也仍是负值；
  - 作为 shared allow/deny gate，它没有展示出足够统一、可迁移的 desk 级价值。
- `no_high_vol_extreme` 版本虽然比中位带略温和，但也同样存在“改善主要靠砍单”的问题，没把这条线救到值得升格的程度。

## Hard verdict
**`Rank 72 / realized-vol mid-band cost-survival gate = park / evidence pool`**

## 为什么是这个 verdict
- 这轮最关键的 blocker 不是方向错，而是 **retention 太低**：
  - `ema_psar_long` 留下来的单子只剩约 `21.49%`
  - `fib_retest_long` 只剩约 `21.90%`
  - `breakout_short` 只剩约 `17.76%`
- 这意味着它当前更像一种“强砍交易数的样本裁剪器”，而不是一个可以共享服务三条主线的诚实生存门。
- 如果一个 shared gate 只能在单条 setup 上、靠大幅缩样本，换来一点点表面改善，那它不该继续占默认 Scout 预算。

## 对交易台的影响
- `Rank 72` 的那次允许预算已用完，应压回 `park / evidence pool`。
- 当前更诚实的 `Next 3`：
  - `Run 1 = EMA due-check only`
  - `Run 2 = Rank 73 / PSAR close-confirmed follow-up gate source intake + 两条轻量诚实守门`
  - `Run 3 = 只有 fresh source 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 最小验证
- 已实际运行：
  - `python3 /root/clawd/jerry/momentum/scripts/build_rank72_realized_vol_midband_clean_replication.py`
- 已确认输出文件存在：
  - `reports/site/factors/scout_rank72_realized_vol_midband_cost_survival_15m/report.html`
  - `reports/site/reading/repo_scout/rank72_realized_vol_midband_cost_survival_clean_replication.html`
- 已确认 `TODO.md` 顶板写回成功。

## 风险 / 边界
- 这轮只用了本地现成 `120d 15m` cache，不是更长样本；但当前 desk 规则下，这已经足够回答“值不值得继续给预算”。
- `failure_before_target` 的定义是最小诚实代理，不是论文原始 regime 标签复刻。
- 结论针对的是 **shared gate 的 desk 价值**，不是说 realized vol 永远没用；只是说这版 `mid-band` 口径当前不值得升格。

## 下一步建议
- 不要继续磨 `Rank 72` 的 wording 或补近义说明页。
- 按顶板直接切到 **`Rank 73 / PSAR close-confirmed follow-up gate`** 做 fresh source intake。

## Commit hash
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
