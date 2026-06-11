# 2026-03-17 20:17 UTC · EMA due window resync

## 本轮归属
- Desk lane：`Run 1 status sync -> authoritative board writeback`
- 触发原因：
  - 当前 wall-clock 已经过 `2026-03-17 20:00 UTC`，而 `TODO` 顶板上一版仍把美股 close 写成“最近的下一次时钟动作”
  - 先核对 `EMA` 是否真的还在 due-now / overdue，再决定是否继续留在 `Run 1`

## 开始前检查
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做最小局部写入，不混提
- 最近 runs：
  - `19:37 UTC`：已把 `Scout Fast Lane` 写成 exhaustion state
  - `19:53 UTC`：已把 tiny-live closure board 同步到最新 manual narrow paper 状态
- 当前 seat 预判：
  - `Paper Seat / EMA` 可能刚经过美股 due window
  - `Scout Seat` 本地 fast-lane 已临时耗尽
  - 因此最值钱的一步不是再开新研究，而是先把 `Run 1` 的真实状态写对

## 本轮主点 + 紧邻子点
- **主点**：核对 `EMA` 的 `20:00 UTC` due window 是否已被真实消化
- **紧邻子点**：把结果写回 `docs/TODO.md` 顶部 `TRADING DESK BOARD` / `Next 3 bot3 runs`

## 本轮做了什么
### 1) 先核对 `EMA` 当前是不是还在 due-now
检查文件：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`

实际看到的关键证据：
- `ema_paper_trading_refresh_history.csv` 已新增 `2026-03-17 20:05 UTC` rows
- 新增行至少覆盖：
  - `美股 1d+1wk（SPY/QQQ/AAPL） -> latest_completed_bar_utc=2026-03-17 00:00 UTC`
  - `创业板ETF 1d -> latest_completed_bar_utc=2026-03-17 00:00 UTC`
  - `沪深300ETF 1d -> latest_completed_bar_utc=2026-03-17 00:00 UTC`
- 最新 `ema_paper_trading_due_guardrail_snapshot.csv` 已改写为：
  - `Crypto 1d+1wk -> 2026-03-18 00:00 UTC`
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - `美股 1d+1wk -> 2026-03-18 20:00 UTC`

这说明：
- 刚刚跨过的 `20:00 UTC` 美股 due window **已经被真实消化**
- 当前全 desk **没有**新的 `due-now / overdue` lane
- `Paper Seat / EMA` 已重新回到 `running paper / waiting_not_due`

### 2) 把 authoritative board 改回当前真实口径
文件：`docs/TODO.md`

本轮只做两处最小更新：
1. 在 `Paper Seat` 最新补充里追加 `2026-03-17 20:17 UTC` 说明，明确写回：
   - `20:00 UTC` 美股 due window 已在 `20:05 UTC` 被消化
   - 当前 Paper Seat 已恢复 `waiting_not_due`
2. 在 `Next 3 bot3 runs` 顶部 authoritative override 中改写默认读法：
   - `Run 1 = waiting_not_due`
   - `Run 2 = 本地 fast-lane 暂无合格新 intake`
   - 若没有新 paper/repo source 或 bot2 点名 promoted candidate，则可诚实回退到 `Run 3 / tiny-live plumbing fallback`

## 本轮 hard verdict
**这轮最重要的结论不是“又要去补 EMA refresh”，而是：`EMA` 的本次美股 due window 已被别的 refresh 链在 `20:05 UTC` 真实消化完了。当前继续把 `Run 1` 当成 due-now 会把作战板读旧。最诚实的当前 desk 读法，是 `Paper Seat` 已回到 `running paper / waiting_not_due`，而后续默认顺序应重新落回 `Run 2 exhausted -> Run 3 fallback`。**

## reader-facing 落点
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 会映射到 control tower / TODO 网页，是当前最直接的 reader-facing authoritative 落点

## 验证 / 证据
已验证：
- `ema_paper_trading_refresh_history.csv` 确有 `2026-03-17 20:05 UTC` 新 rows
- `ema_paper_trading_due_guardrail_snapshot.csv` 当前不再存在 `due-now / overdue` lane
- `docs/TODO.md` 已写回 `20:17 UTC` 最新口径

## 风险 / 边界
- 本轮没有重跑重型 refresh 脚本，因为当前关键问题不是“刷新没跑”，而是“作战板还没写回已经发生的刷新”
- 本轮没有重开 Scout 新研究线
- 本轮没有继续追加 `Rank 2 / Rank 17 / Rank 29` 的 `P3 continuity` 近义接线

## 下一步建议
1. 若 `00:00 UTC` 前没有新的合格 paper/repo source 或 bot2 点名 promoted candidate，则后续 bot3 轮次可按新顶板诚实回退到 `Run 3 / tiny-live plumbing`
2. 到 `Crypto 1d+1wk -> 2026-03-18 00:00 UTC` 再优先检查 `Run 1 / EMA`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
