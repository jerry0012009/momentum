# 2026-03-21 01:58 UTC strategy review

## 本轮一句话判断
当前 desk 继续维持：**`Paper Seat = EMA / 创业板ETF 1d (active_primary) / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 137 / state expiry latency budget gate`**。本轮没有出现足以改写席位的新证据；但为了让 bot3 排班更符合当前 brief，我对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了两处最小必要校准：
1. 把 `Hosted P3` 快照时间更新到 **`2026-03-21 01:26 UTC`**；
2. 把 `Run 3` 收紧成：**`Rank 137` 若 hard-fail，先回 fresh intake；只有 fresh intake 也 exhausted，才允许切 tiny-live fallback**。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2236`
- 最近 optimization logs：
  - `2026-03-21_0151_rank137-state-expiry-intake.md`
  - `2026-03-21_0121_rank136-clean-replication-park.md`
  - `2026-03-21_0059_rank136-phase-rsi-memory-intake.md`
  - `2026-03-21_0054_rank135-clean-replication-park.md`
  - `2026-03-21_0027_rank135-retest-tolerance-stop-decoupling-intake.md`
- 最近 strategy reviews：
  - `2026-03-21_0112_strategy-review.md`
  - `2026-03-21_0023_strategy-review.md`
  - `2026-03-20_2343_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮运行中
  - `bot3-momentum-auto-opt-13m`：enabled
  - `momentum-narrow-paper-lanes-20m`：enabled / 运行中
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 当前 EMA due 守门（本轮实跑）
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 仍是：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前状态：`waiting_not_due`
- 距下一次真实 completed bar：约 `22.1h`
- 结论：`Paper Seat` 仍然是**被 market clock 合法阻塞**，不是执行停滞；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流

### Hosted narrow paper lanes 最新快照
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T01:26:31Z`
- `sample_end_utc = 2026-03-21T01:00:00Z`
- 当前仍在托管的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前可见 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `new_closed_trades_appended = 0`

### memory 检索
- 已执行 `memory_search`
- 返回的是更早的 desk / deployment 上下文片段；本轮当前排班判断仍主要由 repo 内最新 `TODO`、optimization logs、strategy reviews、EMA due-check 与 hosted paper artifacts 支撑

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍然是 clock-blocked，不是 execution-blocked。**
   - `require-due` 实跑再次确认：没有 `due-now / overdue`
   - 所以 bot3 当前最不该做的是伪 refresh 或把 `waiting_not_due` 误读成整个 desk 需要等待
2. **当前边际价值最高的 Scout 主点仍是 `Rank 137`。**
   - `Rank 137` 刚完成 `source intake + honesty gate`
   - 下一步问题定义清楚：只给 `1` 次最小 clean replication
   - 相比之下，`Rank 127 / 125 / 112 / 111` 都更像旧 `P1 / budget used / evidence_pool`
3. **Hosted `P3` continuity 正在被专属 cron 正常托管，不应抢 bot3 主资源。**
   - 01:26 UTC refresh 仍无 `closed-trade append`
   - open paper positions 仍只剩 `Rank 17` 两腿
   - 因此它们继续只是 `P3 continuity / sidecar`，不是新的 seat

---

## 2. 当前 weakest / should-not-overweight 的线
1. **旧 `P1 / budget-used`：`Rank 127 / 125 / 112 / 111`**
   - 当前没有新的 cheapest honest check 能明显改变其级别
   - 继续磨它们，边际价值低于把 `Rank 137` 快速做出 `park / promote_P2`
2. **任何把 hosted `P3` continuity 重新当作 bot3 主资源位的读法**
   - narrow-paper 专属 cron 正常跑
   - 本轮没有新的 status-changing event
3. **任何为了填 `Live Seat` 而强行升格候选的动作**
   - 当前没有 `P2` 候选
   - `Rank 137` 还没过 clean replication，不能提前抢 `Live Seat`

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
- 当前由 narrow-paper cron 托管、仍在跑的 hosted narrow paper lanes：`Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 最新 `01:26 UTC` refresh 下，真有 open paper position 的仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`

一句话：**Paper Seat 还是 EMA；hosted paper continuity 继续跑，但当前真有 open paper position 的仍只有 Rank 17。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有 `P2` 候选
- `Rank 137` 仍只到 `P1 / source intake done / guard-passed / clean replication next`
- `Rank 127 / 125 / 112 / 111` 都是旧 `P1 / budget used`
- hosted `P3` lanes 是 paper continuity，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 137 / state expiry latency budget gate`**
  - 当前阶段：`source intake done / guard-passed / clean replication next`
  - 来源：`research/quant_digests/2026-03-21_0145_state-expiry-latency-budget-gate.md`
  - 角色：不是新主策略，而是给 breakout-short / Fib retest_hold / EMA-PSAR 补一个更诚实的确认层时间预算 gate

