# Breakout mixed-tail forward honesty

- 时间：2026-03-15 08:06 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 子点：`down+flat mixed-tail protective gate` 的更前瞻 forward honesty

## 本轮为什么做这个

先看了 repo 当前状态、最近 optimization loop 记录、以及 `docs/TODO.md`。当前 breakout 主线已经明确卡在：
- 正式 verdict 仍是 `shadow-admission queue / one_more_gate`
- `down-tail coverage = 0/100` 仍是 hard gap
- blunt `pure down -> 0.5x` 不是现成补丁
- 因此更值得继续推进的是：沿 `down+flat mixed-tail` 这刀 very-small protective gate，补一层更前瞻的 honesty，而不是再堆近义 wording 或回到更窄 context 变体

所以这轮选的切片是：**把 `pair halfsize + down+flat mixed-tail protection` 再压成 non-overlap forward blocks，看它是不是只靠单段 tail 幻觉。**

## 本轮完成内容

1. 扩展 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `downflat overlay` 相对默认 `ETH+SOL pair halfsize` 的：
     - `5-day` non-overlap forward blocks
     - `10-day` non-overlap forward blocks
   - 新增对应 artifact 导出：
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_20bps.csv`
     - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_10d_20bps.csv`

2. 刷新 breakout 主报告
   - 更新：`reports/site/factors/support_breakout_v0_h24/report.html`
   - 新增 mixed-tail overlay forward-honesty 段落与两张 block 表
   - 报告口径从之前偏 hopeful 的 “promising gate candidate” 进一步收紧为：
     - `still shadow-only / promising but mixed gate candidate`

3. 更新 `docs/TODO.md`
   - 在 breakout admission 主条目下补入本轮已完成结果，并同步到 plans 镜像页

## 结果摘要

### 相对默认 `ETH+SOL pair halfsize` 的 mixed-tail overlay

#### 5-day non-overlap forward blocks
- active blocks：`1/2` 改善，`1/2` 回吐
- 最好一格：`2026-02-17 -> 2026-02-22`
  - delta vs baseline：约 `+0.55pp`
  - drawdown improve：约 `+0.51pp`
- 最弱一格：`2026-03-04 -> 2026-03-09`
  - delta vs baseline：约 `-0.39pp`
  - drawdown improve：约 `0.00pp`

#### 10-day non-overlap forward blocks
- active blocks：`1/2` 改善，`1/2` 回吐
- 最好一格：`2026-02-17 -> 2026-02-27`
  - delta vs baseline：约 `+0.57pp`
  - drawdown improve：约 `+0.51pp`
- 最弱一格：`2026-02-27 -> 2026-03-09`
  - delta vs baseline：约 `-0.40pp`
  - drawdown improve：约 `0.00pp`

## 这意味着什么

这刀 `down+flat mixed-tail` protection 仍然**不是死掉的方向**，因为：
- overall first-pass 仍是正向
- strict pure-test mixed tail 也仍有改善

但一旦压成更前瞻的 forward blocks，它就已经不是“多数窗口都稳稳更好”的状态，而是很明确的：
- `5-day` = `1/2` 正、`1/2` 负
- `10-day` = `1/2` 正、`1/2` 负

所以当前更诚实的读法不是“快过 gate 了”，而是：
- 这刀仍值得保留在 breakout 的 `one_more_gate` 队列里
- 但它现在只能写成 **shadow-only / promising but mixed gate candidate**
- 它还不足以补齐 breakout 的 admission gap，更不能解除 `one_more_gate`

换句话说：
- `blunt pure-down overlay` 已证明不是补丁
- `mixed-tail overlay` 比 blunt pure-down 更像正确方向
- 但它目前也只到“值得继续 shadow honesty”的程度，还没到“更长 forward 下已足够稳定”的程度

## 本轮验证

已执行：
- `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_support_breakout_v0_reports.py`
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

结果：均成功。

## Git / hygiene 记录

- 本轮开始前与结束后，`jerry/momentum` 工作区都已存在大量**与本轮无关**的脏改动和未跟踪文件（文档、其他报告、artifact、外层工作区文件等）。
- 本轮没有把这些无关改动混入提交。
- 由于当前 worktree 明显不干净，且生成物覆盖面较大，这轮**未做 selective commit**，避免误把其他线上的脏改动一起提交。

## 直接产物

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_20bps.csv`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_forward_blocks_10d_20bps.csv`
