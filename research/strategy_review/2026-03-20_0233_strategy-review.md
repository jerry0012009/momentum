# Strategy Review — 2026-03-20 02:33 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；重点仍是维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛复述研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1638`
- 最近 optimization logs：
  - `2026-03-20 02:31 UTC` `Rank 106 / elephant candle corridor` clean replication -> `park`
  - `2026-03-20 02:28 UTC` `Rank 106 / elephant candle corridor` source intake
  - `2026-03-20 02:20 UTC` `Rank 105 / body-defined zone re-entry` clean replication -> `park`
  - `2026-03-20 02:02 UTC` `Rank 105 / body-defined zone re-entry` source intake
- 最近 strategy review：
  - 最新仍是 `2026-03-20 01:53 UTC`
- 当前 cron（只记 desk 相关）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot7-quant-digest-30m`：上一轮 `ok`
  - `bot6-park-reframe-2h`：上一轮 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：上一轮 `ok`
- Paper Seat 实时状态：
  - `ema_paper_trading_due_guardrail_snapshot.csv` 当前全 desk 仍无 `due-now / overdue`
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`
- P3 sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T02:25:51Z`
  - `new_closed_trades_appended=1`
  - `manual_narrow_paper_status.csv` 显示 `Rank 17` 当前 `ETH/SOL` 两条 hosted paper position 仍 open；这是 `P3 sidecar` 的 status-changing event，但不是新 seat

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：现在是真的被 market clock 卡住，不是 paper 线还有 bot3 没做完的续写动作。最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`，所以 `EMA` 继续占位，但不能让 bot3 围着它空转。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- `Rank 105 / body-defined zone re-entry` 已在 clean replication 后如实压回 `park / evidence pool`；
- `Rank 106 / elephant candle corridor` 也已在 clean replication 后压回 `park / evidence pool`；
- 当前最靠前的 fresh Scout 候选 `MTF CHOP` 还没走完 `source intake + 两条轻量诚实守门`，更没有进入 `Light Stability Pack`；
- `Rank 2 / 17 / 29 / 32b` 继续只是 `P3 hosted lanes / sidecar`，不是新的 live challenger；
- 当前不应为了“桌上必须有 live 名字”而重新抬已 bench 的 breakout 或把 hosted paper 偷渡成 live。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前最诚实的 active Scout 顺序是：

1. **`MTF CHOP charged-up count`**（repo）
2. **`prebreak higher-low pressure ladder context gate`**（repo）
3. **`fresh paper / repo intake reserve`**（来自 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 的 fallback 池）

补充判断：
- `MTF CHOP` 当前边际价值最高，因为它最接近一个会直接改变 desk judgment 的 **long-side veto / regime gate** 问题，而且已经有 repo + 代理快检支撑，下一手正好是 `source intake + 两条轻量诚实守门`；
- `prebreak higher-low pressure ladder` 仍保留，但它更像上下文特征，不像独立 admission key，所以只该当紧邻 reserve；
- fresh intake fallback 池需要保留在桌上，因为当前 `Rank 105 / 106` 都已收口为 `park`，若 `MTF CHOP` 和 `prebreak ladder` 都 exhausted，就该先重新认领 1 条新的 paper / repo source，而不是回头磨旧 `P1` 或把 `P3 continuity` 误当主资源位。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`MTF CHOP charged-up count`** → **`P1`**（`repo weak candidate / source intake + 两条轻量诚实守门 next`）
- **`prebreak higher-low pressure ladder context gate`** → **`P0`**（`repo context backlog / source intake reserve`）
- **`fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`** → **`P0`**（`fallback fresh intake pool`）

#### 旧候选层级
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

补充：`manual_narrow_paper_last_run_summary.json` 虽然在 `02:25:51Z` 出现了 `new_closed_trades_appended=1`，且 `Rank 17` 当前 `ETH/SOL` 两条 hosted paper position 仍 open，但这只说明 **P3 lane 在正常滚动**，不是 Scout 或 Live 新席位。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 MTF CHOP charged-up count 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 MTF CHOP charged-up count guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 prebreak higher-low pressure ladder context gate 的 source intake；若这条 fresh backlog 也 exhausted，则先从 RECENT_PAPER_SEEDS / quant_digests / validated shortlist 再认领 1 条 fresh paper-repo source；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`**

## 2. 为什么这轮不让 `Rank 17` 的 P3 事件抢过 `Scout Seat`
这轮确实出现了一个真实的 P3 status-changing event：
- `manual_narrow_paper_last_run_summary.json @ 2026-03-20T02:25:51Z`：`new_closed_trades_appended=1`
- `manual_narrow_paper_status.csv`：`Rank 17` 当前 `ETH/SOL` 两条 hosted paper position 仍 open

但当前更诚实的 desk 读法仍然是：
- **它值得保留为 low-frequency health check fallback**；
- **它不值得在 fresh Scout 链未 exhausted 前抢过 `MTF CHOP` 或 `prebreak ladder`**；
- **它更不该被误写成新的 `Live Seat` 或新的主资源位**。

原因很简单：
- dedicated cron `momentum-narrow-paper-lanes-20m` 已在正常续跑；
- 当前并没有看到明显异常 open-position / red-watch / due-now paper 漏跑；
- 这个事件改变的是 hosted paper 的滚动状态，不是 Scout 侧的 admission gate。

## 3. 本轮对 `TODO` 顶板的最小必要更新
### 已做
- 在 `docs/TODO.md` 顶部 `TRADING DESK BOARD -> Next 3 bot3 runs` 新增 `2026-03-20 02:33 UTC，bot2 desk review`：
  - 明确写死 `Paper Seat = EMA / waiting_not_due`
  - 维持 `Live Seat = 暂空`
  - 维持 `Scout Seat = MTF CHOP charged-up count`
  - 把 active Scout tiering 收紧为：`MTF CHOP > prebreak higher-low > fresh intake reserve > 旧 P1 evidence_pool > P3 sidecar`
  - 把 `Run 3` 的 failover 补正为：`prebreak higher-low -> fresh paper/repo re-intake -> Rank 17 low-frequency health check fallback -> tiny-live plumbing`

### 本轮不做
- 不改 cron prompt：当前排班通过顶板更新已足够传导给 bot3；
- 不把 `Rank 17` 的 hosted paper 滚动误写成新 seat；
- 不把 `MTF CHOP` 直接吹成 `P2` 或 live challenger。

## 4. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：当前切到 `MTF CHOP charged-up count`
- **当前 active Scout**：`MTF CHOP > prebreak higher-low > fresh intake reserve`
- **P2 / P4 仍空**
- **Rank 17` 的 02:25 append/open-position 事件只算 `P3 sidecar fallback`，不改 seat**
- **bot3 接下来默认：EMA due-check -> MTF CHOP intake -> MTF CHOP clean replication / failover 到 prebreak，再到 fresh re-intake**
