# EMA day-0 ledger snapshot 落表（首个 `0` 真资金 paper/shadow 记账动作）

- 时间：2026-03-15 15:04 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`alpha_closure_board` 同步 deployment 阶段口径（仅围绕 day-0 snapshot 完成态）

## 为什么本轮选这个

先检查了 repo 状态、`docs/TODO.md` 与 12:29 / 13:44 / 14:00 / 14:05 / 14:30 几轮自动优化记录。

当前更 deployment-facing 的剩余硬门槛里，最直接、且仍未完成的一条是：

- `EMA：按 day-0 launch seed rows 真正启动首个 0 真资金 shadow / paper ledger snapshot`

这条比继续补近义 spec / protocol / board 更接近真实 paper/shadow 启动，也正好符合当前 steering：
- breakout 线在现有样本里的 retrospective slicing 已基本冻结；
- EMA 线已经连续补齐 `candidate spec -> operating spec -> monitoring board -> runbook -> kickoff checklist -> ledger template -> day-0 seed rows -> week1 review -> secondary recheck queue`；
- 下一刀更应该把这些规则真正落成首笔账本记录，而不是再新增一层近义页面。

## 本轮改动

### 1) `scripts/build_ema_psar_raw_alpha_report.py`

新增函数：`build_ema_paper_trading_day0_snapshot(...)`

输出 artifact：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_snapshot.csv`

做法：
- 复用现有 `day0_seed_rows + monitoring_board + first_week_review_scorecard + secondary_recheck_queue`；
- 把固定的 `11` 条 day-0 rows 真正写成首份前瞻 ledger snapshot；
- 每条 row 统一落下：
  - `paper_status`
  - `monitor_status`
  - `review_action`
  - `data_health`
  - `first_review_clock`
  - `day0_note`

当前 snapshot 的诚实口径：
- `创业板ETF 1d`：`start_primary_paper / kickoff_green`
- front-queue secondary（如 `SPY 1d` 对应的 `美股-1d`）：`kickoff_yellow_front_queue`
- mid-queue secondary：`kickoff_yellow_mid_queue`
- 厚 backstop secondary：`kickoff_green_backstop`
- `沪深300ETF 1d`：`stay_shadow_until_promotion_gate / kickoff_yellow_shadow`
- stoplist：继续 `keep_excluded / stopped`

重点是：这份 snapshot 不是历史回填，也不是新增 protocol；它是首个真正落表的 `day-0` 账本动作。

### 2) EMA 主报告新增 Q33，并把边界顺延为 Q34

文件：`reports/site/factors/ema_psar_raw_alpha/report.html`（由脚本生成）

新增：
- `Q33. 如果今天就真的把 0 真资金 shadow / paper 账本开出来，首份 day-0 ledger snapshot 应该长什么样？`

页面现在明确回答：
- 为什么这不是再补一张 board；
- 为什么 front-queue secondary 要在 day-0 就先记成 yellow 而不是假装都 green；
- 为什么 stoplist 也要占位成 reopen-only snapshot；
- 为什么这一步只代表首笔记账动作落表，不代表已经新增 forward alpha 证据。

同时：
- 原边界段由 `Q33` 顺延为 `Q34`；
- 相关产物列表新增 `ema_paper_trading_day0_snapshot.csv`。

### 3) `alpha_closure_board` 同步更新为“已落下首份 day-0 ledger snapshot”

文件：`scripts/build_alpha_closure_board_report.py`

同步更新：
- EMA 当前状态从“已有 runbook / checklist / seed rows”升级为“已落下首份 day-0 ledger snapshot”；
- 路线图口径改成：EMA 当前更像 `Step 3.5` —— 已迈出首笔 `0` 真资金记账动作，但还没有真实 forward review；
- 下一步从“开始开账”更新为“沿同一张账本继续做真实 refresh / week-1 review”。

### 4) `docs/TODO.md` 勾选完成

已将下列条目标记为完成：
- `[x] EMA：按 day-0 launch seed rows 真正启动首个 0 真资金 shadow / paper ledger snapshot（不要再继续新增近义 spec 页）`

并补上结果口径：
- 当前 `11` 条 day-0 rows 已统一写进首份 snapshot；
- `创业板ETF 1d` 已明确 `start_primary_paper`；
- front-queue secondary 会在 day-0 就落成 `kickoff_yellow_front_queue`；
- `沪深300ETF 1d` 继续只记 `stay_shadow_until_promotion_gate`；
- stoplist 继续 `keep_excluded`。

## 最小验证 / 证据

已执行：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`

抽查结果：
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_snapshot.csv` 已生成；
- snapshot 共 `11` 行，对应 `primary 1 + secondary 6 + shadow 1 + stoplist 3`；
- EMA 主报告已出现 `Q33` 与 `Q34`；
- `docs/TODO.md` 对应条目已 `[x]`；
- `reports/site/factors/alpha_closure_board/report.html` 已同步到“首份 day-0 ledger snapshot 已落表”的项目级口径。

备注：构图阶段仍有 matplotlib CJK 字形 warning（历史现象），不影响 CSV / HTML 产物。

## 本轮结论（对 Jerry 判断要不要继续往策略 / paper 推进的帮助）

这轮把 EMA 从“paper-ready 文档”推进成了“首笔 `0` 真资金账本记录已落表”：
- 现在不只是知道该跑谁、怎么 review、怎么 promote / demote；
- 还真正把第一份 `day-0` ledger snapshot 写出来了。

这意味着：
- EMA 线已经不再卡在“要不要开账”的抽象问题；
- 下一步默认该看真实 `forward refresh / week-1 review` 能不能沿同一张账本持续跑下去；
- 如果后续 forward 仍诚实，EMA 比 breakout 更接近继续往 paper trading / 小资金实盘评估推进。

## Git hygiene / 提交说明

- 本轮开始前，git 工作区已存在大量与本轮无关的已修改 / 未跟踪文件（跨 breakout、历史报告、外部缓存与其他研究线）。
- 本轮只围绕 EMA day-0 snapshot 主线推进，不把无关脏改动当作本轮成果。
- 本轮未提交 commit。
- 原因：当前 worktree 脏范围过大；此时直接提交容易把与本轮无关的改动混入。若后续需要提交，应只对本轮相关文件做 selective commit。
