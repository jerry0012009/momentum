# EMA 守门入口 smoke test：确认仍未到真实 refresh 窗口

## 为什么这次选这个
- 当前 steering 已把 `EMA baseline family` 固定为最接近 `paper trading / 伪实盘` 的对象。
- `docs/TODO.md` 里唯一仍未收口、且最接近 deployment 的主任务，就是沿同一张 live ledger 继续落下一轮真实 `market-close refresh / week-1 review`。
- 但在没有新 completed bar 的情况下，正确动作不是硬写一轮伪 refresh，而是先验证新加的守门入口能不能在 close 前把这件事拦住。

## 做了什么改动
1. 真跑了一次：
   - `python3 /root/clawd/jerry/momentum/scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
2. 让它先重跑 `build_ema_psar_raw_alpha_report.py`，再读取：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_clock_audit.csv`
3. 把这次 smoke test 的结果补回 `docs/TODO.md` 未完成主线（EMA 连续 refresh / review）下面，避免下一轮又把“尚未到点”误判成“还缺一页说明”。

## 验证 / 证据
- 守门入口按设计返回 `code 2`，表示：`require-due` 已生效，当前没有 `due_now / overdue` lane。
- 最新 `due_guardrail_snapshot` 显示：
  - `Crypto 1d+1wk（BTC/ETH/SOL）` = `due_soon`，距下一次 UTC 日线 close 约 `3.8` 小时；
  - `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d` 距下一次 A 股日线 close 约 `10.8` 小时；
  - `美股 1d+1wk（SPY/QQQ/AAPL）` 距下一次美股日线 close 约 `23.8` 小时。
- 最新 `refresh_clock_audit` 也同步刷新到 `2026-03-15 20:10 UTC`，说明 active `1d` lanes 目前是 **on-clock waiting next close**，不是 stale，也不是脚本没跑。

## 风险 / 边界
- 这轮没有生成新的 forward refresh 结果，因为现在确实还没到下一根 completed daily bar。
- 这是故意保持诚实，不是推进停滞：本轮价值在于确认守门入口已经能在 close 前阻止伪 refresh，并给出下一次该优先执行的 lane。
- `build_ema_psar_raw_alpha_report.py` 运行中仍会打出 matplotlib 中文 glyph warning，但本次不影响 artifact 生成与守门判断。

## 下一步建议
- 下一次进入真实 close 窗口时，默认先跑同一个守门入口；若出现 `due_now / overdue`，就沿同一张 ledger 真续写 refresh / review，而不是回去补近义 queue / source 文案。
- 其中最靠前的就是 `Crypto 1d+1wk`，约 `3.8` 小时后应优先检查。

## Commit hash
- 未提交。

## 未提交原因
- 当前 `git status --short` 里已有大量与本轮无关的既有脏文件；本轮只做了守门 smoke test、刷新 EMA 报告/审计 artifact，并在 `docs/TODO.md` 追加一条最新状态说明。为避免混提无关改动，本轮不做 selective commit。
