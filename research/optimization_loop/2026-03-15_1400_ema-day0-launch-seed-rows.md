# EMA day-0 launch seed rows 落地（runbook -> 可直接开账）

- 时间：2026-03-15 14:00 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`alpha_closure_board` 同步 deployment 入口口径

## 为什么这轮做这个

本轮按当前 steering 继续优先 EMA（closest to paper），且避免再新增近义 board。
在已完成 `candidate spec / operating spec / monitoring board / runbook / kickoff checklist / ledger template` 的前提下，最接近真实 paper/shadow 启动、且能在一轮内完整交付的小任务是：

- 把 `ledger template` 再压成 **day-0 launch seed rows**；
- 让“明天就开 0 真资金账本”从字段层，变成“第一天该先建哪几行账本”的执行层。

## 本轮改动

### 1) 代码与产物（EMA 主报告）

文件：`scripts/build_ema_psar_raw_alpha_report.py`

- 新增函数：`build_ema_paper_trading_day0_seed_rows(runbook_df)`
  - 输出 artifact：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_seed_rows.csv`
  - 按 runbook 自动展开 `market × freq`，为每个 deployment scope 生成 day-0 seed 行；
  - 固化字段：`ledger_book / market_freq_book / signal_state / position_state / monitor_status / review_action / data_health / seed_rule`。

- 在主流程接入生成与落盘：
  - 新增 CSV：`ema_paper_trading_day0_seed_rows.csv`

- 页面新增（并顺延边界问答）：
  - `Q30`：`如果今天就真开账，day-0 launch seed rows 应该先建哪几条？`
  - 解释为何 day-0 不是抽象“开始记账”，而是先固定 launch roster。
  - 原边界段由 `Q30` 顺延为 `Q31`。

- 相关产物列表补充：
  - `ema_paper_trading_kickoff_checklist.csv`
  - `ema_paper_trading_ledger_template.csv`
  - `ema_paper_trading_day0_seed_rows.csv`

### 2) closure 入口同步

文件：`scripts/build_alpha_closure_board_report.py`

- EMA 线描述从 `checklist / ledger template` 同步升级为 `checklist / ledger template / launch seed rows`；
- Step3/当前位置/下一步文案同步到“按 day-0 launch seed 启动真实 shadow/paper 记账”。

### 3) TODO 回写

文件：`docs/TODO.md`

在 deployment-facing 残余门槛下新增并勾选：

- `[x] EMA：把 ledger template 再压成 day-0 launch seed rows`

并写明本轮结果：
- 当前 day-0 固定 `11` 条 seed rows：`primary 1 + secondary 6 + shadow 1 + stoplist 3`；
- secondary 必须按 `market × freq` 拆分，不允许合并成一条“secondary 总曲线”。

## 最小验证 / 证据

执行并通过：

1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`
5. 页面/文案检查：
   - `reports/site/factors/ema_psar_raw_alpha/report.html` 包含 `Q30` 与 `ema_paper_trading_day0_seed_rows.csv`；
   - `reports/site/factors/alpha_closure_board/report.html` 已出现 `launch seed rows / day-0 launch seed` 口径。
6. artifact 结构检查：
   - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_seed_rows.csv` 共 `11` 行；
   - `ledger_book` 分布：`secondary_backstop=6`、`stoplist_reopen_only=3`、`primary_paper=1`、`shadow_watch=1`。

备注：构图阶段仍有 matplotlib CJK 字形 warning（历史现象），不影响 CSV/HTML 产物。

## 风险 / 边界

- 本轮是 deployment 启动层补齐，不是新增 forward/holdout alpha 证据；
- 不改变 EMA 当前统计边界，只把“可执行启动动作”从描述层推进到落表层。

## 下一步建议

- EMA 线下一步默认应按本轮 `launch seed rows` 启动 `0` 真资金 shadow/paper 前瞻记账；
- 研究侧仅在需要时补 `沪深300ETF 1d` promotion honesty 或 secondary batch 降级触发复核，不再回到近义 board 扩写。

## Git / 工作区说明

- 本轮开始前工作区已存在大量与本轮无关的脏改动；
- 为避免混入无关文件，本轮未提交 commit；后续如需提交，应仅对本轮相关文件做 selective commit。

Commit hash：未提交。