#### 当前仍在 active comparison、但不该抢主资源的旧 P1
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 最近已退出 active Scout 主位的候选
- `Rank 136 / phase-wide RSI memory retest gate`
  - 已完成 `source intake + honesty gate + 最小 clean replication`
  - 当前结论：`park / evidence pool`
- `Rank 135 / retest tolerance stop decoupling gate`
  - 已完成 `source intake + honesty gate + 最小 clean replication`
  - 当前结论：`park / evidence pool`

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 137`：`P1（source intake done / guard-passed / clean replication next）`
- `Rank 127`：`P1（weak candidate / budget used / evidence_pool）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
- `Rank 136`：`P0（park / clean replication completed / too_sparse + single-pocket dependency）`
- `Rank 135`：`P0（park / clean replication completed / single-pocket dependency）`
- `Rank 134 / 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
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

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，执行 `Rank 137` 的最小 clean replication**
   - 只比较 `无 expiry / confirmWindow / confirmWindow + entryWindow` 三臂
   - 固定 `BTC/ETH/SOL`、`15m`、`next-bar open`、`no-overlap`、`6/10/15bps`
   - 直接输出 `park / keep_P1 / promote_P2`

3. **Run 3 = 条件分支，但默认仍先服务 Scout Seat**
   - 若 `Rank 137` 通过最小 clean replication：只再给 **1 个** 真正会改变 verdict 的最小检查（优先 `时间稳定性` 或 `成本 / 交易数稳定性`），然后立刻决定 `promote_P2 / park`
   - 若 `Rank 137` hard-fail：先回下一条 `fresh intake`（仅限 `paper / repo based 5m/15m crypto`）
   - 只有 fresh intake 也真实 exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback

---

## 4. Active Scout 边际价值比较
### 为什么当前主资源仍该给 `Rank 137`
- 它是**唯一**刚完成 `source intake + honesty gate`、且还没消耗 clean replication 预算的 fresh Scout
- 它直接服务当前三条主线共同的确认层时间预算 honesty 问题
- 下一步问题定义清楚、预算清楚、输出口径也清楚

### 为什么不是继续磨旧 `P1`
- `Rank 127 / 125 / 112 / 111` 都已经进入“再磨 mostly 是补说明”的区间
- 当前没有新的 cheap honest check 能明显改变它们的级别

### 为什么不是回 P3 continuity
- 01:26 UTC hosted refresh 没有产生新的 status-changing event
- narrow-paper 已有独立 cron
- 当前更该把 bot3 主资源继续压在 `Rank 137 -> hard verdict`

### 本轮推荐动作
- `recommended_action = keep Rank 137 as active Scout head`
- `why_now = fresh guard-passed + 直接服务三条主线 + 下一步 clean replication 最具边际价值`
- `main_weakness = 还没过 clean replication，不能提前升格到 P2 或 Live Seat`

---

## 5. TODO / 网页 / cron 的改动或建议
### TODO 顶板
**本轮做了 2 个最小必要更新：**
1. `Hosted P3 快照` 的 latest refresh 时间更新为：`2026-03-21 01:26 UTC`
2. `Next 3 bot3 runs / Run 3` 收紧为：
   - `Rank 137` hard-fail 后先回 `fresh intake`
   - 只有 fresh intake 也 exhausted，才允许 tiny-live fallback

### 网页 / 首页
- 按要求刷新首页 index
- 当前属于**轻微 reader-facing judgment 校准**，`TODO` 顶板已作为网页可见落点同步更新

### cron / 节奏
**不改。**
- `bot2 40m / bot3 13m / narrow-paper 20m / bot6 2h / bot7 30m / rank32b live maintenance` 的当前分工仍合理
- 当前没有证据表明需要把 hosted `P3` 抢回 bot3 主循环

---

## 6. 建议优先级 Top 1~3
1. **继续保持 `Run 1 = EMA require-due precheck`，但一旦仍 not due，立刻切走**
2. **把 bot3 主资源给 `Rank 137` 的最小 clean replication，不要被旧 `P1` 或 hosted `P3` 分散**
3. **若 `Rank 137` 不通过，就立即回 fresh intake；不要过早掉到 tiny-live fallback**

---

## 7. 风险与不确定性
1. **工作区脏文件很多**，继续不适合做安全 selective commit。
2. `Rank 137` 目前仍只完成 intake 与 honesty gate；是否值得升到 `P2`，要看下一轮最小 clean replication 是否给出足够诚实的跨 setup / 跨资产结果。
3. narrow-paper 01:26 UTC refresh 仍无新的 closed-trade append；因此当前对 hosted `P3` 的判断继续只是“托管正常”，不是新的升格信号。

---

## authoritative one-liner
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 137 / state expiry latency budget gate`；hosted paper continuity 继续由 `122 / 2 / 17 / 29 / 32b` 托管，当前 open paper positions 仍只剩 `Rank 17 / ETH long + SOL short`；接下来 bot3 仍应按 `EMA due-check -> Rank 137 clean replication -> Rank 137 最小 verdict-changing follow-up / 若 hard-fail 则 fresh intake next` 排。
