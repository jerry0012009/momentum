# 2026-03-18 13:15 UTC — Rank 56 / liquidation-map path overlay source intake

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane。
- 当前 due guardrail 仍是：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最近一次托管刷新仍为 `2026-03-18T13:07:40Z` 且 `new_closed_trades_appended=0`，说明当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。
- 因此这轮合法主动作仍是 `Run 2 / Scout Seat`。按当前允许动作重新比较边际价值后，继续认领 **`Rank 56 / liquidation-map path overlay`**，而不是回头磨 `Rank 55` 的 `P1` 检查或退到 `Rank 35b / tiny-live plumbing`。

## 做了什么
### 主点：完成 Rank 56 source intake + 两条轻量诚实守门
- 新增构建脚本：
  - `scripts/build_rank56_liquidation_map_source_intake.py`
- 运行脚本后生成 intake artifact：
  - `reports/artifacts/literature/scout_rank56_liquidation_map_path_overlay_source_intake_card.csv`
- 生成 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_source_intake.html`

### 紧邻子点：authoritative board 最小写回
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 13:12 UTC` 补充：
  - 把这轮结果正式冻结为 **`Rank 56 / liquidation-map path overlay = guard-passed / admit_to_clean_replication_queue`**；
  - 写回 `trade on / trade off` 与 `no-lookahead / no-leakage` 口径；
  - 把当前 `Next 3` 收紧成：
    - `Run 1 = EMA due-check only`
    - `Run 2 = 若 Rank 56 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
    - `Run 3 = 若 Rank 56 clean replication 不能给出更高层 verdict，再回到 Rank 55 那 1 次便宜时间稳定性检查，直接做 P2 / park 判断；若两者都不成立，再比较 Rank 35b > Rank 16b > tiny-live plumbing`

## 证据与守门结论
### 1）为什么它通过了 source intake 的两条轻量守门
- `trade on`：base setup 继续负责方向与价位；`liquidation-map / cluster_path_score` 只负责回答“入场后前方顺势清算燃料是否明显强于反方向陷阱”。
  - long 侧：上方 `short-liquidation fuel` 相对下方 `long-cascade trap` 更占优时，才允许作为 path gate / size tilt；
  - short 侧镜像。
- `trade off`：若 `cluster_path_score` 接近中性、顺势 fuel 不明显、或反方向 trap 更近，则它只能做 `veto / 降仓`，不能单独开仓。
- 这让它更像 shared path/risk overlay，而不是第四条新 entry 框架。

### 2）为什么它没有被 honesty gate 直接判死刑
- repo README 与源码都显示：其核心不是神秘黑箱，而是 **把公开 `aggTrades` 中的大额主动成交映射到固定杠杆假设下的潜在 loss-cut 价位**。
- 关键源码口径：
  - `Buy` 成交映射到 `0.99 / 0.98 / 0.96 / 0.90` 倍价位（近似 `100x / 50x / 25x / 10x` long liquidation proxy）
  - `Sell` 成交映射到 `1.01 / 1.02 / 1.04 / 1.10` 倍价位（short 侧镜像）
  - 支持 `>=100k USDT`、`top_n`、`top 1%` 三种筛选模式
- 这套逻辑本身没有一眼可见的 `lookahead / repaint`；真正的风险在 desk 迁移时：
  1. 误把图像直觉写成 15m 方向 alpha；
  2. 把 signal 后成交倒灌回 `cluster_path_score`；
  3. 忘了这只是 crowding/path proxy，不是真实 liquidation tape。
- 因此本轮已把诚实性前提明确写死为：**下一轮 clean replication 必须严格冻结到 `signal 前 6h/24h 窗口 + next-bar open + no-overlap`**。

## 当前硬结论
- **`Rank 56 / liquidation-map path overlay = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 1 次最小 clean replication 预算，但现在还只是 shared overlay 候选，不是 live seat 挑战者，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 56` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d~180d 15m` cache；
  - 对 signal 前 `6h / 24h` 的 `aggTrades` 计算 `cluster_path_score`；
  - 只比较三臂：`base`、`+binary path gate`、`+size tilt`；
  - 先看四个便宜指标：`post_cost_return@6bps`、`false_follow_through_4bars`、`trade_count_retention`、`positive_asset_ratio`。
- 若改善只来自极端砍样本、只在单一 archetype 上成立、或跨资产不稳，就快速压回 `park / evidence pool`。

## 最小验证
- 已运行：`python3 scripts/build_rank56_liquidation_map_source_intake.py`
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank56_liquidation_map_path_overlay_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 13:12 UTC` 补充。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank56_liquidation_map_path_overlay_source_intake.html`
- `reports/site/plans/momentum_todo.html`（发布后可见）
- 原始 digest 证据页：`reports/site/reading/quant_digests/2026-03-18_1255_liquidation-map-path-overlay.html`

## Git / 风险备注
- 当前 git 工作区存在大量与本轮无关的脏文件与未跟踪产物，未做 commit，避免混提。
- 本轮只做了最小必要写回：新增 1 个 source-intake script、1 个 CSV、1 个 reader-facing HTML，以及 `docs/TODO.md` 顶板更新。
