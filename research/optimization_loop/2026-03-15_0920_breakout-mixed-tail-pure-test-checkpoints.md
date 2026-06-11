# Breakout mixed-tail：strict pure-test tail checkpoints

- 时间：2026-03-15 09:20 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮只推进 1 个主点：继续沿 breakout 的 `down+flat mixed-tail overlay` 补一层**更前瞻、但更诚实**的 strict pure-test tail checkpoint honesty；不重开 EMA / Fib，也不继续堆近义 board。

## 为什么认领这刀

先检查了 `git status --short`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md`，以及最近几轮 optimization loop 记录。

当前 steering 已经很明确：
- breakout 仍是最高优先级；
- 默认主候选仍是 `raw + avoid_fluctuating + ETH+SOL pair halfsize`；
- `down+flat mixed-tail overlay` 只能作为 `one_more_gate` 的 shadow-only 候选继续观察；
- 但如果继续做 breakout，本轮应该优先补 **更长 / 更前瞻的 mixed-tail honesty**，而不是回到更窄 context 分支或继续写近义结论。

最近几轮 mixed-tail 已经连续补过：
- rolling walk-forward
- non-overlap `5d/10d` forward blocks
- target-pocket conditional honesty
- cumulative `5/10/15/20-day` shadow checkpoints

因此这轮不再重复“它是不是 single lucky pocket”这一层，而是把问题压得更 deployment-facing 一点：

> 如果只盯 **strict pure-test mixed tail** 本身，并按更接近实盘 review 的 `6/12/18/24h` 累计 checkpoint 看，mixed-tail overlay 的 edge 到底是稳定存在，还是很快就被压扁？

这刀的价值在于：
- 它仍然沿 breakout / mixed-tail 主线推进；
- 它比再补一张 overall wording 更接近真实 shadow review；
- 它直接回答“这刀能不能被写成更诚实的 conditional protection patch”。

## 本轮完成

### 1) 新增 strict pure-test tail 的小时级 cumulative checkpoints

在 `scripts/build_support_breakout_v0_reports.py` 中新增：
- `summarize_hourly_pair_shadow_checkpoints_hours(...)`

并把它应用到：
- 基线：`avoid_fluctuating_eth_sol_pair_halfsize`
- 对照：`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay`
- 观测口径：只看 `split_mix = test` 的 strict pure-test mixed tail
- review hours：`[6, 12, 18, 24]`

新增 artifact：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_checkpoints_20bps.csv`

### 2) 刷新 breakout 主报告

更新：
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增一节专门回答：
- strict pure-test mixed tail 的 `6/12/18/24h` checkpoints 是否翻负；
- strongest checkpoint 有多强；
- weakest checkpoint 有多薄；
- 为什么这仍不足以把 mixed-tail 从 `shadow-only` 提升成 admission clearance。

### 3) 同步 TODO / plans 入口

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

已把本轮结果记成一条 `[x]` 最新补充，避免 breakout admission 口径继续漂移。

## 结果

相对默认 `ETH+SOL pair halfsize` 基线，strict pure-test mixed tail 内部的 cumulative checkpoints 为：

- `6h`：约 `+0.41pp`，回撤改善约 `+0.55pp`
- `12h`：约 `+0.12pp`，回撤改善约 `+0.87pp`
- `18h`：约 `+0.22pp`，回撤改善约 `+0.87pp`
- `24h`：约 `+0.08pp`，回撤改善约 `+0.87pp`

对应读法：
- 当前 `4/4` checkpoints 仍为正，所以它**不是**“只靠最后一个终点碰巧没翻负”的假 patch；
- 但 delta 也确实没有稳定扩张，反而从前 `6h` 的 `+0.41pp` 很快压到 `24h` 的 `+0.08pp`；
- 这说明 mixed-tail overlay 在 strict pure-test tail 里更像 **方向没塌、但 edge 很薄** 的 protective gate，而不是可直接 promotion 的 conditional policy。

## 本轮 verdict

本轮结果没有改写 breakout 正式 verdict，但把 mixed-tail 的诚实位置收得更紧：

- `default pair halfsize`：继续保留为 breakout 默认主候选
- `down+flat mixed-tail overlay`：仍是 `shadow-only mixed gate`
- `blunt pure-down overlay`：维持 reject / sanity check
- breakout 总 verdict：继续维持 `shadow-admission queue / one_more_gate`

一句话：

> mixed-tail overlay 在 strict pure-test tail 里没有立刻翻负，但优势衰减得很快；它更像“还活着、但很薄”的 shadow gate，而不是能补掉 breakout admission hard gap 的 clearance patch。

## 变更文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_checkpoints_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_plans_site.py
python3 scripts/build_support_breakout_v0_reports.py
python3 scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

- 本轮开始前工作区已经存在大量与本轮无关的脏改动与未跟踪文件；`git status --short` 仅作环境观测，不作为失败条件。
- 本轮只围绕 breakout mixed-tail 的 strict pure-test checkpoint honesty 落地了最小必要修改；没有去碰 `pytrendline_event_validation_v3` 主线，也没有继续新增 EMA 的近义 board。
- 当前 worktree 明显不干净，不适合安全做 selective commit；因此这轮**未提交**，避免把无关脏文件一并混入。

## Post-log actions

- 已执行：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- 结果：主页 index 已轻量刷新并发布到 `https://jp.jerrypsy.top/momentum/`
- 已执行：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout mixed-tail 纯测试尾段 checkpoint" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_0920_breakout-mixed-tail-pure-test-checkpoints.md`
- 结果：邮件已发送到默认收件箱。
