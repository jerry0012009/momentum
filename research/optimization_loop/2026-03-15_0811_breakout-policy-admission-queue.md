# Breakout：conditional policy admission queue 落地（2026-03-15 08:11 UTC）

## 为什么这次选这个
本轮继续按 `support_breakout_v0 / breakout-short follow-up` 主线推进，目标是把已经存在的 mixed-tail / pure-down 证据收敛成一张 **deployment-facing 的 admission queue**，直接回答：
- 哪刀可以继续保留在默认候选；
- 哪刀只能 shadow 观察；
- 哪刀应明确 reject。

这比继续补近义 wording 更接近 “能否继续往策略/伪实盘推进” 的决策需求。

## 做了什么改动
1. 在 `scripts/build_support_breakout_v0_reports.py` 新增：
   - `summarize_breakout_policy_admission_queue(...)`
   - 将 `gate-only / default pair / down+flat mixed-tail overlay / blunt pure-down overlay` 汇总到同一张 admission queue 表。
2. 导出新 artifact：
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_policy_admission_queue_20bps.csv`
3. 在 breakout 主报告新增队列表达区块：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
4. 同步更新 closure board breakout 证据文字，使其与 admission queue 读法一致：
   - `scripts/build_alpha_closure_board_report.py`
   - `reports/site/factors/alpha_closure_board/report.html`
5. 更新 TODO（已打勾）：
   - `docs/TODO.md` 新增 `2026-03-15 08:08 UTC` 条，明确 queue 排位结论。

## 核心结论（给 Jerry）
**一句话结论：breakout 线可以继续推进，但当前默认只能沿 `default pair halfsize` 主候选推进，`mixed-tail overlay` 仅可作为 shadow-only gate，`blunt pure-down overlay` 应保持 reject。**

**一句话证据：同一张 admission queue 下，`mixed-tail` 在 5d/10d non-overlap forward 都是 `1/2` 正、`1/2` 负，`pure-down` 虽把 down coverage 提到 `63/100` 但 overall 从 `19.90%` 回落到 `19.48%`，因此都不足以替代默认主候选。**

## 验证 / 证据
已执行最小必要验证：
- `python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
- `python3 scripts/build_support_breakout_v0_reports.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`

结果：成功。

抽样核对：
- `avoid_fluctuating_policy_admission_queue_20bps.csv` 已生成；
- breakout 报告中 admission queue 表已出现，并包含 `keep / default candidate`、`shadow-only mixed gate`、`reject blunt patch` 三类 verdict。

## 风险 / 边界
- 该 queue 仍是当前样本与当前 policy 范围内的 admission 辅助读法，不等同于实盘放行。
- `one_more_gate` 未解除，主硬缺口仍是更真实 forward / shadow honesty 的持续性，而不是再扩新变体池。

## 下一步建议
- 若下一轮继续 breakout，优先沿 `default pair halfsize + mixed-tail shadow observation` 补更前瞻窗口（而非回到更窄 context 分支）。
- 目标是进一步回答：mixed-tail 是否能稳定成为“附加 gate”，而不只是单段 pocket 修补。

## Commit hash
本轮未提交。

## 未提交原因
当前 git 工作区存在大量与本轮无关的历史脏改动与未跟踪文件；为避免误混提交，本轮只完成文件落地与验证，不做 selective commit。
