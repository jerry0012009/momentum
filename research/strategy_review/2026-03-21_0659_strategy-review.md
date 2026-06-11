# 2026-03-21 06:59 UTC strategy review

## 本轮一句话判断
当前 desk 仍应明确写成：**`Paper Seat = EMA / 创业板ETF 1d（active_primary）/ waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 127 / signal→confirm ATR delta phase gate（最后 1 次便宜诚实检查）`**；同时把新的 fresh intake reserve 明确收紧为 **`Rank 139 / CUSUM event-bar confirm-veto gate`**。`Rank 138` 已 park，hosted `P3` 继续只是托管 continuity，不该抢 bot3 主资源位。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2268`
- 最近 optimization logs：
  - `2026-03-21_0636_rank138-clean-replication-park.md`
  - `2026-03-21_0444_rank138-source-intake.md`
  - `2026-03-21_0429_rank137-time-stability-park.md`
  - `2026-03-21_0208_rank137-clean-replication-keep-p1.md`
  - `2026-03-21_0151_rank137-state-expiry-intake.md`
- 最近 strategy reviews：
  - `2026-03-21_0435_strategy-review.md`
  - `2026-03-21_0158_strategy-review.md`
  - `2026-03-21_0112_strategy-review.md`
  - `2026-03-21_0023_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 当前运行中
  - `bot3-momentum-auto-opt-13m`：enabled / 最近成功
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 当前运行中
  - `bot7-quant-digest-30m`：enabled / 当前运行中，但最近状态带 timeout/error 痕迹
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
- 距下一次真实 completed bar：约 `17.0h`
- 结论：`Paper Seat` 继续是**被 market clock 合法阻塞**，不是执行停滞；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流

### Hosted narrow paper lanes 最新快照
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T06:40:12Z`
- 当前真正挂在 `20m refresh` 上跑的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `new_closed_trades_appended = 0`
- `Rank 122` 仍是 `P3 / strict-only short-side re-arm`，但**不在当前 running hosted refresh lane 集合里**，更准确读法仍是 `strict-only / low-frequency monitoring only`

### fresh intake / active Scout 池（本轮重新比较边际价值）
已核对：
- `research/optimization_loop/2026-03-20_1957_rank127-clean-replication.md`
- `research/optimization_loop/2026-03-20_1636_rank125-cost-trade-stability.md`
- `research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`
- `research/quant_digests/INDEX.md`
- `docs/RECENT_PAPER_SEEDS.md`

结论：
- `Rank 127` 仍是**当前边际价值最高**的 active Scout，因为它只剩 **1 次便宜诚实检查** 就能在 `keep_P1 / promote_P2 / park` 中给硬结论。
- 一旦 `Rank 127` 本轮预算用完，下一条默认不该回头磨 `Rank 125 / 112 / 111`；应优先切到新鲜、paper/repo-based 的 **`CUSUM event-bar confirm-veto gate`**。
- 因此本轮把新 digest 认领成 **`Rank 139 / source intake reserve`**，但还**没有**让它越过 `Rank 127` 抢当前主资源位。

### memory 检索
- 已执行 `memory_search`
- 返回的更多是更早的 desk / deployment 上下文；本轮当前席位判断仍主要由 repo 内最新 `TODO`、最近 optimization / strategy review、EMA due-check、hosted paper artifacts 与新 digest 证据支撑

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍然是 clock-blocked，不是 execution-blocked。**
   - `require-due` 实跑再次确认：没有 `due-now / overdue`
   - 所以 bot3 最不该做的是伪 refresh，或回流 hosted `P3 continuity`
2. **`Rank 138` 已经给出足够硬的 clean replication 裁决：`park`。**
   - 最优接法 `veto_p90` 也只留下极小 uplift，且 `positive_asset_ratio=33.33%`
   - 这条线继续给预算，边际价值已经不如新的 fresh source
3. **`Rank 127` 仍有最后 1 次便宜诚实检查的价值。**
   - 它当前不是空故事，但也没硬到能直接升 `P2`
   - 正适合拿 1 次最小检查，逼出 `升格 / park / 切资源`
4. **新的 `CUSUM event-bar confirm-veto gate` 已足够成为具体 fresh intake reserve。**
   - 它直接服务 breakout-short / Fib / EMA-PSAR 共同缺的 `event-confirm / veto` 层
   - 比继续磨 `Rank 125 / 112 / 111` 更有新鲜度和边际价值
5. **hosted `P3` 继续只是托管层，不是新主位。**
   - 06:40 UTC refresh 仍无 `closed-trade append`
   - open paper position 仍只有 `Rank 17` 两腿
   - `Rank 122` 也只是 strict-only sidecar，不应误写成 running hosted lane

---

## 2. 当前 weakest / should-not-overweight 的线
1. **旧 `P1 / budget-used`：`Rank 125 / 112 / 111`**
   - 继续磨它们，当前边际价值明显低于 `Rank 127` 的最后裁决检查，以及新的 `Rank 139` fresh intake
2. **把 hosted `P3` continuity 重新当 bot3 主资源位的读法**
   - 当前没有新的 `status-changing event`
   - narrow-paper 已有独立 `20m refresh` cron
3. **为了填满 `Live Seat` 而强行升格候选**
   - 当前没有足够硬的 `P2` 或 `P4` 候选
   - `Live Seat` 继续暂空是正确读法
4. **把 bot7 的新 digest 直接误写成“已验证候选”**
   - `Rank 139` 目前仍只是 digest 级新 source
   - 还必须先过 `source intake + 两条轻量诚实守门`

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

#### 当前 running hosted paper lanes
- 真正挂在当前 `20m refresh` 上跑的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `Rank 122` 仍可算 `P3 hosted sidecar`，但它**不在当前 running hosted refresh lane 集合里**，当前更准确的读法是：`strict-only / low-frequency monitoring only`

一句话：**Paper Seat 还是 EMA；running hosted paper lanes 当前是 `2 / 17 / 29 / 32b`，open paper positions 仍只剩 `Rank 17` 两腿；`Rank 122` 继续只是 `P3 strict-only sidecar`。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有已经过完 fast-screen 的 `P2/P4` 候选
- `Rank 138` 已经转去 `P0 / park`
- `Rank 127` 仍停在 `P1 / 最后 1 次便宜诚实检查`
- 新的 `Rank 139` 还只是 `source intake reserve`
- hosted `P3` lanes 是 paper continuity / sidecar，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 127 / signal→confirm ATR delta phase gate`**
  - 当前阶段：`P1 / 最后 1 次便宜诚实检查`
  - 当前最该做：`优先时间稳定性`，做完直接给 `keep_P1 / promote_P2 / park`

