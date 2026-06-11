# 2026-03-16 03:23 UTC｜Scout Seat shortlist card：把 Run 3 备选从抽象“去 scouting”压成可直接认领的 15m crypto 清单

## 为什么这次选这个
- 先按要求检查了 repo 状态、`docs/TODO.md` 顶部 `TRADING DESK BOARD`、最近几轮 optimization logs、当前脏文件与当前席位状态。
- **Run 1 / Paper Seat（EMA）**：仍被真实 close waiting-window 挡住；当前没有新的 `due-now / overdue` lane，不能伪造 paper refresh。
- **Run 2 / Live Seat（breakout）**：仍处于最近 heavy rerun 后的 cooldown 窗口；继续做同类重跑大概率只会重复旧 blocker，不会新增 overturn `one_more_gate` 的硬证据。
- 因此这轮按板上顺序自动切到 **Run 3 / Scout Seat**，交一张真正能在下一轮继续认领的 **fast-cycle crypto shortlist card**，而不是再写一轮泛泛“去研究快周期 crypto”。

## 本轮主点
- 主点：**Scout Seat fast-cycle crypto shortlist card v1**
- 紧邻子点：把这张 card 同步挂到 `TODO/plans` 与 `Trendline Alpha Scout` 页面，避免 shortlist 只留在日志里。

## 做了什么改动
1. 更新 `scripts/build_trendline_alpha_scout_report.py`
   - 新增一张 `Scout Seat 快周期 crypto shortlist（Run 3 fallback v1）` 页面区块。
   - 同时生成新的可审计 artifact：
     - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

2. 这轮把 Run 3 先收口成下面这份默认顺序（`Rank 1 -> Rank 2 -> Rank 3`）：
   1. `τ-band / no-trade breakout filter`
      - 来源：`De Angelis et al. (2021)`
      - 价值：最贴 intraday crypto 的边界交易；最容易在 `5m/15m` breakout 上先拿到 first verdict。
      - 最小实验：`裸 breakout vs τ-band vs 2-of-3 closes outside`
   2. `volume + support-flip + higher-low`
      - 来源：`Yumna et al. (2024)`
      - 价值：和当前 breakout 主线最贴，适合当 confirmation challenger。
      - 最小实验：`裸 breakout vs 放量确认 vs support-flip vs higher-low vs 组合版`
   3. `third-touch + EMA/MACD confluence`
      - 来源：`Wiśniewski (2024)`
      - 价值：更严格的 structure-confirmation gate，但默认优先级低于前两名。
      - 最小实验：`裸 breakout vs third-touch gate vs EMA slope 同向 vs EMA+MACD 共识`

3. 更新 `docs/TODO.md`
   - 在顶部 `Scout Seat` 区块新增 `2026-03-16 03:18 UTC` 最新补充，明确：
     - Run 3 fallback 现在已经有一张可复用 shortlist card；
     - 当前默认顺序就是上面三条；
     - 它们默认先当 **breakout 的 confirmation / execution guard shortlist**，不是直接宣布替代当前 Live Seat。

4. 重建网页可见面
   - `python3 scripts/build_trendline_alpha_scout_report.py`
   - `python3 scripts/build_plans_site.py`

## 硬判断 / 这轮真正新增的 desk call
- **Scout Seat 现在不再只是“继续找材料”。**
- 当前更明确的默认读法是：
  - **Rank 1：`τ-band / no-trade breakout filter`** → 最快给 `15m crypto breakout` 产出 first verdict；
  - **Rank 2：`volume + support-flip + higher-low`** → 最贴当前 breakout 主线的 confirmation 版 challenger；
  - **Rank 3：`third-touch + EMA/MACD confluence`** → 更严格但更慢一档的 structure gate。
- 这三条当前都**不是 live-approved 替代策略**；它们只是被明确写成了 `Run 3` 可直接接手的 shortlist，而不是继续停留在抽象 scout 口号里。

## 验证 / 证据
- `python3 -m py_compile scripts/build_trendline_alpha_scout_report.py`
- `python3 scripts/build_trendline_alpha_scout_report.py`
- `python3 scripts/build_plans_site.py`
- `grep -n "Scout Seat 快周期 crypto shortlist\|scout_seat_fast_cycle_crypto_shortlist_v1.csv\|τ-band / no-trade breakout filter" reports/site/reading/trendline_alpha_scout/report.html docs/TODO.md reports/site/plans/momentum_todo.html`
- 额外核对：
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv` 已生成；
  - `reports/site/reading/trendline_alpha_scout/report.html` 已出现新 shortlist 区块；
  - `reports/site/plans/momentum_todo.html` 已同步显示新的 `Scout Seat` 最新补充。

## 风险 / 边界
- 这轮新增的是 **shortlist / desk 排序**，不是新的本地 alpha 证据，也不是任何 live approval。
- 这三条候选大多仍是 `full_text + no_code + clean-room` 路线；真正要不要升格，仍要看后续 `5m/15m` 最小实验的 first verdict。
- 这轮默认把它们先当 `breakout` 的 confirmation / execution guard challenger，而不是立刻替换当前 Live Seat。

## git / hygiene
- `git status --short --branch` 显示工作区仍有大量与本轮无关的既有脏改 / 未跟踪文件。
- 本轮只安全补了：
  - `scripts/build_trendline_alpha_scout_report.py`
  - `docs/TODO.md`
  - `reports/site/reading/trendline_alpha_scout/report.html`
  - `reports/site/plans/momentum_todo.html`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
- **未提交 git。** 原因：当前 worktree 不干净，不适合把本轮与历史脏改混提。

## Commit hash
- HEAD：`ae221ef`
- 本轮未提交。

## 下一刀默认
1. 若 `EMA` 仍未到真实 due window、`breakout` 也仍在 cooldown，而 Run 3 继续触发，默认优先从 **Rank 1 `τ-band / no-trade breakout filter`** 开始落最小 `15m crypto` 对照实验。
2. 若 `breakout` cooldown 先结束，则仍按 desk 顺序先回到 Live Seat，检查是否出现新的 forward overturn evidence。
3. 若 `EMA` 先进入 `due-now / overdue`，则立即切回 Paper Seat，沿同一张 paper ledger 继续做真实 refresh / review。
