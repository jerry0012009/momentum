# Breakout：pure-test tail 前段 checkpoint honesty

- 时间：2026-03-15 09:40 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮只推进 1 个主点：继续沿 breakout 默认主候选 `raw + avoid_fluctuating + ETH+SOL pair halfsize`，把 strict pure-test tail 再切成“晚段 mixed-tail pocket 进来前”的 checkpoint honesty；不重开 EMA / Fibonacci，也不回头扩 breakout 变体。

## 为什么认领这刀

先检查了：
- `git status --short`
- `docs/AUTO_OPTIMIZATION_LOOP.md`
- `docs/TODO.md`
- 最近几轮 optimization loop 记录（尤其 08:53 / 09:13 / 09:20）

当前 breakout 主线已经很明确：
- 正式 verdict 仍是 `shadow-admission queue / one_more_gate`
- 当前主候选仍是 `default ETH+SOL pair halfsize`
- `mixed-tail overlay` 只能作为 `shadow-only mixed gate`
- 当前最关键的问题不是再写一层近义 verdict，而是更诚实地回答：

> default pair candidate 在 strict pure-test tail 里，到底是自己已经站稳，还是主要靠最后那段 mixed-tail pocket 才把结果补上来？

这刀比再补一层 wording 更接近 admission honesty，因为它直接回答：
- pure-test tail 前半段有没有“厚实”的 default sizing edge；
- 之前看到的 strict tail 正向结果里，有多少其实是最后 mixed-tail 两小时才补上来的。

## 本轮完成

### 1) 新增 default pair candidate 的 strict pure-test tail checkpoints

在 `scripts/build_support_breakout_v0_reports.py` 中新增并落地：
- 口径：基线 `avoid_fluctuating` vs 默认主候选 `avoid_fluctuating_eth_sol_pair_halfsize`
- 观测范围：只看 `split_mix = test` 的 strict pure-test tail
- checkpoints：`60h / 72h`

新增 artifact：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_checkpoints_20bps.csv`

### 2) 刷新 breakout 主报告

更新：
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增一节专门回答：
- 如果先不把最后两小时 `down+flat mixed tail` 算进去，default sizing 在 strict pure-test tail 前半段表现如何；
- 为什么整段 strict tail 的 `+0.77pp` 改善不能被误读成“default pair candidate 已经厚实通过 pure-test honesty”。

### 3) 同步 TODO / plans 页面

更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

已把本轮结果记为一条 `[x]` 最新补充，避免 breakout admission 口径继续漂移。

## 结果

`avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_checkpoints_20bps.csv` 的关键结果：

- `60h` checkpoint：
  - active hours ≈ `14`
  - affected hours ≈ `3`
  - delta vs gate-only ≈ `+0.08pp`
  - drawdown improve ≈ `0.00pp`
- `72h` checkpoint：
  - active hours ≈ `26`
  - affected hours ≈ `3`
  - delta vs gate-only ≈ `+0.08pp`
  - drawdown improve ≈ `0.00pp`

而整段 strict pure-test tail（到样本末尾）此前已经知道是：
- delta vs gate-only ≈ `+0.77pp`
- drawdown improve ≈ `+0.21pp`

因此更诚实的拆法是：
- 在最后两小时 `down+flat mixed tail` 进来前，default pair candidate 其实只是**没翻负**，并没有给出厚实的 pure-test edge；
- 整段 strict tail 的 `+0.77pp` 改善里，约 `+0.69pp` 是最后那两个 mixed-tail 小时才补上来的；
- 这说明 default pair candidate 目前还不能写成“pure-test tail 自己已经厚实通过”，更像是：
  - 前半段 `pure-test tail` = `thin positive / not thick`
  - 后半段 `mixed-tail pocket` = 提供了关键增量，但仍只够支撑 `shadow-only mixed gate`

## 本轮 verdict

本轮没有改写 breakout 总 verdict，但把 blocker 读法压得更清楚：

- `default pair halfsize`：继续保留为默认主候选
- `mixed-tail overlay`：继续停在 `shadow-only mixed gate`
- breakout 总 verdict：继续维持 `shadow-admission queue / one_more_gate`

一句话：

> strict pure-test tail 的总结果虽然仍为正，但 default pair candidate 在最后 mixed-tail pocket 进来前几乎只有 `+0.08pp` 的薄 edge；因此当前 admission blocker 依旧是 `pure-test / down-tail honesty`，而不是 closure wording 不够多。

## 变更文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_checkpoints_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py
python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py /root/clawd/jerry/momentum/scripts/build_plans_site.py
python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py
```

并确认：
- artifact `avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_checkpoints_20bps.csv` 已生成
- `support_breakout_v0_h24/report.html` 已出现新节标题：`晚段 mixed-tail pocket 进来前`
- plans 页面已同步出现本轮 TODO 补充

## Git / hygiene 备注

- 本轮开始前工作区已存在大量与本轮无关的脏改动与未跟踪文件；`git status --short` 仅作环境观测，不作为失败条件。
- 本轮未触碰 `pytrendline_event_validation_v3` 主线，也没有继续给 EMA 补近义 board / page。
- 当前 worktree 明显不干净，且包含大量与本轮无关的既有脏文件；为避免混入无关改动，这轮**未提交**。

## Post-log actions

- 已执行：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 结果：主页 index 已轻量刷新并发布到 `https://jp.jerrypsy.top/momentum/`
- 已执行：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-auto] breakout 纯测试尾段前段诚实度" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-03-15_0940_breakout-pure-test-pre-mixed-checkpoints.md`
  - 结果：邮件已发送到默认收件箱（`18810813576@163.com`）
