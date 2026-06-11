# 2026-03-18 15:05 UTC — Rank 58 / event-anchored VWAP hold-reclaim spine source intake

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane：
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`，最近一次托管刷新为 `2026-03-18T14:55:38Z`，且 `new_closed_trades_appended=0`，说明当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。
- 因此这轮不能把 `waiting_not_due` 误读成整桌等待；合法主动作仍是 `Run 2 / Scout Seat`。
- 按当前 active Scout 边际价值比较：`Rank 58 / event-anchored VWAP hold-reclaim spine` `>` `continuation fail-fast overlay` `>` `pullback-quality score / CQI` `>` `Rank 35b` `>` `Rank 16b` `>` `tiny-live plumbing`。这条线直接修正了 `Rank 51 / session VWAP` 在 24/7 crypto 上暴露出的 session 任意性，而且更像可横向服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 三条主线的 shared hold-reclaim spine。

## 做了什么改动
### 主点：完成 Rank 58 source intake + 两条轻量诚实守门
- 新增 source-intake artifact：
  - `reports/artifacts/literature/scout_rank58_event_anchored_vwap_source_intake_card.csv`
- 新增 reader-facing 页面：
  - `reports/site/reading/repo_scout/rank58_event_anchored_vwap_source_intake.html`

### 紧邻子点：最小 authoritative writeback
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 15:05 UTC` 补充：
  - 把这轮结果冻结为 **`Rank 58 = guard-passed / admit_to_clean_replication_queue`**；
  - 写回 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage` 口径；
  - 把当前 `Next 3` 收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = 若 Rank 58 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
    - `Run 3 = 若 Rank 58 clean replication 后仍不能给出更高层 verdict，则再比较 continuation fail-fast overlay > pullback-quality / CQI > fresh pool 其他 source；只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 守门结论 / 证据
### 1）trade on / trade off 已能冻结
- `trade on`：base setup 继续负责方向与价位；event AVWAP 只负责回答某个**预先冻结的事件锚点**（`breakout/breakdown confirm bar`、`最近确认 swing high/low`、或 `Fib leg 起点 bar`）之后，价格是否仍守在这段新库存成本线强侧。默认只在 `close` 站回对应 `A_VWAP(anchor)` 强侧，或最近 `3` 根里至少 `2` 根维持在强侧时，才允许它作为 shared hold/reclaim gate；可选再叠 `|close-A_VWAP| < 0.5*ATR14` 只做 proximity 确认。
- `trade off`：若锚点类别没有预先冻结、只是事后挑“最好看”的 anchor，或价格只是一根刺穿但没有真正 reclaim / hold，event AVWAP 只能算证据，不算可交易 gate；它也不能单独开仓，只能给现有 `breakout-short / Fib / EMA` setup 做 shared confirmation。

### 2）为什么没有被 honesty gate 直接判死刑
- 两个 repo 的共同核心都是把 `A_VWAP(anchor) = cumsum(Typical*Volume) / cumsum(Volume)` 写成可复用代码；它依赖的是 anchor 之后的 trailing OHLCV，而不是未来窗口。
- 当前没有一眼可见的 `lookahead / repaint / leakage`；真正需要防的是 **anchor 选择自由度**。
- 这轮已把 desk 迁移时的诚实约束写死为：**anchor 类别提前冻结 + signal 当根及之前数据 + next-bar open + no-overlap**，并且只把它降级成 shared hold/reclaim gate，而不是新的一套独立 alpha。

## 当前硬结论
- **`Rank 58 / event-anchored VWAP hold-reclaim spine = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 1 次最小 clean replication 预算，但现在还只是 shared confirmation 候选，不是 live seat 挑战者，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 58` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d~180d 15m` cache；
  - 只比较四臂：`base`、`+session_vwap_gate`、`+event_avwap_gate`、`+event_avwap_gate+0.5ATR proximity`；
  - 统一冻结到 `signal 当根及之前数据 + next-bar open + no-overlap + hold 8 bars`；
  - 先看四个便宜指标：`post_cost_return@6bps`、`false_hold / false_follow_through rate`、`trade_count_retention`、`positive_asset_ratio`。
- 若改善只来自极端减样本、跨资产不稳、或只在单一 anchor 类别上成立，就快速压回 `park / evidence pool`。

## 最小验证
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank58_event_anchored_vwap_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank58_event_anchored_vwap_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 15:05 UTC` 补充。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank58_event_anchored_vwap_source_intake.html`
- 原始 digest：`reports/site/reading/quant_digests/2026-03-18_1500_event-anchored-vwap-hold-gate.html`

## Git / 风险备注
- 当前 git 工作区存在大量与本轮无关的既有脏文件与未跟踪产物，未做 commit，避免混提。
- 本轮只做了最小必要写回：`docs/TODO.md` 顶板更新 + `Rank 58` source-intake artifact / reader-facing 页面 + 本轮日志。
