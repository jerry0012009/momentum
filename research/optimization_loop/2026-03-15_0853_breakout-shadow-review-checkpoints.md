# Breakout default pair halfsize：shadow review checkpoints

- 时间：2026-03-15 08:53 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 子点：把默认 `raw + avoid_fluctuating + ETH+SOL pair halfsize` 再压成更接近 shadow review 的累计 checkpoint honesty

## 本轮为什么做这个

先检查了 repo 当前状态、最近几轮 optimization loop 记录、`docs/AUTO_OPTIMIZATION_LOOP.md` 与 `docs/TODO.md`。

当前 steering 已明确：
- breakout 仍是最高执行优先级；
- `EMA` 线最近已连续补齐 `candidate / operating / monitoring` 近义层，不应继续堆类似页面；
- breakout 线当前默认主候选仍是 `raw + avoid_fluctuating + ETH+SOL pair halfsize`；
- `mixed-tail overlay` 只能保留为 `shadow-only mixed gate`，不应继续反客为主。

最近几轮已经连续沿 mixed-tail 补了：
- forward honesty
- rolling walk-forward
- conditional target-pocket honesty
- admission queue

所以这轮不再继续给 mixed-tail 堆近义证据，而是回到 **默认主候选本身**，补一刀更 deployment-facing 的问题：

**如果把默认 `pair halfsize` 从首个触发日起按 shadow review checkpoint 累积看，`5/10/15/20` 天时它会不会中途翻回 gate-only 下方？**

这刀的价值在于：
- 它比再补一张局部 block 表更接近真实 shadow review；
- 它直接回答 Jerry 更关心的 admission 问题：默认主候选到底只是局部起伏里看起来还行，还是累计 review 也还站得住；
- 同时又不会重新把资源拉回 mixed-tail 支线或 wording/cleanup。

## 本轮完成内容

1. 扩展 `scripts/build_support_breakout_v0_reports.py`
   - 新增 `summarize_hourly_pair_shadow_checkpoints(...)`
   - 口径：从首个 `ETH+SOL pair halfsize` 触发日开始，对默认主候选相对 gate-only 计算累计 shadow review checkpoint：
     - `5d`
     - `10d`
     - `15d`
     - `20d`
   - 不是 overlapping rolling，也不是切成互斥 forward block；而是更像“如果 shadow 运行后在这些 review 点做累计复盘，会看到什么”。

2. 新增 artifact
   - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_shadow_checkpoints_20bps.csv`

3. 刷新 breakout 主报告
   - 更新：`reports/site/factors/support_breakout_v0_h24/report.html`
   - 在默认 `pair halfsize` 的 admission 段落中新增 `shadow review checkpoint` 小节
   - 把当前更诚实的读法压成：
     - local non-overlap `5-day` blocks 不是单调；
     - 但 cumulative shadow review checkpoints 当前还没有翻负。

4. 同步刷新 closure / TODO / plans 入口
   - 更新：`scripts/build_alpha_closure_board_report.py`
   - 更新：`docs/TODO.md`
   - 更新：`reports/site/factors/alpha_closure_board/report.html`
   - 更新：`reports/site/plans/momentum_todo.html`

## 结果摘要

### 默认 `ETH+SOL pair halfsize` 相对 gate-only 的 cumulative shadow review checkpoints

从首个触发日起算，当前 `5/10/15/20` 天 review checkpoint 为：

- `5d`：约 `+1.04pp`，回撤改善约 `+0.50pp`
- `10d`：约 `+0.53pp`，回撤改善约 `+0.50pp`
- `15d`：约 `+3.24pp`，回撤改善约 `+3.12pp`
- `20d`：约 `+3.95pp`，回撤改善约 `+3.12pp`

也就是：
- 当前有动作的 `4/4` 个 checkpoint 都仍优于 gate-only；
- 最弱也不是 late checkpoint，而是 `10d` checkpoint，约仍有 `+0.53pp`；
- 到 `20d` review 时，默认主候选相对 gate-only 仍约领先 `+3.95pp`。

### 这和已有 `5d/10d` non-overlap blocks 怎么一起读

更诚实的合并读法现在是：

- **block 口径：**不是单调稳定
  - `5-day` non-overlap blocks = `3/4` 改善、`1/4` 回吐
  - `10-day` non-overlap blocks = `2/2` 改善
- **cumulative shadow review 口径：**目前没翻负
  - `5/10/15/20-day` checkpoints = `4/4` 仍优于 gate-only

所以当前默认主候选最诚实的位置不再只是：
- “长一点仍站得住、短一点会起伏”

而是可以进一步收紧成：
- **local blocks 会起伏，但 cumulative shadow review 目前还没有翻回 gate-only 下方。**

## 这意味着什么

这轮最重要的新信息不是“breakout 已经过 gate”，而是：

**默认 `pair halfsize` 的一般性 transferability 焦虑继续下降了。**

原因是：
- 它确实不是单调稳定，这点 `5-day` forward blocks 已经诚实承认；
- 但如果换成更贴近真实 shadow 运行的累计 review 眼光，当前还没有出现“随着 review horizon 拉长，候选又跌回 gate-only 下方”的现象。

因此更 deployment-facing 的 admission 口径现在应更新成：
- `default pair halfsize` = **still one_more_gate, but cumulative shadow review not negative**
- breakout 正式 verdict 仍是：`shadow-admission queue / one_more_gate`
- 当前 blocker 已更集中在：
  1. `down-tail coverage = 0/100`
  2. pure-test pocket 仍薄
  3. mixed-tail overlay 仍只能停在 `shadow-only mixed gate`

换句话说：
- 这轮不是把 breakout 判成可直接 paper；
- 而是把“默认主候选会不会一拉长就塌”这个担忧再压小一格；
- 现在更像该继续盯真正的 `down-tail / pure-test honesty`，而不是继续怀疑 cumulative review 已经翻负。

## 本轮验证

已执行：
- `python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
- `python3 scripts/build_support_breakout_v0_reports.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

抽样核对：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_shadow_checkpoints_20bps.csv` 已生成
- breakout 报告已出现 `shadow review checkpoint` 小节
- `docs/TODO.md` 已出现 `2026-03-15 08:53 UTC` 最新补充
- closure board breakout 证据已同步出现 cumulative checkpoint 读法

## Git / hygiene 记录

- 本轮开始前与结束后，`jerry/momentum` 工作区都存在大量与本轮无关的脏改动与未跟踪文件；`git status --short` 仅作为环境观测，不作为失败条件。
- 本轮只围绕 breakout 默认主候选的 cumulative shadow review honesty 修改了：
  - `scripts/build_support_breakout_v0_reports.py`
  - `scripts/build_alpha_closure_board_report.py`
  - `docs/TODO.md`
  - 对应 breakout / closure / plans 页面与新 artifact
- 没有把无关改动混提。
- 本轮**未做 selective commit**，原因是当前 worktree 明显不干净，而且相关生成脚本与页面本身混有大量其他主线历史脏改动；为避免误把无关文件一起提交，只做了文件落地、验证与发布。

## 直接产物

- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_shadow_checkpoints_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`
- `research/optimization_loop/2026-03-15_0853_breakout-shadow-review-checkpoints.md`
