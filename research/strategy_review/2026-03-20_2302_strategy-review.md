# 2026-03-20 23:02 UTC strategy review

## 本轮一句话判断
当前 desk 收口为：**`Paper Seat = EMA / 创业板ETF 1d active_primary / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 133 / triple barrier honest final-verdict layer`**。本轮不是回头继续磨旧 `P1`，也不是让 hosted `P3` 抢资源；在 `EMA` 仍 `waiting_not_due` 的前提下，bot3 下一顺位应改为：**先认领 `Rank 133` 的 source intake，再决定是否给它 1 次最小 clean replication；若 fresh intake 也 exhausted，才允许退到 `fixed partial -> R/ATR partial` 的 tiny-live/path-management fallback。**

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- repo：`master`
- 工作区：`git status --short --branch` 仍显示大量与本轮无关的脏文件；本轮继续只做最小局部更新，不混提。
- 最近 optimization logs：
  - `2026-03-20 22:58 UTC / Rank 132 clean replication -> park`
  - `2026-03-20 22:26 UTC / Rank 131 clean replication -> park`
  - `2026-03-20 21:41 UTC / Rank 130 clean replication -> park`
  - `2026-03-20 20:47 UTC / Rank 128 clean replication -> park`
  - `2026-03-20 20:16 UTC / EMA 美股 due refresh`
- 最近 strategy review：
  - `2026-03-20 22:05 UTC`
  - `2026-03-20 21:04 UTC`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮运行中
  - `bot3-momentum-auto-opt-13m`：enabled / 当前运行中
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 当前顶板 / hosted / EMA 快照
已回读：
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_history.csv`

关键信息：
- hosted paper 最近可见快照已到 `2026-03-20 22:30 UTC`
- 当前 open paper positions 仍只剩：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 29` 继续 `flat / no open position`
- `EMA` 当前 authoritative 状态仍是：
  - `Crypto 1d+1wk（BTC/ETH/SOL） = due_soon / 约 3.7h`
  - `创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d / 美股 1d+1wk = waiting_not_due`

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 现在是被 market clock 阻塞，而不是执行失灵。**
   - 当前没有 `due-now / overdue` lane
   - 所以 desk 的正确导流仍应是：`Scout Seat > tiny-live plumbing > 其他维护`
2. **最近 3 条 fresh Scout（`Rank 130 / 131 / 132`）已经连续给出硬 verdict：全部 park。**
   - 这说明当前不该把 bot3 再导回这些旧点补 write-back；应果断切下一条 fresh intake
3. **hosted `P3` continuity 没有新的 status-changing event。**
   - `Rank 17` 仍有两笔 open paper position
   - `Rank 29` 已 flat
   - 这层继续只算 sidecar，不是新的 seat
4. **最新可直接改变排兵布阵的新证据，不在旧 `P1`，而在 fresh source 池。**
   - `2026-03-20 21:18 UTC` 的 `triple barrier` digest 给出了一个 paper+repo based、且直接服务 breakout-short / Fib / EMA verdict 层的新 intake 点
   - `2026-03-20 22:42 UTC` 的 `fixed partial` digest 更像 tiny-live / path-management fallback，而不是当前 Scout 主点

---

## 2. 当前 weakest / should-park lines
1. **`Rank 132 / 131 / 130 / 129 / 128`**
   - 已经过完该给的 intake / clean replication 快筛
   - 当前都应继续留在 `P0 / park / evidence pool`
2. **`Rank 127 / 125 / 112 / 111`**
   - 都还在 `P1`，但默认预算已用过
   - 继续回头磨它们，当前更像补 admission 叙事，而不是减少真实 gate
3. **任何把 hosted `P3` continuity 写成当前 Scout 主资源位的读法**
   - 当前没有新的 `due-now / overdue` paper refresh，也没有新的 `status-changing event`
   - 按 desk 规则，不应让这层抢 bot3 主资源

---

## 3. 本轮必须回答的 5 个问题
### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
**Primary paper anchor 仍是：`EMA / 创业板ETF 1d active_primary`。**

