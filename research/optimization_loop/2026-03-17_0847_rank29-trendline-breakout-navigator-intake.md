# 2026-03-17 08:47 UTC · Rank 29 trendline breakout navigator intake

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 原因：`EMA` 经 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due` 守门后仍是 `waiting_not_due`；当前没有 `due-now / overdue` lane。
- active Scout 比较：
  - `Rank 17 / Rank 2`：当前没有新的真实 `append/review need`；继续围绕它们补 wiring 的边际价值很低。
  - `Rank 26 / Rank 27 / Rank 28`：本轮前已完成默认预算并压回 `park / evidence pool`。
  - 因此本轮不重开已 park 线，改做 1 条新的 `paper / repo based 15m crypto` source intake。

## 本轮主点
- 新增 `Rank 29 = trendline breakout navigator / multi-swing causal breakout state machine` 的 fresh intake。
- 来源不是外部现成 alpha 宣称，而是 repo 中已存在、边界清楚的 clean-room 模块：
  - `src/momentum/signals/trendline_breakout_navigator.py`
  - `docs/SIGNALS_TRENDLINE_BREAKOUT_NAVIGATOR.md`
- 之所以给它本轮预算，不是因为它“看起来酷”，而是因为：
  1. 它直接贴当前 desk 的 `15m crypto breakout / rejection / false-break` 主问题；
  2. 模块已有因果输出，能区分 `provisional line / wick interaction / close-confirm breakout / segment end_reason`；
  3. 在现有 active Scout 都没有真实 append need 的情况下，它比继续重开已 park 线更有边际价值。

## 先做的硬门槛读法
- `trade on`：至少一档 swing timeframe 形成 active line，随后 `close` 真正突破 active support/resistance，且 composite trend 同向。
- `trade off`：没有 active line、只有 provisional line 但没有后续有效 pivot、或只是 wick interaction / 假突破而没有 close-confirm breakout。
- 当前没有看到明显 `lookahead / repaint` 红旗：模块文档与实现都明确写了 confirmed pivot 只在确认 bar 落表，且 line state / segment 都是逐 bar 因果更新。

## 本轮产物
1. artifact：`reports/artifacts/literature/scout_rank29_trendline_breakout_navigator_source_intake_card.csv`
2. 网页：`reports/site/reading/trendline_alpha_scout/rank29_trendline_breakout_navigator_source_intake.html`
3. TODO 顶部作战板：补入 `Rank 29`，并在 `Run 2` 默认 fresh intake 中明确下一轮只允许做 1 次最小 clean replication。

## 当前 verdict
- `fresh intake only / eligible for one minimal clean replication`
- 不是 paper candidate，也不是 narrow paper pilot。
- 下一轮若继续认领，默认只允许：
  - 复用 `BTC/ETH/SOL 120d 15m` cache；
  - 做 1 次最小 clean replication；
  - 先回答 trade count / friction / false-break-vs-wick-rejection 三个便宜问题。

## 额外检查
- repo 工作区当前存在大量与本轮无关的脏文件；本轮不做混提、不做 commit。
- `run_ema_paper_trading_guarded_refresh.py --require-due` 返回 code 2，但文本结果是预期的 `waiting_not_due / require-due skip`，本轮按等待窗口处理，不视为 desk blocker。
