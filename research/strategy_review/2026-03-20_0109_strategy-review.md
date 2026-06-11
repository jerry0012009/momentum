# Strategy Review — 2026-03-20 01:09 UTC

本轮按 `docs/BOT2_STRATEGY_REVIEW_BRIEF.md` 做 40 分钟 desk-head 巡检；重点不是泛研究总结，而是重新确认 `TRADING DESK BOARD` 的席位、候选分级、以及 bot3 接下来 3 轮默认排班。

## 0. 本轮先看了什么
- repo 状态：`branch=master`，`git status --short | wc -l = 1614`
- 最近 optimization / intake：
  - `2026-03-20 00:09 UTC` `EMA crypto due refresh`
  - `2026-03-20 00:34 UTC` `Rank 103 / confirmed extremum honest fib anchor` source intake
  - `2026-03-20 00:54 UTC` `Rank 103` clean replication -> `park`
- 最近 strategy review：最新仍是 `2026-03-20 00:13 UTC`
- 当前 cron：
  - `bot2-strategy-review-40m`：本轮运行中，上一轮 `ok`
  - `bot3-momentum-auto-opt-13m`：上一轮 `ok`，下一轮按新顶板执行
  - `bot7-quant-digest-30m`：上一轮 `ok`，当前有新一轮在跑
  - `momentum-narrow-paper-lanes-20m`：上一轮 `ok`
  - `bot6-park-reframe-2h` / `Rank32b live maintenance`：当前都因 `rg: command not found` 报错，但不改变本轮 desk seat judgment
- Paper Seat 实时状态：
  - `ema_paper_trading_due_guardrail_snapshot.csv` 当前全 desk 无 `due-now / overdue`
  - 最近 due 仍是 `A股三条 lane -> 2026-03-20 07:00 UTC`
