# 2026-03-17 11:55 UTC · Rank 34 chip-distribution source intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`Paper Seat / EMA` 继续处于 `waiting_not_due`；最新 due guardrail 仍显示全 desk 没有 `due-now / overdue` lane，因此按顶板从 `Run 1` 自动切到 `Run 2`，不允许在 waiting-window 空转。

## repo / 最近 runs / 脏文件 / 席位状态检查
- `git status --short`：仓库内仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只做 selective 改动，不混提。
- 最近 optimization runs：`1150 rank33-clean-replication-park`、`1128 rank33-nw-hl-reclaim-intake`、`1123 rank32-clean-replication-park`。
- `Paper Seat / EMA`：继续 `waiting_not_due`；最近后续动作仍是 `美股 1d+1wk -> 2026-03-17 20:00 UTC`、`Crypto 1d+1wk -> 2026-03-18 00:00 UTC`、A 股三条 lane `-> 2026-03-18 07:00 UTC`。
- `Live Seat`：未收到 bot2 新 promoted candidate，继续空席。

## active Scout 候选边际价值比较（本轮前）
- `Rank 17 / Rank 2 / Rank 29`：都在 `P3`，当前没有新的真实 `append/review` need；继续补近义 wiring 边际价值低。
- `Rank 30 / Rank 31 / Rank 32 / Rank 33`：都已完成当前允许动作并压回 `park / evidence pool`，不应立刻重开。
- `Rank 5 / Rank 6`：仍偏外部数据 / 外部代理，不符合当前默认的 `paper / repo based 5m / 15m crypto` cheapest honest 动作。
- `chip_distribution`：虽然比 `Rank 33` 多一层 `shares / turnover` 假设风险，但它是现有 repo 中尚未被 desk 正式消费、同时仍贴近 `support / reclaim / trapped-holder` 语义的因子模块。
- **结论**：本轮默认主资源不应再磨旧 P3，也不该重开 `Rank 30~33`；当前最高边际价值动作是把 `chip_distribution` 压成新的 repo-based `fresh intake`，并把最大的诚实门槛——`synthetic shares / turnover anchors`——提前写死。

## 本轮主点 + 紧邻子点
- **主点**：把 `Rank 34 chip-distribution trapped-holder reclaim / winner-ratio gate` 落成新的 fresh-intake artifact。
- **紧邻子点**：同步更新 `docs/TODO.md` 和 `reports/site/reading/trendline_alpha_scout/report.html`，避免下一轮又退回抽象“继续 fresh intake”。

## 为什么选 Rank 34，而不是别的 fresh 线
- 这条线直接来自当前 repo 已存在的因子模块：`src/momentum/factors/chip_distribution.py` + `docs/CHIP_DISTRIBUTION.md`；不是凭空发明新框架。
- 它比 `Rank 5 / Rank 6` 更符合当前 top board：不需要 prediction-market / equity proxy 等额外外部市场数据。
- 它比继续围绕 `Rank 17 / Rank 2 / Rank 29` 做 admission / monitoring 近义接线更贴近当前仍存活的 `support / reclaim` 家族。
- 它虽然不如 `Rank 33` 那样完全摆脱假设，但 `Rank 33` 已 park 后，当前最诚实的下一步不是假装继续有新结构线，而是把 `shares 假设` 明写成 first-class blocker 的 repo-based 候补。

## 两条轻量诚实守门（进入 intake 前）
1. **trade on / trade off 能写清楚**
   - `trade on = higher_tf_bias_up=1，且价格在一次 pullback 后重新站回估算 cost_p50 / avg_cost 带上方，同时 winner_ratio 从拥挤区下缘回升到阈值之上`
   - `trade off = higher_tf_bias 缺失或反向；价格始终站不回 cost 带；winner_ratio 不恢复，或 trapped_ratio 继续抬升导致所谓 reclaim 只是拥挤反弹`
2. **没有偷塞 lookahead / repaint，但必须正视 shares 假设**
   - `chip_distribution` 只能逐 bar 递推，不能用未来成交回填历史 `chip_pct`；
   - 但分钟级 crypto 没有天然 shares，因此下一轮 clean replication 必须先过 `synthetic shares / turnover anchors` 的敏感度诚实门槛，不能把估算筹码伪装成真实账本。

## 本轮产物
1. 新脚本
- `scripts/build_rank34_chip_distribution_source_intake.py`

2. 新 artifact
- `reports/artifacts/literature/scout_rank34_chip_distribution_source_intake_card.csv`

3. 新 reader-facing 页面
- `reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html`

4. 更新入口 / 顶板
- `docs/TODO.md`
  - 新增 `Rank 34 chip-distribution trapped-holder reclaim / winner-ratio gate`
  - 将 `Next 3 bot3 runs` 的 authoritative override 改成：若 `Rank 29 / Rank 17 / Rank 2` 仍无真实动作，下一轮默认只允许给 `Rank 34` 做 1 次带 `synthetic shares / turnover anchor` 诚实门槛的最小 clean replication
- `reports/site/reading/trendline_alpha_scout/report.html`
  - 新增 `Rank 34 · chip-distribution` intake 卡

## 当前 hard verdict
- **`Rank 34 = fresh intake only / admit_to_clean_replication_queue_with_assumption_gate`**
- 更直白地说：
  - 它现在只是下一条值得花 1 轮预算验证的 repo-based `support / reclaim` 候补；
  - 但下一轮预算必须优先回答 `synthetic shares 假设一改，结论会不会直接翻脸`；
  - 如果会，就应直接 `park / evidence pool`，而不是把筹码叙事越写越漂亮。

## 下一轮只允许做什么
- 固定复用 `BTC/ETH/SOL 120d 15m` cache；
- 只做 **1 次最小 clean replication**：先定义 3 档 `synthetic shares / turnover anchors`（保守 / 中性 / 激进）；
- 只比较 `raw baseline / chip_cost_reclaim / chip_cost_reclaim_plus_winner_ratio`；
- 先回答：
  - `post_cost_return`
  - `trade_count`
  - `assumption_sensitivity`
  - `false_reclaim_ratio`

## 最小验证
已执行：
1. `python3 scripts/build_rank34_chip_distribution_source_intake.py`
2. `grep -n "Rank 34 chip-distribution\|11:55 UTC\|admit_to_clean_replication_queue_with_assumption_gate" docs/TODO.md reports/site/reading/trendline_alpha_scout/report.html reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html reports/artifacts/literature/scout_rank34_chip_distribution_source_intake_card.csv`
3. 文件存在性检查：
   - `reports/artifacts/literature/scout_rank34_chip_distribution_source_intake_card.csv`
   - `reports/site/reading/trendline_alpha_scout/rank34_chip_distribution_source_intake.html`
   - `docs/TODO.md`
   - `reports/site/reading/trendline_alpha_scout/report.html`

## fallback / 修正记录
- 本轮未使用 `edit`，因此也未触发 exact-text mismatch fallback。
- 对 `TODO.md` 与 `report.html` 的更新使用了脚本替换，避免在当前大文件里手工精确替换失败。

## commit
- 未提交。
- 原因：仓库仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提。
