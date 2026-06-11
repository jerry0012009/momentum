# Breakout mixed-tail rolling walk-forward honesty

- 时间：2026-03-15 08:17 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 子点：`down+flat mixed-tail protective gate` 的更前瞻 rolling shadow honesty

## 本轮为什么做这个

先检查了 repo 当前状态、最近几轮 optimization loop 记录，以及 `docs/TODO.md`。
当前 breakout 主线已经收敛到：
- 正式 verdict 仍是 `shadow-admission queue / one_more_gate`
- 默认主候选仍是 `raw + avoid_fluctuating + ETH+SOL pair halfsize`
- `mixed-tail overlay` 已经被压成 `shadow-only mixed gate`
- 但 steering 也明确要求：如果继续 breakout，优先沿 `down+flat mixed-tail` 补更长 / 更前瞻的 shadow honesty，而不是继续换标题重写 admission queue

所以这轮选的切片是：**把 `pair halfsize + down+flat mixed-tail overlay` 再补一层 `10-day window / 5-day step` rolling walk-forward honesty，回答它是不是只是单格 lucky pocket。**

## 本轮完成内容

1. 扩展 `scripts/build_support_breakout_v0_reports.py`
   - 新增 mixed-tail overlay 相对默认 `ETH+SOL pair halfsize` 的 rolling walk-forward 汇总：
     - `10-day window / 5-day step`
     - `min_active_hours=20`
   - 新增 artifact 导出：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_walkforward_windows_20bps.csv`

2. 刷新 breakout 主报告
   - 更新：`reports/site/factors/support_breakout_v0_h24/report.html`
   - 在 mixed-tail gate 段落中新增 rolling shadow honesty 小节
   - 把 mixed-tail 的口径从“只有 non-overlap split verdict”补成更诚实的双层读法：
     - overlap rolling windows：当前 active windows 不是负面
     - non-overlap forward blocks：仍然是 split verdict

3. 同步刷新 closure / TODO 入口
   - 更新：`scripts/build_alpha_closure_board_report.py`
   - 更新：`docs/TODO.md`
   - 更新：`reports/site/factors/alpha_closure_board/report.html`
   - 更新：`reports/site/plans/momentum_todo.html`

## 结果摘要

### mixed-tail overlay vs 默认 `ETH+SOL pair halfsize`

#### rolling walk-forward（10-day window / 5-day step）
- 真正触发 overlay 的 active windows：`3/3` 仍优于基线
- 其中累计 delta 区间：约 `+0.03pp ~ +0.57pp`
- 其中 `2/3` 个窗口同时伴随更浅回撤；最弱窗口虽然累计仍是正 delta，但回撤改善约 `0.00pp`
- active 段大致落在：`2026-02-10 -> 2026-03-02`

#### 这和上一轮 non-overlap 结果怎么一起读
- 更克制的 non-overlap `5-day` blocks：`1/2` 正、`1/2` 负
- 更克制的 non-overlap `10-day` blocks：`1/2` 正、`1/2` 负

## 这意味着什么

这轮最重要的不是“mixed-tail 已经过 gate”，而是：
- 它已经**不太像单格 lucky pocket**；因为 active rolling windows 当前 `3/3` 都还是正 delta
- 但它也**仍然不是稳定单调的附加 gate**；因为一压成 non-overlap forward blocks，马上就是 `1/2` 正、`1/2` 负

所以更诚实的 deployment-facing 读法应进一步收紧成：
- `mixed-tail overlay` = **shadow honesty improved, but still shadow-only mixed gate**
- 它对 breakout 的价值是：说明“下一道 gate”方向没死，而且不是只有单段 pocket 才成立
- 但它还不足以解除 `one_more_gate`，更不足以把 breakout 改写成 `shadow paper now`

换句话说：
- 这轮确实给 `mixed-tail` 补上了更前瞻的一层 honesty
- 但 admission verdict 不变：**继续沿默认 `pair halfsize` 主候选推进；mixed-tail 只保留为 shadow-only 附加 gate**

## 本轮验证

已执行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_alpha_closure_board_report.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

结果：成功。

抽样核对：
- 新 artifact `avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_walkforward_windows_20bps.csv` 已生成
- breakout 报告中已出现 `rolling walk-forward shadow observation` 小节

## Git / hygiene 记录

- 本轮开始前，`jerry/momentum` 工作区已存在大量**与本轮无关**的脏改动和未跟踪文件；`git status --short` 仅用于环境观测，不作为失败条件。
- 本轮只修改 / 生成了 breakout mixed-tail walkforward 相关脚本、报告、TODO 镜像与新 artifact，没有把无关脏改动混提。
- 当前 worktree 仍明显不干净；为避免误把其他线上的历史改动一起带进去，本轮**未做 selective commit**。

## 直接产物

- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_walkforward_windows_20bps.csv`
