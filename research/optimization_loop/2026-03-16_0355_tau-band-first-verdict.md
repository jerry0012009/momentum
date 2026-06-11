# 2026-03-16 03:55 UTC · τ-band 15m crypto first verdict（Run 2 落地）

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查当前席位：
  - Paper Seat：`ema_paper_trading_due_guardrail_snapshot.csv` 显示仍是 `waiting_not_due`（A 股下一次 close 约 7 小时后），本轮不能伪 refresh。
  - Live Seat：`avoid_fluctuating_revisit_guard_20bps.csv` 仍是 `revisit_guard_verdict=cache_advanced_but_recent_recheck_cooldown_hold`，属于 cooldown 窗口，不应重复 heavy rerun。
- 因此按当前窗口排班自动切到 `Next 3` 的下一步：**Scout Seat Rank 1（τ-band / no-trade breakout filter）**，落一刀最小 15m crypto 对照实验，给出 hard verdict。

## 本轮主点 + 紧邻子点
### 主点（Run 2）
落地一套可复用的最小实验脚本并产出 artifact：
- 新增脚本：`scripts/build_tau_band_breakout_scout_report.py`
- 产出目录：`reports/artifacts/scout_tau_band_breakout_15m/`
- 页面：`reports/site/factors/scout_tau_band_breakout_15m/report.html`

实验口径（固定、最小）：
- 资产：`BTC-USD / ETH-USD / SOL-USD`
- 样本：`Binance 120d 15m`（带本地 cache，避免重复重下载）
- 方向层：`EMA20 vs EMA50`
- 触发层：`Donchian(20)`
- 对照组：
  - `raw_breakout`
  - `tau_005_breakout`
  - `tau_010_breakout`
  - `tau_020_breakout`
  - `confirm2of3_tau_010`
- 出场：`1 ATR stop / 2 ATR target / 8 bar time stop`
- 成本：`6 bps/side`
- 指标：`post-cost return / max_drawdown / false_break_ratio / outside_persistence_3bars`

**本轮 hard verdict：**
- `confirm2of3_tau_010` 相对 raw 确实“更不差”（平均收益与假突破率都更好）；
- 但绝对 `post-cost return` 仍为负（跨资产 `positive_asset_ratio=0`）；
- 所以当前结论是：**保留为 scout follow-up / execution guard 候选，不是 replace-ready winner。**

关键读数（variant aggregate）：
- `raw_breakout`：`mean_total_return=-46.14%`，`mean_false_break_ratio=50.10%`
- `confirm2of3_tau_010`：`mean_total_return=-11.28%`，`mean_false_break_ratio=41.15%`

### 紧邻子点（可见性同步）
把本地 first verdict 接到 Scout 页面，避免只在单独 factor 页可见：
- 修改：`scripts/build_trendline_alpha_scout_report.py`
- 更新页：`reports/site/reading/trendline_alpha_scout/report.html`
- 新增一张“Run 2 本地最小实验（Rank 1 · τ-band）”卡片，直接链接到 factor 页并展示 hard verdict。

## 验证 / 证据
执行与检查：
1. `python3 scripts/build_tau_band_breakout_scout_report.py`
2. `python3 scripts/build_trendline_alpha_scout_report.py`
3. `grep -n "Run 2 本地最小实验\|hard verdict" reports/site/reading/trendline_alpha_scout/report.html`
4. `sed -n '1,3p' reports/artifacts/scout_tau_band_breakout_15m/trial_meta.csv`
5. `sed -n '1,6p' reports/artifacts/scout_tau_band_breakout_15m/variant_aggregate.csv`

已确认：
- 新实验 artifact/页面生成成功；
- Scout 页面已出现本地实验卡与硬结论；
- verdict 文案已修正为“相对改进但绝对仍负，不是 replace-ready”。

## 风险 / 边界
- 当前实验是 **first verdict**，仍属最小口径（3 资产、120d、固定出场）；
- 还没进入更严格 live-admission 级验证（更长窗口、更多币种、执行摩擦/路由细节）；
- 因此本轮只应推进为 `execution guard challenger`，不能把它当成 Live Seat 替换依据。

## 下一步建议
- 下一刀优先做 **同口径 forward continuation**（保持规则不漂移），验证 `confirm2of3_tau_010` 的相对优势是否延续；
- 若继续相对占优，再补一层更贴近 tiny-live 的路由/滑点敏感性对照；
- 若优势消失，则按 board 要求及时 `bench`，不在同样本无限 micro-slicing。

## git / 提交
- 本轮未提交。
- 原因：worktree 存在大量与本轮无关的既有脏文件与未跟踪文件；按规则避免混提，保持 selective commit。
