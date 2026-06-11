# 2026-03-19 04:00 UTC bot2 strategy review

## 本轮先检查了什么
- repo 状态：`git status --short --branch` 显示 `jerry/momentum` 仍有大量既存脏文件，包含 `docs/TODO.md`、多份 reports/artifacts/site 页面与若干 research index；本轮只做 desk-board 最小必要写回，不混提无关脏改。
- 最近 optimization logs：
  - `2026-03-19_0315_rank77-alt-btc-rs-intake.md`
  - `2026-03-19_0334_rank77-breadth-clean-replication.md`
  - `2026-03-19_0350_rank78-band-intake.md`
- 最近 strategy review：
  - `2026-03-19_0320_strategy-review.md`
  - `2026-03-19_0226_strategy-review.md`
- 当前 cron：
  - `bot2-strategy-review-40m`：本轮正在运行
  - `bot3-momentum-auto-opt-13m`：enabled，最近一次 `ok`
  - `momentum-narrow-paper-lanes-20m`：enabled，最近一次 `ok`
  - `bot7-quant-digest-30m`：enabled，最近一次 `ok`
  - 本轮不需要改 cron
- `Paper Seat` 关键状态：`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 仍显示全 desk 无 `due-now / overdue` lane；最近 due 点仍是 `A股三条 lane -> 2026-03-19 07:00 UTC`。
- `P3 narrow paper` 托管状态：`reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T03:56:01Z` 已出现 `new_closed_trades_appended=1`；对应状态表/closed trades 显示 `Rank 17` 刚发生一次真实 `closed-trade append + open-position refresh`。

## Desk verdict（本轮必须回答的 5 件事）

### 1. 谁坐 `Paper Seat`？
- **仍是 `EMA / PSAR raw alpha focus`**。
- 当前状态仍是 **`running paper / waiting_not_due`**，不是执行卡死；最近 due 点还没到，因此这轮不该把主资源重新拉回 P3 continuity。

### 2. `Live Seat` 应继续暂空，还是已有候选值得升格？
- **继续暂空。**
- 原因：当前唯一 active scout 候选 `Rank 78` 还只到 **`P1 / guard-passed`**，尚未完成最小 clean replication，更没到 `Light Stability Pack`；按 desk 纪律，未过这两层前不应抢 `Live Seat`。
- breakout 线继续视为已 bench / 证据池，不因为“桌上需要一个 live challenger”而硬塞回席位。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- 当前 queue-facing 主资源位：
  - **`Rank 78 / adaptive no-trade band / EMA cost survival`**
- 仍在后备队列、但不占当前主资源的 Scout 方向：
  - `one-regime-per-session overlay`
  - `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 里的其他 fresh paper/repo source
- 明确不应重开成 active scout 的旧线：
  - `Rank 77 / alt-vs-BTC RS breadth shared gate`（已 clean replication 后 park）
  - `Rank 76 / intraday clock polarity + event blackout gate`（park）
  - `Rank 75 / GCR exhaustion veto`（park）
  - `Rank 72 / 73 / 74`（park）

### 4. 这些候选分别在 `P0 / P1 / P2 / P3 / P4` 哪一档？
- **`Rank 78 = P1`**（`source intake + 两条轻量诚实守门已过 / minimal clean replication next`）
- **`one-regime-per-session overlay = P0`**（`evidence / backlog`，不是当前默认主资源位）
- **`RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 fresh source = P0`**（`source intake pool`）
- **`Rank 77 / 76 / 75 / 74 / 73 / 72 = P0`**（`park / evidence pool`）
- **`Rank 17 / 2 / 29 / 32b = P3`**（`narrow paper continuity / low-frequency managed lanes`）
  - 其中 **`Rank 17`** 本轮出现 `closed-trade append + open-position refresh`，是**真实 status-changing event**，但仍属 P3 托管位，不是新 scout seat。
- **`P2` 仍空**
- **`P4` 仍空**

### 5. 接下来 3 个 bot3 runs 应怎么排？
1. **`Run 1 = EMA due-check only`**
   - 最近 due 点仍是 `A股 07:00 UTC`；若仍 `waiting_not_due`，不得空转。
2. **`Run 2 = Rank 78 minimal clean replication`**
   - 固定比较 `raw / fixed-band / adaptive-band`，对 `BTC/ETH/SOL 15m` 统一 `signal 当根及之前数据 + next-bar open + no-overlap`。
3. **`Run 3 = 若 Rank 78 给出 hard verdict，则继续按 Scout Seat 回到 fresh queue`**
   - 顺序：`one-regime-per-session overlay > RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source > Rank 35b > Rank 16b > tiny-live plumbing`
   - `Rank 17 @ 03:56 UTC` 的 P3 status event 目前**只保留为低频例外 sidecar**：只有后续 fresh source 这一层也 exhausted，或它出现真实异常待写回，才动用一次 `P3 continuity` 例外，不抢默认 `Run 3`。

## 为什么本轮不是把 `Rank 17` 顶上去
- `manual_narrow_paper_last_run_summary.json` 的确给出了真实 status-changing event；这意味着 **P3 continuity 现在“可以做”**，不是“必须继续等”。
- 但当前 desk 仍处于 `EMA waiting_not_due`，而且 `Rank 78` 是唯一还没用掉那次便宜诚实检查的 active `P1`。按权威顺序，默认仍应是：
  - `Scout Seat`
  - `tiny-live plumbing`
  - `其他维护 / P3 continuity`
- 所以更诚实的读法是：**承认 Rank 17 的事件存在，但不让它把默认主资源从 Scout 拖回 continuity。**

## Active Scout 的边际价值比较
1. **`Rank 78 / adaptive no-trade band / EMA cost survival`**
   - 直接贴 `Paper Seat = EMA` 主线
   - 已 guard-passed
   - 现在最缺的是唯一那次 cheap honest check：minimal clean replication
2. **`one-regime-per-session overlay`**
   - 仍更像 allocation / overlay backlog
   - 没有 `Rank 78` 这么直接贴当前 `EMA` 主线
3. **`RECENT_PAPER_SEEDS / quant_digests / validated shortlist 其他 source`**
   - 作为下一跳 fresh queue 保留
4. **`Rank 17` 的 P3 sidecar**
   - 有 status event，但不是 scout；默认只低频处理

## 本轮最小必要动作
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 新增 `2026-03-19 04:00 UTC` 补充，明确 `Paper Seat / Live Seat / Scout Seat` 判断不变
  - 明确 `Rank 17 @ 03:56 UTC` 只是 `P3 continuity` sidecar，不改默认 seat
  - 收紧 `Next 3 bot3 runs`
- 本轮未改 cron、未改其他 prompt/brief。

## 结论
- **Paper Seat：EMA，keep**
- **Live Seat：继续暂空**
- **Scout Seat：Rank 78 继续拿默认主资源**
- **P2/P4：仍空**
- **Rank 17 的新 append/open-position 事件：承认其为真实 P3 status event，但默认不抢 Run 2 / Run 3**
