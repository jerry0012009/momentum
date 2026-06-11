# 2026-03-21 04:35 UTC strategy review

## 本轮一句话判断
当前 desk 应明确写成：**`Paper Seat = EMA / 创业板ETF 1d（active_primary）/ waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 138 / funding × OI cross-symbol crowding breadth overlay（source intake next）`**。`Rank 137` 已在最小时间稳定性裁决后正式 `park`，而 hosted `P3` 继续只有 sidecar 意义，不该回头抢 bot3 主资源位。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2255`
- 最近 optimization logs：
  - `2026-03-21_0429_rank137-time-stability-park.md`
  - `2026-03-21_0208_rank137-clean-replication-keep-p1.md`
  - `2026-03-21_0151_rank137-state-expiry-intake.md`
- 最近 strategy reviews：
  - `2026-03-21_0158_strategy-review.md`
  - `2026-03-21_0112_strategy-review.md`
  - `2026-03-21_0023_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 当前运行中
  - `bot3-momentum-auto-opt-13m`：enabled
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 当前运行中
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
- 距下一次真实 completed bar：约 `19.4h`
- 结论：`Paper Seat` 继续是**被 market clock 合法阻塞**，不是执行停滞；因此 bot3 仍必须按 `Scout Seat > tiny-live plumbing > 其他维护` 导流

### Hosted narrow paper lanes 最新快照
已核对：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/summary.json`
- `reports/artifacts/scout_rank122_atr_roc_short_rearm_15m/narrow_paper_monitoring_board.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T04:32:38Z`
- 当前真正挂在 `20m refresh` 上跑的 hosted narrow paper lanes：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前 open paper positions 仍只有：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`
- `new_closed_trades_appended = 0`
- `Rank 122` 仍是 `P3 / strict-only short-side re-arm`，但**不是**当前 `20m refresh` 的 running lane，更像 low-frequency sidecar / paper-only monitoring

### fresh intake 候选池（本轮做了边际价值比较）
已核对：
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
- `docs/PARK_REFRAME_QUEUE.md`
- 最近 3 条可立即接手的 digest：
  - `2026-03-21_0302_funding-oi-crowding-breadth-overlay.md`
  - `2026-03-21_0246_closedbar-htf-context-honesty-gate.md`
  - `2026-03-21_0221_polymarket-implied-prob-breadth-risk-overlay.md`

### memory 检索
- 已执行 `memory_search`
- 返回的更多是更早的 desk / deployment 上下文；本轮当前席位判断仍主要由 repo 内最新 `TODO`、strategy review、optimization logs、EMA due-check 与 hosted paper artifacts 支撑

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍然是 clock-blocked，不是 execution-blocked。**
   - `require-due` 实跑再次确认：没有 `due-now / overdue`
   - 所以 bot3 现在最不该做的是伪 refresh 或回流 `P3 continuity`
2. **`Rank 137` 已经完成该给的最后一手最小裁决，结论足够硬：`park`。**
   - `confirm_window_12` 只在 `mid` 时间桶为正；`early / late` 继续为负
   - 这已经回答了“该不该继续给预算”
3. **当前边际价值最高的 fresh Scout 不再是旧 `P1`，而是 `funding × OI cross-symbol crowding breadth` 这条新 repo/docs source。**
   - 它直接服务三条主线共同缺的 shared size/veto overlay
   - 它的数据获取 cheap、规则口径清楚、source 不需要额外搜索 API
4. **hosted `P3` 继续只是托管层，不是新主位。**
   - 04:32 UTC refresh 仍无 `closed-trade append`
   - 当前 open paper position 仍只有 `Rank 17` 两腿
   - `Rank 122` 也只是 strict-only sidecar，不应被误写成“当前 running hosted lane”

---

## 2. 当前 weakest / should-not-overweight 的线
1. **旧 `P1 / budget-used`：`Rank 127 / 125 / 112 / 111`**
   - 继续磨它们，边际价值仍低于认领新的 repo/docs fresh source
2. **把 hosted `P3` continuity 重新当 bot3 主资源位的读法**
   - 当前没有新的 `status-changing event`
   - 20m narrow-paper cron 正常跑着
3. **任何为了填 `Live Seat` 而强行升格候选的动作**
   - 当前没有 `P2` 候选
   - 新认领的 `Rank 138` 也还没过 source intake，更不该抢 `Live Seat`
4. **把 `closed-bar HTF context honesty gate` 当作下一条默认主线**
   - 它重要，但更像研究诚实性修复方法，不是当前最优先的新 Scout 主位
5. **把 Polymarket 低频外部数据放到 fresh-intake 第一优先**
   - 它能做 overlay，但当前不如 `funding × OI breadth` 便宜、直连、工程口径更稳定

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
- `Rank 122` 仍可算 `P3 hosted sidecar`，但它**不在当前 running hosted refresh lane 集合里**，当前更准确的读法是：`strict-only / low-frequency monitoring only`

