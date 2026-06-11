# 2026-03-15 15:20 UTC — EMA first-refresh queue 落表（day-0 后首刷执行顺序）

## 本轮目标
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`alpha_closure_board` 同步 EMA 当前 deployment 阶段口径

## 为什么这次选这个
- 先检查了 repo 状态与最近几轮记录：EMA 已连续补到 `runbook -> day-0 snapshot`，当前最接近 paper trading。
- 按 steering，本轮不继续补近义 board 文案，而是补一刀更 deployment-facing 的“执行面”：把 `day-0 snapshot` 之后“先刷谁、失败怎么降级/回滚”写成可执行队列。
- 这条切片能直接帮助 Jerry 判断：EMA 是否已从“会写规则”进入“可以按账本真实推进”。

## 做了什么改动
1. 在 `scripts/build_ema_psar_raw_alpha_report.py` 新增函数：
   - `build_ema_paper_trading_first_refresh_queue(...)`
   - 输入：`day0_snapshot + first_week_review + secondary_recheck_queue`
   - 输出：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_queue.csv`
   - 作用：把首刷动作压成明确 lane：
     - `p0_primary_first_refresh`
     - `p1_secondary_front_queue`
     - `p1_shadow_refresh_only`
     - `p2_secondary_mid_queue`
     - `p3_secondary_backstop_watch`
     - `stoplist_audit_only`
   - 每条 row 都写死 `immediate_action / week1_focus / if_ok_then / if_fail_then`，避免继续停留在“下一步做 refresh”的口头层。

2. EMA 主报告新增并重排：
   - 新增 `Q34`：day-0 后 first-refresh queue
   - 原“边界”段顺延为 `Q35`
   - 相关产物列表新增 `ema_paper_trading_first_refresh_queue.csv`

3. 更新 `docs/TODO.md`：
   - 新增并勾选完成 `[x]`：
     - `EMA：把 day-0 snapshot 再压成 first-refresh queue，明确首刷顺序与 demote / rollback 动作`

4. 同步 `scripts/build_alpha_closure_board_report.py`：
   - EMA 状态从“已有 day-0 snapshot”升级为“已有 day-0 snapshot + first-refresh queue”
   - 路线图口径从 Step 3.5 更新为 Step 3.6（记账动作 + 首刷顺序已落地）

## 验证 / 证据
已做最小必要验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_alpha_closure_board_report.py`
4. `python3 scripts/build_plans_site.py`

抽查结果：
- 新 artifact 已生成：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_queue.csv`
- 队列前 3 条已明确：
  1) `创业板ETF 1d / A股-1d`（primary first refresh）
  2) `美股 1d+1wk（SPY/QQQ/AAPL） / 美股-1d`（secondary front queue）
  3) `沪深300ETF 1d / A股-1d`（shadow refresh-only）
- 页面已落地：
  - EMA 页出现 `Q34`（first-refresh queue）与 `Q35`（边界）
  - closure board 已出现 `day-0 ledger snapshot + first-refresh queue` 与 `Step 3.6` 口径
- 发布与通知：
  - 已执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 已发送邮件：`[momentum-auto] EMA首刷队列落表`

备注：构图阶段有 matplotlib CJK 字形 warning（历史现象），不影响 CSV/HTML 结果。

## 本轮结论（给 Jerry）
- 核心结论：EMA 线已从“首笔 day-0 账本已落表”进一步推进到“首刷执行顺序与失败动作已落表”，离可持续 paper/shadow 运行又近一格。
- 证据支撑：新增 first-refresh queue 将 primary / secondary / shadow / stoplist 的首刷优先级与 `if_fail_then` 动作写死，且已同步进入 EMA 主页与 closure board。

## 风险 / 边界
- 本轮没有新增 forward alpha 证据；只是把 day-0 后执行顺序与动作纪律固化。
- 真正改变 EMA admission 结论仍依赖后续真实 refresh / week-1 review 数据。

## 下一步建议
- 默认按这张 queue 执行真实首刷与 week-1 review，不要再补近义 board 页面。
- 研究侧如需再补，优先：
  - `沪深300ETF 1d` promotion honesty 是否能从 shadow 变厚；
  - `secondary front queue` 是否需要按规则降回 shadow。

## Git / 工作区说明
- 本轮先执行了 `git status --short`；工作区存在大量与本轮无关的历史脏改与未跟踪文件。
- 本轮未提交 commit，避免混入无关改动。

## Commit hash
- 未提交。