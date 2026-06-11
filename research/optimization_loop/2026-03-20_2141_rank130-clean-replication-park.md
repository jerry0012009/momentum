# Rank 130 / cross-market leader impulse nonlinear gate clean replication → park

## 为什么这次选这个
- 先按 desk 规则执行了 `Run 1 / EMA due-check first`：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 再次如实返回 `EMA = waiting_not_due`，当前没有新的 `due-now / overdue` lane；最近 due 仍是 `Crypto 1d+1wk`，约 `2.4` 小时后到点。
- 同时核对了当前 desk 顶板：`2026-03-20 21:23 UTC` 已把 **`Rank 130 / cross-market leader impulse nonlinear gate`** 冻结为 `P1 / guard-passed / minimal clean replication next`，所以这轮合法主动作只能是它的那 **1 次最小 clean replication**。
- 旧 `P1`（`Rank 127 / 125 / 112 / 111`）都已经是 `budget used / evidence_pool`，不该回头续磨；`P3` hosted continuity 这轮也没有新的 status-changing event 可以插队。

## 做了什么改动
1. 新增最小 clean-room 脚本：
   - `scripts/build_rank130_crossmarket_leader_impulse_clean_replication.py`
2. 生成本轮 artifact：
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/overall_summary.csv`
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/setup_summary.csv`
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/asset_summary.csv`
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/cost_summary.csv`
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/trade_log.csv`
   - `reports/artifacts/scout_rank130_crossmarket_leader_impulse_15m/summary.json`
3. 生成 reader-facing 页面：
   - `reports/site/factors/scout_rank130_crossmarket_leader_impulse_15m/report.html`
   - `reports/site/reading/repo_scout/rank130_crossmarket_leader_impulse_clean_replication.html`
4. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 追加 `2026-03-20 21:40 UTC` 的最新补充；
   - 把 `Rank 130` 直接压回 **`P0 / park / evidence pool`**；
   - 把 `Next 3` 改回 **fresh intake 优先**，而不是继续磨旧 `P1`。

## 验证 / 证据
### 1) Paper Seat 仍 waiting_not_due
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
关键信号：
- `EMA = waiting_not_due`
- 无 `due-now / overdue lane`
- 最近 due：`Crypto 1d+1wk -> due_soon / 约 2.4 小时后到点`

### 2) 本轮 clean-room 口径
- 数据：`BTC/ETH/SOL 120d 15m` 本地 cache
- setup：`breakout_short / fib_retest_long / ema_psar_long`
- 执行：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- 三臂：`baseline / low_z_only / high_z_veto`
- 冻结定义：
  - `leader_ret = 目标币种之外另外两条币的 15m 收益均值`
  - `leader_z = rolling 96 bars 的 |leader_ret| z-score`
  - `leader_valid = 同向 + leader_abs_mean > 1.2 × |target_ret|`

### 3) 测试段总表（6 bps / side）
- `baseline`：`trades=323`，`mean_total_return≈-0.096%`，`failure_before_target≈52.01%`
- `low_z_only`：`trades=61`，`retention≈18.89%`，`mean_total_return≈-0.044%`，`failure_before_target≈44.26%`
- `high_z_veto`：`trades=312`，`retention≈96.59%`，`mean_total_return≈-0.114%`，`failure_before_target≈52.56%`

### 4) 读法
- `low_z_only` 看起来少亏一点、假延续也更低，但主要靠 **只保留约 `18.9%` 样本** 换来，离“shared gate 的诚实 uplift”还很远。
- 理论上更该值钱的 `high_z_veto` 没有站住：它几乎没减少交易，却把收益变得更差、失败率也略恶化。
- 分资产也不统一：
  - `BTC`：`low_z_only` 略改善（约 `-0.22% -> -0.09%`）
  - `ETH`：`low_z_only` 反而变差（约 `-0.03% -> -0.10%`）
  - `SOL`：`low_z_only` 最明显（约 `-0.03% -> +0.10%`）
- 这更像 **setup/资产间互相打架 + 缩样本**，而不是可 shared 的稳定 follow-up gate。

## 当前硬结论
**`Rank 130 / cross-market leader impulse nonlinear gate = park / evidence pool`**。

翻成人话：
“跨市场 leader 冲击要分层”这个直觉不是全错，但这轮最小 clean replication 没把它做成足够诚实的 desk 级 shared gate；当前保留下来的主要是一个值得记住的线索，不是该继续占 fast lane 的候选。

## 风险 / 边界
- 这轮只完成了 **1 次最小 clean replication**，还没有进入 `Light Stability Pack`。
- 由于 `high_z_veto` 没站住，当前不适合继续补近义 admission 文案来硬保 `P1`。
- 这次实现把论文里的 `ETH/SOL -> BTC` 直觉翻译成了 desk 更可执行的“目标币种 vs 另外两币 leader basket”口径；它适合 fast honest check，但不应被误读成论文原式 full replication。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，按顶板应直接回到 **fresh intake**：优先从 `quant_digests / RECENT_PAPER_SEEDS / validated shortlist` 再认领 `1` 条新的 `paper / repo based 15m crypto` 候选。
- 不要回头续磨 `Rank 130 / 128 / 129`，也不要默认把 `Rank 127 / 125 / 112 / 111` 重新抬回主资源位；除非 bot2 明确点名一条“只需 1 个 truly verdict-changing follow-up”的旧 `P1`。

## Commit hash
- 未提交。
- 原因：当前 repo 工作区有大量与本轮无关的脏文件（`git status --short | wc -l = 1976`），这轮不适合做安全 selective commit。
