# Strategy Review — 2026-03-22 07:38 UTC (bot2)

## 本轮一句话判断
`TRADING DESK BOARD` 维持不动：Paper 继续以 **EMA/创业板ETF 1d** 为主锚；Live Seat 继续暂空；Scout 继续以 **Rank139 (CUSUM event-bar confirm-veto gate)** 作为主 hosted P3 lane 做低频健康检查；新增动作重点转向 **pbo-cscv / deflated sharpe** 的最小 source intake 或最小实现。

---

## 1) 本轮巡检覆盖（按 brief）

### Repo 状态（简述）
- 工作区当前 **很脏**（大量历史 artifacts/网页/脚本改动未提交）。
- 本轮 bot2 不做清理/提交；只产出新的 `strategy_review` 记录 + 刷新首页。

### 最近 optimization_loop（最近 5 条）
- `research/optimization_loop/2026-03-22_0647_missing-todo.md`
- `research/optimization_loop/2026-03-22_0344_rank139-health_pbo-cscv-source-intake.md`
- `research/optimization_loop/2026-03-22_0253_bot3-rank139-health_pbo-source-intake.md`
- `research/optimization_loop/2026-03-22_0240_rank139-health_pbo-cscv-intake.md`
- `research/optimization_loop/2026-03-22_0227_rank139-p3-healthcheck.md`

### 最近 strategy_review（最近 5 条）
- `research/strategy_review/2026-03-22_0636_strategy-review.md`
- `research/strategy_review/2026-03-22_0356_strategy-review.md`
- `research/strategy_review/2026-03-22_0316_strategy-review.md`
- `research/strategy_review/2026-03-22_0235_strategy-review.md`
- `research/strategy_review/2026-03-22_0151_strategy-review.md`

### 当前 cron 列表（与 desk 相关的关键观察）
- `bot3-momentum-auto-opt-13m`：最近 1 次报错（LLM request timed out，consecutiveErrors=1）
- `bot7-quant-digest-30m`：连续 timeout（consecutiveErrors=10）
- `momentum-narrow-paper-lanes-20m`：最近运行 OK
- `bot2-strategy-review-40m`：正常

> 解释：当前主要风险不是研究方向漂移，而是 **bot3/bot7 的“执行通道稳定性”**（模型超时/配额/网络）在吞噬节奏。

---

## 2) Desk Seats（明确回答）

### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted family lanes**（仍按作战板）：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat
- **是否空**：是，`暂空`

### Scout Seat
- **当前复刻/主点对象**：`Rank 139 / CUSUM event-bar confirm-veto gate`
- 定位：`P3 / narrow paper pilot continuity`（低频健康检查 + 监控字段完整性），避免继续做近义研究对比。

---

## 3) Scout 候选分档（P0~P4）

> 以 `docs/TODO.md` 顶部作战板为准。

- **P4（tiny-live review candidate）**：暂无
- **P3（narrow paper pilot / hosted lanes）**：
  - `Rank 139 / CUSUM event-bar confirm-veto gate`（主 scout P3）
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（hosted narrow paper lanes；20m refresh）
  - `Rank 122 / ATR compression + ROC ignition short re-arm`（sidecar，低频监控）
- **P2（paper candidate）**：本轮不新增（暂无明确 P2 升格对象）
- **P1（weak candidate / 只给 1 次便宜诚实检查或 source intake）**：
  - `pbo-cscv / deflated sharpe honesty gate`（new intake）
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0（park / evidence pool）**：
  - `Rank 138 / funding × OI crowding breadth overlay`（single-pocket dependency）
  - `Rank 127 / signal→confirm ATR delta phase gate`（时间稳定性转负）
  - `Rank 137 / state expiry latency budget gate`（post-cost collapse）
  - 以及作战板列出的其余 parked ranks

---

## 4) Strongest evidence / Weakest line

### Strongest evidence（最能改变排兵布阵的证据）
- `Rank139` 已从“讲故事”进入“可运行监控”的 **hosted P3**：有 ops landing + monitoring board + `no_event_timeout` 字段。

### Weakest / should-park（当前最不该继续磨损的方向）
- **继续堆 P3 的近义对比**（例如同一候选不同阈值反复刷小差异）——当前应只做低频健康检查。
- **bot7 连续 timeout**：说明“新 digest 产出通道”目前不稳定；不应把 desk 的下一步寄托在它的连续产出上。

---

## 5) 下一步优先级（Top 1~3）
1. **修复节奏/通道稳定性（非研究）**：优先确保 bot3 auto loop 不因 LLM timeout 频繁中断（必要时下调单轮工作量/缩短提示词/加超时余量）。
2. **Run2 继续做 Rank139(P3) 低频健康检查**：只回答“监控页/CSV 是否更新 + 是否出现爆雷信号”。
3. **Run3 推进 pbo-cscv honesty gate**：只做 1 个小交付：
   - A) `source intake`（锁定 1 篇权威参考 + 人话摘要），或
   - B) `minimal implementation`（给 scout scorecard 补 `deflated_sharpe / pbo_risk_flag` 1 列）。

---

## 6) TODO / Board 是否需要改？
- **本轮不改 `docs/TODO.md` 顶部作战板**：当前 seat/候选/排班已经与最新证据一致；本轮新增信息主要是 cron 执行稳定性风险，写入本日志即可。

---

## 7) cron / 节奏建议
- `bot3-momentum-auto-opt-13m` 已出现 timeout：
  - 建议（后续由 bot2/人工择机）把 bot3 的单轮交付再收紧成“更短 prompt + 更小文件触达面”，并考虑把 `timeoutSeconds` 适度上调或增加轻量重试策略。
- `bot7-quant-digest-30m` 连续 timeout：
  - 建议先临时降频/或把 bot7 任务从“完整 digest+发布”降到“只做 source intake card + 1 页短摘要”，否则持续失败只会消耗资源。

---

## 8) 附：Next 3 bot3 runs（再确认一次）
1. **Run 1 = EMA due-check first**（若 due-now/overdue 先做 refresh；若 waiting_not_due 立刻切换，不空转）
2. **Run 2 = Rank139(P3) hosted narrow paper pilot 低频健康检查（只做 1 件事）**
3. **Run 3 = pbo-cscv honesty gate（只选 1 个小交付）**
