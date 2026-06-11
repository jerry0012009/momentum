# 2026-03-20 05:13 UTC — Rank 110 / PSAR pre-flip SAR dot reclaim gate source intake（guard-passed）

## Run 1 -> Run 2 执行
- Run 1：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：`EMA = waiting_not_due`
  - 当前没有 `due-now / overdue` lane
  - 最近 due：`A股三条 lane -> 2026-03-20 07:00 UTC`（约 `1.8h`）
  - `require-due` guard 正常触发（exit code `2`），没有伪造 refresh
- 因此按当前 `TRADING DESK BOARD` 的 authoritative `Next 3`，本轮合法主动作只能切到 `Scout Seat`。

## 开轮检查
- branch：`master`
- repo 脏文件：`git status --short | wc -l = 1676`
- 最近 optimization logs：
  - `2026-03-20_0448_rank109-clean-replication-park.md`
  - `2026-03-20_0418_rank109-htf-premium-discount-intake.md`
  - `2026-03-20_0358_rank108-clean-replication-park.md`
  - `2026-03-20_0334_rank108-prebreak-intake.md`
- 当前席位直读：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 本轮前 `Scout Seat = Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T04:39:11Z` 仍是 `new_closed_trades_appended=0`，因此当前没有新的 `P3 status-changing event` 可以挤掉 fresh Scout 主链。

## Active Scout 候选边际比较（先比较后认领）
1. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
   - `Rank 109` 已在上轮最小 clean replication 后压回 `park / evidence pool`，因此这条线成了当前唯一 queue-facing 的 fresh repo 候选。
   - 直接服务 `EMA / PSAR raw alpha focus`，且下一手就是最便宜的 `source intake + 两条轻量诚实守门`。
2. **fresh paper / repo intake reserve**（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
   - 只有 `Rank 110` 明确 `hard-fail / exhausted` 后才该前移。
3. **旧 `P1 evidence_pool` / `P3 continuity` / `tiny-live plumbing`**
   - 当前都不该挤掉这轮 queue-facing Scout 主链。

结论：本轮只认领 `Rank 110`，不并开其他候选。

## 本轮认领
- 主点：`Rank 110 / PSAR pre-flip SAR dot reclaim gate` 的 `source intake + 两条轻量诚实守门`
- 紧邻子点：同步 reader-facing 落点、顶板顺序刷新

## 本轮动作
- 复核来源：`research/quant_digests/2026-03-20_0354_psar-preflip-dot-reclaim-not-shared-gate.md`
- 新增生成脚本：`scripts/build_rank110_psar_preflip_source_intake.py`
- 执行生成：`python3 scripts/build_rank110_psar_preflip_source_intake.py`
- 生成产物：
  - `reports/artifacts/literature/scout_rank110_psar_preflip_dot_reclaim_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_dot_reclaim_source_intake.html`
- 顶板最小回写：`docs/TODO.md` 的 `Next 3 bot3 runs`

## 两条轻量诚实守门（本轮冻结）
### 1) trade on / trade off
- **trade on**：只把 `pre-flip SAR dot reclaim` 当 continuation admission gate，不单独创造方向。先有 `PSAR flip`，再在固定 `nBars` 窗口内只用 `signal 当根及之前数据` 检查价格是否 reclaim `pre_flip_dot`。
- 首轮默认只把它写成 **long-side optional filter**：bullish gate=`先出现 bullish PSAR flip，随后在 nBars 内出现 open < pre_flip_dot 且 close > pre_flip_dot`，再叠 `EMA side` 作为 continuation 放行。
- **trade off**：若改善主要来自大砍样本、而不是把 `post-cost expectancy` 与 `fail-rate` 一起改善，就不得把它包装成 shared admission layer；若 short 侧没有一致帮助甚至更差，也不得镜像成对称 short gate。它不能替代原始 `EMA / PSAR` trigger，更不能把 repo 里的 `squeeze / volatility` 厚模板偷渡进当前最小问题。

### 2) lookahead / repaint / leakage
- `pre_flip_dot` 只能取 flip 前最后一个已确认 `SAR dot`
- reclaim 检查只能用 `signal 当根及之前数据`
- 下一轮 clean replication 强制 `next-bar open + no-overlap`
- 禁止 future bars 延长 reclaim 窗口、禁止同 bar 成交、禁止事后重配 `nBars`、禁止只报 long 侧较好结果后偷渡成多空共享 gate

## 当前硬结论
**`Rank 110 = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线值得拿 **1 次最小 clean replication** 预算；
- 但当前最该验证的，不是“它是不是 shared alpha”，而是“它是不是只配做 `long-side optional filter / continuation admission gate`”。

## 对顶板的直接影响
- `Paper Seat = EMA / running paper / waiting_not_due`
- `Live Seat = 暂空`
- `Scout Seat = Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- 当前更诚实的 active Scout 顺序：
  1. `Rank 110 / PSAR pre-flip SAR dot reclaim gate`
  2. `fresh paper / repo intake reserve`
  3. `Rank 93 / 90 / 91 / 82 / 80 / 81`（`P1 evidence_pool / budget used`）
  4. `Rank 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`（`P0 park / evidence pool`）
  5. `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（`P3 continuity / hosted lanes / sidecar only`）
- 当前 `P2` 仍空、`P4` 仍空。
- 最新 `Next 3`（本轮后）：
  1. `Run 1 = EMA due-check only（优先盯 A股三条 lane -> 2026-03-20 07:00 UTC）`
  2. `Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 110 / PSAR pre-flip SAR dot reclaim gate 1 次最小 clean replication`
  3. `Run 3 = 若 Rank 110 clean replication 直接 hard-fail / exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`

## 本轮交付（deployable artifact）
- script：`scripts/build_rank110_psar_preflip_source_intake.py`
- artifact：`reports/artifacts/literature/scout_rank110_psar_preflip_dot_reclaim_source_intake_card.csv`
- reader-facing 页面：`reports/site/reading/repo_scout/rank110_psar_preflip_dot_reclaim_source_intake.html`
- 顶板刷新：`docs/TODO.md`

## 最小验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank110_psar_preflip_source_intake.py`
- 回读确认：
  - `reports/artifacts/literature/scout_rank110_psar_preflip_dot_reclaim_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank110_psar_preflip_dot_reclaim_source_intake.html`
  - `docs/TODO.md`

## 风险 / 边界
- 这轮只完成了 intake + 两条守门，**没有**把它升格成已验证 alpha。
- 当前 source 更像 repo 工程模板，不是学术论文级结论；下一轮必须用最小 clean replication 直接回答它到底是 `keep_P1 / promote_to_P2 / park`。
- 当前工作区有大量与本轮无关的脏文件，因此不安全混提。

## Commit hash
- 未提交。
- 原因：工作区存在大量无关脏文件（`1676` 项），本轮只做局部产物与顶板回写，不适合混提。