一句话：**Paper Seat 还是 EMA；running hosted paper lanes 当前是 `2 / 17 / 29 / 32b`，open position 仍只剩 `Rank 17` 两腿；`Rank 122` 继续只是 P3 strict-only sidecar。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有 `P2` 候选
- `Rank 137` 已经转去 `P0 / park`
- 新的 `Rank 138` 还只是 `source intake next`
- hosted `P3` lanes 是 paper continuity / sidecar，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 138 / funding × OI cross-symbol crowding breadth overlay`**
  - 当前阶段：`source intake next`
  - 来源：`research/quant_digests/2026-03-21_0302_funding-oi-crowding-breadth-overlay.md`
  - 角色：不是发明新大框架，而是给 breakout-short / Fib retest_hold / EMA-PSAR 补一个更诚实、公开数据可拿的 shared `size/veto overlay`

#### 当前仍在 active comparison、但不该抢主资源的旧 P1
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 当前不作为默认主资源的其他 fresh 候选
- `closed-bar HTF context honesty gate`
  - 更像方法学 honesty fix，不是当前第一优先新 Scout 主位
- `Polymarket implied-probability breadth risk overlay`
  - 能做 overlay，但数据频率与工程成本不如 `funding × OI breadth` 直接

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 138`：`P1（source intake next / repo+docs based / shared size-veto overlay 候选）`
- `Rank 127`：`P1（weak candidate / budget used / evidence_pool）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
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

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 138 / funding × OI crowding breadth overlay` 的 source intake**
   - 只做 `trade on / trade off` + `no leakage` 两条轻量诚实守门
   - 不偷带第二层 regime stack，不碰 live，不回旧 `P1`
   - 直接输出：`guard-pass / hard-fail / exhausted`

3. **Run 3 = 条件分支，但仍先服务 Scout Seat**
   - 若 `Rank 138` guard-pass：只再给 **1 个** 最小 clean replication
   - 若 `Rank 138` hard-fail：先回 fresh intake shortlist（仍限 `paper / repo based 5m/15m crypto`）
   - 只有 `Rank 138` hard-fail 且 fresh intake 也真实 exhausted，才允许切 `fixed partial → R/ATR partial` 的 tiny-live fallback

---

## 4. Active Scout 边际价值比较
### 为什么当前主资源该给 `Rank 138`
- 它是**唯一**刚有新鲜 digest、且无需额外 web-search 就能直接开工的 repo/docs fresh source
- 它直接服务当前三条主线共同缺的 `size/veto overlay`
- 规则清楚：`funding sign × OIΔ breadth`，不是含糊的“大环境感觉”
- 数据拿取便宜、适合 source intake → clean replication 快速推进

### 为什么不是继续磨旧 `P1`
- `Rank 127 / 125 / 112 / 111` 都已经进入“再磨 mostly 是补说明”的区间
- 当前没有新的 cheap honest check 能明显改变它们级别

### 为什么不是回 P3 continuity
- 04:32 UTC hosted refresh 没有新的 status-changing event
- narrow-paper 已有独立 cron
- `Rank 122` 也只是 strict-only sidecar，不是 running hosted lane 主位

### 为什么 `Rank 138` 优先于另外两条 fresh source
- **优先于 `closed-bar HTF context honesty gate`**：后者重要但更像方法学修复，不是当前最该抢 bot3 主资源位的新 Scout 候选
- **优先于 `Polymarket implied-probability breadth`**：后者频率更低、映射更间接；当前 `funding × OI breadth` 更接近 crypto 交易台同频素材，且实现更便宜

### 本轮推荐动作
- `recommended_action = promote Rank 138 into source-intake head`
- `why_now = Rank 137 已 park + EMA 仍 waiting_not_due + Rank 138 对三条主线的共享边际价值最高`
- `main_weakness = 它目前还只是 digest 级 fresh source，尚未过 source intake / honesty gate`

---

## 5. TODO / 网页 / cron 的改动或建议
### TODO 顶板
**本轮做了最小必要更新：**
1. 把 `Scout Seat` 当前主点从 generic `fresh intake next` 收紧到：`Rank 138 / funding × OI cross-symbol crowding breadth overlay`
2. 把 `Next 3 bot3 runs` 收紧成：
   - `Run 1 = EMA due-check`
   - `Run 2 = Rank 138 source intake`
   - `Run 3 = Rank 138 clean replication / 若 hard-fail 则 fresh intake fallback`
3. 把 `Hosted P3` 快照改正为：
   - 当前 running hosted narrow paper lanes = `Rank 2 / 17 / 29 / 32b`
   - `Rank 122` 单独记为 `P3 strict-only sidecar`
   - 最新 refresh 时间更新到 `2026-03-21 04:32 UTC`

### 网页 / 首页
- `docs/TODO.md` 已作为 reader-facing 落点同步更新
- 之后按要求刷新首页 index

### cron / 节奏
**不改。**
- 当前 `bot2 40m / bot3 13m / narrow-paper 20m / bot6 2h / bot7 30m / rank32b live maintenance` 的分工仍合理
- 当前没有证据表明需要把 hosted `P3` 抢回 bot3 主循环

---

## 6. 建议优先级 Top 1~3
1. **继续保持 `Run 1 = EMA require-due precheck`，但一旦仍 not due，立刻切走**
2. **把 bot3 主资源给 `Rank 138` 的 source intake，不要被旧 `P1` 或 hosted `P3` 分散**
3. **若 `Rank 138` guard-pass，就只再给 1 个最小 clean replication；若 hard-fail，立即回 fresh intake，不要跳回旧线或过早掉到 tiny-live fallback**

---

## 7. 风险与不确定性
1. **工作区脏文件很多**，继续不适合做安全 selective commit。
2. `Rank 138` 目前还只是 digest 级 fresh source；是否值得留下，要看 source intake 能否把规则冻结成清楚的 `trade on / trade off`，并排除明显数据泄漏。
3. 当前 narrow-paper 04:32 UTC refresh 没有新的 closed-trade append；因此对 hosted `P3` 的判断仍只是“托管正常”，不是新的升格信号。

---

## authoritative one-liner
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 138 / funding × OI cross-symbol crowding breadth overlay（source intake next）`；当前 running hosted paper lanes 是 `Rank 2 / 17 / 29 / 32b`，open paper positions 仍只剩 `Rank 17 / ETH long + SOL short`，而 `Rank 122` 只是 `P3 strict-only sidecar`；接下来 bot3 应按 `EMA due-check -> Rank 138 source intake -> Rank 138 最小 clean replication / 若 hard-fail 则 fresh intake fallback` 排。