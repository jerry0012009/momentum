# 2026-03-19 05:04 UTC bot2 strategy review

## 本轮先检查了什么
- repo 状态：`jerry/momentum` 工作区仍有大量既存脏文件；本轮只做巡检、策略 review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs：
  - `2026-03-19_0410_rank78-band-clean-replication.md`
  - `2026-03-19_0431_rank78-time-stability-scope-promotion.md`
  - `2026-03-19_0442_rank79_one-regime-session-intake.md`
- 最近 strategy review：
  - `2026-03-19_0400_strategy-review.md`
  - `2026-03-19_0320_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m` enabled / 本轮正在运行
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane；最近 due 点继续是 `A股三条 lane -> 2026-03-19 07:00 UTC`，当前是真 `waiting_not_due`。
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T04:33:36Z` 显示 `new_closed_trades_appended=0`，说明当前没有新的 narrow-paper append 异常要抢默认主资源。

## 对 04:42 顶板的核对结论
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 的**当前权威读法仍是 04:42 UTC 那版**：
  - `Rank 78` 已从 Scout 主资源位退出，收口为 **`P3 narrow paper pilot approved（EMA-only suppression overlay）`**；
  - `Rank 79 / one-regime-per-session overlay` 已完成 `source intake + 两条轻量诚实守门`，当前是 **`P1 / guard-passed`**；
  - `Run 1 -> Run 3` 顺序仍写成：`EMA due-check only -> Rank 79 minimal clean replication -> 再回 fresh source`。
- 本轮未看到新的 bot3 证据推翻这套排法，因此**不需要再做新的 TODO 顶板写回**；继续沿用 04:42 的 reader-facing judgment 更诚实。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 最近 due 点依然是 `A股 07:00 UTC`；这说明 `Paper Seat` 现在是被 market clock 合法阻塞，不是 desk 空闲。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. 当前新的 Scout 主候选 `Rank 79` 还只到 **`P1 / guard-passed`**，尚未完成最小 clean replication；
  2. `Rank 78` 虽已升到 **`P3 narrow paper pilot approved`**，但它的 scope 已明确收窄为 **`EMA-only suppression overlay`**，这不是“默认 live challenger”；
  3. breakout 线继续维持已 bench / 不再默认强调。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 queue-facing 主资源位只有 1 条：**
  - **`Rank 79 / one-regime-per-session shared allocation overlay`**
- 当前只作为后备 / fresh queue、但不占本轮默认主资源的候选：
  - `first-30m impulse quality gate`
  - `RS+/RS- asymmetry gate`
  - `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 里的其他 fresh paper / repo source
- 明确不应重新抢默认 Scout seat 的旧线：
  - `Rank 78`（已转入 `P3 narrow paper pilot`，不再是默认 Scout）
  - `Rank 77 / 76 / 75 / 74 / 73 / 72`（均已 `park / evidence pool`）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 79 / one-regime-per-session overlay = P1`**（`source intake + 两条轻量诚实守门已过 / minimal clean replication next`）
- **`first-30m impulse quality gate = P0`**（`fresh source intake pool`）
- **`RS+/RS- asymmetry gate = P0`**（`fresh source intake pool`）
- **`RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source = P0`**（`source intake pool`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot approved / EMA-only suppression overlay`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency managed lanes`）
- **`Rank 77 / 76 / 75 / 74 / 73 / 72 = P0`**（`park / evidence pool`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 继续盯 `A股 07:00 UTC`；若仍 `waiting_not_due`，不得空转。
2. **`Run 2 = Rank 79 minimal clean replication`**
   - 固定比较 `baseline / continuation-only / retest-only / one-regime-per-session`，对 `BTC/ETH/SOL 15m` 统一 `signal 当根及之前数据 + next-bar open + no-overlap`，并直接给出 `keep_P1 / promote_to_P2 / park`。
3. **`Run 3 = 仅在 Rank 79 这次 clean replication 已完成后，回到 fresh source queue`**
   - 顺序保持：`first-30m impulse quality gate > RS+/RS- asymmetry gate > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source > Rank 35b > Rank 16b > tiny-live plumbing`
   - `P3 continuity` 只保留为低频 sidecar：只有 fresh source 真的 exhausted，或出现新的 `status-changing event`，才允许动用。

## Active Scout 边际价值比较（本轮显式重排）
1. **`Rank 79 / one-regime-per-session overlay`**
   - 已经 `guard-passed`
   - 直接回答 continuation 与 retest lane 是否不该在同一段 session 里同时抢预算
   - 现在最缺的是那 1 次真正会改变 verdict 的最小 clean replication
2. **`first-30m impulse quality gate`**
   - 仍有价值，但更像 continuation 放行闸门
   - 当前边际价值低于先回答“同场 regime allocation”
3. **`RS+/RS- asymmetry gate`**
   - 更像方向性 veto / sizing 扩展层
   - 当前优先级低于 `Rank 79`
4. **`Rank 78 / EMA-only suppression overlay`**
   - 已进入 `P3 narrow paper pilot`
   - 当前不该继续占默认 Scout 主资源，也不应被误读成新的 live challenger

## 为什么这轮不去碰 `Rank 78` 或 `Rank 17`
- `Rank 78` 已在 `04:31 UTC` 给出 scope 收口后的最终 promotion verdict，继续围着它磨只会增加 continuity 噪音，不会减少真实 gate。
- `Rank 17` 虽在更早一轮出现过真实 append/open-position event，但最新 narrow-paper summary `@ 04:33:36Z` 已回到 `new_closed_trades_appended=0`，说明当前没有新的必须插队的 continuity 异常。
- 因此在 `EMA = waiting_not_due` 的前提下，当前最诚实的顺序仍是：
  - `Scout Seat`
  - `tiny-live plumbing`
  - `其他维护 / P3 continuity`

## 对 TODO 顶板的动作
- **本轮不改 `docs/TODO.md`。**
- 原因：`04:42 UTC` 的 `TRADING DESK BOARD / Next 3 bot3 runs` 已经准确反映当前最新 reader-facing judgment；本轮没有新证据需要翻盘或重排。

## 结论
- **Paper Seat：EMA，keep**
- **Live Seat：继续暂空**
- **Scout Seat：Rank 79 继续拿默认主资源**
- **P2：空；P4：空**
- **Rank 78：已转入 `P3 narrow paper pilot（EMA-only suppression overlay）`，不再占默认 Scout 主资源**
- **本轮 verdict：纯巡检，无需改板；继续执行 04:42 版 `Next 3`**
