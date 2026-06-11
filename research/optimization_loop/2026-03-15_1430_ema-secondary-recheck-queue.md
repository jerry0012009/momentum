# EMA secondary backstop recheck queue（deployment-facing 复核排班）

- 时间：2026-03-15 14:30 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`docs/TODO.md` 与 plans 镜像同步（仅围绕本轮新增产物）

## 为什么本轮选这个

按当前 steering，EMA 已是 closest-to-paper，且最近几轮已连续补齐 `candidate / operating / monitoring / runbook / day-0 / week-1`。
本轮如果继续 EMA，最有价值的 deployment-facing 小切片不是再造近义 board，而是把现有 `active_secondary_backstop` 变成可执行的 **复核优先级队列**：

- 下一轮若资源有限，先查谁？
- 查坏了怎么动作（demote/rollback）？
- 如何避免“整批 secondary 口头维持”掩盖单 pocket 转弱？

同时避免重型下载：直接复用已有 `ema_non60m_honesty_queue.csv` 与 runbook/operating 口径。

## 本轮改动

### 1) 新增 secondary 复核队列构建函数

文件：`scripts/build_ema_psar_raw_alpha_report.py`

- 新增函数：`build_ema_secondary_backstop_recheck_queue(...)`
- 输入：
  - `ema_non60m_honesty_queue`（已有）
  - `ema_paper_trading_candidate_spec`（已有）
  - `ema_paper_trading_operating_spec`（已有）
- 输出：
  - `reports/artifacts/ema_psar_raw_alpha/ema_secondary_backstop_recheck_queue.csv`

关键字段：
- `recheck_rank / global_honesty_rank`
- `secondary_group / pocket_scope`
- `profit_pct / trades / breakeven_roundtrip_cost_bps / approx_net_profit_pct_20bps`
- `recheck_bucket`（`front-of-queue / mid-queue / back-of-queue`）
- `why_recheck_now`
- `if_fail_then_action`（直接继承 operating spec 的降级规则）

### 2) 页面新增 Q32（并顺延边界为 Q33）

文件：`reports/site/factors/ema_psar_raw_alpha/report.html`（由脚本生成）

- 新增 `Q32`：
  - 问题：不再补近义 board 时，`active_secondary_backstop` 下一轮该先复核谁？
  - 给出 front/mid/back 三档计数与第一优先目标
  - 落地表格：`EMA active secondary backstop recheck queue`
- 原边界段从 `Q32` 顺延为 `Q33`

### 3) TODO 勾选同步

文件：`docs/TODO.md`

新增并勾选：
- `[x] EMA：把 active_secondary_backstop 压成可执行 recheck queue（避免整批口头维持）`

并补充当前口径：
- 先看薄 buffer 的 front queue；
- 任一 pocket 被更严格 honesty 打回 `mixed/watch`，按 runbook 从 `active_secondary_backstop` 降回 `shadow`，不再用同批其他口袋遮盖。

## 最小验证

已执行：

1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

抽查通过：
- 新 artifact 存在：
  - `reports/artifacts/ema_psar_raw_alpha/ema_secondary_backstop_recheck_queue.csv`
- 报告页出现：
  - `Q32`（secondary recheck queue）
  - `Q33`（边界）
- TODO 已出现并勾选新条目。

## 本轮可见结果（deployment-facing）

当前 `active_secondary_backstop` 已从“整批叙事”压成可执行复核排班：
- `front-of-queue`: 2
- `mid-queue`: 4
- `back-of-queue`: 8
- 当前第一优先复核目标：`SPY 1d`

这让下一轮是否继续给 secondary 线分配研究资源，有了可执行顺序与明确 fail 动作。

## Git hygiene / 提交说明

- 本轮开始前工作区已存在大量与本轮无关的脏改动与未跟踪文件（跨多条线与历史产物）。
- 为避免混入无关改动，本轮未提交 commit。
- 若后续提交，需仅对本轮相关文件做 selective commit。

Commit hash：未提交。
