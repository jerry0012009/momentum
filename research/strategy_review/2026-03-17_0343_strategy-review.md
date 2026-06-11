# 2026-03-17 03:43 UTC · Desk Board Review

## 本轮一句话判断

**这轮对 bot2 来说属于“按最新已生效作战板做的无额外换席巡检”，但 `Scout Seat` 的分级口径已经真实升级：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 方面，`Rank 17 pullback recovery confirmation` 已在 03:34 UTC 那轮 genuinely verdict-changing scope check 后，从 `paper candidate pool` 进一步升格到 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，而 `Rank 18 / 19 / 20` 都已完成 `clean replication + Light Stability Pack` 并压回 **`P0 / park / evidence pool`**。因此当前 desk 的默认顺序已不再是“Rank 18 clean replication next”，而应收紧为：**`fresh paper / repo based 5m / 15m crypto intake first`；仅当 `Rank 17` 或 `Rank 2` 出现真实 append/review need 或 genuinely verdict-changing check 时，才回补现有 P3。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `2026-03-17 00:20 UTC` 已实际执行：
     - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - `ema_paper_trading_refresh_history.csv` 已新增：
     - `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-16 00:00 UTC`
   - 当前 due guardrail 显示：
     - A 股下一次 close：`2026-03-17 07:00 UTC`
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
   - 因此当前对 `Paper Seat` 的正确读法仍是：
     - **`running paper pilot / waiting_not_due`**
   - 当前没有新的 due-now / overdue lane，所以不该让 `Paper Seat` 抢回默认主资源。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `Rank 17` 虽已升到 `P3 / narrow paper pilot`，但当前仍是 **paper-only（ETH+SOL 窄范围 pilot）**，还不是 `tiny-live review candidate / P4`；
   - `Rank 2` 也仍是 paper-only 的 P3，而不是新的 promoted tiny-live challenger；
   - 因此当前 desk call 继续是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 17 已从 P2 升到 P3，成为当前默认最强 Scout 存活线**
   - `Rank 17 pullback recovery confirmation` 先完成：
     - `paper/repo based source mapping -> clean replication -> Light Stability Pack`
   - 随后进入：
     - `P2 / paper candidate pool`
   - 又在 `03:34 UTC` 完成了一次 genuinely verdict-changing 的最小 scope-honesty check：
     - **不改信号规则，不追新 bar，只把 BTC 弱腿从运行 scope 里诚实剥离，只看 ETH+SOL**
   - 新的窄范围 friction ladder：
     - `6bps/side ≈ +24.12%`
     - `10bps/side ≈ +16.66%`
     - `15bps/side ≈ +7.95%`
     - `20bps/side ≈ -0.12%`
     - `15bps/side positive_asset_ratio = 2/2`
   - 因此当前更诚实的 desk 读法已升级为：
     - **`P3 / narrow paper pilot approved（ETH+SOL only）`**
     - `BTC` 继续 **`P0 / park / excluded red-watch leg`**
   - 这轮真正减少的是真实 gate：
     - 不再把 BTC 弱腿混进同一个 pilot headline 里；
     - 也不再让 Rank 17 长期卡在 `P2` 位置追求更漂亮证据。

4. **Rank 18 / 19 / 20 已连续压回 P0，当前不再占默认主资源**
   - `Rank 18 EMA neighborhood consensus / plateau-stable crossover`：
     - 已完成 `clean replication + Light Stability Pack`
     - 当前 hard verdict = **`P0 / park / evidence pool`**
     - `plateau_vote_5of9_spread_guard @ 6bps ≈ -19.89%`、`positive_asset_ratio=0/3`
   - `Rank 19 box consolidation / structure breakout`：
     - 已完成 `clean replication + Light Stability Pack`
     - 当前 hard verdict = **`P0 / park / evidence pool`**
     - 主变体 `accumulation_ready @ 6bps ≈ -20.13%`、`positive_asset_ratio=0/3`
   - `Rank 20 price-volume divergence breakout filter`：
     - 已完成 `clean replication + Light Stability Pack`
     - 当前 hard verdict = **`P0 / park / evidence pool`**
     - 主变体 `pvd_break24_delta0.5_warn3 @ 6bps ≈ -39.22%`、`positive_asset_ratio=0/3`
   - 这意味着当前 `Scout Seat` 已经不是“Rank 18 clean replication next”，而是：
     - **P0 证据池扩充完毕；P3 / P2 才是现在真正应被比较与预算管理的层。**

5. **Rank 2 继续是 P3，但当前优先级落后于 Rank 17 / fresh intake**
   - `Rank 2 combo_all` 仍是 **`P3 / narrow paper pilot approved`**；
   - 但它近期已连续补完：
     - `ledger template -> refresh seed -> weekly review seed -> writeback seed -> continuity snapshot -> refresh history`
   - 当前更诚实的 desk 读法仍是：
     - 若没有真实 `append/review need` 或 genuinely verdict-changing check，就不应继续默认回补 `Rank 2`。
   - 所以当前 P3 里的默认排序更接近：
     - `Rank 17（新升 P3，且 scope 更窄更诚实）`
     - `Rank 2（老 P3，仅在真实 need 时回补）`

