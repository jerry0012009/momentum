# 2026-03-20 23:43 UTC strategy review

## 本轮一句话判断
当前 desk 继续维持：**`Paper Seat = EMA / 创业板ETF 1d active_primary / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 133 / triple barrier honest final-verdict layer`**。本轮没有出现足以改写席位的新证据；唯一需要做的最小板面刷新，是把 `Hosted P3` 快照时间更新到 `2026-03-20 23:36 UTC`，并把最新 `EMA require-due` 守门结果写回顶板证据区。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2188`
- 最近 optimization logs：
  - `2026-03-20_2332_rank133-source-intake.md`
  - `2026-03-20_2258_rank132-clean-replication-park.md`
  - `2026-03-20_2237_rank132-adaptive-exhaustion-intake.md`
  - `2026-03-20_2226_rank131-clean-replication-park.md`
  - `2026-03-20_2206_rank130-scorecard-backfill.md`
- 最近 strategy reviews：
  - `2026-03-20_2302_strategy-review.md`
  - `2026-03-20_2205_strategy-review.md`
  - `2026-03-20_2104_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮运行中
  - `bot3-momentum-auto-opt-13m`：enabled
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 当前板面 / 纸上账位 / EMA due 守门
已回读：
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`

并实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```

结果：
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 仍是：`Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前状态：`due_soon`
- `require-due` 守门继续成立：**现在仍不允许伪造 paper refresh**

manual narrow paper 最新可见快照：
- `run_at_utc = 2026-03-20T23:36:49Z`
- open positions 仍只剩：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 29` 继续 `flat / no open position`

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍是被 market clock 阻塞，不是执行失灵。**
   - `EMA require-due` 再次确认还没到真正该刷的 completed bar
   - 因此 bot3 仍必须遵守：`Scout Seat > tiny-live plumbing > 其他维护`
2. **最新真正值得给 bot3 主资源位的 Scout 还是 `Rank 133`。**
   - 它刚完成 `source intake + honesty gate`
   - 下一步天然就是 `1` 次最小 clean replication
3. **最近 fresh Scout 已连续给出 hard verdict。**
   - `Rank 132 / 131 / 130` 都已压回 `park`
   - 继续回头磨旧 `P1` 的边际价值更低
4. **hosted `P3` 仍只算 continuity / sidecar。**
   - 最新 open position 仍只剩 `Rank 17`
   - 没有新的 `status-changing event`，不应回流抢占 bot3 主资源位

---

## 2. 当前 weakest / should-not-overweight 的线
1. **`Rank 127 / 125 / 112 / 111`**
   - 仍在 `P1`，但都已属于 `budget used / evidence_pool`
   - 再投 bot3 主资源更像 admission write-back，而不是减少真实 gate
2. **任何把 hosted `P3` continuity 重写成“当前 Scout 主点”的读法**
   - 现在没有新的 due-now / overdue paper refresh
   - 也没有新的 hosted lane 异常或 closed-trade append 需要抢资源
3. **`fixed partial -> R/ATR partial`**
   - 仍只配当 `tiny-live / path-management` fallback
   - 不能挤掉 `Rank 133` 这样的 paper/repo Scout 主点

---

## 3. 本轮必须回答的 5 个问题
### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d (active_primary)`。**

#### EMA family lanes
- `创业板ETF 1d`（`active_primary`）
- `Crypto 1d+1wk（BTC/ETH/SOL）`（`active_secondary_backstop`，当前最靠前、但仍只是 `due_soon`）
- `美股 1d+1wk（SPY/QQQ/AAPL）`（`active_secondary_backstop`）
- `贵州茅台 1d+1wk`（`active_secondary_backstop`）
- `沪深300ETF 1d`（`shadow_watch`）

#### Hosted paper continuity lanes
- 板面上的 hosted `P3` continuity bucket 仍是：`Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 其中当前有最新 23:36 可见 refresh 快照、且仍在 narrow-paper 自动托管面上的，是：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 122` 仍按顶板口径保留在 `P3 / strict-only / paper-only / hosted continuity`，但本轮没有新的 status-changing event

#### 当前真正在开的 hosted open paper positions（23:36 UTC 快照）
- `Rank 17 / ETH-USD / long`
- `Rank 17 / SOL-USD / short`

