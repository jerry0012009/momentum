# 2026-03-22 13:14 UTC — bot2 strategy review

## 本轮一句话判断
`EMA(Paper) 继续 running paper pilot / waiting_not_due；Live Seat 继续暂空；Scout 主资源继续锁定 pbo-cscv(P1) 只做“canonical 对齐”交付（不扩候选），hosted P3 仅事件驱动。`

## 1) Repo / 近期更新 / cron（本轮必查）
- **repo 状态**：工作区存在大量未提交变动/新增（主要是 research 日志、scripts、reports 产物）；本轮不做整理/commit（避免把 desk review 变成 repo 清理）。
- **最近 optimization_loop**（关键方向）：
  - `2026-03-22_1306_pbo-cscv-honesty-gate-mini-report.md`：把 pbo-cscv 从 CSV/脚本补到了一个站点可见页（`reports/site/factors/pbo_cscv_honesty_gate/report.html`）。
  - `2026-03-22_1216_bot3-momentum-auto-opt-13m.md`：EMA waiting_not_due；Rank139(P3) 未见 status-changing event；pbo-cscv 离线 scorecard 刷新。
  - `2026-03-22_1041_pbo-cscv-source-intake.md`：已锁定 PBO/CSCV + DSR 的 canonical source intake（人话摘要已写）。
- **最近 strategy_review**：上一条为 `2026-03-22_1152_strategy-review.md`；本轮补档。
- **cron 列表**：
  - `bot3-momentum-auto-opt-13m` 正常运行。
  - `momentum-narrow-paper-lanes-20m` 正常运行（Rank2/17/29/32b）。
  - `bot7-quant-digest-30m` 近期连续 timeout（consecutiveErrors=4）：建议后续单独排障或降负载（不在本轮 desk board 内扩展）。
  - 备注：本轮用 `openclaw cron list` CLI 读取失败（gateway closed 1000），但通过内置 `cron` 工具已成功取到同等信息；若后续持续复现，再单独修 CLI 连接问题。

## 2) TRADING DESK BOARD 顶部核对（最小必要更新）
已核对 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：席位、Active Scout、Next 3 bot3 runs 与最近证据一致。

- **本轮不做改动**：当前版已经明确了“EMA waiting_not_due 不空转 → 立刻切 Scout”的执行纪律，并把 hosted P3 明确降为事件驱动。

## 3) Seats 明确回答（Paper / Live / Scout）
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **当前状态**：`running paper pilot / waiting_not_due`
- **hosted / family lanes**：
  - 美股 `1d+1wk（SPY/QQQ/AAPL）`
  - Crypto `1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### Live Seat
- **是否空**：是（`暂空`）

### Scout Seat
- **当前复刻/推进对象（主点）**：`pbo-cscv / deflated sharpe honesty gate`
  - 定位：`P1 / honesty-layer intake`
  - 本轮结论：已经完成 `source intake` + `proxy/canonical scorecard` + **站点可见落点**；下一步只允许做 1 个“对齐 canonical 定义/实现细节”的小交付（不要再做近义 demo）。

## 4) 候选分档（P0~P4）— 当前快照
- **P3（hosted narrow paper pilot / continuity）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`；`Rank 139`；sidecar：`Rank 122`。
- **P2**：当前无明确 active P2（不强行升格）。
- **P1（只允许 1 次便宜诚实检查/或 1 个小交付）**：`pbo-cscv`、`Rank125`、`Rank112`、`Rank111`。
- **P0（park/evidence pool）**：其余已 park ranks（含 Rank137/138/127 等）。
- **P4（tiny-live review candidate）**：当前为空。

## 5) Next 3 bot3 runs（排班确认）
1. **Run 1 = EMA due-check first**：有 due-now/overdue 才刷新；否则立即切下一步。
2. **Run 2 = Hosted P3 continuity（事件驱动）**：只在 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时认领；否则跳过。
3. **Run 3 = 只选 1 个（当前：pbo-cscv honesty gate）**：
   - 只做 1 个小交付：`canonical CSCV/PBO/DSR 离线实现对齐/注释 + 引用固化`（不要开新候选）。

## 6) strongest evidence / weakest lines
- **strongest**：pbo-cscv 已从“概念”推进到“可审计离线 scorecard + 网页落点”，对 desk 的多重筛选偏差问题开始有一个统一入口。
- **weakest / should-avoid**：把 hosted P3（尤其 Rank139）拉回重复“近义健康检查/继续扫参数”，除非出现 status-changing event。

## 7) 风险与不确定性
- `bot7-quant-digest-30m` timeout 连续发生，可能吞资源且产出不稳定；建议后续降低频率/收紧提示词/加超时更小的 work scope。
- repo 长期脏工作区会放大误改风险：建议择机做一次“产物与源码分层/最小可回滚整理”，但不在本轮 desk review 内展开。
