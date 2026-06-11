# 2026-03-15 10:43 UTC — breakout gate clearance protocol

## 本轮目标
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：`down+flat mixed-tail overlay`
- 选择原因：当前 steering 已把 breakout 明确放在更高执行优先级，且当前真正卡住 deployment / shadow admission 的，不再是“有没有整体路径”，而是 `one_more_gate` 到底**什么情况下才算过关**。这一刀比继续补近义 wording 或继续扩新分支，更接近 Jerry 判断“要不要继续往 shadow/paper 推”。

## 先看当前上下文 / hygiene
- 先检查了 `git status --short`、`docs/TODO.md`、以及最近两轮记录（`2026-03-15_1020_breakout-admission-blocker-audit.md`、`2026-03-15_1031_breakout-mixed-tail-6h-forward-blocks.md`）。
- 当前 repo 存在大量与本轮无关的脏改动/未跟踪文件（含 EMA、pytrendline、site 生成物、workspace 其他目录内容等）；本轮继续推进 breakout，但**不会混提无关改动**。
- `pytrendline_event_validation_v3` 本轮未重新认领，只作为历史证据背景。

## 本轮完成的实际推进
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增 `summarize_breakout_gate_clearance_protocol(...)`。
2. 产出新 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_gate_clearance_protocol_20bps.csv`
3. 将这张 protocol 直接接回现有 breakout 主报告：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增段落：`如果不想再反复解释：这条 breakout 线的 one_more_gate 具体怎样才算过关？`
4. 更新 `docs/TODO.md`，将这一刀标记为已完成并补入 deployment-facing 结果说明。
5. 另外同步刷新了 plans 页面，使 TODO 的最新口径能在站内可见：
   - `reports/site/plans/momentum_todo.html`
   - `reports/site/plans/report.html`
   - `reports/site/plans/index.html`

## 这刀新增了什么判断力
### 1) default pair halfsize（主候选）
- 不再只说“还卡在 one_more_gate”。
- 现在明确写成：只有当后续更前瞻的 `shadow / holdout` 证据**真正命中 pure down 小时**（当前仍是 `0/100`），且同一段 `pure-test / down-tail` 读法仍不翻负时，才有资格从 `one_more_gate` 再往 `shadow paper now` 走。
- 只要 `pure down coverage` 继续停在 `0/100`，且 strict tail 仍只像当前 `+0.77pp on 5/30h` 这种 very-thin edge，就继续卡住。

### 2) mixed-tail overlay（紧邻子点）
- 不再只说“shadow-only”。
- 现在明确写成：只有当它在 non-overlap / target-pocket 眼光下**不再给 split verdict**，才配继续升级。
- 当前仍停在：`5d = 1/2`、`10d = 1/2`，strict-tail `6h blocks = 2/4` 为正；所以还只能算 `shadow-only mixed gate`。

### 3) blunt pure-down overlay
- 正式固定为 `reject blunt patch`。
- 当前读法也更执行化：只要它还是“补到 coverage，但 overall delta 为负（当前约 `-0.42pp`）”，就不应再被误读成现成补丁。

## 为什么这比继续补 wording 更有用
- 它把 breakout 当前的 `one_more_gate` 从“结论”压成了“执行协议”：
  - 什么结果算真正推进；
  - 什么结果只是继续卡住；
  - 什么分支已经可以长期降级为 reject sanity check。
- 这样下一轮就不必再围绕同一个 blocker 反复换说法，而可以直接对照 protocol 判断：新增 evidence 到底有没有触及 admission gap。

## 最小验证
- 运行：`python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- 结果：成功（exit 0）
- 核验：
  - 新 artifact 存在：`avoid_fluctuating_gate_clearance_protocol_20bps.csv`
  - 主报告已出现新段落：`如果不想再反复解释：这条 breakout 线的 one_more_gate 具体怎样才算过关？`
- 另外运行：`python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 结果：成功（`[ok] plans pages generated`）

## 变更文件（本轮相关）
- `docs/TODO.md`
- `scripts/build_support_breakout_v0_reports.py`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_gate_clearance_protocol_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/index.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/report.html`
- `research/optimization_loop/2026-03-15_1043_breakout-gate-clearance-protocol.md`

## git / commit 说明
- 当前工作区有大量与本轮无关的脏改动与未跟踪文件；不适合在这一轮安全地做整仓提交。
- 本轮默认**不提交**，避免把 EMA / pytrendline / 其他站点生成物与 breakout 这刀混在一起。
- 若后续要提交，更安全的做法应是只挑本轮相关文件 selective commit。

## 后续建议（供下一轮直接接）
- 若继续 breakout，优先直接拿 protocol 当判据：
  1. 继续只沿 `default pair halfsize` 主候选找真正命中 `pure down` 的 forward / shadow honesty；
  2. `mixed-tail overlay` 继续只保留为 shadow-only 子点，除非 non-overlap / target-pocket split verdict 被真正打掉；
  3. 不再回到更窄 context 枝杈，也不再新增近义 board / checklist。

## 发布 / 外发
- homepage index publish：已执行成功
  - 命令：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - URL：`https://jp.jerrypsy.top/momentum/`
- email：已发送成功
  - 命令：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout过关条件压成执行协议" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_1043_breakout-gate-clearance-protocol.md`
  - 收件箱：`18810813576@163.com`
