# 2026-03-18 04:53 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA / PSAR raw alpha` 占位且当前只是 `waiting_not_due`；`Live Seat` 继续空席；`Scout Seat` 当前应由 **`Rank 46 / OI participation gate`** 占主资源位，`Rank 47 / EMA-ADX-VOL skeleton` 退到次选，`Rank 35b` 只保留 fallback。与此同时，`manual narrow-paper lanes` 在 `04:49 UTC` 新增了 **`Rank 32b / SOL-USD`** 的真实 closed-trade append，所以 `Run 3` 不该继续留给空泛 plumbing，而应改成 **`Rank 32b` 最小 append/review writeback**。

## 本轮先检查了什么
- `git -C /root/clawd/jerry/momentum status --short`
  - 结论：repo/workspace 仍有大量与本轮无关的脏文件与未跟踪文件；本轮继续只做 `TODO` 顶板最小 writeback、strategy review 记录、站点镜像刷新，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0449_ema-oi-source-intake.md`：`Rank 46 / OI participation gate` 已完成 source intake，两条轻量诚实守门已过，当前定位是 **`guard-passed / admit_to_clean_replication_queue`**。
  - `2026-03-18_0440_fibtrend-clean-replication-park.md`：`FibTrend-Pro` 已完成那唯一一次最小 clean replication，并如实压回 **`park / evidence pool`**。
  - `2026-03-18_0402_rank27b-atr-zone-park.md`、`2026-03-18_0357_psar-anchor-clean-replication-park.md`：`Rank 27b` 与 `BotScalpingTwinRange` 也都已在允许预算内压回 `park`。
- 最近 strategy review
  - `2026-03-18_0411_strategy-review.md`：上一轮已把 `Scout Seat` 从 `Rank 35b` 拉回 fresh repo intake，并把优先级校到 `FibTrend-Pro > EMA-ADX-VOL skeleton > Rank 35b`。
  - 当前与上一轮相比，真正变化有两点：
    1. `FibTrend-Pro` 已在 `04:40 UTC` 跑完最小 replication 后压回 `park`；
    2. `04:49 UTC` 新出现 `Rank 46 / OI participation gate` source-intake 通过，且同一时刻 `manual narrow-paper lanes` 出现了 `Rank 32b` 的真实 closed-trade append。
- 当前 cron 列表
  - `bot3-momentum-auto-opt-13m`：健康；最近已如实把 `FibTrend-Pro` 压回 `park`，再把 `Rank 46 / OI participation gate` 推到 `guard-passed`。
  - `momentum-narrow-paper-lanes-20m`：健康；`04:49 UTC` 刷新摘要显示 `new_closed_trades_appended=1`。
  - `bot7-quant-digest-30m`：健康；提供 fresh repo source 池。
  - `bot6-park-reframe-2h`：健康；`Rank 35b` 仍只是 derived fallback。

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：当前不是 paper refresh 漏跑，而是真的还没到下一次 due 窗口。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 都是 `P3 narrow paper lane`，不是 live challenger；
  2. 当前没有任何候选达到 `P4 tiny-live review candidate`；
  3. 已 bench 的 breakout 不应被重新抬回；
  4. 这次 `Rank 32b` 的 closed-trade append 只说明它需要最小 continuity writeback，不构成 live promotion。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- 当前 active Scout 候选应读成：
  1. **`Rank 46 / 15m-EMA-9-15-OI-Flip-Signals / OI participation gate`**
  2. **`Rank 47 / EMA-ADX-VOL-CRYPTO KILLER [15M] / EMA-ADX-VOL skeleton`**
  3. `Rank 35b`（仅 fallback）
- 不应重新抢主资源位的线：
  - `FibTrend-Pro`：已完成最小 clean replication，当前 hard verdict=`park`
  - `BotScalpingTwinRange / Rank 27b / Rank 40 / Rank 43`：都已在允许预算内给出 hard verdict=`park`
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：属于 `P3` 托管，不是当前默认 `Scout Seat`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 46 / OI participation gate` → **`P1`**（`source intake / 两条轻量诚实守门已过 / admit_to_clean_replication_queue`）
- `EMA-ADX-VOL-CRYPTO KILLER [15M]` → **`P1`**（`source intake queue / 两条轻量诚实守门 pending`）
- `Rank 35b` → **queue-only / not admitted**
- `Rank 32b` → **`P3`**（`narrow paper pilot approved / full scope / 04:49 UTC 新增 closed-trade append`）
- `Rank 17` → **`P3`**（`narrow paper pilot approved / ETH+SOL only / 当前 2 个 open positions waiting next refresh`）
- `Rank 29` → **`P3`**（`narrow paper pilot approved / low-frequency monitoring only`）
- `Rank 2` → **`P3`**（`narrow paper pilot approved / tiny-live replay execution surface still blocked`）
- `FibTrend-Pro / BotScalpingTwinRange / Rank 27b / Rank 40 / Rank 43` → **`P0`**（`已完成允许预算 -> park / evidence pool`）
- **当前 `P2` 为空，`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check only**
   - 只检查有没有新的 `due-now / overdue`；若仍是 `waiting_not_due`，立即跳过。
2. **Run 2 — `Rank 46 / OI participation gate` minimal clean replication**
   - 固定 `BTC/ETH/SOL 15m`、`next-bar open + no-overlap`；
   - 只比较 `raw EMA(or EMA+PSAR)`、`+oi_level_gate`、`+oi_level_gate+oi_delta_gate`、`+volume_fallback_gate`；
   - 最先回答 `4/8/12 bar follow-through`、`2~4 bar whipsaw ratio`、`net expectancy @ 6/10bps`、`trade_count retention`。
3. **Run 3 — `Rank 32b` closed-trade append / review sync**
   - 这是因为 `manual_narrow_paper_status.csv` 已出现真实 status-changing event：`Rank 32b / SOL-USD` 在 `2026-03-18T04:00:00Z` 新增 closed-trade append；
   - 默认只允许补最小 `append/review` writeback / reader-facing sync；
   - 若托管链已把该 append 完全外显，再回退到 `Rank 47 / EMA-ADX-VOL skeleton`，不要直接跳去空泛 plumbing。

## Active Scout 候选的边际价值比较
1. **`Rank 46 / OI participation gate` 当前边际价值最高**
   - 比 `Rank 47 / EMA-ADX-VOL skeleton` 更窄、更快能给出诚实 verdict；
   - 直接回答当前 desk 真正在意的小问题：`OI > OI-SMA20` 能否在不明显砍掉 trade count 的前提下压低 `2~4 bar whipsaw`；
   - 比 `Rank 35b` 更贴当前 desk，因为前者是 fresh repo-based 15m source，后者仍是 derived fallback。
2. **`Rank 47 / EMA-ADX-VOL skeleton` 次之**
   - 仍是 fresh repo-based 15m crypto source；
   - 但它叠得更厚，当前边际上不如先测 `OI` 这条单轴 filter 来得干净。
3. **`Rank 35b` 只值 fallback**
   - 它不是 fresh paper / repo，而是 park-reframe 派生；
   - 在 fresh source 仍有合格对象的情况下，不应抢主资源位。
4. **`P3` lanes 当前只允许低频状态回补，不重回 `Scout Seat`**
   - 这次只有 `Rank 32b` 出现了真实 closed-trade append，所以只值得拿 1 次最小 append/review sync；
   - `Rank 17 / Rank 29 / Rank 2` 当前没有新的真实 append/review 事件，不该回头占默认主资源。

## strongest evidence
- `ema_paper_trading_due_guardrail_snapshot.csv` 仍清楚显示：`EMA` 当前只是 waiting-window，不是漏跑 refresh。
- `reports/artifacts/literature/scout_repo_ema_oi_participation_source_intake_card.csv` 已明确把 `Rank 46 / OI participation gate` 定位到 `guard-passed / admit_to_clean_replication_queue`。
- `manual_narrow_paper_status.csv` 与 `manual_narrow_paper_closed_trades.csv` 已确认：`Rank 32b / SOL-USD` 在 `04:49 UTC` 刷新中新增了 closed-trade append，这属于真实 status-changing event。
- `momentum-narrow-paper-lanes-20m` 健康，说明 `P3` continuity 继续由专属 cron 托管；bot3 只需在真实事件出现时做最小 writeback，而不该长期回头接管。

## weakest / should-not-overweight lines
- 最不该高估的是把 `P3` 托管误写成新 seat；这次 `Rank 32b` 事件只改变 `Run 3` 的最小回补优先级，不改变席位结构。
- 同样不该高估的是 `Rank 35b`：只要 fresh repo source 还活着，它就仍然只是 fallback。

## 本轮已做的最小必要更新
1. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 把 `Scout Seat` 当前主资源明确切到 `Rank 46 / OI participation gate`；
   - 补写 `P1 / P3 / queue-only` 分级；
   - 把 `Run 3` 从空泛 `tiny-live plumbing` 校到 `Rank 32b closed-trade append / review sync`。
2. 计划同步网页可见落点
   - 重建 `reports/site/plans/momentum_todo.html`
   - 刷新首页 index

## 风险与不确定性
- `Rank 46 / OI participation gate` 目前还不是 clean replication，更不是 `paper candidate`；下一轮若它无法在不显著砍样本的前提下压低 whipsaw，就应快速压回 `park / evidence pool`。
- `Rank 32b` 的 append 已由 dedicated cron 写入 ledger，但 bot3 是否还需要额外 reader-facing writeback，仍要看当前托管页面是否已完全外显；因此把它放在 `Run 3`，而不是抬到前两格。
- 当前 workspace 脏文件很多，本轮仍不适合安全 selective commit。

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了 desk board 最小校准、strategy review 记录与网页同步。