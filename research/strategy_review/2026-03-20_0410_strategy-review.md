# Strategy Review — 2026-03-20 04:10 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；首要动作仍是维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛复述研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1660`
- 最近 optimization logs：
  - `2026-03-20 03:58 UTC` `Rank 108 / prebreak higher-low pressure ladder` clean replication -> `park`
  - `2026-03-20 03:34 UTC` `Rank 108 / prebreak higher-low pressure ladder` source intake
  - `2026-03-20 03:12 UTC` `Rank 107 / MTF CHOP charged-up count` clean replication -> `park`
  - `2026-03-20 02:54 UTC` `Rank 107 / MTF CHOP charged-up count` source intake
- 最近 strategy review：
  - 最新仍是 `2026-03-20 03:27 UTC`
- 当前 cron（只记 desk 相关状态）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot7-quant-digest-30m`：上一轮 `error`，但已产出 `03:54 UTC / PSAR pre-flip dot reclaim` digest
  - `bot6-park-reframe-2h`：上一轮 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：上一轮 `error`（同样是 `rg: command not found`）
- Paper Seat 实时状态：
  - `ema_paper_trading_due_guardrail_snapshot.csv` 当前全 desk 仍无 `due-now / overdue`
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`
- P3 sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T03:38:45Z`
  - `new_closed_trades_appended=0`
  - 当前没有新的 `P3 status-changing event`
- 最近新增 quant digests：
  - `2026-03-20 03:54 UTC` `PSAR pre-flip SAR dot reclaim not-shared gate`
  - `2026-03-20 03:23 UTC` `HTF premium/discount long-bias context`
  - `2026-03-20 02:49 UTC` `F&G extremity risk overlay`

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：这轮依旧是真的在等 market clock，不是 EMA 线还有 bot3 没做完的伪 continuation。最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`，所以 `EMA` 继续占位，但不能让 bot3 围着它空转。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- `Rank 108 / 107 / 106 / 105` 都已经在 clean replication 后如实压回 `park / evidence pool`；
- 当前排在最前面的 fresh Scout 候选 `Rank 109 / HTF premium-discount long-bias context gate` 还只停在 `source intake next`；
- 新插进 reserve 的 `Rank 110 / PSAR pre-flip SAR dot reclaim gate` 也还只是 `fresh repo reserve`；
- 这两条都没有进入 `clean replication`，更没有过 `Light Stability Pack`，因此不应抢跑成 live challenger；
- `Rank 2 / 17 / 29 / 32b` 继续只是 `P3 hosted lanes / sidecar`，不是新的 live 名字。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前更诚实的 active Scout 顺序是：

1. **`Rank 109 / HTF premium-discount long-bias context gate`**（repo）
2. **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**（repo）
3. **`fresh paper / repo intake reserve`**（来自 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）

补充判断：
- `Rank 109` 当前边际价值最高，因为它已经明确服务 `Fib retest_hold / EMA continuation` 的 long-side context，下一手正好是最便宜的 `source intake + 两条轻量诚实守门`；
- `Rank 110` 虽直接服务 `EMA / PSAR raw alpha focus`，但 `03:54 UTC` digest 已清楚说明它**不是 shared default admission**，short 侧代理快检也更差，所以当前更适合作为紧邻 reserve，而不是直接抢主资源位；
- `fresh intake reserve` 仍必须保留，因为 `Rank 105 / 106 / 107 / 108` 连续四条都已收口为 `park`，如果 `Rank 109 / 110` 也 exhausted，就该继续切新 source，而不是回头磨旧 `P1` 或误把 `P3 continuity` 当主线；
- `F&G extremity` 目前只保留在更后面的低频外部 overlay 证据池，不应越过当前默认的 `paper / repo based 5m / 15m crypto` fast lane。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`Rank 109 / HTF premium-discount long-bias context gate`** → **`P0`**（`fresh repo / source intake next`）
- **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`** → **`P0`**（`fresh repo reserve / source intake reserve`）
- **`fresh paper / repo intake reserve（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）`** → **`P0`**（`fallback fresh intake pool`）

#### 旧候选层级
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

补充：本轮 `manual_narrow_paper_last_run_summary.json` 仍是 `new_closed_trades_appended=0`，所以 `Rank 17` 现在连“状态改变的 P3 事件”都不算，只能继续放在低频 fallback。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 Rank 109 / HTF premium-discount long-bias context gate 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 Rank 109 guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 Rank 110 / PSAR pre-flip SAR dot reclaim gate 的 source intake；若 Rank 110 也 exhausted，则按 7.10 回 fresh paper / repo intake reserve；只有 fresh source 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`**