#### EMA 家族 hosted/backstop lanes
- `创业板ETF 1d`（active_primary）
- `Crypto 1d+1wk（BTC/ETH/SOL）`（active_secondary_backstop，当前最近 due）
- `美股 1d+1wk（SPY/QQQ/AAPL）`（active_secondary_backstop）
- `贵州茅台 1d+1wk`（active_secondary_backstop）
- `沪深300ETF 1d`（shadow_watch）

#### 独立 hosted paper lanes
- `Rank 122 / ATR compression + ROC ignition short re-arm gate`（`P3 / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / volume_supportflip_higherlow_combo_all`（`P3`）
- `Rank 17 / pullback_recovery_confirmation`（`P3`）
- `Rank 29 / trendline_breakout_navigator`（`P3`）
- `Rank 32b / ema_slope_floor_continuation`（`P3`）

#### 当前真正在开的 hosted open paper positions（22:30 UTC 最新快照）
- `Rank 17 / ETH-USD / long`
- `Rank 17 / SOL-USD / short`

一句话人话版：**Paper Seat 还是 EMA；hosted P3 lanes 也都在托管，但当前真有 open position 的只剩 `Rank 17`，`Rank 29` 已 flat。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- `P2` 当前仍空
- `Rank 127 / 125 / 112 / 111` 都还是 `P1 / budget used`
- `Rank 133` 也才刚被认定为下一顺位 fresh intake，还没过 source intake / honesty gate
- `Rank 122 / 2 / 17 / 29 / 32b` 虽在 `P3`，但都是 paper-only hosted continuity，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 133 / triple barrier honest final-verdict layer`**
  - 来源：`Grądzki, Wójcik, Lessmann (2025)` + `mchiuminatto/triple_barrier`
  - 当前阶段：`P1 / source intake next`
  - 角色：不是新 entry alpha，而是给 `breakout-short / Fib / EMA-PSAR` 统一补一个更诚实的 `tp_first / sl_first / timeout` verdict 层

#### 当前仍留在 active Scout 比较表，但不再默认主推
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 不应误写成 Scout 主点的 hosted continuity
- `Rank 122 / Rank 2 / Rank 17 / Rank 29 / Rank 32b`
  - 继续只按 `P3 hosted paper continuity / sidecar only` 处理

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 133`：`P1`（`source intake next / paper+repo / verdict-layer candidate`）
- `Rank 127`：`P1`（`weak candidate / budget used / evidence_pool`）
- `Rank 125`：`P1`（`keep_P1 / budget used`）
- `Rank 112`：`P1`（`weak candidate / evidence_pool / budget used`）
- `Rank 111`：`P1`（`evidence_pool / budget used`）

#### P0
- `Rank 132 / 131 / 130 / 129 / 128 / 124 / 123 / 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113`
  - `P0 / park / evidence pool`

#### P2
- **当前为空**

#### P3
- `Rank 122`：`P3`（`narrow paper pilot / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`：`P3`（`hosted narrow paper lanes / continuity only`）

