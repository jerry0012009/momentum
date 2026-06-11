# 2026-03-15 19:35 UTC — EMA due-now / overdue 守门快照

## 本轮先看了什么
- 先看 `git status --short`：工作区本来就很脏，含大量与本轮无关的历史改动 / 产物；按要求只把它当环境观测，不当失败条件。
- 复查 `docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`、以及 2026-03-15 最近几轮 optimization logs。
- 当前 steering 明确：
  - breakout 仍是总优先级最高，但如果拿不到能 overturn scope verdict 的新证据，就不要继续切更细 micro-slices。
  - EMA 若暂无新的真实 forward / holdout，更该补 deployment-facing 的 runbook / shadow operating 缝隙，而不是再堆近义 board。
  - 最近两轮（19:05 / 19:18 UTC）都已明确：在下一根真实 completed daily bar 到来前，不该继续补近义 `overlay / source / queue / closure-copy` 页面。

## 本轮选择的主点
- 选择主点：**EMA / PSAR raw alpha focus**
- 选择的具体小切口：把已有 `next-close action queue` 再压成一个**真正执行层守门**的 `due-now / overdue` 快照。
- 原因：
  1. 这不是再加一层近义 board，而是把“正常 waiting”与“close 已到 / 已过仍未 refresh”分开；
  2. 它直接服务 line-299 那条未完成主线（真实 `market-close refresh / week-1 review`）；
  3. 当前没有新 close，可诚实完成的 deployment-facing 小任务里，这一刀最接近后续 paper / 伪实盘执行。

## 实际改动
### 1) 报告脚本
改 `scripts/build_ema_psar_raw_alpha_report.py`：
- 新增 `fmt_signed_time_gap()`，用于把 close 相对当前时点写成 `约 X 小时后到点 / 已过约 X 小时`；
- 新增 `build_ema_paper_trading_due_guardrail_snapshot()`，输出：
  - `waiting_not_due`
  - `due_soon`
  - `due_now_refresh_window`
  - `overdue_refresh_check`
  - `blocked_before_due`
- 让主构建流程落地新 artifact：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- 在 EMA 主报告里新增 `Q35i`，专门解释：
  - Q35h 负责“到点后先做什么”；
  - Q35i 负责“现在到底还该等，还是已经该停止写近义说明、转去做 refresh / blocked 检查”。
- 同步把新 artifact 挂进相关产物清单，并更新 Q36 边界说明。

### 2) TODO / plans
改 `docs/TODO.md`：
- 新增并勾掉：`EMA：把 next-close queue 再压成 due-now / overdue 守门快照（close 过后别继续误写成 waiting）`。
- 保持主未完成任务不变：`EMA：沿同一张 live ledger 连续落下下一轮 market-close refresh / week-1 review 结果` 仍未完成，且本轮没有假装生成不存在的新 forward。

随后重建：
- `reports/site/factors/ema_psar_raw_alpha/report.html`
- `reports/site/plans/*`

## 本轮结果（最重要的可见产出）
新 artifact 当前读数：
- `Crypto 1d+1wk（BTC/ETH/SOL）` = `due_soon`，距下一次 close 约 `4.4 小时`；
- `创业板ETF 1d` = `waiting_not_due`，距下一次 close 约 `11.4 小时`；
- `贵州茅台 1d+1wk` = `waiting_not_due`，距下一次 close 约 `11.4 小时`；
- `沪深300ETF 1d` = `waiting_not_due`，距下一次 close 约 `11.4 小时`；
- `美股 1d+1wk（SPY/QQQ/AAPL）` = `waiting_not_due`，距下一次 close 约 `1.0 天`。

### 这刀为什么有用
- 之前 `Q35h / next-close queue` 只回答“到点后按什么顺序做”；
- 这次 `Q35i / due-guardrail snapshot` 额外回答“什么时候已经不能继续把它写成 waiting”。
- 因而下次真实 close 一过，bot 不需要再先判断“这是正常等待还是漏刷”——artifact 已把这层守门写死。

## 验证
执行：
- `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
- `python3 scripts/build_ema_psar_raw_alpha_report.py`
- `python3 scripts/build_plans_site.py`

结果：
- 以上命令全部通过；
- 仅出现 matplotlib 的中文 glyph warning，不影响本轮 artifact / html 生成。

## git / 提交说明
- 本轮开始前工作区已存在大量与本轮无关的脏改、未跟踪产物、以及其他研究线残留；
- 按要求没有把这些无关改动混进本轮提交；
- 本轮**未提交**，原因是当前 worktree 噪音太大，直接 selective commit 的审计成本偏高，容易把无关文件一并带入。

## 结论
- 本轮没有伪造新的 EMA forward / review 结果；
- 但确实把 EMA 从“知道下次 close 到了要做什么”推进到“close 到后不会继续误判成 waiting”；
- 下一轮若遇到真实 close，默认就该优先沿 `ema_paper_trading_due_guardrail_snapshot.csv` + `ema_paper_trading_next_close_action_queue.csv` 真落 refresh / blocked 检查，而不是继续补近义 wording。
