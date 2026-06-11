# 2026-03-21 00:23 UTC strategy review

## 本轮一句话判断
当前 desk 继续维持：**`Paper Seat = EMA / 创业板ETF 1d (active_primary) / waiting_not_due`、`Live Seat = 暂空`、`Scout Seat = Rank 135 / fresh intake slot（待认领）`**。`Rank 134` 已在 00:16 UTC 完成最小 clean replication 并被压回 `P0 / park`，因此本轮不该再磨旧 `P1` 或 hosted `P3 continuity`，而应继续把 bot3 导向 **fresh paper/repo intake > tiny-live plumbing > 其他维护**。

---

## 0. 本轮先检查了什么
### Repo / recent logs / cron
- branch：`master`
- 工作区脏文件：`git status --short | wc -l = 2201`
- 最近 optimization logs：
  - `2026-03-21_0016_rank134-clean-replication-park.md`
  - `2026-03-20_2359_rank133-park-rank134-intake.md`
  - `2026-03-20_2332_rank133-source-intake.md`
  - `2026-03-20_2258_rank132-clean-replication-park.md`
  - `2026-03-20_2237_rank132-adaptive-exhaustion-intake.md`
- 最近 strategy reviews：
  - `2026-03-20_2343_strategy-review.md`
  - `2026-03-20_2302_strategy-review.md`
  - `2026-03-20_2205_strategy-review.md`
- 当前关键 cron：
  - `bot2-strategy-review-40m`：enabled / 本轮运行中
  - `bot3-momentum-auto-opt-13m`：enabled
  - `momentum-narrow-paper-lanes-20m`：enabled / 最近成功
  - `bot6-park-reframe-2h`：enabled / 最近成功
  - `bot7-quant-digest-30m`：enabled / 最近成功
  - `Rank32b live maintenance`：enabled / 最近成功

### 当前 EMA due 守门
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
结果：
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`
- 当前状态：`waiting_not_due`
- 距下一次真正 completed bar：约 `23.6h`
- 结论：当前仍然是 **market clock 阻塞**，不是执行停滞；本轮合法导流仍是 `Scout Seat > tiny-live plumbing > 其他维护`

### Hosted narrow paper lanes 最新快照
已回读：
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_status.csv`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_open_positions.csv`

最新 refresh：
- `run_at_utc = 2026-03-21T00:08:42Z`
- `sample_end_utc = 2026-03-20T23:45:00Z`
- 当前仍可见的 hosted open paper positions：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`
- `Rank 2 / Rank 29 / Rank 32b` 当前均为 `flat / none`

---

## 1. 当前 strongest evidence
1. **`Paper Seat` 仍然真 blocked by clock，而不是缺执行。**
   - `EMA require-due` 再次确认：没有任何 lane 到 `due-now / overdue`
   - 因此 bot3 这几轮不该回头做伪 refresh，也不该因为 `EMA` 在等而空转
2. **`Rank 134` 已经给出足够明确的负面 verdict。**
   - clean replication 虽有总体 `+8.16 bps` uplift 幻觉，但只剩 `11.52%` 交易
   - `failure delta = +10.23 pct`
   - `ETH = -29.46 bps`、`SOL = +49.56 bps`，跨资产明显分裂
   - 这类结果应直接进 `P0 / evidence pool`，不值得继续占 `P1`
3. **hosted `P3` lanes 正在被专属 cron 托管。**
   - 20m narrow-paper cron 正常刷新
   - 最新可见 open positions 仍只剩 `Rank 17` 两腿
   - 因此它们继续只是 `P3 continuity / sidecar`，不是新的主 seat

---

## 2. 当前 weakest / should-not-overweight 的线
1. **旧 `P1 budget-used`：`Rank 127 / 125 / 112 / 111`**
   - 这些线继续磨下去，当前更像补说明，不像减少 gate
   - 若没有新的 cheap honest check，不应默认再占 bot3 主资源
2. **任何把 hosted `P3` continuity 重写成“当前 Scout 主点”的读法**
   - 现在没有新的 `status-changing event`
   - 也没有 `due-now / overdue` paper refresh
3. **任何为了填 `Live Seat` 而强行升格的动作**
   - 当前还没有通过 `clean replication + 最小诚实检查` 的新候选
   - `Live Seat` 应继续允许为空

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
- 最新 00:08 UTC refresh 下，仍在跑的 hosted narrow paper lanes 为：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- 当前可见 open positions 只剩：
  - `Rank 17 / ETH-USD / long`
  - `Rank 17 / SOL-USD / short`

一句话：**Paper Seat 还是 EMA；hosted paper continuity 继续跑，但当前真有 open paper position 的只有 Rank 17。**

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
**继续保持暂空。**

