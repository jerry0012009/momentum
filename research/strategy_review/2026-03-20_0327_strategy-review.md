# Strategy Review — 2026-03-20 03:27 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；首要动作仍是维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛复述研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1651`
- 最近 optimization logs：
  - `2026-03-20 03:12 UTC` `Rank 107 / MTF CHOP charged-up count` clean replication -> `park`
  - `2026-03-20 02:54 UTC` `Rank 107 / MTF CHOP charged-up count` source intake
  - `2026-03-20 02:31 UTC` `Rank 106 / elephant candle corridor` clean replication -> `park`
  - `2026-03-20 02:20 UTC` `Rank 105 / body-defined zone re-entry` clean replication -> `park`
- 最近 strategy review：
  - 最新仍是 `2026-03-20 02:33 UTC`
- 当前 cron（只记 desk 相关状态）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot7-quant-digest-30m`：运行中；最新已产出 `2026-03-20 03:23 UTC / HTF premium-discount long-bias context`
  - `bot6-park-reframe-2h`：上一轮 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：上一轮 `ok`
- Paper Seat 实时状态：
  - `ema_paper_trading_due_guardrail_snapshot.csv` 当前全 desk 仍无 `due-now / overdue`
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`
- P3 sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T03:00:29Z`
  - `new_closed_trades_appended=0`
  - `manual_narrow_paper_status.csv` 仍显示 `Rank 17` 的 `ETH/SOL` 两条 hosted paper position open；但当前没有新的 status-changing event
- 最近新增 quant digests：
  - `2026-03-20 03:23 UTC` `HTF premium/discount long-bias context`
  - `2026-03-20 02:49 UTC` `F&G extremity risk overlay`
  - `2026-03-19 23:29 UTC` `prebreak higher-low pressure ladder context gate`

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：这轮依然是真正的 market-clock 阻塞，不是 EMA 线还有 bot3 没做完的伪 continuation。最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`，所以 `EMA` 继续占位，但不能让 bot3 围着它空转。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- `Rank 105 / 106 / 107` 都已经在 clean replication 后如实压回 `park / evidence pool`；
- 当前最靠前的 fresh Scout 候选 `prebreak higher-low pressure ladder` 与刚新增的 `HTF premium/discount long-bias context` 都还停在 `source intake` 之前；
- 这两条都没有进入 `clean replication`，更没有过 `Light Stability Pack`，因此不应抢跑成 live challenger；
- `Rank 2 / 17 / 29 / 32b` 继续只是 `P3 hosted lanes / sidecar`，不是新的 live 名字。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前更诚实的 active Scout 顺序是：

1. **`prebreak higher-low pressure ladder context gate`**（repo）
2. **`HTF premium/discount long-bias context gate`**（repo）
3. **`fresh paper / repo intake reserve`**（来自 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）

补充判断：
- `prebreak higher-low pressure ladder` 当前边际价值最高，因为它仍覆盖 `breakout-short / Fib / EMA` 三条线共同的“回踩前结构背景”问题，而且下一手刚好是最便宜的 `source intake + 两条轻量诚实守门`；
- `HTF premium/discount` 这轮新 digest 已把角色说清：它更像 **`Fib retest_hold / EMA continuation` 的 long-side asymmetric context**，不是 `breakout-short` 的 shared gate，所以当前更适合作为紧邻 reserve，而不是立刻抢主资源位；
- `fresh intake reserve` 仍必须保留，因为 `Rank 105 / 106 / 107` 连续三条都已收口成 `park`，若前两条 backlog 也 exhausted，就该先切新 source，而不是回头磨旧 `P1` 或误把 `P3 continuity` 当主线。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`prebreak higher-low pressure ladder context gate`** → **`P0`**（`fresh repo context candidate / source intake next`）
- **`HTF premium/discount long-bias context gate`** → **`P0`**（`fresh repo reserve / long-side context only / source intake reserve`）
- **`fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`** → **`P0`**（`fallback fresh intake pool`）

#### 旧候选层级
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

补充：本轮 `manual_narrow_paper_last_run_summary.json` 已回到 `new_closed_trades_appended=0`，所以 `Rank 17` 现在连“状态改变的 P3 事件”都不算，只能继续放在低频 fallback。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 prebreak higher-low pressure ladder context gate 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 prebreak higher-low pressure ladder context gate guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 HTF premium/discount long-bias context gate 的 source intake；若这条 fresh repo reserve 也 exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`**

## 2. 为什么这轮把 `HTF premium/discount` 插进 reserve，但没让它抢过 `prebreak`
### `prebreak higher-low pressure ladder` 继续排第一
- 它仍直接服务三条主线共同缺的“回踩前结构背景 + retest 质量交互”问题；
- digest 已经明确：它不该当硬门，而该配合 `small-body retest`；这正好适合 bot3 下一轮做最便宜的 queue-facing intake；
- 它不像旧 `P1` 那样已经多轮预算磨损，也不像 `P3 sidecar` 那样只是 continuity 托管。

### `HTF premium/discount` 升到第二
- 它是新鲜 repo、口径清楚、实验切口便宜；
- 对 `Fib retest_hold / EMA continuation` 的 long-side context 价值比 generic fresh intake 更明确；
- 但它已经清楚暴露出 **非对称性**：对 `breakout-short` 不适合当 shared gate，所以当前不该越过 `prebreak` 抢主资源位。

### 为什么不是 `F&G extremity risk overlay`
- 这条有价值，但当前更像 **日级外部数据 overlay**，不是默认优先的 `paper / repo based 5m/15m crypto` fast-lane；
- 按当前 desk 规则，它更适合继续留在 fresh reserve 池里，而不是挤占这轮默认 Scout 主位。

## 3. 本轮对 `TODO` 顶板的最小必要更新
### 已做
- 在 `docs/TODO.md` 顶部 `TRADING DESK BOARD -> Next 3 bot3 runs` 新增 `2026-03-20 03:27 UTC，bot2 desk review`：
  - 保持 `Paper Seat = EMA / waiting_not_due`
  - 保持 `Live Seat = 暂空`
  - 保持 `Scout Seat = prebreak higher-low pressure ladder context gate`
  - 把 active Scout reserve 收紧为：`prebreak higher-low > HTF premium/discount > fresh intake reserve > 旧 P1 evidence_pool > Rank 17 low-frequency health-check fallback > tiny-live plumbing`
  - 把 `Run 3` 的 failover 更新成：`HTF premium/discount intake -> fresh paper/repo re-intake -> Rank 17 fallback -> tiny-live plumbing`

### 本轮不做
- 不改 cron prompt：当前通过顶板更新已足够传导给 bot3；
- 不把 `Rank 17` 的 open paper position 误写成新的 seat；
- 不把 `HTF premium/discount` 过早吹成 `P1 / P2` 或 live challenger。

## 4. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：当前切到 `prebreak higher-low pressure ladder context gate`
- **Scout reserve**：更新为 `HTF premium/discount long-bias context > fresh paper/repo intake reserve`
- **P2 / P4 仍空**
- **Rank 17` 当前只算 `P3 low-frequency fallback`，本轮没有新的 status-changing event**
- **bot3 接下来默认：EMA due-check -> prebreak intake -> prebreak clean replication / failover 到 HTF premium-discount intake，再到 fresh re-intake**
