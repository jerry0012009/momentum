# 2026-03-19 06:04 UTC bot2 strategy review

## 本轮先检查了什么
- repo 状态：`jerry/momentum` 工作区仍有大量既存脏文件；本轮只做 desk-board 最小必要写回、strategy review 记录、首页 index 刷新与邮件，不混改无关文件。
- 最近 optimization logs：
  - `2026-03-19_0431_rank78-time-stability-scope-promotion.md`
  - `2026-03-19_0513_rank79-clean-replication-park.md`
  - `2026-03-19_0547_rank80-clean-replication-keep-p1.md`
- 最近 strategy review：
  - `2026-03-19_0504_strategy-review.md`
  - `2026-03-19_0400_strategy-review.md`
  - `2026-03-19_0320_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m` enabled / 本轮正在运行
  - `bot3-momentum-auto-opt-13m` enabled
  - `momentum-narrow-paper-lanes-20m` enabled
  - `bot7-quant-digest-30m` enabled
  - `bot6-park-reframe-2h` enabled
  - 本轮不需要改 cron
- `Paper Seat` guardrail：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`，当前是真 `waiting_not_due`。
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T05:36:12Z` 显示 `new_closed_trades_appended=0`，当前没有新的 narrow-paper status-changing event 需要抢默认主资源。

## 这轮为什么要重排 Scout
上一轮 bot2 review（`05:04 UTC`）时，默认主资源还在 `Rank 79`。但最新 bot3 证据已把两条线进一步压清：
- `Rank 79 / one-regime-per-session overlay` 已在 `05:13 UTC` 给出 **`park / evidence pool`**；
- `Rank 80 / first-30m impulse quality gate` 已在 `05:47 UTC` 做完那唯一手最小 clean replication，结果是 **`keep_P1 / evidence_pool`**，而不是直接升到 `P2`。

按当前 desk 纪律：
- `P1` 候选做完那 1 次便宜诚实检查后，默认应更偏向 **`升格 / park / 切新 rank`**；
- 因此 `Rank 80` 当前虽然不该被判死刑，但也**不该继续占默认 Scout 主资源位**；
- 更诚实的动作是：把 bot3 从 `Rank 80` 切去新的 fresh source，而不是继续在同一条线上补近义说明或补不改变级别的检查。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 这不是 desk 空闲，而是合法 market-clock block；最近 due 仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  1. `Rank 80` 刚做完最小 clean replication，仍只到 **`keep_P1 / evidence_pool`**；
  2. `Rank 78` 虽已升到 **`P3 narrow paper pilot`**，但 scope 已明确收窄为 **`EMA-only suppression overlay`**，不是默认 live challenger；
  3. breakout 线继续保持已 bench，不为了“桌上必须有 live challenger”而硬升格旧线。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源位：**
  - `RS+/RS- asymmetry gate`（fresh source intake next）
- **当前紧邻后备：**
  - `ETF lead regime gate`
  - `Fib trend-strength admission layer`
  - `其他 fresh paper/repo based 5m / 15m crypto source`
- **不再占默认主资源、但保留在证据池的候选：**
  - `Rank 80 / first-30m impulse quality gate`（`keep_P1 / evidence_pool`）
- **明确不应重新抢 seat 的旧线：**
  - `Rank 79 / 77 / 76 / 75 / 74 / 73 / 72`（均已 `park / evidence pool`）
  - `Rank 78 / 17 / 2 / 29 / 32b`（均属 `P3` 托管位，不是新的 Scout seat）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`RS+/RS- asymmetry gate = P0`**（`source intake next`）
- **`ETF lead regime gate = P0`**（`fresh intake pool`）
- **`Fib trend-strength admission layer = P0`**（`fresh intake pool`）
- **`Rank 80 / first-30m impulse quality gate = P1`**（`cheap honest check 已用 / keep_P1 / evidence_pool，不再占默认主资源`）
- **`Rank 78 / adaptive no-trade band = P3`**（`narrow paper pilot approved / EMA-only suppression overlay`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency managed lanes`）
- **`Rank 79 / 77 / 76 / 75 / 74 / 73 / 72 = P0`**（`park / evidence pool`）
- **`P2` 当前为空**
- **`P4` 当前为空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **`Run 1 = EMA due-check only`**
   - 继续盯 `A股 07:00 UTC`；若仍 `waiting_not_due`，不得空转。
2. **`Run 2 = RS+/RS- asymmetry gate source intake`**
   - 只做 `paper/repo based 5m / 15m crypto` fresh source intake 与两条轻量诚实守门。
3. **`Run 3 = ETF lead regime gate > Fib trend-strength admission layer > 其他 fresh source`**
   - 只有 fresh source 这一层也 exhausted，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`；
   - `P3 continuity` 继续只算低频 sidecar，不得默认抢占 Scout 主资源。

## Active Scout 边际价值比较（这轮显式重排）
1. **`RS+/RS- asymmetry gate`**
   - 当前第一，不是因为它证据最厚，而是因为 `Rank 80` 已经用掉了那 1 次便宜诚实检查却仍未升到 `P2`；此时更诚实的是切回新的 fresh source，而不是继续磨同一条线。
2. **`ETF lead regime gate`**
   - 仍是 paper/repo based 的 `15m crypto` fresh source；比重新打开 `P3 continuity` 或回退 tiny-live 更符合当前 desk 顺序。
3. **`Fib trend-strength admission layer`**
   - 仍有价值，但更偏单线 admission layer，当前边际价值低于先比较 `RS+/RS-` 与 `ETF lead` 两条更共享的 fresh gate。
4. **`Rank 80 / first-30m impulse quality gate`**
   - 当前只保留为 `P1 evidence_pool`；默认不继续占主资源。
5. **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`**
   - 继续只算 `P3` 托管位，不得被误写成新的 seat。

## 对 TODO 顶板的动作
- **本轮已做最小必要写回。**
- 在 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 新增了 `2026-03-19 06:04 UTC（bot2 desk review）` 补充，明确：
  - `Paper Seat = EMA / running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - `Scout Seat` 默认主资源位已从 `Rank 80` 切到 `RS+/RS- asymmetry gate`
  - `Rank 80` 只保留为 `P1 evidence_pool`，不再继续抢默认主资源
- 本轮不改 cron，不改其他 brief/prompt。

## 结论
- **Paper Seat：EMA，keep**
- **Live Seat：继续暂空**
- **Scout Seat：切到 fresh source，当前先做 `RS+/RS- asymmetry gate`**
- **P2：空；P4：空**
- **Rank 80：保留为 `P1 keep / evidence_pool`，但默认切资源，不再继续磨同一条线**
