# Strategy Review — 2026-03-21 23:39 UTC

## 本轮一句话判断
`EMA` 处于 **running paper pilot / waiting_not_due**，因此 desk 的主资源应继续切到 **Scout Seat：把 Rank139 从 P2 推到可执行的 P3（narrow paper pilot spec + monitoring）**；同时 hosted P3 lanes 仅做连续性健康观察，不抢主资源。

---

## 1) Repo / 产物状态（本轮巡检点）
- git：当前工作区存在大量未提交产物（多为 `reports/artifacts/**`、`reports/site/**`、`scripts/**`、`tmp/**` 等）。这更像持续生成的研究/网页产物堆积，而非“少量可审计的改动”。
- 最近 optimization_loop：`2026-03-21_2326_bot3-auto-ema-rank139-thr06-08.md` 等，显示 bot3 已把 Rank139 的 `thr_mult∈{0.6,0.8}` scorecard / promoteP3 路线跑过一轮。
- 最近 strategy_review：最新为 `2026-03-21_2259_strategy-review.md`，本轮在其基础上只做最小校准与“下一步排班收紧”。

## 2) Trading Desk Board（TODO 顶板）本轮最小更新
- 已做：仅更新 **Hosted P3 快照**时间戳与 `Rank17` 的 `exit_ts_marked`：
  - hosted lanes 最近 refresh：`2026-03-21 23:34 UTC`
  - Rank17 open inferred 的 `exit_ts_marked` 更新为 `2026-03-21 23:15 UTC`
- 未做：不把 cron 报错与 bot 状态噪音写进顶板（保持“作战快照”干净）。

---

## 3) Seat 明确回答（你要求的四个点）

### Paper primary anchor + hosted lanes
- **Paper Seat primary anchor**：`EMA / 创业板ETF 1d (active_primary)`
- **Paper hosted family lanes**（仍由 TODO 顶板定义，维持不变）：
  - 美股 1d+1wk（SPY/QQQ/AAPL）
  - Crypto 1d+1wk（BTC/ETH/SOL）
  - 贵州茅台 1d+1wk
  - 沪深300ETF 1d（shadow_watch）

### Live Seat 是否空
- **Live Seat：暂空**（维持）。当前没有“已完成基础快筛 + 足够接近 tiny-live review”且明显优于其他候选的 scout winner。

### Scout Seat 复刻对象（当前主点）
- **Rank 139 / CUSUM event-bar confirm-veto gate**（定位：post-entry shared confirm/veto layer；当前档位 P2，目标是升 P3 或明确 park）。

### 候选 P0~P4 分档（基于 TODO 顶板当前快照）
- **P3（hosted continuity / sidecar）**：Rank 2 / 17 / 29 / 32b（20m refresh）；Rank122（低频监控）
- **P2（paper candidate）**：Rank139
- **P1（只允许 1 次便宜诚实检查；当前基本已用尽预算）**：Rank125 / Rank112 / Rank111
- **P0（park / evidence pool）**：Rank138 / Rank127 / Rank137 + 其余 bulk parked ranks
- **P4（tiny-live review candidate）**：当前无（Live Seat 仍空）

---

## 4) Strongest evidence / Weakest line

### Strongest evidence（本轮仍有效）
- Rank139 已完成最小 clean replication：baseline mean_net@6bps 为负，加入 post-entry confirm/veto 后 **net expectancy 转正**，且 retention 在可解释区间（≈0.305，见 TODO 顶板 evidence）。

### Weakest / should-park / should-not-occupy-main-resource
- 现阶段不应继续把时间花在：
  - `P3 hosted lanes` 的“近义研究/故事补完”（除非出现真实 status-changing event）
  - 已 `budget used` 的 P1 候选反复追加同类检查（Rank125/112/111）

---

## 5) Next 3 bot3 runs（排班确认）
> 以 TODO 顶板 `Next 3 bot3 runs` 为准，本轮不改，只强调“收紧成可落地交付”。

1. **Run 1 = EMA due-check first**
2. **Run 2 = 若 EMA 仍 waiting_not_due：Rank139 的 thr_mult {0.6,0.8} 对比 + 轻量 scorecard**
3. **Run 3 = 硬结论分支（只选 1 个）**
   - 若仍成立：**promote_P3** 并交付最小 `paper spec + monitoring` 接线
   - 若不稳：keep_P2 + 指定唯一补洞
   - 若硬伤：park + 立刻切 fresh intake / tiny-live plumbing

我对 Run3 的偏好：如果 `thr_mult` 两档都不爆雷、且“成本/交易数稳定性”不过分脆弱，**宁可先升 P3 做 narrow paper pilot**，用运行中的 ledger/monitoring 来继续逼真检验，而不是继续在 P2 讲故事。

---

## 6) Cron / 节奏巡检（只记会改变排兵布阵的点）
- `bot3-momentum-auto-opt-13m`：连续报错 `Unexpected end of JSON input`（consecutiveErrors=3）。这会直接影响 “Next 3 runs” 的真实执行率。
  - 建议：下一轮有空时优先定位 **是某个写入/读取的 json 被截断**，还是 gateway/cli 输出被截断。
  - 但：这属于 **bot2 元治理**，不要把它写回 TODO 顶板占位。
- `bot7-quant-digest-30m`：报错原因是试图读取 `~/.nvm/.../openclaw/skills/n2-free-search/SKILL.md` 但该路径不存在（ENOENT）。
  - 建议：将 bot7 的 brief/实现改为读取 workspace 的 `~/clawd/skills/n2-free-search/SKILL.md`（或直接禁用对该 skill 的硬依赖）。

---

## 7) Top 1~3（本轮建议）
1. **把 Rank139 推到“可运行的 P3”**：交付最小 paper spec、monitoring board（字段、刷新频率、kill/park 规则）。
2. **修复 bot3 13m cron 的 JSON 截断错误**：否则排班只是纸面。
3. （若 1 已推进或 2 卡住）做 1 条 fresh intake（来自 paper/repo），但只认领 1 条，避免再铺开。

---

## 风险与不确定性（诚实声明）
- Rank139 的有效性更像“后置确认/否决层”，其价值可能高度依赖 baseline 主信号族（breakout-short / fib / ema-psar）与 entry timing；进入 P3 后必须用 ledger 明确它在不同 baseline 上的 **边际贡献**，避免把它误当 standalone alpha。
- hosted P3 lanes 的 open inferred（Rank17）仍需下一次 refresh 确认是否真实 close；不要据此做过度叙事。
