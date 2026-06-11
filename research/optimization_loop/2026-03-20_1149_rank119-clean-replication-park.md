# 2026-03-20 11:49 UTC · Rank 119 / confirmed swing + HTF long-context clean replication（park）

## 本轮上下文
- 触发：bot3 13m desk auto loop
- Run 1：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- Run 1 结果：`EMA / Paper Seat` 继续如实返回 **`waiting_not_due`**；最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`
- 因此按顶板当前 `Next 3`，本轮合法主动作就是 **`Rank 119 / confirmed swing + HTF alignment long-side context`** 的那 **1 次最小 clean replication**
- repo 状态：工作区仍有大量与本轮无关的既有脏文件，因此继续只做与本轮直接相关的最小写入，不混提

## 为什么这轮选这个
上一轮已经把 `Rank 119` 冻结成 **`guard-passed / admit_to_clean_replication_queue_as_long_context_only`**。按桌面规则，这一轮不能再回头磨旧 `P1 evidence_pool`，也不能跳去别的新方向；最值钱的动作就是把它用同一套诚实执行口径跑一次最小 clean replication，尽快回答：

**它到底能不能作为 `Fib / EMA` 的 long-side context 留在快筛主桌上，还是应该立刻 park。**

## 做了什么改动
### 1. 先按 desk 规则做 EMA due-check
实际运行：

```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

结果如实返回：当前没有 `due-now / overdue lane`，因此本轮不能继续把主资源花在 `Paper Seat` 上。

### 2. 新增 Rank 119 clean replication 脚本
新增：

- `scripts/build_rank119_confirmed_swing_htf_clean_replication.py`

脚本固定了这轮唯一允许的最小实验口径：
- 只挂 **1 条 archetype = `fib_retest_long`**
- 数据固定复用 **`BTC/ETH/SOL 120d 15m` 本地 cache**
- 1h 上下文不取未来数据：由 15m OHLCV 先重采样出已收盘 1h bar，再 `merge_asof(backward)` 回 15m
- `confirmed swing` 必须确认后才可用；不允许把未确认 swing 倒灌到当前 bar
- 测试段统一：**`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`**
- 比较两臂：
  - `baseline`
  - `long_context_only`
- 训练段只冻结非常小的一组结构年龄参数：
  - `15m max_age ∈ {8,16,24}`
  - `1h max_age ∈ {4,8,12}`
  - `swing_lookback=5` 固定

### 3. 产出 reader-facing 页面
新增 / 更新：
- `reports/artifacts/scout_rank119_confirmed_swing_htf_long_context_15m/`
- `reports/site/factors/scout_rank119_confirmed_swing_htf_long_context_15m/report.html`
- `reports/site/reading/repo_scout/rank119_confirmed_swing_htf_long_context_clean_replication.html`

### 4. 回写顶板
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 把 `Rank 119` 从 `P1 / clean replication next` 改成 **`P0 / park / evidence pool`**
- 把 `Next 3` 顺序收回到 **fresh intake 优先**

## 验证 / 证据
实际运行：

```bash
python3 scripts/build_rank119_confirmed_swing_htf_clean_replication.py
```

脚本输出：
- `verdict = park / evidence pool`
- 训练段冻结参数：`15m max_age=8 / 1h max_age=4`

关键证据来自：
- `reports/artifacts/scout_rank119_confirmed_swing_htf_long_context_15m/summary.json`
- `reports/artifacts/scout_rank119_confirmed_swing_htf_long_context_15m/overall_summary.csv`
- `reports/artifacts/scout_rank119_confirmed_swing_htf_long_context_15m/asset_summary.csv`

### 6 bps/side 的最诚实读法
- `baseline`：
  - `mean_total_return ≈ +0.00%`
  - `positive_asset_ratio = 1/3`
  - `mean_retention = 100%`
  - `mean_false_follow_4bars = 75%`
  - `mean_entries ≈ 8.33`
- `long_context_only`：
  - `mean_total_return = 0.00%`
  - `positive_asset_ratio = 0/3`
  - `mean_retention = 0%`
  - `mean_entries = 0`

翻成人话：
**这套 `confirmed swing + HTF bullish alignment` 在当前 clean-room 里不是“更诚实地过滤坏单”，而是直接把测试段样本砍光了。**

### 分资产读法
- `BTC`：baseline 测试段 `9` 个信号，context 臂 `0` 笔 entry
- `ETH`：baseline 测试段 `8` 个信号，context 臂 `0` 笔 entry
- `SOL`：baseline 测试段 `8` 个信号，context 臂 `0` 笔 entry

所以这轮 hard verdict 很硬：
**它当前不值得继续占用 `Scout Seat` 主资源。**

## 风险 / 边界
- 这轮只测了 **`fib_retest_long`** 这一条 base archetype；没有外推到 `EMA continuation`
- 但这不影响当前 desk 级判断：对于一个只拿到 **1 次最小 clean replication** 预算的 `P1` 来说，测试段直接 `0` entry 已足够构成 `hard-fail / exhausted`
- 它以后若要复活，前提也应该是换一个更宽松、仍因果有效的结构定义；而不是继续沿现在这条过窄口径磨文案

## 当前硬结论
**`Rank 119 / confirmed swing + HTF alignment long-side context = park / evidence pool`**。

一句人话：
**结构一致性这件事在 repo 里像回事，但按当前 15m+1h 因果口径落地后，把样本削到测试段一笔都不剩；现在更像“太挑剔”，不是“更诚实”。**

## 下一步建议
按当前桌面规则，下一轮应改回：
1. `Run 1 = EMA due-check first`
2. 若仍 `waiting_not_due`：
   - `Run 2 = 优先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 认领 1 条新的 fresh intake`
3. 若 fresh intake guard-pass：
   - `Run 3 = 只给它 1 次最小 clean replication`
4. 只有 fresh intake 也 exhausted 后，才允许回到 `tiny-live plumbing`

## 本轮交付
- deployable artifact：`scripts/build_rank119_confirmed_swing_htf_clean_replication.py`
- factor page：`reports/site/factors/scout_rank119_confirmed_swing_htf_long_context_15m/report.html`
- reader-facing scout page：`reports/site/reading/repo_scout/rank119_confirmed_swing_htf_long_context_clean_replication.html`
- board sync：`docs/TODO.md`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 119` 直接相关的最小文件，不适合混提。