原因：
- 当前没有 `P2` 候选
- `Rank 134` 已经被 park
- `Rank 127 / 125 / 112 / 111` 仍是旧 `P1 / budget used`
- hosted `P3` lanes 是 paper continuity，不是 live challenger

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
#### 当前主资源位
- **`Rank 135 / fresh intake slot（待认领）`**
  - 当前阶段：`source intake pending`
  - 来源范围已被 desk board 锁定：只允许从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md` 中认领 **1 条 paper/repo based 5m/15m crypto 候选**

#### 当前仍在 active comparison、但不该抢主资源的旧 P1
- `Rank 127 / signal→confirm ATR delta phase gate`
- `Rank 125 / range location veto gate`
- `Rank 112 / basis dislocation short veto`
- `Rank 111 / abnormal-return event clock`

#### 已退出 active Scout 主位的最新候选
- `Rank 134 / cross-market intraday TSMOM lead-lag gate`
  - 已完成 `source intake + honesty gate + 最小 clean replication`
  - 当前结论：`park / evidence pool`

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
#### P1
- `Rank 135`：`P1（fresh intake slot / source intake pending）`
- `Rank 127`：`P1（weak candidate / budget used / evidence_pool）`
- `Rank 125`：`P1（keep_P1 / budget used）`
- `Rank 112`：`P1（weak candidate / evidence_pool / budget used）`
- `Rank 111`：`P1（evidence_pool / budget used）`

#### P0
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

2. **Run 2 = 若 EMA 仍 `waiting_not_due`，认领 `Rank 135 / fresh intake slot`**
   - 只允许从 `RECENT_PAPER_SEEDS / quant_digests index / validated shortlist` 三者之一挑 `1` 条 `paper / repo based 5m/15m crypto` 候选
   - 当轮只完成：`source intake + trade on/off 冻结 + no-leakage 守门`

3. **Run 3 = 条件分支，但默认仍先服务 fresh Scout**
   - 若 `Rank 135` 守门通过：给 `1` 次最小 clean replication（BTC/ETH/SOL、next-bar open、no-overlap、6/10/15bps）
   - 若 `Rank 135` guard-fail：继续下一条 fresh intake
   - 只有 fresh intake 也真实 exhausted，才允许落到 `tiny-live plumbing / fixed partial -> R/ATR partial` fallback

---

## 4. Active Scout 边际价值比较
### 为什么现在该把主资源给 `Rank 135`，而不是继续磨旧 `P1`
- `Rank 134` 已经完成了该给的 cheapest honest check，并给出足够明确的 `park`
- `Rank 127 / 125 / 112 / 111` 都属于旧 `budget-used`，继续磨的边际价值偏低
- `Rank 135` 代表的是 **新的 fresh intake 机会**，而不是再给旧证据池找补充措辞
- 在 `EMA waiting_not_due` 情况下，这正符合 desk 的默认顺序：**先 fresh intake，再 tiny-live plumbing，再其他维护**

### 本轮推荐动作
- `recommended_action = keep Rank 135 as active Scout head / do fresh intake next`
- `why_now = Rank 134 刚被 park，当前没有 P2 候选，fresh intake 的边际价值最高`
- `main_weakness = Rank 135 还未被具体认领成某一条明确候选，当前只是 queue slot`

---

## 5. TODO / 网页 / cron 是否要改
### TODO 顶板
**本轮不改。**

原因：
- `Paper Seat / Live Seat / Scout Seat` verdict 没变
- `Next 3 bot3 runs` 没变
- `Rank 134 park -> Rank 135 fresh intake` 已在 00:16 UTC 那轮写回顶板
- 当前只新增了更晚一版 hosted paper refresh 时间戳（00:08 UTC），但没有改变席位判断或 run order，不值得为此反复 churn 顶板

### 网页 / 首页
- 仍按要求刷新首页 index
- 本轮不额外改 reader-facing 页面；当前属于**无变更巡检**

### cron / 节奏
**不改。**
- bot2 40m / bot3 13m / narrow-paper 20m / bot6 2h / bot7 30m 的当前分工仍合理
- 当前没有发现需要把 hosted `P3` 再抢回 bot3 主循环的异常

---

## 6. 建议优先级 Top 1~3
1. **继续保持 `Run 1 = EMA require-due precheck`，但一旦仍 not due，立刻切走**
2. **让 bot3 认领 `Rank 135` 的唯一主点：fresh source intake + honesty gate**
3. **只有 fresh intake 真的 exhausted 时，才回 tiny-live plumbing；不要先回头磨旧 `P1` 或 hosted `P3`**

---

## 7. 风险与不确定性
1. **memory_search 当前不可用**（本轮调用返回 embedding/provider unavailable）；不过本轮核心判断已由 repo 内最新日志、TODO 顶板、EMA 守门结果和 manual narrow paper artifacts 支撑，不影响当前 desk 排班。
2. **工作区脏文件非常多**，继续不适合做安全 selective commit。
3. `Rank 135` 当前还只是 slot，不是具体候选；下一轮 fresh intake 的选题质量会直接影响 Scout Seat 的边际价值。

---

## authoritative one-liner
> `Paper Seat = EMA（真 waiting_not_due）`；`Live Seat = 暂空`；`Scout Seat = Rank 135 fresh intake slot`；hosted paper continuity 继续由 `122 / 2 / 17 / 29 / 32b` 托管，当前 open paper positions 只剩 `Rank 17 / ETH long + SOL short`；接下来 bot3 仍应按 `EMA due-check -> Rank 135 source intake -> Rank 135 clean replication / 否则继续 fresh intake` 排。