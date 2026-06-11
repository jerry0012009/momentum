# Strategy Review — 2026-03-20 01:53 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；首要动作是校正 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛复述研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1624`
- 最近 optimization logs：
  - `2026-03-20 01:49 UTC` `Rank 104 / post-break sign-flip density` clean replication -> `park`
  - `2026-03-20 01:15 UTC` `Rank 104` source intake
  - `2026-03-20 00:54 UTC` `Rank 103 / confirmed extremum honest fib anchor` clean replication -> `park`
  - `2026-03-20 00:09 UTC` `EMA crypto due refresh`
- 最近 strategy review：
  - 最新仍是 `2026-03-20 01:09 UTC`
- 当前 cron（只记 desk 相关状态）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：运行中 / 最近 `ok`
  - `bot7-quant-digest-30m`：最近 `ok`，已新增 `01:40 elephant candle corridor` digest
  - `bot6-park-reframe-2h`：最近 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：最近 `ok`
- Paper Seat 实时状态：
  - `ema_paper_trading_due_guardrail_snapshot.csv` 当前全 desk 无 `due-now / overdue`
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`
- P3 sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T01:22:46Z`
  - `new_closed_trades_appended=0`
  - `manual_narrow_paper_status.csv` 仍显示 `Rank 17` 有 open positions，但这只算 hosted `P3 continuity`，不改 seat
- 最近新增 digests：
  - `01:40` `elephant candle corridor long-bias gate`
  - `01:05` `regression channel width not shared gate`
  - `00:32` `Supertrend parameter-surface / PSAR role gate`
  - `00:08` `MTF CHOP charged-up count`

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：现在是真的被 market clock 卡住，不是 paper 线还有没做完的 continuation。最近真正到点的是 `A股三条 lane -> 2026-03-20 07:00 UTC`；在此之前，bot3 不该围着 EMA 假装忙。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- `Rank 104` 刚在 `01:49 UTC` clean replication 后被压回 `park / evidence pool`；
- 当前 fresh Scout 候选都还没过 `clean replication`，更没进入 `Light Stability Pack`；
- `Rank 2 / 17 / 29 / 32b` 继续只是 `P3 hosted lanes / sidecar`，不是 live challenger；
- 当前不应为了“桌上得有个 live 名字”而重新抬已 bench 的 breakout 旧线。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
本轮重新显式比较 active Scout 的边际价值后，当前更诚实的顺序是：

1. **`body-defined zone re-entry honest failure verdict`**（repo）
2. **`elephant candle corridor long-bias gate`**（repo）
3. **`MTF CHOP charged-up count`**（repo）
4. **`prebreak higher-low pressure ladder context gate`**（repo）

补充判断：
- `body-defined zone re-entry` 仍是当前最该先开的主资源位，因为它最直接服务 `breakout-short / Fib / EMA-PSAR` 共同缺的 **honest failure verdict spine**；
- `elephant candle corridor` 这轮应正式插入 reserve，因为它给出了更 queue-facing 的下一手问题：**reclaim / continuation 那根确认 bar 到底算不算“强但不过热”**；
- `MTF CHOP charged-up count` 仍保留，但当前更像 `retest_hold long-side veto`，样本更薄、角色更窄；
- `prebreak higher-low pressure ladder` 仍只配当上下文特征，不该抢主资源位；
- `regression channel width` 已被 `01:05` digest 压成 `not-shared-gate / evidence only`；
- `Supertrend parameter-surface / PSAR role gate` 当前更像 `Paper Seat` 参数稳定性支援题，不是默认 Scout 主资源位。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`body-defined zone re-entry honest failure verdict`** → **`P0`**（`source intake / 两条轻量诚实守门 next`）
- **`elephant candle corridor long-bias gate`** → **`P0`**（`fresh repo reserve / long-side bounce-quality gate`）
- **`MTF CHOP charged-up count`** → **`P0`**（`fresh repo reserve / long-side veto`）
- **`prebreak higher-low pressure ladder context gate`** → **`P0`**（`context backlog / not standalone admission key`）

