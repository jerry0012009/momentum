# Strategy Review — 2026-03-20 05:11 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；首要职责仍是维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛回顾研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1673`
- 重新实跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`EMA = waiting_not_due`**
  - 当前没有 `due-now / overdue` lane
  - 最近 due 仍是 **A股三条 lane -> 2026-03-20 07:00 UTC`（约 1.8h）**
- 最近 optimization logs：
  - `2026-03-20 04:48 UTC` `Rank 109 / HTF premium-discount long-bias context gate` clean replication -> `park`
  - `2026-03-20 04:18 UTC` `Rank 109 / HTF premium-discount long-bias context gate` source intake
  - `2026-03-20 03:58 UTC` `Rank 108 / prebreak higher-low pressure ladder` clean replication -> `park`
  - `2026-03-20 03:34 UTC` `Rank 108 / prebreak higher-low pressure ladder` source intake
- 最近 strategy reviews：
  - 最新仍是 `2026-03-20 04:10 UTC`
  - 其次是 `03:27 UTC`、`02:33 UTC`
- 当前 cron（只记 desk 相关状态）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot7-quant-digest-30m`：运行中；刚新增 `2026-03-20 05:11 UTC / basis dislocation short veto` digest
  - `bot6-park-reframe-2h`：仍是 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：仍是 `error`（`rg: command not found`）
- `P3` sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T04:39:11Z`
  - `new_closed_trades_appended=0`
  - `Rank 17` 当前仍有 `ETH/SOL` open hosted paper position，但这轮没有新的 status-changing event

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：这轮是真的被 market clock 卡住，不是 EMA 线还有 bot3 没做完的伪 continuity。离最近 due 还有约 `1.8h`，所以 `EMA` 继续占位，但 bot3 不能围着它空转。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- 最新 queue-facing 候选 `Rank 109` 已在 `04:48 UTC` 如实压回 `park / evidence pool`；
- 当前排在最前面的 `Rank 110 / PSAR pre-flip SAR dot reclaim gate` 仍只停在 **`P0 / source intake next`**，还没进入 `clean replication`，更没过 `Light Stability Pack`；
- `Rank 2 / 17 / 29 / 32b` 仍只是 **`P3 narrow paper continuity / hosted lanes / sidecar`**，不是可抢跑的 live challenger；
- 这轮没有出现任何足以把某条线升成 `tiny-live review candidate` 的 status-changing 证据。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前更诚实的 queue-facing 读法是：

1. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**（repo）
2. **fresh paper / repo intake reserve**（`RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
   - 当前最新可见新增里，`05:11 UTC / basis dislocation short veto` 只算 **fresh reserve evidence**，还没有高到能越过 `Rank 110` 直接占主资源位
3. **旧 `P1 evidence_pool`**（`Rank 93 / 90 / 91 / 82 / 80 / 81`）
   - 只保留“最多 1 次便宜诚实检查”的预算，不再默认续命

补充：
- `Rank 109` 已经在 `04:48 UTC` 完成那唯一一手会改变 verdict 的 clean replication，并被压回 `park`，所以它**不再**属于 active Scout 主链；
- `P3` 的 `Rank 2 / 17 / 29 / 32b` 仍只算 hosted lanes / sidecar，不是当前 `Scout Seat` 的默认主资源位。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`** → **`P0`**（`fresh repo / source intake next`）
- **fresh paper / repo intake reserve** → **`P0`**（`fallback fresh intake pool`）
  - 其中 `basis dislocation short veto` 当前只算 reserve evidence，不是已认领 queue-facing rank
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 最多 1 次便宜诚实检查`）
- **`Rank 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班维持不变：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 110 / PSAR pre-flip SAR dot reclaim gate 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 Rank 110 guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`**

## 2. Active Scout 候选的边际价值比较（不是默认磨同一条 rank）
### 为什么还是 `Rank 110` 排第一
- `Rank 109` 已经在 `04:48 UTC` 明确收口成 `park`，因此当前最靠前、仍未被验证的 queue-facing fresh 候选自然切到 `Rank 110`；
- `Rank 110` 直接服务当前 `EMA / PSAR raw alpha focus`，而且下一手就是最便宜的 `source intake + 两条轻量诚实守门`；
- 它还没消耗掉那唯一一次“会真正改变 verdict 的最小检查”预算，所以当前边际价值最高。

### 为什么不是直接回旧 `P1`
- `Rank 93 / 90 / 91 / 82 / 80 / 81` 都属于 **预算已磨损的旧证据池**；
- 按当前 desk 规则，`P1` 最多只配 **1 次便宜诚实检查**，做完更偏向 `升格 / park / 切资源`，不应在 fresh queue 还没 exhausted 时抢回主资源位。

### 为什么这轮也不是 `P3 continuity`
- `manual_narrow_paper_last_run_summary.json @ 04:39:11Z` 仍是 `new_closed_trades_appended=0`；
- 当前没有新的 `receipt refs / closed-trade append / weekly-review row / 明显异常` 这类 status-changing event；
- 所以 `Rank 2 / 17 / 29 / 32b` 继续只应放在低频 hosted-lane 健康检查位，不应越过 `Scout Seat` 默认主链。

### 为什么 `basis dislocation` 还只是 reserve
- 它是刚新增的 digest，仍停在“新证据进入池子”的阶段；
- 当前 desk 对 `Scout Seat` 的默认要求仍是 **先把已排到前面的 paper/repo 5m/15m 候选做完最小诚实快筛**；
- 因此它目前只能算 `fresh intake reserve`，不能跳过 `Rank 110` 直接上位。

## 3. 对 `TRADING DESK BOARD` 的处理
### 本轮结论：**顶板不改，继续以 `2026-03-20 04:48 UTC` 版本为权威顺序。**
原因：
- 本轮新核对并没有改变席位判断：`Paper Seat = EMA / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 110`；
- `Rank 109` 的 `park` 结论、`Rank 110` 的上位、以及 `Next 3` 的 failover 顺序，都已在顶板 `04:48 UTC` 版本写清；
- 本轮新增信息里，`bot6` / `Rank32b live maintenance` 的 `rg` 报错属于相邻维护问题，不改变当前三席位判断；`basis dislocation` 则只增加了 reserve 证据，还没有改变主资源排班。

## 4. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：当前 authoritative 仍是 `Rank 110 / PSAR pre-flip SAR dot reclaim gate`
- **层级**：`Rank 110 = P0`；fresh intake reserve = `P0`；旧 evidence pool = `P1`；`Rank 2 / 17 / 29 / 32b = P3`
- **P2 / P4 仍空**
- **bot3 接下来默认仍是：EMA due-check -> Rank 110 intake -> Rank 110 clean replication / failover 到 fresh intake reserve -> 再到 Rank 17 低频 fallback**
