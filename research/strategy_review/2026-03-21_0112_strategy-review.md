# 2026-03-21 01:12 UTC strategy review

## 本轮一句话判断
当前 desk 继续维持：**`Paper Seat = EMA / 创业板ETF 1d (active_primary) / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 136 / phase-wide RSI memory retest gate`**。本轮没有出现足以改写席位的新证据；唯一做的最小必要板面维护，是把 `docs/TODO.md` 顶部 `Hosted P3` 快照时间更新到 `2026-03-21 00:57 UTC`，并继续保持 `bot3` 的默认导流顺序为 **`EMA due-check -> Rank 136 clean replication -> Rank 136 最小 verdict-changing follow-up / 否则下一条 fresh intake`**。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2224`
- 最近 optimization logs：
  - `2026-03-21_0059_rank136-phase-rsi-memory-intake.md`
  - `2026-03-21_0054_rank135-clean-replication-park.md`
  - `2026-03-21_0027_rank135-retest-tolerance-stop-decoupling-intake.md`
  - `2026-03-21_0016_rank134-clean-replication-park.md`
  - `2026-03-20_2359_rank133-park-rank134-intake.md`
- 最近 strategy reviews：
  - `2026-03-21_0023_strategy-review.md`
  - `2026-03-20_2343_strategy-review.md`
  - `2026-03-20_2302_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮运行中
  - `bot3-momentum-auto-opt-13m`：enabled
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 当前 EMA due 守门
已核对最新 `require-due` 结果与 `ema_paper_trading_due_guardrail_snapshot.csv`：
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 仍是：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前状态：`waiting_not_due`
- 距下一次真实 completed bar：约 `23.8h`
- 结论：`Paper Seat` 依然是 **被 market clock 合法阻塞**，不是执行停滞；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流

### Hosted narrow paper lanes 最新快照
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T00:57:33Z`
- 当前仍可见的 hosted open paper positions：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `new_closed_trades_appended = 0`

### memory 检索
- `memory_search` 本轮仍不可用（local embeddings unavailable / `node-llama-cpp` 缺失）
- 但本轮排兵布阵已由 repo 内最新日志、TODO 顶板、EMA 守门结果、manual narrow paper artifacts 与 cron 状态支撑，不影响当前判断

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍然是 clock-blocked，而不是 execution-blocked。**
   - EMA guardrail 明确仍无 `due-now / overdue`
   - 所以 bot3 现在最不该做的是伪 refresh 或空转
2. **最新真正具备边际价值的 Scout 主点是 `Rank 136`。**
   - `Rank 134`、`Rank 135` 都已在最小 clean replication 后给出足够明确的 `park`
   - `Rank 136` 刚完成 `source intake + honesty gate`
   - 下一步天然就是 `1` 次最小 clean replication，而不是再写 intake 近义描述
3. **Hosted `P3` continuity 继续由专属 cron 托管，不应抢 bot3 主资源。**
   - 00:57 UTC refresh 下 open positions 仍只剩 `Rank 17` 两腿
   - 没有新的 closed-trade append、异常 open position 或 overdue refresh 事件
4. **今日 bot3 的 `P3 continuity` 预算并未被消耗。**
   - 00:00 之后的 bot3 记录都落在 `Rank 134 -> Rank 135 -> Rank 136` 的 fresh Scout 链路
   - 没有把 bot3 主资源挪去 hosted `P3` continuity

---

## 2. 当前 weakest / should-not-overweight 的线
1. **旧 `P1 / budget-used`：`Rank 127 / 125 / 112 / 111`**
   - 它们仍可保留在比较表里，但当前更像证据池，不像最该继续消耗主资源的对象
2. **任何把 hosted `P3` continuity 重写成 Scout 主点的读法**
   - 现在没有新的 status-changing event
   - narrow-paper cron 已在正常托管
3. **任何为了“桌上必须有 live challenger”而硬填 `Live Seat` 的动作**
   - 当前没有 `P2` 候选
   - `Rank 136` 也还没过 clean replication

---

## 3. 本轮必须回答的 5 个问题
### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d (active_primary)`。**

#### EMA family lanes
- `创业板ETF 1d`（`active_primary`）
- `Crypto 1d+1wk（BTC/ETH/SOL）`（`active_secondary_backstop`，当前最靠前、但仍 `waiting_not_due`）
- `美股 1d+1wk（SPY/QQQ/AAPL）`（`active_secondary_backstop`）
- `贵州茅台 1d+1wk`（`active_secondary_backstop`）
- `沪深300ETF 1d`（`shadow_watch`）

#### Hosted paper continuity lanes
- 顶板口径继续是：`Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前由 narrow-paper cron 托管、仍在跑的 hosted narrow paper lanes 为：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 最新 00:57 UTC refresh 下，真有 open paper position 的仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`