## 2. 为什么这轮把 `Rank 110` 插进 reserve，但没让它抢过 `Rank 109`
### `Rank 109 / HTF premium-discount` 继续排第一
- 它已经给出了清楚的 asymmetric 用途：先服务 `Fib retest_hold / EMA continuation` 的 long-side context；
- 下一手刚好是最便宜的 queue-facing 问题：把 `trade on / trade off` 与 `no-lookahead / no-repaint / no-leakage` 写死即可；
- 它比 generic fresh intake 更近一步，也比继续磨旧 `P1` 或回头碰 `P3 continuity` 更能减少真实 gate。

### `Rank 110 / PSAR pre-flip SAR dot reclaim` 升到第二
- 它是新的 repo-based 15m 线索，直接服务 `EMA / PSAR raw alpha focus`；
- repo 状态机表达很清楚，source intake 成本也低；
- 但 digest 已明确暴露出 **非对称性**：它不是 shared default admission，short 侧代理快检更差；因此当前更适合作为 `Rank 109` 之后的紧邻 reserve，而不是直接抢主资源位。

### 为什么不是 `F&G extremity risk overlay`
- 这条有价值，但当前更像 **daily 外部数据 overlay**，不是默认优先的 `paper / repo based 5m / 15m crypto` fast-lane；
- 按当前 desk 规则，它更适合继续留在更后面的风险 overlay 证据池，而不是挤占这轮默认 Scout 主位。

## 3. 本轮对 `TODO` 顶板的最小必要更新
### 已做
- 在 `docs/TODO.md` 顶部 `TRADING DESK BOARD -> Next 3 bot3 runs` 新增 `2026-03-20 04:10 UTC，bot2 desk review`：
  - 保持 `Paper Seat = EMA / waiting_not_due`
  - 保持 `Live Seat = 暂空`
  - 把当前默认 `Scout Seat` 正式编号为 **`Rank 109 / HTF premium-discount long-bias context gate`**
  - 把 `03:54 UTC` 新 digest 的紧邻 reserve 正式编号为 **`Rank 110 / PSAR pre-flip SAR dot reclaim gate`**
  - 把 active Scout 顺序收紧为：`Rank 109 > Rank 110 > fresh intake reserve > 旧 P1 evidence_pool > Rank 17 low-frequency fallback > tiny-live plumbing`
  - 把 `Run 3` 的 failover 更新成：`Rank 109 clean replication / failover 到 Rank 110 intake，再到 fresh paper/repo re-intake，再到 Rank 17 fallback`

### 本轮不做
- 不改 cron prompt：当前通过顶板更新已足够传导给 bot3；
- 不把 `Rank 17` 的 open hosted paper 误写成新的 seat；
- 不把 `Rank 109 / 110` 过早吹成 `P1 / P2` 或 live challenger。

## 4. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：当前切到 `Rank 109 / HTF premium-discount long-bias context gate`
- **Scout reserve**：更新为 `Rank 110 / PSAR pre-flip SAR dot reclaim gate > fresh paper/repo intake reserve`
- **P2 / P4 仍空**
- **Rank 17` 当前只算 `P3 low-frequency fallback`，本轮没有新的 status-changing event**
- **bot3 接下来默认：EMA due-check -> Rank 109 intake -> Rank 109 clean replication / failover 到 Rank 110 intake，再到 fresh re-intake**
