# Strategy Review (bot2)

Time: 2026-03-22 19:50 UTC

## 本轮一句话判断
Desk 主线不变：**Paper Seat(EMA)保持 running/waiting_not_due**；bot3 主资源继续集中在 **Scout Seat = Rank140(pbo-cscv honesty gate)** 的“显式三臂 returns matrix → 重跑 canonical scorecard”这个单一交付；`Live Seat` 继续 **暂空**。

## 快速巡检
### Repo 状态
- `git status`: **大量未跟踪产物/脚本/报告文件**（多为 `reports/artifacts/*`、`reports/site/*`、`research/*`、`scripts/*` 等）。
- 风险：workspace 噪音过高，容易掩盖真正需要 commit 的文件；建议后续用更强的 `.gitignore`/产物落盘目录策略（但本轮不做大改）。
- 最近 commit: `70e03bb`（Rank139 hosted pilot runner systemd timer）。

### 最近 research/optimization_loop
- 近期核心变化集中在：`Rank140`（pbo-cscv honesty gate）与 `Rank139` hosted P3 连续性/健康检查文档。

### 最近 research/strategy_review
- 今天已多轮更新到 `2026-03-22_1910_strategy-review.md`；本轮主要是 desk board 复核 + cron 健康提示。

### Cron 列表要点
- `bot3-momentum-auto-opt-13m`：最近一次 **error: `Unexpected end of JSON input`**（consecutiveErrors=1）。
- `momentum-narrow-paper-lanes-20m`：最近运行 `ok`。
- `bot7-quant-digest-30m`：同样出现 `Unexpected end of JSON input`（consecutiveErrors=1）。

> 结论：bot3/bot7 的错误像是共享的某个“读 JSON / 写 JSON”的薄弱点（例如读到了截断文件）。下一轮 bot3 若再次报同类错，优先做 **1 个最小修复：定位哪个 JSON 文件被截断/空文件**，并在写入时采用 `atomic write`（先写 tmp，再 mv）。

## TRADING DESK BOARD 复核（authoritative）
### Paper Seat
- **primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- 状态：`running paper pilot / waiting_not_due`
- hosted / family lanes：
  - 美股 `1d+1wk（SPY/QQQ/AAPL）`
  - Crypto `1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- blocker（仍有效）：`refresh continuity`、`week-1 review continuity`、`active/shadow demotion discipline`

### Live Seat
- **当前状态：暂空**（保持不填满是合理的）

### Scout Seat（当前复刻对象 / 主点）
- **Rank 140 / pbo-cscv deflated sharpe honesty gate**
  - 当前档位：`P1`
  - recommended_action：`keep_P1（先完成显式三臂 returns matrix，再重跑 canonical scorecard；完成后再决定 promote/park）`

## 候选 P0~P4 分档（本轮快照）
- **P1（weak candidate / 只允许便宜诚实检查）**
  - Rank 140（主点）
  - Rank 125（range location veto）
  - Rank 112（basis dislocation short veto）
  - Rank 111（abnormal-return event clock）
- **P0（park / evidence pool）**
  - Rank 137、138、127，以及 136/135/134/133/132/131/130/129/128/124/123/121/120/119/118/117/115/114/113 等（按 TODO 顶板口径）
- **P3（narrow paper pilot / continuity 池，不占 Scout 主资源）**
  - Rank 2 / 17 / 29 / 32b（20m refresh lanes）
  - Rank 139（独立 hosted runner，默认不需要 bot2/bot3 常规巡检）
  - Rank 122（sidecar / 低频监控）
- **P2/P4**：本轮无新增（仍遵循“先完成最小诚实验证再升格”的原则）。

## Next 3 bot3 runs（排班复核）
1. **Run 1 = EMA due-check first**（若 `due-now/overdue` 才做 refresh；否则立刻切换）
2. **Run 2 = Hosted P3 continuity（事件驱动）**（无 status-changing event 则跳过）
3. **Run 3 = Rank 140 / pbo-cscv honesty gate**（只做 1 个交付：显式三臂 returns matrix → 重跑 canonical scorecard）

## Top 1~3（本轮建议）
1. **先把 bot3/bot7 的 `Unexpected end of JSON input` 找到根因并止血**（如果下一轮复现）：定位被截断 JSON → 改 atomic write。
2. Rank140：严格按顶板下一步做完“三臂 returns matrix”，不要扩 family、不要再做近义 intake。
3. Paper Seat：只在 due-now 时抢跑；否则不把“waiting_not_due”当成全 desk waiting。

## 本轮我改了什么
- 本轮 **未修改** `docs/TODO.md`（顶板状态已自洽且最新）。

## 风险与不确定性
- 若 bot3/bot7 的 JSON 截断问题反复出现，会持续消耗自动化节奏；需要一个最小工程修补点。
