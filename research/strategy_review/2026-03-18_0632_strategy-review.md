# 2026-03-18 06:32 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA baseline family` 占位，但当前更诚实的排班已经不是把接下来三轮都写成纯 `Scout fallback`：在 `A 股 07:00 UTC` due window 临近的前提下，前两轮仍按 `EMA waiting_not_due -> Scout Seat` 处理，第三轮应预留回 **`EMA due-now follow-up`**；`Live Seat` 继续空席；`Scout Seat` 当前主资源位只剩 **`Rank 48 / session-range active-hours gate`**，`Rank 35b` 仍只是 fallback，不应提前抢位。

## 本轮先检查了什么
- `git -C /root/clawd/jerry/momentum status --short --branch`
  - 结论：repo/workspace 仍有大量与本轮无关的脏文件与未跟踪文件；本轮继续只做 `TODO` 顶板最小 writeback、strategy review 记录、站点页面刷新，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0518_ema-adx-source-intake.md`：`Rank 47 / EMA-ADX-VOL skeleton` 已完成两条轻量诚实守门。
  - `2026-03-18_0540_ema-adx-clean-replication-park.md`：`Rank 47` 已在允许预算内完成最小 clean replication，并给出 hard verdict=`park / evidence pool`。
  - `2026-03-18_0622_rank48-session-range-intake.md`：`Rank 48 / session-range active-hours gate` 已完成 source intake，两条轻量诚实守门已过，当前是 **`guard-passed / admit_to_clean_replication_queue`**。
- 最近 strategy review
  - `2026-03-18_0453_strategy-review.md`：当时仍把 `Rank 46 / OI participation gate` 放在 Scout 主资源位，并把 `Run 3` 暂时给到 `Rank 32b append/review sync`。
  - 到当前窗口，这两个判断都已过期：`Rank 46` 已在 `05:08 UTC` 被压回 `park`，而 `06:28 UTC` 的 narrow-paper 托管刷新已显示 `new_closed_trades_appended=0`，说明 `Rank 32b` 那次 append 事件已被托管链完全消化。
- 当前 cron 列表
  - `bot3-momentum-auto-opt-13m`：健康，最近已如实完成 `Rank 47 park`、`Rank 48 intake`。
  - `momentum-narrow-paper-lanes-20m`：健康，`2026-03-18T06:28:47Z` 刷新显示 `new_closed_trades_appended=0`。
  - `bot6-park-reframe-2h`：健康，继续只做低频 derived queue，不改当前主席位。
  - `bot7-quant-digest-30m`：本轮列表里最新状态是一次瞬时 error，但不改变当前 desk judgment；眼下也没有比 `Rank 48` 更近的新 fresh source 已落板。

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due（但已进入 due-soon 窗口）`**。
- 直接证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：此刻仍不是漏跑 refresh，而是 **真实 waiting_not_due + 即将切到 due-now**。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. 当前没有任何候选已走到 `P4 tiny-live review candidate`；
  2. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 都是 `P3 narrow paper lane`，不是 live challenger；
  3. `breakout` 已 bench / close，不该被重新抬回默认 live 位；
  4. `Rank 48` 目前还只是 `P1 -> clean replication queue`，离 `Live Seat` 还早。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- 当前真正 active 的 paper/repo based Scout 候选只有：
  1. **`Rank 48 / session-range active-hours gate`**（当前默认主资源位）
- 当前只保留 fallback、不应抢主位的：
  2. `Rank 35b`（derived fallback，非 fresh paper/repo source）
- 当前不应重新抢主资源位的已结案候选：
  - `Rank 44 / BotScalpingTwinRange` → `park`
  - `Rank 45 / FibTrend-Pro` → `park`
  - `Rank 46 / OI participation gate` → `park`
  - `Rank 47 / EMA-ADX-VOL skeleton` → `park`
  - `Rank 27b / Rank 40 / Rank 43` → `park`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 48 / session-range active-hours gate` → **`P1`**（`source intake / 两条轻量诚实守门已过 / admit_to_clean_replication_queue`）
- `Rank 35b` → **queue-only / not admitted**（derived fallback，只有 fresh intake 再次失效才回退）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（narrow paper pilot 托管层；当前没有新的 status-changing event）
- `Rank 44 / 45 / 46 / 47 / 27b / 40 / 43` → **`P0`**（允许预算内已完成最小检查并压回 `park / evidence pool`）
- **当前 `P2` 为空，`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check only**
   - 这轮仍先诚实检查是否已进入 `due-now / overdue`；若仍是 waiting-window，立刻跳过，不空转。
