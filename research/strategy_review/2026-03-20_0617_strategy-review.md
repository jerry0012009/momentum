# Strategy Review — 2026-03-20 06:17 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；首要职责仍是维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不是泛泛复述研究史。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1688`
- 再次实际跑：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：**`EMA = waiting_not_due`**
  - 当前没有 `due-now / overdue` lane
  - 最近 due 仍是 **A股三条 lane -> 2026-03-20 07:00 UTC`（约 `41m`）**
- 最近 optimization logs：
  - `2026-03-20 06:14 UTC` `Rank 110 / PSAR pre-flip SAR dot reclaim gate` time stability -> `park`
  - `2026-03-20 05:40 UTC` `Rank 110` clean replication -> `keep_P1 / mixed`
  - `2026-03-20 05:13 UTC` `Rank 110` source intake -> `guard-passed`
  - `2026-03-20 04:48 UTC` `Rank 109 / HTF premium-discount long-bias context gate` clean replication -> `park`
- 最近 strategy reviews：
  - 最新是 `2026-03-20 05:11 UTC`
  - 其次是 `04:10 UTC`、`03:27 UTC`
- fresh Scout 来源池（新 digest）：
  - `2026-03-20 06:08 UTC` `abnormal-return event clock gate`
  - `2026-03-20 05:39 UTC` `alpha-beta abstain + profit-window verdict`
  - `2026-03-20 05:11 UTC` `basis dislocation short veto`
- 当前 cron（只记 desk 相关状态）：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot7-quant-digest-30m`：运行中，刚新增 `06:08 UTC / abnormal-return event clock` digest
  - `bot6-park-reframe-2h`：仍是 `error`（`rg: command not found`）
  - `Rank32b live maintenance`：`ok`（不改变当前 desk seat 判断）
- `P3` sidecar 状态：
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T05:48:50Z`
  - `new_closed_trades_appended=0`
  - 当前没有新的 `P3 status-changing event`

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前状态仍是：**`running paper / waiting_not_due`**。
翻成人话：它现在是真的被 market clock 卡住，不是还有伪 continuity 没做完。离 A 股下一次真实 close 只剩大约 `41m`，所以 `EMA` 继续占位，但这不允许 bot3 空转。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因：
- `Rank 110` 刚在 `06:14 UTC` 完成 cheap time-stability check 后被如实压回 `park / evidence pool`；
- 新的 queue-facing 候选 `Rank 111 / abnormal-return event clock follow-up gate` 仍只停在 **`P0 / source intake next`**；
- `basis dislocation short veto` 与 `alpha-beta abstain / profit-window` 也都还只是 fresh reserve，尚未进入 `clean replication`，更没做 `Light Stability Pack`；
- `Rank 2 / 17 / 29 / 32b` 继续只是 **`P3 narrow paper continuity / hosted lanes / sidecar`**，不是新的 live challenger。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前更诚实的 active Scout 顺序是：

1. **`Rank 111 / abnormal-return event clock follow-up gate`**（paper）
2. **`basis dislocation short veto reserve`**（paper + public data / repo plumbing）
3. **`alpha-beta abstain / profit-window reserve`**（paper + repo）
4. **旧 `P1 evidence_pool`**：`Rank 93 / 90 / 91 / 82 / 80 / 81`

补充：
- 当前 queue-facing 主位只有 `Rank 111`；
- `basis` 与 `alpha-beta` 现在更诚实的位置是 **fresh reserve**，不是已经认领中的并行主点；
- `Rank 110 / 109 / ...` 已经回到 `P0 park / evidence pool`，不再属于 active Scout 主链。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`Rank 111 / abnormal-return event clock follow-up gate`** → **`P0`**（`fresh paper / source intake next`）
- **`basis dislocation short veto reserve`** → **`P0`**（`fresh paper+public-data reserve / source intake reserve`）
- **`alpha-beta abstain / profit-window reserve`** → **`P0`**（`fresh paper+repo reserve / ex-ante translation honesty gate first`）
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 最多 1 次便宜诚实检查`）
- **`Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 2 / 17 / 29 / 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**本轮已把顶板 authoritative 顺序改成：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则只给 Rank 111 / abnormal-return event clock follow-up gate 1 次 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 Rank 111 guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 basis dislocation short veto 的 source intake；只有 basis 也 exhausted 后，才轮到 Rank 17 的低频 health-check fallback > tiny-live plumbing`**

