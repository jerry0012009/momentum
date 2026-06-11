# 2026-03-15 17:17 UTC — EMA live ledger on-clock 审计（避免把“无新 bar”误判成停转）

## 为什么这次选这个
- 先做了环境观测：`git status --short`（仅观测，不作为失败条件）、最近 optimization_loop 记录、`docs/TODO.md`、`docs/AUTO_OPTIMIZATION_LOOP.md`。
- 当前 steering 下，默认优先 `EMA baseline family`（closest to paper），且已明确“不要继续堆近义 board 页面”。
- EMA 线上一轮已经把 A 股日频 source-risk 清到 `live=5 / fallback=0 / unavailable=0`，但这时容易出现一个执行误判：
  - 周末或非收盘时段没有新 completed bar，容易被误读成“账本停了”。
- 所以本轮主点选择：**不伪造不存在的新 forward 结果**，而是补一张 deployment-facing 的 `refresh clock audit`，把“现在是在按时等待 next close，还是 stale”写清楚。

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`paper-trading runbook / shadow operating rules` 的执行层时钟审计（refresh / week-1 节奏）

## 做了什么改动

### 1) 新增 on-clock 审计产物（核心）
- 文件：`scripts/build_ema_psar_raw_alpha_report.py`
- 新增函数：
  - `build_ema_paper_trading_refresh_clock_audit(...)`
  - 相关辅助：`parse_utc_label(...)`、`next_daily_close_utc(...)`、`fmt_time_gap(...)`
- 新增产物：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_clock_audit.csv`

这张表按 active `1d` lanes 输出：
- `clock_status`（是否 on-clock）
- `next_expected_close_utc`
- `time_to_next_close`
- `week1_review_due_utc`
- `time_to_week1_review`
- `week1_status`
- `current_clock_read / next_gate / why_it_matters`

### 2) EMA 主报告新增 Q35d（deployment-facing）
- 文件：`reports/site/factors/ema_psar_raw_alpha/report.html`（由脚本生成）
- 新增问题：
  - **Q35d. 如果今天还没有新的已收盘日线，这张 live ledger 现在是在按时等下一次 close，还是已经 stale 掉了？**
- 作用：
  - 明确“无新 bar ≠ 账本停转”；
  - 把下一次 close 与 week-1 review 的到时节奏可视化。

### 3) closure board 同步更新（避免入口口径滞后）
- 文件：`scripts/build_alpha_closure_board_report.py`
- 同步了 EMA 卡片文案：
  - 当前不是“缺说明页”，而是**账本在按时等待下一次 market-close refresh**；
  - 下一刀应继续真实 forward refresh / week-1 review，而不是继续堆同类文案。

### 4) TODO 回写（不虚假勾选）
- 文件：`docs/TODO.md`
- 对未完成项
  - `EMA：沿同一张 live ledger 连续落下下一轮 market-close refresh / week-1 review 结果`
- 增加“最新补充（2026-03-15 17:07 UTC）”：
  - 已有 `refresh_clock_audit`，当前是 `on-clock waiting next close`；
  - 该任务**仍未完成**（因为还没有新的真实 completed bar/周 review），但下一刀路径更清楚。

## 验证 / 证据
最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`

关键结果（来自 `ema_paper_trading_refresh_clock_audit.csv`）：
- active `1d` lanes 约 `5/5` 为 `on_clock_waiting_next_close`。
- 首个 `week-1 review` 约在 `2026-03-22 17:16 UTC`（当前未到时）。
- 代表性 next close：
  - `Crypto-1d`：约 `2026-03-16 00:00 UTC`（约 6.7 小时后）
  - `A股-1d`：约 `2026-03-16 07:00 UTC`（约 13.7 小时后）
  - `美股-1d`：约 `2026-03-16 20:00 UTC`（约 1.1 天后）

对应项目级结论：
- EMA 当前不是“停转”，而是“source-risk 已清后，处在按计划等待下一次真实 close 的正常空窗”。

## 风险 / 边界
- 本轮没有制造新的 forward alpha 证据；只是把“是否按计划运行”压成可执行审计层。
- 所以不能把这轮解读为“week-1 review 已完成”或“primary promotion 已通过”。
- 真正改变 admission/promote 结论，仍要等下一次真实 market-close refresh 与后续 week-1 review 实绩。

## 执行层 hygiene
- 本轮把 `git status --short` 作为环境观测使用；当前 worktree 存在大量与本轮无关的历史脏改/未跟踪文件。
- 本轮只推进 EMA deployment-facing 的 on-clock 审计，不混做 breakout/fib 近义任务。

## 下一步建议
1. 等最近一轮真实 completed bar 到达后，沿同一张 live ledger 续写下一笔 `market-close refresh`。
2. 在 `week-1 due` 到时后，按既有 scorecard 给出首个 `green/yellow/red` 实判（不要用口头替代）。
3. front-queue secondary 继续按 `keep / stricter recheck / demote` 三态执行，不回退到 family 汇总遮盖。

## Commit hash
- 本轮未提交。
- 原因：当前仓库存在大量与本轮无关的脏改与未跟踪文件；为避免混入无关改动，本轮保持不提交。