2. **Run 2 — `Rank 48 / session-range active-hours gate` minimal clean replication**
   - 固定 `BTC/ETH/SOL 15m`、`next-bar open + no-overlap`；
   - 只比较 `raw_all_day`、`active_hours_only`、`session_structure_gate`、`+volume_gate`、`+ADX_or_HTF_gate`；
   - 最先回答 `2~4 bar fail rate`、`post-cost expectancy`、`trade_count retention`、`session-bucket contribution`。
3. **Run 3 — `EMA` due-now follow-up（A 股 07:00 close window）**
   - 因为按当前 bot3 节奏，第三轮大概率已落在 `07:00 UTC` 之后；
   - 若届时 `ema_paper_trading_due_guardrail_snapshot.csv` 已切到 `due-now / overdue`，就直接回 `Run 1 / EMA refresh`；
   - 只有若第三轮仍未真正 due，才回退到 `Rank 35b / tiny-live plumbing`，而不是默认继续把三轮都写成 Scout。

## Active Scout 候选的边际价值比较
1. **`Rank 48` 当前边际价值最高**
   - 它是唯一仍然存活的 fresh `repo + paper based` 15m crypto 候选；
   - 它不是再造一条新 alpha，而是可能服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 三条当前收口线的共用 overlay；
   - 比 `Rank 35b` 更贴当前 desk，因为 `Rank 35b` 只是 derived fallback。
2. **`Rank 35b` 仍只值 fallback**
   - 只要 `Rank 48` 还没跑完那唯一一次最小 clean replication，就不该提前切回 `Rank 35b`；
   - 否则会把 `Scout Seat` 又滑回“derived queue 先于 fresh paper/repo”的旧模式。
3. **当前不值得继续磨 `P3` 托管位**
   - `06:28 UTC` narrow-paper 托管刷新已显示没有新 closed-trade append；
   - 因此这轮不应再把 `Rank 32b`、`Rank 17` 等托管位误写成新 seat 或默认 Run 3。

## strongest evidence
- `ema_paper_trading_due_guardrail_snapshot.csv` 明确显示：`EMA` 仍是 waiting-window，但 A 股 due 窗口就在 `07:00 UTC`。
- `2026-03-18_0622_rank48-session-range-intake.md` 已把 `Rank 48` 冻结到 `guard-passed / admit_to_clean_replication_queue`。
- `manual_narrow_paper_last_run_summary.json`（`2026-03-18T06:28:47Z`）显示 `new_closed_trades_appended=0`，说明上一轮 `Rank 32b` append 事件已经被托管层吸收，不需要再抢默认主资源。

## weakest / should-not-overweight lines
- 最不该高估的是把 `due-soon` 仍然写成“三轮都纯 Scout fallback”；这会错过接下来马上到点的 `EMA` refresh 窗口。
- 同样不该高估的是 `Rank 35b`；它仍只是 derived fallback，不应在 `Rank 48` 尚未跑完最小 replication 之前抢位。

## 建议优先级 Top 1~3
1. 先把 `Next 3 bot3 runs` 改成 **`Run 1 = EMA due-check only -> Run 2 = Rank 48 minimal clean replication -> Run 3 = EMA due-now follow-up`**。
2. `Rank 48` 只给 **1 次最小 clean replication**，做完更偏向 `park / 升格`，不要继续停在 intake 文案层。
3. 到 `07:00 UTC` 后，第一时间如实检查 `EMA` 是否转成 `due-now / overdue`；若是，优先回 `EMA refresh`，不要让 bot3 继续沿 Scout 线漂移。

## TODO / web / cron 的改动或建议
- **已改**：`docs/TODO.md` 顶部 `Next 3 bot3 runs` authoritative board，写回当前 `06:32 UTC` 的 near-due judgment。
- **网页可见落点**：同步重建 `reports/site/plans/momentum_todo.html`，让 reader-facing desk board 也反映这次排班变化。
- **cron**：本轮不改 cron；当前只是时间窗内的 `Next 3` 调度修正，不是节奏设计变化。

## 风险与不确定性
- `Rank 48` 目前还不是 clean replication，更不是 `P2 paper candidate`；如果它只是靠切时段砍样本，而没改善成本后 expectancy，应快速压回 `park / evidence pool`。
- `EMA` 的第三轮 due-now follow-up 依赖实际 wall-clock 与 bot3 触发时刻的贴近度；若第三轮触发略早于 `07:00 UTC`，就应如实回退而不是伪造 due。
- 当前 workspace 脏文件很多，本轮仍不适合安全 selective commit。

## Commit
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不安全混提。
