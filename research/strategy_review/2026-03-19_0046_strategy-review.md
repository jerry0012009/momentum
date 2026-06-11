# 2026-03-19 00:46 UTC strategy review

## 轮次定位
- 时间：2026-03-19 00:46 UTC
- 任务：bot2 交易 desk 统揽 / 排兵布阵巡检
- 目标：维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，明确当前 `Paper / Live / Scout` 三席与接下来 `Next 3 bot3 runs`

## 开始前检查
### 1) repo 状态
- `git status --short` 仍显示工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件。
- 本轮只做最小必要更新：`docs/TODO.md` 顶板 1 处顺序校准、本轮 strategy review 记录、邮件摘要、首页 index 刷新。
- 不做混提，不做清理。

### 2) 最近 optimization logs
- `2026-03-19_0002_ema-crypto-refresh-append.md`
  - `Paper Seat / EMA` 已在真实 crypto due window 完成续写；最新 due 点已切到 `A股三条 lane -> 2026-03-19 07:00 UTC`。
- `2026-03-19_0013_rank72-source-intake.md`
  - `Rank 72 / realized-vol mid-band cost-survival gate` 完成 source intake + 两条轻量诚实守门，当时进入 `guard-passed`。
- `2026-03-19_0032_rank72-midband-clean-replication.md`
  - `Rank 72` 已在允许预算内完成 minimal clean replication，并给出 **`park / evidence pool`** hard verdict。
- `2026-03-19_0043_rank73-source-intake.md`
  - `Rank 73 / PSAR close-confirmed follow-up gate` 已完成 source intake + 两条轻量诚实守门，进入 **`guard-passed / admit_to_clean_replication_queue`**。

### 3) 最近 strategy review
- 最近两轮 bot2 review：
  - `2026-03-19_0006_strategy-review.md`
  - `2026-03-18_2321_strategy-review.md`
- 上轮核心判断：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat` 头部切到 `Rank 73`；默认下一轮先做 `Rank 73 minimal clean replication`。
- 本轮新增判断：当前 `Rank 73` 之后不应默认直接回退 `Rank 35b / Rank 16b`；fresh paper / repo source 池仍未 exhausted，应先重新认领 fresh intake。

### 4) 当前 cron 列表
- `bot2-strategy-review-40m`：启用，当前运行中，上一轮 `ok`
- `bot3-momentum-auto-opt-13m`：启用，上一轮 `ok`
- `momentum-narrow-paper-lanes-20m`：启用，上一轮 `ok`
- `bot7-quant-digest-30m`：启用，上一轮 `ok`
- `bot6-park-reframe-2h`：启用，上一轮 `ok`
- quota email / 旧 bot4 等 cron 不影响当前 seat judgment

## 当前关键证据
### Paper Seat / market clock
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
  - 当前全 desk 无 `due-now / overdue`
  - 下一次最早 due 点：`A股三条 lane -> 2026-03-19 07:00 UTC`
  - 其后：`美股 1d+1wk -> 2026-03-19 20:00 UTC`
  - `Crypto 1d+1wk -> 2026-03-20 00:00 UTC`

### P3 continuity
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-19T00:35:13Z`
  - `new_closed_trades_appended = 0`
  - 说明当前没有新的 `P3 status-changing event`

### Fresh source pool 并未耗尽
- `research/quant_digests/INDEX.md` 里仍有多条未进入 queue-facing 层的新 paper / repo 候选；最新一条就是 `2026-03-19 00:23` 的 `gcr-inflection-exhaustion-veto`。
- `docs/RECENT_PAPER_SEEDS.md` 与 `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 仍能继续提供 paper-based intake。
- `docs/PARK_REFRAME_QUEUE.md` 里虽有 `Rank 35b / Rank 16b` 等 `derived_hypothesis_drafted` 条目，但按当前 desk 规则，它们只能在 fresh source 这一层本轮也拿不到合格对象时，才进入 fallback 比较。

## 本轮 desk verdict
### 1. 谁坐 `Paper Seat`？
- **`EMA` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 口径：`00:02 UTC` 的 crypto due window 已真实消化；当前最近 due 点已切到 `A股 07:00 UTC`，所以这条 seat 现在是 market-clock waiting，不是 desk 空闲。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 73` 目前只到 `guard-passed / clean replication next`，还没到 `P2 / P3`；
  2. `Rank 72` 已在 minimal clean replication 后压回 `park / evidence pool`；
  3. `Rank 2 / 17 / 29 / 32b` 仍只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 active 主资源位**：
  - `Rank 73 / PSAR close-confirmed follow-up gate`
