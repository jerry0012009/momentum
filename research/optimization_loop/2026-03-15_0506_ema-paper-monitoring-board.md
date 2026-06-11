# EMA paper-trading monitoring board / admission monitor

- 时间：2026-03-15 05:06 UTC
- 本轮主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`closure / board` 的 deployment-facing 入口同步

## 为什么这次选这个

1. 先检查了 `git status`、最近 optimization loop 记录，以及 `docs/TODO.md` 当前接力棒，确认最近几轮已经连续完成：
   - `EMA final survivor map`
   - `paper-trading candidate spec`
   - `paper-trading operating spec`
   - `A股 daily shadow-promotion scorecard`
2. 当前 steering 明确要求优先推进**离 paper trading 最近**的对象；三条线里，`EMA baseline family` 仍然是最接近 paper 的对象。
3. 既然 `candidate spec / operating spec / shadow scorecard` 都已经有了，最自然的下一刀就不该再是 closure-copy，而是把这三张表压成一张真正可执行的 **paper-trading monitoring board**：
   - 谁今天算 `active primary`
   - 谁只算 `secondary backstop`
   - 谁仍是 `shadow watch`
   - 谁已经属于 `exclude stoplist`
   - 平时该盯哪几列、什么时候该升降级

## 做了什么改动

### 1) 把 EMA 的 deployment 口径再压成 `paper-trading monitoring board`

更新：
- `scripts/build_ema_psar_raw_alpha_report.py`

新增 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_monitoring_board.csv`

网页新增：
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增 `Q26. 如果明天就开始盯 EMA baseline paper，最小 monitoring board 应该长什么样？`

这张 board 不是新回测，而是把现有三层 deployment-facing 结果压成一张更像执行清单的表：
- `创业板ETF 1d` = `active_primary`
- `美股 1d+1wk（SPY/QQQ/AAPL）` = `active_secondary_backstop`
- `Crypto 1d+1wk（BTC/ETH/SOL）` = `active_secondary_backstop`
- `贵州茅台 1d+1wk` = `active_secondary_backstop`
- `沪深300ETF 1d` = `shadow_watch`
- `沪深300ETF 1wk` / `创业板ETF 1wk` / `Crypto 60m（BTC/ETH/SOL rolling）` = `exclude_stoplist`

同时把每个 pocket 的：
- `evidence_anchor`
- `monitor_focus`
- `keep_running_if`
- `escalate_or_stop_if`
- `current_read`

统一落成表格，避免后面又回到“谁看起来还行就一起讲 family”的含混表达。

### 2) 把 closure board 的 EMA 口径同步成 `candidate + operating + monitoring`

更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`

同步后，closure board 对 EMA 的读法已经不是“closest to paper，但细节还散着”，而是明确写成：
- 已有 `paper-trading candidate spec + operating spec + monitoring board`
- 也就是不只知道“谁能进 paper”，还知道“平时盯什么、何时升降级”

### 3) TODO / 计划入口同步

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

已新增并打勾：
- `[x] EMA：把 candidate spec / operating spec / shadow scorecard 再压成 paper-trading monitoring board`

## 验证 / 证据

已执行：

```bash
python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py
python3 scripts/build_ema_psar_raw_alpha_report.py
python3 scripts/build_alpha_closure_board_report.py
python3 scripts/build_plans_site.py
```

命中检查：
- `reports/site/factors/ema_psar_raw_alpha/report.html` 已出现新的 `Q26`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_monitoring_board.csv` 已生成
- `reports/site/factors/alpha_closure_board/report.html` 已出现 `monitoring board / monitoring spec` 口径
- `docs/TODO.md` 与 `reports/site/plans/momentum_todo.html` 已同步新增并打勾该任务

备注：
- 运行时仍有 matplotlib 中文字形 warning（既有字体问题），但 HTML / CSV 产物正常生成，不影响本轮结论页落地。
- 本轮没有重跑重型下载；主要复用现有 EMA survivor / candidate / operating / shadow 结果。

## 为什么这轮算真实推进

这轮不是继续补“EMA 最接近 paper”的近义重写，而是把它推进到更接近执行层的一步：

**现在不仅知道谁进 paper，还知道谁今天该 active、谁只 shadow、谁是 stoplist，以及这些判断平时要盯哪几列。**

这对 Jerry 当前最关心的问题有直接帮助：
- EMA 线是不是已经可以开始最小伪实盘管理？
- 如果开始，日常应该先盯 primary、secondary、shadow、exclude 里的哪些对象？
- 什么时候该升格、什么时候该停，不至于靠主观感觉临时改口径？

## 风险 / 边界

1. 这轮**没有新增回测**；它做的是把现有 deployment-facing 证据压成更可执行的 monitor board。
2. `secondary backstop` 仍不等于已经和 `创业板ETF 1d` 一样硬；它们仍主要承担“EMA 不只剩一格 daily survivor”的 backstop 证明，不该稀释 primary 试点结果。
3. `沪深300ETF 1d` 虽然 recent 有改善，但 current board 仍清楚显示它只是 `shadow_watch`，不应因为 latest 两个窗口变好就偷渡升格。
4. `A股 weekly + crypto 60m` 当前仍属于 `exclude_stoplist`；若未来要 reopen，必须靠新的 overturn evidence，而不是靠 family 汇总或局部窗口反弹。

## 下一步建议

1. 如果 EMA 线继续，默认优先还是追 `沪深300ETF 1d`：它现在是 board 上唯一最值得继续挑战的 `shadow promotion candidate`。
2. 不建议再回头给 `60m crypto` 或 `A股 weekly frontier` 找 hopeful 解释；它们现在已经明确处在 stoplist。
3. 若要切回 breakout，仍应保持当前更诚实的项目口径：`shadow-admission queue / one_more_gate`，优先追 `ETH+SOL pair-conditioned halfsize` 的 forward transferability，而不是重新扩分支。

## Commit hash

本轮**未提交**。

原因：
1. repo 在本轮开始前就存在大量与本轮无关的既有脏改动与未跟踪文件；
2. 本轮涉及文件（`docs/TODO.md`、相关脚本、站点页）本身也处在持续累计修改链上；
3. 当前无法安全保证 selective commit 只打包本轮增量，因此这轮只落文件、日志与邮件，不做不干净提交。

## 一句话结论

**EMA 线现在已经不只知道“谁最接近 paper”，还知道“谁今天该 active / shadow / stop，以及平时该盯哪几列”；这让它比 breakout 更像一条可以开始伪实盘管理的 baseline 线。**
