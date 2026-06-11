# Strategy Review (bot2) — 2026-03-21 20:55 UTC

## 0) 本轮硬性检查结果

### Repo 状态
- branch: `master`
- HEAD: `2b8f62c rank32b: add flowchart and run replay to transparency page`
- 工作区：大量 `?? untracked`（以 `reports/artifacts/**`, `reports/site/**`, `research/**` 生成物为主）。本轮不做清理/提交，仅记录：当前 repo **非干净态**，后续若要稳定 CI/协作需要再收敛（.gitignore / artifacts 外置等）。

### 最近 research/optimization_loop/
- 目录存在大量历史条目；本轮 desk 排班仍以 `docs/TODO.md` 顶部 board 为准（见下）。

### 最近 research/strategy_review/
- 最近已有多次 strategy-review 记录（2026-03-15 ~ 2026-03-21）。本文件为本轮追加。

### 当前 cron 列表（摘要）
- `bot2-strategy-review-40m`（本 job）
- `bot3-momentum-auto-opt-13m`（自动按 board 执行 Next 3 runs）
- `momentum-narrow-paper-lanes-20m`（Rank 2/17/29/32b lanes refresh）
- `Rank32b live maintenance`（2h，只读巡检 + 邮件）
- 其他：bot6/bot7 等（部分处于 error 或 disabled）

> 备注：多条 job 历史里出现 `Unexpected end of JSON input`（delivery 端/解析端异常痕迹）。本轮不做修复动作，仅在 desk 侧保持“以 board 为 authoritative”。

---

## 1) TRADING DESK BOARD 读取 & 最小必要更新

- 已读取 `docs/TODO.md` 顶部 `TRADING DESK BOARD（authoritative，2026-03-21）`。
- **最小更新已做**：把 board 里“bot3 连续 timeout”的旧描述替换为 **当前 bot3 最近一轮为 ok**，并把 evidence 条目收敛回 5 条。

---

## 2) 本轮 desk 统揽结论（必须明确回答）

### 2.1 Paper primary anchor + hosted lanes
- **Paper primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Paper family lanes（hosted）**：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- **Hosted narrow paper lanes（20m refresh sidecar）**：`Rank 2 / Rank 17 / Rank 29 / Rank 32b`

### 2.2 Live seat 是否空
- **Live Seat：暂空**（不抢位，只有 scout 候选完成基础快筛且足够接近 paper/tiny-live review 才争夺）。

### 2.3 Scout 复刻对象（当前主 scout）
- **Scout Seat 当前主点**：`Rank 139 / CUSUM event-bar confirm-veto gate`
- **本轮 scout 复刻对象**：`Rank 139`（目标：做 1 次“最小 clean replication”，只回答核心三分类是否改善 post-cost 表现/留存/失败结构）。

### 2.4 候选 P0~P4 分档（desk 视角）
- **P0（park / evidence pool，不再占主资源）**：`Rank 138`, `Rank 127`, 以及 136/135/134/.../113 等 evidence pool（详见 board）。
- **P1（当前要花主资源推进/判决）**：
  - `Rank 139`（guard-passed，进入 clean replication queue）
  - `Rank 125`（range location veto，keep_P1）
  - `Rank 112`（basis dislocation short veto，弱候选）
  - `Rank 111`（event clock，evidence_pool）
- **P2（准备升格/进入更强对照的候选）**：本轮 **暂未明确新入列**（以 `Rank 139` 的最小 clean replication 结果来决定是否升 P2/P3）。
- **P3（hosted / sidecar continuity，继续跑但不占 seat）**：
  - `Rank 2 / 17 / 29 / 32b`（narrow paper lanes 20m refresh）
  - `Rank 122`（strict-only paper sidecar，低频监控）
- **P4（仅备忘，不主动推进）**：更远端/历史线索与非当前三条收口线相关条目（当前不需要占用 bot3 资源）。

### 2.5 Next 3 bot3 runs 排班（authoritative）
1. **Run 1**：EMA due-check first（若真实 due-now/overdue，则先做 paper refresh）
2. **Run 2**：若 EMA 仍 `waiting_not_due` → `Rank 139` 最小 clean replication
3. **Run 3**：
   - 若 `Rank 139` 过关 → 直接给 `promote_P2 / promote_P3 / keep_P1` 硬结论；
   - 若 `Rank 139` 直接 park / source exhausted → `fresh intake > tiny-live plumbing`；
   - 仅当 Run2 与 fresh intake 都 exhausted，才允许切 tiny-live 的 path-management fallback。

---

## 3) 本轮后续动作
- 刷新首页：`bash scripts/publish_homepage_index.sh`（见下一步执行日志）
