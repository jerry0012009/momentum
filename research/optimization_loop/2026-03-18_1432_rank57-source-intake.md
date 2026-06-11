# 2026-03-18 14:32 UTC — Rank 57 / TTM squeeze release regime gate source intake

## 为什么这轮轮到它
- 先按 `TRADING DESK BOARD` 执行 `Run 1`：重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`，当前仍没有新的 `due-now / overdue` lane。
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`
  - `A股三条 lane -> 2026-03-19 07:00 UTC`
- 同时检查 `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`，最近一次托管刷新为 `2026-03-18T14:29:23Z`，且 `new_closed_trades_appended=0`，说明当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。
- 因此这轮不能把 `waiting_not_due` 误读成整桌等待；合法主动作仍是 `Run 2 / Scout Seat`。
- 按当前 active Scout 边际价值比较：`Rank 57 / TTM squeeze release regime gate` `>` `pullback-quality score / CQI` `>` `Rank 35b` `>` `Rank 16b` `>` `tiny-live plumbing`。这条线只依赖现有 `15m OHLCV`，更像可横向服务 `breakout-short / Fib retest_hold / EMA-PSAR` 的 shared `avoid-chop / expansion-confirmation` gate，边际价值高于回头磨已退到 evidence pool 的 `Rank 55 / 56`。

## 做了什么改动
### 主点：完成 Rank 57 source intake + 两条轻量诚实守门
- 复用并执行已有 intake 脚本：
  - `python3 scripts/build_rank57_ttm_squeeze_source_intake.py`
- 产物确认：
  - `reports/artifacts/literature/scout_rank57_ttm_squeeze_release_regime_gate_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_source_intake.html`

### 紧邻子点：最小 authoritative writeback
- 在 `docs/TODO.md` 顶部权威区追加 `2026-03-18 14:32 UTC` 补充：
  - 把这轮结果冻结为 **`Rank 57 = guard-passed / admit_to_clean_replication_queue`**；
  - 写回 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage` 口径；
  - 把当前 `Next 3` 收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = 若 Rank 57 已 guard-passed 且 EMA 仍 waiting_not_due，则立刻给它 1 次最小 clean replication`
    - `Run 3 = 若 Rank 57 clean replication 后仍不能给出更高层 verdict，则按 7.10 再认领 1 条 fresh paper/repo source；只有 fresh pool 也 exhausted 时，才回退到 Rank 35b > Rank 16b > tiny-live plumbing`

## 守门结论 / 证据
### 1）trade on / trade off 已能冻结
- `trade on`：base setup 继续负责方向与价位；TTM squeeze 只负责回答当前是否仍困在低波压缩里，或是否刚从 squeeze release 切到扩张窗口。默认只在 `sqz_on=0` 且最近 `1~4` 根内刚从 `sqz_on -> sqz_off / release` 时，才允许它作为 shared regime gate；可选再叠 `momentum_sign` 只做方向一致确认。
- `trade off`：若仍处在 `sqz_on`、release 已过久、或 `momentum_sign` 与 base 方向不一致，则 overlay 只能 `veto / 延后`，不能单独开仓，也不能把低波压缩状态偷换成主 alpha。

### 2）为什么没有被 honesty gate 直接判死刑
- `hackingthemarkets/ttm-squeeze` 直接把 squeeze 写成 `BB(20,2)` 是否完全包在 `KC(20,1.5*ATR)` 内，并检测从 `squeeze_on` 到非 squeeze 的 `release`。
- `GiustiRo/squeezem-adx-ttm` 也明确写出 `sqzOn / sqzOff` 与线性回归 momentum 的组合读法。
- 上述状态都可只用 signal 当根及之前数据计算；当前没有一眼可见的 `lookahead / repaint / leakage`。
- 这轮已把 desk 迁移时的诚实约束写死为：**`signal 当根及之前数据 + next-bar open + no-overlap`**，并且只把它降级成 shared `avoid-chop / expansion-confirmation` gate，而不是第四条 entry alpha。

## 当前硬结论
- **`Rank 57 / TTM squeeze release regime gate = guard-passed / admit_to_clean_replication_queue`**。
- 更直白地说：这条线值得拿 1 次最小 clean replication 预算，但现在还只是 shared overlay 候选，不是 live seat 挑战者，也不配跳过最小复现直接升级。

## 下一轮只允许做什么
- 若下一轮 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 57` **1 次最小 clean replication**：
  - 固定 `BTC / ETH / SOL 120d~180d 15m` cache；
  - 只比较四臂：`base`、`+no_sqz_on_veto`、`+release_recent_gate(1~4 bars)`、`+release_recent_gate+momentum_sign`；
  - 统一冻结到 `next-bar open + no-overlap + hold 8 bars`；
  - 先看四个便宜指标：`post_cost_return@6bps`、`whipsaw_2bars/4bars`、`trade_count_retention`、`positive_asset_ratio`。
- 若改善只来自极端减样本、跨资产不稳、或只在单一 archetype 上成立，就快速压回 `park / evidence pool`。

## 最小验证
- 已执行：`python3 scripts/build_rank57_ttm_squeeze_source_intake.py`
- 已确认产物存在：
  - `reports/artifacts/literature/scout_rank57_ttm_squeeze_release_regime_gate_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_source_intake.html`
- 已确认 `docs/TODO.md` 顶部写回包含 `2026-03-18 14:32 UTC` 补充。

## Reader-facing 落点
- `reports/site/reading/repo_scout/rank57_ttm_squeeze_release_regime_gate_source_intake.html`
- 原始 digest：`reports/site/reading/quant_digests/2026-03-18_1328_ttm-squeeze-release-regime-gate.html`

## Git / 风险备注
- 当前 git 工作区存在大量与本轮无关的既有脏文件与未跟踪产物，未做 commit，避免混提。
- 本轮只做了最小必要写回：`docs/TODO.md` 顶板更新 + `Rank 57` source-intake artifact / reader-facing 页面确认 + 本轮日志。