## P0 / P1 / P2 / P3 / P4 当前分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1`
  - `Rank 3`
  - `Rank 4`
  - `Rank 4b`
  - `Rank 5`
  - `Rank 7`
  - `Rank 8`
  - `Rank 9`
  - `Rank 10`
  - `Rank 11`
  - `Rank 12`
  - `Rank 13`
  - `Rank 14`
  - `Rank 15`
  - `Rank 16`
  - `Rank 18`
  - `Rank 19`
  - `Rank 20`
  - 以及 `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate / 只配 1 次便宜诚实检查**
  - **当前默认空缺**（没有值得继续给 1 次便宜检查但尚未升/杀的 active line）
- **P2 = paper candidate**
  - **当前默认空缺**（`Rank 17` 已从 P2 升到 P3；没有其他存活在 P2 的 active line）
- **P3 = narrow paper pilot**
  - `Rank 2 combo_all`
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## 当前 weakest / should-park lines

- 继续把 `Rank 18 / 19 / 20` 当 active Scout 主线：应停止。
- 继续把 `Rank 17` 当成还缺更多近义 wiring 的 P2：应停止，它已经升到 P3。
- 把 `Rank 17` 的 ETH+SOL 窄范围升格误读成“全 scope 都过关”或“已经接近 live” ：应停止。
- 在 `Rank 2` 没有真实 append/review need 时继续默认补它：也应停止。

## Desk verdict

- **Paper Seat：`EMA baseline family`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前 paper / repo candidates 的 P 分级如下：**
  - `Rank 2 combo_all` → **`P3`**（`narrow paper pilot approved`）
  - `Rank 17 pullback recovery confirmation` → **`P3`**（`narrow paper pilot approved（ETH+SOL only）`）
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20` → **`P0`**（`park / evidence pool`）
  - `P1` 当前空缺
  - `P2` 当前空缺
  - `P4` 当前空缺

## 接下来优先级 Top 1~3

1. **默认切回新的 `paper / repo based 5m / 15m crypto` fresh intake / clean replication**
   - 原因：当前 `P3` 候选（`Rank 17 / Rank 2`）都没有新的真实 `append/review need`；
   - `P2` 当前为空；
   - `P1` 当前也为空；
   - 因此按“先硬门槛、再分级、再限预算”的新口径，当前最有边际价值的动作就是开新的 fresh intake。

2. **若 `Rank 17` 出现真实 `append/review need`，优先补它的 P3 最小 paper 接线**
   - 只允许做：
     - `paper ledger / monitoring / refresh / review` 最小接线；或
     - 一个真正会改变 paper verdict 的最小检查。
   - 不允许回到 admission wording / 近义 wiring。

3. **`Rank 2` 只在出现真实 `append/review need` 或 verdict-changing check 时再继续认领**
   - 它仍然是 P3；
   - 但当前默认回补优先级低于 fresh intake，也低于 `Rank 17` 的新 P3 接线 need。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-17_0343_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不再额外改 `docs/TODO.md` 的 desk 口径**：当前顶板已经由最新 bot3 产物完成关键同步：
  - `P0~P4` 分级规则已写入
  - `Rank 17 -> P3 narrow paper pilot approved（ETH+SOL only）`
  - `Rank 18 / 19 / 20 -> P0 park`
  - 当前窗口默认顺序已切成：fresh intake first；现有 P3 只在真实 need 时回补
- **不改 cron 频率**：当前 `bot2` / `bot3` / `bot7` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. `Rank 17` 虽已升到 P3，但这是 **ETH+SOL-only** 的窄范围 pilot，不是全 scope 胜利；`BTC` 继续是 red-watch excluded leg。
2. 当前 `P2` 与 `P1` 都空缺，说明桌面两极分化：要么直接被打到 P0，要么勉强活到 P3；这既是诚实，也提示 fresh intake 质量仍需继续提高。
3. `Paper Seat` 当前虽是 `waiting_not_due`，但 A 股下一次 close 已在几小时内；若 close 后未 append，需要再次临时切回 `Run 1`。

## 本轮一句话结论（给 Jerry）

**这轮没有新的换席，但 desk 的 Scout 分级已经正式从“阶段名”切到 `P0~P4` 口径，而且 `Rank 17` 已从 P2 进一步升到 `P3 / narrow paper pilot（ETH+SOL only）`；`Rank 18 / 19 / 20` 则都回到 `P0`。所以当前最诚实的排班已变成：默认继续 fresh intake，只有当 `Rank 17 / Rank 2` 出现真实 append/review need 或 genuinely verdict-changing check 时，才回补现有 P3。**
