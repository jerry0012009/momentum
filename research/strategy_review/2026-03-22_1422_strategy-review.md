# 2026-03-22 14:22 UTC — bot2 strategy review

## 本轮一句话判断
`TRADING DESK BOARD 维持不变：EMA(Paper) 继续 running paper pilot / waiting_not_due；Live Seat 继续暂空；Scout 主资源继续锁定 Rank140(pbo-cscv,P1) 做“canonical 对齐”单点交付；hosted P3 仅事件驱动。`

## 1) Repo / 近期更新 / cron（本轮必查）
- **repo 状态**：工作区仍为大量未提交变动（多为 reports/artifacts/site 产物 + research 日志 + scripts 迭代）。本轮不做整理/commit（避免 desk review 变成 repo 清理）。
- **最近 optimization_loop（Top 5 by mtime）**：
  - `research/optimization_loop/2026-03-22_1341_pbo-cscv-canonical-links.md`
  - `research/optimization_loop/2026-03-22_1306_pbo-cscv-honesty-gate-mini-report.md`
  - `research/optimization_loop/2026-03-22_1216_bot3-momentum-auto-opt-13m.md`
  - `research/optimization_loop/2026-03-22_1142_bot3-auto-opt-ema139-pbo.md`
  - `research/optimization_loop/2026-03-22_1112_bot3-auto-opt-13m.md`
- **最近 strategy_review**：上一条为 `research/strategy_review/2026-03-22_1314_strategy-review.md`；本轮为增量巡检补档。
- **当前 cron 列表要点**：
  - `bot3-momentum-auto-opt-13m`：正常运行。
  - `momentum-narrow-paper-lanes-20m`：正常运行（此刻处于 running）。
  - `bot7-quant-digest-30m`：上次 run `timeout`（consecutiveErrors=1），当前也处于 running；建议后续把 bot7 scope 再收紧或提高超时容忍，但不在本轮扩展处理。

## 2) TRADING DESK BOARD 顶部核对（最小必要更新）
已重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：席位、Active Scout、Next 3 bot3 runs 与最近证据一致。

- **本轮改动**：无（当前作战板已经足够清晰，且能驱动 bot3 “EMA waiting_not_due 不空转→切 Scout”的执行纪律）。

## 3) Seats 明确回答（Paper / Live / Scout）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted lanes（family lanes）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat
- **是否空**：是（`暂空`）

### Scout Seat
- **当前复刻/推进对象（主点）**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
  - 当前档位：`P1`
  - 推荐动作：`keep_P1`（不扩候选），只做 1 个“canonical 对齐”交付。

## 4) 候选分档（P0~P4）— 当前快照
- **P4（tiny-live review candidate）**：空
- **P3（narrow paper pilot / continuity）**：
  - `Rank 2 / Rank 17 / Rank 29 / Rank 32b`（hosted narrow paper lanes, 20m refresh）
  - sidecar/hosted：`Rank 122 / Rank 139`
- **P2（paper candidate）**：当前无 active P2（不强行升格）
- **P1（弱候选，仅允许 1 次便宜诚实检查/或 1 个小交付）**：
  - `Rank 140 / pbo-cscv honesty gate`
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0（park / evidence pool）**：其余已 park ranks（含 Rank137/138/127/…）

## 5) Next 3 bot3 runs（排班确认）
1. **Run 1 = EMA due-check first**
   - 有真实 `due-now/overdue` 才刷新；否则立即切下一步。
2. **Run 2 = Hosted P3 continuity（事件驱动）**
   - 只在 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时认领；否则跳过。
3. **Run 3 = 只选 1 个（当前：Rank 140 / pbo-cscv）**
   - 下一步只做 1 个小交付（二选一，择其一即可）：
     - `canonical CSCV/PBO/DSR 离线实现对齐（含引用固化 + 最小可复现脚本/注释）`
     - 或 `再补 1 篇权威 source intake（用于锁口径 + 防止自说自话）`

## 6) strongest evidence / weakest lines
- **strongest evidence**：Scout 主线已经从“随缘找 alpha”切到“统一诚实守门层(pbo-cscv) + hosted P3 continuity”，能更直接服务 paper/tiny-live 的后续 gate。
- **weakest / should-avoid**：把 hosted P3（尤其 Rank139）拉回 Scout 主资源位做近义 health-check/扫参数，除非出现 status-changing event。

## 7) 风险与不确定性
- `bot7-quant-digest-30m` 仍有 timeout 风险：如果继续复现，建议下一轮 desk review 再决定是否降频/改 prompt/拆成更小步骤。
- repo 持续脏会放大误改风险：但这是“工程卫生”问题，不应抢占当前 desk 的 seat 排班。
