# EMA day-0 启动清单与记账模板（runbook -> 可执行启动层）

- 时间：2026-03-15 13:44 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`alpha_closure_board` 同步 deployment 入口口径（仅围绕本轮新增 artifact）

## 为什么这轮选这个

当前 steering 明确：EMA 是最接近 paper 的对象，且不要再堆 admission/operating/monitoring 近义页面；若没有新的 holdout/forward，下一刀应补更接近实际启动的 runbook/operating 细节。

上一轮已经补了 `runbook`，本轮选一个更 deployment-facing 的小完整切片：

- 把 runbook 再压成 **day-0 kickoff checklist** 与 **ledger template**；
- 让“今天就启动 0 真资金 shadow/paper 账本”有可直接执行的表格输入，不再停留在口头规则。

## 本轮改动

### 1) 代码：新增 2 个生成函数并接入主流程

文件：`scripts/build_ema_psar_raw_alpha_report.py`

- 新增 `build_ema_paper_trading_kickoff_checklist(...)`
  - 输出：`ema_paper_trading_kickoff_checklist.csv`
  - 内容聚焦 day-0 必做 5 步：
    1. 冻结 scope roster（primary/secondary/shadow/stoplist）
    2. 建四类独立账本
    3. 刷新 cadence 落日历
    4. review 强制落 `monitor_status + review_action`
    5. `data_health` 触发暂停/rollback 的硬动作

- 新增 `build_ema_paper_trading_ledger_template(...)`
  - 输出：`ema_paper_trading_ledger_template.csv`
  - 内容聚焦最小可执行记账字段（13 列），包括：
    - `deployment_scope / ledger_book / market_freq_book`
    - `signal_state / position_state`
    - `gross_pnl_pct / net_pnl_pct_20bps`
    - `benchmark_psar_net20_pct`
    - `monitor_status / review_action / data_health / note`

- 在 `main()` 中接入两份 artifact 的构建与落盘。

### 2) 页面：EMA 主报告新增 Q29（并把原边界段后移为 Q30）

文件：`reports/site/factors/ema_psar_raw_alpha/report.html`（由脚本生成）

- 新增 Q29：
  - 主题：如果明天就启动 `0` 真资金 shadow/paper，day-0 checklist 与记账模板最小该长什么样。
  - 增加两张表：
    - `EMA paper/shadow day-0 kickoff checklist`
    - `EMA paper/shadow ledger template`

- 原 “这页的边界是什么” 顺位更新为 Q30。

- 相关产物列表新增：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_kickoff_checklist.csv`
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_ledger_template.csv`

### 3) 项目级入口同步：closure board 更新为“runbook + day-0 启动层”

文件：`scripts/build_alpha_closure_board_report.py`（生成 `reports/site/factors/alpha_closure_board/report.html`）

- 把 EMA 的 `closest to paper` 描述同步到：
  - 已有 `candidate / operating / monitoring / runbook`
  - 且已补齐 `day-0 kickoff checklist / ledger template`
- 路线图 Step 3 与“离 paper trading 还有多远”段同步更新为：
  - 下一步不是再补近义 board，而是按同一套字段启动前瞻记账。

### 4) TODO 回写

文件：`docs/TODO.md`

在 `Deployment-facing 剩余硬门槛` 下新增并勾选：

- `[x] EMA：把 runbook 再压成 day-0 kickoff checklist / ledger template`

并补充本轮产物路径与口径说明。

## 最小验证 / 证据

执行并通过：

1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`
5. 关键 grep：
   - EMA 页出现 `Q29`、`Q30`
   - closure board 出现 `day-0 kickoff checklist / ledger template`
   - TODO 出现并勾选新增条目
6. artifact 文件读取确认：
   - `ema_paper_trading_kickoff_checklist.csv`
   - `ema_paper_trading_ledger_template.csv`

备注：本轮构图仍有 matplotlib CJK 字形 warning（历史现象），不影响 CSV/HTML 结果。

## 风险 / 边界

- 本轮是**运行规范层补齐**，不是新增 forward/holdout alpha 证据；不会改变 EMA 的统计结论边界。
- `ledger template` 当前是最小字段模板，不是自动执行引擎；后续若真跑 shadow/paper 仍需把字段接到日常更新流程。

## 下一步建议

- EMA 线下一步直接按本轮 checklist + ledger template 启动 `0` 真资金 shadow/paper 记账（而不是继续补近义 board）。
- 研究侧若再补刀，优先围绕 `沪深300ETF 1d` 的 promotion honesty 与 secondary batch 的降级触发审计。

## Git / 提交说明

- 本轮开始前工作区已存在大量与本轮无关的脏改动（含跨模块报告与 artifacts）。
- 本轮未提交 commit，避免混入无关改动；后续若要提交，应仅对本轮相关文件做 selective commit。

Commit hash：未提交（见上）。
