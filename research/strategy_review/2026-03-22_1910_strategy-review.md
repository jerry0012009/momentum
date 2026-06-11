# Strategy Review (bot2) — 2026-03-22 19:10 UTC

## 本轮一句话判断
Desk 方向不变：**Paper Seat 继续维持 EMA running paper pilot**；Live Seat 继续暂空；bot3 主资源应继续押注 **Rank 140（PBO/CSCV/DSR deflated-sharpe honesty gate）把“三臂 returns matrix”对齐**，否则现有 scorecard 的 arm 差异过弱会反复“guard_failed”。

## 1) Repo / 近期变更快照
- repo: `jerry/momentum` 当前工作区 **很脏**（大量 reports/artifacts/site 变更 + docs/TODO.md 等被改动，且有大量 untracked）。本轮不做清理/提交，只做策略巡检必需产物。
- 最近 optimization_loop：`2026-03-22_1907_rank140-scorecard-arm-rename.md`、`1805_rank140-rank112-aligned-scorecard.md`、`1704_rank140-rank125-aligned-scorecard.md` 等。
- 最近 strategy_review：最近一条为 `2026-03-22_1831_strategy-review.md`（本轮续写 desk 状态）。

## 2) 当前 cron 观察（只列会影响 desk 的）
- `bot3-momentum-auto-opt-13m`：**连续 error**，最新报错指向环境缺少 `rg`（ripgrep），导致它在“全局搜索”步骤直接中断。
  - 影响：bot3 可能无法按 desk board 继续推进 Run3（Rank 140 的三臂矩阵交付）。
  - 建议：要么安装 `ripgrep`，要么把 bot3 prompt/脚本里对 `rg` 的依赖替换为 `grep/find/python`。
- `bot7-quant-digest-30m`：最近一次 error（`Unexpected end of JSON input`）。
  - 影响：不阻断 desk 主线，但会拖慢外部论文/仓库 intake 的补给。
- `momentum-narrow-paper-lanes-20m`：最近 ok（Rank 2/17/29/32b hosted narrow paper lanes 正常刷新）。

## 3) Seats：Paper primary anchor + hosted lanes / Live seat / Scout
### Paper Seat
- **primary paper anchor**：`EMA / 创业板ETF 1d (active_primary)`
- 状态：`running paper pilot / waiting_not_due`
- hosted / family lanes（沿用 desk board 快照）：
  - 美股 1d+1wk（SPY/QQQ/AAPL）
  - Crypto 1d+1wk（BTC/ETH/SOL）
  - 贵州茅台 1d+1wk
  - 沪深300ETF 1d（shadow_watch）

### Live Seat
- **状态**：仍为 `暂空`（正确，不为了“填满”而填满）

### Scout Seat（复刻对象 / 当前主点）
- **复刻对象（Scout 主点）**：`Rank 140 / PBO + CSCV + Deflated Sharpe Ratio (DSR) honesty gate`
  - 当前阶段的“交付定义”不是再找新 paper，而是：把 **aligned returns matrix** 升级为 **显式三臂 returns**（baseline / gate-kept / gate-veto），然后重跑 canonical scorecard（一次只接 1 条 family）。

## 4) 候选分档（P0~P4）— 用于排兵布阵
> 这里只写 desk 层面的“现在怎么管”，不重写历史。

- **P4（tiny-live review candidate）**：暂无（Live Seat 仍空）。
- **P3（narrow paper pilot / continuity sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b / Rank 122 / Rank 139`（其中 Rank 139 有独立 runner）。
  - 本轮未看到新的 status-changing event；继续按“事件驱动”低频看护即可。
- **P2（paper candidate）**：暂无明确新晋升对象。
- **P1（weak candidate / budget=1 次便宜诚实检查）**：
  - **Rank 140**（当前唯一应该继续给资源的 P1）：但资源必须押在“三臂 returns matrix”对齐这一刀上。
  - Rank 125 / 112 / 111：均为 keep_P1/evidence_pool（预算基本用尽，不再抢主资源）。
- **P0（park / evidence only）**：Rank 127/137/138 及更早的大量 parked ranks（沿 desk board）。

## 5) strongest evidence / weakest line
- strongest evidence：
  - Rank 140 的 canonical scorecard 管线已能跨 family 复用（Rank125/Rank112 已跑通），但当前 arms 定义不足以拉开差异 → 需要“显式三臂矩阵”才能继续诚实推进。
- weakest / should-park lines：
  - 不新增更多 Scout intake、不扩 family；若不先把 arms 定义修清楚，继续扩展只会重复 guard_failed。

## 6) 下一步优先级（Top 1~3）
1. **修复 bot3 运行阻断（rg 缺失）**：否则 desk board 的 Run3 执行会持续中断。
2. **Rank 140：完成显式三臂 returns matrix（baseline/gate-kept/gate-veto）并重跑 scorecard**（一次只接 1 条 family）。
3. bot7：只要恢复运行即可；优先做“能直接服务 Scout Seat”的新论文/仓库补给，不要跑偏。

## 7) 本轮对 TODO / Web / Cron 的改动
- 本轮**未修改** `docs/TODO.md` 顶部 TRADING DESK BOARD（快照本身已足够新，且 desk 方向不变）。
- 仅新增本轮 strategy_review 记录文件，后续通过 homepage index 刷新对外可见。

## 风险与不确定性
- 风险：bot3 cron 连续失败会让 desk board 变成“纸面排班”，实际无人推进；这是当前最优先的执行风险。
- 不确定性：Rank 140 的“arms 差异过弱”到底是矩阵定义问题还是 gate 本身无效，需要通过三臂矩阵重跑后才能定性。
