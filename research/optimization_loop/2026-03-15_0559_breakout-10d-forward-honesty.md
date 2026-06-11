# 2026-03-15 05:59 UTC — breakout 10d forward honesty

## 本轮主点
- **主点：`support_breakout_v0` 的 longer forward / admission honesty**
- 延续最近两轮已经补过的：
  - `2026-03-15 05:12`：`down-tail honesty`
  - `2026-03-15 05:45`：non-overlap `5-day` forward blocks（`3/4` improve，`1/4` 约 `-0.56pp`）
- 本轮不再继续补 EMA 近义 board，也不再扩 breakout 分支；只回答一个更 deployment-facing 的问题：
  - **如果把默认 `ETH+SOL pair-conditioned halfsize` 的 non-overlap forward block 再放长到 `10-day`，它还站不站得住？**

## 为什么选这个点
- 当前 steering 已经把 breakout 线的 blocker 收窄到：
  1. `late-segment / pure-test transferability`
  2. `down tail honesty`
- `down-tail` 上一轮已明确看到：当前受影响约 `44` 小时里 pure `down = 0`，说明那块还没真正被碰到。
- 所以这轮就顺着另一条 deployment-facing 缺口继续压硬：
  - 不重复写“active windows 里 3/3 都更好”；
  - 也不满足于 `5-day` block 的 `usable but not monotonic`；
  - 直接看 **更长一点的 non-overlap `10-day` forward evidence**。

## 开始前环境观测
- 按要求先看了 repo 状态与最近在做什么：
  - `git status --short` 显示当前工作区本来就有大量既有脏文件，覆盖 docs / reports / scripts / artifacts / 上层 workspace。
  - 这不是失败条件；本轮继续推进，但明确避免混提无关改动。
  - 最近两轮主线确实都在 breakout admission 收口：`down-tail honesty` → `5-day forward-block honesty`。
- 因此本轮没有随机跳题，而是继续把 breakout admission 的同一条主缺口压紧一层。

## 本轮产出

### 1) 新增 artifact：non-overlap `10-day` forward blocks
新增文件：
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_10d_20bps.csv`

关键结果：
- 当前有动作的 `2/2` 个 `10-day` block 都优于 gate-only
- 两格分别约为：
  - `2026-02-20 ~ 2026-03-02`：`+0.53pp`，回撤改善约 `+0.50pp`
  - `2026-03-02 ~ 2026-03-12`：`+3.22pp`，回撤改善约 `+2.67pp`

这和上一轮的 `5-day` 证据合起来，给出的更诚实读法是：
- **短一点看：不是单调稳定**（`5-day = 3/4` improve，`1/4` 小回吐）
- **长一点看：方向仍站得住**（`10-day = 2/2` improve）

### 2) 更新 breakout v0 主报告
更新：
- `scripts/build_support_breakout_v0_reports.py`
- `reports/site/factors/support_breakout_v0_h24/report.html`

新增内容：
- 在原来的 `5-day non-overlap blocks` 之后，追加一段明确的 `10-day` non-overlap forward honesty 小节。
- admission verdict 的读法同步收紧为：
  - 一般性的 `late-segment transferability` 焦虑已经比前几轮更弱；
  - 当前真正还没过关的，更像是 **`pure-test / down-tail honesty`**，而不是“这刀是不是完全只靠 lucky patch”。

### 3) 更新 closure board
更新：
- `scripts/build_alpha_closure_board_report.py`
- `reports/site/factors/alpha_closure_board/report.html`

breakout 行现在更明确写成：
- `5-day` block 有起伏，但 `10-day` block 目前仍 `2/2` 为正；
- 因此它更像“长一点仍站得住、短一点会起伏”的 sizing candidate；
- breakout 仍是 `shadow-admission queue / one_more_gate`；
- 但 blocker 读法已从泛化的 late-segment 焦虑，收窄到更具体的 **`pure-test / down-tail`**。

### 4) 更新 TODO 与 plans 入口
更新：
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`

在 breakout admission 已完成条目下补了一条最新说明：
- `10-day` non-overlap forward blocks 当前有动作的 `2/2` 都优于 gate-only；
- 这说明 breakout 默认 sizing candidate 正在更接近 shadow admission；
- 但当前 still `one_more_gate`，原因更集中在 `pure-test / down-tail honesty`。

## 最关键结论（给 Jerry / deployment 决策用）
- breakout 默认 `ETH+SOL pair-conditioned halfsize` 现在已经**不太像只是后半段 lucky patch**；
- 但它也**还不够**被写成默认 shadow paper policy；
- 新的更诚实 admission 读法应是：
  - `5-day` 看：**usable but not monotonic**
  - `10-day` 看：**directionally still positive**
  - 所以一般性的 `late-segment transferability` 焦虑在下降
  - 但真正还没过关的是：
    1. `pure-test` 证据仍薄（当前只有约 `5` 小时、约 `+0.76pp`）
    2. `down-tail` 仍几乎没被真正碰到（pure `down = 0`）
- 因此 breakout 线当前最诚实的位置依旧是：
  - **`shadow-admission queue / one_more_gate`**
- 但它离 shadow paper 的距离，已经比“只会后段好看”的旧读法更近一步。

## 最小验证
已执行：
- `python3 -m py_compile scripts/build_support_breakout_v0_reports.py scripts/build_alpha_closure_board_report.py scripts/build_plans_site.py`
- `python3 scripts/build_support_breakout_v0_reports.py`
- `python3 scripts/build_alpha_closure_board_report.py`
- `python3 scripts/build_plans_site.py`

已检查：
- 新 artifact 存在：
  - `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_10d_20bps.csv`
- 关键短语已落到页面 / TODO：
  - `10-day`
  - `2/2`
  - `+0.53pp`
  - `+3.22pp`
  - `pure-test / down-tail honesty`

## 本轮改动文件
- `docs/TODO.md`
- `scripts/build_support_breakout_v0_reports.py`
- `scripts/build_alpha_closure_board_report.py`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_eth_sol_pair_halfsize_forward_blocks_10d_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/factors/alpha_closure_board/report.html`
- `reports/site/plans/momentum_todo.html`

## Git / 提交说明
- 当前 repo 与上层 workspace 存在大量与本轮无关的既有脏文件。
- 为避免误混，本轮**未提交**。
- 如果后续需要提交，必须做严格 selective commit；本轮理论上只应挑上述 breakout/TODO/board 相关文件。

## 下一轮建议
- breakout 线若继续，默认不要再回头补近义 board / closure-copy。
- 更值得的下一刀优先级应是：
  1. **真正面对 `down tail` 的 honesty**（若能找到实际触达样本）
  2. 或更贴近 shadow-run 的真实前瞻观察，而不是继续做近义静态表