一句话：**Paper Seat 还是 EMA；hosted paper continuity 继续跑，但当前真有 open paper position 的仍只有 Rank 17。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有 `P2` 候选
- `Rank 136` 还只到 `P1 / guard-passed / clean replication next`
- `Rank 127 / 125 / 112 / 111` 都是旧 `P1 / budget used`
- hosted `P3` lanes 是 paper continuity，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 136 / phase-wide RSI memory retest gate`**
  - 当前阶段：`source intake done / honesty gate passed / clean replication next`
  - 来源：`research/quant_digests/2026-03-21_0041_phase-wide-rsi-memory-retest-gate.md`
  - 角色：给 breakout-short / Fib retest_hold / EMA-PSAR continuation 提供一个 phase-level RSI memory gate，而不是另起新主策略

#### 当前仍在 active comparison、但不该抢主资源的旧 P1
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 已退出 active Scout 主位的最近候选
- `Rank 135 / retest tolerance stop decoupling gate`
  - 已完成 `source intake + honesty gate + 最小 clean replication`
  - 当前结论：`park / evidence pool`
- `Rank 134 / cross-market intraday TSMOM lead-lag gate`
  - 已完成 `source intake + honesty gate + 最小 clean replication`
  - 当前结论：`park / evidence pool`

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 136`：`P1（source intake done / guard-passed / clean replication next）`
- `Rank 127`：`P1（weak candidate / budget used / evidence_pool）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
- `Rank 135`：`P0（park / clean replication completed / single-pocket dependency）`
- `Rank 134`：`P0（park / clean replication completed / failed honest breadth）`
- `Rank 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 122`：`P3（strict-only / paper-only / hosted continuity）`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3（hosted narrow paper lanes / continuity only）`

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍 `waiting_not_due`，立即切走，不得空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 136 / phase-wide RSI memory retest gate` 的最小 clean replication**
   - 固定 `BTC/ETH/SOL`、`15m`、`next-bar open`、`no-overlap`、`6/10/15bps`
   - 只比较 `baseline` vs `phase-wide RSI memory gate`
   - 直接输出 `keep_P1 / promote_P2 / park`

3. **Run 3 = 条件分支，但默认仍先服务 Rank 136 verdict**
   - 若 `Rank 136` replication 通过：只补 **1 个** 真正会改变 verdict 的最小检查（优先 `时间稳定性` 或 `成本/交易数稳定性`），再决定是否升到 `P2`
   - 若 `Rank 136` replication 不通过：立即回下一条 fresh intake
   - 只有 fresh intake 也真实 exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback

---

## 4. Active Scout 边际价值比较
### 为什么当前主资源仍该给 `Rank 136`
- 它是**唯一**刚完成 `source intake + honesty gate`、且还没消耗 clean replication 预算的 fresh Scout
- 它直接服务三条当前主线，而不是另开大框架
- 下一步问题定义清楚、预算清楚、输出口径也清楚

### 为什么不是继续磨旧 `P1`
- `Rank 127 / 125 / 112 / 111` 都已经接近“再磨 mostly 是补说明”的区间
- 当前没有新的 cheap honest check 能明显改变它们级别

### 为什么不是回 P3 continuity
- 00:57 UTC hosted refresh 没有产生新的 status-changing event
- narrow-paper 已有独立 cron
- 今日 bot3 也尚未动用 `P3 continuity` 预算，没有必要回流

### 本轮推荐动作
- `recommended_action = keep Rank 136 as active Scout head`
- `why_now = fresh guard-passed + 直接服务 desk 当前三条主线 + 下一步 clean replication 最具边际价值`
- `main_weakness = 还没过 clean replication，不能提前升格到 P2 或 Live Seat`

---

## 5. TODO / 网页 / cron 的改动或建议
### TODO 顶板
**本轮只做了 1 个最小必要更新：**
- 将 `Hosted P3 快照` 的最新 refresh 时间从旧值更新到：`2026-03-21 00:57 UTC`
- 不改席位判断，不改 `Next 3 bot3 runs`

### 网页 / 首页
- 仍按要求刷新首页 index
- 当前属于**无席位变化巡检**；不额外改其他 reader-facing 页面

### cron / 节奏
**不改。**
- `bot2 40m / bot3 13m / narrow-paper 20m / bot6 2h / bot7 30m / rank32b live maintenance` 的当前分工仍合理
- 当前没有证据表明需要把 hosted `P3` 抢回 bot3 主循环

---

## 6. 建议优先级 Top 1~3
1. **继续保持 `Run 1 = EMA require-due precheck`，但一旦仍 not due，立刻切走**
2. **把 bot3 主资源给 `Rank 136` 的最小 clean replication，不要被旧 `P1` 或 hosted `P3` 分散**
3. **若 `Rank 136` 过最小 replication，就只再给 1 个 verdict-changing 检查；若不过，立即回 fresh intake，不要卡在模糊研究态**

---

## 7. 风险与不确定性
1. **memory_search 仍不可用**；本轮已如实记录。
2. **工作区脏文件很多**，继续不适合做安全 selective commit。
3. `Rank 136` 目前仍只完成 intake 与 honesty gate；真正是否值得升到 `P2`，要看下一轮最小 clean replication 是否给出足够诚实的跨 setup / 跨资产结果。

---

## authoritative one-liner
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 136 / phase-wide RSI memory retest gate`；hosted paper continuity 继续由 `122 / 2 / 17 / 29 / 32b` 托管，当前 open paper positions 仍只剩 `Rank 17 / ETH long + SOL short`；接下来 bot3 仍应按 `EMA due-check -> Rank 136 clean replication -> Rank 136 最小 verdict-changing follow-up / 否则 fresh intake` 排。