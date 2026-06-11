# 2026-03-20 15:15 UTC · Rank 124 / interim wick + ATR stop anchor / clean replication

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作落在 **`Rank 124 / interim wick + ATR stop anchor` 的 1 次最小 clean replication**。当前 hard verdict：**`park / evidence pool`**。

## 先检查了什么
- `git branch --show-current` -> `master`
- `git status --short | wc -l` -> `1889`
  - 工作区仍很脏，不混提；只做本轮相关最小写回。
- 最近 optimization logs：最新已到
  - `2026-03-20_1458_rank124-wick-stop-intake.md`
  - `2026-03-20_1435_rank123-rsi-state-machine-clean-replication.md`
  - `2026-03-20_1404_rank123-rsi-state-machine-intake.md`
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 4.8h`、`Crypto 1d+1wk -> 8.8h`、`创业板ETF 1d -> 63.8h`
  - 说明：本轮 `Run 1` 无新 due-now / overdue lane，合法主动作必须切回 `Scout Seat`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - authoritative `Next 3`：`Run 1 = EMA due-check first -> Run 2 = Rank 124 minimal clean replication -> Run 3 = keep_P1 / promote_P2 / park`

## 为什么这轮认领 Rank 124
这轮最诚实的动作不是回头续磨 `Rank 112 / 111`，也不是去消费 `Rank 122` 的 `P3 continuity` 预算，而是把上一轮已经 guard-pass 的 `Rank 124` 真正跑成一个可复核的 clean-room。

这条线值这 1 次预算，不是因为它像新 alpha，而是因为它直接回答一个更接近部署的问题：
**同样的 entry，初始 stop 该继续围着 entry 画 `1.5 ATR`，还是更诚实地挂在最近反向对抗的 wick 外？**

如果这件事成立，它会直接改变 desk 的 risk plumbing；如果不成立，也应该尽快 park，而不是停在 source intake 文字层。

## 本轮主点
### Rank 124 minimal clean replication
固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache，只比较三种初始风险锚：
- `atr_only`：`entry ± 1.5 ATR`
- `wick_atr`：最近反向实体 K 的 wick 外，再加 `0.25 ATR`
- `wick_pct`：最近反向实体 K 的 wick 外，再加 `0.2%`

全部统一挂到 3 条最小 base setup：
- `fib_retest_long`
- `ema_psar_long`
- `breakout_short`

执行口径全部写死为：
- `signal 当根及之前数据`
- `next-bar open`
- `no-overlap`
- `hold 8 bars`

其中 `wick` 也被收得很窄：只允许取 **signal 前最近 6 根里最后一根反向实体 K** 的 wick；如果窗口里没有反向实体 K，才退回 signal bar 自己的极值。没有做训练段调参，也没有做事后最优窗口搜索。

## 结果 / 硬结论
## authoritative verdict
**`Rank 124 / interim wick + ATR stop anchor = park / evidence pool`**。

翻成人话：
- 结构锚 stop 的确让近端 stopout 变少；
- 但它主要靠 **stop 更宽** 在换结果，而不是把成本后收益变得更诚实；
- 因此它当前不够格升成 shared risk upgrade，更不该被误写成 alpha 改善。

### desk 级主读法（6 bps / side）
- `atr_only`
  - `mean_total_return ≈ -6.19%`
  - `mean_stop_hit_8bars ≈ 50.01%`
  - `mean_avg_stop_distance_pct ≈ 0.70%`
- `wick_atr`
  - `mean_total_return ≈ -7.85%`
  - `mean_stop_hit_8bars ≈ 33.22%`
  - `mean_avg_stop_distance_pct ≈ 1.14%`
- `wick_pct`
  - `mean_total_return ≈ -7.21%`
  - `mean_stop_hit_8bars ≈ 28.95%`
  - `mean_avg_stop_distance_pct ≈ 1.23%`

结论很直白：
**少被打 stop 这件事是真的，但买到它的代价是更大的风险半径，而不是更好的 post-cost expectancy。**

### 分 setup 读法
1. `fib_retest_long`
   - `atr_only ≈ +0.38%`
   - `wick_atr ≈ +0.98%`
   - `wick_pct ≈ +0.61%`
   - 这里有一点改善味道，但不是跨 setup 的硬提升。

2. `ema_psar_long`
   - `atr_only ≈ -3.36%`
   - `wick_atr ≈ -4.21%`
   - `wick_pct ≈ -3.56%`
   - 更宽 stop 没换来更好的结果。

3. `breakout_short`
   - `atr_only ≈ -15.57%`
   - `wick_atr ≈ -20.32%`
   - `wick_pct ≈ -18.68%`
   - 这是最明确的否决点：stop hit 下降了，但整体回撤更差，说明并不是“更诚实地避开噪声”，而更像“让坏单活得更久”。

### stop distance 诚实边界
- `breakout_short`
  - `atr_only mean_stop_distance ≈ 0.73%`
  - `wick_atr mean_stop_distance ≈ 1.33%`
  - `wick_pct mean_stop_distance ≈ 1.41%`
- `ema_psar_long`
  - `atr_only ≈ 0.68%`
  - `wick_atr ≈ 1.05%`
- `fib_retest_long`
  - `atr_only ≈ 0.68%`
  - `wick_atr ≈ 1.04%`

也就是说，这轮结果不是“结构锚把风险定义得更准了”，而更像“结构锚把 stop 距离整体抬高了约 35%~90%”。

## 做了什么改动
### 新增脚本
- `scripts/build_rank124_interim_wick_stop_clean_replication.py`

### 生成 artifacts
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/signal_catalog.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/trade_log.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/asset_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/setup_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/overall_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/stop_distance_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/summary.json`

### reader-facing 落点
- `reports/site/factors/scout_rank124_interim_wick_stop_anchor_15m/report.html`
- `reports/site/reading/repo_scout/rank124_interim_wick_stop_anchor_clean_replication.html`

### board write-back
- 已把 `docs/TODO.md` 顶部 board 更新为：
  - `Rank 124 = park / evidence pool`
  - `Scout Seat` 主资源位切回 fresh intake
  - `Next 3` 改写为：`EMA due-check -> fresh intake -> 若 guard-pass 再给 1 次 minimal clean replication`

## 验证 / 证据
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`
- `python3 scripts/build_rank124_interim_wick_stop_clean_replication.py`
  - 成功生成 reader-facing page 与 artifact
  - 生成时输出 hard verdict：`park / evidence pool`

关键证据文件：
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/overall_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/setup_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/stop_distance_summary.csv`
- `reports/artifacts/scout_rank124_interim_wick_stop_anchor_15m/summary.json`

## 风险 / 边界
- 这轮只验证 **initial stop anchor**，没有改 entry，也没有改 position sizing；
- `wick` 定义当前收得很窄（最近 6 根里的最后一根反向实体 K），不是完整 market-structure engine；
- stop 更少被打并不自动等于更好，尤其在 short 侧很容易变成“让坏单扛更久”；
- 当前结果不足以支持 shared risk overlay 升级，因此继续投入 `Light Stability Pack` 预算不诚实。

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条新的 fresh intake`
  - `Run 3 = 若新 intake guard-pass，再给 1 次最小 clean replication`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 124` 直接相关文件与 board 局部更新，不适合混提。
