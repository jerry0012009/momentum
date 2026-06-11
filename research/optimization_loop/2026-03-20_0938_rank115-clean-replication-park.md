# Rank 115 / same-clock intraday RVOL volume gate clean replication → park

## 为什么这轮是它
- 先按交易台指挥板继续执行 `Run 1 / EMA due-check first`：再次实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果继续如实返回 **全 desk `waiting_not_due`**。
- 最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`；因此这轮 `Paper Seat` 没有新的 due-now / overdue 动作可做。
- `Rank 115` 在上一轮已经完成 `source intake + 两条轻量诚实守门`，按顶板 `Next 3` 的唯一合法主动作，就是给它那 **1 次最小 clean replication**；不并开第二条 Scout 候选。

## 本轮只认领了什么
- **主点**：`Rank 115 / same-clock intraday RVOL volume gate` 的 1 次最小 clean replication。
- **紧邻子点**：把 hard verdict、active Scout 顺序、以及新的 `Next 3` 写回 `docs/TODO.md` 顶板。
- 没有并开其他 fresh intake、没有回头磨 `P3 continuity`、也没有去碰 `tiny-live plumbing`。

## 先做的 desk 检查
1. 再次执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 输出继续确认全 desk `waiting_not_due`；最靠前 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、其次 `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`。
   - `require-due` 模式下以 code `2` 退出，属于诚实等待路径，不是失败。
2. 再看当前工作区状态
   - repo 里本来就有大量与本轮无关的脏文件 / 未跟踪文件；因此本轮只新增 `Rank 115` clean replication 脚本、对应 artifacts / reader-facing 页面、顶板写回、以及本轮日志，不做混提。

## 这次最小 clean replication 怎么做的
### 固定范围
- **唯一 base archetype**：`fib_retest_long`
- **样本**：`BTC / ETH / SOL` 的 `120d 15m` 本地 cache
- **执行冻结**：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- **成本**：主看 `6bps/side`，并补看 `10bps/side`

### 规则骨架
- baseline：保留原来的 `naive rolling RVOL` 口径，即 `volume / rolling mean(last N bars)`。
- same-clock 版：把 volume gate 改成 `slot_rvol = 当前量 / 历史同 HH:MM 的过去 N 次均量`。
- 两臂都只作为 `fib_retest_long` 的 **volume confirmation layer**，不单独开仓、不偷渡成新 alpha。
- 训练段只冻结两项：
  - `lookback = 12`
  - `slot_spike = 1.5`
- 然后在测试段统一比较：
  - `baseline_naive_rvol`
  - `same_clock_rvol`

## 结果
### 测试段总表（核心看 6bps）
- `baseline_naive_rvol @ 6bps`
  - `mean_total_return ≈ -0.19%`
  - `positive_asset_ratio = 1/3`
  - `mean_retention ≈ 40.28%`
  - `mean_false_follow_4bars ≈ 70.00%`
  - `mean_entries ≈ 3.33`
  - `mean_expectancy ≈ -0.037%`
- `same_clock_rvol @ 6bps`
  - `mean_total_return ≈ -0.10%`
  - `positive_asset_ratio = 1/3`
  - `mean_retention ≈ 24.54%`
  - `mean_false_follow_4bars ≈ 72.22%`
  - `mean_entries ≈ 2.00`
  - `mean_expectancy ≈ -0.190%`

### 分资产读法
- **BTC**：same-clock 版从 `+1.03%` 掉到 `-0.59%`，而且 `9` 个测试信号里有 `3` 个是 `naive_only`、只有 `1` 个是 `slot_only`；这更像把本来还能做的单砍掉了。
- **ETH**：两臂几乎等价（都是 `-0.47%`、`2` 笔 entry），说明 same-clock 在这条线上基本没带来新的信息。
- **SOL**：same-clock 版从 `-1.12%` 改到 `+0.76%`，但主要伴随 entry 从 `5` 笔缩到 `3` 笔；改善有一点，但证据不够强，且不足以覆盖 BTC 的退化。

### Gate 分歧摘要
- `BTC`：`naive_only = 3`、`slot_only = 1`
- `ETH`：两臂完全一致（`naive_only = 0`、`slot_only = 0`）
- `SOL`：`naive_only = 2`、`slot_only = 0`

## 最诚实的当前结论
- 当前 hard verdict：**`Rank 115 = park / evidence pool`**。
- 翻成人话：same-clock RVOL 确实改变了 gate 判定，但放到这次 `fib_retest_long` clean-room 后，并没有形成足够诚实的 desk uplift。
- 更直白一点：
  - 它虽然把 `mean_total_return` 从 `-0.19%` 小幅抬到 `-0.10%`；
  - 但 `retention` 从 `40.28%` 掉到 `24.54%`；
  - `false_follow_4bars` 反而从 `70.00%` 恶化到 `72.22%`；
  - 所以这次结果更像 **“样本重排 / 少做单换外观”**，不是更诚实的 confirmation upgrade。

## 为什么这轮直接 park，而不是 keep_P1
- 这条线已经拿到了它唯一允许的那手最小 clean replication。
- 当前测试段 `6bps` 下，same-clock 版对 baseline 的 `mean_total_return` 改善只有 **`+0.09%`**，不够硬。
- 更关键的是，改善没有伴随更低的 `false_follow_4bars`，反而略微恶化，同时 trade retention 明显塌缩。
- 在 desk 当前“先硬门槛、再分级、再限预算”的规则下，再继续给它预算就会变成为了一个 measurement idea 继续续命，而不是为了改变当前席位判断。

## 这轮产物
- 新脚本：`scripts/build_rank115_same_clock_intraday_rvol_clean_replication.py`
- artifacts：`reports/artifacts/scout_rank115_same_clock_intraday_rvol_15m/`
  - `summary.json`
  - `overall_summary.csv`
  - `asset_summary.csv`
  - `train_grid_summary.csv`
  - `test_disagreement_summary.csv`
  - `trade_log.csv`
  - `signal_catalog.csv`
- reader-facing 页面：
  - `reports/site/factors/scout_rank115_same_clock_intraday_rvol_15m/report.html`
  - `reports/site/reading/repo_scout/rank115_same_clock_intraday_rvol_clean_replication.html`

## 顶板写回
- 已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 写回为：
  - `Rank 115 -> park / evidence pool`
  - active Scout 顺序重新切回 **fresh intake 优先**
  - `Run 2` 从继续磨 `Rank 115` 改成 **fresh intake**
  - fresh intake 默认来源：`docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`：
  1. 优先从 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 认领 **1 条新的 fresh intake**；
  2. 新方向进入 queue-facing 前，先拿下一个顺序 `Rank`；
  3. 只要 fresh intake 能过两条轻量诚实守门，下一轮就只给它 **1 次最小 clean replication**；
  4. 若 fresh intake 也 exhausted，再诚实回退到 `tiny-live plumbing fallback`。

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`；在 `require-due` 模式下以 code `2` 退出，属于预期等待路径。
- `python3 scripts/build_rank115_same_clock_intraday_rvol_clean_replication.py`
  - 成功产出 `summary.json / overall_summary.csv / asset_summary.csv / train_grid_summary.csv / test_disagreement_summary.csv / trade_log.csv / signal_catalog.csv`
  - 关键摘要：`park / evidence pool`

## 风险 / 边界
- 这次 clean replication 只挂了 **`fib_retest_long`**，还没有证明 same-clock RVOL 在其他 base archetype（如 `breakout-short follow-up` / `EMA-PSAR volume gate`）上一定同样无效；但按当前预算规则，它已经不值得继续占默认 fast lane。
- 未来如果某条 archetype 本身更依赖时段 volume 季节性，可以把 same-clock 当作低优先级附带检查；但那不应继续占当前 Scout 主资源位。

## Commit hash
- 未提交。

## 未提交原因
- git 工作区存在大量与本轮无关的已修改 / 未跟踪文件；为避免混提，本轮只保留本轮脚本、artifacts、reader-facing 页面、顶板 write-back 与日志。