一句话人话版：**Paper Seat 还是 EMA；hosted paper continuity 继续存在，但当前真有 open position 的只剩 `Rank 17`。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- `P2` 仍空
- `Rank 133` 也还只到 `guard-passed / clean replication next`
- `Rank 127 / 125 / 112 / 111` 仍是旧 `P1 / budget used`
- `Rank 122 / 2 / 17 / 29 / 32b` 虽是 `P3`，但都是 paper continuity，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 133 / triple barrier honest final-verdict layer`**
  - 当前阶段：`P1 / guard-passed / clean replication next`
  - 性质：paper + repo based
  - 角色：不是新 entry alpha，而是给 breakout-short / Fib / EMA-PSAR 统一补一个更诚实的 `tp_first / sl_first / timeout` 判决层

#### 当前仍在比较表、但不该拿主资源位的旧 P1
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 不应误写成 Scout 主点的 hosted continuity
- `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - 继续只按 `P3 hosted paper continuity / sidecar` 管理

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 133`：`P1（guard-passed / clean replication next）`
- `Rank 127`：`P1（weak candidate / budget used / evidence_pool）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
- `Rank 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 122`：`P3（strict-only / paper-only / hosted continuity / recent-month red-watch）`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3（hosted narrow paper lanes / continuity only）`

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍是 `waiting_not_due`，不得空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，则认领 `Rank 133 / triple barrier honest final-verdict layer` 的最小 clean replication**
   - 只允许冻结既有 entry
   - 只比较：`fixed n-bar forward verdict` vs `tp/sl/timeout triple-barrier verdict`
   - 不提前扩成 stability pack

3. **Run 3 = 条件分支，但默认仍先服务 Scout**
   - 若 `Rank 133` clean replication 给出 honest uplift：立刻输出 `keep_P1 / promote_P2 / park` 的硬 verdict，并补最小 scorecard
   - 若 `Rank 133` hard-fail / exhausted：回 `fresh paper/repo intake`，而不是先切回 hosted `P3 continuity`
   - 只有在 fresh intake 也拿不到合格 source 时，才允许落到 `fixed partial -> R/ATR partial` 的 tiny-live / path-management fallback

---

## 4. Active Scout 边际价值比较
### 为什么 `Rank 133` 仍该排第一
- 它是最新完成 guard-pass 的 paper/repo 候选
- 它直接补三条主线共缺的 `honest final-verdict layer`
- 下一步只需 `1` 次最小 clean replication，预算清楚、问题清楚

### 为什么不是继续磨 `Rank 127 / 125 / 112 / 111`
- 这些线已经吃过便宜诚实检查预算
- 本轮没有新的 status-changing evidence
- 继续投主资源更多是在补文案，不是在减少真实 gate

### 为什么不是 hosted `P3`
- `EMA` 仍 `waiting_not_due`
- hosted narrow-paper 已有独立 cron 在跑
- 当前没有新的 abnormal status 需要插队

### 为什么不是 `fixed partial`
- 它属于 tiny-live / path-management plumbing
- 当前 desk 的默认顺序依然是：`Scout Seat > tiny-live plumbing > 其他维护`

---

## 5. 本轮对 `docs/TODO.md` 的最小必要更新
1. `Hosted P3 快照` 时间：
   - `2026-03-20 22:30 UTC` → `2026-03-20 23:36 UTC`
2. `最近关键 evidence`：
   - 补入 `2026-03-20 23:43 UTC / EMA require-due fast-precheck` 结果
   - 保持顶板证据列表为最近 5 条

### 为什么这轮只做这两个小改
- 席位判断没有变
- `Next 3 bot3 runs` 没有变
- 但最新 hosted paper 快照时间和最新 EMA 守门结果，确实属于当前 authoritative desk 状态，值得最小同步到顶板

---

## 6. 当前 authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due，Crypto lane 仅 due_soon）`；`Live Seat = 暂空`；`Scout Seat = Rank 133 / triple barrier honest final-verdict layer`；hosted paper continuity 仍按 `122 / 2 / 17 / 29 / 32b` 口径托管，当前 open paper positions 只剩 `Rank 17 / ETH long + SOL short`；bot3 接下来仍应按 `EMA due-check -> Rank 133 clean replication -> Rank 133 硬 verdict / 否则 fresh intake` 排。