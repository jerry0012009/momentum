# 2026-03-18 15:37 UTC — Rank 59 / Ichimoku Kijun + cloud-side continuation gate source intake

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`：最近一次托管刷新为 `2026-03-18T15:19:15Z`，虽然 `new_closed_trades_appended=2`，但当前并不构成比 fresh Scout intake 更高优先级的 `P3` 抢占理由；按顶板顺序，`EMA = waiting_not_due` 时仍应优先做 `Scout Seat`。
- 因此这轮不能把 `waiting_not_due` 误读成整桌等待；合法主动作仍是 `Run 2 / fresh paper-repo intake`。
- 按当前 active Scout 边际价值比较：`Rank 59 / Ichimoku Kijun + cloud-side continuation gate` `>` `continuation fail-fast overlay` `>` `pullback-quality score / CQI` `>` `Rank 35b` `>` `Rank 16b` `>` `tiny-live plumbing`。原因不是 Ichimoku 已经更强，而是它更贴 15m continuation 的 shared 结构问题，只依赖现有 OHLCV，比 fail-fast overlay 更少受 session VWAP 语义拖累，也比 CQI 更少带着 `4H/Daily long-only` 迁移负担。

## 做了什么改动
### 主点：完成 Rank 59 source intake + 两条轻量诚实守门
- 新增 source-intake artifact：
  - `reports/artifacts/literature/scout_rank59_ichimoku_kijun_cloud_source_intake_card.csv`
- 新增 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_source_intake.html`

### 紧邻子点：最小 authoritative writeback
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 15:37 UTC` 补充：
  - 把这轮结果冻结为 **`Rank 59 = guard-passed / admit_to_clean_replication_queue`**；
  - 写回与 `continuation fail-fast overlay / pullback-quality score / CQI` 的当前边际价值比较；
  - 把当前 `Next 3` 收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = 若 Rank 59 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
    - `Run 3 = 若 Rank 59 clean replication 后仍不能给出更高层 verdict，则再比较 continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source；只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 守门结论 / 证据
### 1）trade on / trade off 已能冻结
- `trade on`：base setup 继续负责方向与价位；Kijun / cloud-side 只负责回答价格是否仍站在更慢的结构防守线外。第一轮冻结成：
  - long：`close > cloud_top` 且 `tenkan > kijun`
  - short：镜像
  - `retest_hold` 放宽版：最近 `3` 根里至少 `2` 根收在 Kijun 正确一侧，且最新收盘不回云内
- `trade off`：若价格仍在云内、Tenkan/Kijun 尚未翻到顺势侧、或只是同 bar 一次刺穿后马上收回，就不把它当 continuation gate；它也不能单独开仓，只能给现有 `breakout-short / Fib / EMA` setup 做 shared confirmation。

### 2）为什么没有被 honesty gate 直接判死刑
- `Tenkan / Kijun / cloud` 都能用 trailing high-low 中值滚动构造，不依赖未来窗口，本轮未看到一眼可判死刑的 `lookahead / repaint / leakage`。
- 当前最需要防的不是“指标本身未来函数”，而是**把整套 Ichimoku tuned preset 和时间 veto 一起偷渡进第一轮**。
- 这轮已把 desk 迁移时的诚实约束写死为：**`signal 当根及之前数据 + next-bar open + no-overlap`**，并且先拆成 `kijun_only / cloud_side / kijun+cloud_side` 分臂；Chikou、RSI、时间过滤、BE/trailing 都暂不进入第一轮最小复现。

## 当前硬结论
- **`Rank 59 / Ichimoku Kijun + cloud-side continuation gate = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 1 次最小 clean replication 预算，但现在还只是 shared continuation gate 候选，不是新的 alpha，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 59` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d~180d 15m` cache；
  - 只比较五臂：`base`、`+kijun_only`、`+cloud_side`、`+kijun+cloud_side`、`+kijun+cloud_side+adx_floor`；
  - 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
  - 先看四个便宜指标：`post_cost_return@6bps`、`trade_count_retention`、`4~8 bar failure rate`、`winner_truncation_rate`。
- 若改善主要来自极端减样本、只在单一 archetype 上成立、或 cloud-side 只是换个名字重复 EMA 方向投票，就快速压回 `park / evidence pool`。

## 最小验证
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank59_ichimoku_kijun_cloud_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 15:37 UTC` 补充。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank59_ichimoku_kijun_cloud_source_intake.html`
- 原始 digest：`reports/site/reading/quant_digests/2026-03-18_1531_ichimoku-kijun-cloud-gate.html`

## Git / 风险备注
- 当前 git 工作区存在大量与本轮无关的既有脏文件与未跟踪产物，未做 commit，避免混提。
- 本轮只做了最小必要写回：`docs/TODO.md` 顶板更新 + `Rank 59` source-intake artifact / reader-facing 页面 + 本轮日志。
