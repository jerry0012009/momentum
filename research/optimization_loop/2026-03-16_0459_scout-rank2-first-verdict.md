# 2026-03-16 04:59 UTC｜Scout Seat：Rank 2（volume + support-flip + higher-low）first verdict 落地

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` + `Next 3 bot3 runs` 执行：

- **Run 1 / Paper Seat**：`ema_paper_trading_due_guardrail_snapshot.csv` 仍是 `waiting_not_due`（A 股下次 close 约 `07:00 UTC`），本轮不能伪造 refresh。
- **Run 2 / Live Seat**：`avoid_fluctuating_revisit_guard_20bps.csv` 仍是 `rerun_cooldown_active=yes`（最近 heavy recheck `2026-03-15 23:25 UTC`），本轮不应重复 heavy rerun。
- 因此按规则自动切到 **Run 3（Scout/Tiny-live fallback）**，并优先认领紧邻可交付项：把上一轮的 `Rank 2 clean-room spec` 推到 **本地 first verdict**（不是继续写 spec 近义页）。

## 本轮主点 + 紧邻子点

### 主点（Run 3 / Scout Seat）
把 `Rank 2 volume + support-flip + higher-low` 从“可实现规范”推进为“有结果的最小实验”：

- 新脚本：`scripts/build_volume_supportflip_higherlow_first_verdict.py`
- 复用缓存：`reports/artifacts/scout_tau_band_breakout_15m/cache/*.csv`（120d / 15m，避免新重下载）
- 新产物：
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/variant_aggregate.csv`
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/asset_summary.csv`
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/event_candidates.csv`
  - `reports/artifacts/scout_volume_supportflip_higherlow_15m/trial_meta.csv`
  - 页面：`reports/site/factors/scout_volume_supportflip_higherlow_15m/report.html`

实验矩阵（遵循 clean-room spec v1）：
- `raw_breakout`
- `volume_only`
- `support_flip_only`
- `higher_low_only`
- `combo_all`

同口径执行：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | 6bps/side`。

### 紧邻子点（reader-facing 落点 + board continuity）
- 更新 `scripts/build_trendline_alpha_scout_report.py`，在 Scout 首页新增 **Rank 2 first verdict 卡片**；
- 同步刷新 `docs/TODO.md` 顶部 desk board 与 `reports/site/plans/momentum_todo.html`：
  - 追加 `2026-03-16 04:58 UTC` 的 Rank 2 first verdict 补充；
  - 更新当前窗口排班为 `2026-03-16 05:00`，明确下一轮若 Rank 1 cache 仍不足，不要重复同一份 Rank 2 first verdict。

## 验证 / 证据
执行：
1. `python3 -m py_compile scripts/build_volume_supportflip_higherlow_first_verdict.py scripts/build_trendline_alpha_scout_report.py`
2. `python3 scripts/build_volume_supportflip_higherlow_first_verdict.py`
3. `python3 scripts/build_trendline_alpha_scout_report.py`
4. `python3 -m py_compile scripts/build_plans_site.py && python3 scripts/build_plans_site.py`
5. `grep` 检查 Scout 页面与 factor 页面中 Rank 2 first verdict 的可见落点。

关键读数（`variant_aggregate.csv`）：
- `raw_breakout`：`mean_total_return=-40.39%`，`mean_false_break_ratio=48.75%`，`positive_asset_ratio=0/3`
- `combo_all`：`mean_total_return=+2.33%`，`mean_false_break_ratio=6.67%`，`positive_asset_ratio=2/3`
- `higher_low_only`：`mean_total_return=+1.67%`，`mean_false_break_ratio=1.67%`，`positive_asset_ratio=2/3`

## 本轮 hard verdict
**`combo_all` 在当前 15m/120d 本地口径下，已经相对 raw 同时改善了收益与假突破率；可作为 Rank 2 的继续复核版本。**
但当前仍属于 first verdict，**不直接宣布 replace-ready / tiny-live ready**。

## 风险 / 边界
- 当前样本仍是 3 币种、120d、固定出场口径；
- 尚未加入真实路由摩擦、成交偏差、交易限额等 live 级约束；
- `support_flip_only` 与 `volume_only` 仍显著负收益，说明“单点确认”不稳定，不能草率升格。

## 下一步建议
- cooldown 结束后，若 Live Seat 允许一次重跑，优先按 Run 2 规则做 `breakout rerun`（一次即可，不要高频重复）；
- Scout 侧下一刀只做 **Rank 2 combo_all 的轻量 forward / friction 复核**，验证优势是否延续；
- 若优势在 forward 或摩擦后塌陷，及时 `bench`，不做同样本无限续切。

## Commit hash
- 未提交。

## 如果未提交，原因
当前 worktree 存在大量与本轮无关的既有脏文件与未跟踪文件；为避免混提，本轮仅做 selective 改动与产物刷新，不打包提交。

---

核心结论（一句话）：
`Rank 2 combo_all` 已从“规范候选”进入“有正向 first verdict 的 confirmation challenger”，但还没到 tiny-live 准入。

证据支撑（一句话）：
在复用同一份 15m/120d cache 和同一执行成本口径下，`combo_all` 把跨资产平均收益从 `-40.39%` 拉到 `+2.33%`，同时把假突破率从 `48.75%` 压到 `6.67%`（`positive_asset_ratio=2/3`）。