#### P4
- **当前为空**

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若有真实 `due-now / overdue` lane，先做 paper refresh
   - 若仍是 `waiting_not_due`，不能空转

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 133 / triple barrier honest final-verdict layer` 的 source intake**
   - 先冻结：
     - 它是不是只改 `verdict`，而不偷改现有 entry
     - `trade on / trade off` 是否能清楚写成：`tp/sl/timeout` 判决替代 fixed `n-bar` 判决
     - 是否存在 lookahead / labeling leakage

3. **Run 3 = 条件分支**
   - 若 `Rank 133` guard-pass：只给 **1 次最小 clean replication**
     - 对照：`fixed n-bar forward verdict` vs `tp/sl/timeout triple-barrier verdict`
     - 统一口径：冻结既有 entry、只改 post-entry 判决层
   - 若 `Rank 133` hard-fail / exhausted：回下一条 fresh intake
   - 只有 fresh intake 也 exhausted 后，才允许切 `fixed partial -> R/ATR partial` 的 tiny-live / path-management fallback

---

## 4. Active Scout 边际价值比较（why now）
### 为什么 `Rank 133` 现在排第一
- 它是当前 freshest 的 paper+repo based 候选，且直接服务三条主线共同缺的 **honest final-verdict layer**
- 它不是又一个“再加一层入场过滤”的拥挤题，而是能减少当前 `follow-up / timeout / hold-quality` 判决口径混乱
- 它下一步天然就是：`source intake -> honesty gate -> 1 次最小 clean replication`，非常符合当前 Scout fast lane

### 为什么不是回头磨 `Rank 127 / 125 / 112 / 111`
- 这些线都已拿过该拿的预算
- 当前没有新的 status-changing evidence 支持升格
- 再做更像 admission write-back，而不是减少真实 gate

### 为什么不是把 `fixed partial` 直接抬成 Scout 主点
- `fixed partial -> R/ATR partial` 更像 **tiny-live / path-management plumbing**
- 当前 desk 顺序明确是 `Scout Seat > tiny-live plumbing > 其他维护`
- 所以它是一个很好的 fallback，但不该抢当前 Scout 主资源位

---

## 5. 建议优先级 Top 1~3
1. **保持 `Run 2 = Rank 133 source intake`，不要回头磨旧 P1。**
2. **若 `Rank 133` guard-pass，只给 1 次最小 clean replication，不要一口气铺 stability pack。**
3. **继续把 hosted `P3` 只当托管层；`fixed partial` 则只保留为 tiny-live/path-management fallback，不抢 Scout 主点。**

---

## 6. TODO / web / cron 的改动或建议
### 本轮实际改动
已最小更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
- 把 `Scout Seat` 从泛泛 `fresh intake reserve` 收紧到 **`Rank 133 / triple barrier honest final-verdict layer`**
- 把 `Active Scout` 第一位具体化为 `Rank 133`
- 把 `Next 3 bot3 runs` 改成：`EMA due-check -> Rank 133 intake -> Rank 133 clean replication / or next fresh intake`
- 把 hosted P3 snapshot 时间同步到 `2026-03-20 22:30 UTC`
- 用一条 recent evidence 明确写出：`fixed partial` 当前只配做 tiny-live/path-management fallback

### 为什么这轮要改顶板
因为 `Rank 132` 已在 `22:58 UTC` 给出 `park` verdict，当前如果继续把 Scout 写成抽象 `fresh intake reserve`，bot3 仍可能随机漂移；而 `21:18 UTC` 的 `triple barrier` 证据已经足够具体，可直接作为下一顺位 `Rank 133` 认领。

### cron / 节奏建议
- **暂不改 cron**
- 当前 cron 结构仍匹配 desk 分工：
  - `bot2` = 排兵布阵
  - `bot3` = 主资源位执行
  - `momentum-narrow-paper-lanes-20m` = hosted `P3` continuity
  - `bot6 / bot7` = 低频 reframe / digest

---

## 7. 风险与不确定性
1. **`Rank 133` 目前还只是 intake 指定，不是已经过门的 clean replication 候选。**
   - 不能提前把它写成 `P2`
2. **`triple barrier` 更像 verdict harness，不是自动等于 live execution rule。**
   - 第一轮必须严格冻结 entry，不偷带多轴变化
3. **`fixed partial -> R/ATR partial` 的 fallback 很有吸引力，但角色仍应是 tiny-live/path-management，不应被包装成 fresh Scout alpha。**
4. **`Crypto 1d+1wk` 已进入 due-soon 窗口。**
   - 之后只要到点，就必须优先让路给 `Paper Seat`

---

## authoritative one-liner
> `Paper Seat = EMA（继续 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 133 / triple barrier honest final-verdict layer`；hosted P3 lane 仍按 `122 / 2 / 17 / 29 / 32b` 托管，当前 open paper positions 只剩 `Rank 17 / ETH long + SOL short`；若 `EMA` 继续 waiting，bot3 下一顺位先做 `Rank 133 intake`，不是回头磨旧 P1，也不是让 tiny-live plumbing 抢主位。
