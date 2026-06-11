# 2026-03-18 16:56 UTC — Rank 60 / FVG-BOS imbalance retest gate source intake

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最近一次托管刷新为 `2026-03-18T16:45:11Z`，`new_closed_trades_appended=0`，当前不构成比 fresh Scout intake 更高优先级的 `P3` 抢占理由。
- 因此这轮不能把 `waiting_not_due` 误读成整桌等待；合法主动作仍是 `Run 2 / Rank 60 source intake + 两条轻量诚实守门`。
- 按当前 active Scout 边际价值比较：`Rank 60 / FVG-BOS imbalance retest gate` `>` `Rank 61 / lower-TF volume-delta polarity mismatch veto` `>` `continuation fail-fast overlay` `>` `pullback-quality / CQI` `>` `Rank 35b` `>` `Rank 16b` `>` `tiny-live plumbing`。原因不是 Rank 60 已经更强，而是它更贴三条主线共同缺的 shared continuation syntax，只依赖现有 `15m OHLCV`，比 Rank 61 少一层 lower-TF 对齐摩擦。

## 做了什么改动
### 主点：完成 Rank 60 source intake + 两条轻量诚实守门
- 新增 source-intake artifact：
  - `reports/artifacts/literature/scout_rank60_fvg_bos_imbalance_retest_source_intake_card.csv`
- 新增 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_source_intake.html`

### 紧邻子点：最小 authoritative writeback
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 16:56 UTC` 补充：
  - 把这轮结果冻结为 **`Rank 60 = guard-passed / admit_to_clean_replication_queue`**；
  - 写回与 `Rank 61 / continuation fail-fast overlay / pullback-quality / CQI` 的当前边际价值比较；
  - 把当前 `Next 3` 收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = 若 Rank 60 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
    - `Run 3 = 若 Rank 60 clean replication 后仍不能给出更高层 verdict，则转去比较 Rank 61 > continuation fail-fast overlay > pullback-quality / CQI；只有这一层也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 守门结论 / 证据
### 1）trade on / trade off 已能冻结
- `trade on`：base setup 继续负责方向与价位；`BOS` 只负责回答是否刚完成顺势扩展，`FVG / VI retest` 只负责回答扩展后的回头是否仍被同方向 imbalance zone 接住。第一轮冻结成：最近 `N=8` 根内先出现 confirmed BOS，再要求 price 回踩到同向 `FVG` 或更窄的 `VI` 区间，并以收盘仍站在正确一侧才放行。
- `trade off`：若没有先出现 confirmed BOS、gap 只是随机跳空盒子、price 回头直接收回 imbalance zone 另一侧，或 retest 发生在逆势 / 无 bias 场景，就不把它当 continuation；它也不能单独开仓，只能给 breakout-short / Fib / EMA-PSAR 三条既有 setup 做 shared gate。

### 2）为什么没有被 honesty gate 直接判死刑
- `Trade-Sense` 里 `BOS / FVG / VI` 都能冻结成可枚举事件：
  - `BOS`：用最近 confirmed swing 的 `close` 穿越判断；
  - `FVG`：用三根 K 的 `low[t] > high[t-2]` / `high[t] < low[t-2]` 判断；
  - `VI`：用更窄的一根错位 gap 判断。
- 上述定义都只依赖 signal 当根及之前数据，本轮未见一眼可判死刑的 `lookahead / repaint / leakage`。
- 当前最需要防的不是指标未来函数，而是**把 liquidity sweep / premium-discount / HTF bias / community wording 一起偷渡进第一轮**。
- 这轮已把 desk 迁移时的诚实约束写死为：**`confirmed swing + signal 当根及之前数据 + next-bar open + no-overlap`**，并且先拆成 `BOS only / BOS+FVG / BOS+VI` 三臂；当前还不是新 alpha，只是 shared continuation gate 候选。

## 当前硬结论
- **`Rank 60 / FVG-BOS imbalance retest gate = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 1 次最小 clean replication 预算，但现在还只是 shared continuation syntax 候选，不是新的 alpha，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 60` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d~180d 15m` cache；
  - 只比较四臂：`base`、`+BOS_only`、`+BOS+FVG_retest`、`+BOS+VI_retest`；
  - 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
  - 先看四个便宜指标：`post_cost_return@6bps`、`trade_count_retention`、`4~8 bar failure rate`、`positive_asset_ratio`。
- 若改善主要来自极端减样本、只在单一 archetype 上成立、或 FVG / VI 只是给 BOS 换词包装，就快速压回 `park / evidence pool`。

## 最小验证
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank60_fvg_bos_imbalance_retest_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 16:56 UTC` 补充。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank60_fvg_bos_imbalance_retest_source_intake.html`
- 原始 digest：`reports/site/reading/quant_digests/2026-03-18_1559_fvg-bos-imbalance-gate.html`

## Git / 风险备注
- 当前 git 工作区存在大量与本轮无关的既有脏文件与未跟踪产物，未做 commit，避免混提。
- 本轮只做了最小必要写回：`docs/TODO.md` 顶板更新 + `Rank 60` source-intake artifact / reader-facing 页面 + 本轮日志。
