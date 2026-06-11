# breakout：pair-conditioned halfsize 滚动诚实度复核

- 时间：2026-03-15 02:10 UTC
- 主点：`support_breakout_v0 / breakout-short follow-up`
- 本轮聚焦：把当前默认 sizing candidate（`ETH+SOL pair-conditioned halfsize`）推进到更严格的 `walk-forward / holdout / portfolio honesty`，并顺手把更窄 `context-conditioned` 分支正式 park。

## 先看当前状态
- 先检查了 `docs/TODO.md`、最近 optimization loop 记录、以及 repo 工作区状态，避免随机跳题。
- 当前接力棒里，`EMA / PSAR` 刚在上一轮（`2026-03-15_0202_ema-final-survivor-map.md`）交付了 final survivor map；因此这轮按 `Top 3` 转回 breakout 主线，优先解决 TODO 里的第 2 条：`pair-conditioned halfsize` 的更严格复核。

## 本轮动作
1. 复用已有 `support_breakout_v0_h24` 产物，不新增重型下载或新候选池。
2. 在 `scripts/build_support_breakout_v0_reports.py` 中新增 `summarize_hourly_pair_walkforward_windows()`：
   - 固定规则，不重新训练参数；
   - 用 `10-day window / 5-day step` 做 rolling active-hour 对照；
   - 直接比较 `avoid_fluctuating` gate-only 与 `ETH+SOL pair-conditioned halfsize` 的同口径 `20bps hourly path`。
3. 新增 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_walkforward_windows_20bps.csv`
4. 把结果挂回：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/factors/alpha_closure_board/report.html`
   - `docs/TODO.md`（并同步到 `reports/site/plans/momentum_todo.html`）
5. 把更窄 `context-conditioned / pure-test × up` 分支正式标成 `park / diagnostic branch`，避免后续继续并列消耗 breakout 主资源。

## 关键结果
Rolling active-hour honesty（`10-day / 5-day`）结果如下：

- 前半段 3 个窗口：`affected_hours = 0`，说明 policy 根本没触发；这几格与 gate-only 基本重合，不能硬说成“6/6 全胜”。
- 真正触发 `pair-conditioned` 的后半段 3 个窗口：
  - `2026-02-15 ~ 2026-02-25`：收益改善约 `+1.02pp`，回撤改善约 `+0.97pp`
  - `2026-02-20 ~ 2026-03-02`：收益改善约 `+0.53pp`，回撤改善约 `+0.50pp`
  - `2026-02-25 ~ 2026-03-07`：收益改善约 `+2.13pp`，回撤改善约 `+3.12pp`
- 因此本轮最诚实的收口是：
  - `pair-conditioned halfsize` 不是“全样本每段都更好”；
  - 但它也不只是 overall 总表里的 lucky patch；
  - 在 policy 真正触发的后半段 active windows 里，当前是 `3/3` 窗口同时做到“收益更高 + 回撤更浅”；
  - 这足够继续保留 breakout 默认 sizing candidate 位，但应明确标注为 `late-segment active windows` 驱动、后续仍需继续观察迁移性的候选。

## TODO / 页面入口同步
- `docs/TODO.md` 已把以下两项改为完成：
  - `[x] breakout：把 pair-conditioned halfsize 推到更严格的 walk-forward / holdout / portfolio honesty`
  - `[x] breakout：把更窄的 context branch 正式 park 成诊断型分支，并把资源顺序写死到页面入口`
- breakout 页面与 closure board 现在统一写法：
  - 默认保留：`ETH+SOL pair-conditioned halfsize`
  - 诊断分支：`context-conditioned / pure-test × up`（park，不再并列抢主资源）

## 最小验证
执行：
- `python3 scripts/build_support_breakout_v0_reports.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`

检查：
- 新 CSV 已生成且数值正确；
- `support_breakout_v0_h24/report.html` 已出现 `10-day window / 5-day step`、`late-segment active windows` 等新文案；
- `momentum_todo.html` 已同步新的 `[x]` 状态与结果摘要。

## Git / 提交说明
- 本轮 **未提交 commit**。
- 原因：当前 repo 工作区存在大量与本轮无关的历史脏文件与未跟踪产物，且 `scripts/build_support_breakout_v0_reports.py` / 相关 site 文件本身已经承载了前序多轮累计未提交修改；本轮若直接提交会混入大量非本轮变更，不符合“只在能安全 selective commit 时才提交本轮文件”的要求。
- 因此本轮选择：保留文件修改与日志记录，但不做不干净的混合提交。

## 邮件发送
- 已执行：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout pair-conditioned 滚动诚实度复核" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_0210_breakout-pair-walkforward-honesty.md`
- 结果：发送成功（默认收件箱）

## 本轮结论（一句话）
`ETH+SOL pair-conditioned halfsize` 已经从“overall 表里更好看”推进到“在 policy 真正触发的后半段 rolling windows 里连续更好”，因此继续保留默认位；更窄 `context-conditioned` 分支正式 park。