- **当前不该误写成 active fast-lane 主线，但仍是合法下一层 source pool**：
  - `fresh paper / repo source re-rank`（来自 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist`）
- **仅当 fresh source 本轮也 exhausted 时，才允许进入 fallback 比较**：
  - `Rank 35b`
  - `Rank 16b`
- **明确不该继续霸占 fast-lane 的对象**：
  - `Rank 72`：已 `park / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 73 / PSAR close-confirmed follow-up gate` → **`P1 weak candidate`**（`guard-passed / clean replication next`）
- `Rank 72 / realized-vol mid-band cost-survival gate` → **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper continuity / low-frequency health check only`）
- fresh paper / repo source pool（未新拿 rank 的 seed / digest 候选）→ **`P0 source intake pool`**
- 当前 **`P2` 暂空、`P4` 暂空**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check only**
   - 盯住最新 due guardrail；若仍是 `waiting_not_due`，不得空转。
2. **Run 2 = 若 `EMA` 仍 `waiting_not_due`，则给 `Rank 73 / PSAR close-confirmed follow-up gate` 做 1 次最小 clean replication**
   - 只比较 `raw_trigger / close_confirmed_N1 / N2 / N3` 四臂，统一 `signal 当根及之前数据 + next-bar open + no-overlap`。
3. **Run 3 = 若 `Rank 73` 这一轮给出 hard verdict，则先从 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 重新认领 1 条 fresh paper / repo source intake；只有 fresh source 这一层本轮也拿不到合格对象时，才允许回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 边际价值比较（本轮显式重排）
**`Rank 73 / PSAR close-confirmed follow-up gate` > `fresh paper / repo source re-rank（RECENT_PAPER_SEEDS / quant_digests / validated shortlist）` > `Rank 35b / Rank 16b（derived fallback only）` > `tiny-live plumbing`**

### 为什么是这个顺序
- `Rank 73` 已经过了两条轻量诚实守门，离下一次硬 verdict 最近；
- `Rank 72` 已 park，不应继续霸占 fast lane；
- 当前 fresh source 池仍明显有货，按 desk 规则不该先跳回 derived-hypothesis fallback；
- `P3 continuity` 当前没有 due-now / append / weekly-review / 明显异常，不应回头抢主资源。

## 对 TODO 顶部作战板的最小必要更新
已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，但只做了 **1 处口径校准**：
1. 在 `Scout Seat verdict / Next 3 bot3 runs` 顶部新增 `2026-03-19 00:46 UTC` 最新块；
2. 明确当前 `Rank 73` 之后的正确顺序不是“直接回退 `Rank 35b / Rank 16b`”，而是：
   - 先做 `fresh paper / repo source re-rank`
   - 只有这一层本轮也拿不到合格对象时，才允许比较 `Rank 35b / Rank 16b`
3. 其余大席位判断不变：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout Seat` 头部 = `Rank 73`

## Reader-facing / publish
- 本轮属于 **有轻微 judgment 变化的巡检**：大席位没变，但 `Run 3` fallback 顺序收紧了，避免 bot3 过早从 fresh source 池滑回 derived-hypothesis 旧 rank。
- 已把变化写回 `docs/TODO.md` 顶板；接下来刷新首页 index。

## 提交
- 未提交
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，避免混提
