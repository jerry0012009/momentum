# Breakout mixed-tail conditional honesty

- 时间：2026-03-15 08:31 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 子点：把 `down+flat mixed-tail overlay` 的 forward split verdict 再拆成 `target-pocket conditional honesty`

## 本轮为什么做这个

先检查了 repo 状态、最近几轮 optimization loop 记录，以及 `docs/TODO.md`。
当前 breakout 主线仍是：
- 正式 verdict = `shadow-admission queue / one_more_gate`
- 默认主候选 = `raw + avoid_fluctuating + ETH+SOL pair halfsize`
- `mixed-tail overlay` 当前只是 `shadow-only mixed gate`

最近几轮已经把 mixed-tail 补到了：
- strict pure-test mixed-tail tail snapshot
- non-overlap `5d/10d` forward blocks
- rolling `10d window / 5d step` shadow honesty
- admission queue

但还差一个更 deployment-facing 的问题没有回答干净：
**mixed-tail 的 split verdict，到底只是“整体 path 被非目标小时稀释”，还是 target mixed-tail pocket 自己也会转弱？**

这轮就只做这一刀，因为它最直接回答：这条 mixed-tail 线能不能诚实地写成一个更像样的 conditional policy。

## 本轮完成内容

1. 扩展 `scripts/build_support_breakout_v0_reports.py`
   - 给 mixed-tail overlay 的 non-overlap forward blocks 补上 block 内 target-pocket 条件累计字段：
     - `conditional_cumulative_before`
     - `conditional_cumulative_after`
     - `conditional_delta_pp`
   - 让 forward block 表不只看 overall path，也能直接看 mixed-tail target pocket 自己在每个 block 里有没有真的变好。

2. 刷新 breakout 主报告
   - 更新：`reports/site/factors/support_breakout_v0_h24/report.html`
   - 在 mixed-tail forward blocks 段落中新增更硬的读法：
     - split verdict 不是“非目标小时稀释”导致的假象
     - target pocket 自己在 active `5d` blocks 里也是 `1/2` 正、`1/2` 负

3. 同步刷新 closure / TODO 入口
   - 更新：`scripts/build_alpha_closure_board_report.py`
   - 更新：`docs/TODO.md`
   - 更新：`reports/site/factors/alpha_closure_board/report.html`
   - 更新：`reports/site/plans/momentum_todo.html`

## 结果摘要

### mixed-tail overlay 的 hard read（相对默认 `ETH+SOL pair halfsize`）

#### active `5-day` forward blocks
- overall path：`1/2` 改善，`1/2` 转弱
- target mixed-tail pocket 自己：`1/2` 改善，`1/2` 转弱

最好一格（约 `2026-02-17 -> 2026-02-22`）：
- overall delta vs baseline：约 `+0.55pp`
- target-pocket conditional delta：约 `+0.55pp`
- 说明这格不是 only-path illusion，target pocket 本身也真的更好

最弱一格（约 `2026-03-04 -> 2026-03-09`）：
- overall delta vs baseline：约 `-0.39pp`
- target-pocket conditional cumulative：约从 `+0.77%` 回落到 `+0.39%`
- target-pocket conditional delta：约 `-0.38pp`
- 说明这格不是“target pocket 其实没问题、只是被别的小时拖累”；而是 mixed-tail target pocket 自己也已经转弱

#### active `10-day` forward blocks
- overall path：`1/2` 改善，`1/2` 转弱
- target mixed-tail pocket 自己：同样延续 train/test split
- 最弱 `10d` block 的 target-pocket conditional delta 也约 `-0.38pp`

## 这意味着什么

这轮最重要的新信息是：

**mixed-tail 当前的 split verdict 不是表层噪音，而是 conditional pocket 自己也会在晚段 test block 里转弱。**

所以更诚实的 deployment-facing 读法要再收紧一格：
- `mixed-tail overlay` 不是死掉的方向
- 它也不只是单格 lucky pocket
- 但它现在还**不能**被写成“target pocket 已稳定受益”的 honest conditional policy
- 因此它仍只能停在：`shadow-only mixed gate`
- breakout 正式 verdict 继续维持：`one_more_gate`

换句话说：
- 这轮不是把 mixed-tail 判死
- 而是把它从“也许只是 overall split”进一步压实成：**late test mixed-tail pocket 自己也会转弱**
- 这让 admission 读法更硬，也更接近 Jerry 真正关心的“能不能继续往策略 / 伪实盘推进”问题

## 本轮验证

已执行：
- `python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
- `python3 scripts/build_support_breakout_v0_reports.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`

抽样核对：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_10d_20bps.csv`

新字段已出现，且最弱 block 的 `conditional_delta_pp` 约为 `-0.38pp`。

## Git / hygiene 记录

- 本轮开始前与结束后，`jerry/momentum` 工作区都存在大量与本轮无关的脏改动和未跟踪文件；`git status --short` 仅作为环境观测，不作为失败条件。
- 本轮只围绕 breakout mixed-tail conditional honesty 修改了：
  - `scripts/build_support_breakout_v0_reports.py`
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 对应报告 / plans 页面与 breakout artifact
- 没有把无关改动混提。
- 本轮**未做 selective commit**，原因是当前 worktree 明显不干净，且存在大量其他主线的历史脏文件与生成物；为避免误把无关改动一起提交，只做了文件落地与最小验证。

## 直接产物

- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_10d_20bps.csv`
