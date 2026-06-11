# 2026-03-15 18:53 UTC｜EMA：next-close action queue（把 waiting 变成到点可执行）

## 为什么这次选这个
- 先看了 repo 状态、`docs/TODO.md`、以及刚完成的 EMA 相关收口。
- 当前三条线里，EMA 仍是 closest-to-paper 主线；而 line-299（`market-close refresh / week-1 review`）仍未完成。
- 但在当前时点没有新的 completed bar，不能伪造 forward 结果；如果继续补近义说明页，价值很低。
- 所以本轮选 line-299 的 deployment-facing 邻近切片：**把 `on-clock waiting next close` 直接压成一张可执行队列**，让下一次真实收盘到来时按顺序落账，减少执行漂移。

## 本轮主点 / 子点
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：line-299（连续落下下一轮 market-close refresh / week-1 review）的执行准备层

## 做了什么改动

### 1) 新增 next-close 执行队列构建器
- 文件：`scripts/build_ema_psar_raw_alpha_report.py`
- 新增函数：`build_ema_paper_trading_next_close_action_queue(...)`
- 新增 artifact：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_next_close_action_queue.csv`

这张队列按 `next_expected_close_utc` 排序，覆盖 `active_primary / active_secondary_backstop / shadow_watch`，每条 lane 固定给出：
- `action_when_due`
- `if_not_due`
- `if_blocked`
- `why_this_step`

也就是把“到点做什么、没到点做什么、卡数据时怎么回滚”写成执行级动作，而不是口头记忆。

### 2) 报告页新增 Q35h（执行队列可视化）
- 页面：`reports/site/factors/ema_psar_raw_alpha/report.html`
- 新增小节：`Q35h. 下一次真实收盘一到，EMA 这张账本要按什么顺序落 refresh...`
- 新增表格：`EMA paper/shadow next-close action queue`

### 3) TODO 回写并勾选
- 文件：`docs/TODO.md`
- 新增并勾选：
  - `[x] EMA：把 on-clock waiting 压成 next-close action queue（到点可执行，不靠口头记忆）`
- 同时保留 line-299 未勾选（因为真实 `market-close refresh / week-1 review` 结果本轮尚无新 bar，不能伪造）。

## 验证 / 证据
最小验证：
1. `python3 -m py_compile scripts/build_ema_psar_raw_alpha_report.py scripts/build_plans_site.py`
2. `python3 scripts/build_ema_psar_raw_alpha_report.py`
3. `python3 scripts/build_plans_site.py`

结果：通过（仅有既有 matplotlib 中文字体 warning，不影响输出）。

关键产物检查：
- `ema_paper_trading_next_close_action_queue.csv` 已生成，当前排队前几条为：
  1. `Crypto 1d+1wk`（约 `2026-03-16 00:00 UTC`）
  2. `创业板ETF 1d`（约 `2026-03-16 07:00 UTC`）
  3. `贵州茅台 1d+1wk`（约 `2026-03-16 07:00 UTC`）
  4. `沪深300ETF 1d`（约 `2026-03-16 07:00 UTC`）
  5. `美股 1d+1wk`（约 `2026-03-16 20:00 UTC`）
- `report.html` 已出现 `Q35h` 与 artifact 链接。
- `docs/TODO.md` 已新增并勾选对应条目。

## 这轮为什么算有效推进
- 本轮没有伪造任何新 forward 证据，也没有继续堆近义 board。
- 但它把“等待下一次 close”从状态描述，变成了**到点即执行**的统一队列，直接缩短 line-299 的落地路径。
- 对 Jerry 的判断价值：现在可以明确区分“当前只是没到收盘时点”与“执行上真的没准备好”。

## 风险 / 边界
- 这不是 admission 升级，也不是新的 alpha 证据。
- 该队列只解决执行连续性，不替代真实 `market-close refresh / week-1 review` 的结果本身。
- 下一步仍必须等真实 completed bar 到来后，按队列落账并给出 keep/demote 结果。

## 执行层 hygiene
- `git status --short` 仅作环境观测；当前工作区存在大量与本轮无关的历史脏改/未跟踪文件。
- 本轮只触达 EMA 主线相关文件，不混提 breakout/Fibonacci 新改动。

## Commit hash
- HEAD：`c271463`
- 本轮未提交。
- 原因：当前工作区有大量与本轮无关脏文件；为避免混入无关改动，先只落地脚本/报告/TODO/记录。