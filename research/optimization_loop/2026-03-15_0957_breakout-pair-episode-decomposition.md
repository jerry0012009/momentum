# Breakout default pair candidate episode decomposition

- 时间：2026-03-15 09:57 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮只推进 1 个主点：把默认 `raw + avoid_fluctuating + ETH+SOL pair halfsize` 的受影响小时按**真实时间顺序**压成 episode decomposition，回答它现在到底是不是已经有一段像样的 pure-test honesty。

## 为什么认领这刀

按当前 steering，breakout 的最高优先级仍是补最后一道 admission gate，而且默认主候选已经明确收窄到：

- 主候选：`ETH+SOL pair-conditioned halfsize`
- mixed-tail overlay：只保留 `shadow-only` 观察项
- blocker：`pure-test / down-tail honesty`

上一轮（09:40 UTC）已经确认：如果先不把最后两小时 `down+flat mixed tail` 算进去，default pair candidate 在 strict pure-test tail 前半段的累计改善其实只剩约 `+0.08pp`。

所以这轮继续把问题压得更 deployment-facing 一点：

> 这 44 个默认 pair sizing 受影响小时，按真实时间顺序拆开后，到底是连续的 pure-test honesty，还是几段不同 context 拼出来的结果？

## 本轮完成

### 1) 新增 default pair candidate 的 episode artifact

在 `scripts/build_support_breakout_v0_reports.py` 中新增 `summarize_policy_affected_hour_episodes(...)`，把默认 `ETH+SOL pair halfsize` 的 affected hours 按：

- 时间连续性（1h 连续）
- `symbol_pair`
- `split_mix`
- `regime_mix`

压成 chronologically ordered episodes，并输出：

- `start_time / end_time`
- `hours`
- `hour_share_within_target`
- `conditional_cumulative_before / after`
- `delta_pp`
- `mean_hourly_return_before / after`

新增 artifact：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_episode_summary_20bps.csv`

### 2) 刷新 breakout 主报告

在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增一节：

- 把默认 pair candidate 的 `44` 个受影响小时按真实时间段拆开；
- 明确指出它当前不是“一整段厚实 pure-test honesty”；
- 明确哪几段在真正贡献 default pair candidate 的 delta。

### 3) 同步 TODO / plans 页面

- `docs/TODO.md` 为 breakout open item 增加一条 `[x]` 最新补充；
- 重新生成 `reports/site/plans/*`，确保入口页同步更新。

## 结果

默认 `ETH+SOL pair halfsize` 的 `44` 个受影响小时，按真实时间顺序当前压成 4 段：

1. `train × flat`：`14h`，条件累计约 `-2.02% -> -1.01%`，改善约 `+1.01pp`
2. `test+validate × up`：`25h`，条件累计约 `-3.79% -> -1.87%`，改善约 `+1.92pp`
3. `test × up`：`3h`，条件累计约 `-0.16% -> -0.08%`，改善约 `+0.08pp`
4. `test × down+flat`：`2h`，条件累计约 `-1.37% -> -0.69%`，改善约 `+0.68pp`

最重要的 deployment-facing 读法：

- default pair candidate 现在**不是**靠一整段连续 pure-test honesty 站住；
- 它的大头仍来自：`train × flat` 与 `test+validate × up` 这些 earlier / overlap episodes；
- 真正 pure-test 前半段（`test × up`）只给出约 `+0.08pp` 的 very thin edge；
- 最后那 `2h` 的 `test × down+flat` mixed-tail pocket 才又补出约 `+0.68pp`。

所以更诚实的答案是：

> default pair candidate 还不能写成“pure-test 自己已经很厚、可以往 shadow paper 升格”；它更像是 overlap carry 还在撑，真正 pure-test 只给出 very thin support，最后再被 mixed-tail pocket 补一刀。

## 本轮 verdict

本轮没有改写 breakout 的正式 verdict，反而把 blocker 压得更具体：

- `default pair halfsize`：继续保留为默认主候选
- breakout 正式 verdict：继续维持 `shadow-admission queue / one_more_gate`
- 当前 blocker：仍是 `pure-test / down-tail honesty`

一句话：

> 这条 breakout 主候选现在不是“已经有连续 pure-test 厚证据”，而是“earlier episodes + overlap carry 还在撑，pure-test 自己仍薄，最后 mixed-tail pocket 才补一点”。所以它离 shadow admission 更近了，但还没过线。

## 变更文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_episode_summary_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
python3 -m py_compile scripts/build_plans_site.py
python3 scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

本轮开始前 `git status --short` 已显示大量与本轮无关的脏改动与未跟踪文件；本轮结束后该情况仍存在，包括：

- 多条与 EMA / trendline / reading pages 相关的既有脏文件；
- workspace 级 `memory/`、缓存目录与大量未跟踪 artifact；
- 本轮生成路径之外的大量历史遗留未跟踪结果。

因此本轮**没有提交**，避免把无关改动混进 selective commit。若后续要提交，应先单独清理/隔离工作区，再只挑本轮 breakout episode decomposition 相关文件。