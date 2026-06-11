# Rank 114 / pullback → two-sided breakout window verdict clean replication → park

## 为什么这轮是它
- 先按交易台指挥板继续执行 `Run 1 / EMA due-check first`：再次实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果继续如实返回 **全 desk `waiting_not_due`**。
- 最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`；因此这轮 `Paper Seat` 没有新的 due-now / overdue 动作可做。
- `Rank 114` 在上一轮已经完成 `source intake + 两条轻量诚实守门`，按顶板 `Next 3` 的唯一合法主动作，就是给它那 **1 次最小 clean replication**；不并开第二条 Scout 候选。

## 本轮只认领了什么
- **主点**：`Rank 114 / pullback → two-sided breakout window verdict` 的 1 次最小 clean replication。
- **紧邻子点**：把 hard verdict、active Scout 顺序、以及新的 `Next 3` 写回 `docs/TODO.md` 顶板。
- 没有并开其他 fresh intake、没有回头磨 `P3 continuity`、也没有去碰 `tiny-live plumbing`。

## 先做的 desk 检查
1. 再次执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 输出继续确认全 desk `waiting_not_due`；最靠前 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、其次 `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`。
   - `require-due` 模式下以 code `2` 退出，属于诚实等待路径，不是失败。
2. 再看当前工作区状态
   - repo 里本来就有大量与本轮无关的脏文件 / 未跟踪文件；因此本轮只新增 `Rank 114` clean replication 脚本、对应 artifacts / reader-facing 页面、顶板写回、以及本轮日志，不做混提。

## 这次最小 clean replication 怎么做的
### 固定范围
- **唯一 base archetype**：`fib_retest_long`
- **样本**：`BTC / ETH / SOL` 的 `120d 15m` 本地 cache
- **执行冻结**：`signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`
- **成本**：主看 `6bps/side`，并补看 `10 / 15bps`

### 规则骨架
- baseline：`fib_retest_long_signal` 出现后，直接 `next-bar open` 入场。
- window 版：
  1. signal 后只允许在前 `1~3` 根里寻找 pullback bar；
  2. 若找到 pullback bar，则用该 bar 的 `high / low` 加上 `offset_atr` 定义 `success_edge / failure_edge`；
  3. 只在后续 `window_bars` 内判 `success / failure / timeout`；
  4. 只有 `success` 才允许 `next-bar open` 入场；`failure / timeout` 直接视为 veto；
  5. 参数只能在训练段冻结，再去测试段验证，禁止全样本 / 事后挑最好组合。

### 训练段冻结结果
- 训练段挑出的唯一方案是：
  - `pullback_bars = 3`
  - `window_bars = 4`
  - `offset_atr = 0.20`
- 对应变体名：`window_pb3_w4_o20`

## 结果
### 测试段总表（核心看 6bps）
- `baseline_direct_entry @ 6bps`
  - `mean_total_return ≈ -0.72%`
  - `positive_asset_ratio = 0/3`
  - `mean_retention = 100.00%`
  - `mean_false_follow_4bars ≈ 80.00%`
  - `mean_entries ≈ 5.0`
- `window_pb3_w4_o20 @ 6bps`
  - `mean_total_return ≈ -0.95%`
  - `positive_asset_ratio = 2/3`
  - `mean_retention ≈ 66.67%`
  - `mean_false_follow_4bars ≈ 83.33%`
  - `mean_timeout_or_fail_rate ≈ 33.33%`
  - `mean_entries ≈ 3.33`

### 分资产读法
- **BTC**：window 版比 baseline 好一些（`+0.47%` vs `-0.16%`），但改善不够大，也没把 `false_follow_4bars` 压得更干净。
- **ETH**：window 版略转正（`+0.09%`），但同样主要伴随 trade count 下降。
- **SOL**：window 版明显更差（约 `-3.41%`），且 `timeout/fail` 很高，说明这套 skeleton 在当前 clean-room 上并不稳。

## 最诚实的当前结论
- 当前 hard verdict：**`Rank 114 = park / evidence pool`**。
- 翻成人话：repo 里的 `pullback → two-sided verdict` 作为 **概念 / execution skeleton** 有启发，但放进当前 `fib_retest_long` clean-room 后，并没有形成值得继续保留的 honest uplift。
- 更直白一点：
  - 它没有把坏单过滤成更好的 desk 收益；
  - `retention` 从 `100%` 掉到 `66.67%`；
  - `false_follow_4bars` 甚至没有改善；
  - 所以这次结果更像 **“砍样本换外观”**，不是更诚实的 entry path。

## 为什么这轮直接 park，而不是 keep_P1
- 这条线已经拿到了它唯一允许的那手最小 clean replication。
- 当前测试段 `6bps` 下，冻结后窗口版对 baseline 的 `mean_total_return` 改善只有 **`-0.23%`**，不是正向 uplift。
- `positive_asset_ratio` 虽然从 `0/3` 变成 `2/3`，但主要是靠少做单换来的，且 `SOL` 明显恶化。
- 在 `false_follow_4bars` 也没有下降、`timeout/fail` 还抬升的前提下，再继续给它预算只会变成 admission wording / 参数近义调参，不符合 desk 当前“先硬门槛、再分级、再限预算”的规则。

## 这轮产物
- 新脚本：`scripts/build_rank114_pullback_two_sided_window_clean_replication.py`
- artifacts：`reports/artifacts/scout_rank114_pullback_two_sided_window_15m/`
  - `summary.json`
  - `overall_summary.csv`
  - `asset_summary.csv`
  - `train_grid_summary.csv`
  - `trade_log.csv`
  - `signal_catalog.csv`
- reader-facing 页面：
  - `reports/site/factors/scout_rank114_pullback_two_sided_window_15m/report.html`
  - `reports/site/reading/repo_scout/rank114_pullback_two_sided_window_clean_replication.html`

## 顶板写回
- 已把 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 写回为：
  - `Rank 114 -> park / evidence pool`
  - `Run 2` 从继续磨 `Rank 114` 改成 **fresh intake**
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
- `python3 scripts/build_rank114_pullback_two_sided_window_clean_replication.py`
  - 成功产出 `summary.json / overall_summary.csv / asset_summary.csv / train_grid_summary.csv / trade_log.csv / signal_catalog.csv`
  - 关键摘要：`park / evidence pool`

## 风险 / 边界
- 这次 clean replication 只挂了 **`fib_retest_long`**，还没有证明这个 skeleton 在其他 base archetype（如 `breakout-short` / `EMA-PSAR raw trigger`）上一定同样无效；但按当前预算规则，它已经不值得继续占默认 fast lane。
- 若未来别的 archetype 自身已经更强，再回头把这个 skeleton 当副层实验可以；但那应该是后续的低优先级附带检查，不应继续当当前 Scout 主线。

## Commit hash
- 未提交。

## 未提交原因
- git 工作区存在大量与本轮无关的已修改 / 未跟踪文件；为避免混提，本轮只保留本轮脚本、artifacts、reader-facing 页面、顶板 write-back 与日志。
