# 2026-03-15 10:50 UTC — breakout pure-test active-block 审计

## 本轮目标
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 紧邻子点：`ETH+SOL pair halfsize` 的 strict pure-test tail honesty
- 选择原因：上一轮已经把 breakout 的 `one_more_gate` 压成了执行型 `gate clearance protocol`，所以这轮不再补近义 protocol / wording，而是直接补一个更 deployment-facing 的小切片：默认主候选在 strict pure-test tail 里，是否已经能拆成多段独立可复用的 active block。这个问题比继续做 board / checklist 近义页，更直接关系到“要不要继续往 shadow/paper 推”。

## 先看当前上下文 / hygiene
- 先检查了 `git status --short`、`docs/TODO.md`、最近两轮日志（`2026-03-15_1031_breakout-mixed-tail-6h-forward-blocks.md`、`2026-03-15_1043_breakout-gate-clearance-protocol.md`）。
- 当前 repo 仍有大量与本轮无关的脏改动 / 未跟踪文件（EMA、pytrendline、其他站点生成物、workspace 其他目录等）；本轮继续推进 breakout，但**不会混提无关改动**。
- `pytrendline_event_validation_v3` 本轮未 reopen，只作为历史证据背景。

## 本轮完成的实际推进
1. 在 `scripts/build_support_breakout_v0_reports.py` 增加默认 `ETH+SOL pair halfsize` 的 strict pure-test tail non-overlap `6h` active-block 审计，并输出新 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_forward_blocks_6h_20bps.csv`
2. 将这刀结果直接接回 breakout 主报告：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增段落：`如果再强迫 strict pure-test tail 只按 non-overlap 6h active blocks 讲话：它到底有几段真能独立站住？`
3. 更新 `docs/TODO.md`，把这刀标记为已完成，并补入 deployment-facing 解释。
4. 同步重建 plans 镜像：
   - `reports/site/plans/momentum_todo.html`
   - `reports/site/plans/report.html`
   - `reports/site/plans/index.html`

## 这刀新增了什么判断力
### 1) strict pure-test tail 并没有形成“多段独立可复用”的 honest block
- 当前 non-overlap `6h` active-block 审计一共给出 `5` 段 block，但真正有 sizing 动作的只有 `1/5` 段。
- 这唯一一段就是最后那格 `2026-03-09 00:00 -> 06:00 UTC` 的 `test × down+flat` mixed-tail pocket。
- 该段相对 gate-only 的 delta 约 `+0.68pp`，条件 pocket 自己也约改善 `+0.68pp`。

### 2) 更早的 pure-test 前半段仍薄到连 active block 都难独立成形
- 前面那 `3` 个 `test × up` 小时，并没有凑成任何一个满足最小门槛（至少 `4` 个活跃小时）的 `6h` active block。
- 换句话说，前半段目前还只能写成“没翻负 / 证据很薄”，还不能写成“已经拆成多段都能独立站住”。

### 3) 这让 breakout 的 blocker 更收紧，而不是更宽松
- 这刀并没有推翻上一轮 `gate clearance protocol`，反而把 blocker 说得更硬了：
  - 当前 default pair candidate 还没有给出“多段独立可复用”的 pure-test honesty；
  - 唯一能单独成块的 active block，仍是最后那格 mixed-tail pocket；
  - 所以 breakout 正式 verdict 继续维持 `shadow-admission queue / one_more_gate`。
- 更诚实的 deployment-facing 读法是：**pure-test / down-tail honesty 仍是主 blocker，不是页面措辞问题。**

## 最小验证
- 运行：`python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- 结果：成功（exit 0）
- 核验：
  - 新 artifact 已生成：`avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_forward_blocks_6h_20bps.csv`
  - 主报告已出现新段落：`如果再强迫 strict pure-test tail 只按 non-overlap 6h active blocks 讲话：它到底有几段真能独立站住？`
- 另外运行：`python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- 结果：成功（`[ok] plans pages generated`）

## 变更文件（本轮相关）
- `docs/TODO.md`
- `scripts/build_support_breakout_v0_reports.py`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_forward_blocks_6h_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/index.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/report.html`
- `research/optimization_loop/2026-03-15_1050_breakout-puretest-active-blocks.md`

## git / commit 说明
- 当前工作区有大量与本轮无关的脏改动与未跟踪文件；不适合在这一轮安全地做整仓提交。
- 本轮默认**不提交**，避免把 EMA / pytrendline / 其他站点生成物与 breakout 这刀混在一起。
- 若后续要提交，更安全的做法仍是只挑本轮相关文件 selective commit。

## 后续建议（供下一轮直接接）
1. 若继续 breakout，默认仍只沿 `default pair halfsize` 主候选推进，但要优先找**真正命中 pure down 小时**的更前瞻 shadow / holdout honesty。
2. 不要再回头给 default pair candidate 补近义 wording；现在更关键的是回答：后续有没有真实 `pure down` 命中，以及命中后同段是否仍不翻负。
3. `mixed-tail overlay` 继续只保留为 shadow-only 子点，不因为这轮唯一 active block 恰好来自 mixed-tail pocket，就把它误读成 admission 已经过关。

## 发布 / 外发
- homepage index publish：已执行成功
  - 命令：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：`[ok] homepage index published -> /var/www/momentum-report/index.html`
  - URL：`https://jp.jerrypsy.top/momentum/`
- email：已发送成功
  - 命令：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout纯test段还站不成多段" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_1050_breakout-puretest-active-blocks.md`
  - 收件箱：`18810813576@163.com`