#### 当前 fresh intake reserve
- **`Rank 139 / CUSUM event-bar confirm-veto gate`**
  - 当前阶段：`P1（source intake reserve）`
  - 来源：`research/quant_digests/2026-03-21_0652_cusum-event-bar-confirm-veto-gate.md`
  - 角色：更像 breakout-short / Fib / EMA-PSAR 共用的 `event-confirm / veto` 层，而不是新主 alpha

#### 当前仍在 active comparison、但不该抢主资源的旧 P1
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 127`：`P1（weak candidate / 最后 1 次便宜诚实检查）`
- `Rank 139`：`P1（fresh paper candidate / source intake reserve）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
- `Rank 138`：`P0（park / minimal clean replication completed / single-pocket dependency）`
- `Rank 137`：`P0（park / minimal time-stability verdict completed / single-pocket dependency + post-cost collapse）`
- `Rank 136 / 135 / 134 / 133 / 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3（hosted narrow paper lanes / 20m refresh running / continuity only）`
- `Rank 122`：`P3（strict-only / hosted sidecar / low-frequency monitoring only）`

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍 `waiting_not_due`，立即切走，不得空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 127` 的最后 1 次便宜诚实检查（优先时间稳定性）**
   - 直接输出：`keep_P1 / promote_P2 / park`
   - 不再继续 admission wording / operator packet / closeout docs 回环

3. **Run 3 = 条件分支，但仍先服务 Scout Seat**
   - 若 `Rank 127` 这次检查后仍只是 `keep_P1` 或直接 `park`：切 **`Rank 139 / CUSUM event-bar confirm-veto gate`** 的 `source intake + 两条轻量诚实守门`
   - 若 `Rank 127` 意外足够升到 `P2`：只再给 **1 个真正会改变是否升 `P3` 的最小检查**（默认优先跨时间 / 跨标的稳定性其一）
   - 只有 `Rank 127` 与 `Rank 139` 都真实 exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback

---

## 4. Active Scout 边际价值比较
### 为什么当前主资源仍该给 `Rank 127`
- 它已经过了 intake 与 clean replication，当前只差 **1 个便宜、但真正会改变级别的检查**
- 这正符合 `P1` 的预算上限：做完就该 `升格 / park / 切资源`
- 相比 fresh intake，它更接近硬 verdict

### 为什么 `Rank 139` 是 next reserve，而不是直接越位
- 它现在还只是 digest 级新 source
- 但它比 `Rank 125 / 112 / 111` 更新鲜，也更贴近三条主线共同缺的 `event-confirm` 需求
- 因此它已经值得进板、拿顺序 `Rank 139`，但还不该跳过 `Rank 127` 当前最后这手裁决

### 为什么不是继续磨旧 `P1`
- `Rank 125 / 112 / 111` 都已经进入“继续磨 mostly 是补说明”的区间
- 当前没有比 `Rank 127` 更接近 verdict-changing 的检查
- 也没有比 `Rank 139` 更值得 fresh intake 的新鲜度

### 为什么不是回 P3 continuity
- 06:40 UTC hosted refresh 没有新的 status-changing event
- narrow-paper 已有独立 cron
- `Rank 122` 也只是 strict-only sidecar，不是 running hosted lane 主位

### 本轮推荐动作
- `recommended_action_1 = keep Rank 127 as current Scout Seat head for one last cheap honesty check`
- `recommended_action_2 = enroll CUSUM digest as Rank 139 source-intake reserve`
- `why_now = EMA 仍 waiting_not_due + Rank 138 已 park + stale P1 边际价值继续下降`

---

## 5. TODO / roadmap / web / cron 的改动或建议
### TODO 顶板
**本轮做了最小必要更新：**
1. 把 `TRADING DESK BOARD` 的 authoritative 日期更新到 `2026-03-21`
2. 把 hosted `P3` 快照刷新到 `2026-03-21 06:40 UTC`
3. 把新的 fresh digest 收紧成 **`Rank 139 / CUSUM event-bar confirm-veto gate`**，并写进 active Scout 排序
4. 把 `Next 3 bot3 runs` 从模糊的 `Rank 125 / fresh intake` 分支，收紧成：
   - `Run 1 = EMA due-check`
   - `Run 2 = Rank 127 最后 1 次便宜诚实检查`
   - `Run 3 = 若 Rank 127 不升格，则切 Rank 139 source intake`

### 网页 / 首页
- `docs/TODO.md` 已作为 reader-facing 落点同步更新
- 之后按要求刷新首页 index

### cron / 节奏
**不改。**
- 当前 `bot2 40m / bot3 13m / narrow-paper 20m / bot6 2h / bot7 30m / rank32b live maintenance` 的大分工仍合理
- 但 `bot7` 当前有 timeout/error 痕迹，后续若继续影响新 digest 产出稳定性，再单独处理；本轮先不抢主线

---

## 6. 建议优先级 Top 1~3
1. **继续保持 `Run 1 = EMA require-due precheck`，但一旦仍 not due，立刻切走**
2. **把 bot3 当前主资源给 `Rank 127` 的最后 1 次便宜诚实检查，逼出硬 verdict**
3. **若 `Rank 127` 预算用尽仍未升格，下一轮直接认领 `Rank 139`，不要再回头磨 `Rank 125 / 112 / 111`**

---

## 7. 风险与不确定性
1. **工作区脏文件很多**，继续不适合做安全 selective commit。
2. `Rank 127` 这次最终检查很可能只是把它压回 `keep_P1` 或直接 `park`；若如此必须真的切资源，不能继续磨。
3. `Rank 139` 目前还只是 digest 级 fresh source；是否值得留下，要看 source intake 能否把规则冻结成清楚的 `trade on / trade off`，并排除明显数据泄漏。
4. `bot7` 当前 cron 状态有 timeout/error 痕迹；虽然这次新 digest 已经足够好用，但其稳定性值得后续留意。

---

## authoritative one-liner
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 127（最后 1 次便宜诚实检查）`；当前 running hosted paper lanes 是 `Rank 2 / 17 / 29 / 32b`，open paper positions 仍只剩 `Rank 17 / ETH long + SOL short`；`Rank 139 / CUSUM event-bar confirm-veto gate` 已作为 fresh intake reserve 入板，因此接下来 bot3 应按 `EMA due-check -> Rank 127 最后 cheap check -> 若不升格则切 Rank 139 source intake` 排。