#### 旧候选层级（本轮不升格）
- **`Rank 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 不再默认续命`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 body-defined zone re-entry honest failure verdict 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 body-defined zone re-entry honest failure verdict guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 elephant candle corridor long-bias gate 的 source intake；只有这一层也 exhausted，才轮到 MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate > 旧 P1 evidence_pool > P3 continuity sidecar > tiny-live plumbing`**

## 2. 为什么这轮把 `elephant candle corridor` 插进 reserve，但没让它抢过 `body-defined zone`
### `body-defined zone re-entry` 仍排第一
- 它是当前候选里**唯一最像 shared verdict spine** 的一条；
- 代理快检直接回答的是“回到 wick 区还不够，回到 body accepted zone 才更像真失败 / 真修复”；
- 这条问题对 `breakout-short`、`Fib retest_hold`、`EMA/PSAR continuation repair` 都立刻有用。

### `elephant candle corridor` 升到第二
- 它也是 repo-based、15m crypto、规则足够清楚；
- 它比 `MTF CHOP` 更接近一个可立刻认领的 queue-facing admission 问题：确认 bar 是否 **强但不过热**；
- 它对 `Fib reclaim long / EMA continuation long` 的代理改善更直观，且样本量比 `MTF CHOP charged>=2` 更扎实。

### `MTF CHOP` 暂列第三
- 这条仍有价值，但更像 long-side veto，不是 shared admission / failure spine；
- 当前 `charged>=2` 的关键子样本偏薄，更适合做第二层 reserve，而不是抢过前两条。

### `prebreak ladder` 继续第四
- 最新 digest 已经很明确：它更像上下文特征，不像独立入场键；
- 除非前面几条 fresh 候选都 exhausted，否则不该重新抢主资源位。

## 3. P3 continuity 预算口径（本轮强调）
- `EMA = waiting_not_due` 时，bot3 不得把 `P3 narrow paper continuity` 当默认 Run 2/Run 3；
- 最新 `manual_narrow_paper_last_run_summary.json` 已回到 `new_closed_trades_appended=0`，因此当前没有新的 `status-changing event` 需要插队；
- 今天从 `00:09 UTC` 之后，bot3 主资源实际都花在 `EMA due refresh` 与 `Rank 103 / 104` Scout 链上，**`P3 continuity` 的 bot3 主资源预算可视为尚未动用**；
- `Rank 2 / 17 / 29 / 32b` 继续只由 sidecar 托管，不重新占 `Scout Seat`。

## 4. 本轮最小必要动作
### 已做
- 对 `docs/TODO.md` 顶部 `TRADING DESK BOARD -> Next 3 bot3 runs` 做最小必要更新：
  - 新增 `2026-03-20 01:53 UTC，bot2 desk review` 补充；
  - 保持 `Paper Seat = EMA / waiting_not_due`、`Live Seat = 暂空`；
  - 维持 `Scout Seat = body-defined zone re-entry honest failure verdict`；
  - 把 active Scout reserve 顺序更新为 `elephant candle corridor > MTF CHOP > prebreak ladder`；
  - 把 `Run 3` 的 failover 更新成先切 `elephant candle corridor`，而不是直接回到 `MTF CHOP`。

### 本轮不做
- 不改 cron prompt：当前排班只需通过顶板更新即可传导到 bot3；
- 不把 `Rank 17` 的 hosted paper 状态误写成新 seat；
- 不把 `elephant candle corridor` 直接吹成 live challenger 或 `P2`。

## 5. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：继续是 `body-defined zone re-entry honest failure verdict`
- **Scout reserve**：改成 `elephant candle corridor > MTF CHOP > prebreak ladder`
- **P2 / P4 仍空**
- **bot3 接下来默认：EMA due-check -> body-zone intake -> body-zone clean replication / failover 到 elephant corridor intake**
