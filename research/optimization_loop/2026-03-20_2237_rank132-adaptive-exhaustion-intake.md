# Rank 132 / adaptive exhaustion countertrend-leg gate intake

## 为什么这次选这个
- 先按 desk board 执行 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回仍是 `waiting_not_due`；当前没有 `due-now / overdue` lane，最靠前的仍是 `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 1.4 小时后到点`。
- 因此本轮不能伪造 paper refresh，必须切到 `Run 2 / fresh intake reserve`。
- 再比较 active Scout 的当前边际价值：
  - `Rank 127 / 125 / 112 / 111` 都已是 `P1 / budget used / evidence_pool`，不适合继续磨；
  - `Rank 131` 刚在最小 clean replication 后如实压回 `P0 / park`；
  - hosted `P3`（`122 / 2 / 17 / 29 / 32b`）这轮没有 status-changing event，不该抢主资源位。
- 所以这轮最诚实的动作，是从现有 seed pool 里认领下一个顺序 Rank，并优先选一个**同时服务 breakout-short / Fib retest_hold / EMA-PSAR overlay** 的低预算 gate。
- 在现有种子里，`2026-03-20_2218_adaptive-exhaustion-countertrend-leg-gate.md` 最贴近 desk 主线，因此本轮将其正式编成 **`Rank 132`**。

## 做了什么改动
1. 新建 queue-facing artifact：
   - `reports/artifacts/literature/scout_rank132_adaptive_exhaustion_countertrend_leg_source_intake_card.csv`
2. 新建 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank132_adaptive_exhaustion_countertrend_leg_source_intake.html`
3. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 把 `Scout Seat` 当前主点切到 `Rank 132`；
   - 把 `Active Scout` 排序改为 `Rank 132 > 127 > 125 > 112 > 111`；
   - 把 `Next 3 bot3 runs` 改成：`Run 1 = EMA due-check` → `Run 2 = Rank 132 最小 clean replication` → `Run 3 = honest uplift / park / fresh intake fallback`；
   - 把最新关键 evidence 追加为 `2026-03-20 22:35 UTC / Rank 132 intake + honesty gate passed`。

## 验证 / 证据
### 1) EMA 本轮仍是 waiting_not_due
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
关键信号：
- `当前没有 due-now / overdue lane`
- 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 1.4 小时后到点`
- `require-due` 已开启：当前应等待下一根 completed bar，而不是伪造 refresh

### 2) Rank 132 两条轻量诚实守门
当前最诚实的 `trade on / trade off`：
- **trade on**：它只配当 `breakout-short follow-up`、`Fib retest_hold`、`EMA/PSAR follow-up` 的 `countertrend-leg admission / veto gate`。先有 baseline setup，再在 broken level / Fib zone / EMA trigger 附近检查最近 `1~3` 根 `5m` 是否出现与交易方向一致的 exhaustion state：
  - `long` 看 `sellers exhausted`
  - `short` 看 `buyers exhausted`
- **trade off**：它不是独立 alpha，不是反转神谕，也不是见 exhaustion 就逆势开仓。若没有既有 baseline setup、若信号来自 signal 之后的数据、若只是靠明显延迟入场换漂亮报表、或若它把 `trade_count retention` 砍穿，就不得升成 shared default gate。
- **honesty gate**：通过。exhaustion 状态只能由 `signal 当根及之前、已完成的 5m/15m bars` 计算；参数窗口必须预先冻结；后续 clean replication 必须统一到 `next-bar open + no-overlap`，禁止用 future swing 完成或 future path 倒灌。

### 3) 为什么它现在比旧 P1 更值钱
- `Rank 127 / 125 / 112 / 111` 都已经拿过那 `1` 次便宜诚实检查，本轮继续回头磨更像 admission wording，而不是减少真实 gate。
- `Rank 132` 补的是三条主线都能复用的同一层缺口：**回踩/反抽这条 countertrend leg 到底是不是已经走完**。
- 它的角色也更诚实：不是再发明一个主方向信号，而是在现有 setup 上加一层 cheap `follow-up honesty gate`。

## 当前硬结论
**`Rank 132 / adaptive exhaustion countertrend-leg gate = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 别再把回踩腿写成“摸到位就够了”。
- 很多假确认的核心问题，不是没碰到线位，而是**那条反向腿根本还没走完**。
- 这条线值得给 `1` 次最小 clean replication 预算，但还远不到 `paper candidate`。

## 风险 / 边界
- 这轮只做了 `fresh intake + honesty gate`，没有做 clean replication，更没有进入 `Light Stability Pack`。
- 当前主要证据来自 repo 实现与论文背景，不是现成的大样本 crypto OOS 结论；这轮保留的是“机制值得测”，不是“alpha 已被证明”。
- `exhaustion` 很容易靠明显延迟入场换出更漂亮的持有期统计，因此下一轮必须显式看 `entry_delay_bars` 与 `trade_count retention`。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，则严格只给 `Rank 132` **1 次最小 clean replication**：
  - 对照：`baseline / minor exhaustion gate / minor+major strict tier`
  - 统一口径：`BTC/ETH/SOL perpetual`、`15m signal + 5m execution readout`、`next-bar open + no-overlap`
  - 成本：`6 / 10 / 15 bps per side`
  - 主看：`post_cost_expectancy / false_reclaim_ratio@4bars / mae@4bars 或 sl_first_rate / trade_count_retention / entry_delay_bars`
- 若 clean replication 只是靠更晚入场换漂亮报表，或交易数明显塌陷，则直接 `park`，不要继续打磨 wording。

## Commit hash
- 未提交。
- 原因：repo 工作区仍有大量与本轮无关的脏文件，这轮不适合做安全 selective commit。
