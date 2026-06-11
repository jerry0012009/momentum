# breakout 当前样本 gate 正式冻结

## 为什么这次选这个
- 先看了 repo 状态、最近 auto loop 记录和 `docs/TODO.md`。
- breakout 线最近已经连续多轮都在围绕同一段历史样本补 `pure-test / down-tail` admission 证据，而且当前更硬结论已经收敛成：`pure down coverage = 0/100`、`pre-down bridge coverage = 0`、pure-test 前半段仍只有 very thin edge。
- 按今天的 steering，这种情况下下一刀不该继续切更细的 same-sample micro-slices，而应把 verdict 压成更 deployment-facing 的冻结口径，避免 bot3 下一轮又回到近义重写。

## 做了什么改动
- 把 `docs/TODO.md` 里那条 breakout 主候选 admission 任务从未完成改成已完成，并明确写成：
  - 当前样本的最后一道 gate 已压成 `freeze verdict`；
  - `same-sample admission freeze` 已在 TODO / breakout 主报告 / closure board 统一落口径；
  - `mixed-tail overlay` 继续只保留 `shadow-only` 观察项，不再与默认主候选并列消耗主资源。
- 更新 `scripts/build_alpha_closure_board_report.py`：
  - breakout 状态文案明确补上 `same-sample admission slicing 已冻结`；
  - 首页 closure summary 明确写成：breakout 现在仍是 `one_more_gate`，但当前样本里的 same-sample admission slicing 已基本冻结，下一次有效推进必须来自新的 `pure-test / down-tail` forward honesty，而不是继续在同一段历史样本里切片。
- 重新生成：
  - `reports/site/factors/alpha_closure_board/report.html`
  - `reports/site/plans/momentum_todo.html`（通过 `build_plans_site.py`）

## 验证 / 证据
- 运行：
  - `python3 scripts/build_alpha_closure_board_report.py`
  - `python3 scripts/build_plans_site.py`
- grep 复核通过：
  - `docs/TODO.md` 已出现 `same-sample admission freeze`；
  - `alpha_closure_board/report.html` 已出现 `same-sample admission slicing 已冻结`；
  - `plans/momentum_todo.html` 已同步新口径。

## 风险 / 边界
- 这轮没有新增 breakout 新证据，也没有重新跑重型回测；做的是把已经收敛的 blocker 诚实收口，减少后续重复劳动。
- breakout 线不是被 park；只是把“当前样本还能不能继续靠 retrospective admission slicing 挖出 overturn evidence”这件事明确收成：暂时不值得再挖。
- 下一次 breakout 真正有效推进，必须来自新的 shadow / holdout 里真实命中 `pure-test / down-tail` 的 forward 证据。

## 下一步建议
- 默认把主资源切回 `EMA` 的 deployment-facing 执行面（真实 `0` 真资金 shadow / paper 记账启动准备），而不是继续给 breakout 堆近义 gate 页面。
- 若后续 breakout 有新 forward/shadow 样本真正命中 `pure down` 或 pre-down bridge，再 reopen admission gate。

## Commit hash
- 未提交。

## 如果未提交，原因
- 当前 git worktree 有大量与本轮无关的既有脏改动与未跟踪文件；这轮只做了 selective 文档/closure sync，为避免混提无关改动，本轮不安全提交。
