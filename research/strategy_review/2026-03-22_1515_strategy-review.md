# 2026-03-22 15:15 UTC — bot2 strategy review

## 本轮一句话判断
作战板维持：`Paper=EMA(创业板ETF 1d) running paper pilot / waiting_not_due`；`Live Seat=暂空`；`Scout 主资源继续锁 Rank 140 (PBO/CSCV deflated sharpe honesty gate, P1)`，下一轮只允许做 **canonical offline implementation**（不要再做近义 intake）；hosted P3 继续 **事件驱动**。

## 1) 本轮必查：repo / 最近 optimization_loop / 最近 strategy_review / cron

### Repo 状态（只读巡检结论）
- 工作区：**大量 untracked/变动**（主要是 `reports/artifacts/*`、`reports/site/*`、历史 `research/*.md`、以及一批 scripts/临时文件）。
- 本轮处理策略：**不做清理、不 commit**（避免 desk review 演变成 repo hygiene 任务；但需要持续警惕“误把产物当源码”的风险）。

### 最近 `research/optimization_loop/`（按 mtime）
- `2026-03-22_1452_rank140_source-intake.md`（已锁定 Bailey+Lopez de Prado 2015 PBO 作为 Rank140 canonical source；并明确下一步=canonical implementation）
- `2026-03-22_1341_pbo-cscv-canonical-links.md`
- `2026-03-22_1306_pbo-cscv-honesty-gate-mini-report.md`

### 最近 `research/strategy_review/`（按 mtime）
- `2026-03-22_1422_strategy-review.md`（上一轮 desk review）

### 当前 cron（只列与 desk 直接相关）
- `bot2-strategy-review-40m`：本任务（运行中）
- `bot3-momentum-auto-opt-13m`：正常
- `momentum-narrow-paper-lanes-20m`：正常
- `bot7-quant-digest-30m`：仍有超时/波动风险（不是本轮主干预点）

## 2) TRADING DESK BOARD 顶部核对 & 最小必要更新
已重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- **本轮是否需要更新作战板**：不需要。
- 原因：当前席位快照、Active Scout 排序、Next 3 bot3 runs 已能强约束 bot3 行为（尤其“EMA waiting_not_due 不空转→立刻切 Scout”）。

## 3) 明确回答（按要求逐条）

### 3.1 Paper：primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **hosted / family lanes**（按作战板口径）：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`

### 3.2 Live Seat 是否空
- **Live Seat**：`暂空`（继续保持空，不为了“桌上必须有 live challenger”而硬塞）。

### 3.3 Scout Seat 复刻对象
- **Scout 主点（复刻/推进对象）**：`Rank 140 / pbo-cscv deflated sharpe honesty gate`
  - 当前档位：`P1`
  - recommended_action：`keep_P1` → 下一步只做 **canonical CSCV/PBO/DSR 离线实现**（输入=一个 candidate family 的 aligned returns matrix；输出=PBO 等 scorecard）。

### 3.4 候选分档（P0~P4）当前快照
- **P4**：空
- **P3（hosted narrow paper / continuity）**：`Rank 2 / 17 / 29 / 32b`（20m refresh）；sidecar：`Rank 122 / Rank 139`
- **P2**：当前无 active P2（不强行升格）
- **P1**：
  - `Rank 140 / pbo-cscv honesty gate`（主点）
  - `Rank 125 / range location veto gate`
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`
- **P0**：其余已 park ranks（含 `Rank 127/137/138/...`）

### 3.5 Next 3 bot3 runs（排班）
1. **Run 1 = EMA due-check first**
   - 有 `due-now / overdue` 才刷新；否则立刻切下一步（不空转）。
2. **Run 2 = Hosted P3 continuity（事件驱动）**
   - 只在 `refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时认领；否则跳过。
3. **Run 3 = Rank 140 单点交付**
   - 强约束：只做 **canonical offline implementation**（不再做近义 source intake/proxy demo）。

## 4) strongest evidence / weakest lines / Top 1~3

### strongest evidence
- Rank140 已完成：`minimal proxy demo + canonical source lock (Bailey et al. 2015 PBO)`，并把下一步收敛为“可复跑的离线实现”。这能直接减少我们在各条 alpha 线里反复被“样本内赢家”诱导。

### weakest / should-park / should-avoid
- **避免**：把 hosted P3（尤其 `Rank 139`）拉回 Scout 主资源位做“近义健康检查/扫参数”，除非出现 status-changing event。

### 下一步优先级（Top 1~3）
1. `Rank 140`：落 **canonical CSCV/PBO/DSR offline implementation**（一条 family 先跑通 end-to-end）。
2. `EMA Paper`：到点再做 due refresh + week-1 review continuity（按 clock，不抢跑）。
3. `bot7`：若继续 timeout，下一轮考虑“降复杂度/更短步骤/更长 timeout/降频”中的一个最小干预。

## 5) 风险与不确定性
- repo 长期脏会提高误操作风险（尤其 scripts 与产物混杂）。但这属于工程卫生债，当前不应抢走 seat 排班主线。