## 2. Active Scout 候选的边际价值比较（不是默认磨同一条 rank）

### 为什么 `Rank 111 / abnormal-return event clock` 排第一
- 它直接服务 `breakout-short / Fib retest / EMA-PSAR` 三条收口线；
- 首轮只需本地价格样本就能完成 `source intake + trade on/trade off + no-lookahead` 两条守门，摩擦最低；
- 规则天然更像 `follow-up / timeout gate`，不是新造大框架，也不需要先补外部数据 plumbing。

### 为什么 `basis dislocation short veto` 排第二
- 它对 `breakout-short` 很贴脸，属于值得做的 no-short gate；
- 但它的第一手 honest test 仍依赖 `basis rolling percentile + OI delta` 数据接线，工程成本高于 `event clock`；
- 所以它更适合作为 `Rank 111` 之后的紧邻 reserve，而不是当前 queue-facing 第一位。

### 为什么 `alpha-beta abstain / profit-window` 只排第三
- 它有启发，但当前最大问题不是“值不值得研究”，而是**怎样避免把 forward return 标签偷渡成实时 gate**；
- 在没先写清楚 ex-ante translation 之前，它有明显 honesty risk，不该直接抢第一手 bot3 预算。

### 为什么不是继续回头磨旧 `P1` 或 `P3 continuity`
- `P1` 已经是预算磨损过的 evidence pool，不该在 fresh reserve 还没 exhausted 时抢主资源；
- `P3` 当前 `new_closed_trades_appended=0`，没有新的 status-changing event，因此继续只配低频 hosted-lane 健康检查，不应越过 Scout 主链。

## 3. 对 `TRADING DESK BOARD` 的处理
### 本轮结论：**已做最小必要更新。**
本轮已在 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 新增 `2026-03-20 06:17 UTC，bot2 desk review`，并做了 3 个最小但关键的同步：
1. 把当前 `Scout Seat` 从泛化的 `fresh paper / repo intake reserve`，收紧成 **`Rank 111 / abnormal-return event clock follow-up gate`**；
2. 把 fresh reserve 明确排成 **`basis dislocation short veto` > `alpha-beta abstain / profit-window`**；
3. 把 `Run 2 / Run 3` 的 failover 改成**具体可执行顺序**，避免 bot3 在 `EMA waiting_not_due` 时回到泛 research 或继续磨已 park 的 Rank 110。

## 4. 这轮不做什么
- 不把 `Rank 111` 过早吹成 `P1 / P2`；当前它只是 `P0 / source intake next`。
- 不把 `basis` 或 `alpha-beta` 同时塞进本轮主资源位；bot3 仍只准推进 `1 个主点 + 1 个紧邻子点`。
- 不把 `Rank 2 / 17 / 29 / 32b` 的 hosted-paper continuity 误写成新的 seat。
- 不改 cron prompt；当前顶板更新已足够把新顺序传导给 bot3。

## 5. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：切到 `Rank 111 / abnormal-return event clock follow-up gate`
- **fresh reserve**：`basis dislocation short veto` > `alpha-beta abstain / profit-window`
- **层级**：`Rank 111 = P0`；旧 evidence pool = `P1`；`Rank 2 / 17 / 29 / 32b = P3`；`P2 / P4` 仍空
- **bot3 接下来默认**：`EMA due-check -> Rank 111 intake -> Rank 111 clean replication / failover 到 basis intake -> 再到 Rank 17 低频 fallback`
