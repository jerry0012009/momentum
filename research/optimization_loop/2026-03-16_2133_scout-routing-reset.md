# 2026-03-16 21:33 UTC｜Scout Seat：把默认主资源从 Rank 2 连续 wiring 重置到新的 paper/repo intake

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 判断：

- `Run 1 / Paper Seat`：`EMA` 当前是 `waiting_not_due / due_soon`，这轮没有新的 `due-now / overdue` refresh；
- `Live Seat`：仍暂空，没有 bot2 新 promoted candidate；
- 因此本轮应落到 `Run 2 / Scout Fast Lane`。

但本轮先比较了所有 active Scout 候选的边际价值，而不是默认继续做 `Rank 2`：

1. `Rank 2 combo_all`
   - 当前已是 `narrow paper pilot approved`；
   - 最近连续多轮已经补齐：`ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`；
   - 若再继续认领，只有在出现真实 `append-ready refresh/review row` 或一个会改变 paper verdict 的最小检查时才合理；否则就会违反 board 7.7，继续在近义 wiring 层空转。
2. `Rank 4 / Rank 4b crypto stat-arb`
   - clean replication 与唯一允许的一刀 `time stability` 都已完成，当前 verdict 都是 `park / evidence pool`；
   - 没有新的 pair universe / 新数据源 / 新 spec，不应再占本轮主资源。
3. `Rank 3 third-touch + EMA/MACD`
   - 最小 `Light Stability Pack` 已补齐，当前 hard verdict 已是 `park`；
   - 再做只会重复 closeout。
4. `Rank 1 τ-band`
   - 已完成最小复现与诚实检查，结论仍是 post-cost 绝对偏负；
   - 继续重看当前边际价值低。

因此本轮的硬判断不是再补一张 Rank 2 wiring 卡，而是：
- **把作战板明确重置成：下一轮起，`Scout Seat` 默认先去新的 `paper / repo based 5m / 15m crypto` intake / clean replication；`Rank 2` 只有在出现真实 append/review need 或 verdict-changing check 时才继续认领。**

## 本轮做了什么改动
只做了最小必要的 desk-level 路由修改，避免再次陷入同一路线的近义推进：

1. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 在 `Rank 2 combo_all` 条目下新增 `2026-03-16 21:30 UTC` 补充：
     - 明确 `Rank 2` 已连续补完最小 `narrow paper` wiring；
     - 若下一轮没有真实 `append-ready refresh/review row` 或 verdict-changing check，默认应把主资源让给新的 `paper / repo based 5m / 15m crypto intake`。
2. 更新 `Next 3 bot3 runs` 当前窗口排班
   - 把当前回退链从“`Scout Seat > Rank 2 paper-pilot minimal wiring > tiny-live plumbing`”收紧为：
   - `Scout Seat（fresh paper/repo intake first；Rank 2 only on real append/review need） > tiny-live plumbing > 其他维护 / 等 bot2 新点名`
3. 更新 `Run 2 — Scout Fast Lane` 的具体执行顺序
   - 新增显式规则：
     - 若 active 候选都已在 `park`，或 `Rank 2` 只剩近义 wiring 可补、却没有真实 `append/review` 需要或 verdict-changing check，默认优先转去新的 `paper / repo based 5m / 15m crypto source intake / clean replication`。

## 最小验证
已执行并通过：
1. `python3 scripts/build_plans_site.py`
2. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
3. `grep -n "fresh paper/repo intake first\|2026-03-16 21:30 UTC\|source intake / clean replication" docs/TODO.md reports/site/plans/momentum_todo.html`

验证结果：
- `docs/TODO.md` 已出现新的 `21:30 UTC` 作战板补充；
- `reports/site/plans/momentum_todo.html` 已同步新的回退链与 `Run 2` 顺序；
- 首页索引已刷新：`https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **当前没有任何已激活 Scout 候选值得继续默认吃掉主资源去做近义 wiring。**
- 更诚实的当前 desk 读法应是：
  - `Rank 2` 保留 `narrow paper pilot approved / paper-only`；
  - 但除非出现真实 `append/review` 需求或会改变 paper verdict 的最小检查，否则它不该继续主导 `Scout Seat`；
  - 下一轮起，`Scout Seat` 应优先回到新的 **paper / repo based 5m / 15m crypto** 候选 intake / clean replication。

## 对 desk 主线的意义
这轮减少的不是 alpha 不确定性，而是**排班漂移风险**：
- 避免 bot3 在 `EMA waiting_not_due` 时反复把 `Scout Seat` 花在同一条 `Rank 2` wiring 链上；
- 把默认主资源重新对准当前 board 真正要求的 fast-lane 行为：
  - `source intake`
  - `clean replication`
  - `Light Stability Pack`
  - `promote to narrow paper pilot / paper candidate / park`

## 网页可见落点
- `docs/TODO.md`
- `reports/site/plans/momentum_todo.html`
- `https://jp.jerrypsy.top/momentum/`

## 风险 / 边界
- 这轮是 **desk routing / hard verdict reset**，不是新的 alpha 证据；
- 也没有改变 `Rank 2` 的策略 verdict：它仍是 `narrow paper pilot approved / paper-only`；
- 这轮的目的只是停止无意义的连续 wiring，把下一轮默认动作重新对准新的 paper/repo scout intake。

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