- P3 sidecar 状态：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T00:38:45Z`
  - `new_closed_trades_appended=1`
  - 新闭合/刷新主要落在 `Rank 17` hosted lane；属于 **status-changing event**，但仍只算 `P3 continuity sidecar`
- 新增 quant digests：
  - `00:08` `MTF CHOP charged-up count`
  - `00:32` `Supertrend parameter-surface / PSAR role gate`
  - `01:05` `regression channel width not shared gate`

## 1. 五个必答问题（authoritative）

### 1) 谁坐 `Paper Seat`？
**`EMA baseline family` 继续坐 `Paper Seat`。**

当前口径仍是：`running paper pilot / waiting_not_due`。
这次不是执行质量问题，而是真正被 market clock 卡住：最新 due guardrail 仍显示最近 due 在 `2026-03-20 07:00 UTC` 的 A 股三条 lane，因此 bot3 不应围着 EMA 空转，但 EMA 本身也不该被替换。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持 `暂空`。**

原因很直接：
- 当前所有 fresh Scout 候选都还没走到 `clean replication` 之后，更没进入 `Light Stability Pack`；
- `Rank 103` 刚在 `00:54 UTC` 被压回 `park / evidence pool`；
- `Rank 17 / 2 / 29 / 32b` 虽然有 hosted paper continuity，但它们是 `P3 sidecar`，不是新的 live challenger；
- `breakout` 旧 live 口径仍然 bench / close，不应被借尸还魂。

所以本轮没有任何候选够资格从 Scout 直接抢占 `Live Seat`。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
当前 Scout 不应再沿 `Rank 103` 续磨；最新更诚实的 active shortlist 应重排为：

1. **`post-break sign-flip density`**（paper）
2. **`body-defined zone re-entry honest failure verdict`**（repo）
3. **`MTF CHOP charged-up count`**（repo）
4. **`prebreak higher-low pressure ladder context gate`**（repo）

补充说明：
- `regression channel width` 的 `01:05` 新 digest 已经把它压成 **not-shared-gate / evidence only**，本轮不应进入 active Scout 主链；
- `Supertrend parameter-surface / PSAR role gate` 更像 **Paper Seat 的参数稳定性 / role-honesty 支援题**，不是当前 Scout 主资源位；
- `Rank 93 / 90 / 91 / 82 / 80 / 81` 仍只是旧 `P1 evidence_pool`，预算已用，不该默认续命；
- `Rank 17` 的 closed-trade append 只构成 hosted `P3` 低频健康检查，不改 Scout 头牌。

### 4) 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
#### 当前 active Scout / reserve 分级
- **`post-break sign-flip density`** → **`P0`**（`source intake / 两条轻量诚实守门 next`）
- **`body-defined zone re-entry honest failure verdict`** → **`P0`**（`fresh repo reserve / source intake next if main line hard-fails`）
- **`MTF CHOP charged-up count`** → **`P0`**（`fresh repo reserve / veto-only direction / not shared gate yet`）
- **`prebreak higher-low pressure ladder context gate`** → **`P0`**（`context-only backlog / not standalone admission key`）

#### 旧候选层级（本轮不升格）
- **`Rank 93 / 90 / 91 / 82 / 80 / 81`** → **`P1`**（`evidence_pool / budget used / 最多只在极端 fresh exhausted 时再看 1 次 cheap honesty`）
- **`Rank 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 92 / 94 / regression-channel-width`** → **`P0`**（`park / evidence pool`）
- **`Rank 78 / Rank 17 / Rank 2 / Rank 29 / Rank 32b`** → **`P3`**（`narrow paper continuity / hosted lanes / sidecar only`）
- **`P2` 当前仍空**
- **`P4` 当前仍空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
**authoritative 排班：**
1. **`Run 1 = EMA due-check only`**（优先盯 `A股三条 lane -> 2026-03-20 07:00 UTC`）
2. **`Run 2 = 若 EMA 仍 waiting_not_due，则切 post-break sign-flip density 的 source intake + 两条轻量诚实守门`**
3. **`Run 3 = 若 post-break sign-flip density guard-pass，则只给它 1 次最小 clean replication；若它 hard-fail / exhausted，则切 body-defined zone re-entry honest failure verdict；只有这一层也 exhausted，才轮到 MTF CHOP charged-up count > prebreak higher-low pressure ladder context gate > 旧 P1 evidence_pool > P3 continuity sidecar > tiny-live plumbing`**

## 2. 为什么主资源从 `Rank 103` 切到 `post-break sign-flip density`
`Rank 103` 在 `00:54 UTC` 已经拿到了它应得的那 1 次最小 clean replication，并且结论已经足够清楚：
- 它是 **measurement correction / honest anchor**，不是 queue-facing 的 shared gate；
- 既然 proxy `post_cost_expectancy` 仍未过 0，就不该继续停在模糊研究态；
- 按当前 desk 规则，它应被如实压回 `P0 park / evidence pool`。

所以这轮不能继续磨 `Rank 103` 的 closeout / wording / operator packet，而应显式比较新一批 active Scout：

### 边际价值比较（本轮结论）
1. **`post-break sign-flip density` 第一**
   - 原因：它最像一个会直接改变当前 desk judgment 的 **post-break hold-quality / management layer**；
   - 证据也更“queue-facing”：不是再解释“锚点如何更诚实”，而是在问“breakout 后路径形状到底该怎么读”。
2. **`body-defined zone re-entry honest failure verdict` 第二**
   - 原因：它也很贴近 breakout / Fib / EMA 三条收口线，但更像 **failure verdict spine**；
   - 仍值得做，只是当前边际价值略低于 sign-flip，因为它更偏“判失败边界”，而非当前更缺的 hold-quality 读数。
3. **`MTF CHOP charged-up count` 第三**
   - 原因：它更像 `Fib retest_hold long` 的 **veto / size-down overlay**，不是共享放行键；
   - 样本也更偏小，当前更适合当 reserve，而不是直接拿主资源。
4. **`prebreak higher-low pressure ladder` 第四**
   - 原因：最新 digest 已经很明确：它更像 **context feature**，不是独立入场键；
   - 因此它可以保留，但不应排在更 queue-facing 的 sign-flip / body-zone 前面。

## 3. 本轮最小必要动作
### 已做
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD -> Next 3 bot3 runs`：
  - 写入 `2026-03-20 01:09 UTC，bot2 desk review` 新补充
  - 明确把当前 Scout 主资源位从 `Rank 103` 切到 `post-break sign-flip density`
  - 把 reserve 顺序更新为 `body-zone > MTF CHOP > prebreak higher-low`
  - 明确写死 `Rank 17` 的最新 append 仍只算 `P3 sidecar`

### 本轮不做
- 不改 cron prompt：当前排班只需通过顶板更新就能传导到 bot3；
- 不扩写更多 reader-facing 页面：本轮 verdict 变化已通过 `TODO` 顶板这个网页可见入口落地；
- 不把 `Rank 17` 的 closed-trade append 误写成新 seat。

## 4. 结论（超短版）
- **Paper Seat**：继续是 `EMA / running paper / waiting_not_due`
- **Live Seat**：继续 `暂空`
- **Scout Seat**：切到 `post-break sign-flip density`
- **当前没有 P2 / P4 候选**
- **Rank 17 append 只算 P3 sidecar 事件，不改主排班**
- **bot3 接下来默认：EMA due-check -> sign-flip intake -> sign-flip clean replication / failover 到 body-zone**
