# Rank 114 / pullback → two-sided breakout window verdict source intake

## 为什么这轮是它
- 先按交易台指挥板执行 `Run 1 / EMA due-check first`：再次实际运行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，结果继续如实返回 **全 desk `waiting_not_due`**。
- 最近 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-21 00:00 UTC`；因此这轮 `Paper Seat` 没有新的 due-now / overdue 动作可做。
- `Rank 113` 已在上一轮完成那 1 次最小 clean replication，并按 hard verdict 压回 `park / evidence pool`；所以当前按 `TRADING DESK BOARD` 的 `Next 3`，合法主动作只能切到 **`Rank 114 / pullback → two-sided breakout window verdict` 的 source intake + 两条轻量诚实守门**。

## 本轮只认领了什么
- **主点**：`Rank 114 / pullback → two-sided breakout window verdict` 的 source intake。
- **紧邻子点**：把两条轻量诚实守门与下轮 clean replication 边界写回 `docs/TODO.md` 顶板。
- 没有并开第二条 Scout 候选；严格遵守“一轮最多 1 个主点 + 1 个紧邻子点”。

## 做了什么
1. 再次执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 输出继续确认全 desk `waiting_not_due`；最靠前 due 仍是 `美股 1d+1wk -> 2026-03-20 20:00 UTC`、其次 `Crypto 1d+1wk -> 2026-03-21 00:00 UTC`。
   - `require-due` 模式下以 code `2` 退出，属于诚实等待路径，不是失败。
2. 基于 `2026-03-20 07:42` 的 repo digest，把 `Rank 114` 正式写成 queue-facing source intake artifact：
   - `reports/artifacts/literature/scout_rank114_pullback_two_sided_window_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank114_pullback_two_sided_window_source_intake.html`
3. 把 `docs/TODO.md` 顶板同步到新的更诚实 desk 读法：
   - `Rank 114 = guard-passed / admit_to_clean_replication_queue`
   - 当前 active Scout 顺序前推为：`Rank 114 > Rank 113 (park) > Rank 112 (P1 budget used) > Rank 111 (P1 budget used)`
   - 下一轮只允许给 `Rank 114` **1 次最小 clean replication**，不并开其他候选。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on**：它不是新 alpha，只是把现有 raw trigger 降级成 `scan / armed`，再把真正 entry 写成一个很短的 post-trigger verdict：
  - 先有 base trigger（如 `breakout-short` / `fib_retest_long` / `EMA-PSAR raw trigger`）
  - 然后等 `1~3` 根 pullback 或一个有限深度回踩
  - 再开一个双边窗口：顺向破 `success edge` 才允许 entry；反向破 `failure edge` 直接否决；超时则 `timeout`
- **trade off**：没有 base trigger 时不能单独开仓；若 clean replication 证明改善只来自大砍样本、只在单一 symbol 偶然成立、或只能靠事后挑最好窗口，那就应直接 `park`。

### 2) lookahead / repaint / leakage
- `pullback`、`window`、`success/failure/timeout` 全部只能用 **signal 当根及之前可见** 的 OHLC / ATR / rolling extrema 定义。
- clean replication 必须统一到 **`next-bar open + no-overlap`**，禁止同 bar 既判断 breakout 又按同 bar 成交。
- `pullback depth`、`offset`、`window bars` 只能在训练段冻结，再去测试段验证；禁止全样本 / 事后最优。
- `timeout` 必须是一级状态，不能在结果不好看时再事后补 `late-entry veto`。

## 最诚实的当前结论
- 当前 hard verdict：**`Rank 114 = guard-passed / admit_to_clean_replication_queue`**。
- 翻成人话：这条线值得拿 **1 次最小 clean replication** 预算，因为它提供的是一个可同时服务 `breakout-short / Fib / EMA-PSAR` 的共享 entry skeleton；但它当前还只是 repo-based 的执行骨架，不是已验证 alpha，更不配抢 `Live Seat`。

## 为什么这轮不继续做 clean replication
- 顶板 `Next 3` 对这一轮的授权只到 `Rank 114 source intake`。
- 本轮已经完成：
  - `Run 1` 的真实 due-check
  - `Run 2` 的 source intake + 两条轻量诚实守门
- 再往前推进到 clean replication 会超出“1 个主点 + 1 个紧邻子点”的预算，也会违反这轮板子给 `Rank 114` 的顺序控制。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`：
  1. 只给 `Rank 114` **1 次最小 clean replication**；
  2. 固定复用 `BTC/ETH/SOL 120d 15m` 本地 cache；
  3. 只挂 `1` 条 archetype（优先 `breakout-short` 或 `fib_retest_long`）；
  4. 训练段冻结 `pullback depth + offset + window bars` 各 `1` 组；
  5. 测试段统一 `next-bar open + no-overlap` 比较 `baseline direct entry` vs `window verdict`；
  6. 若改善主要来自砍样本、没有更诚实的成本后 uplift，就直接 `park`；若至少 `2` 个 symbol 上保留 honest improvement，才考虑升到 `P2 / paper candidate pool`。

## 验证 / 证据
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回 `waiting_not_due`；在 `require-due` 模式下以 code `2` 退出，属于预期等待路径。
- source digest：`research/quant_digests/2026-03-20_0742_pullback-two-sided-window-verdict.md`
- 新 reader-facing artifact：
  - `reports/artifacts/literature/scout_rank114_pullback_two_sided_window_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank114_pullback_two_sided_window_source_intake.html`

## 风险 / 边界
- repo 来源是 `XAUUSD 5m`，不是 crypto perp；它当前只能作为 execution skeleton 候选，不能把作者自报回测当作 crypto 证据。
- 这条线最容易犯的错，就是把 pullback/window/timeout 做成事后挑参数的包装层；下一轮 clean replication 必须严格 train-freeze / test-verify。

## Commit hash
- 未提交。

## 未提交原因
- 当前 git 工作区存在大量与本轮无关的已修改/未跟踪文件；为避免混提，本轮只保留本轮 source intake artifact、reader-facing 页面、顶板 write-back 与日志。
